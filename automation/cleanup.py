"""Empreinte des fichiers créés par une tâche et nettoyage contrôlé après annulation."""
import json
import os
from pathlib import Path
import re
import shutil

EPISODES = 'content/episodes'
OUTPUTS = 'output/options'
AUDIO = 'public/audio/production'
ENTRY = re.compile(r'(content/episodes/[A-Za-z0-9._-]+\.json'
                   r'|output/options/option-(?:[1-9]|1[0-4])(?:/[A-Za-z0-9._-]+)?'
                   r'|public/audio/production/[a-f0-9]{16}\.(?:wav|mp3)'
                   r'|provenance:[a-f0-9]{16})')
JOB = re.compile(r'[a-f0-9]{12}')


def valid_entry(value):
    return isinstance(value, str) and bool(ENTRY.fullmatch(value)) and '..' not in value


def provenance_keys(root):
    path = Path(root) / AUDIO / 'provenance.json'
    try:
        return set(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, ValueError):
        return set()


def baseline(root):
    """Inventaire avant exécution : une seule tâche génère à la fois."""
    root = Path(root)
    entries = set()
    for directory, pattern in ((EPISODES, '*.json'), (AUDIO, '*.wav'), (AUDIO, '*.mp3')):
        entries |= {f'{directory}/{p.name}' for p in (root / directory).glob(pattern)}
    outputs = root / OUTPUTS
    if outputs.is_dir():
        for option in outputs.iterdir():
            entries.add(f'{OUTPUTS}/{option.name}')
            if option.is_dir():
                entries |= {f'{OUTPUTS}/{option.name}/{child.name}' for child in option.iterdir()}
    entries |= {'provenance:' + key for key in provenance_keys(root)}
    return sorted(entries)


def footprint(root, before):
    """Entrées apparues depuis l'inventaire, limitées aux formes autorisées."""
    return sorted(e for e in set(baseline(root)) - set(before) if valid_entry(e))


def owned_tree(path, uid):
    if path.is_symlink() or path.lstat().st_uid != uid:
        return False
    if path.is_dir():
        for child in path.rglob('*'):
            if child.is_symlink() or child.lstat().st_uid != uid:
                return False
    return True


def referenced_audio(root, excluded):
    """Voix encore utilisées par un autre épisode ou une fiche d'option."""
    root = Path(root)
    names = set()
    candidates = [p for p in (root / EPISODES).glob('*.json') if f'{EPISODES}/{p.name}' not in excluded]
    candidates += list((root / 'src/options').glob('option-*/content.json'))
    candidates += list((root / 'src/options').glob('option-*/variants/*.json'))
    for path in candidates:
        try:
            narration = json.loads(path.read_text(encoding='utf-8')).get('narration', [])
        except (OSError, ValueError, AttributeError):
            continue
        names |= {Path(c['src']).name for c in narration if isinstance(c, dict) and isinstance(c.get('src'), str)}
    return names


def remove_files(root, entries, uid=None):
    """Supprime uniquement les fichiers de l'empreinte appartenant au compte worker."""
    root = Path(root).resolve()
    uid = os.geteuid() if uid is None else uid
    entries = [e for e in entries if valid_entry(e)]
    report = {'deleted': [], 'skipped': []}
    keep_audio = referenced_audio(root, set(entries))
    deleted_audio = set()
    # Les réalisations avant leur dossier d'option, les fichiers avant la provenance.
    for entry in sorted((e for e in entries if not e.startswith('provenance:')), key=lambda e: -e.count('/')):
        path = root / entry
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            report['skipped'].append({'path': entry, 'reason': 'lien ou chemin hors dépôt'})
            continue
        if not path.exists():
            continue
        if entry.startswith(AUDIO) and path.name in keep_audio:
            report['skipped'].append({'path': entry, 'reason': 'voix utilisée par un autre épisode'})
            continue
        if not owned_tree(path, uid):
            report['skipped'].append({'path': entry, 'reason': 'fichier non créé par le worker'})
            continue
        if path.is_dir():
            if entry.count('/') == 2 and any(path.iterdir()):
                report['skipped'].append({'path': entry, 'reason': 'dossier d’option non vide'})
                continue
            shutil.rmtree(path)
        else:
            path.unlink()
        if entry.startswith(AUDIO) and path.suffix == '.wav':
            deleted_audio.add(path.stem)
        report['deleted'].append(entry)
    keys = {e.removeprefix('provenance:') for e in entries if e.startswith('provenance:')} & deleted_audio
    if keys:
        meta = root / AUDIO / 'provenance.json'
        if meta.is_symlink():
            report['skipped'].append({'path': 'provenance.json', 'reason': 'lien interdit'})
        else:
            data = json.loads(meta.read_text(encoding='utf-8'))
            for key in keys:
                data.pop(key, None)
            # Réécriture sur place : le dossier à sticky bit interdit de remplacer le fichier root.
            with meta.open('r+', encoding='utf-8') as stream:
                stream.write(json.dumps(data, ensure_ascii=False, indent=2))
                stream.truncate()
                stream.flush()
                os.fsync(stream.fileno())
            report['deleted'] += sorted('provenance:' + k for k in keys)
    return report


def session_ids(run_dir):
    """Sessions Codex et Claude citées dans les journaux protégés de la tâche."""
    ids = set()
    for events in Path(run_dir).glob('*/events.jsonl') if Path(run_dir).is_dir() else ():
        if events.is_symlink():
            continue
        for line in events.read_text(errors='replace').splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            value = event.get('thread_id') if event.get('type') == 'thread.started' else (
                event.get('session_id') if event.get('type') == 'system' else None)
            if isinstance(value, str) and re.fullmatch(r'[0-9a-f-]{36}', value):
                ids.add(value)
    return ids


def remove_private(job_id, sessions, state_root, media_root, codex_home, claude_home):
    """Journaux, copies Telegram et transcriptions des deux agents pour cette seule tâche."""
    if not JOB.fullmatch(job_id):
        raise ValueError('Identifiant de tâche invalide.')
    report = {'deleted': [], 'skipped': []}
    run_dir = Path(state_root) / 'runs' / job_id
    ids = {s for s in sessions if isinstance(s, str) and re.fullmatch(r'[0-9a-f-]{36}', s)} | session_ids(run_dir)
    for base, pattern in ((Path(codex_home) / 'sessions', '**/*{}*.jsonl'), (Path(claude_home) / 'projects', '*/{}.jsonl')):
        if not base.is_dir() or base.is_symlink():
            continue
        for session in ids:
            for path in base.glob(pattern.format(session)):
                if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
                    report['skipped'].append({'path': str(path), 'reason': 'transcription liée ou hors dossier'})
                    continue
                path.unlink()
                report['deleted'].append('session:' + session)
                companion = path.with_suffix('')
                if companion.is_dir() and not companion.is_symlink():
                    shutil.rmtree(companion)
    for directory in (run_dir, Path(media_root) / job_id):
        if directory.is_symlink():
            report['skipped'].append({'path': str(directory), 'reason': 'lien interdit'})
        elif directory.is_dir():
            shutil.rmtree(directory)
            report['deleted'].append(str(directory))
    return report
