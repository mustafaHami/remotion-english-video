import copy
import json
from pathlib import Path
import tempfile
import unittest
from automation import buffer
from automation.store import Store

class BufferTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'jobs.sqlite'
        self.store=Store(self.path);buffer.ensure_schema(self.store)
        self.job=self.store.create(101,101,1)['jobId']
        self.store.db.execute("UPDATE jobs SET status='validated',review=? WHERE id=?",(json.dumps({'videoSha256':'a'*64}),self.job))
        self.payload=buffer.draft_input({'id':'channel-a','service':'instagram','isDisconnected':False,'isLocked':False,'allowedActions':['manageUpdates']},'Caption','https://example.com/video.mp4','Title')
        self.store.db.execute('INSERT INTO buffer_drafts(job,revision,channel,service,video_hash,payload) VALUES(?,?,?,?,?,?)',(self.job,1,'channel-a','instagram','a'*64,json.dumps(self.payload)))
        self.body={'jobId':self.job,'revision':1,'channelId':'channel-a','dispatchId':'execution-1'}
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def response(self):
        return {'data':{'createPost':{'__typename':'PostActionSuccess','post':{'id':'post-1','channelId':'channel-a','status':'draft','text':'Caption','sentAt':None,'dueAt':None,'assets':[{'source':'https://example.com/video.mp4'}]}}}}
    def test_claim_once_even_after_restart_and_no_receipt(self):
        self.assertEqual(len(buffer.claim_draft(self.store,self.body)['requests']),1)
        self.store.close();self.store=Store(self.path)
        self.assertEqual(buffer.claim_draft(self.store,self.body|{'dispatchId':'execution-2'})['requests'],[])
        self.assertEqual(self.store.get(self.job)['status'],'validated');self.assertIsNone(self.store.get(self.job)['approval'])
    def test_unprepared_destination_and_stale_or_unvalidated_job_rejected(self):
        for change in [{'channelId':'foreign'},{'revision':2}]:
            with self.assertRaises(ValueError):buffer.claim_draft(self.store,self.body|change)
        self.store.db.execute("UPDATE jobs SET status='pending_validation'")
        with self.assertRaises(ValueError):buffer.claim_draft(self.store,self.body)
    def test_receipt_idempotent_never_closes_or_marks_shared(self):
        buffer.claim_draft(self.store,self.body)
        body=self.body|{'response':self.response()}
        self.assertEqual(buffer.record_draft(self.store,body)['status'],'draft')
        buffer.record_draft(self.store,body)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0],1)
        self.assertIsNone(self.store.get(self.job)['shared_at']);self.assertIsNone(self.store.get(self.job)['closed_at'])
        with self.assertRaises(ValueError):buffer.record_draft(self.store,body|{'dispatchId':'other'})
    def test_unknown_external_result_is_not_retried(self):
        for change in [{'status':'scheduled'},{'channelId':'other'},{'sentAt':'2026-10-24'},{'text':'changed'},{'assets':[]}]:
            response=self.response();response['data']['createPost']['post'].update(change)
            with self.assertRaises(buffer.BufferError):buffer.draft_receipt(response,self.payload)
        buffer.claim_draft(self.store,self.body)
        result=buffer.record_draft(self.store,self.body|{'response':{'errors':[{'message':'failure'}]}})
        self.assertEqual(result['status'],'unknown');self.assertFalse(result['publicationConfirmed'])
        self.assertEqual(buffer.claim_draft(self.store,self.body)['requests'],[])
    def test_non_draft_mutations_rejected_before_dispatch(self):
        for change in [{'saveToDraft':False},{'saveToDraft':1},{'dueAt':'2026-11-01'},{'mode':'shareNow'},{'draftId':'x'}]:
            with self.assertRaises(buffer.BufferError):buffer.validate_draft_input(self.payload|change)
        self.store.db.execute('UPDATE buffer_drafts SET payload=?',(json.dumps(self.payload|{'saveToDraft':False}),))
        with self.assertRaises(buffer.BufferError):buffer.claim_draft(self.store,self.body)
        self.assertEqual(self.store.db.execute('SELECT status FROM buffer_drafts').fetchone()[0],'prepared')
    def test_reader_cannot_publish_and_export_has_no_retry_or_schedule(self):
        with self.assertRaises(buffer.BufferError):buffer.Reader('fake').query('createPost')
        workflow=json.loads((Path(__file__).resolve().parents[1]/'deploy/n8n/workflows/buffer-drafts.json').read_text())
        self.assertFalse(any(n['type'].endswith(('telegramTrigger','scheduleTrigger')) for n in workflow['nodes']))
        self.assertFalse(next(n for n in workflow['nodes'] if n['id']=='buffer-create')['retryOnFail'])
        self.assertEqual(workflow['settings']['saveDataErrorExecution'],'none')

if __name__=='__main__':unittest.main()
