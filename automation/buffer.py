"""Préparation Buffer : lectures API fermées et requêtes de brouillons uniquement."""
import datetime
import json
from pathlib import Path
import re
import stat
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = 'https://api.buffer.com'
QUERIES = {
    'publication_post': '''query EnglizyPublication($input: PostInput!) {
      post(input:$input) { id channelId channelService status text sentAt dueAt externalLink
        schedulingType notificationStatus allowedActions error { message }
        assets { source mimeType type }
        metadata { __typename
          ... on InstagramPostMetadata { type shouldShareToFeed firstComment isAiGenerated }
          ... on TiktokPostMetadata { type title isAiGenerated }
          ... on YoutubePostMetadata { type title privacy madeForKids category { categoryId }
            embeddable notifySubscribers license isAiGenerated } }
      }
    }''',
    'account': 'query EnglizyAccount { account { id organizations { id name } } }',
    'channels': '''query EnglizyChannels($input: ChannelsInput!) {
      channels(input:$input) { id organizationId name displayName service type
        isDisconnected isLocked isQueuePaused allowedActions externalLink }
    }''',
    'post': '''query EnglizyPost($input: PostInput!) {
      post(input:$input) { id channelId status text sentAt dueAt assets {
        source mimeType type ... on VideoAsset { thumbnail video {
          durationMs width height fileSize isVideoProcessing videoCodec audioCodec } }
      } }
    }''',
    'configuration': '''query EnglizyConfiguration($input: ConfigurationInput!) {
      configuration(input:$input) { channels { channelId service
        authorizationStatus { feature status reason }
        content { configurationContentTypes supportedProperties } } }
    }''',
}
DRAFT_MUTATION = '''mutation EnglizyDraft($input: CreatePostInput!) {
  createPost(input:$input) {
    __typename
    ... on PostActionSuccess { post { id channelId status text sentAt dueAt assets { source } } }
    ... on MutationError { message }
  }
}'''


class BufferError(ValueError):
    """Messages contrôlés sans corps HTTP ni clé."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Ne jamais transmettre l'en-tête Bearer à un autre hôte.


def read_secret(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise BufferError('Clé Buffer absente ou permissions non privées ; utiliser automation-secrets.py.')
    token = path.read_text().strip()
    if not token or any(c.isspace() for c in token):
        raise BufferError('Clé Buffer locale invalide.')
    return token


class Reader:
    """Ce client ne peut envoyer aucune mutation, même appelée hors de n8n."""
    def __init__(self, token):
        self._token = token
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        self.rate_limits = []

    def query(self, operation, variables=None):
        if operation not in QUERIES:
            raise BufferError('Opération Buffer non autorisée en lecture seule.')
        payload = {'query':QUERIES[operation], 'variables':variables or {}}
        req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method='POST',
            headers={'Authorization':'Bearer ' + self._token, 'Content-Type':'application/json',
                     'User-Agent':'Englizy-n8n/1.0'})
        try:
            with self.opener.open(req, timeout=30) as response:
                self.rate_limits = response.headers.get_all('RateLimit') or []
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise BufferError('Réponse Buffer trop volumineuse.')
                data = json.loads(raw)
        except urllib.error.HTTPError as error:
            raise BufferError(f'API Buffer : HTTP {error.code}. Aucun nouvel essai automatique.') from None
        except (OSError, ValueError, urllib.error.URLError):
            raise BufferError('API Buffer indisponible ou réponse illisible. Aucun secret journalisé.') from None
        if not isinstance(data, dict):
            raise BufferError('Réponse Buffer invalide.')
        if data.get('errors') or not isinstance(data.get('data'), dict):
            codes = sorted({str(e.get('extensions', {}).get('code', 'GRAPHQL_ERROR')) for e in data.get('errors', [])})
            safe = [c for c in codes if re.fullmatch('[A-Z_0-9]{1,60}', c)]
            raise BufferError('Requête Buffer refusée : ' + ', '.join(safe or ['GRAPHQL_ERROR']))
        return data['data']

    def inventory(self):
        account = self.query('account')['account']
        organizations = []
        for org in account['organizations']:
            channels = self.query('channels', {'input':{'organizationId':org['id']}})['channels']
            if any(c['organizationId'] != org['id'] for c in channels):
                raise BufferError('Canal rattaché à une organisation inattendue.')
            organizations.append(org | {'channels':channels})
        return {'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'accountId':account['id'], 'organizations':organizations, 'rateLimits':self.rate_limits}


def episode_social(episode):
    """Légendes écrites par Codex dans l'épisode ; mêmes règles que scripts/lib/lesson.cjs."""
    social = episode.get('social')
    if not isinstance(social, dict) or sorted(social) != ['captions', 'youtubeTitle']:
        raise BufferError("Légendes absentes de l'épisode ; demander une révision qui ajoute social.")
    title, captions = social['youtubeTitle'], social['captions']
    if not isinstance(title, str) or not title.strip() or len(title) > 100 or re.search('[<>]', title):
        raise BufferError('Titre YouTube requis, 100 caractères au maximum, sans < ni >.')
    if not isinstance(captions, dict) or sorted(captions) != ['instagram', 'tiktok', 'youtube']:
        raise BufferError('Légendes Instagram, TikTok et YouTube requises.')
    for service, text in captions.items():
        if not isinstance(text, str) or not text.strip() or len(text) > 2000:
            raise BufferError('Légende vide ou trop longue : ' + service)
        if re.search(r'https?://|www\.', text, re.I):
            raise BufferError('Aucun lien dans une légende : ' + service)
        if len(re.findall(r'#\w+', text)) > 30:
            raise BufferError('Plus de 30 hashtags : ' + service)
    return title, captions


