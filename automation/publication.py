"""Publication de brouillons existants, accord exact et réconciliation sans renvoi."""
import datetime
import html
import json
import os
from .buffer import QUERIES
from .store import digest, now

MUTATION='''mutation EnglizyPublishApproved($input: EditPostInput!) {
 editPost(input:$input) { __typename
  ... on PostActionSuccess { post { id channelId status text sentAt dueAt externalLink schedulingType notificationStatus error { message } } }
  ... on MutationError { message }
 }
}'''


def ensure_schema(store):
    store.db.executescript('''CREATE TABLE IF NOT EXISTS buffer_publications (
      job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL, channel TEXT NOT NULL,
      service TEXT NOT NULL, post_id TEXT NOT NULL UNIQUE, expected TEXT NOT NULL,
      edit_input TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'prepared', dispatch TEXT,
      reads INTEGER NOT NULL DEFAULT 0, next_check TEXT, response TEXT, external_url TEXT,
      PRIMARY KEY(job,revision,channel));''')


def content(post):
    return {k:post[k] for k in ['id','channelId','channelService','text','assets','metadata','schedulingType']}


def published_matches(post, expected):
    if not all(k in post for k in expected):return False
    # Buffer peut rapatrier la vidéo publiée vers son stockage (observé TikTok).
    # L'URL exacte est contrôlée AVANT envoi ; après, comparer l'identité du post,
    # les textes/réglages et la liste des types de médias, sans exiger l'ancienne URL.
    def normalized(value):
        return value | {'assets':[{k:v for k,v in a.items() if k!='source'} for a in value['assets']]}
    return normalized(content(post))==normalized(expected)


def prepare(store, job_id, revision, posts):
    with store.tx():
        job=store.get(job_id)
        if job['status']!='validated' or job['revision']!=revision or job['approval']:
            raise ValueError('Une version validée sans publication engagée est requise.')
        rows=store.db.execute('SELECT * FROM buffer_drafts WHERE job=? AND revision=? ORDER BY channel',(job_id,revision)).fetchall()
        if not rows or len(posts)!=len(rows):raise ValueError('Destinations incomplètes.')
        snapshots=[]
        for row in rows:
            post=next((p for p in posts if p['channelId']==row['channel']),None)
            payload=json.loads(row['payload']);receipt=json.loads(row['receipt'] or '{}')
            if (row['status']!='draft' or not post or post['id']!=receipt.get('bufferPostId')
                or post['status']!='draft' or post['sentAt'] or post['dueAt']
                or post['text']!=payload['text'] or post['channelService']!=row['service']
                or post['schedulingType']!='automatic' or 'publishPostNow' not in post['allowedActions']
                or [a['source'] for a in post['assets']] != [a['video']['url'] for a in payload['assets']]
                or json.loads(job['review'])['videoSha256']!=row['video_hash']):
                raise ValueError('Brouillon modifié, indisponible ou incompatible avec la version validée.')
            expected=content(post)
            edit={k:payload[k] for k in ['text','assets','metadata','aiAssisted']}
            edit.update(id=post['id'],mode='shareNow',saveToDraft=False,schedulingType='automatic')
            old=store.db.execute('SELECT expected,edit_input FROM buffer_publications WHERE job=? AND revision=? AND channel=?',(job_id,revision,row['channel'])).fetchone()
            if old and (json.loads(old['expected'])!=expected or json.loads(old['edit_input'])!=edit):
                raise ValueError('Proposition existante différente : ne pas remplacer un accord.')
            store.db.execute('INSERT OR IGNORE INTO buffer_publications(job,revision,channel,service,post_id,expected,edit_input) VALUES(?,?,?,?,?,?,?)',
                (job_id,revision,row['channel'],row['service'],post['id'],json.dumps(expected),json.dumps(edit)))
            snapshots.append({'channel':row['channel'],'postId':post['id'],'content':expected,'edit':edit})
        snapshot={'jobId':job_id,'revision':revision,'videoSha256':json.loads(job['review'])['videoSha256'],
                  'destinations':snapshots,'mode':'shareNow'}
        store.db.execute('UPDATE jobs SET snapshot=? WHERE id=?',(json.dumps(snapshot),job_id))
        store.audit(job_id,'publication-prepared',{'revision':revision,'snapshotHash':digest(snapshot)})
        return digest(snapshot)


