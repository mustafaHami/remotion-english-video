#!/usr/bin/env python3
"""Installer une seule liaison n8n vers les brouillons Buffer, sans publication."""
import json
import os
from pathlib import Path
import runpy
import secrets
import sys
import subprocess
import argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from automation.buffer import read_secret
if os.geteuid()!=0:raise SystemExit('Exécuter avec sudo.')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--update',action='store_true',help='Après revue, sauvegarder et mettre à jour notre workflow existant.')
args=parser.parse_args()
os.umask(0o077)
a=runpy.run_path(str(ROOT/'scripts/automation-admin.py'))
state=a['STATE'];internal=a['load']('bridge-credential.json')
if (state/'buffer-credential.json').exists():
    credential=a['load']('buffer-credential.json')
else:
    # GET /credentials n'est pas disponible sur toutes les éditions. Lire
    # uniquement les métadonnées d'un export chiffré, sans déchiffrer les jetons.
    temporary='/tmp/englizy-credentials-'+secrets.token_hex(12)+'.json'
    try:
        subprocess.run(['docker','exec','n8n-n8n-1','n8n','export:credentials','--all','--output='+temporary],check=True,capture_output=True)
        existing=json.loads(subprocess.check_output(['docker','exec','n8n-n8n-1','cat',temporary]))
        if any(c['name']=='Englizy — Buffer API' for c in existing):
            raise SystemExit('Identifiant Buffer homonyme : examiner avant de créer une copie.')
    finally:
        subprocess.run(['docker','exec','n8n-n8n-1','rm','-f',temporary],check=True,capture_output=True)
    value=a['n8n']('/credentials','POST',{'name':'Englizy — Buffer API','type':'httpHeaderAuth',
        'data':{'name':'Authorization','value':'Bearer '+read_secret('/var/lib/englizy/secrets/buffer-access-token')}})
    credential={k:value[k] for k in ['id','name']};a['save']('buffer-credential.json',credential)
if (state/'buffer-workflow.json').exists():
    reference=a['load']('buffer-workflow.json');workflow=a['n8n']('/workflows/'+reference['id'])
    if args.update:
        previous=workflow
        fresh=json.loads((ROOT/'deploy/n8n/workflows/buffer-drafts.json').read_text())
        old={n['id']:n for n in previous['nodes']}
        if set(old)-{n['id'] for n in fresh['nodes']}:
            raise SystemExit('Nœuds ajoutés dans n8n : réconcilier avant mise à jour.')
        a['save']('buffer-before-update-'+str(previous['versionCounter'])+'.json',previous)
        config=json.loads(Path('/etc/englizy/bridge.json').read_text())
        for n in fresh['nodes']:
            if n['id'] in old:
                for key in ['credentials','webhookId']:
                    if key in old[n['id']]:n[key]=old[n['id']][key]
            if n['type']=='n8n-nodes-base.webhook':n['parameters']['path']=old[n['id']]['parameters']['path']
            if n['type']=='n8n-nodes-base.httpRequest':
                n['parameters']['url']=n['parameters']['url'].replace('http://REQUIRES-BRIDGE-CONFIGURATION',f"http://{config['bind']}:{config['port']}")
        if previous['active']:a['n8n']('/workflows/'+previous['id']+'/unpublish','POST',{})
        workflow=a['n8n']('/workflows/'+previous['id'],'PUT',fresh)
else:
    if any(w['name']=='Englizy — Brouillons Buffer (sans publication)' for w in a['listing']('workflows')):
        raise SystemExit('Workflow homonyme préexistant : examiner avant installation.')
    workflow=json.loads((ROOT/'deploy/n8n/workflows/buffer-drafts.json').read_text())
    config=json.loads(Path('/etc/englizy/bridge.json').read_text())
    for n in workflow['nodes']:
        if n['type']=='n8n-nodes-base.webhook':
            n['parameters']['path']='englizy-buffer-'+secrets.token_hex(16)
            n['credentials']={'httpHeaderAuth':internal}
        elif n['type']=='n8n-nodes-base.httpRequest':
            n['credentials']={'httpHeaderAuth':credential if n['id']=='buffer-create' else internal}
            n['parameters']['url']=n['parameters']['url'].replace('http://REQUIRES-BRIDGE-CONFIGURATION',f"http://{config['bind']}:{config['port']}")
    workflow=a['n8n']('/workflows','POST',workflow)
    reference={k:workflow[k] for k in ['id','name']};a['save']('buffer-workflow.json',reference)
if not workflow['active']:
    a['n8n']('/workflows/'+workflow['id']+'/publish','POST',{'versionId':workflow['versionId']})
print(json.dumps({'workflowId':workflow['id'],'name':workflow['name'],'active':True,'publicationEnabled':False},ensure_ascii=False))
