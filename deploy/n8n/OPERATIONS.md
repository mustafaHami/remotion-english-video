# Intégration n8n — relevé VPS du 23 octobre 2026

HTTPS, Telegram et le lancement d'un diagnostic Codex sont opérationnels. Le parcours demande → question Codex → réponse Telegram → reprise de la même session → résultat a été vérifié, avec conservation de la question puis de la réponse après redémarrage. La production vidéo, la prévisualisation et Buffer ne sont pas encore opérationnels. Aucun rappel quotidien ni publication sociale n'est activé.

## Installation conservée et accès

| Élément | Configuration observée |
| --- | --- |
| VPS | `srv2080063`, Ubuntu 26.04.1 LTS, x86_64, environ 16 Go RAM |
| Dépôt | `/root/projects/remotion-english-video`, synchronisé sans écrasement depuis `origin/main` à `a9f8276` avant les changements |
| Outils | Node 24.22.1, npm 11.19.1, Python 3.14.4, Codex CLI 0.164.0 |
| n8n | Conteneur `n8n-n8n-1`, image conservée `n8nio/n8n:2.44.5` |
| Compose | `/root/services/n8n/compose.yaml` |
| Données | Volume `n8n_n8n_data`, monté sur `/home/node/.n8n` ; SQLite et clé dans ce volume |
| Port n8n | `127.0.0.1:5678` ; le tunnel SSH reste fonctionnel |
| Entrée HTTPS | nginx 1.28.3, `/etc/nginx/sites-available/n8n`, lien dans `sites-enabled` |
| Domaine | `n8n.mhd-projects.cloud`, A `187.126.5.210`, aucun AAAA au relevé |
| Certificat | Let’s Encrypt, expiration initiale 21 janvier 2027 ; TLS 1.3 observé |
| Renouvellement | `certbot.timer`, challenge webroot `/var/lib/letsencrypt`, hook `reload-nginx` |
| Éditeur | Authentification du propriétaire existant conservée ; API sans clé = `401` |
| Secrets de gestion | `/var/lib/englizy/secrets` en `0700`, fichiers `0600`, hors partage Samba |

Le partage Samba `projects` expose `/root/projects`. Ne pas placer les secrets opérationnels dans le dépôt, même dans un fichier ignoré. Le compte n8n propriétaire existant a été préservé. Aucun volume n'a été remplacé ni réinitialisé. Le conteneur a été recréé par Compose avec la même image et le même volume pour appliquer les URL externes.

Variables ajoutées au service n8n : `N8N_HOST=n8n.mhd-projects.cloud`, `N8N_PROTOCOL=https`, `N8N_EDITOR_BASE_URL=https://n8n.mhd-projects.cloud`, `N8N_WEBHOOK_URL=https://n8n.mhd-projects.cloud/`, `N8N_PROXY_HOPS=1`. Le proxy transmet les en-têtes attendus et les WebSockets. Le fichier [nginx.conf](nginx.conf) correspond à la configuration installée. Aucun socket Docker n'est monté dans n8n.

Le certificat a été obtenu sans adresse email de contact ACME. Son renouvellement est configuré. `certbot renew --dry-run --cert-name n8n.mhd-projects.cloud --run-deploy-hooks` a réussi, avec contrôle de configuration et rechargement nginx.

Google : réexamen réussi déclaré par l'utilisateur. Le 23 octobre, l'outil public Google renvoyait le statut `6` (« aucune donnée disponible ») pour le domaine et le sous-domaine. Cela ne constitue pas un certificat d'absence de risque. L'utilisateur a ensuite confirmé une connexion réussie à l'éditeur HTTPS depuis son PC. Aucun contournement de protection navigateur n'a été demandé.

## Sauvegarde et retour arrière

Sauvegarde initiale : `/var/backups/englizy/20261023T132207439537Z` (dossier `0700`, fichiers `0600`). Elle contient Compose, l'intégralité du volume n8n dont sa clé de chiffrement et un manifeste SHA-256. n8n a été brièvement arrêté pour la cohérence, puis redémarré.