def approve(store, job_id, revision, owner, chat, source):
    with store.tx():
        job=store.owned(job_id,owner,chat)
        if job['revision']!=revision or not job['snapshot'] or job['snapshot'].get('mode')!='shareNow':
            raise ValueError('Aucune proposition de publication pour cette version.')
        if job['approval']:
            if job['approval'].get('snapshotHash')!=digest(job['snapshot']):raise ValueError('Accord périmé.')
            return {'accepted':True,'alreadyApproved':True}
        if job['status']!='validated':raise ValueError('Version non validée.')
        rows=store.db.execute('SELECT * FROM buffer_publications WHERE job=? AND revision=?',(job_id,revision)).fetchall()
        if len(rows)!=len(job['snapshot']['destinations']) or not rows or any(r['status']!='prepared' for r in rows):
            raise ValueError('Proposition incomplète ou déjà engagée.')
        approval={'owner':owner,'chat':chat,'revision':revision,'snapshotHash':digest(job['snapshot']),'source':source,'at':now()}
        store.db.execute('UPDATE jobs SET approval=?,updated=? WHERE id=?',(json.dumps(approval),now(),job_id))
        store.db.execute("UPDATE buffer_publications SET status='ready' WHERE job=? AND revision=?",(job_id,revision))
        store.audit(job_id,'publication-approved',approval)
        return {'accepted':True,'jobId':job_id,'revision':revision}


def authorized(store,row):
    job=store.get(row['job']);approval=job['approval'];snapshot=job['snapshot']
    if (not approval or not snapshot or approval.get('snapshotHash')!=digest(snapshot)
        or job['revision']!=row['revision'] or approval['revision']!=row['revision']
        or (approval['owner'],approval['chat'])!=(job['owner'],job['chat'])
        or json.loads(job['review'])['videoSha256']!=snapshot['videoSha256']
        or job['status'] not in ['validated','publishing','partially_published','publication_unknown']):
        raise ValueError('Accord de publication absent, périmé ou tâche inactive.')
    expected=next((x for x in snapshot['destinations'] if x['channel']==row['channel']),None)
    if (not expected or expected['postId']!=row['post_id'] or expected['content']!=json.loads(row['expected'])
        or expected['edit']!=json.loads(row['edit_input'])):raise ValueError('Contenu de publication modifié après accord.')
    return job


def claim_reads(store, body):
    if os.environ.get('PUBLISH_ENABLED')!='true':return {'reads':[],'disabled':True}
    with store.tx():
        requests=[];moment=datetime.datetime.now(datetime.timezone.utc)
        rows=store.db.execute("SELECT * FROM buffer_publications WHERE status IN ('ready','submitting','accepted','unknown') AND (next_check IS NULL OR next_check<=?) ORDER BY job,channel LIMIT 3",(moment.isoformat(),)).fetchall()
        for row in rows:
            authorized(store,row)
            delay=[60,60,120,300,900,1800,3600,7200][min(row['reads'],7)]
            if row['reads']>=8:
                store.db.execute("UPDATE buffer_publications SET status='attention' WHERE post_id=?",(row['post_id'],))
                notify(store,row,'attention','Suivi interrompu après huit lectures : vérification manuelle nécessaire, aucun renvoi.')
                continue
            store.db.execute('UPDATE buffer_publications SET reads=reads+1,next_check=? WHERE post_id=?',((moment+datetime.timedelta(seconds=delay)).isoformat(),row['post_id']))
            requests.append({'postId':row['post_id'],'request':{'query':QUERIES['publication_post'],'variables':{'input':{'id':row['post_id']}}}})
        return {'reads':requests}


def notify(store,row,key,text):
    identifier=f"publication:{row['job']}:{row['revision']}:{row['channel']}:{key}"
    if store.db.execute('SELECT 1 FROM outbox WHERE id=?',(identifier,)).fetchone():return
    store.emit(identifier,row['job'],
        {'kind':'text','text':html.escape(f"{row['service']} · {row['job']} v{row['revision']}\n"+text)})


