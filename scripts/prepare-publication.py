#!/usr/bin/env python3
"""Figer les brouillons pour un accord précis ; aucune publication ni accord automatique."""
import argparse,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from automation import publication
from automation.buffer import Reader,read_secret
from automation.store import Store
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',required=True);p.add_argument('--revision',required=True,type=int);args=p.parse_args()
if os.geteuid()!=0:p.error('Exécuter avec sudo.')
os.umask(0o077)
s=Store('/var/lib/englizy-bridge/jobs.sqlite',owner_permissions=True)
try:
 publication.ensure_schema(s);job=s.get(args.job)
 media=s.db.execute('SELECT * FROM buffer_media WHERE job=? AND revision=?',(args.job,args.revision)).fetchone()
 if not media:raise ValueError('Copie média absente.')
 path=Path('/var/lib/englizy-public-media')/media['filename']
 if path.is_symlink() or not path.resolve().is_relative_to('/var/lib/englizy-public-media'):raise ValueError('Chemin média invalide.')
 with path.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
 if sha!=media['sha256'] or sha!=json.loads(job['review'])['videoSha256']:raise ValueError('Média modifié depuis validation.')
 rows=s.db.execute('SELECT * FROM buffer_drafts WHERE job=? AND revision=?',(args.job,args.revision)).fetchall()
 reader=Reader(read_secret('/var/lib/englizy/secrets/buffer-access-token'));posts=[]
 for row in rows:
  payload=json.loads(row['payload']);post=reader.query('publication_post',{'input':{'id':json.loads(row['receipt'])['bufferPostId']}})['post']
  wanted=payload['metadata'][row['service']];observed=post['metadata']
  for key,value in wanted.items():
   actual=(observed.get('category') or {}).get('categoryId') if key=='categoryId' else observed.get(key)
   if actual!=value:raise ValueError('Réglage du brouillon différent de la proposition : '+key)
  delivery=s.db.execute('SELECT status FROM outbox WHERE id=?',(f"buffer-caption:{args.job}:{args.revision}:{row['channel']}",)).fetchone()
  if not delivery or delivery['status']!='sent':raise ValueError('Légende à envoyer et faire relire avant accord.')
  posts.append(post)
 fingerprint=publication.prepare(s,args.job,args.revision,posts)
 print(json.dumps({'jobId':args.job,'revision':args.revision,'preparedDestinations':[p['channelService'] for p in posts],'snapshotHash':fingerprint,'approved':False}))
finally:s.close()
