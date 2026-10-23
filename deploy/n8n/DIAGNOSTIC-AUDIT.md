# Audit du parcours diagnostic — 23 octobre 2026

Audit demandé par l'utilisateur : réception unique, identité, rétention n8n, doublons, redémarrage et corrélation de session. Aucune vidéo ni publication autorisée ou effectuée dans cet audit.

## Vérifié et corrigé

- Un seul Telegram Trigger actif : workflow `ypqdFC3lJ6UP2nj0`. Association et ancien test privé désactivés. Les filtres IF correspondent à l'identité confirmée, exigent une conversation privée et couvrent messages/callbacks ; le bridge recontrôle les deux identifiants. Trois requêtes synthétiques au bridge réel (mauvais utilisateur, conversation, callback) ont reçu `403`, sans événement enregistré. Ce contrôle ne simule pas un second compte réellement connecté à Telegram.
- Le workflow de notifications `i3qVaC6RQOB6wuqT` conservait chaque succès toutes les 10 secondes. **Corrigé** : succès `none`, erreurs `all`, sauvegarde de progression et exécutions manuelles désactivées. La version modifiée est publiée. Les reçus utiles restent dans la base des tâches indépendante.
- **1 636 scrutations vides** archivées sous `/var/lib/englizy/management/empty-poll-archive-*`, puis supprimées par l'API n8n. Une exécution réussie ayant effectué un envoi est conservée, ainsi que les historiques des autres workflows. Le script `scripts/prune-empty-notification-executions.py` fait une inspection sans mutation par défaut ; `--apply` exige une archive privée avant chaque suppression et recontrôle le contenu. Il ne cible ni erreur ni exécution avec envoi ni base de tâches.
- La rétention native observée dans l'image et sans surcharge d'environnement est active : **336 heures / 10 000 exécutions**, suppression logique toutes les 60 minutes et physique toutes les 15 minutes, tampon d'une heure. Les succès non conservés disparaissent de l'interface ; n8n garde temporairement des lignes marquées supprimées jusqu'au nettoyage physique. Leur disparition physique par le cycle natif reste à observer ; aucun réglage d'horloge ni seuil de purge n'a été forcé.
- Un événement Telegram est dédupliqué transactionnellement par `update_id`. La réservation d'une notification déjà envoyée ne la renvoie pas. Une livraison incertaine reste à réconcilier manuellement ; aucun renvoi automatique du nœud Telegram n'est configuré.
- **Corrigé** : une ancienne réservation du worker est désormais liée à son identifiant de traitement (`lease`). Elle ne peut pas récupérer un nouveau tour du même job après une réponse. Les anciens enregistrements sans lease deviennent inopérants, sans supprimer les tâches.
- 39 tests Python simulés couvrent notamment doublons de demande/réponse, session exacte, réponses ambiguës, refus des tâches vidéo, réception d'un résultat malgré perte de réponse HTTP, interruption pendant Codex, anciens leases et purge sélective. Une réussite simulée ne constitue pas une conversation Telegram réelle.

## Redémarrage et sauvegardes réels

Avant modification : aucun job en génération ni en file. Les services Python ont été arrêtés à cette frontière sûre et la base sauvegardée. n8n a été arrêté/sauvegardé/redémarré avec le même volume et la même image. Sauvegarde : `/var/backups/englizy/20261023T212818910824Z`, intégrité SQLite et présence de la même clé contrôlées, un propriétaire/six workflows/deux identifiants. Le code des services a ensuite été installé et redémarré sous leurs comptes non root.

La tâche antérieure `3c098f98f159` reste `needs_input`, avec exactement la même question, session et résultat. Ses reçus d'envoi sont inchangés. Aucune génération supplémentaire n'a été lancée par le redémarrage. Preuves privées : `audit-current.json`, `audit-restart-initial.json`, `audit-identity-http.json`, `audit-retention.json`, `empty-poll-prune-report.json` dans `/var/lib/englizy/management`.

## Parcours Telegram complet — en attente de participation

L'utilisateur a été invité à envoyer `/diagnostic` à son bot. Il doit ensuite répondre au **message de question de cette nouvelle tâche**, après le contrôle de redémarrage. La réponse par citation ou `/repondre tâche question réponse` permet de distinguer ce test de l'ancienne question toujours conservée.

Restent à constater réellement : nouvelle demande Telegram, question Codex, conservation de sa réponse après redémarrage, reprise du même UUID, résultat et reçu Telegram. Le workflow HTTPS temporaire `dFCuaedtvxhzK6tg` est désactivé ; son webhook répond réellement `404`. Il ne sert pas au nouveau test lancé depuis Telegram. Preuve privée : `audit-diagnostic-disabled.json`. La réception et les notifications sont nécessaires pour terminer l'aller-retour Telegram.

Références : [gestion des données d'exécution n8n](https://docs.n8n.io/hosting/scaling/execution-data/), [variables de rétention](https://docs.n8n.io/hosting/configuration/environment-variables/executions/). Les valeurs ont aussi été vérifiées dans le code réellement installé de n8n 2.44.5.
