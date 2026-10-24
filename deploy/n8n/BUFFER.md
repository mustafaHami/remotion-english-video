# Buffer : trois brouillons vérifiés, aucune publication

Le 24 octobre 2026, l'utilisateur a choisi Instagram, TikTok et YouTube pour préparer des brouillons de la vidéo validée `ecee3555f0c8`, révision 2. Ce choix n'autorise ni publication ni programmation. La tâche, Excel et `planning/production.json` restent `validated` ; `shared_at`, `closed_at` et l'accord de publication restent vides.

## Connexion et workflow

La clé API Buffer est lue depuis `/var/lib/englizy/secrets/buffer-access-token` (root, 0600, parents 0700). Une copie est stockée chiffrée dans les identifiants n8n « Englizy — Buffer API », type Header Auth. Le fichier local est conservé pour l'inspection en lecture seule. Aucun secret n'est exporté dans Git. Telegram reste exclusivement géré par ses nœuds et son identifiant n8n existant.

Le workflow actif **Englizy — Brouillons Buffer (sans publication)**, ID `xeDjKycj3wDwtrGt`, contient : webhook authentifié → réservation SQLite → branche déjà traité ou création → HTTP GraphQL Buffer → reçu SQLite. Aucun Telegram Trigger, horaire, nœud de publication ou bouton Publier n'est ajouté. Il existe trois workflows actifs au total : réception Telegram, notifications, brouillons Buffer. Les quatre workflows de test demeurent désactivés.

Le code n'accepte qu'une vidéo `validated`, sa révision exacte, son empreinte validée et une destination préalablement préparée par l'opérateur. Le corps GraphQL impose `saveToDraft: true`, sans `dueAt`. Le paramètre API obligatoire `mode: addToQueue` ne programme rien lorsque `saveToDraft` est vrai ; le statut effectivement relu doit être `draft`, avec `sentAt` et `dueAt` nuls.

Les tables `buffer_media` et `buffer_drafts` conservent les liens tâche/version/destination, l'empreinte, les textes préparés, la réservation et les reçus. Une réservation passe atomiquement de `prepared` à `submitting` avant l'appel externe. Aucun retry de la création Buffer. Une interruption ou réponse incertaine reste `submitting` ou `unknown` et nécessite une réconciliation ; ne pas remettre aveuglément à `prepared`. Un reçu identique est idempotent. Ni `draft` ni un reçu de notification ne vaut publication confirmée.

Le workflow ne conserve pas les exécutions n8n, y compris les erreurs, car le webhook porte un en-tête secret. Les états, résultats et notifications utiles restent dans SQLite. Aucun polling périodique de Buffer : seules les lectures d'inspection et les créations explicitement préparées ont été exécutées.

## Copie média et rétention

Buffer demande une URL HTTPS directe. Une seule copie de la vidéo validée est servie sous `/englizy-media/<64 caractères aléatoires>.mp4`, depuis `/var/lib/englizy-public-media` (root:www-data, dossier 0750, MP4 0640). L'URL est accessible sans connexion à qui la connaît, sans index de dossier, sans journal des accès et sans publication du dépôt. Elle reste hors Git. GET/HEAD seulement, type `video/mp4`, accès partiel HTTP Range pris en charge. Le reste de n8n garde son proxy et son authentification.

Le fragment installé est `/etc/nginx/snippets/englizy-buffer-media.conf`, inclus dans le serveur HTTPS de `/etc/nginx/sites-available/n8n`. Les chemins inexistants sous le préfixe renvoient 404. Un chemin normalisé hors de ce préfixe peut recevoir le HTML de l'interface n8n ; cela n'expose aucun fichier SQLite.

Cette copie est incluse dans la suppression des MP4 **10 jours après publication terminée confirmée**. Les chemins, liens et empreintes sont contrôlés avant suppression. À 15 jours après clôture, les légendes/requêtes/réponses détaillées locales sont purgées ; les clés et reçus minimaux restent pour empêcher les doublons. Les brouillons présents chez Buffer ne sont pas supprimés par cette purge locale. Une vidéo validée non publiée conserve ses médias et ses données.

