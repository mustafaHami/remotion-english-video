# Audit du parcours diagnostic — 23 octobre 2026

Audit demandé par l'utilisateur : réception unique, identité, rétention n8n, doublons, redémarrage et corrélation de session. Aucune vidéo ni publication autorisée ou effectuée dans cet audit.

## Vérifié et corrigé

- Un seul Telegram Trigger actif : workflow `ypqdFC3lJ6UP2nj0`. Association et ancien test privé désactivés. Les filtres IF correspondent à l'identité confirmée, exigent une conversation privée et couvrent messages/callbacks ; le bridge recontrôle les deux identifiants. Trois requêtes synthétiques au bridge réel (mauvais utilisateur, conversation, callback) ont reçu `403`, sans événement enregistré. Ce contrôle ne simule pas un second compte réellement connecté à Telegram.
- Le workflow de notifications `i3qVaC6RQOB6wuqT` conservait chaque succès toutes les 10 secondes. **Corrigé** : succès `none`, erreurs `all`, sauvegarde de progression et exécutions manuelles désactivées. La version modifiée est publiée. Les reçus utiles restent dans la base des tâches indépendante.
- **1 636 scrutations vides** archivées sous `/var/lib/englizy/management/empty-poll-archive-*`, puis supprimées par l'API n8n. Une exécution réussie ayant effectué un envoi est conservée, ainsi que les historiques des autres workflows. Le script `scripts/prune-empty-notification-executions.py` fait une inspection sans mutation par défaut ; `--apply` exige une archive privée avant chaque suppression et recontrôle le contenu. Il ne cible ni erreur ni exécution avec envoi ni base de tâches.
- La rétention native observée dans l'image et sans surcharge d'environnement est active : **336 heures / 10 000 exécutions**, suppression logique toutes les 60 minutes et physique toutes les 15 minutes, tampon d'une heure. Les succès non conservés disparaissent de l'interface ; n8n garde temporairement des lignes marquées supprimées jusqu'au nettoyage physique. Le moteur de purge a été testé réellement dans une copie isolée, sans réseau ni port et avec tous les workflows désactivés : exécution terminée vieillie de 30 jours et ligne déjà marquée supprimées ; succès récent et exécution en attente conservés. Le test accélère uniquement dans la copie les intervalles à une minute et le tampon à zéro. La configuration de production n'a pas changé ; son cycle de 15 minutes n'a pas été chronométré. Rapport : `restore-pruning-check.json` dans la sauvegarde `20261023T212818910824Z`.
- Un événement Telegram est dédupliqué transactionnellement par `update_id`. La réservation d'une notification déjà envoyée ne la renvoie pas. Une livraison incertaine reste à réconcilier manuellement ; aucun renvoi automatique du nœud Telegram n'est configuré.
- **Corrigé** : une ancienne réservation du worker est désormais liée à son identifiant de traitement (`lease`). Elle ne peut pas récupérer un nouveau tour du même job après une réponse. Les anciens enregistrements sans lease deviennent inopérants, sans supprimer les tâches.
- Le contrôle du Telegram Trigger installé a aussi été rejoué sans réseau : secret invalide refusé, callbacks transmis, conservation des updates configurée. 39 tests Python simulés couvrent notamment doublons de demande/réponse, session exacte, réponses ambiguës, refus des tâches vidéo, réception d'un résultat malgré perte de réponse HTTP, interruption pendant Codex, anciens leases et purge sélective. Une réussite simulée ne constitue pas une conversation Telegram réelle.

## Redémarrage et sauvegardes réels

Avant modification : aucun job en génération ni en file. Les services Python ont été arrêtés à cette frontière sûre et la base sauvegardée. n8n a été arrêté/sauvegardé/redémarré avec le même volume et la même image. Sauvegarde : `/var/backups/englizy/20261023T212818910824Z`, intégrité SQLite et présence de la même clé contrôlées, un propriétaire/six workflows/deux identifiants. Le code des services a ensuite été installé et redémarré sous leurs comptes non root.

La tâche antérieure `3c098f98f159` reste `needs_input`, avec exactement la même question, session et résultat. Ses reçus d'envoi sont inchangés. Aucune génération supplémentaire n'a été lancée par le redémarrage. Preuves privées : `audit-current.json`, `audit-restart-initial.json`, `audit-identity-http.json`, `audit-retention.json`, `empty-poll-prune-report.json` dans `/var/lib/englizy/management`.

## Parcours Telegram complet — vérifié

Votre `/diagnostic` a été reçu par l'exécution n8n **1668** et a créé la tâche **`d7d42f15ce32`**. Le même événement réel a été rejoué deux fois auprès du bridge : une seule tâche, une seule invocation initiale. Codex a posé la question `97d1b8cdd6b4`, envoyée dans Telegram. Après redémarrage réel de n8n et du bridge, sa tâche, sa question et sa session étaient inchangées.

Le worker a été arrêté avant votre réponse pour observer sa persistance. Votre commande `/repondre … AUDIT-OK` a été enregistrée et la tâche mise en file. Un nouveau redémarrage de n8n et du bridge a conservé la réponse et la session. Le même événement de réponse a été rejoué deux fois sans nouvelle tâche ni invocation.

Le worker a ensuite repris **la même session `01a16aae-16ca-7290-a392-851b88487402`**. Résultat : `completed`, « Test terminé. Code de reprise : AUDIT-OK. », envoyé par le nœud Telegram avec le reçu **message 15**. Il y a eu exactement **deux tours Codex** pour cette tâche : question, puis conclusion. Une nouvelle relecture de l'événement de réponse après achèvement n'a pas relancé le travail.

Un dernier redémarrage des trois services après achèvement a laissé tâches, questions, réponses, accords et reçus inchangés. La boîte de notifications n'a remis aucun message envoyé en file. L'ancienne tâche de diagnostic reste conservée en attente ; elle n'a pas été supprimée ni confondue avec ce test. Aucun artefact vidéo n'a été créé.

Preuves privées supplémentaires dans `/var/lib/englizy/management` : `audit-real-demand.json`, `audit-question-restart.json`, `audit-answer-restart.json`, `audit-complete.json` et `audit-final-restart.json`. Les identifiants personnels et messages complets restent hors Git.

Le workflow HTTPS temporaire **`dFCuaedtvxhzK6tg` est désactivé**, son webhook répond `404`. Seuls **Réception Telegram et tâches durables** et **Questions et résultats vers Telegram** restent actifs. La commande `/diagnostic` reste disponible sur le récepteur autorisé ; la création vidéo et toute publication restent refusées par le runtime.

Références : [gestion des données d'exécution n8n](https://docs.n8n.io/hosting/scaling/execution-data/), [variables de rétention](https://docs.n8n.io/hosting/configuration/environment-variables/executions/). Les valeurs ont aussi été vérifiées dans le code réellement installé de n8n 2.44.5.

Contrôles du dépôt réussis : `npm run check`, `npm test`, `npm run verify`, `git diff --check`. Livraison par la PR #14, sans fusion ni modification des protections.
