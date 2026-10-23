"""Scénarios simulés : aucun accès Telegram, n8n, Buffer ou modèle."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
import importlib.util
from unittest.mock import patch

from automation.runner import arguments, allowed_file, SCHEMA, validate_schema
from automation.store import Store, digest

SESSION = '01a168f3-7278-75b2-aa8f-ccaf2902b955'


class DurableStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'jobs.sqlite'
        self.store = Store(self.path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def job(self):
        return self.store.create(101, 101, 4)['jobId']

    def result(self, job_id, status):
        return {'jobId': job_id, 'revision': 1, 'status': status, 'sessionId': SESSION,
                'questionId': None, 'question': 'Quel code ?' if status == 'needs_input' else None,
                'artifacts': dict.fromkeys(['video', 'episode', 'manifest', 'inspection']),
                'checks': {'technicalVideo': False, 'visualImages': False, 'subjectiveListening': False, 'notes': []},
                'summary': 'Simulation', 'error': 'Panne simulée' if status == 'failed' else None}

    def preview(self):
        job_id = self.job()
        self.store.claim()
        self.store.record(job_id, 1, self.result(job_id, 'completed'), SESSION)
        snapshot = {'videoSha256': 'a' * 64, 'captions': {'test-channel': 'Légende de test'},
                    'destinations': ['test-channel'], 'schedule': None}
        snapshot_hash = self.store.set_preview(job_id, 1, snapshot)
        return job_id, snapshot, snapshot_hash

    def test_deduplication_survives_restart(self):
        first = self.store.event(42, lambda: self.store.create(101, 101, 4))
        self.store.close()
        self.store = Store(self.path)
        second = self.store.event(42, lambda: self.fail('Événement rejoué'))
        self.assertEqual(first, second)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 1)

    def test_failed_event_rolls_back_dedup_and_job(self):
        def failure():
            self.job()
            raise ValueError('panne simulée')
        with self.assertRaises(ValueError):
            self.store.event(43, failure)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 0)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM events').fetchone()[0], 0)

    def test_only_one_generation(self):
        a, b = self.job(), self.job()
        self.assertEqual(self.store.claim()['id'], a)
        self.assertIsNone(self.store.claim())
        self.assertEqual(self.store.get(b)['status'], 'queued')

    def test_question_persisted_before_notification_and_exact_session_resumed(self):
        job_id = self.job()
        self.store.claim()
        self.store.record(job_id, 1, self.result(job_id, 'needs_input'), SESSION)
        self.store.close()
        self.store = Store(self.path)
        job = self.store.get(job_id)
        self.assertEqual(self.store.pending()[0]['payload']['questionId'], job['question'])
        answer = self.store.answer(job_id, job['question'], 101, 101, 'ABCD')
        self.assertEqual(answer['sessionId'], SESSION)
        self.assertEqual(self.store.claim()['session'], SESSION)
        with self.assertRaises(ValueError):
            self.store.answer(job_id, job['question'], 101, 101, 'seconde réponse')

    def test_wrong_owner_chat_question_or_session_rejected(self):
        job_id = self.job()
        self.store.claim()
        with self.assertRaises(ValueError):
            self.store.record(job_id, 1, self.result(job_id, 'needs_input'), 'invented-session')
        self.store.record(job_id, 1, self.result(job_id, 'needs_input'), SESSION)
        question = self.store.get(job_id)['question']
        for owner, chat in [(102, 101), (101, 102)]:
            with self.assertRaises(PermissionError):
                self.store.answer(job_id, question, owner, chat, 'non autorisé')
        with self.assertRaises(ValueError):
            self.store.answer(job_id, 'old-question', 101, 101, 'obsolète')

    def test_revision_invalidates_approval_and_old_button(self):
        job_id, snapshot, snapshot_hash = self.preview()
        self.store.approve(job_id, 1, snapshot_hash, 101, 101)
        self.store.revise(job_id, 1, 101, 101, 'Corriger la légende')
        self.assertIsNone(self.store.get(job_id)['approval'])
        self.assertEqual(self.store.get(job_id)['revision'], 2)
        previous = self.store.db.execute('SELECT snapshot,approval FROM revisions WHERE job=? AND revision=1', (job_id,)).fetchone()
        self.assertEqual(json.loads(previous['snapshot']), snapshot)
        self.assertEqual(json.loads(previous['approval'])['snapshotHash'], snapshot_hash)
        with self.assertRaises(ValueError):
            self.store.approve(job_id, 1, snapshot_hash, 101, 101)

    def test_approval_is_bound_to_all_snapshot_fields(self):
        job_id, snapshot, snapshot_hash = self.preview()
        for key, value in [('videoSha256', 'b' * 64), ('captions', {'test-channel': 'Autre texte'}),
                           ('destinations', ['another-channel']), ('schedule', '2026-11-01T10:00:00Z')]:
            with self.assertRaises(ValueError):
                self.store.approve(job_id, 1, digest(snapshot | {key: value}), 101, 101)
        self.assertEqual(self.store.get(job_id)['status'], 'awaiting_approval')

    def test_double_click_is_atomic_even_outside_n8n(self):
        job_id, snapshot, snapshot_hash = self.preview()
        def click(_):
            other = Store(self.path)
            try:
                other.approve(job_id, 1, snapshot_hash, 101, 101)
                return True
            except ValueError:
                return False
            finally:
                other.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(click, range(2))), [False, True])

    def test_approval_survives_restart_without_publication(self):
        job_id, snapshot, snapshot_hash = self.preview()
        result = self.store.approve(job_id, 1, snapshot_hash, 101, 101)
        self.assertFalse(result['published'])
        self.store.close()
        self.store = Store(self.path)
        self.assertEqual(self.store.get(job_id)['approval']['snapshotHash'], snapshot_hash)
        # Nouveau processus Python, pas seulement une nouvelle connexion en mémoire.
        check = subprocess.run([sys.executable, '-c',
            'from automation.store import Store; import sys,json; s=Store(sys.argv[1]); print(json.dumps(s.get(sys.argv[2])["approval"])); s.close()',
            str(self.path), job_id], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(check.stdout)['snapshotHash'], snapshot_hash)

    def test_cancel_prevents_old_approval(self):
        job_id, snapshot, snapshot_hash = self.preview()
        self.store.cancel(job_id, 1, 101, 101)
        with self.assertRaises(ValueError):
            self.store.approve(job_id, 1, snapshot_hash, 101, 101)

    def test_restart_does_not_automatically_retry_generation(self):
        job_id = self.job()
        self.store.claim()
        self.store.close()
        self.store = Store(self.path)
        self.assertIsNone(self.store.claim())
        self.store.recover()  # Simulation d'un contrôle opérateur des processus.
        self.assertEqual(self.store.get(job_id)['status'], 'failed')
        self.assertIsNone(self.store.claim())

    def test_unknown_publication_preserves_platform_success(self):
        job_id = self.job()
        self.store.db.execute("UPDATE jobs SET status='publishing' WHERE id=?", (job_id,))
        self.store.db.execute("INSERT INTO platform_results VALUES(?,1,'test-channel','published','receipt-1',NULL)", (job_id,))
        self.store.recover()
        self.assertEqual(self.store.get(job_id)['status'], 'publication_unknown')
        self.assertEqual(self.store.db.execute('SELECT external_id FROM platform_results').fetchone()[0], 'receipt-1')

    def test_failures_remain_failures(self):
        job_id = self.job()
        self.store.claim()
        self.store.record(job_id, 1, self.result(job_id, 'failed'), SESSION)
        self.assertEqual(self.store.get(job_id)['status'], 'failed')
        self.assertIsNone(self.store.claim())

    def test_invalid_option_or_event_rejected(self):
        for option in [0, 15, True, '4']:
            with self.assertRaises(ValueError):
                self.store.create(101, 101, option)
        for event in [None, '42', True, -1]:
            with self.assertRaises(ValueError):
                self.store.event(event, lambda: None)

    def test_schema_rejects_invalid_json_shape(self):
        schema = json.loads(SCHEMA.read_text())
        result = self.result('000000000001', 'completed')
        validate_schema(result, schema)
        for invalid in [result | {'status': 'published'}, result | {'revision': True}, result | {'extra': 1}, {}]:
            with self.assertRaises(ValueError):
                validate_schema(invalid, schema)

    def test_paths_and_missing_artifacts_rejected(self):
        with self.assertRaises(ValueError):
            allowed_file('/etc/passwd', 'output/options')
        with self.assertRaises(FileNotFoundError):
            allowed_file('/nonexistent-englizy-file.mp4', 'output/options')

    def test_shell_data_never_enters_command_arguments(self):
        job = {'session': SESSION, 'brief': '$(touch /tmp/do-not-create) ; rm -rf /'}
        args = arguments(job, Path(self.tmp.name), probe=True)
        self.assertNotIn(job['brief'], args)
        self.assertIn(SESSION, args)
        self.assertNotIn('--last', args)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', args)
        self.assertIn('sandbox_mode="read-only"', args)
        with self.assertRaises(ValueError):
            arguments({'session': ';touch /tmp/no'}, Path(self.tmp.name))


class N8nTelegramManagementTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('automation_admin', Path(__file__).resolve().parents[1] / 'scripts/automation-admin.py')
        self.admin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.admin)
        self.tmp = tempfile.TemporaryDirectory()
        self.admin.STATE = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_pairing_requires_exclusive_bot_confirmation(self):
        with self.assertRaises(RuntimeError):
            self.admin.pair_start('credential-1', 'test_bot', False)

    def test_other_active_telegram_workflow_blocks_pairing(self):
        with patch.object(self.admin, 'listing', return_value=[{'id': 'other', 'active': True,
                'nodes': [{'type': 'n8n-nodes-base.telegramTrigger'}]}]):
            with self.assertRaises(RuntimeError):
                self.admin.no_other_receiver()

    def test_pairing_only_calls_n8n_and_uses_existing_credential(self):
        calls = []
        def api(path, method='GET', body=None):
            calls.append((path, method, body))
            if path.startswith('/credentials?'):
                return {'data': [{'id': 'credential-1', 'name': 'Private bot', 'type': 'telegramApi'}]}
            if path.startswith('/workflows?'):
                return {'data': []}
            if path == '/workflows' and method == 'POST':
                return body | {'id': 'pairing-1', 'versionId': 'v1'}
            return {}
        with patch.object(self.admin, 'n8n', side_effect=api), patch.object(self.admin, 'request', side_effect=AssertionError('Appel direct interdit')), patch.object(self.admin, 'wait_telegram_webhook'), patch('builtins.print'):
            self.admin.pair_start('credential-1', 'test_bot', True)
        workflow = next(c[2] for c in calls if c[0] == '/workflows')
        self.assertFalse(any(node['type'] == 'n8n-nodes-base.telegram' for node in workflow['nodes']))
        self.assertEqual(workflow['nodes'][0]['credentials']['telegramApi']['id'], 'credential-1')
        self.assertFalse(any(c[0] == '/credentials' and c[1] == 'POST' for c in calls))

    def test_candidate_is_read_from_n8n_and_not_messaged(self):
        pending = {'challenge': 'ABC123', 'credentialId': 'credential-1', 'workflowId': 'pairing-1',
                   'startedAt': self.admin.now()}
        self.admin.save('telegram-pairing.json', pending)
        message = {'text': '/start ABC123', 'date': int(__import__('time').time()),
            'from': {'id': 101, 'first_name': 'Test', 'is_bot': False}, 'chat': {'id': 101, 'type': 'private'}}
        def api(path, method='GET', body=None):
            if path.startswith('/executions?'):
                return {'data': [{'id': 'execution-1'}]}
            if path.startswith('/executions/execution-1?'):
                return {'data': {'resultData': {'runData': {'Recevoir le code d’association': [
                    {'data': {'main': [[{'json': {'message': message}}]]}}]}}}}
            if path.endswith('/unpublish'):
                return {}
            if path == '/workflows/pairing-1':
                return {}
            self.fail('Appel inattendu : ' + path)
        with patch.object(self.admin, 'n8n', side_effect=api), patch.object(self.admin, 'request', side_effect=AssertionError('Appel direct interdit')), patch.object(self.admin, 'wait_telegram_webhook'), patch('builtins.print'):
            self.admin.pair_check()
        candidate = self.admin.load('telegram-candidate.json')
        self.assertEqual(candidate['userId'], 101)
        self.assertFalse((self.admin.STATE / 'telegram-identity.json').exists())
        with patch('builtins.print'):
            self.admin.pair_confirm(101, 101)
        self.assertEqual(self.admin.load('telegram-identity.json')['credentialId'], 'credential-1')


class GitHubCredentialTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('github_local', Path(__file__).resolve().parents[1] / 'scripts/github-local.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_helper_refuses_other_repositories_or_hosts(self):
        import io
        for request in ['protocol=https\nhost=example.com\npath=mustafaHami/remotion-english-video.git\n',
                        'protocol=https\nhost=github.com\npath=other-org/other-repository.git\n']:
            with patch('sys.stdin', io.StringIO(request)), patch('sys.stdout', new_callable=io.StringIO) as output, patch.object(self.module, 'token', side_effect=AssertionError('Secret non requis')):
                self.module.helper('get')
                self.assertEqual(output.getvalue(), '')

    def test_cli_receives_token_only_in_environment(self):
        fake = 'TEST-ONLY-NOT-A-REAL-TOKEN'
        with patch('sys.argv', ['github-local.py', 'gh', 'api', 'repos/mustafaHami/remotion-english-video']), patch.object(self.module, 'token', return_value=fake), patch.object(self.module.subprocess, 'run') as execute:
            execute.return_value.returncode = 0
            with self.assertRaises(SystemExit) as result:
                self.module.main()
            self.assertEqual(result.exception.code, 0)
            self.assertNotIn(fake, execute.call_args.args[0])
            self.assertEqual(execute.call_args.kwargs['env']['GH_TOKEN'], fake)

    def test_cli_token_display_is_disabled(self):
        with patch('sys.argv', ['github-local.py', 'gh', 'auth', 'token']):
            with self.assertRaises(RuntimeError):
                self.module.main()


if __name__ == '__main__':
    unittest.main()
