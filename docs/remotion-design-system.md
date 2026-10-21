> Historique des essais. Les règles actives validées le 21/10/2026 sont dans `AGENTS.md`, `README.md` et `docs/production.md`. Les mentions anciennes « sans mascotte » ou « uniquement en test » ci-dessous ne pilotent plus la production.

# Système visuel — prototype test style v1

Mise à jour V3 : le dernier retour utilisateur demande au moins 35–40 secondes avec davantage d’exemples. Cette durée est un objectif éditorial demandé, pas une règle générale de TikTok ou Instagram. Les nouvelles vues conservent les cartes centrées et montrent jusqu’à trois exemples successifs, plutôt que trois exercices simultanément à l’écran. La conversation comprend huit répliques, par paires sur quatre cartes. Un mémo peut construire progressivement trois lignes ; c’est un format explicatif sans quiz.

L’option 2 accélère le tableau (48 images entre les formes, au lieu de 60), retire les longues attentes finales et passe à trois phrases d’usage. Quatre compositions séparées partagent ce modèle : be, have, can et could. Am / is / are et have / has gardent des couleurs cohérentes par forme. Pour can/could, la forme commune est montrée sans inventer d’infinitif ou de terminaison en s. Les longues phrases de la déclinaison could sont adaptées localement à 26u pour conserver des marges intérieures.

Les réponses des quiz arrivent après cinq secondes de recherche. La prononciation démarre après leur révélation. Les groupes de mots et verbes à particule sont prononcés, puis réutilisés dans une phrase ; le tableau présent/passé/futur fait entendre chaque paire présent/passé, puis les futurs. Durées réelles des clips mesurées, placements par frames et sans chevauchement. Le format écoute/répétition garde une vraie plage silencieuse. La synthèse vocale n’est appelée qu’en préparation : les rendus ordinaires lisent les fichiers WAV locaux.

Le décor secondaire en étoile est retiré des titres V3 pour laisser davantage de place aux formulations longues. Le cercle discret, les aplats, les polices et les rebords sont conservés. Les versions précédentes restent accessibles pour comparer le style et le rythme.

Statut actuel : base graphique de l’option 1 retenue pour décliner les autres vues ; chaque nouveau format reste à examiner. Aucune publication. Les notes v1 ci-dessous conservent l’historique. Références lues intégralement : prompt-agent-remotion.md, palette-design-video-tiktok.md, PROJET.md et code existant. Aucune consigne AGENTS.md trouvée à la racine, dans les parents ou dans les sources.

## Règles retenues

- Une scène logique de 360 × 640, agrandie une seule fois ×3. Export 1080 × 1920, 30 i/s, 480 frames.
- Tokens partagés : couleurs exactes, Baloo 2 800 et Nunito 600/700/800, dimensions, rayons, bordures et rebords durs. Polices variables officielles stockées dans public/fonts avec licences OFL ; chargement bloquant par FontFace et delayRender, accents inclus.
- Lavande pour accroche/question/réflexion/réponse, citron pour astuce, menthe pour fin. Feuille crème, textes encre, traductions et sous-titres violets, corail uniquement sur pointillés et arc.
- Bonne réponse verte sur fond vert pâle avec coche. SVG de coche, commentaire, cloche et étincelle issus de la charte. Aucun dégradé, emoji, flou ou rotation de texte.
- Animations déterministes par frame ; courbes reveal/drop en Bézier, spring Remotion réel pour les swipes. Une même carte se réorganise à 60 ; cartes entières glissées à 300 et 420.

## Adaptations explicites sans mascotte