## Préparation et installation

Après inventaire, sauvegarde et revue :

```sh
sudo python3 scripts/buffer-admin.py inspect
sudo python3 scripts/buffer-admin.py prepare --job IDENTIFIANT --revision VERSION --services instagram tiktok youtube
python3 scripts/build-buffer-workflow.py
sudo python3 scripts/install-buffer-workflow.py
```

La préparation actuelle est volontairement limitée au premier épisode option 1 dont les dix verbes sont contrôlés avant emploi des légendes. Un autre contenu nécessite ses propres textes ; le script refuse de lui appliquer ceux-ci. `--update` sur l'installateur exige une revue, sauvegarde la version n8n et conserve le chemin privé et les credentials. Les identifiants de comptes, postes et le chemin du webhook sont dans `/var/lib/englizy/management`, pas dans les exports génériques.

Déployer les modules du bridge à une frontière sans travail en cours selon OPERATIONS.md. Installer le fragment nginx après sauvegarde, puis `nginx -t` avant rechargement. L'unité de suivi autorise également la suppression contrôlée dans `/var/lib/englizy-public-media`.

## Vérifications réelles

- API Buffer authentifiée : les trois canaux sont connectés et autorisent la gestion des brouillons.
- Créations n8n réservées dans les exécutions **5176, 5179, 5181**. Trois identifiants Buffer distincts conservés, un par destination. Relecture API : **draft**, aucune date, aucune publication.
- Média reconnu sur les trois brouillons : `video/mp4`, **1080 × 1920**, **73 515 ms**, miniature présente, `isVideoProcessing: false`. HEAD 200, Range 206 et SHA-256 de la copie HTTPS identique au MP4 validé.
- Reçus Telegram **28–30** pour les brouillons, **31–33** pour les légendes proposées et les réglages YouTube. Textes envoyés par les nœuds Telegram existants.
- Redémarrages du bridge/worker puis du conteneur n8n : les trois reçus persistent. Une répétition réelle de la demande renvoie `alreadyClaimed: true` sans nouvelle réservation ni appel Buffer. Défaut initial corrigé : une sortie vide provoquait « No item to return was found » dans n8n ; une branche explicite répond maintenant au doublon.
- Le suivi Excel termine sans erreur ; la vidéo reste `validated`. Aucun MP4 réel n'est éligible à la purge. Le récapitulatif horaire du 24 octobre à 09h Paris a été envoyé, reçu **27**.
- Tests simulés : destination étrangère, version périmée, vidéo non validée, mutation non brouillon, réponse incohérente, interruption, reçu répété et copie publique modifiée refusée avant purge.

Preuves privées : `/var/lib/englizy/management/buffer-verification.json`, `buffer-readback-*.json`. Sauvegarde avant modification : `/var/backups/englizy/buffer-before-20261024T071642Z` (SQLite cohérent, code, nginx et unité). Sauvegarde n8n après connexion : `/var/backups/englizy/20261024T072116886376Z` ; extraction isolée, intégrité SQLite et égalité de la clé de chiffrement vérifiées (1 utilisateur, 7 workflows, 3 credentials). Les clés restent hors du dépôt.

## Suite non exécutée

La lecture humaine des brouillons et les éventuelles corrections restent possibles. L'adaptateur de publication réelle avec accord lié au MP4, aux légendes, destinations et horaire n'est pas encore activé. Il faudra ensuite suivre séparément chaque plateforme, réconcilier les résultats incertains et mettre à jour l'historique uniquement sur publication confirmée. Aucun horaire quotidien de création/publication n'est activé.

Références : [création de brouillon](https://developers.buffer.com/examples/create-draft-post.html), [vidéo](https://developers.buffer.com/examples/create-video-post.html), [hébergement du média](https://developers.buffer.com/guides/hosting-media.html), [schéma API](https://developers.buffer.com/reference.html).
