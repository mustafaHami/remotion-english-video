# Suivi, récapitulatif et rétention

Règles explicitement choisies par l'utilisateur : un partage désigne une publication terminée **sur les réseaux**, jamais l'envoi privé Telegram. Récapitulatif quotidien à **09:00 Europe/Paris**. Vidéos partagées : suppression après 10 jours ; détails des tâches closes : après 15 jours. Les tâches ouvertes sont conservées jusqu'à demande explicite.

## États et commandes

| État | Signification | Fermée ? |
| --- | --- | --- |
| `queued`, `generating` | En file ou création en cours | Non |
| `needs_input` | Une question attend une réponse | Non |
| `awaiting_preview` | MP4 prêt, envoi non confirmé | Non |
| `pending_validation` | Envoi Telegram confirmé, avis attendu | Non |
| `validated` | Cette version est validée, reste à publier | Non |
| `shared` | Publication terminée sur les réseaux, confirmée | Oui |
| `failed` | Incident à examiner ; `/annuler ID` supprime tout | Non |
| `needs_fallback` | Quota épuisé pendant le travail, relance avec l'autre agent à confirmer | Non |
| `cancelling` | Annulation demandée, nettoyage par le worker | Non |
| `cleanup_failed` | Nettoyage en erreur, `/annuler ID` réessaie | Non |
| `cancelled` | Annulée et nettoyée (ligne minimale), retirée d'Excel et de `production.json` | Oui |

`/encours` liste les identifiants, options, états et actions attendues. `/valider IDENTIFIANT VERSION` valide seulement une version réellement envoyée, avec son empreinte ; ce n'est pas un accord de publication. Après publication manuelle terminée, `/partage IDENTIFIANT VERSION CONFIRME plateformes ou liens` enregistre la déclaration explicite de l'utilisateur confirmé, les plateformes reconnues et les liens fournis, sans effectuer de requête de publication. Il faut confirmer la fin sur toutes les destinations prévues ; une publication partielle reste ouverte. Les plateformes/liens inconnus restent absents, sans invention.

Une commande `/partage` incomplète affiche désormais sa syntaxe et précise qu’elle ne publie pas les brouillons Buffer. Aucun état ne change. L’aide générale mentionne aussi cette commande.

Les brouillons Buffer sont documentés dans [BUFFER.md](BUFFER.md) ; `/publier IDENTIFIANT VERSION CONFIRME` autorise la publication d’une proposition préparée, voir [PUBLICATION.md](PUBLICATION.md). Les états `publishing`, `partially_published` et `publication_unknown` restent ouverts. Seules les confirmations sur toutes les destinations permettent `shared`.

Un menu `/video` et un ancien bouton de sélection refusent une nouvelle création tant qu'une vidéo reste ouverte. Le suivi des lignes humaines du Journal est aussi consulté via `production.json`. Les questions de diagnostic n'interdisent pas à elles seules une vidéo. Une nouvelle tâche est toujours déclenchée par un choix explicite, jamais par le récapitulatif.

## Excel et persistance

La base demeure la source des tâches du bot ; Excel est une projection lisible avec une ligne par vidéo. `production.json` fournit le même suivi sans secrets. Les anciennes publications ne sont pas réécrites ; leurs libellés « Publié » sont interprétés comme `shared`. Les nouveaux blocs `[Suivi IDENTIFIANT]` du Calendrier préservent les briefs autour d'eux. Les lignes externes du Journal restent inchangées.

Le service `englizy-tracking.service`, déclenché environ chaque minute par son timer, exécute le script fixe `scripts/planning/maintain-tracking.py`. Il ne lance pas Codex. Il est isolé sans réseau, avec dépôt en lecture seule et droits de modification limités au planning, aux sorties, aux états et copies privées nécessaires. Les identifiants d'API et le cache Codex lui sont inaccessibles. Les opérations SQLite passent sous l'UID propriétaire pour ne pas créer de WAL appartenant à root. Un verrou empêche deux maintenances concurrentes.

Le classeur est sauvegardé avant modification dans `/var/lib/englizy-tracking/workbooks`, puis écrit par remplacement atomique après contrôle. Les cellules libres, publications historiques et formules sont préservées ; un conflit dans une ligne gérée ou une modification concurrente fait échouer la synchronisation sans écrasement. Les textes sont écrits comme données, jamais comme formules. Les exécutions sans changement ne réécrivent pas le classeur.

Installation après sauvegarde et première synchronisation contrôlée :

```sh
sudo python3 scripts/install-tracking.py --daily-summary-time 09:00 --start
sudo python3 scripts/install-codex-workflows.py --update --activate
```

