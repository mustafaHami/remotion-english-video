#!/usr/bin/env python3
"""Sauvegarde cohérente de l'installation inspectée, puis contrôle hors production."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile

if os.geteuid() != 0:
    raise SystemExit('Exécuter avec sudo.')
os.umask(0o077)
container = 'n8n-n8n-1'
info = json.loads(subprocess.check_output(['docker', 'inspect', container]))[0]
mount = next(m for m in info['Mounts'] if m['Destination'] == '/home/node/.n8n')
source = Path(mount['Source'])
compose = Path(info['Config']['Labels']['com.docker.compose.project.config_files'])
key = json.loads((source / 'config').read_text()).get('encryptionKey')
if not key:
    raise SystemExit('Clé de chiffrement absente : sauvegarde refusée.')
destination = Path('/var/backups/englizy') / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
destination.mkdir(parents=True, mode=0o700)
running = info['State']['Running']
try:
    if running:
        subprocess.run(['docker', 'stop', '--time', '30', container], check=True, stdout=subprocess.DEVNULL)
    shutil.copy2(compose, destination / 'compose.yaml')
    with tarfile.open(destination / 'n8n-data.tar.gz', 'w:gz') as archive:
        archive.add(source, arcname='data')
finally:
    if running:
        subprocess.run(['docker', 'start', container], check=True, stdout=subprocess.DEVNULL)
with tempfile.TemporaryDirectory(dir=destination) as temporary:
    with tarfile.open(destination / 'n8n-data.tar.gz') as archive:
        archive.extractall(temporary, filter='data')
    restored = Path(temporary) / 'data'
    assert json.loads((restored / 'config').read_text())['encryptionKey'] == key
    db = sqlite3.connect(restored / 'database.sqlite')
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    counts = {table: db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
              for table in ['user', 'workflow_entity', 'credentials_entity']}
    db.close()
manifest = {'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'container': container, 'image': info['Config']['Image'], 'volume': mount.get('Name'),
            'restoreCheck': 'isolated extraction, SQLite integrity, encryption key equality', 'counts': counts,
            'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in destination.iterdir() if p.is_file()}}
(destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
for p in destination.iterdir():
    if p.is_file():
        p.chmod(0o600)
print(json.dumps({'backup': str(destination), 'restoreCheck': 'passed', 'counts': counts}))
