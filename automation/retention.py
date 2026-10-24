"""Rétention autorisée : vidéos shared 10 j, détails des tâches closes 15 j."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import shutil
import uuid


def aged(value, days, moment):
    return bool(value) and moment >= datetime.datetime.fromisoformat(value) + datetime.timedelta(days=days)


def purge_worker_artifacts(store, job, worker_root='/var/lib/englizy-worker'):
    """Remove this closed job's Codex and Claude transcripts only after checking every durable reference."""
    base = Path(worker_root)
    runs_root = base / 'jobs' / 'runs'
    sessions_root = base / '.codex' / 'sessions'
    job_id = job['id']
    if not re.fullmatch(r'[a-f0-9]{12}', job_id):
        raise ValueError('Identifiant invalide pour purge Codex.')
    ids = set()
    if job.get('session'):
        ids.add(str(uuid.UUID(job['session'])))
    run_dir = runs_root / job_id
    if (runs_root.is_symlink() or (base / '.codex').is_symlink() or sessions_root.is_symlink()
            or run_dir.is_symlink() or (run_dir.exists() and run_dir.resolve().parent != runs_root.resolve())):
        raise ValueError('Dossier de tâche Codex hors chemin ou lien interdit.')
    if run_dir.exists():
        if not run_dir.is_dir():
            raise ValueError('Le chemin des journaux Codex n’est pas un dossier.')
        for event_file in run_dir.glob('*/events.jsonl'):
            if (event_file.is_symlink() or event_file.parent.is_symlink()
                    or not event_file.resolve().is_relative_to(run_dir.resolve())):
                raise ValueError('Journal Codex lié ou hors dossier.')
            with event_file.open() as stream:
                for line in stream:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if event.get('type') == 'thread.started':
                        ids.add(str(uuid.UUID(event['thread_id'])))
                    elif event.get('type') == 'system' and event.get('subtype') == 'init' and event.get('session_id'):
                        ids.add(str(uuid.UUID(event['session_id'])))
    if sessions_root.is_symlink():
        raise ValueError('Répertoire des sessions Codex lié : purge refusée.')
    sessions_root_resolved = sessions_root.resolve()
    for session_id in ids:
        # Any other retained task may still need the same exact session.
        reference = store.db.execute(
            'SELECT 1 FROM jobs WHERE id<>? AND session=? AND purged_at IS NULL LIMIT 1',
            (job_id, session_id)).fetchone()
        if reference:
            continue
        for rollout in sessions_root.rglob(f'*{session_id}*.jsonl') if sessions_root.exists() else ():
            if rollout.is_symlink() or not rollout.resolve().is_relative_to(sessions_root_resolved) or not rollout.is_file():
                raise ValueError('Transcription Codex liée ou hors répertoire des sessions.')
            rollout.unlink()
        claude_root = base / '.claude' / 'projects'
        if claude_root.is_symlink():
            raise ValueError('Répertoire des sessions Claude lié : purge refusée.')
        for transcript in claude_root.glob(f'*/{session_id}.jsonl') if claude_root.is_dir() else ():
            if transcript.is_symlink() or not transcript.resolve().is_relative_to(claude_root.resolve()):
                raise ValueError('Transcription Claude liée ou hors répertoire des sessions.')
            transcript.unlink()
            companion = transcript.with_suffix('')
            if companion.is_dir() and not companion.is_symlink():
                shutil.rmtree(companion)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def apply(store, root, spool, backup_dir, moment=None, public_media='/var/lib/englizy-public-media',
          worker_root='/var/lib/englizy-worker'):
    moment = moment or datetime.datetime.now(datetime.timezone.utc)
    root, spool = Path(root).resolve(), Path(spool).resolve()
    candidates = [dict(r) for r in store.db.execute("SELECT * FROM jobs WHERE purged_at IS NULL AND closed_at IS NOT NULL")]
    eligible = [j for j in candidates if
                (j['status'] == 'shared' and aged(j['shared_at'], 10, moment) and not j['media_deleted_at']) or
                (j['status'] in ['shared','cancelled','completed'] and aged(j['closed_at'], 15, moment))]
    if not eligible:
        return {'mediaDeleted': [], 'detailsPurged': [], 'codexArtifactsPurged': []}
    backup_dir = Path(backup_dir); backup_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    backup = backup_dir / ('before-retention-' + moment.strftime('%Y%m%dT%H%M%S%f') + '.sqlite')
    copy = sqlite3.connect(backup)
    store.db.backup(copy); copy.close(); backup.chmod(0o600)
    report = {'mediaDeleted': [], 'detailsPurged': [], 'codexArtifactsPurged': []}
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
            if store.db.execute("SELECT 1 FROM sqlite_master WHERE name='buffer_media'").fetchone():
                public_root = Path(public_media)
                for item in store.db.execute('SELECT * FROM buffer_media WHERE job=?',(j['id'],)):
                    if (public_root.is_symlink() or not re.fullmatch('[a-f0-9]{64}[.]mp4',item['filename'])
                            or item['sha256'] != media['originalSha256']):
                        raise ValueError('Copie Buffer non reconnue ; purge refusée.')
                    files.append((public_root/item['filename'],item['sha256'],public_root.resolve()))
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
            # Filesystem cleanup is idempotent and precedes erasing the durable session UUID.
            purge_worker_artifacts(store, j, worker_root)
            with store.tx():
                # Conserver les identifiants/reçus minimaux : les retries ne recréent rien.
                store.db.execute('DELETE FROM questions WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM revisions WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM preview_media WHERE job=?', (j['id'],))
                store.db.execute('DELETE FROM audit WHERE job=?', (j['id'],))
                if store.db.execute("SELECT 1 FROM sqlite_master WHERE name='buffer_drafts'").fetchone():
                    store.db.execute("UPDATE buffer_drafts SET payload='{}',response=NULL WHERE job=?",(j['id'],))
                    store.db.execute('DELETE FROM buffer_media WHERE job=?',(j['id'],))
                if store.db.execute("SELECT 1 FROM sqlite_master WHERE name='buffer_publications'").fetchone():
                    for r in store.db.execute('SELECT post_id,response FROM buffer_publications WHERE job=?',(j['id'],)).fetchall():
                        response=json.loads(r['response'] or '{}')
                        minimal={k:response.get(k) for k in ['status','sentAt','externalLink']}
                        store.db.execute("UPDATE buffer_publications SET expected='{}',edit_input='{}',response=? WHERE post_id=?",(json.dumps(minimal),r['post_id']))
                store.db.execute('UPDATE outbox SET payload=? WHERE job=?',
                                 (json.dumps({'kind':'tombstone','jobId':j['id']}), j['id']))
                store.db.execute("UPDATE jobs SET result=NULL,session=NULL,question=NULL,brief='',snapshot=NULL,approval=NULL,purged_at=? WHERE id=?",
                                 (moment.isoformat(),j['id']))
                store.audit(j['id'], 'closed-details-purged', {'closedAt':j['closed_at'],'minimalRecordRetained':True})
            report['detailsPurged'].append(j['id'])
            report['codexArtifactsPurged'].append(j['id'])
    return report
