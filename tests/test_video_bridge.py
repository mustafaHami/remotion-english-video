"""Choix et transport de prévisualisation simulés : aucun rendu ni appel Telegram."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from automation.bridge import Application
from automation.store import Store
from automation import worker


class VideoBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.spool = self.root / 'media'
        self.spool.mkdir()
        self.config = {'database': str(self.root / 'jobs.sqlite'), 'owner': 101, 'chat': 101,
                       'videoEnabled': True, 'mediaRoot': str(self.spool)}
        self.app = Application(self.config)

    def tearDown(self):
        self.tmp.cleanup()

    def update(self, event, text):
        return {'update_id': event, 'message': {'text': text, 'from': {'id': 101}, 'chat': {'id': 101, 'type': 'private'}}}

    def menu(self):
        self.app.route('n8n', '/telegram', self.update(1, '/video'))
        store = Store(self.config['database'])
        menu = store.pending()[0]['payload']
        store.close()
        return menu

    def choice(self, menu, event=2, sender=101, index=0):
        button = menu['keyboard']['rows'][index]['row']['buttons'][0]
        return {'update_id': event, 'callback_query': {'id': str(event), 'data': button['additionalFields']['callback_data'],
                'from': {'id': sender}, 'message': {'chat': {'id': 101, 'type': 'private'}}}}

    def job(self):
        menu = self.menu()
        result = self.app.route('n8n', '/telegram', self.choice(menu))
        claim = self.app.route('worker', '/worker/claim', {'claimId': 'a' * 32})['job']
        self.assertEqual(claim['id'], result['jobId'])
        return claim

    def result(self, job, status='completed'):
        return {'jobId': job['id'], 'revision': 1, 'status': status,
                'sessionId': '01a168f3-7278-75b2-aa8f-ccaf2902b955', 'questionId': None,
                'question': 'Précision nécessaire ?' if status == 'needs_input' else None,
                'artifacts': dict.fromkeys(['video', 'episode', 'manifest', 'inspection']),
                'checks': {'technicalVideo': True, 'visualImages': True, 'subjectiveListening': False, 'notes': []},
                'summary': 'Prévisualisation simulée', 'error': None}

    def preview(self, job):
        path = self.spool / job['id'] / 'r1/preview.mp4'
        path.parent.mkdir(parents=True)
        data = b'fake-mp4-for-transport-test' * 100
        path.write_bytes(data)
        return {'path': str(path.relative_to(self.spool)), 'sha256': hashlib.sha256(data).hexdigest(),
                'originalSha256': 'b' * 64, 'size': len(data), 'compressed': False,
                'width': 1080, 'height': 1920, 'duration': 33.0}

    def submit(self, job, preview):
        with patch('automation.media.probe', return_value={'width': 1080, 'height': 1920, 'duration': 33.0}):
            return self.app.route('worker', '/worker/result', {'lease': job['lease'], 'result': self.result(job), 'preview': preview})

    def test_menu_has_all_14_options_and_double_click_creates_one_job(self):
        menu = self.menu()
        self.assertEqual(sum(len(r['row']['buttons']) for r in menu['keyboard']['rows']), 14)
        first = self.app.route('n8n', '/telegram', self.choice(menu))
        self.app = Application(self.config)
        second = self.app.route('n8n', '/telegram', self.choice(menu, event=3, index=1))
        self.assertEqual(first['jobId'], second['jobId'])
        self.assertTrue(second['alreadySelected'])
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 1)
        store.close()

    def test_foreign_click_and_unknown_menu_cannot_start_video(self):
        menu = self.menu()
        with self.assertRaises(PermissionError):
            self.app.route('n8n', '/telegram', self.choice(menu, sender=102))
        invalid = self.choice(menu)
        invalid['callback_query']['data'] = 'video:aaaaaaaaaaaa:4'
        self.app.route('n8n', '/telegram', invalid)
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 0)
        store.close()

    def test_number_in_open_menu_takes_priority_over_old_diagnostic_question(self):
        old = self.app.route('n8n', '/diagnostics', {})
        claim = self.app.route('worker', '/worker/claim', {'claimId': 'c' * 32})['job']
        self.app.route('worker', '/worker/result', {'lease': claim['lease'], 'result': self.result(claim, 'needs_input')})
        self.menu()
        chosen = self.app.route('n8n', '/telegram', self.update(10, '1'))
        store = Store(self.config['database'])
        self.assertEqual(store.get(old['jobId'])['status'], 'needs_input')
        self.assertEqual(store.get(chosen['jobId'])['kind'], 'video')
        self.assertEqual(store.get(chosen['jobId'])['option'], 1)
        store.close()

    def test_preview_delivery_preserves_result_and_never_approves_publication(self):
        job = self.job()
        preview = self.preview(job)
        self.submit(job, copy.deepcopy(preview))
        self.submit(job, copy.deepcopy(preview))
        notes = self.app.route('n8n', '/outbox/claim', {'dispatchId': 'test-preview'})['notifications']
        video = next(n for n in notes if n['kind'] == 'video')
        self.assertEqual(video['mediaPath'], '/media/' + job['id'] + '/1')
        self.assertIn('Écoute subjective non effectuée', video['text'])
        self.assertEqual(len(self.app.video('n8n', job['id'], 1)), preview['size'])
        with self.assertRaises(PermissionError):
            self.app.video('worker', job['id'], 1)
        self.app.route('n8n', '/outbox/receipt', {'id': video['id'], 'messageId': 77, 'chatId': 101})
        self.app = Application(self.config)
        store = Store(self.config['database'])
        self.assertEqual(store.get(job['id'])['status'], 'awaiting_review')
        self.assertIsNone(store.get(job['id'])['approval'])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM preview_media').fetchone()[0], 1)
        store.close()
        self.assertFalse(any(n['kind'] == 'video' for n in self.app.route('n8n', '/outbox/claim', {'dispatchId': 'next'})['notifications']))
        for path in ['/publish', '/approve']:
            with self.assertRaises(PermissionError):
                self.app.route('n8n', path, {})

    def test_changed_video_cannot_be_downloaded(self):
        job = self.job()
        preview = self.preview(job)
        self.submit(job, preview)
        (self.spool / preview['path']).write_bytes(b'x' * preview['size'])
        with self.assertRaises(ValueError):
            self.app.video('n8n', job['id'], 1)

    def test_outside_path_and_bad_hash_roll_back_completed_result(self):
        job = self.job()
        preview = self.preview(job)
        for field, value in [('path', '../secret'), ('sha256', '0' * 64), ('size', 100_000_000)]:
            altered = dict(preview, **{field: value})
            with self.assertRaises(ValueError):
                self.submit(job, altered)
        store = Store(self.config['database'])
        self.assertEqual(store.get(job['id'])['status'], 'generating')
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM preview_media').fetchone()[0], 0)
        store.close()

    def test_worker_invokes_video_mode_and_relays_necessary_question(self):
        menu = self.menu()
        self.app.route('n8n', '/telegram', self.choice(menu))
        config = {'stateDir': str(self.root / 'worker'), 'bridge': 'http://invalid.test', 'videoEnabled': True}
        def transport(url, token, path, body):
            return self.app.route('worker', path, body)
        with patch.object(worker, 'request', side_effect=transport), patch.object(worker, 'run', side_effect=lambda j,*a,**k: self.result(j, 'needs_input')) as run:
            worker.cycle(config, 'fake')
        self.assertFalse(run.call_args.kwargs['probe'])
        store = Store(self.config['database'])
        self.assertEqual(store.db.execute('SELECT status FROM jobs').fetchone()[0], 'needs_input')
        store.close()

    def test_restart_during_preview_preparation_never_calls_codex_again(self):
        job = self.job()
        config = {'stateDir': str(self.root / 'worker'), 'bridge': 'http://invalid.test',
                  'videoEnabled': True, 'mediaRoot': str(self.spool)}
        directory = Path(config['stateDir'])
        directory.mkdir()
        state = {'phase': 'preparing', 'job': job, 'result': self.result(job)}
        worker.save(directory / 'active.json', state)
        preview = self.preview(job)
        def transport(url, token, path, body):
            return self.app.route('worker', path, body)
        with patch.object(worker, 'request', side_effect=transport), patch.object(worker, 'run') as run, \
                patch('automation.media.prepare', return_value=preview), \
                patch('automation.media.probe', return_value={'width': 1080, 'height': 1920, 'duration': 33.0}):
            worker.cycle(config, 'fake')
        run.assert_not_called()
        self.assertFalse((directory / 'active.json').exists())
        store = Store(self.config['database'])
        self.assertEqual(store.get(job['id'])['status'], 'awaiting_preview')
        store.close()


if __name__ == '__main__':
    unittest.main()
