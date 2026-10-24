#!/usr/bin/env python3
"""Inspection API en lecture seule et préparation locale des brouillons Buffer."""
import argparse
import json
import os
from pathlib import Path
import sys
import datetime
import hashlib
import secrets
import shutil
import grp
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from automation.buffer import Reader, read_secret, BufferError, ensure_schema, draft_input
from automation.store import Store


def prepare(job_id, revision, services):
    if not job_id or revision is None or not services:
        raise BufferError('Tâche, version et destinations explicitement choisies requises.')
    inventory=json.loads(Path('/var/lib/englizy/management/buffer-inventory.json').read_text())
    checked=datetime.datetime.fromisoformat(inventory['checkedAt'])
    if datetime.datetime.now(datetime.timezone.utc)-checked > datetime.timedelta(hours=24):
        raise BufferError('Inventaire Buffer trop ancien ; refaire inspect.')
    channels=[]
    for service in services:
        found=[c for o in inventory['organizations'] for c in o['channels'] if c['service']==service]
        if len(found)!=1:
            raise BufferError('Destination absente ou ambiguë : '+service)
        channels.append(found[0])
    store=Store('/var/lib/englizy-bridge/jobs.sqlite',owner_permissions=True);ensure_schema(store)
    try:
        job=store.get(job_id)
        if job['status']!='validated' or job['revision']!=revision or not job['review']:
            raise BufferError('Seule la version déjà validée peut préparer des brouillons.')
        value=job['result']['artifacts']['video'].removeprefix('/srv/englizy-repository/')
        original=(ROOT/value).resolve(strict=True)
        if not original.is_relative_to(ROOT/'output/options') or original.suffix!='.mp4':
            raise BufferError('MP4 hors périmètre.')
        with original.open('rb') as stream:
            sha=hashlib.file_digest(stream,'sha256').hexdigest()
        if sha!=json.loads(job['review'])['videoSha256']:
            raise BufferError('La vidéo a changé depuis sa validation.')
        # Le premier épisode est déterminé, aucune nouvelle génération ni nouveau rendu.
        episode_path=(ROOT/job['result']['artifacts']['episode'].removeprefix('/srv/englizy-repository/')).resolve(strict=True)
        if not episode_path.is_relative_to(ROOT/'content/episodes'):
            raise BufferError('Épisode hors périmètre.')
        episode=json.loads(episode_path.read_text())
        expected=['work','walk','cook','clean','wash','help','call','talk','listen','rest']
        if (episode['option']!=1 or episode.get('lessonData',{}).get('rows') !=
                [{'present':'I '+v,'past':'I '+v+'ed','future':'I will '+v} for v in expected]):
            raise BufferError('Ces légendes concernent seulement le premier épisode vérifié ; préparer celles du nouvel épisode.')
        title='10 verbes anglais : présent, passé et futur'
        captions={
            'instagram':'Présent, passé, futur : révisez 10 verbes anglais du quotidien.\nExemple : I work → I worked → I will work.\nÀ vous : écrivez une phrase avec « I will… » !\n#ApprendreAnglais #AnglaisFacile #LearnEnglish #EnglizyGo',
            'tiktok':'10 verbes anglais au présent, au passé et au futur !\nI work → I worked → I will work.\nÀ vous de compléter : I will…\n#ApprendreAnglais #LearnEnglish #AnglaisFacile #EnglizyGo',
            'youtube':'Révisez 10 verbes réguliers anglais : work, walk, cook, clean, wash, help, call, talk, listen et rest.\nPrésent, passé et futur avec will, avec prononciation.\nÀ vous : écrivez une phrase avec « I will… ».\n#Shorts #ApprendreAnglais #LearnEnglish #EnglizyGo',
        }
        directory=Path('/var/lib/englizy-public-media');directory.mkdir(mode=0o750,exist_ok=True)
        os.chown(directory,0,grp.getgrnam('www-data').gr_gid);directory.chmod(0o750)
        row=store.db.execute('SELECT * FROM buffer_media WHERE job=? AND revision=?',(job_id,revision)).fetchone()
        filename=row['filename'] if row else secrets.token_hex(32)+'.mp4'
        if not re.fullmatch('[a-f0-9]{64}[.]mp4',filename):
            raise BufferError('Nom de copie média invalide.')
        destination=directory/filename
        if directory.is_symlink() or destination.is_symlink():
            raise BufferError('Lien média interdit.')
        if destination.exists():
            if hashlib.sha256(destination.read_bytes()).hexdigest()!=sha:
                raise BufferError('Copie Buffer existante différente ; intervention requise.')
        else:
            temporary=destination.with_suffix('.tmp');shutil.copyfile(original,temporary)
            os.chown(temporary,0,grp.getgrnam('www-data').gr_gid);temporary.chmod(0o640);temporary.replace(destination)
        url='https://n8n.mhd-projects.cloud/englizy-media/'+filename
        with store.tx():
            store.db.execute('INSERT OR IGNORE INTO buffer_media VALUES(?,?,?,?,?)',(job_id,revision,filename,sha,url))
            for c in channels:
                payload=draft_input(c,captions[c['service']],url,title)
                old=store.db.execute('SELECT payload FROM buffer_drafts WHERE job=? AND revision=? AND channel=?',(job_id,revision,c['id'])).fetchone()
                if old and json.loads(old[0])!=payload:
                    raise BufferError('Brouillon existant différent ; ne pas écraser ni recréer.')
                store.db.execute('INSERT OR IGNORE INTO buffer_drafts(job,revision,channel,service,video_hash,payload) VALUES(?,?,?,?,?,?)',
                                 (job_id,revision,c['id'],c['service'],sha,json.dumps(payload,ensure_ascii=False)))
            store.audit(job_id,'buffer-drafts-prepared',{'revision':revision,'services':services,'publishEnabled':False})
        return {'prepared':True,'jobId':job_id,'revision':revision,'services':services,'publicMediaConfigured':False,'published':False}
    finally:store.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['inspect','prepare'])
    parser.add_argument('--job')
    parser.add_argument('--revision',type=int)
    parser.add_argument('--services',nargs='+',choices=['instagram','tiktok','youtube'])
    args=parser.parse_args()
    if os.geteuid()!=0:
        parser.error('Exécuter avec sudo pour lire le stockage protégé.')
    os.umask(0o077)
    try:
        if args.action=='prepare':
            print(json.dumps(prepare(args.job,args.revision,args.services),ensure_ascii=False));return
        inventory=Reader(read_secret('/var/lib/englizy/secrets/buffer-access-token')).inventory()
    except BufferError as error:
        raise SystemExit(str(error)) from None
    directory=Path('/var/lib/englizy/management');directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    target=directory/'buffer-inventory.json';temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n');temp.replace(target)
    print(json.dumps({'verified':True,'readOnly':True,'organizations':[
        {'name':o['name'],'channels':[{'name':c['displayName'] or c['name'],'service':c['service'],
         'disconnected':c['isDisconnected'],'locked':c['isLocked'],'allowedActions':c['allowedActions']} for c in o['channels']]}
        for o in inventory['organizations']]},ensure_ascii=False))


if __name__=='__main__':main()
