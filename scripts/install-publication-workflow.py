#!/usr/bin/env python3
"""Installer le suivi des publications explicitement autorisées, sans créer d'accord."""
import json,os,secrets,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if os.geteuid()!=0:raise SystemExit('Exécuter avec sudo.')
os.umask(0o077)
a=runpy.run_path(str(ROOT/'scripts/automation-admin.py'))
if (a['STATE']/'publication-workflow.json').exists():
 w=a['n8n']('/workflows/'+a['load']('publication-workflow.json')['id'])
else:
 w=json.loads((ROOT/'deploy/n8n/workflows/buffer-publication.json').read_text())
 if any(x['name']==w['name'] for x in a['listing']('workflows')):raise SystemExit('Workflow homonyme à examiner.')
 internal=a['load']('bridge-credential.json');credential=a['load']('buffer-credential.json')
 config=json.loads(Path('/etc/englizy/bridge.json').read_text())
 for n in w['nodes']:
  if n['type']=='n8n-nodes-base.webhook':
   n['parameters']['path']='englizy-publication-'+secrets.token_hex(16);n['credentials']={'httpHeaderAuth':internal}
  elif n['type']=='n8n-nodes-base.httpRequest':
   n['credentials']={'httpHeaderAuth':credential if n['parameters']['url']=='https://api.buffer.com' else internal}
   n['parameters']['url']=n['parameters']['url'].replace('http://REQUIRES-BRIDGE-CONFIGURATION',f"http://{config['bind']}:{config['port']}")
 w=a['n8n']('/workflows','POST',w);a['save']('publication-workflow.json',{k:w[k] for k in ['id','name']})
if not w['active']:a['n8n']('/workflows/'+w['id']+'/publish','POST',{'versionId':w['versionId']})
print(json.dumps({'id':w['id'],'name':w['name'],'active':True,'approvalCreated':False},ensure_ascii=False))
