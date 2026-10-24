#!/usr/bin/env python3
"""Installe les workflows natifs Telegram/bridge, sans lire le jeton Telegram."""
import argparse
import json
import os
from pathlib import Path
import runpy
import secrets
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--activate', action='store_true')
parser.add_argument('--update', action='store_true', help='Après revue des changements existants, appliquer les exports avec sauvegarde privée.')
args = parser.parse_args()
if os.geteuid() != 0:
    parser.error('Exécuter avec sudo.')
os.umask(0o077)
admin = runpy.run_path(str(ROOT / 'scripts/automation-admin.py'))
identity = admin['load']('telegram-identity.json')
if identity.get('confirmation') != 'explicit-user-confirmation':
    raise SystemExit('Compte Telegram non confirmé.')
telegram = admin['telegram_credential'](identity['credentialId'])
config = json.loads(Path('/etc/englizy/bridge.json').read_text())
bridge_url = f"http://{config['bind']}:{config['port']}"
if (config['owner'], config['chat']) != (identity['userId'], identity['chatId']):
    raise SystemExit('Identité différente entre le bridge et n8n.')
state = admin['STATE']
if (state / 'bridge-credential.json').exists():
    internal = admin['load']('bridge-credential.json')
else:
    if any(c['name'] == 'Englizy — Liaison interne VPS' for c in admin['listing']('credentials')):
        raise SystemExit('Un identifiant homonyme préexiste ; examiner sa propriété sans le remplacer.')
    secret = Path('/var/lib/englizy/secrets/n8n-bridge-token').read_text().strip()
    value = admin['n8n']('/credentials', 'POST', {'name': 'Englizy — Liaison interne VPS', 'type': 'httpHeaderAuth',
        'data': {'name': 'Authorization', 'value': 'Bearer ' + secret}})
    internal = {k: value[k] for k in ['id', 'name']}
    admin['save']('bridge-credential.json', internal)
references = admin['load']('codex-workflows.json') if (state / 'codex-workflows.json').exists() else {}
for filename in ['telegram-ingress', 'telegram-notifications', 'codex-diagnostic']:
    previous = None
    if filename in references:
        workflow = admin['n8n']('/workflows/' + references[filename]['id'])
        previous = workflow
    if previous is None or (args.update and filename != 'codex-diagnostic'):
        workflow = json.loads((ROOT / 'deploy/n8n/workflows' / (filename + '.json')).read_text())
        if previous:
            old_nodes = {n['id']: n for n in previous['nodes']}
            if set(old_nodes) - {n['id'] for n in workflow['nodes']}:
                raise SystemExit('Nœuds ajoutés dans n8n : réconcilier manuellement avant mise à jour.')
            admin['save'](filename + '-before-update-' + str(previous['versionCounter']) + '.json', previous)
            for node in workflow['nodes']:
                if node['id'] in old_nodes and 'webhookId' in old_nodes[node['id']]:
                    node['webhookId'] = old_nodes[node['id']]['webhookId']
        for node in workflow['nodes']:
            parameters = node['parameters']
            kind = node['type']
            if kind in ['n8n-nodes-base.telegramTrigger', 'n8n-nodes-base.telegram']:
                node['credentials'] = {'telegramApi': telegram}
            if kind == 'n8n-nodes-base.httpRequest':
                parameters['url'] = parameters['url'].replace('http://REQUIRES-BRIDGE-CONFIGURATION', bridge_url)
                node['credentials'] = {'httpHeaderAuth': internal}
            if kind == 'n8n-nodes-base.webhook':
                parameters['path'] = 'englizy-diagnostic-' + secrets.token_hex(16)
                node['credentials'] = {'httpHeaderAuth': internal}
            if kind == 'n8n-nodes-base.if' and node['id'] == 'durable-identity':
                conditions = parameters['conditions']['conditions']
                next(c for c in conditions if c['id'] == 'owner')['rightValue'] = identity['userId']
                next(c for c in conditions if c['id'] == 'chat')['rightValue'] = identity['chatId']
            if kind == 'n8n-nodes-base.telegram' and parameters.get('resource') == 'message':
                parameters['chatId'] = str(identity['chatId'])
        if previous:
            if previous['active']:
                admin['n8n']('/workflows/' + previous['id'] + '/unpublish', 'POST', {})
                if filename == 'telegram-ingress':
                    admin['wait_telegram_webhook'](previous, False)
            workflow = admin['n8n']('/workflows/' + previous['id'], 'PUT', workflow)
        else:
            workflow = admin['n8n']('/workflows', 'POST', workflow)
        references[filename] = {**references.get(filename, {'createdAt': admin['now']()}),
                                'id': workflow['id'], 'name': workflow['name'], 'updatedAt': admin['now']()}
        admin['save']('codex-workflows.json', references)
    if args.activate and not workflow['active'] and filename != 'codex-diagnostic':
        if filename == 'telegram-ingress':
            admin['no_other_receiver'](workflow['id'])
        admin['n8n']('/workflows/' + workflow['id'] + '/publish', 'POST', {'versionId': workflow['versionId']})
        if filename == 'telegram-ingress':
            try:
                admin['wait_telegram_webhook'](workflow, True)
            except RuntimeError:
                admin['n8n']('/workflows/' + workflow['id'] + '/unpublish', 'POST', {})
                raise
    print(json.dumps({'workflowId': workflow['id'], 'name': workflow['name'],
                      'activationRequested': args.activate and filename != 'codex-diagnostic'}, ensure_ascii=False))
