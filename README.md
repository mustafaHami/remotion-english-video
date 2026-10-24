# Remotion English Video

Projet durable de vidéos pédagogiques d’anglais pour TikTok et Instagram : **14 options de vidéo**, un système graphique commun, des contenus quotidiens séparés du code et un historique des publications.

Les modèles ont été validés par l’utilisateur le 21 octobre 2026. Les règles finales prévalent sur les anciens briefs de test. Les options 3 et 4 ont été publiées le **20 octobre 2026**, selon confirmation utilisateur ; leurs contenus sont enregistrés. Les liens et plateformes de ces publications ne sont pas encore renseignés.

## Démarrer

Node.js 22, Python 3.11+ et FFmpeg sont nécessaires. Utiliser de préférence un environnement Python virtuel (`python -m venv .venv`, puis activer cet environnement avant les commandes). Depuis la racine :

```sh
npm ci
python -m pip install -r requirements.txt
npm run browser
npm run check
npm test
npm run dev
```

Remotion Studio affiche `Option1` à `Option14`. Il n’y a pas de nouveau projet à créer pour chaque vidéo.

## Créer une vidéo avec l’agent

Lancer `$create-english-video` dans Codex (ou `/create-english-video` dans Claude Code). Tu choisis uniquement l’option parmi les 14 formats. Le skill consulte toutes les entrées de sa colonne dans l’Excel, le Journal, l’historique JSON et les épisodes existants, puis choisit un sujet et des exercices différents. Il annonce son choix et poursuit la création sans te demander de fournir le contenu. Les réglages visuels et les voix validés sont conservés par défaut. Il prépare ensuite le contenu, les voix, le rendu et les contrôles.

Chaque réalisation possède son dossier, par exemple `output/options/option-4/2026-10-21_14-35-07/option-4.mp4`. `creation.json` indique l’heure de création en Europe/Paris, les dates UTC de fin de rendu et de contrôle ainsi que l’état réel du traitement. Les précédentes vidéos sont conservées ; un rendu n’est pas une publication.

Pour l’agent ou une utilisation manuelle :

```sh
npm run video:new -- --option=4
# Adapter le fichier content/episodes/... renvoyé au brief ; il contient encore le modèle.
npm run video:new -- --render="output/options/option-4/<date_heure>/creation.json"
```

La seconde commande prépare les WAV, les tracés éventuels, le MP4 et le rapport technique. Elle utilise `.venv` si disponible, sinon `python` ; `PYTHON` permet de choisir un autre interpréteur. Le skill effectue ensuite la revue des captures et décrit précisément les vérifications réalisées. La publication reste une étape distincte.

## Produire une vidéo

```sh
npm run render -- --option=4
python scripts/verify-video.py --option=4
```

Sortie : `output/options/option-4/option-4.mp4`, captures, contenu utilisé et rapport de contrôle. Les rendus ne sont pas versionnés. Pour régénérer tous les exemples : `npm run render:all`, puis `npm run inspect:all`.

Pour un nouvel épisode, copier le `content.json` de l’option dans `content/episodes/`, changer les données et les textes des répliques sans modifier les composants :

```sh
python scripts/prepare-audio.py --content content/episodes/mon-episode.json
node scripts/render.cjs --content=content/episodes/mon-episode.json --output=output/videos/mon-episode
python scripts/verify-video.py --folder=output/videos/mon-episode
```

Pour l’option 1, préparer aussi les nouveaux tracés avant le rendu : `python scripts/build-writing-paths.py --content content/episodes/mon-episode.json`.

## Où travailler

| Dossier | Rôle |
|---|---|
| `src/options/option-1` … `option-14` | Données de référence et fiche de chaque format |
| `src/options/ProductionLesson.tsx` | Assemblage des séquences et des voix |
| `src/templates`, `src/components`, `src/design` | Vues, renard et règles visuelles communes |
| `content/episodes` | Contenus distincts des vidéos à produire |
| `planning/calendrier-publications.xlsx` | Planning humain : Date + 14 options, puis journal |
| `planning/publications.json` | Historique structuré utilisé pour éviter les doublons |
| `src/archive/experiments` | Anciens essais ; aucune règle active à déduire d’une ancienne version |
| `output/options`, `output/videos` | Exemples et épisodes rendus, exclus de Git |

## Règles actuelles

Renard adulte **de face**, écharpe sauge et yeux ambrés : `public/mascots/fox-front/poses.png`. Corps fixe ; salut localisé à la main et geste de pouce animé. Accueil parlé court, conclusion verte avec félicitations et au revoir. Aucun saut ou flottement du corps.

Baloo 2 et Nunito locales, lavande/citron/menthe, cartes et boutons centrés, contours et ombres nettes. Animation calculée par frame, 1080 × 1920 à 30 i/s. Voix française Denise ; anglais Sonia ; dialogue alternant Sonia/Ryan. Les WAV sont figés et embarqués : un rendu ordinaire ne régénère pas la voix.

Les quiz gardent quatre secondes de recherche et trois secondes de réponse, sans couper la prononciation. Le dialogue garde son débit de conversation ; l’écoute/répétition conserve sa fenêtre silencieuse ; le tableau des dix opposés révèle une paire toutes les trois secondes. Le modèle précis de chaque option fait foi.

## Pour les agents et GitHub

Lire [AGENTS.md](AGENTS.md), puis la fiche de l’option. Claude Code charge également [CLAUDE.md](CLAUDE.md). Les skills de production et de livraison sont dans `.agents/skills`, avec entrées Claude synchronisées dans `.claude/skills`.

- [Méthode de production](docs/production.md)
- [Schéma des contenus](docs/content-schema.md)
- [Planning et historique](planning/README.md)
- [Contribution, commit et push](CONTRIBUTING.md)
- [Validation et migration](docs/migration.md)
- [TODO à réaliser sur le VPS](deploy/TODO-VPS.md)

Sur le VPS, la chaîne Telegram → n8n → Codex ou Claude (choisi par `/modele` avant chaque `/video`, voir [MODELS.md](deploy/n8n/MODELS.md)) → prévisualisation privée → brouillons Buffer → publication est installée ; chaque publication exige un accord explicite lié à une version précise (`/publier`). Aucun horaire de création ou de publication automatique n’est activé. Voir [deploy/n8n/OPERATIONS.md](deploy/n8n/OPERATIONS.md) et [PUBLICATION.md](deploy/n8n/PUBLICATION.md). Aucun secret n’est inclus dans ce dépôt.
