"""Worker supervisé : une invocation Codex ou Claude à la fois, reprise d'envoi idempotente."""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid

from .runner import run, QuotaExhausted
from .runner import ROOT
from . import cleanup
from . import engines
from . import media


def save(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def request(url, token, path, body):
    req = urllib.request.Request(url + path, data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}, method='POST')
    # Le secret interne ne doit jamais passer par un éventuel proxy d'environnement.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=30) as response:
        return json.load(response)


def latest_usage(run_root, job_id, run_started_at_ns=None):
    if run_started_at_ns is None:
        return None, None
    candidates = (Path(run_root) / job_id).glob('*/usage.json')
    for path in sorted((item for item in candidates if item.stat().st_mtime_ns >= run_started_at_ns),
                       key=lambda item: item.stat().st_mtime_ns, reverse=True):
        try:
            value = json.loads(path.read_text())
            session = value.pop('sessionId')
            return value, session
        except (OSError, ValueError, KeyError):
            continue
    return None, None


def quotas(*names):
    return {name: engines.read_quota(name) for name in names}


def clean(config, task):
    """Suppression idempotente : une reprise après panne refait les mêmes contrôles."""
    files = cleanup.remove_files(ROOT, task.get('files', []))
    private = cleanup.remove_private(task['jobId'], task.get('sessions', []), config['stateDir'], config['mediaRoot'],
                                     os.environ.get('CODEX_HOME', str(Path.home() / '.codex')), engines.claude_config_dir())
    return {'deleted': files['deleted'] + private['deleted'], 'skipped': files['skipped'] + private['skipped']}


def cycle(config, token):
    directory = Path(config['stateDir'])
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_file = directory / 'active.json'
    if state_file.exists():
        state = json.loads(state_file.read_text())
    else:
        pending = request(config['bridge'], token, '/worker/quota-request', {})
        if pending.get('requestId'):
            # Lecture sans tour de modèle pour Codex, appel Haiku minimal pour Claude.
            request(config['bridge'], token, '/worker/quotas', {'requestId': pending['requestId'], 'quotas': quotas(*engines.ENGINES)})
            return True
        state = {'phase': 'claiming', 'claimId': uuid.uuid4().hex}
        save(state_file, state)
    if state['phase'] == 'claiming':
        response = request(config['bridge'], token, '/worker/claim', {'claimId': state['claimId']})
        if response.get('cleanup'):
            state.update(phase='cleaning', cleanup=response['cleanup'])
            save(state_file, state)
        elif response['job'] is None:
            state_file.unlink()
            return False
        else:
            state.update(phase='claimed', job=response['job'], answer=response.get('answer'))
            save(state_file, state)
    if state['phase'] == 'cleaning':
        task = state['cleanup']
        try:
            report, error = clean(config, task), None
        except Exception as failure:
            report, error = None, f'{type(failure).__name__}: {failure}'[:500]
        request(config['bridge'], token, '/worker/cleanup-done', {'jobId': task['jobId'], 'lease': task['lease'],
                'report': report, 'error': error})
        state_file.unlink()
        return True
    job = state['job']
    engine = job.get('engine') or 'codex'
    is_probe = job.get('kind') == 'probe'
    if state['phase'] == 'running':
        # systemd KillMode=control-group a arrêté les anciens enfants avant ce redémarrage.
        state['usage'], state['usageSession'] = latest_usage(directory / 'runs', job['id'], state.get('runStartedAtNs'))
        state['footprint'] = cleanup.footprint(ROOT, state['baseline']) if state.get('baseline') is not None else []
        state['phase'] = 'failed'
        save(state_file, state)
    if state['phase'] == 'claimed':
        if not is_probe:
            # Avant tout travail : un agent sans quota ne commence pas la vidéo.
            check = engines.read_quota(engine)
            if check['exhausted'] is True:
                state.update(phase='quota', started=False, footprint=[],
                             quotas={engine: check} | quotas(engines.other(engine)))
                save(state_file, state)
    if state['phase'] == 'claimed':
        state['phase'] = 'running'
        state['runStartedAtNs'] = time.time_ns()
        state['baseline'] = None if is_probe else cleanup.baseline(ROOT)
        save(state_file, state)
        exhausted = False
        try:
            if not is_probe and not config.get('videoEnabled', False):
                raise ValueError('Production non activée sur ce worker.')
            result = run(job, directory / 'runs', probe=is_probe, answer=state.get('answer'), timeout=900 if is_probe else 7200)
            usage, usage_session = latest_usage(directory / 'runs', job['id'], state['runStartedAtNs'])
            if usage_session and usage_session != result['sessionId']:
                raise ValueError('Compteurs rattachés à une autre session.')
            state.update(phase='preparing' if not is_probe and result['status'] == 'completed' else 'submitting',
                         result=result, usage=usage, usageSession=result['sessionId'])
        except Exception as error:
            state['usage'], state['usageSession'] = latest_usage(directory / 'runs', job['id'], state.get('runStartedAtNs'))
            save(directory / 'last-failure.json', {'jobId': job['id'], 'type': type(error).__name__, 'error': str(error)})
            # Un échec quelconque peut cacher un quota épuisé : le compte fait foi.
            exhausted = not is_probe and (isinstance(error, QuotaExhausted) or engines.read_quota(engine)['exhausted'] is True)
            state['phase'] = 'quota' if exhausted else 'failed'
        state['footprint'] = cleanup.footprint(ROOT, state['baseline']) if state['baseline'] is not None else []
        if exhausted:
            state.update(started=True, quotas=quotas(*engines.ENGINES))
        save(state_file, state)
    if state['phase'] == 'preparing':
        # Résultat durable avant la copie : un redémarrage ne rappelle pas l'agent.
        try:
            state['preview'] = media.prepare(state['result'], ROOT, config['mediaRoot'])
            state['phase'] = 'submitting'
        except Exception as error:
            save(directory / 'last-failure.json', {'jobId': job['id'], 'type': type(error).__name__, 'error': str(error)})
            state['phase'] = 'failed'
        save(state_file, state)
    common = {'lease': job['lease'], 'usage': state.get('usage'), 'footprint': state.get('footprint', [])}
    if state['phase'] == 'submitting':
        request(config['bridge'], token, '/worker/result', common | {'result': state['result'], 'preview': state.get('preview')})
    elif state['phase'] == 'quota':
        request(config['bridge'], token, '/worker/quota-exhausted', common | {'jobId': job['id'], 'started': state['started'],
                'quotas': state['quotas'], 'sessionId': state.get('usageSession')})
    elif state['phase'] == 'failed':
        request(config['bridge'], token, '/worker/failure', common | {'jobId': job['id'], 'sessionId': state.get('usageSession')})
    state_file.unlink()
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    config = json.loads(args.config.read_text())
    token = (Path(os.environ['CREDENTIALS_DIRECTORY']) / 'worker-token').read_text().strip()
    print('Worker Codex/Claude prêt ; publication désactivée.', flush=True)
    while True:
        try:
            worked = cycle(config, token)
            time.sleep(0.5 if worked else 3)
        except (OSError, ValueError, urllib.error.URLError):
            print('Échange interne interrompu ; réservation ou résultat conservé sur disque.', flush=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
