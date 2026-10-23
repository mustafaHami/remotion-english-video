# Intégration n8n — relevé VPS du 23 octobre 2026

Ce relevé décrit une première tranche. La chaîne Telegram → production → prévisualisation → Buffer n'est pas encore opérationnelle. Aucun rappel quotidien ni publication sociale n'est activé.

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

À la dernière inspection avant association : **aucun identifiant n8n**, aucun workflow Telegram. Cela ne prouve pas qu'un même bot n'est pas utilisé ailleurs. Demander son nom public et la confirmation de son usage exclusif avant d'activer son webhook ; ne pas écraser le récepteur d'un autre outil. Le contrôle local refuse également tout autre workflow Telegram actif.

Parcours préparé, pas encore validé avec le compte utilisateur :

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

Les workflows Telegram ne sont pas encore importés et leurs IDs ne sont donc pas inventés. Leurs références réelles seront enregistrées sous `/var/lib/englizy/management`, hors Git. Les exports ont des filtres à `0` qui refusent tous les comptes tant que l'installateur ne les a pas renseignés.

**Limite relevée dans le code installé :** le Telegram Trigger 1.5 active `drop_pending_updates` lors de son enregistrement. Ces workflows conviennent à l'association et au test ponctuel, mais ne constituent pas encore le récepteur durable de production. Avant cette étape, choisir et tester un webhook n8n préservant les updates en attente, le secret Telegram et le filtrage des callbacks. Un seul récepteur reste actif pour un bot ; aucun deuxième poller VPS n'est prévu.

## Lanceur Codex et état durable : préparés, pas installés comme services

L'implémentation préparée utilise Python standard (SQLite compris), déjà nécessaire au projet, plutôt que d'ajouter un runtime TypeScript. Les composants Remotion et leurs fixtures ne changent pas.

- `automation/store.py` : transactions SQLite/WAL, événements Telegram dédupliqués, file à une seule génération, questions liées à une session et une révision, versions et accords conservés, boîte de notifications durable, résultats séparés par destination.
- `automation/runner.py` : arguments séparés, prompt par stdin, sortie JSON validée selon `result.schema.json`, session relevée dans `thread.started`, reprise par UUID exact. Jamais `--last`, jamais de shell interpolant un message.
- `automation/validate-episode.cjs` : cohérence épisode/leçon/empreinte et historique. Le lanceur recoupe chemins, manifeste, rapport, option et MP4, puis refait le contrôle technique avant de considérer une production terminée. Cette branche de production reste à tester sur un véritable rendu.
- `needs_input` termine le tour Codex. Le stockage conserve la question avant sa notification et reprend uniquement sa session après réponse corrélée.
- Un accord lie hash vidéo, légendes, destinations, horaire et révision. Une correction invalide l'accord courant et conserve la version approuvée dans la table `revisions`. Double clic concurrent : un seul accord accepté.
- Après interruption, aucune génération n'est relancée automatiquement. Une publication engagée devient `publication_unknown` après examen opérateur ; les succès par destination sont conservés.

Test réel effectué avec le Codex déjà authentifié du compte interactif, en lecture seule : tâche `000000000001`, question structurée, puis reprise de la session `01a168f3-7278-75b2-aa8f-ccaf2902b955` avec un code de test, résultat `completed`. Aucun média produit. Journaux protégés : `/var/lib/englizy/probes`. Ce test ne prouve pas encore l'aller-retour Telegram ↔ question Codex.

La production refuse de tourner en root. Il reste à définir un compte de service, ses droits limités aux données/sorties, son authentification Codex et l'API interne authentifiée accessible depuis le réseau Docker. Aucun workflow n'a accès à une commande root, au socket Docker ou à un lanceur de production actuellement actif. La liaison n8n → worker et le relais de questions restent à installer/tester ; le seul module SQLite ne constitue pas un service opérationnel.

## Contrôles et suite

`npm ci`, installation des requirements dans `.venv`, `npm run browser`, `npm run check`, `npm test`, `npm run verify` exécutés avec succès sur le VPS. Les contrôles existants des 14 options passent avec Node 24 ; le projet recommande Node 22 et la CI utilise toujours Node 22.

24 scénarios d'automatisation **simulés** passent, intégrés à `npm test` : événements dédupliqués, rollback, génération unique, question conservée/reprise exacte, mauvais propriétaire/conversation/session, accord persistant vérifié depuis un nouveau processus Python, empreintes modifiées, double clic concurrent, ancienne version, annulation, interruption, publication inconnue et succès partiels, erreur explicite, option invalide, JSON hors contrat, fichiers absents/hors périmètre, données shell jamais passées en arguments de commande. Les tests de gestion Telegram vérifient aussi la lecture du candidat dans n8n, l'absence d'appel direct au bot et de copie de son jeton, ainsi que le refus d'un autre récepteur actif. Le helper Git refuse les autres hôtes et dépôts ; le lanceur CLI transmet son jeton seulement par environnement et interdit son affichage.

Pas de changement visuel : aucun nouveau rendu ni écoute vidéo n'est présenté comme effectué. Il reste à tester réellement : utilisateur Telegram non autorisé, échanges après redémarrage des services, panne de voix/rendu, MP4 volumineux, session expirée et restauration d'une sauvegarde contenant les futurs identifiants/services.

Buffer n'est pas connecté. Aucun adaptateur réseau de publication, URL média publique, destinataire social ni horaire n'est configuré. Continuer après production et prévisualisation vérifiées ; conserver les garde-fous du [contrat de publication](../publishing-contract.md). Un accord précis de publication réelle et un accord d'activation quotidienne restent nécessaires.

Livraison Git : suivre `CONTRIBUTING.md`, conserver les protections. L'utilisateur a enregistré son PAT fine-grained limité au dépôt personnel dans `/var/lib/englizy/secrets/github-pat` en `0600`. `python3 scripts/github-local.py configure-git` a configuré uniquement le helper de ce dépôt ; `python3 scripts/github-local.py gh <arguments>` fournit `GH_TOKEN` au seul processus GitHub CLI, sans OAuth ni copie dans la configuration gh. L'accès API au dépôt personnel et `git fetch origin` sont vérifiés. L'API indique que `main` est protégée et attend le contrôle `quality` ; la lecture détaillée des protections renvoie `403` avec ce PAT, sans empêcher la livraison par PR ni nécessiter de droits supplémentaires. Les droits effectifs d'écriture sont à confirmer par le push de livraison et la création de PR. Aucun appel d'organisation ni modification des protections n'a été effectué.

Références consultées : [proxy et URL n8n](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/), [API n8n](https://docs.n8n.io/api/authentication/), [Bot API Telegram](https://core.telegram.org/bots/api), [Codex non interactif](https://learn.chatgpt.com/docs/non-interactive-mode), [nginx WebSockets](https://nginx.org/en/docs/http/websocket.html), [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html).
