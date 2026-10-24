# Publication autorisée depuis Telegram

`/partage` déclare une publication manuelle déjà terminée. `/publier IDENTIFIANT VERSION CONFIRME` autorise l'envoi immédiat des brouillons préparés pour cette version. Une commande incomplète affiche l'aide sans accord ni changement d'état. L'identité Telegram privée est contrôlée avant les deux commandes.

Le 24 octobre 2026, après choix d'Instagram, TikTok et YouTube et réception des légendes dans Telegram, l'utilisateur a précisé dans la conversation Codex : « Lancer la publication des brouillons ». Cet accord a été enregistré pour la seule vidéo `ecee3555f0c8`, version 2, avec ses trois brouillons existants. Il ne vaut pas accord pour une autre vidéo ni activation d'un horaire quotidien.

## Préparation, accord et déclenchement

`scripts/prepare-publication.py --job IDENTIFIANT --revision VERSION` relit les brouillons via l'API Buffer et vérifie : vidéo validée, empreinte de la copie média, destination, légende effectivement envoyée dans Telegram, paramètres de plateforme, statut draft sans date et action publishPostNow disponible. Il prépare une proposition sans l'approuver.

La proposition durable contient les identifiants des brouillons, le SHA-256 du MP4, les textes, médias, métadonnées, comptes, version et mode immédiat. L'accord persiste avec l'identité, la source et le hash de cette proposition. Un changement invalide son utilisation ; une commande ancienne ne peut pas valider une autre version. Un deuxième accord identique est sans effet supplémentaire.

Le bridge doit aussi disposer de `PUBLISH_ENABLED=true`. Le drop-in explicite `/etc/systemd/system/englizy-bridge.service.d/30-publication.conf` active ce contrôle sur le bridge uniquement. Les commandes historiques `daily.cjs --publish` et le worker Codex ne sont pas activés pour publier.

Le workflow **Englizy — Publication autorisée et suivi Buffer**, ID `zT7sSe30Ts9xx5V2`, comporte des nœuds HTTP visibles :

1. Réserver les lectures de tâches autorisées.
2. Relire le brouillon Buffer et comparer son contenu à la proposition approuvée.
3. Réserver atomiquement un unique envoi.
4. Envoyer `editPost` sur l'identifiant existant, `mode: shareNow`, `saveToDraft: false`, avec le contenu approuvé.
5. Conserver le résultat, puis relire uniquement le statut lors des contrôles suivants.

Le déclencheur technique tourne chaque minute. Sans tâche autorisée, aucun appel Buffer n'est effectué. Ce déclencheur ne génère pas de vidéo et ne donne aucun accord. Les lectures sont progressivement espacées (1, 1, 2, 5, 15, 30, 60, 120 minutes), huit réservations de lecture maximum avant intervention. Un webhook authentifié permet aussi un contrôle opérateur sans contourner ces limites.

Les exécutions n8n ne sont pas conservées ; l'en-tête privé du webhook n'entre pas dans un historique persistant. Les identifiants Buffer sont exclusivement dans les credentials n8n pour les mutations. Python prépare et contrôle les requêtes, mais n'effectue pas la mutation HTTP lui-même.

## Reprise et résultats

`buffer_publications` conserve une ligne par tâche/version/destination : proposition, requête prévue, réservation, statut, reçus et date du prochain contrôle. Une réservation passe à `submitting` avant l'appel externe. Il n'y a **aucun retry de mutation**. Une interruption, erreur réseau ou réponse ambiguë entraîne une réconciliation du même identifiant par lecture ; elle ne recrée et ne renvoie pas un post.

Un brouillon modifié entre l'accord et le dernier contrôle est bloqué. `scheduled`, `sending` et une réponse acceptée ne valent pas publication confirmée. Un statut `sent` doit avoir `sentAt`, le mode `automatic` et ne pas être une déclaration manuelle de notification. Les succès par réseau sont conservés et ne sont pas renvoyés si un autre échoue.

La tâche reste ouverte en `publishing`, `partially_published` ou `publication_unknown`. Elle passe à `shared`, avec `closed_at`, uniquement quand toutes les destinations approuvées sont confirmées. Les URLs viennent de Buffer ; un lien absent n'est jamais inventé. Le service de suivi synchronise alors Excel, production.json et publications.json, sans nouvelle publication.