```sh
sudo python3 scripts/backup-n8n.py
```

Le script inspecte les chemins du conteneur au lieu de supposer un volume neuf. Il extrait ensuite la sauvegarde dans un dossier isolé, vérifie l'intégrité SQLite et compare la clé de chiffrement. Ce contrôle a réussi : un utilisateur, aucun workflow et aucun identifiant lors de la sauvegarde initiale.

Un démarrage réel de cette sauvegarde a aussi réussi avec `sudo python3 scripts/test-n8n-restore.py /var/backups/englizy/20261023T132207439537Z` : même image déjà présente, copie temporaire des données, réseau Docker `none`, aucun port publié, aucun volume de production monté. Le propriétaire restauré est reconnu et `/healthz/readiness` répond. Les workflows de la copie sont désactivés avant démarrage. Le conteneur de test et la copie temporaire ont ensuite été retirés ; le rapport `restore-boot-check.json` reste dans la sauvegarde. Cette sauvegarde initiale ne contenant pas encore d'identifiants, ce test ne prouve pas leur déchiffrement futur.

Une seconde sauvegarde cohérente a réussi après réception du code Telegram : `/var/backups/englizy/20261023T162623329351Z`, avec un utilisateur, deux workflows et un identifiant. Son extraction, son intégrité SQLite et sa clé ont été contrôlées. Cette sauvegarde est désormais complétée par celle décrite ci-dessous.

La sauvegarde `/var/backups/englizy/20261023T165902267076Z` contient n8n et `automation-state.tar.gz` pris pendant le même arrêt des trois services. L'archive privée comprend les états bridge/worker, les configurations `/etc/englizy`, les secrets de gestion et le cache d'authentification Codex du compte de service. Elle contient donc des secrets et doit rester en `0600`, dans un dossier `0700`. Les processus ont été redémarrés et la question en attente conservée avec la même session. Le 23 octobre, un démarrage de la copie n8n a réussi avec réseau `none`, aucun port ni volume de production, et workflows désactivés dans la copie. L'extraction de l'état d'automatisation a aussi confirmé l'intégrité SQLite, la question, la session exacte et les permissions du cache d'authentification. Aucun worker restauré n'a été lancé. Rapports : `restore-boot-check.json` et `automation-restore-check.json` dans cette sauvegarde. Le test n'a pas déchiffré ni utilisé les identifiants Telegram.

`backup-n8n.py` ne sauvegarde que n8n. Pour une sauvegarde complète, attendre qu'aucune génération ni publication ne soit engagée, arrêter l'entrée n8n, revérifier la file, puis arrêter les services bridge/worker et archiver leurs états avec n8n avant de redémarrer les trois services. Ne pas déduire une cohérence interservices de deux archives prises à des instants différents. Les futurs épisodes/audio/MP4 demanderont une sauvegarde supplémentaire ; aucun média n'a été créé par ces diagnostics. Le contrôle optionnel `python3 scripts/test-n8n-restore.py <sauvegarde> --check-pruning` teste aussi la purge native sur des exécutions vieillies uniquement dans une copie sans réseau ; il conserve une attente ancienne et un succès récent. Il accélère les délais seulement dans cette copie.

Pour revenir aux URL privées, sauvegarder d'abord l'état courant, comparer le Compose sauvegardé au Compose actuel, rétablir uniquement les variables d'URL concernées, puis `docker compose -f /root/services/n8n/compose.yaml up -d --no-deps --pull never n8n`. Désactiver le site nginx si nécessaire. Ne pas restaurer la vieille base sur les données actuelles : cela perdrait les identifiants et workflows créés depuis. Ne jamais utiliser `docker compose down -v`.

Une restauration réelle du volume exige un arrêt, une sauvegarde de l'état courant et une destination isolée. Aucun script de restauration destructive n'est fourni.

## Connexion API n8n réellement testée

