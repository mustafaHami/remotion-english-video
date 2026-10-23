#!/usr/bin/env python3
"""Démarrage d'une copie de sauvegarde, sans réseau, port ni volume de production."""
import argparse
import datetime
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
parser.add_argument('--check-pruning', action='store_true', help='Teste la purge native sur des dates modifiées uniquement dans la copie isolée.')
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
    pruning_ids = []
    if args.check_pruning:
        pruning_ids = [row[0] for row in db.execute("SELECT id FROM execution_entity WHERE status='success' ORDER BY id DESC LIMIT 4")]
        if len(pruning_ids) != 4:
            raise RuntimeError('Quatre exécutions terminées sont requises dans la copie pour ce test.')
        current = datetime.datetime.now(datetime.timezone.utc)
        old = (current - datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S.000')
        recent = current.strftime('%Y-%m-%d %H:%M:%S.000')
        # Ancienne terminée, suppression déjà marquée, terminée récente, attente ancienne.
        db.execute('UPDATE execution_entity SET startedAt=?,stoppedAt=?,deletedAt=NULL WHERE id=?', (old, old, pruning_ids[0]))
        db.execute('UPDATE execution_entity SET deletedAt=? WHERE id=?', (old, pruning_ids[1]))
        db.execute('UPDATE execution_entity SET startedAt=?,stoppedAt=?,deletedAt=NULL WHERE id=?', (recent, recent, pruning_ids[2]))
        db.execute("UPDATE execution_entity SET status='waiting',finished=0,startedAt=?,stoppedAt=NULL,deletedAt=NULL,waitTill='2099-01-01 00:00:00.000' WHERE id=?", (old, pruning_ids[3]))
    db.commit()
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    db.close()
    for item in [data, *data.rglob('*')]:
        os.chown(item, 1000, 1000, follow_symlinks=False)
    try:
        pruning_environment = ['-e', 'EXECUTIONS_DATA_PRUNE=true', '-e', 'EXECUTIONS_DATA_MAX_AGE=336',
                               '-e', 'EXECUTIONS_DATA_HARD_DELETE_BUFFER=0',
                               '-e', 'EXECUTIONS_DATA_PRUNE_SOFT_DELETE_INTERVAL=1',
                               '-e', 'EXECUTIONS_DATA_PRUNE_HARD_DELETE_INTERVAL=1'] if args.check_pruning else []
        subprocess.run(['docker', 'run', '-d', '--pull=never', '--name', container, '--network', 'none',
            '--mount', f'type=bind,src={data},dst=/home/node/.n8n',
            '-e', 'N8N_DIAGNOSTICS_ENABLED=false', '-e', 'N8N_VERSION_NOTIFICATIONS_ENABLED=false',
            '-e', 'N8N_TEMPLATES_ENABLED=false', '-e', 'N8N_PERSONALIZATION_ENABLED=false',
            *pruning_environment, manifest['image']], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
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
        if args.check_pruning:
            print('Copie isolée prête ; observation de la purge native avec intervalles de test de 1 minute.', flush=True)
            for attempt in range(90):
                check = sqlite3.connect(f'file:{data / "database.sqlite"}?mode=ro', uri=True)
                remaining = {row[0]: row[1] for row in check.execute('SELECT id,status FROM execution_entity WHERE id IN (?,?,?,?)', pruning_ids)}
                check.close()
                if all(identifier not in remaining for identifier in pruning_ids[:2]):
                    break
                time.sleep(2)
            else:
                raise RuntimeError('La purge native n’a pas supprimé les deux anciennes exécutions de test.')
            assert remaining.get(pruning_ids[2]) == 'success'
            assert remaining.get(pruning_ids[3]) == 'waiting'
            report['pruning'] = {'oldFinishedRemoved': True, 'deletionMarkerRemoved': True,
                                 'recentFinishedPreserved': True, 'waitingPreserved': True,
                                 'syntheticDatesInIsolatedCopy': True, 'testIntervalsMinutes': 1,
                                 'testHardDeleteBufferHours': 0,
                                 'productionConfigurationChanged': False}
            (backup / 'restore-pruning-check.json').write_text(json.dumps(report, indent=2) + '\n')
        (backup / 'restore-boot-check.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))
    finally:
        subprocess.run(['docker', 'rm', '-f', container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