def draft_input(channel, text, media_url, title):
    """Prépare uniquement un brouillon ; aucun appel HTTP ici."""
    if channel.get('isDisconnected') is not False or channel.get('isLocked') is not False:
        raise BufferError('Canal déconnecté, verrouillé ou non vérifié.')
    if 'manageUpdates' not in channel.get('allowedActions', []):
        raise BufferError('La gestion des brouillons est indisponible pour ce canal.')
    service = channel.get('service')
    if service not in ['instagram','tiktok','youtube'] or not channel.get('id'):
        raise BufferError('Canal non pris en charge par cette intégration.')
    url = urllib.parse.urlsplit(media_url)
    if (url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment
            or url.port not in [None,443] or not url.path.endswith('.mp4')):
        raise BufferError('Une URL HTTPS directe et stable vers le MP4 est requise.')
    if not isinstance(text,str) or not text.strip() or len(text)>2000:
        raise BufferError('Légende vide ou trop longue pour la préparation commune.')
    if not isinstance(title,str) or not title.strip() or len(title)>100:
        raise BufferError('Titre vidéo requis, au maximum 100 caractères.')
    metadata = {'instagram':{'type':'reel','shouldShareToFeed':True},
                'tiktok':{}, 'youtube':{'title':title,'categoryId':'27','privacy':'public','madeForKids':False}}
    result = {'channelId':channel['id'], 'text':text, 'schedulingType':'automatic', 'mode':'addToQueue',
              'saveToDraft':True, 'needsApproval':False, 'aiAssisted':True,
              'assets':[{'video':{'url':media_url}}], 'metadata':{service:metadata[service]}}
    validate_draft_input(result)
    return result


def validate_draft_input(value):
    if (value.get('saveToDraft') is not True or value.get('needsApproval') is not False
            or value.get('mode') != 'addToQueue' or value.get('schedulingType') != 'automatic'
            or any(k in value for k in ['dueAt','draftId','ideaId'])):
        raise BufferError('Cette étape autorise seulement saveToDraft=true, sans programmation.')


def draft_receipt(response, expected):
    """Un brouillon ne devient jamais un reçu confirmed:true de publication."""
    if response.get('errors'):
        raise BufferError('Résultat Buffer incertain ; examiner avant toute nouvelle tentative.')
    result = response.get('data', {}).get('createPost', {})
    if result.get('__typename') != 'PostActionSuccess':
        raise BufferError('Brouillon non confirmé par Buffer ; aucun nouvel essai automatique.')
    post = result.get('post', {})
    if (not post.get('id') or post.get('status') != 'draft' or post.get('sentAt') is not None or post.get('dueAt') is not None
            or post.get('channelId') != expected['channelId'] or post.get('text') != expected['text']
            or not post.get('assets')):
        raise BufferError('Réponse Buffer incompatible avec le brouillon attendu.')
    return {'bufferPostId':post['id'], 'channelId':post['channelId'], 'status':'draft', 'confirmed':False}