def observe(store,row,post):
    expected=json.loads(row['expected'])
    if (post.get('id')!=row['post_id'] or post.get('channelId')!=row['channel'] or post.get('text')!=expected['text']):
        raise ValueError('Résultat de publication différent de la destination autorisée.')
    state=post.get('status');url=post.get('externalLink')
    if (state=='sent' and post.get('sentAt') and post.get('schedulingType')=='automatic'
        and not post.get('notificationStatus') and published_matches(post,expected)):
        state='sent'
    elif state=='error':state='error'
    elif state in ['scheduled','sending']:state='accepted'
    else:state='unknown'
    store.db.execute('UPDATE buffer_publications SET status=?,response=?,external_url=? WHERE post_id=?',
        (state,json.dumps(post),url if state=='sent' else None,row['post_id']))
    store.db.execute('INSERT INTO platform_results VALUES(?,?,?,?,?,?) ON CONFLICT(job,revision,destination) DO UPDATE SET status=excluded.status,external_id=excluded.external_id,url=excluded.url',
        (row['job'],row['revision'],row['service'],state,row['post_id'],url if state=='sent' else None))
    if state=='sent':notify(store,row,'sent','Publication confirmée par Buffer.'+ ('\n'+url if url else ' Lien non fourni.'))
    elif state=='error':notify(store,row,'error','Publication refusée : '+str((post.get('error') or {}).get('message','Voir Buffer.'))[:700]+' Aucun renvoi automatique.')
    elif state=='unknown':notify(store,row,'unknown','Résultat encore incertain. Lecture de contrôle prévue ; aucun renvoi automatique.')
    all_rows=store.db.execute('SELECT * FROM buffer_publications WHERE job=? AND revision=?',(row['job'],row['revision'])).fetchall()
    if all(r['status']=='sent' for r in all_rows):
        job=store.get(row['job'])
        store.confirm_shared(row['job'],row['revision'],job['owner'],job['chat'],{
            'source':'platform-receipts','allDestinationsConfirmed':True,'confirmation':'Buffer : chaque destination au statut sent, avec date et mode automatique.',
            'platforms':[r['service'] for r in all_rows],'urls':[r['external_url'] for r in all_rows if r['external_url']],
            'receipts':[{'service':r['service'],'bufferPostId':r['post_id'],'sentAt':json.loads(r['response'])['sentAt']} for r in all_rows]})
        store.emit(f"publication-complete:{row['job']}:{row['revision']}",row['job'],{'kind':'text','text':f"Vidéo {row['job']} publiée sur toutes les destinations. Tâche close ; mise à jour du suivi Excel en cours."})
    elif any(r['status']=='sent' for r in all_rows):
        store.db.execute("UPDATE jobs SET status='partially_published',updated=? WHERE id=?",(now(),row['job']))
    elif state in ['unknown','error']:
        store.db.execute("UPDATE jobs SET status='publication_unknown',updated=? WHERE id=?",(now(),row['job']))
    return state


def preflight(store,body):
    with store.tx():
        row=store.db.execute('SELECT * FROM buffer_publications WHERE post_id=?',(body['postId'],)).fetchone()
        if not row:raise ValueError('Publication inconnue.')
        if row['status'] in ['sent','error','attention','blocked']:return {'mutations':[]}
        authorized(store,row)
        response=body['response'];post=(response.get('data') or {}).get('post')
        if response.get('errors') or not post:return {'mutations':[],'readFailed':True}
        if row['status']=='ready':
            if os.environ.get('PUBLISH_ENABLED')!='true':return {'mutations':[],'disabled':True}
            if (post['status']!='draft' or post['sentAt'] or post['dueAt']
                or content(post)!=json.loads(row['expected']) or 'publishPostNow' not in post['allowedActions']):
                store.db.execute("UPDATE buffer_publications SET status='blocked',response=? WHERE post_id=?",(json.dumps(post),row['post_id']))
                notify(store,row,'blocked','Brouillon modifié ou indisponible depuis l’accord : publication bloquée.')
                return {'mutations':[],'blocked':True}
            dispatch=str(body['dispatchId'])
            edit=json.loads(row['edit_input'])
            if edit.get('mode')!='shareNow' or edit.get('saveToDraft') is not False or edit.get('id')!=row['post_id']:
                raise ValueError('Mutation différente de la publication autorisée.')
            store.db.execute("UPDATE buffer_publications SET status='submitting',dispatch=? WHERE post_id=?",(dispatch,row['post_id']))
            store.db.execute("UPDATE jobs SET status=CASE WHEN status='partially_published' THEN status ELSE 'publishing' END,updated=? WHERE id=?",(now(),row['job']))
            store.audit(row['job'],'buffer-publication-dispatched',{'postId':row['post_id'],'revision':row['revision']})
            return {'mutations':[{'postId':row['post_id'],'dispatchId':dispatch,'request':{'query':MUTATION,'variables':{'input':edit}}}]}
        observe(store,row,post)
        return {'mutations':[],'observed':True}


def receipt(store,body):
    with store.tx():
        row=store.db.execute('SELECT * FROM buffer_publications WHERE post_id=?',(body['postId'],)).fetchone()
        if not row or row['dispatch']!=body['dispatchId']:raise ValueError('Reçu sans réservation.')
        if row['status'] in ['sent','error','accepted','unknown']:return {'accepted':True,'status':row['status']}
        authorized(store,row)
        response=body['response'];result=(response.get('data') or {}).get('editPost') or {}
        if response.get('errors') or result.get('__typename')!='PostActionSuccess':
            store.db.execute("UPDATE buffer_publications SET status='unknown',response=? WHERE post_id=?",(json.dumps(response),row['post_id']))
            store.db.execute("UPDATE jobs SET status=CASE WHEN status='partially_published' THEN status ELSE 'publication_unknown' END,updated=? WHERE id=?",(now(),row['job']))
            notify(store,row,'unknown','Réponse Buffer incertaine : réconciliation par lecture, aucun renvoi.')
            return {'accepted':True,'status':'unknown'}
        return {'accepted':True,'status':observe(store,row,result['post'])}
