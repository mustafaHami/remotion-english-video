"""API privée n8n/worker : SQLite durable, commandes fermées, aucun appel Telegram."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets

from .store import Store, digest, now


class Application:
    def __init__(self, config):
        self.config = config
        if any(type(config[k]) is not int or config[k] <= 0 for k in ['owner', 'chat']):
            raise ValueError('Identité privée confirmée requise.')
        store = Store(config['database'])
        store.close()

    def diagnostic(self, store):
        # Le numéro interne ne sélectionne aucun format : le worker utilise uniquement --probe.
        job = store.create(self.config['owner'], self.config['chat'], 4, 'Diagnostic sans média', kind='probe')
        store.emit('queued:' + job['jobId'], job['jobId'], {'kind': 'text', 'jobId': job['jobId'],
            'text': f"Diagnostic {job['jobId']} en attente. Aucune vidéo ni publication ne sera créée."})
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
            if 'callback_query' in update:
                return {'accepted': True, 'action': 'unsupported_callback'}
            text = message.get('text', '')
            if not isinstance(text, str) or len(text) > 8000:
                raise ValueError('Message invalide.')
            event_id = update['update_id']

            def reply(value, job_id=None, payload=None):
                store.emit('event:' + str(event_id), job_id, payload or {'kind': 'text', 'text': value})
                return {'accepted': True, 'jobId': job_id}

            try:
                if text.strip() == '/diagnostic':
                    return self.diagnostic(store)
                match = re.fullmatch(r'/statut\s+([a-f0-9]{12})', text.strip())
                if match:
                    job = store.owned(match[1], sender['id'], chat['id'])
                    return reply(f"Tâche {job['id']} : {job['status']} (version {job['revision']}).", job['id'])
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
                    reply(f'Réponse enregistrée pour {job_id}. Reprise de sa session Codex.', job_id)
                    return result
                return reply('Liaison Codex : /diagnostic, /statut <tâche>, /question <tâche>. La création vidéo et la publication ne sont pas encore activées.')
            except ValueError as error:
                return reply(str(error))

        return store.event(update.get('update_id'), operation)

    def route(self, role, path, body):
        store = Store(self.config['database'])
        try:
            if role == 'n8n':
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
                    entries = store.claim_notifications(claim_id=dispatch_id)
                    notifications = []
                    for entry in entries:
                        payload = entry['payload']
                        text = payload.get('text', '')
                        if payload['kind'] == 'question':
                            text = (f"Tâche {payload['jobId']} — question {payload['questionId']}\n\n{text[:2500]}\n\n"
                                    'Répondez à ce message. Si une seule question est en attente, vous pouvez aussi saisir simplement votre réponse.\n'
                                    f"Commande explicite : /repondre {payload['jobId']} {payload['questionId']} votre réponse")
                        notifications.append({'id': entry['id'], 'text': text[:4000], 'chatId': self.config['chat']})
                    return {'notifications': notifications}
                if path == '/outbox/receipt':
                    if (type(body.get('messageId')) is not int or body['messageId'] <= 0
                            or body.get('chatId') != self.config['chat']):
                        raise ValueError('Reçu Telegram invalide.')
                    store.mark_delivery(body['id'], 'sent', {'messageId': body['messageId'], 'chatId': body['chatId']})
                    return {'accepted': True}
            if role == 'worker':
                if path == '/worker/claim':
                    claim_id = body.get('claimId', '')
                    if not isinstance(claim_id, str) or not re.fullmatch('[a-f0-9]{32}', claim_id):
                        raise ValueError('Identifiant de réservation invalide.')
                    with store.tx():
                        previous = store.db.execute('SELECT job FROM worker_claims WHERE id=?', (claim_id,)).fetchone()
                        if previous:
                            job = store.get(previous['job']) if previous['job'] else None
                        else:
                            job = store.claim()
                            if job:
                                store.db.execute('INSERT INTO worker_claims VALUES(?,?)', (claim_id, job['id']))
                        if job is None or job['status'] != 'generating':
                            return {'job': None}
                        if job['kind'] != 'probe':
                            raise ValueError('Worker limité aux diagnostics sans média.')
                        question = store.db.execute('SELECT answer FROM questions WHERE id=?', (job['question'],)).fetchone()
                        return {'job': {k: job[k] for k in ['id', 'revision', 'option', 'kind', 'brief', 'session', 'result', 'lease']},
                                'answer': question['answer'] if question else None}
                if path == '/worker/result':
                    result = body['result']
                    result_hash = digest(result)
                    with store.tx():
                        previous = store.db.execute('SELECT digest FROM worker_receipts WHERE lease=?', (body['lease'],)).fetchone()
                        if previous:
                            if previous['digest'] != result_hash:
                                raise ValueError('Résultat différent pour un traitement déjà enregistré.')
                            return {'accepted': True}
                        job = store.get(result['jobId'])
                        if job['lease'] != body['lease'] or job['kind'] != 'probe':
                            raise ValueError('Traitement obsolète ou non pris en charge.')
                        store.record(job['id'], result['revision'], result, result['sessionId'])
                        store.db.execute('INSERT INTO worker_receipts VALUES(?,?)', (body['lease'], result_hash))
                        return {'accepted': True}
                if path == '/worker/failure':
                    store.fail(body['jobId'], body['lease'])
                    return {'accepted': True}
            raise PermissionError('Route non autorisée pour ce compte de service.')
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
            self.send(200 if self.path == '/healthz' else 404, {'ok': self.path == '/healthz'})

        def do_POST(self):
            self.connection.settimeout(20)
            supplied = self.headers.get('Authorization', '')
            role = next((name for name, token in tokens.items()
                         if secrets.compare_digest(supplied.encode(), ('Bearer ' + token).encode())), None)
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
    print('Bridge privé prêt ; publication et génération vidéo désactivées.', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
