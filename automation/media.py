"""Copie de prévisualisation privée ; aucune URL publique ni appel Telegram."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

MAX_BYTES = 47 * 1024 * 1024


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                            capture_output=True, text=True, check=True, timeout=60)
    data = json.loads(result.stdout)
    video = next(s for s in data['streams'] if s['codec_type'] == 'video')
    if video['codec_name'] != 'h264' or not any(s['codec_type'] == 'audio' for s in data['streams']):
        raise ValueError('Prévisualisation MP4 H.264 avec audio requise.')
    return {'width': video['width'], 'height': video['height'], 'duration': float(data['format']['duration'])}


def prepare(result, root, spool):
    """Appelé après validation indépendante du résultat et du MP4 original par le runner."""
    original = (Path(root) / result['artifacts']['video']).resolve(strict=True)
    relative = f"{result['jobId']}/r{result['revision']}/preview.mp4"
    destination = Path(spool) / relative
    # Le groupe et le bit setgid sont hérités du spool sans chmod setgid,
    # interdit par RestrictSUIDSGID. Le worker est mono-thread.
    previous_mask = os.umask(0o027)
    try:
        destination.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    finally:
        os.umask(previous_mask)
    original_hash = sha256(original)
    compressed = original.stat().st_size > MAX_BYTES
    temporary = destination.with_name('preview.tmp.mp4')
    if compressed:
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', str(original),
                        '-vf', 'scale=720:1280', '-c:v', 'libx264', '-preset', 'medium', '-crf', '26',
                        '-threads', '2', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(temporary)],
                       check=True, timeout=1200, capture_output=True)
    else:
        shutil.copyfile(original, temporary)
    size = temporary.stat().st_size
    if not 1024 <= size <= MAX_BYTES:
        raise ValueError('Prévisualisation trop volumineuse ; aucun envoi Telegram effectué.')
    info = probe(temporary)
    preview_hash = sha256(temporary)
    if destination.exists() and sha256(destination) != preview_hash:
        raise ValueError('Prévisualisation de cette version déjà présente avec une autre empreinte.')
    temporary.chmod(0o640)
    with temporary.open('rb') as stream:
        os.fsync(stream.fileno())
    temporary.replace(destination)
    return {'path': relative, 'sha256': preview_hash, 'originalSha256': original_hash,
            'size': size, 'compressed': compressed, **info}


def checked_path(spool, job_id, revision, media):
    if (not re.fullmatch('[a-f0-9]{12}', job_id) or type(revision) is not int or revision < 1
            or media.get('path') != f'{job_id}/r{revision}/preview.mp4'
            or not re.fullmatch('[a-f0-9]{64}', media.get('sha256', ''))
            or not re.fullmatch('[a-f0-9]{64}', media.get('originalSha256', ''))
            or type(media.get('size')) is not int or not 1024 <= media['size'] <= MAX_BYTES
            or type(media.get('compressed')) is not bool):
        raise ValueError('Métadonnées de prévisualisation invalides.')
    base = Path(spool).resolve(strict=True)
    path = (base / media['path']).resolve(strict=True)
    if not path.is_relative_to(base) or not path.is_file() or path.stat().st_size != media['size']:
        raise ValueError('Prévisualisation hors périmètre ou modifiée.')
    return path


def read_verified(spool, job_id, revision, media):
    path = checked_path(spool, job_id, revision, media)
    with path.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) != media['size'] or hashlib.sha256(data).hexdigest() != media['sha256']:
        raise ValueError('Empreinte de prévisualisation modifiée ; envoi refusé.')
    return data
