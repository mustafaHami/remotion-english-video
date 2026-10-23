# Planning et publications

`calendrier-publications.xlsx` possède deux feuilles :

- **Calendrier** : exactement Date + Option 1 à Option 14. Une cellule contient un brief ou le contenu publié, et peut désigner un fichier JSON d’épisode. Les cellules futures vides ne constituent pas des demandes de publication.
- **Journal** : une ligne par vidéo, avec date, option, contenu complet, statut, identifiant et liens.

Le Journal suit aussi les vidéos non publiées : `pending_validation` après l'envoi privé, `validated` après validation de cette version, `shared` après publication terminée sur les réseaux. `shared` signifie tâche close ; une vidéo validée reste ouverte. Les anciennes lignes « Publié » restent préservées et sont normalisées en `shared` dans `production.json`.

`production.json` est la projection lisible des tâches et des lignes externes du Journal. Elle ne contient aucun identifiant de compte ni secret. La tâche `ecee3555f0c8` (option 1, création le 24/10/2026 en heure de Paris) y figure comme `validated`, avec contenu et validation humaine. Le registre `publications.json` conserve seulement ses deux publications déjà confirmées ; cette nouvelle vidéo n'y est pas déclarée publiée.

Le 20/10/2026, les options 3 et 4 ont été publiées selon déclaration de l’utilisateur. Les contenus exacts figurent dans le classeur et `publications.json`. Plateformes et liens n’ont pas été fournis : ils restent vides.

## Source des données

L’Excel est l’entrée humaine du planning. `python scripts/planning/import-calendar.py` lit le classeur ; `--write` synchronise explicitement `calendar.json`. `publications.json` est le registre structuré des publications confirmées et des réservations du pipeline. Ne pas remplacer ce registre à partir d’une cellule libre du planning.

Le service `englizy-tracking` synchronise le Journal, les blocs de suivi du Calendrier et `production.json` environ chaque minute. Après une publication confirmée, il ajoute également la fiche au registre `publications.json` avec le statut historique compatible `published`. Il conserve les briefs existants et sauvegarde le classeur avant modification. Une ligne gérée par le service et modifiée manuellement provoque un arrêt explicite pour réconciliation, plutôt qu'un écrasement. Modifier les états via les commandes Telegram ; les nouvelles lignes humaines du Journal restent lisibles dans le suivi.

Le constructeur historique `scripts/planning/build-workbook.mjs` refuse désormais une reconstruction lorsqu'un suivi de production existe. Utiliser `scripts/planning/maintain-tracking.py --config /etc/englizy/tracking.json` sur le VPS. Ce script n'exécute aucune publication. Les règles et preuves opérationnelles figurent dans [TRACKING.md](../deploy/n8n/TRACKING.md).

## Variété

Comparer les phrases complètes et les paires de mots à l’historique de toutes les options. Une paire inversée est la même paire. Réutiliser un verbe courant dans un autre contexte est possible ; republier la même phrase ne l’est pas sans brief explicite de révision et adaptation documentée du contrôle.

Un contenu rendu ou téléversé n’est pas automatiquement publié. Seule une confirmation explicite de l’utilisateur ou un reçu de plateforme autorise le statut publié. En cas d’incertitude, vérifier avant toute nouvelle tentative.
