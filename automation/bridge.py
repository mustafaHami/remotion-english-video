"""API privée n8n/worker : SQLite durable, commandes fermées, aucun appel Telegram."""
import argparse
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import uuid
import html

from .store import Store, digest, now, keyboard, describe_quota, LABELS
from . import media
from . import tracking
from . import buffer
from . import publication
from .engines import DETAILS

QUOTA_READ_SECONDS = 60


class Application:
    def __init__(self, config):
        self.config = config
        if any(type(config[k]) is not int or config[k] <= 0 for k in ['owner', 'chat']):
            raise ValueError('Identité privée confirmée requise.')
        store = Store(config['database'])
        buffer.ensure_schema(store)
        publication.ensure_schema(store)
        store.close()

    def diagnostic(self, store, engine='codex'):
        # Le numéro interne ne sélectionne aucun format : le worker utilise uniquement --probe.
        job = store.create(self.config['owner'], self.config['chat'], 4, 'Diagnostic sans média', kind='probe', engine=engine)
        store.emit('queued:' + job['jobId'], job['jobId'], {'kind': 'text', 'jobId': job['jobId'],
            'text': f"Diagnostic {LABELS[engine]} {job['jobId']} en attente. Aucune vidéo ni publication ne sera créée."})
        return job

    def ready_for_video(self, store):
        if not self.config.get('videoEnabled', False):
            raise ValueError('La création vidéo n’est pas encore activée.')
        if any(r['kind'] == 'video' for r in tracking.outstanding(store, self.config)):
            raise ValueError('Une vidéo reste à traiter avant une nouvelle création. Envoyez /encours pour la retrouver.')

    def model_menu(self, store):
        """Un choix explicite du modèle avant chaque vidéo ; les quotas sont relus par le worker."""
        self.ready_for_video(store)
        owner, chat = self.config['owner'], self.config['chat']
        store.db.execute("""UPDATE model_menus SET status='superseded',updated=? WHERE owner=? AND chat=?
            AND status IN ('reading','open','selected') AND job IS NULL""", (now(), owner, chat))
        identifier = uuid.uuid4().hex[:12]
        store.db.execute("INSERT INTO model_menus(id,owner,chat,status,created,updated) VALUES(?,?,?,'reading',?,?)",
                         (identifier, owner, chat, now(), now()))
        return identifier

    def publish_model_menu(self, store, identifier, quotas):
        store.db.execute("UPDATE model_menus SET status='open',quotas=?,updated=? WHERE id=?",
                         (json.dumps(quotas), now(), identifier))
        lines = [f"{i}. {LABELS[e]} ({DETAILS[e]}) — {describe_quota(quotas.get(e))}" for i, e in enumerate(LABELS, 1)]
        store.emit('model-menu:' + identifier, None, {'kind': 'menu', 'text':
            'Quel modèle pour la prochaine vidéo ?\n\n' + '\n'.join(lines)
            + '\n\nTouchez un bouton ou répondez 1 ou 2, puis envoyez /video.',
            'keyboard': keyboard(*((f'{i}. {LABELS[e]}', f'model:{identifier}:{e}') for i, e in enumerate(LABELS, 1)))})

    def expire_quota_reads(self, store):
        """Sans réponse du worker, le menu part avec des quotas inconnus (choix toujours possible)."""
        limit = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=QUOTA_READ_SECONDS)).isoformat()
        for row in store.db.execute("SELECT id FROM model_menus WHERE status='reading' AND created<?", (limit,)).fetchall():
            self.publish_model_menu(store, row['id'], {e: {'engine': e, 'status': 'unknown', 'exhausted': None, 'windows': []}
                                                       for e in LABELS})

    def select_model(self, store, identifier, engine):
        menu = store.db.execute('SELECT * FROM model_menus WHERE id=? AND owner=? AND chat=?',
                                (identifier, self.config['owner'], self.config['chat'])).fetchone()
        if not menu or engine not in LABELS:
            raise ValueError('Choix inconnu ; envoyez /modele.')
        if menu['status'] == 'selected' and menu['engine'] == engine:
            return {'accepted': True, 'engine': engine, 'alreadySelected': True}
        if menu['status'] != 'open':
            raise ValueError('Ce menu n’est plus valable ; envoyez /modele.')
        quota = json.loads(menu['quotas'] or '{}').get(engine) or {}
        if quota.get('status') == 'not_configured':
            raise ValueError(f'{LABELS[engine]} n’est pas encore configuré sur le VPS. Choisissez l’autre modèle.')
        if quota.get('exhausted') is True:
            raise ValueError(f'{LABELS[engine]} n’a plus d’usage disponible ({describe_quota(quota)}). '
                             'Choisissez l’autre modèle ou réessayez plus tard avec /modele.')
        store.db.execute("UPDATE model_menus SET status='selected',engine=?,updated=? WHERE id=?", (engine, now(), identifier))
        return {'accepted': True, 'engine': engine}

    def selected_model(self, store):
        return store.db.execute("""SELECT * FROM model_menus WHERE owner=? AND chat=? AND status='selected'
            AND job IS NULL ORDER BY created DESC LIMIT 1""", (self.config['owner'], self.config['chat'])).fetchone()

    def options(self, store):
        self.ready_for_video(store)
        model = self.selected_model(store)
        if not model:
            raise ValueError('Vous avez oublié de choisir le modèle. Envoyez /modele, choisissez 1 ou 2, puis /video.')
        root = Path(os.environ.get('ENGLIZY_REPO', Path(__file__).resolve().parents[1]))
        catalog = json.loads((root / 'src/options/catalog.json').read_text())
        if {item['option'] for item in catalog} != set(range(1, 15)):
            raise ValueError('Catalogue des 14 options incomplet.')
        choice = store.db.execute('''SELECT id FROM option_choices WHERE owner=? AND chat=? AND job IS NULL
            AND model_menu=? ORDER BY created LIMIT 1''', (self.config['owner'], self.config['chat'], model['id'])).fetchone()
        identifier = choice['id'] if choice else uuid.uuid4().hex[:12]
        if not choice:
            store.db.execute('INSERT INTO option_choices(id,owner,chat,created,model_menu) VALUES(?,?,?,?,?)',
                             (identifier, self.config['owner'], self.config['chat'], now(), model['id']))
        keyboard = {'rows': [{'row': {'buttons': [
            {'text': str(item['option']), 'additionalFields': {'callback_data': f"video:{identifier}:{item['option']}"}}
            for item in catalog[i:i + 2]]}} for i in range(0, 14, 2)]}
        text = (f"Modèle : {LABELS[model['engine']]}.\nChoisissez votre format :\n\n" + '\n'.join(f"{i['option']}. {i['name']}" for i in catalog)
                + '\n\nTouchez un numéro ci-dessous. Le contenu sera choisi automatiquement, puis le MP4 vous sera envoyé ici. Aucune publication.'
                + f'\nSi nécessaire : /choisir {identifier} NUMÉRO')
        return {'kind': 'menu', 'text': text, 'keyboard': keyboard}

    def choose(self, store, identifier, option):
        if not self.config.get('videoEnabled', False):
            raise ValueError('La création vidéo n’est pas encore activée.')
        choice = store.db.execute('SELECT * FROM option_choices WHERE id=? AND owner=? AND chat=?',
                                  (identifier, self.config['owner'], self.config['chat'])).fetchone()
        if not choice:
            raise ValueError('Choix inconnu ; envoyez /video pour ouvrir le menu.')
        if choice['job']:
            job = store.get(choice['job'])
            return {'jobId': job['id'], 'status': job['status'], 'alreadySelected': True}
        if any(r['kind'] == 'video' for r in tracking.outstanding(store, self.config)):
            raise ValueError('Une vidéo reste à traiter. Envoyez /encours ; aucune nouvelle création lancée.')
        model = store.db.execute("SELECT * FROM model_menus WHERE id=? AND status='selected' AND job IS NULL",
                                 (choice['model_menu'],)).fetchone() if choice['model_menu'] else None
        if not model:
            raise ValueError('Ce menu n’a plus de modèle valable. Envoyez /modele, puis /video.')
        job = store.create(self.config['owner'], self.config['chat'], option, 'Création directe depuis Telegram. Prévisualisation uniquement.',
                           kind='video', engine=model['engine'])
        store.db.execute('UPDATE option_choices SET job=? WHERE id=?', (job['jobId'], identifier))
        store.db.execute("UPDATE model_menus SET status='consumed',job=?,updated=? WHERE id=?", (job['jobId'], now(), model['id']))
        store.emit('queued:' + job['jobId'], job['jobId'], {'kind': 'text', 'jobId': job['jobId'],
            'text': f"Option {option} sélectionnée avec {LABELS[model['engine']]}. Tâche {job['jobId']} en file : choix d’un contenu inédit, voix, rendu et vérifications. Vous recevrez le MP4 ici. Aucune publication."})
        return job

    def ingest(self, store, update):
        message = update.get('message') or update.get('callback_query', {}).get('message', {})
        sender = update.get('message', {}).get('from') or update.get('callback_query', {}).get('from', {})
        chat = message.get('chat', {})
        if (type(sender.get('id')) is not int or type(chat.get('id')) is not int
                or sender['id'] != self.config['owner'] or chat['id'] != self.config['chat']
                or chat.get('type') != 'private' or sender.get('is_bot')):
            raise PermissionError('Compte non autorisé.')

        def operation():
            text = message.get('text', '')
            if not isinstance(text, str) or len(text) > 8000:
                raise ValueError('Message invalide.')
            event_id = update['update_id']

            def reply(value, job_id=None, payload=None):
                store.emit('event:' + str(event_id), job_id, payload or {'kind': 'text', 'text': value})
                return {'accepted': True, 'jobId': job_id}

            try:
                match = re.fullmatch(r'/publier\s+([a-f0-9]{12})\s+([1-9][0-9]*)\s+CONFIRME', text.strip())
                if match:
                    if os.environ.get('PUBLISH_ENABLED') != 'true':
                        raise ValueError('Publication non activée sur le VPS.')
                    result = publication.approve(store,match[1],int(match[2]),sender['id'],chat['id'],'Telegram /publier CONFIRME')
                    reply(('Cette version a déjà reçu un accord. Aucune nouvelle publication déclenchée. /statut '+match[1]
                           if result.get('alreadyApproved') else 'Accord enregistré pour cette version et ses destinations préparées. Le résultat de chaque réseau reviendra ici.'),match[1])
                    return result
                if text.strip().split(maxsplit=1)[:1] == ['/publier']:
                    return reply('Après lecture de la vidéo, des légendes et des destinations préparées : '
                                 '/publier IDENTIFIANT VERSION CONFIRME. '
                                 'Cette commande autorise une publication réelle immédiate via Buffer. Aucun accord enregistré pour cette commande incomplète.')
                if text.strip() == '/encours':
                    return tracking.emit_summary(store, self.config, 'summary-event:' + str(event_id))
                match = re.fullmatch(r'/valider\s+([a-f0-9]{12})\s+([1-9][0-9]*)', text.strip())
                if match:
                    result = store.validate_preview(match[1], int(match[2]), sender['id'], chat['id'])
                    reply('Vidéo validée, prête à partager. Aucune autorisation de publication enregistrée.', match[1])
                    return result
                match = re.fullmatch(r'/partage\s+([a-f0-9]{12})\s+([1-9][0-9]*)\s+CONFIRME\s+(.+)', text.strip(), re.DOTALL)
                if match:
                    details = match[3].strip()
                    platforms = [name for name in ['Instagram','TikTok','YouTube'] if name.lower() in details.lower()]
                    urls = re.findall(r'https://[^\s<>]+', details)
                    store.confirm_shared(match[1], int(match[2]), sender['id'], chat['id'], {
                        'source':'explicit-user-confirmation', 'allDestinationsConfirmed':True,
                        'confirmation':'Utilisateur : publication terminée sur les réseaux. ' + details,
                        'platforms':platforms, 'urls':urls})
                    reply('Publication terminée enregistrée : shared, tâche close. MP4 conservé 10 jours, détails de tâche 15 jours.', match[1])
                    return {'jobId':match[1], 'status':'shared'}
                if text.strip().split(maxsplit=1)[:1] == ['/partage']:
                    return reply(
                        '/partage ne lance pas la publication des brouillons Buffer. '
                        'Cette commande déclare une publication déjà terminée sur les réseaux.\n\n'
                        'Seulement si vous avez déjà publié :\n'
                        '/partage IDENTIFIANT VERSION CONFIRME plateformes ou liens\n\n'
                        'Indiquez toutes les destinations terminées. '
                        'Pour retrouver l’identifiant et la version : /encours ou /statut IDENTIFIANT. '
                        'Aucun état modifié, aucune publication lancée.')
                if 'callback_query' in update:
                    data = update['callback_query'].get('data', '')
                    match = re.fullmatch(r'video:([a-f0-9]{12}):(\d{1,2})', data)
                    if match:
                        return self.choose(store, match[1], int(match[2]))
                    match = re.fullmatch(r'model:([a-f0-9]{12}):(codex|claude)', data)
                    if match:
                        return self.model_selected(store, reply, match[1], match[2])
                    match = re.fullmatch(r'fallback:([a-f0-9]{12}):(yes|no)', data)
                    if match:
                        return self.fallback(store, reply, match[1], match[2] == 'yes', sender['id'], chat['id'])
                    match = re.fullmatch(r'cancel:([a-f0-9]{12})', data)
                    if match:
                        return self.cancel(store, reply, match[1], sender['id'], chat['id'])
                    return {'accepted': True, 'action': 'unsupported_callback'}
                command = text.strip()
                if command in ['/modele', '/modèle', '/model']:
                    self.model_menu(store)
                    return reply('Lecture des quotas Codex et Claude… Le choix du modèle arrive dans quelques secondes.')
                if command in ['/video', '/options']:
                    return reply('', payload=self.options(store))
                match = re.fullmatch(r'/annuler\s+([a-f0-9]{12})', command)
                if match:
                    return self.cancel(store, reply, match[1], sender['id'], chat['id'])
                match = re.fullmatch(r'/relancer\s+([a-f0-9]{12})\s+(oui|non)', command, re.I)
                if match:
                    return self.fallback(store, reply, match[1], match[2].lower() == 'oui', sender['id'], chat['id'])
                if re.fullmatch(r'[12]', command) and not message.get('reply_to_message'):
                    menu = store.db.execute("""SELECT id,status FROM model_menus WHERE owner=? AND chat=?
                        AND status IN ('reading','open') ORDER BY created DESC LIMIT 1""", (sender['id'], chat['id'])).fetchone()
                    if menu and menu['status'] == 'reading':
                        raise ValueError('Lecture des quotas en cours : attendez le menu des modèles, puis répondez 1 ou 2.')
                    if menu:
                        return self.model_selected(store, reply, menu['id'], list(LABELS)[int(command) - 1])
                if command.lower() in ['oui', 'non'] and not message.get('reply_to_message'):
                    waiting = store.db.execute("SELECT id FROM jobs WHERE owner=? AND chat=? AND status='needs_fallback'",
                                               (sender['id'], chat['id'])).fetchall()
                    if len(waiting) == 1:
                        return self.fallback(store, reply, waiting[0]['id'], command.lower() == 'oui', sender['id'], chat['id'])
                match = re.fullmatch(r'/choisir\s+([a-f0-9]{12})\s+(\d{1,2})', text.strip())
                if match:
                    return self.choose(store, match[1], int(match[2]))
                # Un numéro saisi devant un menu ouvert est un choix, pas une réponse
                # à un ancien diagnostic. Une réponse citant une question reste corrélée.
                if re.fullmatch(r'\d{1,2}', text.strip()) and not message.get('reply_to_message'):
                    choice = store.db.execute('SELECT id FROM option_choices WHERE owner=? AND chat=? AND job IS NULL ORDER BY created LIMIT 1',
                                              (sender['id'], chat['id'])).fetchone()
                    if choice:
                        return self.choose(store, choice['id'], int(text.strip()))
                if text.strip() == '/diagnostic':
                    return self.diagnostic(store)
                if text.strip() == '/diagnostic claude':
                    return self.diagnostic(store, 'claude')
                match = re.fullmatch(r'/statut\s+([a-f0-9]{12})', text.strip())
                if match:
                    job = store.owned(match[1], sender['id'], chat['id'])
                    usage = store.usage_by_engine(job['id'])
                    number = lambda value: f'{value:,}'.replace(',', '\u202f')
                    detail = '\n'.join(f"Usage {LABELS[e]} cumulé : {number(u['total_tokens'])} tokens — entrée {number(u['input_tokens'])} "
                                       f"(dont cache {number(u['cached_input_tokens'])}), sortie {number(u['output_tokens'])}."
                                       for e, u in usage.items()) or 'Usage : non mesuré.'
                    return reply(f"Tâche {job['id']} : {job['status']} (version {job['revision']}, modèle {LABELS[job['engine']]}).\n{detail}", job['id'])
                match = re.fullmatch(r'/question\s+([a-f0-9]{12})', text.strip())
                if match:
                    job = store.owned(match[1], sender['id'], chat['id'])
                    if job['status'] != 'needs_input':
                        raise ValueError('Cette tâche n’attend pas de réponse.')
                    return reply('', job['id'], {'kind': 'question', 'jobId': job['id'], 'questionId': job['question'],
                        'text': job['result']['question'], 'revision': job['revision']})
                match = re.fullmatch(r'/repondre\s+([a-f0-9]{12})\s+([a-f0-9]{12})\s+(.+)', text, re.DOTALL)
                correlation = None
                if match:
                    correlation = match[1], match[2], match[3]
                elif text.strip() and not text.startswith('/'):
                    replied_to = message.get('reply_to_message', {}).get('message_id')
                    if replied_to is not None:
                        job_id, question_id = store.question_for_message(replied_to)
                        correlation = job_id, question_id, text
                    else:
                        waiting = store.db.execute("SELECT id,question FROM jobs WHERE owner=? AND chat=? AND status='needs_input'",
                                                   (sender['id'], chat['id'])).fetchall()
                        if len(waiting) == 1:
                            correlation = waiting[0]['id'], waiting[0]['question'], text
                        elif len(waiting) > 1:
                            raise ValueError('Plusieurs questions sont en attente : répondez au message correspondant ou utilisez /repondre tâche question réponse.')
                if correlation:
                    job_id, question_id, answer = correlation
                    result = store.answer(job_id, question_id, sender['id'], chat['id'], answer)
                    reply(f'Réponse enregistrée pour {job_id}. Reprise de la session de son agent.', job_id)
                    return result
                return reply('Commandes : /modele puis /video, /encours, /statut IDENTIFIANT, /question IDENTIFIANT, '
                             '/valider IDENTIFIANT VERSION, /annuler IDENTIFIANT, /relancer IDENTIFIANT oui|non.\n'
                             '/partage : aide pour déclarer une publication déjà terminée sur les réseaux. '
                             '/publier : aide pour autoriser la publication des brouillons préparés. Aucun horaire automatique de publication.')
            except ValueError as error:
                return reply(str(error))

        result = store.event(update.get('update_id'), operation)
        if 'callback_query' in update:
            result = result | {'callbackId': update['callback_query']['id'], 'callbackText': 'Choix reçu.'}
        return result

    def model_selected(self, store, reply, identifier, engine):
        result = self.select_model(store, identifier, engine)
        if not result.get('alreadySelected'):
            reply(f'Modèle sélectionné : {LABELS[engine]} ({DETAILS[engine]}). Envoyez /video pour choisir le format.')
        return result

    def fallback(self, store, reply, job_id, accept, owner, chat):
        result = store.fallback_decision(job_id, owner, chat, accept)
        reply(f"Relance avec {LABELS[result['engine']]} en file : reprise à partir des fichiers déjà produits." if accept else
              f'Relance refusée : la tâche {job_id} est annulée, tout ce qui a été produit va être supprimé.', job_id)
        return result

    def cancel(self, store, reply, job_id, owner, chat):
        job = store.owned(job_id, owner, chat)
        if job['status'] == 'cleanup_failed':
            result = self.retry_cleanup(store, job)
        else:
            result = store.request_cancel(job_id, 'user-request', owner, chat)
        if not result.get('alreadyCancelled'):
            reply(f'Annulation de la tâche {job_id} enregistrée : suppression des fichiers, voix, rendu et journaux en cours.', job_id)
        return result

    def retry_cleanup(self, store, job):
        with store.tx():
            store.db.execute("UPDATE jobs SET status='cancelling',cleanup_error=NULL,lease=NULL,updated=? WHERE id=? AND status='cleanup_failed'",
                             (now(), job['id']))
            store.audit(job['id'], 'cleanup-retry')
        return {'jobId': job['id'], 'status': 'cancelling'}

    def route(self, role, path, body):
        store = Store(self.config['database'])
        try:
            if role == 'n8n':
                if path == '/buffer/publications/claim':
                    return publication.claim_reads(store, body)
                if path == '/buffer/publications/preflight':
                    return publication.preflight(store, body)
                if path == '/buffer/publications/receipt':
                    return publication.receipt(store, body)
                if path == '/buffer/drafts/claim':
                    return buffer.claim_draft(store, body)
                if path == '/buffer/drafts/receipt':
                    return buffer.record_draft(store, body)
                if path == '/daily-summary':
                    return tracking.daily_summary(store, self.config)
                if path == '/telegram':
                    return self.ingest(store, body)
                if path == '/diagnostics':
                    with store.tx():
                        request_id = body.get('requestId')
                        if request_id is not None:
                            if not isinstance(request_id, str) or not re.fullmatch('[a-f0-9]{32}', request_id):
                                raise ValueError('Identifiant de diagnostic invalide.')
                            previous = store.db.execute('SELECT response FROM admin_requests WHERE id=?', (request_id,)).fetchone()
                            if previous:
                                return json.loads(previous['response'])
                        result = self.diagnostic(store)
                        if request_id:
                            store.db.execute('INSERT INTO admin_requests VALUES(?,?)', (request_id, json.dumps(result)))
                        return result
                if path == '/outbox/claim':
                    dispatch_id = body.get('dispatchId', '')
                    if not isinstance(dispatch_id, str) or not re.fullmatch('[A-Za-z0-9_-]{1,100}', dispatch_id):
                        raise ValueError('Identifiant de notification invalide.')
                    with store.tx():
                        self.expire_quota_reads(store)
                    entries = store.claim_notifications(claim_id=dispatch_id)
                    notifications = []
                    for entry in entries:
                        payload = entry['payload']
                        text = payload.get('text', '')
                        if payload['kind'] == 'question':
                            text = (f"Tâche {payload['jobId']} — question {payload['questionId']}\n\n{text[:2500]}\n\n"
                                    'Répondez à ce message. Si une seule question est en attente, vous pouvez aussi saisir simplement votre réponse.\n'
                                    f"Commande explicite : /repondre {payload['jobId']} {payload['questionId']} votre réponse")
                        note = {'id': entry['id'], 'kind': payload['kind'], 'text': html.escape(text[:3500]),
                                'chatId': self.config['chat'], 'keyboard': payload.get('keyboard', {})}
                        if payload['kind'] == 'ready':
                            job = store.get(payload['jobId'])
                            row = store.db.execute('SELECT media FROM preview_media WHERE job=? AND revision=?',
                                                   (job['id'], payload['revision'])).fetchone()
                            if not row:
                                raise ValueError('Prévisualisation contrôlée manquante.')
                            item = json.loads(row['media'])
                            note.update(kind='video', mediaPath=f"/media/{job['id']}/{payload['revision']}",
                                        width=item['width'], height=item['height'], duration=int(item['duration']))
                            caption = (f"Prévisualisation — option {job['option']} — tâche {job['id']} — {LABELS[job['engine']]}\n"
                                       + job['result']['summary'][:400]
                                       + '\nContrôle technique et inspection d’images effectués.'
                                       + ('\nÉcoute subjective non effectuée.' if not job['result']['checks']['subjectiveListening'] else '')
                                       + ('\nCopie compressée pour Telegram ; original conservé.' if item['compressed'] else '\nMP4 original, sans compression supplémentaire par le VPS.')
                                       + f"\nAprès lecture : /valider {job['id']} {payload['revision']}"
                                       + '\nAucune publication.')
                            note['text'] = html.escape(caption)
                        notifications.append(note)
                    return {'notifications': notifications}
                if path == '/outbox/receipt':
                    if (type(body.get('messageId')) is not int or body['messageId'] <= 0
                            or body.get('chatId') != self.config['chat']):
                        raise ValueError('Reçu Telegram invalide.')
                    store.mark_delivery(body['id'], 'sent', {'messageId': body['messageId'], 'chatId': body['chatId']})
                    return {'accepted': True}
            if role == 'worker':
                if path == '/worker/quota-request':
                    row = store.db.execute("SELECT id FROM model_menus WHERE status='reading' ORDER BY created LIMIT 1").fetchone()
                    return {'requestId': row['id'] if row else None}
                if path == '/worker/quotas':
                    with store.tx():
                        store.save_quotas(body.get('quotas'))
                        menu = store.db.execute("SELECT id FROM model_menus WHERE id=? AND status='reading'",
                                                (body.get('requestId'),)).fetchone()
                        if menu:
                            self.publish_model_menu(store, menu['id'], body['quotas'])
                    return {'accepted': True}
                if path == '/worker/quota-exhausted':
                    footprint = body.get('footprint', [])
                    return store.quota_exhausted(body['jobId'], body['lease'], body.get('started'), body.get('quotas'),
                                                 footprint, body.get('usage'), body.get('sessionId'))
                if path == '/worker/cleanup-done':
                    return store.finish_cleanup(body['jobId'], body['lease'], body.get('report'), body.get('error'))
                if path == '/worker/claim':
                    claim_id = body.get('claimId', '')
                    if not isinstance(claim_id, str) or not re.fullmatch('[a-f0-9]{32}', claim_id):
                        raise ValueError('Identifiant de réservation invalide.')
                    with store.tx():
                        previous = store.db.execute('SELECT job,lease FROM worker_claims WHERE id=?', (claim_id,)).fetchone()
                        if previous:
                            job = store.get(previous['job']) if previous['job'] else None
                            if job and job['lease'] != previous['lease']:
                                return {'job': None}
                            if job and job['status'] == 'cancelling':
                                return {'job': None, 'cleanup': {'jobId': job['id'], 'lease': job['lease'],
                                        'files': store.files(job['id']), 'sessions': store.sessions(job['id'])}}
                        else:
                            # Un nettoyage demandé passe avant toute nouvelle fabrication.
                            cleanup = store.claim_cleanup()
                            if cleanup:
                                store.db.execute('INSERT INTO worker_claims(id,job,lease) VALUES(?,?,?)',
                                                 (claim_id, cleanup['jobId'], cleanup['lease']))
                                return {'job': None, 'cleanup': cleanup}
                            job = store.claim()
                            if job:
                                store.db.execute('INSERT INTO worker_claims(id,job,lease) VALUES(?,?,?)',
                                                 (claim_id, job['id'], job['lease']))
                        if job is None or job['status'] != 'generating':
                            return {'job': None}
                        if job['kind'] != 'probe' and not self.config.get('videoEnabled', False):
                            raise ValueError('Worker limité aux diagnostics sans média.')
                        question = store.db.execute('SELECT answer FROM questions WHERE id=?', (job['question'],)).fetchone()
                        return {'job': {k: job[k] for k in ['id', 'revision', 'option', 'kind', 'brief', 'session', 'result',
                                                            'lease', 'engine', 'handoff']},
                                'answer': question['answer'] if question else None}
                if path == '/worker/result':
                    result = body['result']
                    usage = body.get('usage')
                    # Keep the pre-migration receipt digest compatible with pending retries.
                    result_hash = digest(result)
                    with store.tx():
                        previous = store.db.execute('SELECT digest FROM worker_receipts WHERE lease=?', (body['lease'],)).fetchone()
                        if previous:
                            if previous['digest'] != result_hash:
                                raise ValueError('Résultat différent pour un traitement déjà enregistré.')
                            return {'accepted': True}
                        job = store.get(result['jobId'])
                        if job['lease'] != body['lease'] or (job['kind'] != 'probe' and not self.config.get('videoEnabled', False)):
                            raise ValueError('Traitement obsolète ou non pris en charge.')
                        store.add_files(job['id'], body.get('footprint', []))
                        store.record(job['id'], result['revision'], result, result['sessionId'],
                                     usage=usage, invocation=body['lease'])
                        if job['kind'] == 'video' and result['status'] == 'completed':
                            if not result['checks']['technicalVideo'] or not result['checks']['visualImages']:
                                raise ValueError('Vérifications vidéo manquantes.')
                            descriptor = body['preview']
                            media.read_verified(self.config['mediaRoot'], job['id'], result['revision'], descriptor)
                            actual = media.probe(media.checked_path(self.config['mediaRoot'], job['id'], result['revision'], descriptor))
                            if any(actual[k] != descriptor[k] for k in actual):
                                raise ValueError('Caractéristiques vidéo incohérentes.')
                            store.db.execute('INSERT INTO preview_media VALUES(?,?,?)',
                                             (job['id'], result['revision'], json.dumps(descriptor)))
                        store.db.execute('INSERT INTO worker_receipts VALUES(?,?)', (body['lease'], result_hash))
                        return {'accepted': True}
                if path == '/worker/failure':
                    with store.tx():
                        job = store.get(body['jobId'])
                        if job['lease'] != body['lease']:
                            raise ValueError('Traitement obsolète.')
                        if job['status'] == 'generating':
                            store.add_files(job['id'], body.get('footprint', []))
                        if body.get('usage') is not None and body.get('sessionId'):
                            store.record_usage(job['id'], body['sessionId'], body['lease'], body['usage'], job['engine'])
                        store.fail(body['jobId'], body['lease'])
                    return {'accepted': True}
            raise PermissionError('Route non autorisée pour ce compte de service.')
        finally:
            store.close()

    def video(self, role, job_id, revision):
        if role != 'n8n':
            raise PermissionError('Transport vidéo réservé à n8n.')
        store = Store(self.config['database'])
        try:
            job = store.get(job_id)
            if job['revision'] != revision or job['status'] not in ['awaiting_preview', 'pending_validation', 'validated']:
                raise ValueError('Version vidéo indisponible.')
            row = store.db.execute('SELECT media FROM preview_media WHERE job=? AND revision=?', (job_id, revision)).fetchone()
            if not row:
                raise ValueError('Prévisualisation absente.')
            return media.read_verified(self.config['mediaRoot'], job_id, revision, json.loads(row['media']))
        finally:
            store.close()


