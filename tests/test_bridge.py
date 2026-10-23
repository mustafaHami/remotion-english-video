"""Intégration simulée de l'API, des sessions et des notifications ; aucun service externe."""
import copy
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from automation.bridge import Application, handler
from automation.store import Store
from automation import worker

SESSION = '01a168f3-7278-75b2-aa8f-ccaf2902b955'


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = {'database': str(Path(self.tmp.name) / 'jobs.sqlite'), 'owner': 101, 'chat': 101}
        self.app = Application(self.config)

    def tearDown(self):
        self.tmp.cleanup()

    def update(self, event_id, text, owner=101, chat=101):
        return {'update_id': event_id, 'message': {'text': text, 'from': {'id': owner, 'is_bot': False},
                'chat': {'id': chat, 'type': 'private'}}}

    def result(self, job, status='needs_input'):
        return {'jobId': job['id'], 'revision': job['revision'], 'status': status, 'sessionId': SESSION,
                'questionId': None, 'question': 'Quel code ?' if status == 'needs_input' else None,
                'artifacts': dict.fromkeys(['video', 'episode', 'manifest', 'inspection']),
                'checks': {'technicalVideo': False, 'visualImages': False, 'subjectiveListening': False, 'notes': []},
                'summary': 'Diagnostic simulé terminé', 'error': None}

    def claim(self, identifier='a' * 32):
        return self.app.route('worker', '/worker/claim', {'claimId': identifier})

    def submit(self, job, status='needs_input'):
        body = {'lease': job['lease'], 'result': self.result(job, status)}
        return self.app.route('worker', '/worker/result', body)

    def test_private_identity_enforced_for_messages_and_callbacks(self):
        for update in [self.update(1, '/diagnostic', owner=102), self.update(2, '/diagnostic', chat=102),
                       {'update_id': 3, 'callback_query': {'from': {'id': 102}, 'message': {'chat': {'id': 101, 'type': 'private'}}}}]:
            with self.assertRaises(PermissionError):
                self.app.route('n8n', '/telegram', update)
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 0)
        store.close()

    def test_worker_cannot_forge_user_commands_or_approval(self):
        for path in ['/diagnostics', '/telegram', '/outbox/receipt', '/approve']:
            with self.assertRaises(PermissionError):
                self.app.route('worker', path, {})
        with self.assertRaises(PermissionError):
            self.app.route('n8n', '/worker/claim', {'claimId': 'a' * 32})

    def test_telegram_duplicate_and_worker_retry_do_not_duplicate_jobs(self):
        first = self.app.route('n8n', '/telegram', self.update(1, '/diagnostic'))
        second = self.app.route('n8n', '/telegram', self.update(1, '/diagnostic'))
        self.assertEqual(first['jobId'], second['jobId'])
        claim = self.claim()
        self.assertEqual(claim, self.claim())
        self.assertEqual(claim['job']['id'], first['jobId'])

    def test_diagnostic_request_retry_survives_application_restart(self):
        body = {'requestId': 'c' * 32}
        first = self.app.route('n8n', '/diagnostics', body)
        self.app = Application(self.config)
        self.assertEqual(first, self.app.route('n8n', '/diagnostics', body))
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 1)
        self.assertEqual(len(store.pending()), 1)
        store.close()

    def test_real_protocol_question_answer_result_and_exact_session(self):
        created = self.app.route('n8n', '/diagnostics', {})
        job = self.claim()['job']
        body = {'lease': job['lease'], 'result': self.result(job)}
        self.app.route('worker', '/worker/result', copy.deepcopy(body))
        self.app.route('worker', '/worker/result', copy.deepcopy(body))
        notes = self.app.route('n8n', '/outbox/claim', {'dispatchId': 'execution-10'})['notifications']
        self.assertEqual(len(notes), 2)  # Attente, puis une seule question malgré le résultat rejoué.
        question = next(note for note in notes if note['id'].startswith('question:'))
        self.app.route('n8n', '/outbox/receipt', {'id': question['id'], 'messageId': 55, 'chatId': 101})
        self.app = Application(self.config)  # Redémarrage de l'application, état conservé.
        update = self.update(2, 'CODE-TEST')
        update['message']['reply_to_message'] = {'message_id': 55}
        self.app.route('n8n', '/telegram', update)
        resumed = self.claim('b' * 32)
        self.assertEqual(resumed['job']['id'], created['jobId'])
        self.assertEqual(resumed['job']['session'], SESSION)
        self.assertEqual(resumed['answer'], 'CODE-TEST')
        self.submit(resumed['job'], 'completed')
        store = Store(self.config['database'])
        self.assertEqual(store.get(created['jobId'])['status'], 'completed')
        self.assertIsNone(store.get(created['jobId'])['approval'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM questions').fetchone()[0], 1)
        store.close()

    def test_plain_answer_accepted_only_when_one_question_is_pending(self):
        for identifier in ['a' * 32, 'b' * 32]:
            self.app.route('n8n', '/diagnostics', {})
            self.submit(self.claim(identifier)['job'])
        self.app.route('n8n', '/telegram', self.update(3, 'ambigu'))
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute("SELECT COUNT(*) FROM jobs WHERE status='needs_input'").fetchone()[0], 2)
        self.assertTrue(any('Plusieurs questions' in item['payload'].get('text', '') for item in store.pending()))
        store.close()

    def test_notification_claim_and_receipt_are_idempotent(self):
        self.app.route('n8n', '/diagnostics', {})
        first = self.app.route('n8n', '/outbox/claim', {'dispatchId': 'execution-1'})
        self.assertEqual(first, self.app.route('n8n', '/outbox/claim', {'dispatchId': 'execution-1'}))
        self.assertEqual(self.app.route('n8n', '/outbox/claim', {'dispatchId': 'execution-2'})['notifications'], [])
        receipt = {'id': first['notifications'][0]['id'], 'messageId': 50, 'chatId': 101}
        self.app.route('n8n', '/outbox/receipt', receipt)
        self.app.route('n8n', '/outbox/receipt', receipt)
        self.assertEqual(self.app.route('n8n', '/outbox/claim', {'dispatchId': 'execution-1'})['notifications'], [])

    def test_video_jobs_cannot_be_launched_by_diagnostic_worker(self):
        store = Store(self.config['database'])
        job = store.create(101, 101, 4)
        store.close()
        with self.assertRaises(ValueError):
            self.claim()
        store = Store(self.config['database'])
        self.assertEqual(store.get(job['jobId'])['status'], 'queued')
        store.close()

    def test_restart_during_codex_does_not_rerun_it(self):
        directory = Path(self.tmp.name) / 'worker'
        directory.mkdir()
        state = {'phase': 'running', 'job': {'id': 'a' * 12, 'lease': 'lease-1'}}
        (directory / 'active.json').write_text(json.dumps(state))
        with patch.object(worker, 'run', side_effect=AssertionError('Ne pas relancer Codex')), patch.object(worker, 'request') as request:
            worker.cycle({'stateDir': str(directory), 'bridge': 'http://example.invalid'}, 'fake-token')
        self.assertEqual(request.call_args.args[2], '/worker/failure')
        self.assertFalse((directory / 'active.json').exists())

    def test_http_authentication_and_role_boundaries(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler(self.app, {'n8n': 'n8n-test', 'worker': 'worker-test'}))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            for token, endpoint, expected in [('', '/diagnostics', 401), ('Bearer invalid', '/diagnostics', 401),
                                               ('Bearer worker-test', '/diagnostics', 403)]:
                req = urllib.request.Request(url + endpoint, data=b'{}', headers={'Authorization': token})
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(req)
                self.assertEqual(error.exception.code, expected)
                error.exception.close()
            req = urllib.request.Request(url + '/diagnostics', data=b'{}', headers={'Authorization': 'Bearer n8n-test'})
            with urllib.request.urlopen(req) as response:
                self.assertEqual(json.load(response)['status'], 'queued')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
