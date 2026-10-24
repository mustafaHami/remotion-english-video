# Choix du modèle : Codex ou Claude

Choix de l'utilisateur du 24 octobre 2026 : chaque vidéo est fabriquée par **Codex ou Claude, au choix explicite**, avant chaque `/video`. Il n'y a pas de modèle par défaut. Les deux agents suivent le même skill `create-english-video`, la même mission, le même contrat JSON (`automation/result.schema.json`) et les mêmes contrôles indépendants du runner (MP4, épisode, légendes `social`, prévisualisation). Seul l'agent change.

| Agent | Modèle et effort | Authentification |
| --- | --- | --- |
| Codex | réglages de la configuration privée du worker (non imposés par le dépôt) | cache `/var/lib/englizy-worker/.codex` |
| Claude | `claude-opus-5-5`, effort `medium` (`automation/engines.py`) | jeton `claude setup-token` dans `/var/lib/englizy/secrets/claude-oauth-token`, transmis par `LoadCredential` |

## Parcours Telegram

1. `/modele` : le bridge demande au worker une lecture fraîche des quotas, puis envoie le menu `1. Codex` / `2. Claude` avec le pourcentage restant de chaque fenêtre (5 h, semaine). Réponse par bouton ou par `1` / `2`.
   - Codex : `codex app-server`, méthode `account/rateLimits/read`, sans tour de modèle ni consommation.
   - Claude : appel Haiku minimal sans outil ni session, seul l'événement `rate_limit_event` est lu (coût négligeable, mais il compte dans le quota Claude).
   - Si le worker ne répond pas en 60 s, le menu part avec « quota inconnu » et le choix reste possible.
2. Un modèle épuisé ou non configuré est refusé par un message ; le menu reste ouvert pour l'autre.
3. `/video` sans modèle choisi répond « Vous avez oublié de choisir le modèle ». Le menu des formats affiche le modèle. Le choix de l'option crée la tâche avec son agent et **consomme** le choix : la vidéo suivante exige un nouveau `/modele`.
4. Avant tout travail, le worker relit le quota de l'agent. S'il est épuisé, rien n'est commencé : la tâche est annulée avec un message, sans question.
5. Si l'agent tombe à court de quota **pendant** le travail (événement d'épuisement ou quota relu à 100 % après un échec), la tâche passe en `needs_fallback` et Telegram demande : « Relancer avec l'autre agent ? Oui / Non ». La question reste ouverte et bloque les nouvelles vidéos jusqu'à la réponse.
   - **Oui** (bouton, `oui`, ou `/relancer ID oui`) : l'autre agent démarre une nouvelle session avec la liste des fichiers déjà produits (`handoff`) et reprend là où le premier s'est arrêté. La mémoire de conversation ne passe pas d'un agent à l'autre ; l'état réel des fichiers fait foi.
   - **Non** (bouton, `non`, ou `/relancer ID non`) : annulation et nettoyage complet.
   - Si l'autre agent est lui aussi épuisé ou non configuré, la tâche est annulée directement.
6. `/annuler ID` annule une tâche `queued`, `needs_input`, `needs_fallback`, `failed`, `awaiting_preview` ou `pending_validation`. Refusé pendant `generating` et après validation : Buffer et la publication gardent leur parcours.

## Empreinte et nettoyage

Une seule tâche génère à la fois. Avant chaque exécution, le worker inventorie `content/episodes`, `output/options` et `public/audio/production` (y compris les clés de `provenance.json`). Après l'exécution, réussie ou non, la différence forme l'**empreinte** de la tâche, conservée dans `job_files`. Seules les formes attendues sont acceptées (épisode `.json`, dossier de réalisation, WAV/MP3 à nom haché, clé de provenance).

Une annulation passe la tâche en `cancelling` ; les messages non encore envoyés pour elle sont retirés de la file. Le worker, seul propriétaire des fichiers, supprime alors :

- les entrées de l'empreinte appartenant au compte `englizy-worker`, sans lien symbolique ni chemin hors dépôt ;
- les voix créées par la tâche, **sauf** celles utilisées par un autre épisode ou une fiche d'option, et leurs clés de `provenance.json` ;
- le dossier de prévisualisation `/var/lib/englizy-media/<tâche>`, les journaux `/var/lib/englizy-worker/jobs/runs/<tâche>` et les transcriptions Codex et Claude des sessions de la tâche.

Puis le bridge purge la base : questions, versions, prévisualisation, empreinte, compteurs d'usage et audit sont effacés ; les messages déjà envoyés deviennent des pierres tombales. Il reste une ligne minimale (`cancelled`, motif, dates) et un seul événement d'audit `cancelled-cleaned` avec des compteurs, sans contenu, pour la déduplication Telegram et la traçabilité. Le service de suivi retire ensuite la ligne du Journal, le bloc `[Suivi]` du Calendrier et la fiche de `production.json`, après avoir vérifié que la ligne Excel n'a pas été modifiée à la main.

Le nettoyage est repris à l'identique après un redémarrage (état durable `cleaning`). En cas d'erreur, la tâche passe en `cleanup_failed`, rien n'est relancé automatiquement, et `/annuler ID` réessaie.

## Sécurité de Claude

Claude s'exécute sous `englizy-worker`, dans l'isolement systemd existant, et en plus dans une prison **bubblewrap** : système en lecture seule, écriture limitée aux quatre dossiers de fabrication et à sa configuration `/var/lib/englizy-worker/.claude`, `/tmp` privé ; état du worker, cache Codex, copies Telegram, configuration `/etc/englizy`, secrets, identifiants systemd et sauvegardes masqués. Mode `dontAsk` (aucune invite), outils de fabrication autorisés, `WebFetch` et `WebSearch` refusés ; les règles de `/etc/claude-code/managed-settings.json` s'appliquent aussi. Comme pour Codex, l'agent peut lire son propre jeton dans son environnement ; aucun autre secret ne lui est transmis.

## Installation sur le VPS

À une frontière sans tâche en cours, après sauvegarde :

```sh
claude setup-token                                      # par l'utilisateur, dans son terminal
sudo python3 scripts/automation-secrets.py claude-oauth-token   # saisie masquée du jeton
sudo systemctl stop englizy-worker englizy-bridge
sudo python3 scripts/install-automation-services.py --start
sudo python3 scripts/install-tracking.py --daily-summary-time 09:00 --start
```

L'installateur copie l'exécutable Claude figé dans `/usr/local/lib/englizy-claude/claude`, crée la configuration privée du worker et n'ajoute le drop-in `30-claude.conf` que si le jeton existe. Sans jeton, Claude apparaît « non configuré » dans `/modele` et Codex reste utilisable. Aucun workflow n8n n'est modifié : les nouveaux boutons passent par le récepteur et les notifications existants.

## Tests

`tests/test_models.py` simule : lecture des quotas, menu, refus d'un modèle épuisé, oubli de `/modele`, délai de lecture, épuisement avant le début, relance Oui avec reprise, Non avec nettoyage et purge, deux agents épuisés, règles d'annulation, échec puis reprise du nettoyage, entrées invalides refusées, cycle complet du worker avec redémarrage pendant le nettoyage, et retrait d'Excel. La prison bubblewrap a été vérifiée réellement sous le compte worker (écriture autorisée et refusée, secret masqué). Ces tests n'appellent aucun agent réel.