def handler(application, tokens):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Aucun corps, en-tête d'authentification ou message Telegram dans les logs HTTP.

        def send(self, status, value):
            data = json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == '/healthz':
                self.send(200, {'ok': True})
                return
            match = re.fullmatch(r'/media/([a-f0-9]{12})/([1-9][0-9]*)', self.path)
            if not match:
                self.send(404, {'error': 'Route inconnue.'})
                return
            role = self.role()
            if role is None:
                self.send(401, {'error': 'Authentification requise.'})
                return
            try:
                data = application.video(role, match[1], int(match[2]))
            except PermissionError:
                self.send(403, {'error': 'Accès refusé.'})
                return
            except (ValueError, OSError):
                self.send(409, {'error': 'Prévisualisation absente ou modifiée.'})
                return
            self.send_response(200)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Content-Disposition', 'attachment; filename="preview.mp4"')
            self.end_headers()
            self.wfile.write(data)

        def role(self):
            supplied = self.headers.get('Authorization', '')
            return next((name for name, token in tokens.items()
                         if secrets.compare_digest(supplied.encode(), ('Bearer ' + token).encode())), None)

        def do_POST(self):
            self.connection.settimeout(20)
            role = self.role()
            if role is None:
                self.send(401, {'error': 'Authentification requise.'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 65536:
                    self.send(413, {'error': 'Taille de requête refusée.'})
                    return
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError('Objet JSON requis.')
                result = application.route(role, self.path, body)
                self.send(200, result)
            except PermissionError:
                self.send(403, {'error': 'Accès refusé.'})
            except (ValueError, KeyError, TypeError):
                self.send(409, {'error': 'Requête invalide, obsolète ou ambiguë.'})
            except Exception:
                self.send(500, {'error': 'Erreur interne ; état conservé, vérifier avant nouvelle tentative.'})
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    config = json.loads(args.config.read_text())
    credentials = Path(os.environ['CREDENTIALS_DIRECTORY'])
    tokens = {name: (credentials / (name + '-token')).read_text().strip() for name in ['n8n', 'worker']}
    if len(set(tokens.values())) != 2 or any(len(token) < 32 for token in tokens.values()):
        raise ValueError('Deux secrets de transport distincts sont requis.')
    application = Application(config)
    server = ThreadingHTTPServer((config['bind'], config['port']), handler(application, tokens))
    print('Bridge privé prêt ; publication ' + ('soumise à accord exact.' if os.environ.get('PUBLISH_ENABLED') == 'true' else 'désactivée.'), flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
