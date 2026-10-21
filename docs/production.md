# Production de vidéos

## Règles validées le 21 octobre 2026

Tous les formats sont validés comme concepts ; les adaptations communes sont intégrées aux options stables. Les anciennes restrictions « uniquement l’option 1 », « sans mascotte », « voix Zira » et « toujours en test » ne pilotent plus la production. Les historiques sont conservés pour traçabilité.

Utiliser le renard de face (`FrontalFoxMascot refinedMotion`) et `MascotBookend`. Le corps ne flotte pas et ne saute pas ; la main salue puis s’arrête, le pouce effectue son geste et revient. La fin reste verte sans flash lavande. Le renard n’est pas superposé aux exercices.

Le contenu doit être clair, utile et adapté à un niveau accessible. Une vidéo traite un thème ; les formats à phrases peuvent contenir trois exemples. Dix paires pour l’option 3, dix verbes pour l’option 1, huit répliques pour l’option 9. Les exemples servent de fixtures, pas de contenu inédit à republier.

## Création à la demande

Utiliser le skill `create-english-video` pour recueillir l’option et le brief manquants. Une demande directe n’exige pas une cellule Excel renseignée, mais l’historique et le planning doivent être consultés pour éviter les doublons. Les étapes ci-dessous restent celles du traitement quotidien planifié.

`npm run video:new -- --option=N` crée un brouillon distinct et réserve `output/options/option-N/<date_heure>/creation.json` (Europe/Paris, suffixe en cas de collision). Après adaptation du contenu et de la narration, `npm run video:new -- --render="<creation.json>"` prépare l’audio, rend et vérifie. Les états draft, preparing, rendering, rendered, verified ou failed décrivent uniquement la fabrication. Les dates UTC du rendu et du contrôle complètent la date locale de création. La revue visuelle et l’écoute effectivement effectuées doivent être annoncées séparément. Aucun historique de publication n’est modifié par ce script.

Un dossier contenant déjà un MP4 est conservé : créer une nouvelle demande pour une révision. Après une erreur avant production du MP4, corriger l’épisode puis relancer la même demande ; un verrou indique un traitement encore actif ou à examiner après un incident.

## Déroulement quotidien

1. Lire la date explicite Europe/Paris et le brief de la cellule de l’option dans l’Excel. Une cellule vide n’autorise pas à inventer un planning.
2. Choisir une option et proposer un contenu distinct de l’historique. Copier la fixture dans `content/episodes/<date>-option-N.json`.
3. Modifier les champs documentés, la narration associée et les timings si une phrase est plus longue. Ne jamais raccourcir une voix en coupant sa fin.
4. Régénérer les WAV. Pour l’option 1, générer les tracés Nunito pour les nouvelles formes.
5. Contrôler les données : `npm run verify`. Pour un épisode : `node scripts/render.cjs --content=... --output=output/videos/<id>` puis `python scripts/verify-video.py --folder=...`.
6. Inspecter les images et les transitions. Écouter/visionner quand ces moyens sont disponibles et annoncer précisément les vérifications réellement faites.
7. Publier uniquement via la configuration effective du VPS. Enregistrer le reçu, les URL, la date réelle et les contenus. Synchroniser ensuite le journal et le calendrier Excel sans écraser des briefs existants.

## Timings par famille

- Options 4, 5, 6, 8 et 11 : présentation 1,5 s, recherche 4 s, réponse 3 s. Option 12 : premier modèle immédiat, puis deux essais avec recherche. Option 4 : 33 s au total.
- Option 3 : recherche initiale de 4 s, puis dix révélations espacées de 3 s ; 42,5 s au total.
- Option 1 : dix verbes et deux colonnes à écrire avec prononciations ; sa durée est plus longue pour rester lisible.
- Option 2 : formes principales puis trois usages ; une famille be/have/can/could par vidéo.
- Option 9 : huit répliques, alternance Sonia/Ryan. Ne pas accélérer par la règle des quiz.
- Option 10 : écoute, fenêtre silencieuse de répétition de 5,33 s, puis réécoute.
- Options 7 et 14 : association ou démonstration visuelle en trois cartes ; pas de minuteur de réflexion artificiel quand la scène enseigne directement.
- Option 13 : mémo cumulatif de trois groupes, avec exemple prononcé pour chacun.

## Voix

WAV mono 24 kHz, rate -5 %, volume Remotion 0,85. Denise parle français, Sonia l’anglais, Ryan le second interlocuteur. `edge-tts` est le fournisseur actuel ; il nécessite le réseau pour de nouveaux clips et n’offre ici aucun engagement de disponibilité. Les rendus utilisent les fichiers locaux. Une indisponibilité doit arrêter la préparation, pas supprimer la narration.

## Publication fiable

`node scripts/daily.cjs --date=YYYY-MM-DD` lit le planning sans produire ou publier. Ajouter `--content=... --dry-run` pour valider un épisode inédit. Sans `--dry-run`, le traitement rend et inspecte. `--publish` exige l’adaptateur configuré sur le VPS et un reçu confirmé.

Conserver `.runtime` sur un volume persistant. Une publication dont le résultat est incertain nécessite une vérification sur la plateforme ; aucune nouvelle tentative automatique. Ne pas supprimer un verrou après un incident avant d’avoir vérifié le processus et son état.
