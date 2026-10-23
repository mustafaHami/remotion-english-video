"""Worker supervisé : une invocation Codex à la fois, reprise d'envoi idempotente."""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid

from .runner import run
from .runner import ROOT
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


def cycle(config, token):
    directory = Path(config['stateDir'])
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_file = directory / 'active.json'
    if state_file.exists():
        state = json.loads(state_file.read_text())
    else:
        state = {'phase': 'claiming', 'claimId': uuid.uuid4().hex}
        save(state_file, state)
    if state['phase'] == 'claiming':
        response = request(config['bridge'], token, '/worker/claim', {'claimId': state['claimId']})
        if response['job'] is None:
            state_file.unlink()
            return False
        state.update(phase='claimed', job=response['job'], answer=response.get('answer'))
        save(state_file, state)
    elif state['phase'] == 'running':
        # systemd KillMode=control-group a arrêté les anciens enfants avant ce redémarrage.
        state['phase'] = 'failed'
        save(state_file, state)
    if state['phase'] == 'claimed':
        state['phase'] = 'running'
        save(state_file, state)
        try:
            is_probe = state['job']['kind'] == 'probe'
            if not is_probe and not config.get('videoEnabled', False):
                raise ValueError('Production non activée sur ce worker.')
            result = run(state['job'], directory / 'runs', probe=is_probe, answer=state.get('answer'), timeout=900 if is_probe else 7200)
            state.update(phase='preparing' if not is_probe and result['status'] == 'completed' else 'submitting', result=result)
        except Exception as error:
            save(directory / 'last-failure.json', {'jobId': state['job']['id'], 'type': type(error).__name__, 'error': str(error)})
            state['phase'] = 'failed'
        save(state_file, state)
    if state['phase'] == 'preparing':
        # Résultat durable avant la copie : un redémarrage ne rappelle pas Codex.
        try:
            state['preview'] = media.prepare(state['result'], ROOT, config['mediaRoot'])
            state['phase'] = 'submitting'
        except Exception as error:
            save(directory / 'last-failure.json', {'jobId': state['job']['id'], 'type': type(error).__name__, 'error': str(error)})
            state['phase'] = 'failed'
        save(state_file, state)
    job = state['job']
    if state['phase'] == 'submitting':
        request(config['bridge'], token, '/worker/result', {'lease': job['lease'], 'result': state['result'], 'preview': state.get('preview')})
    elif state['phase'] == 'failed':
        request(config['bridge'], token, '/worker/failure', {'jobId': job['id'], 'lease': job['lease']})
    state_file.unlink()
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    config = json.loads(args.config.read_text())
    token = (Path(os.environ['CREDENTIALS_DIRECTORY']) / 'worker-token').read_text().strip()
    print('Worker Codex prêt ; publication désactivée.', flush=True)
    while True:
        try:
            worked = cycle(config, token)
            time.sleep(0.5 if worked else 3)
        except (OSError, ValueError, urllib.error.URLError):
            print('Échange interne interrompu ; réservation ou résultat conservé sur disque.', flush=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