- Aucun personnage, asset, SVG, pose ou bulle de mascotte importé dans cette expérience. Ancien RestaurantQuiz conservé dans un groupe Historique.
- Accroche conservée ; « Tu as 3 secondes. » remplace le chapeau. Feuille initiale à y=330 plutôt que 470, duo make/ou/do dans la feuille, repris du contenu de couverture. Aucun nouveau décor de remplissage.
- Question : feuille à y=190, phrase à y=212, traduction à y=316 sur deux lignes, options à y=398. Le titre contextuel « Make ou do ? » occupe le haut, minuteur à (246,108), indice/feedback à y=470. Le contexte pédagogique remplace l'espace du personnage.
- Astuce : titre contextuel dans l'en-tête, feuille y=230, colonnes y=254. Sous-titre long « + créer, fabriquer » sur deux lignes ; même hauteur réservée dans les deux colonnes. Note explicite : repère simplifié, pas règle universelle.
- La note de nuance est à y=194 dans l'en-tête, après correction d'un chevauchement avec la dernière pastille. Le contenu des cartes est masqué aux limites sûres pendant les swipes ; les fonds et feuilles continuent leur déplacement entier.
- Fin : chapeau « Abonne-toi pour le prochain piège. » sur deux lignes. Feuille à y=300 et carte à y=340 pour rapprocher le prochain sujet. Entrées de fin avancées pendant le swipe afin de laisser plus d'une seconde de lecture à la carte ; cloche à 456 conservée.
- Limite prudente sous y=290 : x≤300. Largeur du contenu 280 au lieu de 284 ; options légèrement rentrées à x=24, largeur272 pour protéger aussi leur rebond. Indice sur deux lignes. Pas de réduction générale des polices.
- Silencieux pour ce premier essai. Pas de couverture ni photo de profil livrée ; pas d'épisode réel ni suivi Excel.

## Points à vérifier dans les rendus

Polices réellement chargées et accents, retours à la ligne, coche pendant le changement d'état, 3/2/1 et arc 156–240, rebonds contenus, absence de coutures/flashs lors des swipes, lecture des pastilles et de la fin, conformité des fonds et absence de personnages. Zones TikTok vérifiées selon le document fourni ; les interfaces actuelles Reels/Shorts ne sont pas réputées identiques.

## Extension de test v2 — « Le déclic »

À la demande de l'utilisateur : davantage de design, textes sur une ligne, réflexion sur l'apprentissage et TikTok/Instagram. La v1 reste conservée. Sa réception est positive, sans validation explicite pour lancer un épisode réel.

Nouveaux composants partagés dans DeclicComponents.tsx, styles centralisés dans design/editorial.ts, modèle DeclicLesson.tsx, données dans experiments/test-style-v2. Palette et polices conservées ; exception assumée aux formes de la v1 : fiche crème 280u, rayon28, bordure encre2u, relief encre6u, onglets et progression en trois étapes. La grande feuille est remplacée par cette fiche à titre d'exploration autorisée par le retour utilisateur. Phrase à 23u (69px export), titres à 30–34u sur une ligne, traductions à14u ; aucune compression horizontale.

Le format expérimental passe de16 à22 secondes pour ajouter un nouvel essai. Deux compositions utilisent le même modèle : TestStyleV2-TikTok et TestStyleV2-Instagram. Accroche et mémo final distincts ; même zone conservatrice entre64 et508u, x≤300 sous290u. Les aperçus des zones sont schématiques et ne prétendent pas reproduire des interfaces actuelles. Une première fiche trop large coupait visuellement son contour au masque de sécurité ; largeur corrigée avant les exports finaux.

Recherche, limites et sources : recherche-attention-apprentissage-v2.md. Les choix de rythme et de plateforme sont des hypothèses de production à évaluer, pas des préférences universelles démontrées. Le nom « Le déclic » est une proposition de concept.

## Test option 1 — fiche de conjugaison

L'utilisateur demande de valider l'option 1 et le style avant de produire les autres vidéos. Une seule fiche, trois verbes, trois temps. Suppression des tags, du nom de concept et de la progression en étapes ; un seul titre « Présent, passé, futur. » et une consigne courte sous la fiche.

Fiche crème à (16,190), largeur 328u, hauteur 280u, rayon 30u, bordure encre 1,5u et relief dur de 5u. Le fond et le bord de la fiche utilisent la largeur ; les mots s'arrêtent avant x=300u sous y=290u pour l'interface mobile. Colonnes en x=32,119,206 ; mots en Nunito 800 à 17u, titre Baloo 2 à 30u, onglets à 13u. Onglets lavande/citron/menthe, corail uniquement pour la barre de réflexion. Le fond devient menthe à la fin.

