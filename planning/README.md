# Planning et publications

`calendrier-publications.xlsx` possède deux feuilles :

- **Calendrier** : exactement Date + Option 1 à Option 14. Une cellule contient un brief ou le contenu publié, et peut désigner un fichier JSON d’épisode. Les cellules futures vides ne constituent pas des demandes de publication.
- **Journal** : une ligne par vidéo, avec date, option, contenu complet, statut, identifiant et liens.

Le 20/10/2026, les options 3 et 4 ont été publiées selon déclaration de l’utilisateur. Les contenus exacts figurent dans le classeur et `publications.json`. Plateformes et liens n’ont pas été fournis : ils restent vides.

## Source des données

L’Excel est l’entrée humaine du planning. `python scripts/planning/import-calendar.py` lit le classeur ; `--write` synchronise explicitement `calendar.json`. `publications.json` est le registre structuré des publications confirmées et des réservations du pipeline. Ne pas remplacer ce registre à partir d’une cellule libre du planning.

Après un reçu confirmé, l’agent reporte les mêmes informations dans le Journal et la cellule concernée. Préserver les autres cellules. Le constructeur `scripts/planning/build-workbook.mjs` sert à recréer le classeur depuis les deux JSON après synchronisation ; il nécessite le SDK de la compétence Spreadsheets (`ARTIFACT_TOOL_MODULE` si le runtime le fournit). Ne pas le relancer sur un Excel modifié sans importer d’abord le planning et préserver le journal. L’installation de ce mécanisme de synchronisation sur le VPS reste un TODO.

## Variété

Comparer les phrases complètes et les paires de mots à l’historique de toutes les options. Une paire inversée est la même paire. Réutiliser un verbe courant dans un autre contexte est possible ; republier la même phrase ne l’est pas sans brief explicite de révision et adaptation documentée du contrôle.

Un contenu rendu ou téléversé n’est pas automatiquement publié. Seule une confirmation explicite de l’utilisateur ou un reçu de plateforme autorise le statut publié. En cas d’incertitude, vérifier avant toute nouvelle tentative.
