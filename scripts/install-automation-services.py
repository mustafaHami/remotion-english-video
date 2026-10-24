#!/usr/bin/env python3
"""Installe la liaison privée et les accès vidéo ciblés, sans changer Docker ni ses volumes."""
import argparse
import json
import os
from pathlib import Path
import pwd
import secrets
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--start', action='store_true')
mode = parser.add_mutually_exclusive_group()
mode.add_argument('--enable-video', action='store_true')
mode.add_argument('--diagnostic-only', action='store_true')
args = parser.parse_args()
if os.geteuid() != 0:
    parser.error('Exécuter avec sudo.')
os.umask(0o077)
for service in ['englizy-bridge', 'englizy-worker']:
    status = subprocess.run(['systemctl', 'show', '--value', '--property=ActiveState', service],
                            capture_output=True, text=True)
    if status.stdout.strip() not in ['', 'inactive', 'failed']:
        raise SystemExit('Arrêter les services à une frontière de tâche sûre avant mise à jour : ' + service)
identity = json.loads(Path('/var/lib/englizy/management/telegram-identity.json').read_text())
if identity.get('confirmation') != 'explicit-user-confirmation':
    raise SystemExit('Identité Telegram non confirmée.')
container = json.loads(subprocess.check_output(['docker', 'inspect', 'n8n-n8n-1']))[0]
networks = list(container['NetworkSettings']['Networks'].values())
if len(networks) != 1 or not networks[0].get('Gateway'):
    raise SystemExit('Réseau Docker ambigu ; relever la passerelle avant installation.')
gateway = networks[0]['Gateway']
previous_config = Path('/etc/englizy/worker.json')
video_enabled = args.enable_video or (previous_config.exists() and json.loads(previous_config.read_text()).get('videoEnabled', False))
if args.diagnostic_only:
    video_enabled = False
for name in ['englizy-bridge', 'englizy-worker']:
    home = '/var/lib/' + name
    try:
        user = pwd.getpwnam(name)
        if user.pw_dir != home:
            raise SystemExit('Compte préexistant avec un autre dossier : ' + name)
    except KeyError:
        subprocess.run(['useradd', '--system', '--user-group', '--create-home', '--home-dir', home,
                        '--shell', '/usr/sbin/nologin', name], check=True)
    user = pwd.getpwnam(name)
    path = Path(home)
    path.mkdir(mode=0o700, exist_ok=True)
    path.chmod(0o700)
    os.chown(path, user.pw_uid, user.pw_gid)
worker_user = pwd.getpwnam('englizy-worker')
bridge_user = pwd.getpwnam('englizy-bridge')
media_root = Path('/var/lib/englizy-media')
media_root.mkdir(mode=0o2750, exist_ok=True)
os.chown(media_root, worker_user.pw_uid, bridge_user.pw_gid)
media_root.chmod(0o2750)
if video_enabled:
    # Codex protège ce répertoire dans son sandbox. Il doit déjà exister sur
    # le montage parent en lecture seule, même sans configuration locale.
    for protected in ['.codex', '.aws']:
        codex_project = ROOT / protected
        if not codex_project.exists():
            codex_project.mkdir(mode=0o755)
            codex_project.chmod(0o755)
    output_parent = ROOT / 'output'
    output_parent.mkdir(mode=0o755, exist_ok=True)
    output_parent.chmod(0o755)
    for relative in ['content/episodes', 'public/audio/production', 'output/options', 'node_modules/.cache']:
        path = ROOT / relative
        path.mkdir(mode=0o755, parents=True, exist_ok=True)
        os.chown(path, 0, worker_user.pw_gid)
        path.chmod(0o1775)  # Nouveaux fichiers autorisés ; les anciens fichiers root restent protégés.
    provenance = ROOT / 'public/audio/production/provenance.json'
    if provenance.exists():
        os.chown(provenance, 0, worker_user.pw_gid)
        provenance.chmod(0o664)