Chaque résultat est envoyé par le workflow Telegram existant. Les notifications sont dédupliquées. Une publication partielle ou une erreur conserve la tâche et les médias. La rétention à 10/15 jours ne commence qu'après confirmation et clôture ; la purge des détails conserve les identifiants et reçus minimaux nécessaires à la déduplication.

## Installation et intervention

Après sauvegarde et contrôles, déployer les modules via la procédure OPERATIONS.md à une frontière sans génération en cours. Installer le drop-in seulement dans le cadre d'un parcours de publication autorisé, puis redémarrer le bridge. Construire et installer le workflow :

```sh
python3 scripts/build-publication-workflow.py
sudo python3 scripts/install-publication-workflow.py
```

L'installateur préserve un workflow déjà référencé ; il ne crée aucun accord. Le chemin privé, les références et l'accord de cette première publication sont stockés sous `/var/lib/englizy/management`. Pour suspendre tout nouveau traitement, désactiver ce workflow et retirer le drop-in ; ne pas réinitialiser une réservation ni restaurer une ancienne base par-dessus les reçus actuels. Une demande déjà acceptée par Buffer doit être vérifiée côté service.

## Contrôles

70 tests Python couvrent notamment absence d'accord, identité, ancienne version, modification des légendes ou de la proposition, double accord, double déclenchement après réouverture, erreur/timeout, résultat partiel, sent simulé par notification, espacement des lectures et conservation des reçus après purge. Tests externes et résultats réels sont consignés dans le bilan ci-dessous.

Sauvegarde avant activation : `/var/backups/englizy/publication-before-20261024T075144Z`. Le premier essai authentifié sans accord n'a renvoyé aucune action ; sans authentification le webhook renvoie 403. L'accord utilisateur est dans `publication-user-approval.json`, hors Git.

Références officielles : [édition d'un post et statuts](https://developers.buffer.com/reference.html), [cycle de publication](https://developers.buffer.com/guides/posts-and-scheduling.html).

## Résultat réel du 24 octobre 2026

Les trois mutations ont été acceptées puis confirmées par lecture, sans renvoi. Instagram et YouTube ont été confirmés d'abord, avec tâche `partially_published` ; TikTok a ensuite terminé. Le statut `shared` et la clôture ont été enregistrés à **07:55:05 UTC (09:55:05 Paris)**.

| Destination | Date `sentAt` UTC | Lien retourné par Buffer |
| --- | --- | --- |
| Instagram | 07:53:29 | https://www.instagram.com/reel/De3o9Ooj0Wo/ |
| TikTok | 07:54:17 | https://tiktok.com/@englizygo/video/7700139194793889057 |
| YouTube | 07:52:35 | https://www.youtube.com/watch?v=LnhpfHyuG5w |

Buffer a rapatrié le média TikTok dans son stockage S3 après publication. Le contrôle avant envoi exige l'URL exacte approuvée ; le contrôle après publication accepte ce changement d'URL, en vérifiant l'identifiant du post, le compte, le texte, les réglages, le nombre et les types de médias. Aucun lien social n'a été déduit ou inventé. La lecture subjective des publications sur les plateformes n'a pas été effectuée par l'agent.

Reçus Telegram **36–40** : accord, résultats par réseau et clôture. Trois réservations de mutation exactement sont présentes dans l'audit. Le Journal Excel (ligne 8), production.json et publications.json ont été relus : vidéo `shared`, trois destinations et trois liens ; le registre contient maintenant trois publications (deux historiques préservées et celle-ci). Les preuves privées sont dans `/var/lib/englizy/management/publication-verification.json`.

Quatre workflows sont actifs : réception unique Telegram, notifications, préparation des brouillons et publication autorisée/suivi. Les quatre workflows temporaires de test restent désactivés. Aucun horaire de création ou publication quotidienne n'est activé.

Sauvegardes après vérification : `/var/backups/englizy/publication-verified-20261024T075918Z` (base et planning) et `/var/backups/englizy/20261024T075918571800Z` (n8n : 8 workflows, 3 credentials, extraction et intégrité vérifiées). Après redémarrage Python et n8n, le webhook de contrôle retourne zéro lecture : les trois reçus restent `sent`, avec exactement trois réservations d’envoi et aucun renvoi. Les modules déployés correspondent au code livré.
