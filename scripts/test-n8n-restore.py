#!/usr/bin/env python3
"""Démarrage d'une copie de sauvegarde, sans réseau, port ni volume de production."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tarfile
import tempfile
import time
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('backup', type=Path)
args = parser.parse_args()
os.umask(0o077)
backup = args.backup.resolve(strict=True)
if os.geteuid() != 0 or not backup.is_relative_to('/var/backups/englizy'):
    parser.error('Sauvegarde sous /var/backups/englizy et exécution root requises.')
manifest = json.loads((backup / 'manifest.json').read_text())
archive_path = backup / 'n8n-data.tar.gz'
with archive_path.open('rb') as stream:
    if hashlib.file_digest(stream, 'sha256').hexdigest() != manifest['sha256'][archive_path.name]:
        raise SystemExit('Empreinte de sauvegarde incorrecte.')
container = 'englizy-restore-test-' + uuid.uuid4().hex[:12]
with tempfile.TemporaryDirectory(dir=backup) as temporary:
    with tarfile.open(archive_path) as archive:
        archive.extractall(temporary, filter='data')
    data = Path(temporary) / 'data'
    db = sqlite3.connect(data / 'database.sqlite')
    # Évite toute exécution des anciens workflows, même sans accès réseau.
    db.execute('UPDATE workflow_entity SET active=0,activeVersionId=NULL')
    db.commit()
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    db.close()
    for item in [data, *data.rglob('*')]:
        os.chown(item, 1000, 1000, follow_symlinks=False)
    try:
        subprocess.run(['docker', 'run', '-d', '--pull=never', '--name', container, '--network', 'none',
            '--mount', f'type=bind,src={data},dst=/home/node/.n8n',
            '-e', 'N8N_DIAGNOSTICS_ENABLED=false', '-e', 'N8N_VERSION_NOTIFICATIONS_ENABLED=false',
            '-e', 'N8N_TEMPLATES_ENABLED=false', '-e', 'N8N_PERSONALIZATION_ENABLED=false',
            manifest['image']], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        probe = "Promise.all(['/healthz/readiness','/rest/settings'].map(p=>fetch('http://127.0.0.1:5678'+p).then(r=>{if(!r.ok)throw Error('health');return r.json()}))).then(v=>{if(v[1].data.userManagement.showSetupOnFirstLoad)throw Error('owner');console.log('restored-owner-and-health-ok')}).catch(()=>process.exit(1))"
        for attempt in range(45):
            result = subprocess.run(['docker', 'exec', container, 'node', '-e', probe], capture_output=True, text=True)
            if result.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError('La copie isolée n’a pas atteint l’état prêt.')
        report = {'container': container, 'image': manifest['image'], 'network': 'none',
                  'portsPublished': False, 'restoredOwner': True, 'readiness': True,
                  'productionDataMounted': False, 'automaticWorkflowsInCopy': 'disabled',
                  'timestamp': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
        (backup / 'restore-boot-check.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))
    finally:
        subprocess.run(['docker', 'rm', '-f', container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