Deux pauses de cinq secondes remplacent le compte à rebours de trois secondes. Les réponses sont écrites dans l'ordre, avec une courte pause entre elles. Le stylo vectoriel suit les contours de la police réelle, révélés par masque SVG ; aucune police manuscrite substituée, aucun effet de saisie caractère par caractère. Les réponses précédentes restent stables. Le surlignage local indique uniquement la cellule active. Pas de mascotte ni de main photographique dans ce premier essai.

Les dimensions sont centralisées dans design/worksheet.ts, les tracés et le stylo dans components/WrittenText.tsx, le modèle dans templates/TenseWorksheet.tsx et les données dans experiments/test-option-1. Les tracés précalculés depuis Nunito sont fournis dans les sources ; le rendu habituel ne dépend pas de FontTools. L'outil FontTools 4.67.0 est installé dans le cache local pour leur régénération facultative, sans nouvelle installation Remotion.

### Révision v2 : dix verbes et centrage

L'utilisateur apprécie le design et demande explicitement dix verbes minimum, une fiche plus grande et un centrage précis. Le tableau passe à dix lignes et trente formes. Fiche (12,134), 336 × 342u, rayon28, bordure2, rebord dur5 ; titre centré à y=82. Grille de312u entre x=24 et336, trois colonnes de104u centrées en76,180,284 ; dix lignes de27u. Onglets identiques de96 ×30u centrés sur ces axes. Consigne en (12,488), 336 ×26u, axe180 identique à la fiche. La barre de réflexion utilise aussi le centre180. La bordure entière de2u évite un arrondi de mise en page qui avait décalé la barre interne d'un demi-u.

Les formes sont en Nunito800 à16,5u. Leur contour réel fournit le centre horizontal, afin que les mots de longueurs différentes soient centrés optiquement. Le stylo est réduit à62% pour rester discret dans une grille plus dense. Contenu dans rows.json et paramètres d'export dans render-config.json, sans duplication des listes entre génération des tracés et rendu.

Le retrait droit de300u est levé pour ce prototype à la demande de centrage de l'utilisateur. Le texte reste avant336u et entre64 et516u, mais cette version ne revendique pas de protection contre les boutons TikTok à partir de300u. L'aperçu mobile est schématique et présente cette limite avant toute diffusion. Les autres compositions gardent leurs paramètres de zones sûres précédents.

Les formes terminées sont isolées en images SVG autonomes ; seul le mot écrit utilise un masque animé. Cette séparation corrige la disparition temporaire des formes précédentes observée lors du premier contrôle v2. Le contenu reste vectoriel, avec les mêmes contours Nunito.
# Déclinaison des autres vues — base option 1 retenue

Après le retour utilisateur autorisant la suite, les options 2–14 reprennent la fiche de 336 × 342u centrée à x=180u, le titre centré, le guide de 336u et les polices locales. Primitives partagées : OptionScene, Text, Tile, Arrow, Pause, Translation, Receipt et SoundIcon. Sept pronoms pour le schéma to be, dix paires pour le tableau d’opposés ; pas d’obligation artificielle de dix éléments dans les formats à une phrase. Les autres formats conservent un exercice, et l’option 12 seule teste le transfert facultatif.

La disposition varie avec l’intention : colonnes reliées pour les pronoms, paire surlignée pour les opposés, deux choix pour les quiz, retrait du mot en trop, deux bulles sans personnage, groupes qui se rejoignent, fiche récapitulative avec objets vectoriels et bus avec flèche de sortie. Les graphismes sont des objets SVG locaux, sans image générée ni mascotte. Aplats et rebords durs ; le vert de correction est accompagné d’une coche.

Les révélations sont pilotées par les frames. Pauses de cinq à sept secondes pour les exercices ; les explications n’ajoutent pas un quiz pour remplir leur durée. Les formats durent de 20 à 37 secondes selon la lecture. Le passage final à la menthe préserve la fiche au lieu de rajouter une carte promotionnelle. L’option 1 de 53 secondes reste inchangée. Comme pour cette base, les nouvelles vues sont centrées dans le cadre entier ; les interfaces mobiles devront être vérifiées dans une étape de diffusion, non demandée ici.

L’option 10 synchronise les deux lectures d’un même fichier audio local (3s et 14s), l’onde issue des échantillons décodés et les indications Écoute / À toi / Réécoute. La voix est provisoire et synthétique ; aucun choix définitif de narration n’est déduit de cet essai.

