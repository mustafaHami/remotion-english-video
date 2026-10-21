# Vérifications de la migration — 21 octobre 2026

- TypeScript : réussi.
- 12 tests de production : réussis (contenus/voix, doublons entre formats, paires inversées, états de publication incertains, fenêtres de quiz et empreintes stables).
- 14 options et variantes have/can/could : données et ressources audio valides.
- 14 MP4 effectivement rendus puis entièrement décodés : 17,700 frames, 590 secondes, 118 passages vocaux.
- Zéro erreur de mise en page sur les frames mesurées ; erreur maximale de centrage inférieure à 0,054 pixel (tracés de l’option 1).
- H.264/AAC, 1080 × 1920, 30 fps, BT.709. Voix présentes, pas de chevauchement ou saturation, fenêtres silencieuses contrôlées.
- Planches des 14 options inspectées visuellement ; accroche trop longue de l’option 9 raccourcie à l’écran puis vidéo rendue et contrôlée à nouveau.
- Épisode supplémentaire avec trois nouvelles phrases en option 4 : préparé sans modifier le composant, rendu et contrôlé en 33 s. Il n’a pas été publié.
- Excel : deux feuilles rendues et inspectées, 15 colonnes de calendrier, dates typées, exactement deux publications déclarées du 20/10/2026. Lecture avec openpyxl dans un environnement Python isolé réussie.
- Traitement quotidien d’une journée sans brief : retourne no_plan, aucune publication.

## Durées des modèles

| Option | Secondes | Passages vocaux |
|---|---:|---:|
| 1 | 73.5 | 22 |
| 2 | 50.5 | 12 |
| 3 | 42.5 | 12 |
| 4 | 33 | 5 |
| 5 | 34 | 5 |
| 6 | 34 | 5 |
| 7 | 34 | 8 |
| 8 | 34 | 5 |
| 9 | 51.5 | 10 |
| 10 | 50.5 | 8 |
| 11 | 34 | 5 |
| 12 | 34 | 5 |
| 13 | 50.5 | 8 |
| 14 | 34 | 8 |

## Limites explicitement conservées

Ces vérifications locales ont été faites sous Windows. La CI prépare un contrôle depuis Ubuntu ; le Dockerfile et l’installation finale du VPS restent à exécuter sur le serveur selon la demande utilisateur. Pas d’écoute humaine ni de lecture animée subjective annoncée. Les API sociales, comptes, ordonnanceur et synchronisation Excel du VPS restent dans deploy/TODO-VPS.md. Les deux publications historiques sont déclarées par l’utilisateur, leurs plateformes et URL restent inconnues.
