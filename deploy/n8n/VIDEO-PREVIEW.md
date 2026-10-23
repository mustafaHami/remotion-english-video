# Création vidéo et prévisualisation privée

Étape autorisée après le diagnostic Telegram/Codex. Évolution des états, suivi Excel et rétention : [TRACKING.md](TRACKING.md). Buffer, les destinations sociales et les horaires de publication restent déconnectés. Aucun bouton de publication n'est exposé.

## Parcours

1. `/video` ou `/options` ouvre le catalogue des 14 noms du projet dans Telegram, avec boutons numérotés. Le premier menu a été envoyé par n8n (message 16).
2. Le choix appartient au compte et à la conversation confirmés. Un numéro saisi en texte sélectionne également le menu ouvert ; une réponse citant explicitement une question reste rattachée à cette question. Le premier clic crée un job vidéo ; un double clic ou un ancien bouton consommé retrouve le même job. `/choisir <identifiant du menu> <numéro>` est une alternative explicite.
3. Le worker appelle Codex avec le skill `.agents/skills/create-english-video/SKILL.md`. Il lit planning Excel, historique et épisodes, sélectionne un contenu inédit puis crée un épisode distinct. Les scripts du projet préparent l'audio, le MP4 et les contrôles. Remotion utilise deux rendus de frames concurrents.
4. Les questions nécessaires gardent le mécanisme de corrélation et de reprise testé. Les messages ordinaires ne créent aucune nouvelle vidéo.
5. Le runner vérifie les chemins, manifeste, contenu, empreinte, pistes audio/vidéo, dimensions, durée et rapports. Il relance le contrôle technique ; l'inspection d'images reste une action de l'agent à constater séparément. Une écoute subjective absente est annoncée.
6. Le worker prépare une copie privée du MP4 dans `/var/lib/englizy-media/<job>/r<révision>/preview.mp4`. Sous 47 Mio, copie identique ; au-delà, copie réduite en 720 × 1280, H.264/AAC, sans toucher à l'original. Une copie encore trop grande provoque un échec explicite. L'empreinte du fichier envoyé et celle de l'original sont distinctes et persistées.
7. n8n télécharge cette seule copie via une route interne authentifiée, puis son nœud **Envoyer la prévisualisation MP4** utilise `sendVideo` avec le binaire. Aucun dossier public ni URL de média publique n'est créé. Le bridge vérifie l'empreinte avant chaque téléchargement.
8. Le reçu Telegram fait passer le job de `awaiting_preview` à `pending_validation` (anciennement `awaiting_review`). Cet état n'est **pas** une approbation de publication. Aucun accord social n'est créé.

## Comptes et fichiers

Le projet reste monté en lecture seule dans les deux services. Le drop-in `englizy-worker-video.conf` ouvre seulement `content/episodes`, `public/audio/production`, `output/options` et `node_modules/.cache` au worker. Les dossiers existants appartiennent à root avec un droit de groupe et le sticky bit ; les anciens fichiers root restent protégés, sauf `provenance.json`, nécessaire à la mise à jour audio. Les nouveaux fichiers sont privés au worker ; root peut les inspecter et les sauvegarder. Modèles, scripts, planning, historique et `.git` restent en lecture seule.

L'accès réel a été testé sous l'UID du worker dans son espace de montage : écriture dans les quatre répertoires autorisés, refus sur modèle/historique/scripts/Git, absence d'accès au secret de transport n8n et à la base du bridge. Preuve privée : `/var/lib/englizy/management/video-worker-access.json`.

Le stockage de prévisualisation appartient au worker et au groupe bridge, avec dossiers `2750` et fichiers `0640`. Le worker écrit les copies ; le bridge les lit. Le conteneur n8n ne reçoit aucun montage du dépôt ni socket Docker. Les jetons Telegram restent exclusivement dans les identifiants n8n.

Les succès de scrutation n8n ne sont pas conservés ; les erreurs et reçus durables restent disponibles. Un envoi Telegram incertain n'est pas relancé automatiquement. Les fichiers du job et les aperçus restent conservés après réception.

## Installation et retour au diagnostic

Examiner les jobs et attendre qu'aucun travail ne soit en cours ou en file avant de stopper les services. Sauvegarder états, configurations et code avant mise à jour.

```sh
sudo systemctl stop englizy-worker englizy-bridge
sudo python3 scripts/install-automation-services.py --enable-video --start
# Après revue des changements n8n existants :
sudo python3 scripts/install-codex-workflows.py --update --activate
```

L'installateur de workflows sauvegarde les versions précédentes dans le stockage privé et refuse d'écraser des nœuds ajoutés hors export. Les autres modifications manuelles doivent être examinées avant `--update`. Les identifiants et webhook IDs existants sont réutilisés ; le diagnostic HTTPS temporaire reste inactif.

`--diagnostic-only` retire seulement le drop-in vidéo de cet installateur et désactive les nouvelles créations vidéo dans la configuration. Ne pas l'utiliser pendant une fabrication. Le stockage, les rendus et les tâches ne sont pas supprimés. Une mise à jour sans ces drapeaux conserve le mode précédent.