def ensure_schema(store):
    store.db.executescript('''
      CREATE TABLE IF NOT EXISTS buffer_media (
        job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL,
        filename TEXT NOT NULL UNIQUE, sha256 TEXT NOT NULL, url TEXT NOT NULL,
        PRIMARY KEY(job,revision));
      CREATE TABLE IF NOT EXISTS buffer_drafts (
        job TEXT NOT NULL REFERENCES jobs(id), revision INTEGER NOT NULL,
        channel TEXT NOT NULL, service TEXT NOT NULL, video_hash TEXT NOT NULL,
        payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'prepared',
        dispatch TEXT, receipt TEXT, response TEXT,
        PRIMARY KEY(job,revision,channel));
    ''')


def claim_draft(store, body):
    revision, channel, dispatch = body['revision'], body['channelId'], body['dispatchId']
    with store.tx():
        job = store.get(body['jobId'])
        if (type(revision) is not int or job['revision'] != revision or job['status'] != 'validated'
                or not isinstance(dispatch,str) or not re.fullmatch('[A-Za-z0-9_-]{1,100}',dispatch)):
            raise ValueError('Vidéo non validée ou version de brouillon obsolète.')
        row = store.db.execute('SELECT * FROM buffer_drafts WHERE job=? AND revision=? AND channel=?',
                               (job['id'],revision,channel)).fetchone()
        if not row:
            raise ValueError('Destination non préparée ; aucun appel Buffer autorisé.')
        if row['status'] != 'prepared':
            return {'requests':[], 'alreadyClaimed':True}  # Jamais rejouer une mutation incertaine.
        if json.loads(job['review'])['videoSha256'] != row['video_hash']:
            raise ValueError('La vidéo préparée ne correspond plus à la validation.')
        payload=json.loads(row['payload']);validate_draft_input(payload)
        store.db.execute("UPDATE buffer_drafts SET status='submitting',dispatch=? WHERE job=? AND revision=? AND channel=?",
                         (dispatch,job['id'],revision,channel))
        store.audit(job['id'],'buffer-draft-claimed',{'revision':revision,'channelId':channel})
        return {'requests':[{'jobId':job['id'],'revision':revision,'channelId':channel,'dispatchId':dispatch,
                            'request':{'query':DRAFT_MUTATION,'variables':{'input':payload}}}]}


def record_draft(store, body):
    job, revision, channel = body['jobId'], body['revision'], body['channelId']
    with store.tx():
        row=store.db.execute('SELECT * FROM buffer_drafts WHERE job=? AND revision=? AND channel=?',
                             (job,revision,channel)).fetchone()
        if not row or row['dispatch'] != body['dispatchId']:
            raise ValueError('Reçu Buffer sans réservation correspondante.')
        response=json.dumps(body['response'],sort_keys=True)
        if row['response']:
            if row['response'] != response:
                raise ValueError('Réponse différente pour un brouillon déjà traité.')
            return {'accepted':True,'status':row['status'],'publicationConfirmed':False}
        try:
            receipt=draft_receipt(body['response'],json.loads(row['payload']))
            status='draft'
        except BufferError:
            receipt=None;status='unknown'
        store.db.execute('UPDATE buffer_drafts SET status=?,receipt=?,response=? WHERE job=? AND revision=? AND channel=?',
                         (status,json.dumps(receipt),response,job,revision,channel))
        store.audit(job,'buffer-draft-result',{'revision':revision,'channelId':channel,'status':status})
        store.emit(f'buffer-draft:{job}:{revision}:{channel}',job,{'kind':'text',
            'text':(f"Brouillon Buffer {row['service']} enregistré pour {job}, version {revision}. Aucune publication."
                    if status=='draft' else f"Résultat Buffer à vérifier pour {job} ({row['service']}). Aucune nouvelle tentative automatique.")})
        return {'accepted':True,'status':status,'publicationConfirmed':False}
