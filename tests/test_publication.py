import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from automation import buffer,publication
from automation.store import Store
from automation.bridge import Application

class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'jobs.sqlite';self.s=Store(self.path)
  buffer.ensure_schema(self.s);publication.ensure_schema(self.s)
  self.job=self.s.create(101,101,1)['jobId']
  self.s.db.execute("UPDATE jobs SET status='validated',review=? WHERE id=?",(json.dumps({'videoSha256':'a'*64}),self.job))
  self.posts=[]
  for service in ['instagram','tiktok','youtube']:
   c={'id':service,'service':service,'isDisconnected':False,'isLocked':False,'allowedActions':['manageUpdates']}
   payload=buffer.draft_input(c,'Caption','https://example.com/video.mp4','Title')
   post={'id':'post-'+service,'channelId':service,'channelService':service,'status':'draft','text':'Caption','sentAt':None,'dueAt':None,'externalLink':None,'notificationStatus':None,'schedulingType':'automatic','allowedActions':['publishPostNow'],'assets':[{'source':'https://example.com/video.mp4','mimeType':'video/mp4','type':'video'}],'metadata':{'type':'video'}}
   self.posts.append(post)
   self.s.db.execute("INSERT INTO buffer_drafts(job,revision,channel,service,video_hash,payload,status,receipt) VALUES(?,?,?,?,?,?,'draft',?)",(self.job,1,service,service,'a'*64,json.dumps(payload),json.dumps({'bufferPostId':post['id']})))
  publication.prepare(self.s,self.job,1,self.posts)
  self.env=patch.dict(os.environ,{'PUBLISH_ENABLED':'true'});self.env.start()
 def tearDown(self):self.env.stop();self.s.close();self.tmp.cleanup()
 def approve(self):publication.approve(self.s,self.job,1,101,101,'explicit test approval')
 def preflight(self,post):return publication.preflight(self.s,{'postId':post['id'],'response':{'data':{'post':post}},'dispatchId':'execution-1'})
 def test_no_approval_or_disabled_never_produces_mutation(self):
  self.assertEqual(publication.claim_reads(self.s,{})['reads'],[])
  with self.assertRaises(ValueError):self.preflight(self.posts[0])
  with self.assertRaises(PermissionError):publication.approve(self.s,self.job,1,999,101,'x')
  with self.assertRaises(ValueError):publication.approve(self.s,self.job,2,101,101,'x')
  self.approve()
  with patch.dict(os.environ,{'PUBLISH_ENABLED':'false'}):
   self.assertEqual(publication.claim_reads(self.s,{})['reads'],[])
   self.assertEqual(self.preflight(self.posts[0])['mutations'],[])
 def test_telegram_command_requires_owner_version_and_explicit_confirmation(self):
  app=Application({'database':str(self.path),'owner':101,'chat':101})
  def message(event,text,owner=101):return {'update_id':event,'message':{'text':text,'from':{'id':owner},'chat':{'id':101,'type':'private'}}}
  with self.assertRaises(PermissionError):app.route('n8n','/telegram',message(1,f'/publier {self.job} 1 CONFIRME',999))
  app.route('n8n','/telegram',message(2,f'/publier {self.job}'))
  app.route('n8n','/telegram',message(3,f'/publier {self.job} 2 CONFIRME'))
  self.assertIsNone(self.s.get(self.job)['approval'])
  self.assertTrue(app.route('n8n','/telegram',message(4,f'/publier {self.job} 1 CONFIRME'))['accepted'])
  self.assertTrue(app.route('n8n','/telegram',message(5,f'/publier {self.job} 1 CONFIRME'))['alreadyApproved'])
  self.assertEqual(self.s.db.execute("SELECT COUNT(*) FROM audit WHERE action='publication-approved'").fetchone()[0],1)
 def test_restart_double_approval_and_duplicate_preflight_do_not_resend(self):
  self.approve();self.approve();self.assertEqual(len(publication.claim_reads(self.s,{})['reads']),3)
  first=self.preflight(self.posts[0]);self.assertEqual(len(first['mutations']),1)
  self.s.close();self.s=Store(self.path)
  self.assertEqual(self.preflight(self.posts[0])['mutations'],[])
  self.assertEqual(self.s.db.execute("SELECT COUNT(*) FROM audit WHERE action='buffer-publication-dispatched'").fetchone()[0],1)
  self.assertIsNone(self.s.get(self.job)['shared_at'])
 def test_changed_remote_caption_or_local_approval_blocks(self):
  self.approve();changed=copy.deepcopy(self.posts[0]);changed['text']='Unapproved'
  self.assertTrue(self.preflight(changed)['blocked'])
  self.assertEqual(self.s.db.execute('SELECT status FROM buffer_publications WHERE post_id=?',(changed['id'],)).fetchone()[0],'blocked')
  self.s.db.execute('UPDATE jobs SET snapshot=?',(json.dumps({'modified':True}),))
  with self.assertRaises(ValueError):self.preflight(self.posts[1])
 def test_partial_publication_does_not_close_and_all_sent_closes_with_receipts(self):
  self.approve()
  for index,post in enumerate(self.posts):
   request=self.preflight(post)['mutations'][0]
   accepted=post|{'status':'sending'}
   publication.receipt(self.s,{'postId':post['id'],'dispatchId':request['dispatchId'],'response':{'data':{'editPost':{'__typename':'PostActionSuccess','post':accepted}}}})
   self.assertIsNone(self.s.get(self.job)['shared_at'])
   sent=post|{'status':'sent','sentAt':'2026-10-24T09:00:00Z','externalLink':'https://example.com/'+post['id']}
   self.preflight(sent)
   if index<2:
    self.assertEqual(self.s.get(self.job)['status'],'partially_published');self.assertIsNone(self.s.get(self.job)['closed_at'])
  job=self.s.get(self.job);self.assertEqual(job['status'],'shared');self.assertTrue(job['closed_at'])
  self.assertEqual(len(json.loads(job['sharing'])['receipts']),3)
  self.assertEqual(publication.claim_reads(self.s,{})['reads'],[])
 def test_error_or_notification_marked_sent_is_never_confirmed(self):
  self.approve();self.preflight(self.posts[0])
  fake=self.posts[0]|{'status':'sent','sentAt':'2026-10-24T09:00:00Z','schedulingType':'notification','notificationStatus':'markedAsPublished'}
  self.preflight(fake);self.assertIsNone(self.s.get(self.job)['shared_at'])
  self.assertEqual(self.s.db.execute('SELECT status FROM buffer_publications WHERE post_id=?',(fake['id'],)).fetchone()[0],'unknown')
 def test_polling_backoff_and_terminal_attempt_limit(self):
  self.approve();self.assertEqual(len(publication.claim_reads(self.s,{})['reads']),3)
  self.assertEqual(publication.claim_reads(self.s,{})['reads'],[])
  self.s.db.execute('UPDATE buffer_publications SET reads=8,next_check=NULL')
  self.assertEqual(publication.claim_reads(self.s,{})['reads'],[])
  self.assertEqual(self.s.db.execute("SELECT COUNT(*) FROM buffer_publications WHERE status='attention'").fetchone()[0],3)
 def test_unknown_mutation_response_can_only_reconcile_not_resend(self):
  self.approve();req=self.preflight(self.posts[0])['mutations'][0]
  response={'postId':req['postId'],'dispatchId':req['dispatchId'],'response':{'errors':[{'message':'timeout'}]}}
  self.assertEqual(publication.receipt(self.s,response)['status'],'unknown')
  self.assertEqual(self.preflight(self.posts[0])['mutations'],[])
  sent=self.posts[0]|{'status':'sent','sentAt':'2026-10-24T09:00:00Z'}
  self.preflight(sent);self.assertEqual(self.s.get(self.job)['status'],'partially_published')
 def test_buffer_media_backfill_url_does_not_invalidate_confirmed_post(self):
  self.approve();self.preflight(self.posts[1])
  sent=copy.deepcopy(self.posts[1]);sent.update(status='sent',sentAt='2026-10-24T09:00:00Z')
  sent['assets'][0]['source']='https://example.com/buffer-backfilled-video.mp4'
  self.preflight(sent)
  self.assertEqual(self.s.db.execute('SELECT status FROM buffer_publications WHERE post_id=?',(sent['id'],)).fetchone()[0],'sent')

if __name__=='__main__':unittest.main()
