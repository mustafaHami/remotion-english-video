"""La purge ne cible que les scrutations vides, jamais les preuves d'envoi."""
import copy
import json
from pathlib import Path
import runpy
import unittest

is_empty = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/prune-empty-notification-executions.py'))['is_empty_poll']


class RetentionTests(unittest.TestCase):
    def test_only_completed_empty_notification_polls_are_removable(self):
        run = {'workflowId': 'notifications', 'status': 'success', 'finished': True, 'mode': 'trigger',
               'data': {'resultData': {'runData': {
                   'Consulter les notifications en attente': [{}],
                   'Réserver les notifications sans doublon': [{'data': {'main': [[{'json': {'notifications': []}}]]}}],
                   'Préparer chaque notification': [{}]}}}}
        self.assertTrue(is_empty(run, 'notifications'))
        for key, value in [('workflowId', 'ingress'), ('status', 'error'), ('finished', False),
                           ('mode', 'manual'), ('customData', {'important': 'true'})]:
            altered = copy.deepcopy(run)
            altered[key] = value
            self.assertFalse(is_empty(altered, 'notifications'))
        altered = copy.deepcopy(run)
        altered['data']['resultData']['runData']['Envoyer la question ou le résultat'] = [{}]
        self.assertFalse(is_empty(altered, 'notifications'))
        altered = copy.deepcopy(run)
        altered['data']['resultData']['runData']['Réserver les notifications sans doublon'][0]['data']['main'][0][0]['json']['notifications'] = [{'id': 'question'}]
        self.assertFalse(is_empty(altered, 'notifications'))

    def test_export_keeps_errors_without_poll_success_or_manual_data(self):
        path = Path(__file__).resolve().parents[1] / 'deploy/n8n/workflows/telegram-notifications.json'
        workflow = json.loads(path.read_text())
        self.assertEqual(workflow['settings']['saveDataSuccessExecution'], 'none')
        self.assertEqual(workflow['settings']['saveDataErrorExecution'], 'all')
        self.assertFalse(workflow['settings']['saveManualExecutions'])
        send = next(n for n in workflow['nodes'] if n['type'] == 'n8n-nodes-base.telegram')
        self.assertFalse(send.get('retryOnFail', False))


if __name__ == '__main__':
    unittest.main()