destination = Path('/opt/englizy-automation')
destination.mkdir(mode=0o755, parents=True, exist_ok=True)
shutil.copytree(ROOT / 'automation', destination / 'automation', dirs_exist_ok=True,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
for path in [destination, *destination.rglob('*')]:
    path.chmod(0o755 if path.is_dir() else 0o644)
config_dir = Path('/etc/englizy')
config_dir.mkdir(mode=0o755, exist_ok=True)
config_dir.chmod(0o755)
repository_alias = Path('/srv/englizy-repository')
repository_alias.mkdir(mode=0o755, exist_ok=True)
repository_alias.chmod(0o755)
configs = {
    'bridge': {'owner': identity['userId'], 'chat': identity['chatId'], 'bind': gateway,
               'port': 8787, 'database': '/var/lib/englizy-bridge/jobs.sqlite',
               'videoEnabled': video_enabled, 'mediaRoot': str(media_root)},
    'worker': {'bridge': f'http://{gateway}:8787', 'stateDir': '/var/lib/englizy-worker/jobs',
               'videoEnabled': video_enabled, 'mediaRoot': str(media_root)},
}
# Conserver les réglages de suivi explicitement activés par l'opérateur.
old_bridge = config_dir / 'bridge.json'
if old_bridge.exists():
    previous_bridge = json.loads(old_bridge.read_text())
    for key in ['planningIndex', 'dailySummaryTime']:
        if key in previous_bridge:
            configs['bridge'][key] = previous_bridge[key]
for kind, value in configs.items():
    user = pwd.getpwnam('englizy-' + kind)
    path = config_dir / (kind + '.json')
    path.write_text(json.dumps(value, indent=2) + '\n')
    os.chown(path, 0, user.pw_gid)
    path.chmod(0o640)
for name in ['n8n-bridge-token', 'worker-bridge-token']:
    path = Path('/var/lib/englizy/secrets') / name
    if not path.exists():
        path.write_text(secrets.token_urlsafe(48))
    path.chmod(0o600)
worker = pwd.getpwnam('englizy-worker')
codex_home = Path(worker.pw_dir) / '.codex'
codex_home.mkdir(mode=0o700, exist_ok=True)
auth = codex_home / 'auth.json'
if not auth.exists():
    shutil.copyfile('/root/.codex/auth.json', auth)
    auth.chmod(0o600)
    os.chown(auth, worker.pw_uid, worker.pw_gid)
config = codex_home / 'config.toml'
if not config.exists():
    source = tomllib.loads(Path('/root/.codex/config.toml').read_text())
    if source.get('model_provider', 'openai') != 'openai':
        raise SystemExit('Fournisseur Codex personnalisé : examiner sa configuration sans recopier de secrets.')
    text = '\n'.join(k + ' = ' + json.dumps(source[k]) for k in ['model', 'model_reasoning_effort'] if k in source)
    config.write_text(text + '\ncli_auth_credentials_store = "file"\n')
    config.chmod(0o600)
    os.chown(config, worker.pw_uid, worker.pw_gid)
os.chown(codex_home, worker.pw_uid, worker.pw_gid)
git_config = Path(worker.pw_dir) / '.gitconfig'
if not git_config.exists():
    git_config.write_text('[safe]\n\tdirectory = /srv/englizy-repository\n')
    os.chown(git_config, worker.pw_uid, worker.pw_gid)
    git_config.chmod(0o600)
for service in ['englizy-bridge', 'englizy-worker']:
    target = Path('/etc/systemd/system') / (service + '.service')
    shutil.copyfile(ROOT / 'deploy/n8n' / (service + '.service'), target)
    target.chmod(0o644)
dropin = Path('/etc/systemd/system/englizy-worker.service.d/20-video.conf')
if video_enabled:
    dropin.parent.mkdir(mode=0o755, exist_ok=True)
    shutil.copyfile(ROOT / 'deploy/n8n/englizy-worker-video.conf', dropin)
    dropin.chmod(0o644)
elif dropin.exists():
    dropin.unlink()  # Notre seule dérogation vidéo ; aucun autre drop-in n'est touché.
subprocess.run(['systemd-analyze', 'verify', '/etc/systemd/system/englizy-bridge.service',
                '/etc/systemd/system/englizy-worker.service'], check=True)
subprocess.run(['systemctl', 'daemon-reload'], check=True)
if args.start:
    subprocess.run(['systemctl', 'enable', '--now', 'englizy-bridge.service', 'englizy-worker.service'], check=True)
print(json.dumps({'installed': True, 'started': args.start, 'bridge': f'http://{gateway}:8787',
                  'mode': 'video-preview' if video_enabled else 'probe-only',
                  'repositoryAccess': 'read-only with targeted data/output mounts' if video_enabled else 'read-only bind mount',
                  'codexAuth': 'private service cache; no secret in Git or logs'}))
