"""Agents Codex et Claude : quotas, détection d'épuisement et isolement de Claude."""
import json
import os
from pathlib import Path
import re
import select
import subprocess
import tempfile
import time

ENGINES = ('codex', 'claude')
LABELS = {'codex': 'Codex', 'claude': 'Claude'}
# Codex garde le modèle et l'effort de la configuration privée du worker (choix utilisateur).
CLAUDE_MODEL = 'claude-opus-5-5'
CLAUDE_EFFORT = 'medium'
DETAILS = {'codex': 'réglages du compte worker', 'claude': 'Opus 5.5, effort medium'}
QUOTA_PATTERN = re.compile(r'usage limit|rate limit|quota|limit reached|limite d.utilisation', re.I)


def other(engine):
    if engine not in ENGINES:
        raise ValueError('Agent inconnu.')
    return 'claude' if engine == 'codex' else 'codex'


def claude_binary():
    return os.environ.get('ENGLIZY_CLAUDE_BIN', '/usr/local/lib/englizy-claude/claude')


def claude_token():
    """Jeton longue durée transmis par systemd ; jamais écrit dans un journal."""
    directory = os.environ.get('CREDENTIALS_DIRECTORY')
    path = Path(directory) / 'claude-token' if directory else None
    if not path or not path.is_file():
        return None
    value = path.read_text().strip()
    return value or None


def claude_config_dir():
    return os.environ.get('ENGLIZY_CLAUDE_CONFIG_DIR', str(Path(os.environ.get('HOME', '/var/lib/englizy-worker')) / '.claude'))


def window_label(minutes):
    if minutes == 300:
        return '5 h'
    if minutes == 10080:
        return 'semaine'
    if isinstance(minutes, int) and minutes > 0:
        return f'{minutes // 1440} j' if minutes % 1440 == 0 else f'{minutes // 60} h'
    return 'fenêtre'


def unknown(engine, status='unknown'):
    return {'engine': engine, 'status': status, 'exhausted': None, 'windows': []}


def parse_codex_limits(response):
    """Réponse account/rateLimits/read de codex app-server."""
    limits = response.get('rateLimits') or {}
    windows, exhausted = [], False
    for key in ('primary', 'secondary'):
        window = limits.get(key)
        if not isinstance(window, dict) or type(window.get('usedPercent')) is not int:
            continue
        used = max(0, min(100, window['usedPercent']))
        windows.append({'label': window_label(window.get('windowDurationMins')), 'remaining': 100 - used})
        exhausted = exhausted or used >= 100
    exhausted = exhausted or bool(limits.get('rateLimitReachedType')) or response.get('ordinaryUsageAllowed') is False
    if not windows and not exhausted:
        return unknown('codex')
    return {'engine': 'codex', 'status': 'ok', 'exhausted': exhausted, 'windows': windows}


def parse_claude_limits(event):
    """Événement stream-json rate_limit_event de Claude Code."""
    info = event.get('rate_limit_info') or {}
    windows, exhausted = [], info.get('status') == 'rejected'
    for key, label in (('five_hour', '5 h'), ('seven_day', 'semaine')):
        window = (info.get('unifiedWindows') or {}).get(key)
        if not isinstance(window, dict) or not isinstance(window.get('utilization'), (int, float)):
            continue
        used = max(0.0, min(1.0, float(window['utilization'])))
        windows.append({'label': label, 'remaining': round((1 - used) * 100)})
        exhausted = exhausted or used >= 1 or window.get('status') == 'rejected'
    if not windows and not exhausted:
        return unknown('claude')
    return {'engine': 'claude', 'status': 'ok', 'exhausted': exhausted, 'windows': windows}


def read_codex_quota(timeout=30):
    """Lecture seule, sans tour de modèle : aucun quota consommé."""
    env = {k: v for k, v in os.environ.items() if k in ['PATH', 'HOME', 'CODEX_HOME', 'LANG', 'LC_ALL', 'TMPDIR']}
    try:
        process = subprocess.Popen(['codex', 'app-server'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, text=True, env=env, cwd=tempfile.gettempdir())
    except OSError:
        return unknown('codex')
    deadline = time.monotonic() + timeout

    def send(message):
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()

    def receive(identifier):
        while time.monotonic() < deadline:
            ready, _, _ = select.select([process.stdout], [], [], 1)
            if not ready:
                continue
            line = process.stdout.readline()
            if not line:
                return None
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if message.get('id') == identifier:
                return message
        return None

    try:
        send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'englizy-worker', 'version': '1'}}})
        if not (receive(1) or {}).get('result'):
            return unknown('codex')
        send({'jsonrpc': '2.0', 'method': 'initialized'})
        send({'jsonrpc': '2.0', 'id': 2, 'method': 'account/rateLimits/read'})
        answer = receive(2) or {}
        return parse_codex_limits(answer['result']) if isinstance(answer.get('result'), dict) else unknown('codex')
    except (OSError, ValueError, KeyError):
        return unknown('codex')
    finally:
        process.kill()
        process.wait()


def read_claude_quota(timeout=90):
    """Appel Haiku minimal sans outil ni session : seul l'événement de quota est exploité."""
    token = claude_token()
    if not token or not Path(claude_binary()).is_file():
        return unknown('claude', 'not_configured')
    with tempfile.TemporaryDirectory() as directory:
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': directory, 'LANG': 'C.UTF-8',
               'CLAUDE_CONFIG_DIR': claude_config_dir(), 'CLAUDE_CODE_OAUTH_TOKEN': token, 'DISABLE_AUTOUPDATER': '1'}
        try:
            process = subprocess.run([claude_binary(), '-p', '--output-format', 'stream-json', '--verbose',
                                      '--model', 'claude-haiku-5-5', '--no-session-persistence', '--setting-sources', '',
                                      '--max-turns', '1', '--tools', ''], input='ok', capture_output=True, text=True,
                                     timeout=timeout, cwd=directory, env=env)
        except (OSError, subprocess.TimeoutExpired):
            return unknown('claude')
    found = None
    for line in process.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'rate_limit_event':
            found = parse_claude_limits(event)
    return found or unknown('claude')


def read_quota(engine):
    return read_codex_quota() if engine == 'codex' else read_claude_quota()


def quota_from_events(engine, events_path):
    """Épuisement signalé pendant l'exécution, indépendamment du code de sortie."""
    try:
        lines = Path(events_path).read_text().splitlines()
    except OSError:
        return False
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if engine == 'codex' and event.get('type') in ('error', 'turn.failed'):
            message = event.get('message') or (event.get('error') or {}).get('message') or ''
            if QUOTA_PATTERN.search(str(message)):
                return True
        if engine == 'claude':
            if event.get('type') == 'rate_limit_event' and parse_claude_limits(event)['exhausted']:
                return True
            if event.get('type') == 'result' and event.get('is_error') and (
                    event.get('api_error_status') == 429 or QUOTA_PATTERN.search(str(event.get('result') or ''))):
                return True
    return False


def jail(command, writable, hidden, config_dir, workdir):
    """bubblewrap : système en lecture seule, secrets et état du worker masqués,
    écriture limitée aux dossiers de fabrication et à la configuration Claude."""
    args = ['bwrap', '--die-with-parent', '--new-session', '--unshare-pid', '--unshare-ipc', '--unshare-uts',
            '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp']
    for path in hidden:
        if Path(path).is_dir():
            args += ['--tmpfs', str(path)]
    for path in writable:
        args += ['--bind', str(path), str(path)]
    args += ['--bind', str(config_dir), str(config_dir), '--setenv', 'HOME', '/tmp', '--chdir', str(workdir), '--']
    return args + list(command)
