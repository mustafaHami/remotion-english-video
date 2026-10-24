"""État SQLite transactionnel, indépendant des exécutions n8n."""
from contextlib import contextmanager
import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid
from functools import wraps
import re
import os


def connect_as_owner(path, readonly=False):
    """Maintenance mono-thread : les fichiers WAL gardent l'UID du service DB."""
    uid = Path(path).stat().st_uid
    @contextmanager
    def owner():
        previous = os.geteuid()
        if previous == 0 and uid != previous:
            os.seteuid(uid)
        try:
            yield
        finally:
            if os.geteuid() != previous:
                os.seteuid(previous)
    class Connection(sqlite3.Connection):
        def execute(self, *args, **kwargs):
            with owner():
                return super().execute(*args, **kwargs)
        def executescript(self, *args, **kwargs):
            with owner():
                return super().executescript(*args, **kwargs)
    with owner():
        return sqlite3.connect('file:' + str(path) + ('?mode=ro' if readonly else '?mode=rw'),
                               uri=True, factory=Connection, timeout=15, isolation_level=None)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


CANCELLABLE = ['queued', 'needs_input', 'needs_fallback', 'failed', 'awaiting_preview', 'pending_validation', 'cleanup_failed']
LABELS = {'codex': 'Codex', 'claude': 'Claude'}
REASONS = {'quota-before-start': 'quota épuisé avant le début', 'quota-all': 'quotas Codex et Claude épuisés',
           'fallback-declined': 'relance refusée', 'user-request': 'demande explicite'}


def keyboard(*buttons):
    return {'rows': [{'row': {'buttons': [{'text': text, 'additionalFields': {'callback_data': data}}
                                          for text, data in buttons]}}]}


def cancel_keyboard(job_id):
    return keyboard(('Annuler et tout supprimer', f'cancel:{job_id}'))


def describe_quota(snapshot):
    if not snapshot or snapshot.get('status') == 'not_configured':
        return 'non configuré'
    if not snapshot.get('windows'):
        return 'quota inconnu'
    text = ' · '.join(f"{w['label']} : {w['remaining']} % restant" for w in snapshot['windows'])
    return text + (' — épuisé' if snapshot.get('exhausted') else '')


def valid_quota(engine, value):
    return (isinstance(value, dict) and value.get('engine') == engine
            and value.get('status') in ['ok', 'unknown', 'not_configured'] and value.get('exhausted') in [True, False, None]
            and isinstance(value.get('windows'), list) and len(value['windows']) <= 4
            and all(isinstance(w, dict) and isinstance(w.get('label'), str) and len(w['label']) <= 12
                    and type(w.get('remaining')) is int and 0 <= w['remaining'] <= 100 for w in value['windows']))