Le récapitulatif utilise un second Schedule Trigger dans le workflow de notifications existant, expression `0 9 * * *`, timezone Europe/Paris. Il appelle `/daily-summary`, qui persiste une notification unique par date avant l'envoi par le nœud Telegram. La scrutation toutes les 10 secondes continue de transporter questions et résultats. Il reste un seul workflow récepteur du bot ; les quatre workflows de test restent désactivés.

## Rétention réellement activée

À partir de `shared_at + 10 jours`, le MP4 original de la version partagée et ses copies Telegram et Buffer sont supprimés après vérification des chemins et empreintes. Une modification inattendue bloque la suppression. À partir de `closed_at + 15 jours`, les résultats détaillés, questions/réponses, anciennes révisions, détails d'audit, journaux de travail Codex et fichiers de transcription de la session sont purgés. Une notification au résultat incertain bloque la purge de son contexte. La purge de la transcription vérifie que l'UUID n'est référencé par aucune autre tâche non purgée ; elle refuse les liens symboliques et chemins inattendus. Les compteurs d'usage restent séparés afin que `/statut` puisse encore les afficher après purge.

Le worker mesure les `turn.completed.usage` disponibles : les tours d'une invocation sont additionnés, l'invocation est identifiée par son lease pour éviter un doublon lors d'un renvoi, puis les invocations distinctes sont additionnées pour la tâche. Les tokens mis en cache sont affichés à titre informatif et sont déjà inclus dans les tokens d'entrée ; le total est entrée + sortie. Ce sont des compteurs d'usage, pas une facture. Les anciennes tâches sans relevé restent « non mesurées » ; aucune valeur n'est reconstruite.

Une fiche minimale, la preuve de validation/partage et les identifiants/reçus nécessaires à la déduplication restent conservés ; la fiche de contenu dans Excel/JSON évite les doublons pédagogiques. Aucun ancien événement ne devient une nouvelle tâche après purge. Les tâches ouvertes, y compris les vidéos validées non publiées et les incidents, ne sont jamais supprimées automatiquement. Pour une suppression sur demande, identifier précisément la tâche et contrôler qu'aucun worker ne travaille dessus ; aucune commande Telegram de suppression générale n'est exposée.

Ces délais concernent les données actives, pas les sauvegardes privées existantes, les bases internes générales du cache Codex, les WAV partagés, les épisodes versionnés ou les captures de contrôle. Ces fichiers ne sont pas effacés automatiquement. Les sauvegardes de base prises avant purge restent privées ; leur rotation constitue une politique distincte.

## Preuves et limites

- Journal : vidéo `ecee3555f0c8`, option 1, révision 2, **validated**, date de création 24/10/2026 Paris. `closed_at` et `shared_at` restent vides, aucun accord de publication. Anciennes lignes et briefs préservés après relecture du XLSX. Le registre des publications confirmées contient toujours seulement les deux anciennes vidéos.
- Le blocage d'une nouvelle création a été vérifié sur l'état réel sans créer de tâche. Récapitulatif de contrôle envoyé par n8n, reçu Telegram **26**.
- Timer Excel actif ; plusieurs cycles observés, dont des cycles sans réécriture. Aucune donnée réelle éligible à la purge : zéro fichier et zéro tâche supprimés.
- 70 tests Python simulés couvrent notamment la version validée, le propriétaire, la déclaration de partage, le refus de création supplémentaire, le suivi Excel externe, la conservation des briefs, les conflits, l'idempotence, les seuils exacts de 10/15 jours et le refus de suppression d'un MP4 modifié. Le récapitulatif est testé avant/après 09h en été et en hiver, avec déduplication après réouverture de la base.
- Le premier déclenchement **horaire réel à 09h Paris le 24 octobre** est constaté : reçu Telegram **27**, clé durable `daily-summary:2026-10-24:0`. Buffer a ensuite reçu trois brouillons ; aucune publication sociale n'a été effectuée.

Sauvegarde avant migration : `/var/backups/englizy/tracking-before-20261023T231142Z/state-before.tar.gz`. Sauvegardes après vérification : `/var/backups/englizy/tracking-verified-20261023T232037Z` (base contrôlée et fichiers de suivi) et `/var/backups/englizy/20261023T232037232674Z` (n8n, extraction et intégrité vérifiées). Preuve privée : `/var/lib/englizy/management/tracking-check.json`.

Mise à jour après publication autorisée : le 24 octobre, la vidéo `ecee3555f0c8` est passée à `shared` seulement après trois confirmations Buffer. Excel et le registre ont été relus ; voir [PUBLICATION.md](PUBLICATION.md). Les preuves `validated` ci-dessus décrivent l’étape précédente, avant cet accord.
