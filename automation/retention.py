"""Rétention autorisée : vidéos shared 10 j, détails des tâches closes 15 j."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3


def aged(value, days, moment):
    return bool(value) and moment >= datetime.datetime.fromisoformat(value) + datetime.timedelta(days=days)


def apply(store, root, spool, backup_dir, moment=None):
    moment = moment or datetime.datetime.now(datetime.timezone.utc)
    root, spool = Path(root).resolve(), Path(spool).resolve()
    candidates = [dict(r) for r in store.db.execute("SELECT * FROM jobs WHERE purged_at IS NULL AND closed_at IS NOT NULL")]
    eligible = [j for j in candidates if
                (j['status'] == 'shared' and aged(j['shared_at'], 10, moment) and not j['media_deleted_at']) or
                (j['status'] in ['shared','cancelled','completed'] and aged(j['closed_at'], 15, moment))]
    if not eligible:
        return {'mediaDeleted': [], 'detailsPurged': []}
    backup_dir = Path(backup_dir); backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    backup = backup_dir / ('before-retention-' + moment.strftime('%Y%m%dT%H%M%S%f') + '.sqlite')
    copy = sqlite3.connect(backup)
    store.db.backup(copy); copy.close(); backup.chmod(0o600)
    report = {'mediaDeleted': [], 'detailsPurged': []}
    for j in eligible:
        # Empêcher toute suppression par état technique accidentel ou timestamp isolé.
        if j['status'] == 'shared':
            evidence = json.loads(j['sharing'] or '{}')
            if (not evidence.get('confirmation') or evidence.get('allDestinationsConfirmed') is not True
                    or evidence.get('source') not in ['explicit-user-confirmation','platform-receipts']):
                raise ValueError('Publication non confirmée : purge refusée.')
        if j['status'] == 'shared' and aged(j['shared_at'], 10, moment) and not j['media_deleted_at']:
            original = json.loads(j['result'])['artifacts']['video']
            relative = original.removeprefix('/srv/englizy-repository/')
            path = root / relative
            if path.is_absolute() and not path.is_relative_to(root):
                raise ValueError('MP4 hors du dépôt.')
            descriptor = store.db.execute('SELECT media FROM preview_media WHERE job=? AND revision=?', (j['id'],j['revision'])).fetchone()
            if not descriptor:
                raise ValueError('Empreintes média absentes ; purge refusée.')
            media = json.loads(descriptor[0])
            preview = spool / f"{j['id']}/r{j['revision']}/preview.mp4"
            if not re.fullmatch('[a-f0-9]{12}', j['id']):
                raise ValueError('Identifiant invalide.')
            if path.resolve().parent.parent != root / 'output/options' / f"option-{j['option']}":
                raise ValueError('MP4 hors dossier de réalisation.')
            files = [(path, media['originalSha256'], root / 'output/options'), (preview, media['sha256'], spool)]
            for file, expected, allowed in files:
                if file.is_symlink() or not file.resolve().is_relative_to(allowed):
                    raise ValueError('Lien ou chemin de suppression interdit.')
                if file.exists():
                    if file.suffix != '.mp4' or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
                        raise ValueError('MP4 modifié : purge refusée.')
            with store.tx():
                store.audit(j['id'], 'media-deletion-started', {'revision':j['revision'], 'sharedAt':j['shared_at']})
            # Une interruption entre les deux suppressions peut reprendre sans toucher d'autres fichiers.
            for file, _, _ in files:
                file.unlink(missing_ok=True)
            with store.tx():
                store.db.execute('UPDATE jobs SET media_deleted_at=? WHERE id=?', (moment.isoformat(),j['id']))
                store.audit(j['id'], 'media-deleted', {'revision':j['revision']})
            report['mediaDeleted'].append(j['id'])
            j['media_deleted_at'] = moment.isoformat()
        if aged(j['closed_at'], 15, moment) and (j['status'] != 'shared' or j['media_deleted_at']):
            if j['status'] not in ['shared','cancelled','completed']:
                continue
            if store.db.execute("SELECT 1 FROM outbox WHERE job=? AND status IN ('pending','delivering','delivery_unknown')", (j['id'],)).fetchone():
                continue  # Une notification non résolue garde son contexte.
            with store.tx():
                # Conserver les identifiants/reçus minimaux : les retries ne recréent rien.
                store.db.execute('DELETE FROM questions WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM revisions WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM preview_media WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM audit WHERE job=?', (j['id'],))
                store.db.execute('UPDATE outbox SET payload=? WHERE job=?',
                                 (json.dumps({'kind':'tombstone','jobId':j['id']}), j['id']))
                store.db.execute("UPDATE jobs SET result=NULL,session=NULL,question=NULL,brief='',snapshot=NULL,approval=NULL,purged_at=? WHERE id=?",
                                 (moment.isoformat(),j['id']))
                store.audit(j['id'], 'closed-details-purged', {'closedAt':j['closed_at'],'minimalRecordRetained':True})
            report['detailsPurged'].append(j['id'])
    return report