def atomic(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.db.in_transaction:
            return method(self, *args, **kwargs)
        with self.tx():
            return method(self, *args, **kwargs)
    return wrapped


class Store:
    def __init__(self, path, owner_permissions=False):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = connect_as_owner(path) if owner_permissions else sqlite3.connect(path, timeout=15, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, revision INTEGER NOT NULL, owner INTEGER NOT NULL,
            chat INTEGER NOT NULL, option INTEGER NOT NULL CHECK(option BETWEEN 1 AND 14),
            status TEXT NOT NULL, session TEXT, question TEXT, result TEXT,
            snapshot TEXT, approval TEXT, brief TEXT NOT NULL, updated TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, response TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY, job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL,
            session TEXT NOT NULL, text TEXT NOT NULL, answer TEXT, answered TEXT);
          CREATE TABLE IF NOT EXISTS outbox (
            id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', receipt TEXT);
          CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY, job TEXT, action TEXT NOT NULL, at TEXT NOT NULL, data TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS platform_results (
            job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL, destination TEXT NOT NULL,
            status TEXT NOT NULL, external_id TEXT, url TEXT,
            PRIMARY KEY(job, revision, destination));
          CREATE TABLE IF NOT EXISTS revisions (
            job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL,
            result TEXT, snapshot TEXT, approval TEXT,
            PRIMARY KEY(job, revision));
          CREATE TABLE IF NOT EXISTS worker_claims (id TEXT PRIMARY KEY, job TEXT);
          CREATE TABLE IF NOT EXISTS worker_receipts (lease TEXT PRIMARY KEY, digest TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS delivery_claims (id TEXT PRIMARY KEY, entries TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS admin_requests (id TEXT PRIMARY KEY, response TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS option_choices (
            id TEXT PRIMARY KEY, owner INTEGER NOT NULL, chat INTEGER NOT NULL,
            job TEXT REFERENCES jobs(id), created TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS preview_media (
            job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL,
            media TEXT NOT NULL, PRIMARY KEY(job,revision));
          CREATE TABLE IF NOT EXISTS codex_usage (
            job TEXT NOT NULL, session TEXT NOT NULL, invocation TEXT NOT NULL,
            input_tokens INTEGER NOT NULL, cached_input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL, reasoning_output_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL, updated TEXT NOT NULL,
            PRIMARY KEY(job,session,invocation));
          CREATE TABLE IF NOT EXISTS model_menus (
            id TEXT PRIMARY KEY, owner INTEGER NOT NULL, chat INTEGER NOT NULL, status TEXT NOT NULL,
            engine TEXT, quotas TEXT, job TEXT REFERENCES jobs(id), created TEXT NOT NULL, updated TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS job_files (
            job TEXT NOT NULL REFERENCES jobs(id), path TEXT NOT NULL, PRIMARY KEY(job, path));
          CREATE TABLE IF NOT EXISTS quota_snapshots (engine TEXT PRIMARY KEY, data TEXT NOT NULL, at TEXT NOT NULL);
        ''')
        usage_columns = {r[1] for r in self.db.execute('PRAGMA table_info(codex_usage)')}
        if usage_columns and 'invocation' not in usage_columns:
            required = {'job','session','input_tokens','cached_input_tokens','output_tokens',
                        'reasoning_output_tokens','total_tokens','updated'}
            if not required.issubset(usage_columns):
                raise RuntimeError('Ancien schéma codex_usage inconnu ; migration refusée.')
            # Preserve earlier per-session totals as one legacy invocation row.
            with self.tx():
                self.db.execute('ALTER TABLE codex_usage RENAME TO codex_usage_legacy')
                self.db.execute('''CREATE TABLE codex_usage (
                    job TEXT NOT NULL, session TEXT NOT NULL, invocation TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL, cached_input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL, reasoning_output_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL, updated TEXT NOT NULL,
                    PRIMARY KEY(job,session,invocation))''')
                self.db.execute('''INSERT INTO codex_usage
                    SELECT job,session,'legacy',input_tokens,cached_input_tokens,output_tokens,
                           reasoning_output_tokens,total_tokens,updated FROM codex_usage_legacy''')
                self.db.execute('DROP TABLE codex_usage_legacy')
        columns = {r[1] for r in self.db.execute('PRAGMA table_info(jobs)')}
        for name, definition in [('kind', "TEXT NOT NULL DEFAULT 'video'"), ('lease', 'TEXT'),
                                 ('validated_at', 'TEXT'), ('shared_at', 'TEXT'), ('closed_at', 'TEXT'),
                                 ('review', 'TEXT'), ('sharing', 'TEXT'), ('media_deleted_at', 'TEXT'), ('purged_at', 'TEXT'),
                                 ('engine', "TEXT NOT NULL DEFAULT 'codex'"), ('handoff', 'TEXT'), ('fallback', 'TEXT'),
                                 ('cancel_reason', 'TEXT'), ('cleanup_error', 'TEXT')]:
            if name not in columns:
                self.db.execute(f'ALTER TABLE jobs ADD COLUMN {name} {definition}')
        if 'engine' not in {r[1] for r in self.db.execute('PRAGMA table_info(codex_usage)')}:
            self.db.execute("ALTER TABLE codex_usage ADD COLUMN engine TEXT NOT NULL DEFAULT 'codex'")
        if 'model_menu' not in {r[1] for r in self.db.execute('PRAGMA table_info(option_choices)')}:
            self.db.execute('ALTER TABLE option_choices ADD COLUMN model_menu TEXT')
        if 'lease' not in {r[1] for r in self.db.execute('PRAGMA table_info(worker_claims)')}:
            self.db.execute('ALTER TABLE worker_claims ADD COLUMN lease TEXT')
        self.db.execute("UPDATE jobs SET status='pending_validation' WHERE status='awaiting_review'")
        self.db.execute("UPDATE jobs SET closed_at=updated WHERE kind='probe' AND status='completed' AND closed_at IS NULL")

    def close(self):
        self.db.close()

    @contextmanager
    def tx(self):
        if self.db.in_transaction:
            yield
            return
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def get(self, job_id):
        row = self.db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise ValueError('Tâche inconnue.')
        result = dict(row)
        for key in ['result', 'snapshot', 'approval', 'handoff', 'fallback']:
            result[key] = json.loads(result[key]) if result[key] else None
        return result

    def owned(self, job_id, owner, chat):
        job = self.get(job_id)
        if type(owner) is not int or type(chat) is not int or (job['owner'], job['chat']) != (owner, chat):
            raise PermissionError('Compte ou conversation non autorisé.')
        return job

    def outstanding(self, owner, chat):
        return [dict(r) for r in self.db.execute("""SELECT id,revision,option,status,question,kind FROM jobs
            WHERE owner=? AND chat=? AND purged_at IS NULL AND
            ((kind='video' AND status NOT IN ('shared','published','cancelled')) OR status='needs_input')
            ORDER BY updated,id""", (owner, chat))]

    @atomic
    def validate_preview(self, job_id, revision, owner, chat, source='Telegram /valider'):
        job = self.owned(job_id, owner, chat)
        if job['revision'] != revision or job['status'] not in ['pending_validation', 'validated']:
            raise ValueError('Validation impossible : vérifier la tâche et la version envoyée.')
        if job['status'] == 'validated':
            return {'jobId': job_id, 'status': 'validated', 'revision': revision}
        media = self.db.execute('SELECT media FROM preview_media WHERE job=? AND revision=?', (job_id, revision)).fetchone()
        delivery = self.db.execute('SELECT status FROM outbox WHERE id=?', (f'ready:{job_id}:{revision}',)).fetchone()
        if not media or not delivery or delivery['status'] != 'sent':
            raise ValueError('La vidéo doit être envoyée avant validation.')
        at = now()
        review = {'revision': revision, 'videoSha256': json.loads(media[0])['originalSha256'], 'at': at, 'source': source}
        self.db.execute("UPDATE jobs SET status='validated',validated_at=?,review=?,updated=? WHERE id=?",
                        (at, json.dumps(review), at, job_id))
        self.audit(job_id, 'preview-validated', review)
        return {'jobId': job_id, 'status': 'validated', 'revision': revision}

    @atomic
    def confirm_shared(self, job_id, revision, owner, chat, evidence):
        """Enregistre une publication terminée, jamais un simple envoi Telegram."""
        job = self.owned(job_id, owner, chat)
        permitted = ['validated']
        if evidence.get('source') == 'platform-receipts':
            permitted += ['publishing','partially_published','publication_unknown']
        if job['revision'] != revision or job['status'] not in permitted:
            raise ValueError('Seule la version validée peut être déclarée partagée.')
        if (evidence.get('source') not in ['explicit-user-confirmation', 'platform-receipts']
                or evidence.get('allDestinationsConfirmed') is not True or not evidence.get('confirmation')):
            raise ValueError('Confirmation de publication terminée sur les réseaux requise.')
        at = now()
        self.db.execute("UPDATE jobs SET status='shared',shared_at=?,closed_at=?,sharing=?,updated=? WHERE id=?",
                        (at, at, json.dumps(evidence), at, job_id))
        self.audit(job_id, 'shared', evidence)

    def audit(self, job_id, action, data=None):
        self.db.execute('INSERT INTO audit(job,action,at,data) VALUES(?,?,?,?)',
                        (job_id, action, now(), json.dumps(data or {})))

    def emit(self, key, job_id, payload):
        self.db.execute('INSERT INTO outbox(id,job,payload) VALUES(?,?,?)',
                        (key, job_id, json.dumps(payload, ensure_ascii=False)))

    def event(self, event_id, operation):
        """Déduplication et mutation dans la même transaction (acquittement après commit)."""
        if type(event_id) is not int or event_id < 0:
            raise ValueError('Identifiant Telegram invalide.')
        with self.tx():
            old = self.db.execute('SELECT response FROM events WHERE id=?', (event_id,)).fetchone()
            if old:
                return json.loads(old[0])
            response = operation()
            self.db.execute('INSERT INTO events VALUES(?,?)', (event_id, json.dumps(response)))
            return response

    @atomic
    def create(self, owner, chat, option, brief='', kind='video', engine='codex'):
        if type(owner) is not int or type(chat) is not int or owner <= 0 or chat <= 0:
            raise ValueError('Compte et conversation privée numériques requis.')
        if type(option) is not int or not 1 <= option <= 14:
            raise ValueError('Choisir une option entière entre 1 et 14.')
        if kind not in ['video', 'probe']:
            raise ValueError('Type de tâche inconnu.')
        if engine not in ['codex', 'claude']:
            raise ValueError('Agent inconnu.')
        job_id = uuid.uuid4().hex[:12]
        self.db.execute('''INSERT INTO jobs(id,revision,owner,chat,option,status,brief,updated,kind,engine)
                           VALUES(?,1,?,?,?,'queued',?,?,?,?)''', (job_id, owner, chat, option, brief, now(), kind, engine))
        self.db.execute('INSERT INTO revisions(job,revision) VALUES(?,1)', (job_id,))
        self.audit(job_id, 'created', {'engine': engine})
        return {'jobId': job_id, 'revision': 1, 'status': 'queued'}

    def claim(self):
        with self.tx():
            if self.db.execute("SELECT 1 FROM jobs WHERE status='generating'").fetchone():
                return None
            row = self.db.execute("SELECT id FROM jobs WHERE status='queued' ORDER BY updated,id LIMIT 1").fetchone()
            if row is None:
                return None
            self.db.execute("UPDATE jobs SET status='generating',lease=?,updated=? WHERE id=?", (uuid.uuid4().hex, now(), row[0]))
            self.audit(row[0], 'claimed')
            return self.get(row[0])

    def record(self, job_id, revision, result, actual_session, usage=None, invocation=None):
        from .runner import SCHEMA, validate_schema
        validate_schema(result, json.loads(SCHEMA.read_text()))
        with self.tx():
            job = self.get(job_id)
            if job['status'] != 'generating' or job['revision'] != revision:
                raise ValueError('Résultat obsolète ou tâche non active.')
            if result['jobId'] != job_id or result['revision'] != revision:
                raise ValueError('Résultat rattaché à une autre tâche.')
            if not actual_session or result['sessionId'] != actual_session:
                raise ValueError('Session de l’agent non vérifiée.')
            uuid.UUID(actual_session)
            if job['session'] and job['session'] != actual_session:
                raise ValueError('Le résultat a changé de session.')
            if usage is not None:
                self.record_usage(job_id, actual_session, invocation or f'r{revision}', usage, job['engine'])
            status = result['status']
            question_id = None
            if status == 'needs_input':
                question_id = uuid.uuid4().hex[:12]
                self.db.execute('INSERT INTO questions(id,job,revision,session,text) VALUES(?,?,?,?,?)',
                    (question_id, job_id, revision, actual_session, result['question']))
                result['questionId'] = question_id
                self.emit('question:' + question_id, job_id, {'kind': 'question', 'jobId': job_id,
                    'revision': revision, 'questionId': question_id, 'text': result['question']})
            elif status == 'completed':
                # Le résultat validé ne vaut ni prévisualisation ni accord humain.
                if job['kind'] == 'probe':
                    self.emit(f'completed:{job_id}:{revision}', job_id, {'kind': 'text', 'text': result['summary'], 'jobId': job_id})
                else:
                    status = 'awaiting_preview'
                    self.emit(f'ready:{job_id}:{revision}', job_id, {'kind': 'ready', 'jobId': job_id, 'revision': revision})
            elif status != 'failed':
                raise ValueError('Statut de l’agent inconnu.')
            if status == 'failed':
                self.emit(f'failed:{job_id}:{revision}', job_id, {'kind': 'text', 'text': 'La tâche a échoué. Diagnostic conservé sur le VPS.', 'jobId': job_id})
            self.db.execute('UPDATE jobs SET status=?,session=?,question=?,result=?,updated=? WHERE id=?',
                (status, actual_session, question_id, json.dumps(result), now(), job_id))
            self.db.execute('UPDATE revisions SET result=? WHERE job=? AND revision=?',
                            (json.dumps(result), job_id, revision))
            if job['kind'] == 'probe' and status == 'completed':
                self.db.execute('UPDATE jobs SET closed_at=? WHERE id=?', (now(), job_id))
            self.audit(job_id, status)

    def usage_by_engine(self, job_id):
        totals = {}
        for row in self.db.execute('''SELECT engine,input_tokens,cached_input_tokens,output_tokens,
                    reasoning_output_tokens,total_tokens FROM codex_usage WHERE job=?''', (job_id,)):
            item = totals.setdefault(row['engine'], dict.fromkeys(
                ('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens'), 0))
            for key in item:
                item[key] += row[key]
        return totals

    def codex_usage(self, job_id):
        return self.usage_by_engine(job_id).get('codex')

    @atomic
    def record_usage(self, job_id, session, invocation, usage, engine='codex'):
        names = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')
        if (not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0 for k in names)
                or usage['cached_input_tokens'] > usage['input_tokens']
                or usage.get('total_tokens') != usage['input_tokens'] + usage['output_tokens']):
            raise ValueError('Compteurs d’usage invalides.')
        uuid.UUID(session)
        if engine not in ['codex', 'claude']:
            raise ValueError('Agent inconnu.')
        if not isinstance(invocation, str) or not invocation or len(invocation) > 128:
            raise ValueError('Identifiant d’invocation invalide.')
        previous = self.db.execute('''SELECT total_tokens FROM codex_usage
            WHERE job=? AND session=? AND invocation=?''', (job_id, session, invocation)).fetchone()
        if previous is None or usage['total_tokens'] > previous['total_tokens']:
            self.db.execute('''INSERT INTO codex_usage(job,session,invocation,input_tokens,cached_input_tokens,
                output_tokens,reasoning_output_tokens,total_tokens,updated,engine) VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(job,session,invocation) DO UPDATE SET input_tokens=excluded.input_tokens,
                cached_input_tokens=excluded.cached_input_tokens,output_tokens=excluded.output_tokens,
                reasoning_output_tokens=excluded.reasoning_output_tokens,
                total_tokens=excluded.total_tokens,updated=excluded.updated''',
                (job_id, session, invocation, *(usage[k] for k in names), usage['total_tokens'], now(), engine))

    @atomic
    def answer(self, job_id, question_id, owner, chat, text):
        job = self.owned(job_id, owner, chat)
        question = self.db.execute('SELECT * FROM questions WHERE id=? AND job=?', (question_id, job_id)).fetchone()
        if (job['status'] != 'needs_input' or job['question'] != question_id or not question
                or question['answer'] is not None or question['revision'] != job['revision']
                or question['session'] != job['session']):
            raise ValueError('Question expirée, déjà répondue ou ambiguë.')
        if not text.strip() or len(text) > 8000:
            raise ValueError('Réponse vide ou trop longue.')
        self.db.execute('UPDATE questions SET answer=?,answered=? WHERE id=?', (text, now(), question_id))
        self.db.execute("UPDATE jobs SET status='queued',updated=? WHERE id=?", (now(), job_id))
        self.audit(job_id, 'answered', {'questionId': question_id})
        return {'jobId': job_id, 'status': 'queued', 'sessionId': job['session']}

    def set_preview(self, job_id, revision, snapshot):
        with self.tx():
            job = self.get(job_id)
            if job['revision'] != revision or job['status'] != 'awaiting_preview':
                raise ValueError('Livrable obsolète.')
            if (not isinstance(snapshot.get('videoSha256'), str) or not re.fullmatch('[a-f0-9]{64}', snapshot['videoSha256'])
                    or not snapshot.get('captions') or not snapshot.get('destinations')):
                raise ValueError('Prévisualisation incomplète.')
            self.db.execute("UPDATE jobs SET status='awaiting_approval',snapshot=?,approval=NULL,updated=? WHERE id=?",
                            (json.dumps(snapshot), now(), job_id))
            self.db.execute('UPDATE revisions SET snapshot=? WHERE job=? AND revision=?',
                            (json.dumps(snapshot), job_id, revision))
            self.audit(job_id, 'previewed', {'revision': revision, 'snapshotHash': digest(snapshot)})
            return digest(snapshot)

    @atomic
    def approve(self, job_id, revision, snapshot_hash, owner, chat):
        job = self.owned(job_id, owner, chat)
        if job['revision'] != revision or job['status'] != 'awaiting_approval' or digest(job['snapshot']) != snapshot_hash:
            raise ValueError('Bouton ancien, accord déjà traité ou livrable modifié.')
        approval = {'owner': owner, 'chat': chat, 'revision': revision, 'snapshotHash': snapshot_hash, 'at': now()}
        self.db.execute("UPDATE jobs SET status='approved',approval=?,updated=? WHERE id=?",
                        (json.dumps(approval), now(), job_id))
        self.db.execute('UPDATE revisions SET approval=? WHERE job=? AND revision=?',
                        (json.dumps(approval), job_id, revision))
        self.audit(job_id, 'approved', approval)
        return {'jobId': job_id, 'status': 'approved', 'published': False}

    @atomic
    def revise(self, job_id, revision, owner, chat, brief):
        job = self.owned(job_id, owner, chat)
        if job['revision'] != revision or job['status'] not in ['awaiting_preview', 'pending_validation', 'validated', 'awaiting_approval', 'approved', 'failed']:
            raise ValueError('Révision indisponible ou obsolète.')
        self.db.execute("""UPDATE jobs SET revision=revision+1,status='queued',question=NULL,
            snapshot=NULL,approval=NULL,review=NULL,validated_at=NULL,brief=?,updated=? WHERE id=?""", (brief, now(), job_id))
        self.db.execute('INSERT INTO revisions(job,revision) VALUES(?,?)', (job_id, revision + 1))
        self.audit(job_id, 'revised', {'previousRevision': revision})
        return {'jobId': job_id, 'revision': revision + 1, 'status': 'queued'}

    @atomic
    def cancel(self, job_id, revision, owner, chat):
        job = self.owned(job_id, owner, chat)
        if job['revision'] != revision or job['status'] in ['generating', 'publishing', 'publication_unknown', 'published', 'shared', 'scheduled', 'partially_published']:
            raise ValueError('Traitement engagé : vérification manuelle nécessaire.')
        at = now()
        self.db.execute("UPDATE jobs SET status='cancelled',approval=NULL,closed_at=?,updated=? WHERE id=?", (at, at, job_id))
        self.audit(job_id, 'cancelled')
        return {'jobId': job_id, 'status': 'cancelled'}

    def recover(self):
        """Seulement après contrôle opérateur des processus ; aucune relance automatique."""
        with self.tx():
            rows = self.db.execute("SELECT id,status FROM jobs WHERE status IN ('generating','publishing')").fetchall()
            for row in rows:
                status = 'publication_unknown' if row['status'] == 'publishing' else 'failed'
                self.db.execute('UPDATE jobs SET status=?,updated=? WHERE id=?', (status, now(), row['id']))
                self.audit(row['id'], 'operator-recovery', {'previousState': row['status']})
            return len(rows)

    def pending(self):
        return [dict(row) | {'payload': json.loads(row['payload'])}
                for row in self.db.execute("SELECT * FROM outbox WHERE status='pending' ORDER BY rowid")]

    def mark_delivery(self, outbox_id, status, receipt=None):
        if status not in ['sent', 'delivery_unknown']:
            raise ValueError('Statut de notification invalide.')
        with self.tx():
            previous = self.db.execute('SELECT status,receipt FROM outbox WHERE id=?', (outbox_id,)).fetchone()
            if previous and previous['status'] == status and json.loads(previous['receipt']) == receipt:
                return
            changed = self.db.execute("UPDATE outbox SET status=?,receipt=? WHERE id=? AND status IN ('pending','delivering')",
                                     (status, json.dumps(receipt), outbox_id)).rowcount
            if not changed:
                raise ValueError('Notification déjà traitée.')
            item = self.db.execute('SELECT job,payload FROM outbox WHERE id=?', (outbox_id,)).fetchone()
            payload = json.loads(item['payload'])
            if status == 'sent' and payload.get('kind') == 'ready':
                self.db.execute("UPDATE jobs SET status='pending_validation',updated=? WHERE id=? AND revision=? AND status='awaiting_preview'",
                                (now(), item['job'], payload['revision']))
                self.audit(item['job'], 'preview-delivered', receipt)

    def claim_notifications(self, limit=10, claim_id=None):
        with self.tx():
            if claim_id:
                previous = self.db.execute('SELECT entries FROM delivery_claims WHERE id=?', (claim_id,)).fetchone()
                if previous:
                    entries = []
                    for identifier in json.loads(previous['entries']):
                        row = self.db.execute("SELECT * FROM outbox WHERE id=? AND status='delivering'", (identifier,)).fetchone()
                        if row:
                            entries.append(dict(row) | {'payload': json.loads(row['payload'])})
                    return entries
            entries = self.pending()[:limit]
            for entry in entries:
                self.db.execute("UPDATE outbox SET status='delivering' WHERE id=?", (entry['id'],))
            if claim_id and entries:
                self.db.execute('INSERT INTO delivery_claims VALUES(?,?)', (claim_id, json.dumps([e['id'] for e in entries])))
            return entries

    def question_for_message(self, message_id):
        for row in self.db.execute("SELECT payload,receipt FROM outbox WHERE status='sent'"):
            receipt = json.loads(row['receipt'])
            payload = json.loads(row['payload'])
            if isinstance(receipt, dict) and receipt.get('messageId') == message_id and payload.get('kind') == 'question':
                return payload['jobId'], payload['questionId']
        raise ValueError('Répondre au message de question correspondant ou utiliser /repondre avec ses identifiants.')

    def fail(self, job_id, lease):
        with self.tx():
            job = self.get(job_id)
            if job['status'] == 'failed' and job['lease'] == lease:
                return
            if job['status'] != 'generating' or job['lease'] != lease:
                raise ValueError('Traitement obsolète.')
            self.db.execute("UPDATE jobs SET status='failed',updated=? WHERE id=?", (now(), job_id))
            self.audit(job_id, 'worker-failed')
            text = f"La tâche {job_id} a été interrompue ou a échoué. Journaux et fichiers conservés pour diagnostic ; aucune publication."
            payload = {'kind': 'text', 'jobId': job_id, 'text': text}
            if job['kind'] == 'video':
                payload = {'kind': 'menu', 'jobId': job_id, 'text': text + f'\nPour tout supprimer : /annuler {job_id}',
                           'keyboard': cancel_keyboard(job_id)}
            self.emit(f"failed:{job_id}:{job['revision']}", job_id, payload)

    @atomic
    def add_files(self, job_id, entries):
        from .cleanup import valid_entry
        if not isinstance(entries, list) or len(entries) > 5000 or not all(valid_entry(e) for e in entries):
            raise ValueError('Empreinte de fichiers invalide.')
        for entry in entries:
            self.db.execute('INSERT OR IGNORE INTO job_files VALUES(?,?)', (job_id, entry))

    def files(self, job_id):
        return [r[0] for r in self.db.execute('SELECT path FROM job_files WHERE job=? ORDER BY path', (job_id,))]

    def sessions(self, job_id):
        found = {r[0] for r in self.db.execute('SELECT session FROM codex_usage WHERE job=?', (job_id,))}
        found |= {r[0] for r in self.db.execute('SELECT session FROM questions WHERE job=?', (job_id,))}
        session = self.get(job_id)['session']
        return sorted(s for s in found | {session} if s)

    @atomic
    def save_quotas(self, quotas):
        if not isinstance(quotas, dict) or not set(quotas) <= set(LABELS) or not all(valid_quota(k, v) for k, v in quotas.items()):
            raise ValueError('Relevé de quotas invalide.')
        for engine, value in quotas.items():
            self.db.execute('INSERT OR REPLACE INTO quota_snapshots VALUES(?,?,?)', (engine, json.dumps(value), now()))

    def quota(self, engine):
        row = self.db.execute('SELECT data FROM quota_snapshots WHERE engine=?', (engine,)).fetchone()
        return json.loads(row[0]) if row else None

    @atomic
    def request_cancel(self, job_id, reason, owner=None, chat=None, lease=None):
        """Passe la tâche en nettoyage ; seul le worker supprime ensuite les fichiers."""
        job = self.get(job_id) if owner is None else self.owned(job_id, owner, chat)
        if job['status'] in ['cancelling', 'cancelled']:
            return {'jobId': job_id, 'status': job['status'], 'alreadyCancelled': True}
        allowed = CANCELLABLE + (['generating'] if lease is not None and lease == job['lease'] else [])
        if job['kind'] != 'video' or job['status'] not in allowed:
            raise ValueError('Annulation impossible maintenant : attendez la fin de la création en cours '
                             'ou vérifiez la tâche avec /statut ' + job_id + '.')
        if reason not in REASONS:
            raise ValueError('Motif d’annulation inconnu.')
        self.db.execute("""UPDATE jobs SET status='cancelling',cancel_reason=?,cleanup_error=NULL,lease=NULL,
            fallback=NULL,question=NULL,updated=? WHERE id=?""", (reason, now(), job_id))
        # Les messages pas encore partis pour cette tâche ne doivent plus l'être.
        self.db.execute("UPDATE outbox SET status='superseded' WHERE job=? AND status='pending'", (job_id,))
        self.audit(job_id, 'cancel-requested', {'reason': reason, 'previous': job['status']})
        return {'jobId': job_id, 'status': 'cancelling'}

    def claim_cleanup(self):
        with self.tx():
            row = self.db.execute("SELECT id FROM jobs WHERE status='cancelling' ORDER BY updated,id LIMIT 1").fetchone()
            if row is None:
                return None
            lease = uuid.uuid4().hex
            self.db.execute('UPDATE jobs SET lease=?,updated=? WHERE id=?', (lease, now(), row[0]))
            return {'jobId': row[0], 'lease': lease, 'files': self.files(row[0]), 'sessions': self.sessions(row[0])}

    @atomic
    def finish_cleanup(self, job_id, lease, report, error):
        job = self.get(job_id)
        if job['status'] in ['cancelled', 'cleanup_failed'] and job['lease'] == lease:
            return {'jobId': job_id, 'status': job['status']}
        if job['status'] != 'cancelling' or job['lease'] != lease:
            raise ValueError('Nettoyage obsolète.')
        if error is not None:
            if not isinstance(error, str):
                raise ValueError('Erreur de nettoyage invalide.')
            self.db.execute("UPDATE jobs SET status='cleanup_failed',cleanup_error=?,updated=? WHERE id=?",
                            (error[:500], now(), job_id))
            self.audit(job_id, 'cleanup-failed', {'error': error[:500]})
            self.emit(f'cleanup-failed:{job_id}:{uuid.uuid4().hex[:8]}', None, {'kind': 'menu',
                'text': f'Le nettoyage de la tâche {job_id} a échoué ; rien n’a été relancé automatiquement. '
                        f'Diagnostic conservé sur le VPS. Pour réessayer : /annuler {job_id}', 'keyboard': cancel_keyboard(job_id)})
            return {'jobId': job_id, 'status': 'cleanup_failed'}
        if (not isinstance(report, dict) or not isinstance(report.get('deleted'), list)
                or not isinstance(report.get('skipped'), list)):
            raise ValueError('Rapport de nettoyage invalide.')
        at = now()
        for table in ['questions', 'revisions', 'preview_media', 'job_files', 'codex_usage', 'audit']:
            self.db.execute(f'DELETE FROM {table} WHERE job=?', (job_id,))
        self.db.execute("UPDATE outbox SET payload=? WHERE job=? AND status='sent'",
                        (json.dumps({'kind': 'tombstone', 'jobId': job_id}), job_id))
        self.db.execute("""UPDATE jobs SET status='cancelled',result=NULL,session=NULL,question=NULL,brief='',
            snapshot=NULL,approval=NULL,review=NULL,handoff=NULL,fallback=NULL,cleanup_error=NULL,
            closed_at=?,purged_at=?,updated=? WHERE id=?""", (at, at, at, job_id))
        # Seule trace conservée : identifiant, motif et compteurs, sans contenu.
        self.audit(job_id, 'cancelled-cleaned', {'reason': job['cancel_reason'], 'deleted': len(report['deleted']),
                                                  'skipped': len(report['skipped'])})
        text = (f"Tâche {job_id} annulée ({REASONS.get(job['cancel_reason'], 'annulation')}). "
                f"{len(report['deleted'])} élément(s) supprimé(s) : fichiers, voix, rendu, journaux et sessions.")
        if report['skipped']:
            text += f" {len(report['skipped'])} élément(s) conservé(s) par sécurité (partagé ou non créé par la tâche)."
        self.emit(f'cancelled:{job_id}', None, {'kind': 'text', 'text': text})
        return {'jobId': job_id, 'status': 'cancelled'}

    @atomic
    def quota_exhausted(self, job_id, lease, started, quotas, footprint, usage=None, session=None):
        job = self.get(job_id)
        handled = self.db.execute("SELECT 1 FROM audit WHERE job=? AND action IN ('quota-exhausted','cancel-requested') LIMIT 1",
                                  (job_id,)).fetchone()
        # Un renvoi après redémarrage du worker ne doit ni échouer en boucle ni rien changer.
        if job['status'] in ['needs_fallback', 'cancelling', 'cancelled', 'cleanup_failed'] and (handled or job['purged_at']):
            return {'jobId': job_id, 'status': job['status'], 'alreadyRecorded': True}
        if job['lease'] != lease:
            raise ValueError('Traitement obsolète.')
        if job['status'] != 'generating' or job['kind'] != 'video' or type(started) is not bool:
            raise ValueError('Traitement obsolète.')
        self.add_files(job_id, footprint)
        self.save_quotas(quotas)
        if usage is not None and session:
            self.record_usage(job_id, session, lease, usage, job['engine'])
        engine = job['engine']
        alternative = 'claude' if engine == 'codex' else 'codex'
        current, spare = quotas.get(engine), quotas.get(alternative) or {}
        if not started and not job['handoff']:
            self.request_cancel(job_id, 'quota-before-start', lease=lease)
            self.emit(f'quota-before-start:{job_id}', None, {'kind': 'text', 'text':
                f"{LABELS[engine]} n’a plus d’usage disponible ({describe_quota(current)}). "
                'Aucune vidéo n’a été commencée et la tâche est annulée. Choisissez un autre modèle avec /modele.'})
            return {'jobId': job_id, 'status': 'cancelling'}
        if spare.get('exhausted') is True or spare.get('status') == 'not_configured':
            self.request_cancel(job_id, 'quota-all', lease=lease)
            self.emit(f'quota-all:{job_id}', None, {'kind': 'text', 'text':
                f"Codex et Claude n’ont plus d’usage disponible. La tâche {job_id} est annulée : "
                'tout ce qui a été produit va être supprimé.'})
            return {'jobId': job_id, 'status': 'cancelling'}
        fallback = {'from': engine, 'to': alternative, 'at': now()}
        self.db.execute("UPDATE jobs SET status='needs_fallback',fallback=?,updated=? WHERE id=?",
                        (json.dumps(fallback), now(), job_id))
        self.audit(job_id, 'quota-exhausted', {'engine': engine, 'started': started})
        self.emit(f'fallback:{job_id}:{uuid.uuid4().hex[:8]}', job_id, {'kind': 'menu', 'jobId': job_id,
            'text': (f"{LABELS[engine]} n’a plus d’usage pendant la création de la vidéo option {job['option']} "
                     f"(tâche {job_id} ; {describe_quota(current)}).\n\n"
                     f"Relancer avec {LABELS[alternative]} ({describe_quota(spare)}) ? "
                     f"Il reprendra là où {LABELS[engine]} s’est arrêté.\n"
                     'Non : annulation et suppression de tout ce qui a été produit.\n'
                     f'Vous pouvez aussi répondre oui ou non, ou /relancer {job_id} oui|non.'),
            'keyboard': keyboard((f'Oui, relancer avec {LABELS[alternative]}', f'fallback:{job_id}:yes'),
                                 ('Non, tout annuler', f'fallback:{job_id}:no'))})
        return {'jobId': job_id, 'status': 'needs_fallback'}

    @atomic
    def fallback_decision(self, job_id, owner, chat, accept):
        job = self.owned(job_id, owner, chat)
        if job['status'] != 'needs_fallback' or not job['fallback']:
            raise ValueError('Aucune relance en attente pour cette tâche.')
        if not accept:
            return self.request_cancel(job_id, 'fallback-declined', owner, chat)
        target = job['fallback']['to']
        handoff = {'from': job['engine'], 'reason': 'quota', 'files': self.files(job_id)}
        self.db.execute("""UPDATE jobs SET engine=?,status='queued',session=NULL,question=NULL,lease=NULL,
            handoff=?,fallback=NULL,updated=? WHERE id=?""", (target, json.dumps(handoff), now(), job_id))
        self.audit(job_id, 'fallback-accepted', {'from': job['engine'], 'to': target})
        return {'jobId': job_id, 'status': 'queued', 'engine': target}