La clé saisie localement par l'utilisateur est lue dans `/var/lib/englizy/secrets/n8n-api-key`. Le script ne l'imprime pas. Son expiration déclarée est le **21 décembre 2026 à 23 h UTC** : créer une clé de remplacement dans n8n puis relancer la saisie protégée avant cette date, et vérifier `n8n-status` avant de révoquer l'ancienne.

```sh
sudo python3 scripts/automation-secrets.py n8n-api-key
sudo python3 scripts/automation-admin.py n8n-status
sudo python3 scripts/automation-admin.py n8n-smoke
sudo python3 scripts/automation-admin.py credentials-status
```

Workflow créé : **Englizy — Test de connexion HTTPS (sans publication)**, ID `n9Ie7gSW3vIZXSrN`. Test API → activation → POST webhook HTTPS → réponse JSON attendu réussi. Workflow désactivé en fin de test ; webhook redevenu `404`. Export générique sans secret : [connection-test.json](workflows/connection-test.json).

Cette version enregistre et retire ses déclencheurs de manière asynchrone. Le script attend le résultat observable du webhook ; `active: true` seul n'est pas considéré comme une preuve d'exécution. Les routes `/publish` et `/unpublish` ont été vérifiées sur l'instance.

## Telegram : n8n est l'unique gestionnaire des échanges

Choix utilisateur : le jeton est saisi **uniquement dans les identifiants Telegram API de n8n**. Aucun jeton Telegram n'est demandé par le script de secrets, copié dans le stockage local de gestion, déchiffré par l'agent ou placé dans les exports. Le programme VPS ne gère aucun webhook Telegram et ne lance aucun poller `getUpdates` ; il ne fait pas de `sendMessage` direct. Les nœuds n8n font la réception et l'envoi. La gestion de l'association lit les résultats de leurs exécutions via l'API n8n.

À l'inspection initiale : aucun identifiant n8n, aucun workflow Telegram. L'utilisateur a depuis ajouté l'identifiant **Telegram account**, de type `telegramApi`, dont la présence et le test de connexion sont vérifiés par l'API n8n. Il a fourni **@muss_vps_n8n_bot** et confirmé que ce bot est réservé à cette instance. Le contrôle local refuse également tout autre workflow Telegram actif.

Parcours d'association et de test :

1. L'utilisateur crée/teste « Englizy — Telegram » dans n8n. L'agent ne lit que ses métadonnées via l'API.
2. L'opérateur lance l'association uniquement après confirmation que ce bot n'a aucun autre récepteur actif :

   ```sh
   sudo python3 scripts/automation-admin.py telegram-pair-start --credential-id=<ID_N8N> --bot-username=<NOM_PUBLIC> --bot-exclusive-confirmed
   ```

3. Le workflow [telegram-pairing.json](workflows/telegram-pairing.json) reçoit un code privé pendant 30 minutes. Il n'envoie aucun message. L'agent relève le candidat dans les exécutions n8n :

   ```sh
   sudo python3 scripts/automation-admin.py telegram-pair-check
   ```

4. Après confirmation explicite des deux IDs numériques par l'utilisateur, seulement :

   ```sh
   sudo python3 scripts/automation-admin.py telegram-pair-confirm --user-id=<ID> --chat-id=<ID>
   sudo python3 scripts/automation-admin.py telegram-install
   sudo python3 scripts/automation-admin.py telegram-enable-test
   ```

5. L'utilisateur envoie un message. Le workflow [telegram-connection-test.json](workflows/telegram-connection-test.json) utilise les filtres numériques utilisateur **et** conversation du Trigger 1.5, puis un nœud Telegram répond uniquement à la conversation confirmée. Les callbacks sont également filtrés par cette version. Vérifier l'exécution et la réception, puis désactiver le test avec `telegram-disable-test`. Le script attend qu'une requête sans secret soit refusée par le webhook (`403`) à l'activation, puis que le chemin redevienne inconnu (`404`) après désactivation, avant tout changement de récepteur.

État réellement vérifié : le workflow d'association **MkrDsOiJttrknu0M** a reçu le code privé, exécution n8n **4**, puis a été désactivé. Le webhook a refusé une requête sans secret (`403`) et est redevenu inconnu (`404`) après désactivation. L'utilisateur a explicitement confirmé son compte. Les IDs numériques et la preuve d'association restent dans `/var/lib/englizy/management`, hors Git.

