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


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def atomic(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.db.in_transaction:
            return method(self, *args, **kwargs)
        with self.tx():
            return method(self, *args, **kwargs)
    return wrapped


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=15, isolation_level=None)
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
        ''')
        columns = {r[1] for r in self.db.execute('PRAGMA table_info(jobs)')}
        for name, definition in [('kind', "TEXT NOT NULL DEFAULT 'video'"), ('lease', 'TEXT')]:
            if name not in columns:
                self.db.execute(f'ALTER TABLE jobs ADD COLUMN {name} {definition}')

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
        for key in ['result', 'snapshot', 'approval']:
            result[key] = json.loads(result[key]) if result[key] else None
        return result

    def owned(self, job_id, owner, chat):
        job = self.get(job_id)
        if type(owner) is not int or type(chat) is not int or (job['owner'], job['chat']) != (owner, chat):
            raise PermissionError('Compte ou conversation non autorisé.')
        return job

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
    def create(self, owner, chat, option, brief='', kind='video'):
        if type(owner) is not int or type(chat) is not int or owner <= 0 or chat <= 0:
            raise ValueError('Compte et conversation privée numériques requis.')
        if type(option) is not int or not 1 <= option <= 14:
            raise ValueError('Choisir une option entière entre 1 et 14.')
        if kind not in ['video', 'probe']:
            raise ValueError('Type de tâche inconnu.')
        job_id = uuid.uuid4().hex[:12]
        self.db.execute('''INSERT INTO jobs(id,revision,owner,chat,option,status,brief,updated,kind)
                           VALUES(?,1,?,?,?,'queued',?,?,?)''', (job_id, owner, chat, option, brief, now(), kind))
        self.db.execute('INSERT INTO revisions(job,revision) VALUES(?,1)', (job_id,))
        self.audit(job_id, 'created')
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

    def record(self, job_id, revision, result, actual_session):
        from .runner import SCHEMA, validate_schema
        validate_schema(result, json.loads(SCHEMA.read_text()))
        with self.tx():
            job = self.get(job_id)
            if job['status'] != 'generating' or job['revision'] != revision:
                raise ValueError('Résultat obsolète ou tâche non active.')
            if result['jobId'] != job_id or result['revision'] != revision:
                raise ValueError('Résultat rattaché à une autre tâche.')
            if not actual_session or result['sessionId'] != actual_session:
                raise ValueError('Session Codex non vérifiée.')
            uuid.UUID(actual_session)
            if job['session'] and job['session'] != actual_session:
                raise ValueError('Le résultat a changé de session.')
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
                raise ValueError('Statut Codex inconnu.')
            if status == 'failed':
                self.emit(f'failed:{job_id}:{revision}', job_id, {'kind': 'text', 'text': 'La tâche a échoué. Diagnostic conservé sur le VPS.', 'jobId': job_id})
            self.db.execute('UPDATE jobs SET status=?,session=?,question=?,result=?,updated=? WHERE id=?',
                (status, actual_session, question_id, json.dumps(result), now(), job_id))
            self.db.execute('UPDATE revisions SET result=? WHERE job=? AND revision=?',
                            (json.dumps(result), job_id, revision))
            self.audit(job_id, status)

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
        if job['revision'] != revision or job['status'] not in ['awaiting_preview', 'awaiting_approval', 'approved', 'failed']:
            raise ValueError('Révision indisponible ou obsolète.')
        self.db.execute("""UPDATE jobs SET revision=revision+1,status='queued',question=NULL,
            snapshot=NULL,approval=NULL,brief=?,updated=? WHERE id=?""", (brief, now(), job_id))
        self.db.execute('INSERT INTO revisions(job,revision) VALUES(?,?)', (job_id, revision + 1))
        self.audit(job_id, 'revised', {'previousRevision': revision})
        return {'jobId': job_id, 'revision': revision + 1, 'status': 'queued'}

    @atomic
    def cancel(self, job_id, revision, owner, chat):
        job = self.owned(job_id, owner, chat)
        if job['revision'] != revision or job['status'] in ['generating', 'publishing', 'publication_unknown', 'published', 'scheduled', 'partially_published']:
            raise ValueError('Traitement engagé : vérification manuelle nécessaire.')
        self.db.execute("UPDATE jobs SET status='cancelled',approval=NULL,updated=? WHERE id=?", (now(), job_id))
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
            self.emit(f"failed:{job_id}:{job['revision']}", job_id, {'kind': 'text', 'jobId': job_id,
                'text': 'Le diagnostic Codex a été interrompu ou a échoué. Aucun média produit ; les journaux sont conservés.'})