Sauvegardes avant installation : `/var/backups/englizy/video-stage-20261023T215816Z/automation-before.tar.gz` (états/configurations/code privés) et `/var/backups/englizy/20261023T215817429207Z` (n8n, même volume et clé contrôlés). Après production, `/var/backups/englizy/video-verified-20261023T221806Z/automation-and-media.tar.gz` contient les états, identifiants privés, épisodes, WAV, MP4 et copie Telegram ; `/var/backups/englizy/20261023T221810058923Z` contient n8n. Extraction isolée : intégrité SQLite, reçu envoyé, confirmation humaine et empreintes des deux MP4 contrôlés. Après redémarrage de n8n et des services, reçu inchangé, aucun job relancé, un seul récepteur Telegram actif et webhook protégé. Ces archives contiennent des secrets : dossiers 0700, fichiers 0600, hors dépôt.

## Vérification

47 scénarios Python simulés passent à cette étape. Les tests supplémentaires couvrent catalogue, double clic, compte non autorisé, mode vidéo du worker, question nécessaire, résultat non publiant, fichier modifié, chemin hors stockage, rollback et persistance du reçu de prévisualisation. Aucun de ces tests simulés ne prétend produire un véritable MP4.

Menu réellement envoyé (message 16), puis option **1** choisie en texte par l'utilisateur, exécution n8n **1856**. Le texte « 1 » avait initialement été associé à l'ancien diagnostic ouvert : la priorité du menu numérique a été corrigée, avec test de non-régression, et le choix original récupéré une seule fois dans la tâche `ecee3555f0c8`. L'ancien diagnostic et son résultat sont conservés dans l'audit ; aucun événement n'a été effacé.

Le premier lancement vidéo a échoué avant toute création de contenu : les répertoires protégés `.codex` et `.aws` étaient absents du montage parent en lecture seule. Ils sont désormais créés vides par l'installateur, sans lever les protections du sandbox. Après vérification, la même tâche/session a été reprise en révision 2, en conservant le résultat d'échec de la révision 1. Les bibliothèques système `libnss3` et `libnspr4`, requises par Chromium et absentes du VPS, ont aussi été installées ; aucune image ou donnée n8n n'a changé.

`sudo python3 scripts/check-video-worker.py --browser` vérifie réellement, sous le compte worker et dans le sandbox Codex configuré comme la production : lecture du skill/planning, écriture dans les quatre chemins autorisés, refus sur les modèles/historique/Git et démarrage du navigateur. Ce contrôle a réussi. L'accès réseau est nécessaire à la préparation vocale et aux connexions locales du navigateur ; les droits de fichiers restent limités.

La première fabrication réelle a réussi : tâche `ecee3555f0c8`, révision 2, option 1, dix verbes réguliers du quotidien. Création du dossier le **24/10/2026 à 00:09:29 Europe/Paris**, fin de rendu le 23/10 à 22:11:57 UTC. MP4 : `output/options/option-1/2026-10-24_00-09-29/option-1.mp4`, **73,5 s, 1080 × 1920, 30 i/s, 4 758 425 octets**, H.264 avec audio. Les 2 205 frames et la piste audio sont décodées, les 22 voix contrôlées, zéro erreur de cadrage. Captures, transitions et gestes du renard inspectés avec `view_image` ; revue conservée dans `visual-review.json`. Aucun modèle ni historique de publication n'a changé.

Deux défauts supplémentaires ont été corrigés pendant ce premier parcours : une consigne trop longue a été raccourcie dans l'épisode avec narration synchronisée avant qu'un MP4 existe ; le `chmod` setgid du stockage privé était refusé par `RestrictSUIDSGID`. Le worker utilise désormais l'héritage de groupe et de permissions à la création des dossiers, sans lever cette protection. Le résultat validé est enregistré dans une phase `preparing` avant préparation de la copie. Sa reprise après redémarrage est testée sans nouvel appel à Codex. Une copie réelle de ce MP4 a aussi été préparée sur deux révisions sous un service jetable avec `RestrictSUIDSGID=yes`, UID worker et umask 0077 : groupe bridge hérité, dossiers 2750 et fichiers 0640 confirmés ; seules les copies temporaires de contrôle ont été retirées. Pour ce premier incident, le résultat déjà validé a été récupéré après contrôle opérateur, avec audit, sans nouveau rendu ni nouvelle session.

Le nœud Telegram de n8n a réellement envoyé le MP4 : **message 25**, reçu durable `ready:ecee3555f0c8:2`, tâche `awaiting_review`. Copie identique à l'original, sans compression supplémentaire ; empreintes vérifiées. L'utilisateur a confirmé **« Lecture, image et son corrects »**. Cette confirmation est persistée dans l'audit avec révision et empreinte ; le champ d'approbation de publication reste vide. L'agent n'a pas effectué d'écoute subjective lui-même. Preuve privée : `/var/lib/englizy/management/first-video-result.json`.

Deux workflows restent actifs : réception unique et notifications. Les quatre workflows de test restent inactifs. Limites : clic réel sur un bouton non encore constaté (ce premier choix était numérique en texte ; callbacks et double clic testés en simulation), compression d'un MP4 volumineux non vérifiée en production, Buffer et parcours de publication non configurés.

Références vérifiées : [nœud Telegram sendVideo n8n](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.telegram/message-operations/#send-video), [Telegram Bot API sendVideo](https://core.telegram.org/bots/api#sendvideo). La limite consultée est de 50 MB ; la marge locale de 47 Mio reste inférieure.
