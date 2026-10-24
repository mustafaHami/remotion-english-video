#!/usr/bin/env python3
"""Gestion technique locale ; valeurs sensibles lues uniquement hors du dépôt."""
import argparse
import datetime
import json
import os
from pathlib import Path
import secrets
import hashlib
import time
import urllib.error
import urllib.request
import urllib.parse
import re

ROOT = Path(__file__).resolve().parents[1]
STATE = Path('/var/lib/englizy/management')
SECRETS = Path('/var/lib/englizy/secrets')
N8N = 'https://n8n.mhd-projects.cloud'


class HTTPFailure(RuntimeError):
    def __init__(self, status):
        self.status = status
        super().__init__(f'Appel refusé : HTTP {status}. Consulter le service sans afficher ses secrets.')


def save(name, value):
    STATE.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = STATE / (name + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(STATE / name)


def load(name):
    return json.loads((STATE / name).read_text())


def request(url, method='GET', body=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise HTTPFailure(error.code) from None
    except urllib.error.URLError:
        raise RuntimeError('Service injoignable ; vérifier le réseau et le certificat.') from None


def n8n(path, method='GET', body=None):
    return request(N8N + '/api/v1' + path, method, body,
                   {'X-N8N-API-KEY': (SECRETS / 'n8n-api-key').read_text().strip()})


def listing(resource):
    result, cursor = [], None
    while True:
        page = n8n('/' + resource + '?limit=100' + ('&cursor=' + urllib.parse.quote(cursor) if cursor else ''))
        result.extend(page['data'])
        cursor = page.get('nextCursor')
        if not cursor:
            return result


def telegram_credential(identifier):
    for credential in listing('credentials'):
        if credential['id'] == identifier and credential['type'] == 'telegramApi':
            return {k: credential[k] for k in ['id', 'name']}
    raise RuntimeError('Identifiant Telegram API introuvable dans n8n. Le saisir dans son interface, pas sur le VPS.')


def no_other_receiver(allowed_id=None):
    # Refus prudent même si l'autre trigger pourrait utiliser un autre bot.
    for workflow in listing('workflows'):
        if workflow['active'] and workflow['id'] != allowed_id and any(
                node['type'] == 'n8n-nodes-base.telegramTrigger' for node in workflow['nodes']):
            raise RuntimeError('Un autre workflow Telegram est actif ; examiner son usage avant activation.')


def wait_telegram_webhook(workflow, active):
    trigger = next(node for node in workflow['nodes'] if node['type'] == 'n8n-nodes-base.telegramTrigger')
    url = N8N + '/webhook/' + trigger['webhookId'] + '/webhook'
    for attempt in range(30):
        try:
            request(url, 'POST', {})  # Sans secret : aucun faux message n'entre dans le workflow.
            raise RuntimeError('Le webhook Telegram accepte une requête sans secret ; arrêter le test.')
        except HTTPFailure as error:
            if error.status == (403 if active else 404):
                return
            if error.status not in [403, 404]:
                raise
        time.sleep(0.5)
    raise RuntimeError('État observable du webhook Telegram non confirmé.')


def smoke():
    """Workflow inoffensif conservé mais désactivé après le test HTTPS."""
    try:
        workflow = n8n('/workflows/' + load('n8n-smoke.json')['id'])
    except FileNotFoundError:
        workflow = json.loads((ROOT / 'deploy/n8n/workflows/connection-test.json').read_text())
        workflow['nodes'][0]['parameters']['path'] = 'englizy-test-' + secrets.token_hex(16)
        workflow = n8n('/workflows', 'POST', workflow)
        save('n8n-smoke.json', {'id': workflow['id']})
    identifier = workflow['id']
    path = workflow['nodes'][0]['parameters']['path']
    try:
        n8n('/workflows/' + identifier + '/publish', 'POST', {'versionId': workflow['versionId']})
        # Le service de publication n8n enregistre ses triggers de manière asynchrone.
        for attempt in range(30):
            try:
                result = request(N8N + '/webhook/' + path, 'POST', {'test': 'connexion uniquement'})
                break
            except HTTPFailure as error:
                if error.status != 404 or attempt == 29:
                    raise
                time.sleep(0.5)
        if result != {'ok': True, 'service': 'englizy-n8n', 'publishing': False}:
            raise RuntimeError('Réponse du workflow inattendue.')
    finally:
        n8n('/workflows/' + identifier + '/unpublish', 'POST', {})
    for attempt in range(30):
        try:
            request(N8N + '/webhook/' + path, 'POST', {})
        except HTTPFailure as error:
            if error.status == 404:
                break
            raise
        if attempt == 29:
            raise RuntimeError('Le webhook de test répond encore après désactivation.')
        time.sleep(0.5)
    save('n8n-smoke-result.json', {'id': identifier, 'verifiedAt': now(), 'httpsWebhook': True, 'inactiveWebhook': True})
    print(json.dumps({'workflowId': identifier, 'httpsWebhook': 'passed', 'finalState': 'inactive'}))


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def pair_start(credential_id, bot_username, exclusive_confirmed):
    if not exclusive_confirmed:
        raise RuntimeError('Confirmer avec l’utilisateur que ce bot n’a aucun autre récepteur actif avant activation.')
    if not bot_username or not re.fullmatch(r'@?[A-Za-z0-9_]{5,32}', bot_username):
        raise RuntimeError('Nom public du bot requis, sans jeton.')
    credential = telegram_credential(credential_id)
    previous = load('telegram-pairing.json') if (STATE / 'telegram-pairing.json').exists() else None
    no_other_receiver(previous['workflowId'] if previous else None)
    if previous:
        n8n('/workflows/' + previous['workflowId'] + '/unpublish', 'POST', {})
        wait_telegram_webhook(n8n('/workflows/' + previous['workflowId']), False)
    challenge = secrets.token_hex(12)
    workflow = json.loads((ROOT / 'deploy/n8n/workflows/telegram-pairing.json').read_text())
    workflow['nodes'][0]['credentials'] = {'telegramApi': credential}
    workflow['nodes'][1]['parameters']['conditions']['conditions'][0]['rightValue'] = '/start ' + challenge
    workflow = n8n('/workflows', 'POST', workflow)
    save('telegram-pairing.json', {'challenge': challenge, 'credentialId': credential_id,
        'botUsername': bot_username.lstrip('@'), 'workflowId': workflow['id'],
        'startedAt': now(), 'exclusiveBotConfirmation': 'explicit-user-confirmation-required-by-operator'})
    n8n('/workflows/' + workflow['id'] + '/publish', 'POST', {'versionId': workflow['versionId']})
    try:
        wait_telegram_webhook(workflow, True)
    except RuntimeError:
        n8n('/workflows/' + workflow['id'] + '/unpublish', 'POST', {})
        raise
    print(f"Workflow d’association activé, sans envoi. Ouvrez https://t.me/{bot_username.lstrip('@')} et envoyez : /start {challenge}")


def pair_check():
    pending = load('telegram-pairing.json')
    start = datetime.datetime.fromisoformat(pending['startedAt']).timestamp()
    if datetime.datetime.now(datetime.timezone.utc).timestamp() - start > 1800:
        n8n('/workflows/' + pending['workflowId'] + '/unpublish', 'POST', {})
        raise RuntimeError('Association expirée et workflow désactivé ; relancer l’association.')
    query = '/executions?workflowId=' + pending['workflowId'] + '&status=success&limit=100'
    candidates = []
    for execution in n8n(query)['data']:
        detail = n8n('/executions/' + execution['id'] + '?includeData=true')
        runs = detail.get('data', {}).get('resultData', {}).get('runData', {})
        for run in runs.get('Recevoir le code d’association', []):
            for item in run.get('data', {}).get('main', [[]])[0]:
                message = item.get('json', {}).get('message', {})
                sender, chat = message.get('from', {}), message.get('chat', {})
                if (message.get('text') == '/start ' + pending['challenge'] and message.get('date', 0) >= start - 1
                        and chat.get('type') == 'private' and sender.get('id') == chat.get('id')
                        and type(sender.get('id')) is int and not sender.get('is_bot')):
                    candidates.append({'userId': sender['id'], 'chatId': chat['id'],
                        'firstName': sender.get('first_name'), 'username': sender.get('username'),
                        'executionId': execution['id']})
    unique = {c['userId']: c for c in candidates}
    if len(unique) != 1:
        raise RuntimeError('Aucune identité unique détectée dans les exécutions n8n ; attendre le message privé avec le code.')
    candidate = next(iter(unique.values())) | {'credentialId': pending['credentialId'],
        'challengeHash': hashlib.sha256(pending['challenge'].encode()).hexdigest()}
    save('telegram-candidate.json', candidate)
    n8n('/workflows/' + pending['workflowId'] + '/unpublish', 'POST', {})
    wait_telegram_webhook(n8n('/workflows/' + pending['workflowId']), False)
    print(json.dumps({'candidateToConfirm': candidate, 'pairingWorkflow': 'inactive'}, ensure_ascii=False))


def pair_confirm(user_id, chat_id):
    candidate = load('telegram-candidate.json')
    pending = load('telegram-pairing.json')
    elapsed = datetime.datetime.now(datetime.timezone.utc).timestamp() - datetime.datetime.fromisoformat(pending['startedAt']).timestamp()
    if elapsed > 1800 or candidate['challengeHash'] != hashlib.sha256(pending['challenge'].encode()).hexdigest():
        raise RuntimeError('Association expirée ou remplacée ; recommencer la détection.')
    if candidate['userId'] != user_id or candidate['chatId'] != chat_id:
        raise RuntimeError('Identité différente du candidat détecté.')
    # À appeler seulement après confirmation explicite de ces identifiants par l’utilisateur.
    save('telegram-identity.json', {**candidate, 'confirmedAt': now(), 'confirmation': 'explicit-user-confirmation'})
    print('Identité enregistrée. Aucun message envoyé.')


def telegram_install():
    identity = load('telegram-identity.json')
    credential = telegram_credential(identity['credentialId'])
    no_other_receiver()
    if (STATE / 'telegram-workflow.json').exists():
        workflow = n8n('/workflows/' + load('telegram-workflow.json')['id'])
        print(json.dumps({'workflowId': workflow['id'], 'active': workflow['active'], 'alreadyInstalled': True}))
        return
    workflow = json.loads((ROOT / 'deploy/n8n/workflows/telegram-connection-test.json').read_text())
    for node in workflow['nodes']:
        if node['type'] in ['n8n-nodes-base.telegramTrigger', 'n8n-nodes-base.telegram']:
            node['credentials'] = {'telegramApi': credential}
        if node['type'] == 'n8n-nodes-base.telegramTrigger':
            node['parameters']['additionalFields'].update(chatIds=str(identity['chatId']), userIds=str(identity['userId']))
        if node['type'] == 'n8n-nodes-base.telegram':
            node['parameters']['chatId'] = str(identity['chatId'])
    workflow = n8n('/workflows', 'POST', workflow)
    save('telegram-workflow.json', {'id': workflow['id'], 'credentialId': credential['id']})
    print(json.dumps({'workflowId': workflow['id'], 'active': workflow['active']}))


def telegram_enable():
    identity = load('telegram-identity.json')
    reference = load('telegram-workflow.json')
    telegram_credential(identity['credentialId'])
    if reference['credentialId'] != identity['credentialId']:
        raise RuntimeError('Identifiant différent de l’association.')
    no_other_receiver(reference['id'])
    workflow = n8n('/workflows/' + reference['id'])
    trigger = next(node for node in workflow['nodes'] if node['type'] == 'n8n-nodes-base.telegramTrigger')
    fields = trigger['parameters']['additionalFields']
    reply = next(node for node in workflow['nodes'] if node['type'] == 'n8n-nodes-base.telegram')
    if (fields.get('chatIds') != str(identity['chatId']) or fields.get('userIds') != str(identity['userId'])
            or reply['parameters'].get('chatId') != str(identity['chatId'])):
        raise RuntimeError('Filtres du test différents du compte confirmé.')
    n8n('/workflows/' + workflow['id'] + '/publish', 'POST', {'versionId': workflow['versionId']})
    try:
        wait_telegram_webhook(workflow, True)
    except RuntimeError:
        n8n('/workflows/' + workflow['id'] + '/unpublish', 'POST', {})
        raise
    print('Webhook n8n disponible et requête sans secret refusée. Envoyer un message privé au bot pour vérifier sa réponse.')


def telegram_disable():
    reference = load('telegram-workflow.json')
    n8n('/workflows/' + reference['id'] + '/unpublish', 'POST', {})
    wait_telegram_webhook(n8n('/workflows/' + reference['id']), False)
    print('Workflow Telegram de test désactivé.')


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['n8n-status', 'n8n-smoke', 'telegram-pair-start',
        'telegram-pair-check', 'telegram-pair-confirm', 'telegram-install', 'credentials-status',
        'telegram-enable-test', 'telegram-disable-test'])
    parser.add_argument('--user-id', type=int)
    parser.add_argument('--chat-id', type=int)
    parser.add_argument('--credential-id')
    parser.add_argument('--bot-username')
    parser.add_argument('--bot-exclusive-confirmed', action='store_true')
    args = parser.parse_args()
    if args.command == 'n8n-status':
        result = n8n('/workflows?limit=100')
        print(json.dumps({'connected': True, 'workflows': [
            {k: w.get(k) for k in ['id', 'name', 'active']} for w in result['data']]}))
    elif args.command == 'n8n-smoke':
        smoke()
    elif args.command == 'telegram-pair-start':
        pair_start(args.credential_id, args.bot_username, args.bot_exclusive_confirmed)
    elif args.command == 'telegram-pair-check':
        pair_check()
    elif args.command == 'telegram-pair-confirm':
        pair_confirm(args.user_id, args.chat_id)
    elif args.command == 'credentials-status':
        print(json.dumps([{k: c.get(k) for k in ['id', 'name', 'type']} for c in listing('credentials')], ensure_ascii=False))
    elif args.command == 'telegram-install':
        telegram_install()
    elif args.command == 'telegram-enable-test':
        telegram_enable()
    elif args.command == 'telegram-disable-test':
        telegram_disable()


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, FileNotFoundError) as error:
        if isinstance(error, FileNotFoundError):
            raise SystemExit('Configuration locale manquante ; renseigner le secret ou réaliser l’étape précédente.') from None
        raise SystemExit(str(error)) from None