Le test privé **riwxDWD1DzItHGAx** a réellement reçu un message et envoyé la réponse par le nœud Telegram : exécution **5** réussie, reçu Telegram conservé hors Git. Il est maintenant **désactivé**, comme l'association et le test HTTPS.

Le récepteur durable utilise le **Telegram Trigger 1.2**, livré dans l'image actuelle. Le contrôle `docker exec -i n8n-n8n-1 node < scripts/test-telegram-trigger.cjs` vérifie en simulation sur le nœud installé `drop_pending_updates=false`, la transmission des callbacks authentifiés et le refus d'un mauvais secret. Les filtres natifs anciens ne sont pas utilisés : un IF explicite contrôle utilisateur, conversation et type privé pour messages et callbacks, puis le bridge vérifie à nouveau l'identité. Le webhook réel refuse les requêtes sans secret (`403`), y compris après redémarrage. La réception d'un message réellement arrivé pendant une coupure n'a pas encore été testée.

| Workflow | ID | État |
| --- | --- | --- |
| Réception Telegram et tâches durables | `ypqdFC3lJ6UP2nj0` | Actif, seul récepteur de ce bot |
| Questions et résultats vers Telegram | `i3qVaC6RQOB6wuqT` | Actif, notifications via nœud Telegram |
| Lancer un diagnostic Codex sans vidéo | `dFCuaedtvxhzK6tg` | Désactivé après contrôle, webhook `404` |

Les exports dans `deploy/n8n/workflows` restent génériques : aucun secret ni identité personnelle. `scripts/build-automation-workflows.py` les reconstruit. `scripts/install-codex-workflows.py --activate` les installe en utilisant les références privées, sans lire le jeton Telegram ; il conserve les workflows déjà référencés plutôt que d'écraser leurs modifications. Il refuse un second récepteur actif. Le workflow de notifications consulte la boîte durable **toutes les 10 secondes** : ce déclencheur technique n'est ni un rappel quotidien, ni un lancement de vidéo, ni une publication. Aucun horaire quotidien n'est activé.

## Liaison Codex installée, limitée aux diagnostics

Python standard et SQLite assurent la liaison privée ; les composants vidéo ne changent pas. L'API écoute uniquement sur la passerelle Docker observée `172.18.0.1:8787`. Aucun accès public nginx ne lui est associé. Deux secrets distincts séparent les rôles n8n et worker : requête sans authentification refusée (`401`), création de diagnostic avec le rôle worker refusée (`403`), vérifiées réellement.

| Élément | Installation |
| --- | --- |
| Code exécuté | `/opt/englizy-automation/automation`, copie appartenant à root |
| API et base | Compte `englizy-bridge`, service homonyme, `/var/lib/englizy-bridge/jobs.sqlite` |
| Exécution Codex | Compte `englizy-worker`, service homonyme, états/journaux dans `/var/lib/englizy-worker/jobs` |
| Authentification Codex | Cache privé `/var/lib/englizy-worker/.codex`, initialisé une fois depuis le compte existant ; jamais écrasé par l'installateur |
| Configurations | `/etc/englizy/bridge.json` et `worker.json`, root/groupe du service, `0640` |
| Transport interne | Secrets root `0600` dans `/var/lib/englizy/secrets`, transmis par `LoadCredential` |
| Projet visible | Bind mount **en lecture seule** vers `/srv/englizy-repository`, uniquement dans les services |

Les deux services sont actifs et activés au démarrage. Ils ont `ProtectSystem=strict`, `ProtectHome=yes`, aucune capacité root et des répertoires privés `0700`. L'isolation a été vérifiée dans l'espace de montage du worker : utilisateur non root, dépôt lisible mais en lecture seule, secret de transport n8n et base du bridge inaccessibles. Le cache Codex conserve ses propres renouvellements. Le modèle et l'effort existants ont été repris sans changement. Une connexion réussie et une invocation Codex réelle ont été constatées sous ce compte.

