#!/usr/bin/env python3
"""Purge ciblée par API des scrutations vides réussies, avec archive privée préalable."""
import argparse
import json
import os
from pathlib import Path
import runpy
import urllib.parse


def is_empty_poll(execution, workflow_id):
    if (execution.get('workflowId') != workflow_id or execution.get('status') != 'success'
            or not execution.get('finished') or execution.get('mode') != 'trigger'
            or execution.get('customData') or execution.get('retryOf')):
        return False
    result = execution.get('data', {}).get('resultData', {})
    runs = result.get('runData', {})
    allowed = {'Consulter les notifications en attente', 'Réserver les notifications sans doublon',
               'Préparer chaque notification'}
    if result.get('error') or set(runs) != allowed:
        return False
    reservations = runs['Réserver les notifications sans doublon']
    if len(reservations) != 1:
        return False
    items = reservations[0].get('data', {}).get('main', [])
    return items == [[{'json': {'notifications': []}, 'pairedItem': {'item': 0}}]] or (
        len(items) == 1 and len(items[0]) == 1 and items[0][0].get('json') == {'notifications': []}
        and set(items[0][0]) <= {'json', 'pairedItem'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Exécuter avec sudo.')
    os.umask(0o077)
    admin = runpy.run_path(str(Path(__file__).resolve().parent / 'automation-admin.py'))
    workflow_id = admin['load']('codex-workflows.json')['telegram-notifications']['id']
    candidates, kept, cursor = [], [], None
    while True:
        query = '/executions?workflowId=' + workflow_id + '&status=success&includeData=true&limit=100'
        if cursor:
            query += '&cursor=' + urllib.parse.quote(cursor)
        page = admin['n8n'](query)
        for execution in page['data']:
            (candidates if is_empty_poll(execution, workflow_id) else kept).append(execution['id'])
        cursor = page.get('nextCursor')
        if not cursor:
            break
    report = {'workflowId': workflow_id, 'emptyCandidates': len(candidates), 'keptIds': kept,
              'deletedIds': [], 'startedAt': admin['now'](), 'apply': args.apply}
    if args.apply:
        directory = admin['STATE'] / ('empty-poll-archive-' + admin['now']().replace(':', '-'))
        directory.mkdir(mode=0o700)
        for identifier in candidates:
            # Relire avant suppression ; jamais supprimer les envois, erreurs ou autres workflows.
            execution = admin['n8n']('/executions/' + identifier + '?includeData=true')
            if not is_empty_poll(execution, workflow_id):
                continue
            with (directory / (identifier + '.json')).open('x') as stream:
                json.dump(execution, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            admin['n8n']('/executions/' + identifier, 'DELETE')
            report['deletedIds'].append(identifier)
            if len(report['deletedIds']) % 100 == 0:
                print(json.dumps({'emptyPollsDeleted': len(report['deletedIds'])}), flush=True)
        report['archive'] = str(directory)
        admin['save']('empty-poll-prune-report.json', report)
    print(json.dumps({'emptyCandidates': len(candidates), 'deleted': len(report['deletedIds']),
                      'usefulSuccessesKept': len(kept), 'apply': args.apply}))


if __name__ == '__main__':
    main()
