"""États lisibles, récapitulatif et blocage des créations superflues."""
import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

LABELS = {
    'queued': 'en file', 'generating': 'création en cours', 'needs_input': 'réponse attendue',
    'awaiting_preview': 'envoi du MP4 en attente', 'pending_validation': 'vidéo à valider',
    'validated': 'validée, à publier', 'failed': 'incident à examiner',
    'shared': 'publiée, tâche close', 'cancelled': 'annulée',
    'publishing': 'publication en cours', 'partially_published': 'publication partielle, suivi en cours',
    'publication_unknown': 'publication à vérifier, aucun renvoi automatique',
    'needs_fallback': 'quota épuisé, relance avec l’autre modèle à confirmer',
    'cancelling': 'annulation et nettoyage en cours', 'cleanup_failed': 'nettoyage à vérifier',
}


def outstanding(store, config):
    rows = store.outstanding(config['owner'], config['chat'])
    known = {r[0] for r in store.db.execute('SELECT id FROM jobs')}
    if config.get('planningIndex'):
        # Une vue absente/illisible bloque les créations plutôt que d'ignorer le suivi.
        data = json.loads(Path(config['planningIndex']).read_text())
        for record in data['videos']:
            if record['id'] not in known and record['status'] not in ['shared', 'published', 'cancelled']:
                rows.append(record | {'revision': record.get('revision', 1), 'kind': 'video'})
    return rows


def summary_lines(store, config):
    rows = outstanding(store, config)
    lines = ['Suivi des vidéos et questions en cours :']
    for r in rows:
        line = f"{r['id']} · option {r['option']} · {LABELS.get(r['status'], r['status'])}"
        if r['status'] == 'pending_validation':
            line += f"\n/valider {r['id']} {r['revision']}"
        elif r['status'] == 'validated' and not r.get('external'):
            line += f"\nUniquement après publication terminée sur les réseaux :\n/partage {r['id']} {r['revision']} CONFIRME plateformes ou liens"
        elif r['status'] == 'needs_input':
            line += f"\n/question {r['id']}"
        elif r['status'] == 'needs_fallback':
            line += f"\n/relancer {r['id']} oui   ou   /relancer {r['id']} non"
        elif r['status'] in ['failed', 'cleanup_failed']:
            line += f"\nPour tout supprimer : /annuler {r['id']}"
        lines.append(line)
    if not rows:
        lines.append('Aucune tâche en cours ni vidéo à publier.')
    return lines


def emit_summary(store, config, key, title=None):
    # Plusieurs messages si nécessaire : ne jamais tronquer la liste des tâches.
    if store.db.execute('SELECT 1 FROM outbox WHERE id=?', (key + ':0',)).fetchone():
        return {'accepted': True, 'alreadyRecorded': True}
    chunks, current = [], title or ''
    for line in summary_lines(store, config):
        if len(current) + len(line) > 2800:
            chunks.append(current); current = ''
        current += ('\n\n' if current else '') + line
    if current:
        chunks.append(current)
    for i, text in enumerate(chunks):
        store.emit(key + ':' + str(i), None, {'kind': 'text', 'text': text})
    return {'accepted': True, 'messages': len(chunks)}


def daily_summary(store, config, moment=None):
    if config.get('dailySummaryTime') != '09:00':
        raise ValueError('Récapitulatif quotidien non configuré.')
    moment = moment or datetime.datetime.now(datetime.timezone.utc)
    local = moment.astimezone(ZoneInfo('Europe/Paris'))
    if local.hour < 9:
        return {'accepted': True, 'notDue': True}
    with store.tx():
        return emit_summary(store, config, 'daily-summary:' + local.date().isoformat(),
                            'Récapitulatif du ' + local.strftime('%d/%m/%Y'))