- `automation/bridge.py` authentifie les routes, déduplique les événements et corrèle les réponses. Il n'appelle jamais Telegram directement.
- `automation/worker.py` persiste la réservation et le résultat avant chaque échange. Un résultat peut être retransmis sans relancer Codex. Une interruption pendant l'exécution devient un échec explicite, sans relance aveugle.
- `automation/runner.py` utilise des arguments séparés, le prompt par stdin, une sortie structurée et l'UUID réellement obtenu. La reprise vise cet UUID, jamais « la dernière session ». Les secrets de transport sont exclus de l'environnement Codex.
- `automation/store.py` conserve tâches, questions, événements, reçus et versions dans SQLite/WAL. Les futurs accords de publication sont liés à la révision, au hash vidéo, aux légendes, destinations et horaire ; ces garde-fous sont testés en simulation, pas encore exposés comme parcours de publication.
- L'API et le worker **refusent les tâches vidéo** dans cette tranche. Le lanceur de production est préparé mais n'a pas encore produit ni validé de MP4. Il faudra ouvrir seulement les chemins de données/sorties nécessaires, conserver les modèles en lecture seule et vérifier une première production.

### Diagnostic réel et reprise

La tâche `3c098f98f159` a été créée par le workflow HTTPS authentifié. Le worker a réellement lancé Codex, puis la question « Quel est le code de reprise de ce test ? » a été envoyée par le nœud Telegram. Les reçus d'attente et de question sont persistés. Après arrêt/redémarrage de n8n et des deux services, la tâche est toujours `needs_input`, avec la même question et la même session Codex. Cette ancienne tâche reste conservée en attente. Un second test complet, tâche `d7d42f15ce32`, a depuis réussi avec la réponse `AUDIT-OK`, après redémarrages avant et après réponse ; résultat Telegram reçu sous l'identifiant message 15. Voir l'audit complémentaire. Aucun média n'a été généré. Les preuves privées se trouvent dans `/var/lib/englizy/management/codex-diagnostic-current.json`, `codex-restart-check.json` et `worker-isolation-check.json`.

Commandes Telegram disponibles : `/diagnostic`, `/statut <tâche>`, `/question <tâche>` et `/repondre <tâche> <question> <réponse>`. Une réponse au message de question conserve sa corrélation ; du texte simple n'est accepté comme réponse que si une seule question est en attente. Plusieurs questions demandent une corrélation explicite. Les autres utilisateurs/conversations sont refusés. Aucun choix de format vidéo ni bouton de publication n'est encore actif.

Les notifications sont réservées avant envoi et acquittées avec le reçu n8n/Telegram. Si n8n s'arrête entre ces étapes, une entrée peut rester `delivering` : examiner l'exécution et son reçu avant toute nouvelle tentative. Il n'y a pas de renvoi aveugle ni de promesse d'envoi « exactement une fois ». `/question <tâche>` permet à l'utilisateur de demander à nouveau une question persistante. Les tâches/réponses restent conservées même si une notification échoue.

### Exploitation et mises à jour

```sh
sudo systemctl status englizy-bridge englizy-worker
sudo journalctl -u englizy-bridge -u englizy-worker --since today
sudo python3 scripts/automation-admin.py n8n-status
```

Les logs système ne contiennent ni en-têtes d'authentification ni corps Telegram ; les événements Codex restent dans le dossier privé du worker. Une authentification expirée doit être réparée localement pour ce compte, sans coller son cache dans la conversation. L'expiration de la clé de gestion n8n reste à surveiller indépendamment.

Pour mettre à jour le code des services : examiner les tâches, suspendre les workflows de lancement/réception, attendre une frontière sûre (aucune tâche en cours ni en file), puis arrêter les deux services. L'installateur refuse les services encore actifs. Sauvegarder les états avant migration, puis :

```sh
sudo python3 scripts/install-automation-services.py --start
```

