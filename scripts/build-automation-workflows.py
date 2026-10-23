#!/usr/bin/env python3
"""Exports génériques sans identifiants ni secrets ; installation séparée par API n8n."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'deploy/n8n/workflows'


def node(identifier, name, kind, version, x, parameters, **extra):
    return {'id': identifier, 'name': name, 'type': 'n8n-nodes-base.' + kind,
            'typeVersion': version, 'position': [x, 0], 'parameters': parameters, **extra}


def link(name):
    return {'node': name, 'type': 'main', 'index': 0}


def http(identifier, name, path, body, x):
    return node(identifier, name, 'httpRequest', 4.2, x, {
        'method': 'POST', 'url': 'http://REQUIRES-BRIDGE-CONFIGURATION' + path,
        'authentication': 'genericCredentialType', 'genericAuthType': 'httpHeaderAuth',
        'sendBody': True, 'specifyBody': 'json', 'jsonBody': body, 'options': {'timeout': 15000}},
        retryOnFail=True, maxTries=3, waitBetweenTries=2000)


def write(filename, name, nodes, connections, note, save='all', save_errors=None):
    nodes.append(node(filename + '-note', 'Fonctionnement et limites', 'stickyNote', 1, 0,
        {'content': note, 'width': 850, 'height': 230}))
    nodes[-1]['position'] = [0, -290]
    value = {'name': name, 'nodes': nodes, 'connections': connections,
             'settings': {'executionOrder': 'v1', 'timezone': 'Europe/Paris',
                          'saveDataSuccessExecution': save, 'saveDataErrorExecution': save_errors or save,
                          'saveExecutionProgress': False, 'saveManualExecutions': False}}
    (DEST / (filename + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


trigger = node('durable-telegram', 'Recevoir les messages et réponses', 'telegramTrigger', 1.2, 0,
               {'updates': ['message', 'callback_query'], 'additionalFields': {}})
conditions = [
    {'id': 'owner', 'leftValue': '={{ $json.message?.from?.id ?? $json.callback_query?.from?.id ?? -1 }}',
     'rightValue': 0, 'operator': {'type': 'number', 'operation': 'equals'}},
    {'id': 'chat', 'leftValue': '={{ $json.message?.chat?.id ?? $json.callback_query?.message?.chat?.id ?? -1 }}',
     'rightValue': 0, 'operator': {'type': 'number', 'operation': 'equals'}},
    {'id': 'private', 'leftValue': '={{ $json.message?.chat?.type ?? $json.callback_query?.message?.chat?.type ?? "" }}',
     'rightValue': 'private', 'operator': {'type': 'string', 'operation': 'equals'}},
]
guard = node('durable-identity', 'Vérifier utilisateur et conversation privés', 'if', 2.2, 300,
             {'conditions': {'options': {'caseSensitive': True, 'typeValidation': 'strict', 'version': 2},
                             'conditions': conditions, 'combinator': 'and'}, 'options': {}})
enqueue = http('durable-enqueue', 'Persister la commande avant le travail', '/telegram', '={{ JSON.stringify($json) }}', 630)
callback = node('callback-present', 'Un bouton attend un accusé', 'if', 2.2, 930,
    {'conditions': {'options': {'typeValidation': 'strict', 'version': 2}, 'conditions': [
        {'id': 'callback', 'leftValue': '={{ Boolean($json.callbackId) }}', 'rightValue': True,
         'operator': {'type': 'boolean', 'operation': 'true', 'singleValue': True}}], 'combinator': 'and'}, 'options': {}})
ack = node('callback-ack', 'Confirmer le clic Telegram', 'telegram', 1.2, 1220,
    {'resource': 'callback', 'operation': 'answerQuery', 'queryId': '={{ $json.callbackId }}',
     'additionalFields': {'text': '={{ $json.callbackText }}'}})
write('telegram-ingress', 'Englizy — Réception Telegram et tâches durables', [trigger, guard, enqueue, callback, ack], {
    trigger['name']: {'main': [[link(guard['name'])]]}, guard['name']: {'main': [[link(enqueue['name'])], []]},
    enqueue['name']: {'main': [[link(callback['name'])]]}, callback['name']: {'main': [[link(ack['name'])], []]}},
    '## Réception unique du bot\nTrigger 1.2 : secret Telegram vérifié et updates en attente conservées. '
    'Les trois filtres suivants contrôlent aussi les callbacks ; les valeurs 0 refusent tous les comptes. '
    'Le bridge recontrôle l’identité et déduplique update_id dans SQLite. '
    'Aucune commande shell, aucune publication. Ne pas activer un autre Telegram Trigger pour ce bot.')

timer = node('notification-poll', 'Consulter les notifications en attente', 'scheduleTrigger', 1.2, 0,
             {'rule': {'interval': [{'field': 'seconds', 'secondsInterval': 10}]}})
reserve = http('notification-reserve', 'Réserver les notifications sans doublon', '/outbox/claim',
               '={{ JSON.stringify({dispatchId:String($execution.id)}) }}', 300)
split = node('notification-split', 'Préparer chaque notification', 'splitOut', 1, 600,
             {'fieldToSplitOut': 'notifications', 'include': 'noOtherFields',
              'options': {'destinationFieldName': 'notification'}})
send = node('notification-send', 'Envoyer la question ou le résultat', 'telegram', 1.2, 900,
            {'resource': 'message', 'operation': 'sendMessage', 'chatId': '0',
             'text': '={{ $json.notification.text }}', 'additionalFields': {'appendAttribution': False, 'parse_mode': 'HTML'},
             'replyMarkup': '={{ $json.notification.kind === "menu" ? "inlineKeyboard" : "none" }}',
             'inlineKeyboard': '={{ $json.notification.keyboard }}'})
is_video = node('notification-video', 'La notification contient une vidéo', 'if', 2.2, 850,
    {'conditions': {'options': {'typeValidation': 'strict', 'version': 2}, 'conditions': [
        {'id': 'video', 'leftValue': '={{ $json.notification.kind }}', 'rightValue': 'video',
         'operator': {'type': 'string', 'operation': 'equals'}}], 'combinator': 'and'}, 'options': {}})
download = node('preview-download', 'Récupérer le MP4 contrôlé sur le VPS', 'httpRequest', 4.2, 1150,
    {'method': 'GET', 'url': '=http://REQUIRES-BRIDGE-CONFIGURATION{{ $json.notification.mediaPath }}',
     'authentication': 'genericCredentialType', 'genericAuthType': 'httpHeaderAuth',
     'options': {'timeout': 120000, 'response': {'response': {'responseFormat': 'file', 'outputPropertyName': 'video'}}}},
    retryOnFail=True, maxTries=3, waitBetweenTries=2000)
video_send = node('preview-send', 'Envoyer la prévisualisation MP4', 'telegram', 1.2, 1450,
    {'resource': 'message', 'operation': 'sendVideo', 'chatId': '0', 'binaryData': True,
     'binaryPropertyName': 'video', 'replyMarkup': 'none',
     'additionalFields': {'caption': '={{ $("Préparer chaque notification").item.json.notification.text }}',
                          'parse_mode': 'HTML',
                          'width': '={{ $("Préparer chaque notification").item.json.notification.width }}',
                          'height': '={{ $("Préparer chaque notification").item.json.notification.height }}',
                          'duration': '={{ $("Préparer chaque notification").item.json.notification.duration }}'}})
send['position'] = [1150, 230]
receipt = http('notification-receipt', 'Conserver le reçu Telegram', '/outbox/receipt',
    '={{ JSON.stringify({id:$("Préparer chaque notification").item.json.notification.id, '
    'messageId:$json.message_id ?? $json.result?.message_id, chatId:$json.chat?.id ?? $json.result?.chat?.id}) }}', 1200)
receipt['position'] = [1780, 100]
write('telegram-notifications', 'Englizy — Questions et résultats vers Telegram', [timer, reserve, split, is_video, download, video_send, send, receipt], {
    timer['name']: {'main': [[link(reserve['name'])]]}, reserve['name']: {'main': [[link(split['name'])]]},
    split['name']: {'main': [[link(is_video['name'])]]}, is_video['name']: {'main': [[link(download['name'])], [link(send['name'])]]},
    download['name']: {'main': [[link(video_send['name'])]]}, video_send['name']: {'main': [[link(receipt['name'])]]},
    send['name']: {'main': [[link(receipt['name'])]]}},
    '## Transport technique uniquement\nScrutation toutes les 10 secondes, aucun rappel quotidien. '
    'Question persistée avant envoi ; reçu conservé avec son identifiant de tâche/question. '
    'Un envoi Telegram ne se répète pas automatiquement après un résultat inconnu. '
    'Les succès de scrutation ne sont pas conservés dans n8n ; erreurs conservées, reçus durables dans SQLite. '
    'Le jeton Telegram reste dans les identifiants n8n. Pas de publication sociale.', save='none', save_errors='all')

webhook = node('diagnostic-webhook', 'Recevoir un diagnostic autorisé', 'webhook', 2.1, 0,
    {'httpMethod': 'POST', 'path': 'REQUIRES-UNIQUE-DIAGNOSTIC-PATH', 'authentication': 'headerAuth',
     'responseMode': 'lastNode', 'options': {}})
diagnostic = http('diagnostic-enqueue', 'Mettre le diagnostic Codex en file', '/diagnostics',
                  '={{ JSON.stringify({requestId:$json.body.requestId}) }}', 350)
write('codex-diagnostic', 'Englizy — Lancer un diagnostic Codex sans vidéo', [webhook, diagnostic],
    {webhook['name']: {'main': [[link(diagnostic['name'])]]}},
    '## Test court sans fabrication\nWebhook HTTPS authentifié. Le bridge répond avec un job stable ; '
    'le worker lance Codex séparément. Une question revient par le workflow de notifications. '
    'Réponse Telegram → même job → même UUID de session. Aucun épisode, média ou publication. '
    'Données d’exécution non conservées pour ne pas stocker l’en-tête du webhook.', save='none')
print('Exports n8n génériques créés, sans secrets.')