L'installation copie les modules et unités, conserve les secrets et le cache existants et remet les services en route. Vérifier santé, états et webhooks avant de réactiver l'entrée. Les workflows existants ne sont pas mis à jour automatiquement : examiner leur export et leurs modifications avant application. Pour un retour arrière, conserver le code et les unités précédents et vérifier la compatibilité du schéma SQLite ; ne jamais restaurer une ancienne base par-dessus les nouvelles réponses ou validations.

## Audit complémentaire

Voir [DIAGNOSTIC-AUDIT.md](DIAGNOSTIC-AUDIT.md) pour les contrôles de rétention, de déduplication et de redémarrage. Les succès de scrutation ne sont désormais plus conservés dans n8n ; les erreurs et reçus durables restent disponibles.

## Contrôles et suite

`npm ci`, installation des requirements dans `.venv`, `npm run browser`, `npm run check`, `npm test`, `npm run verify` exécutés avec succès sur le VPS. Les contrôles existants des 14 options passent avec Node 24 ; le projet recommande Node 22 et la CI utilise toujours Node 22.

39 scénarios d'automatisation **simulés** passent, intégrés à `npm test` : événements dédupliqués, rollback, génération unique, question conservée/reprise exacte, mauvais propriétaire/conversation/session, accord persistant vérifié depuis un nouveau processus Python, empreintes modifiées, double clic concurrent, ancienne version, annulation, interruption, publication inconnue et succès partiels, erreur explicite, option invalide, JSON hors contrat, fichiers absents/hors périmètre, données shell jamais passées en arguments de commande. Les tests de gestion Telegram vérifient aussi la lecture du candidat dans n8n, l'absence d'appel direct au bot et de copie de son jeton, ainsi que le refus d'un autre récepteur actif. Le helper Git refuse les autres hôtes et dépôts ; le lanceur CLI transmet son jeton seulement par environnement et interdit son affichage.

Les tests supplémentaires du bridge vérifient les rôles HTTP, l'identité des messages/callbacks, les retries sans doublon, la corrélation de session, les réponses ambiguës, les reçus et l'absence de relance après interruption. Pas de changement visuel : aucun nouveau rendu ni écoute vidéo n'est présenté comme effectué. Il reste à tester réellement : compte Telegram non autorisé réellement connecté (refus synthétique vérifié), panne de voix/rendu, MP4 volumineux et session expirée.

Buffer n'est pas connecté. Aucun adaptateur réseau de publication, URL média publique, destinataire social ni horaire n'est configuré. Continuer après production et prévisualisation vérifiées ; conserver les garde-fous du [contrat de publication](../publishing-contract.md). Un accord précis de publication réelle et un accord d'activation quotidienne restent nécessaires.

Livraison Git : suivre `CONTRIBUTING.md`, conserver les protections. L'utilisateur a enregistré son PAT fine-grained limité au dépôt personnel dans `/var/lib/englizy/secrets/github-pat` en `0600`. `python3 scripts/github-local.py configure-git` a configuré uniquement le helper de ce dépôt ; `python3 scripts/github-local.py gh <arguments>` fournit `GH_TOKEN` au seul processus GitHub CLI, sans OAuth ni copie dans la configuration gh. L'accès API au dépôt personnel et `git fetch origin` sont vérifiés. L'API indique que `main` est protégée et attend le contrôle `quality` ; la lecture détaillée des protections renvoie `403` avec ce PAT, sans empêcher la livraison par PR ni nécessiter de droits supplémentaires. Le push normal de `feat/n8n-integration-stage-1` et la création de la [PR #14](https://github.com/mustafaHami/remotion-english-video/pull/14) ont réussi : les droits effectifs pour ces opérations sont vérifiés. Aucune fusion, aucun appel d'organisation ni modification des protections n'a été effectué.

Références consultées : [proxy et URL n8n](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/), [API n8n](https://docs.n8n.io/api/authentication/), [Bot API Telegram](https://core.telegram.org/bots/api), [Codex non interactif](https://learn.chatgpt.com/docs/non-interactive-mode), [nginx WebSockets](https://nginx.org/en/docs/http/websocket.html), [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html).
