# Prompt à transmettre à l’expert Remotion

Tu es chargé de réaliser **un exemple Remotion de l’option 1 avec notre renard animé en 3D**, dans le projet existant `D:/ai-generation-video`. Le travail Blender est préparé par un autre agent ; ton rôle est le montage, le placement, les trajectoires et la synchronisation avec la leçon. Réalise directement le test et examine son rendu.

## Périmètre demandé

- Travaille uniquement sur l’option 1 : présent, passé et futur. Le dossier existant correspondant à « output test option V1 » est **`D:/ai-generation-video/output/options/option-1`**.
- Conserve les versions précédentes. Crée une composition distincte, par exemple `TestOption1Renard3D`, et rends `D:/ai-generation-video/output/options/option-1/test-option-1-renard-3d-v1.mp4`.
- Pars de la version actuelle de l’option 1, en examinant `src/archive/experiments/options-v5/Composition.tsx`, son `render-config.json`, `voice-manifest.json`, le corps de leçon dans `src/archive/experiments/options-v3`, et les exports existants de ce dossier. `TestOption1V5` est une base à comparer ; ne pars pas automatiquement de l’ancien quiz restaurant.
- Garde le design, les tableaux, les textes, les voix et les temps pédagogiques de cette option. Intègre la mascotte dans des espaces disponibles. Adapte son intervention au contenu, sans masquer les phrases ni les colonnes. Ne modifie pas les autres options et ne publie rien.
- La demande actuelle autorise le renard 3D dans ce test de l’option 1. Les anciennes exclusions de mascotte présentes dans l’historique ne s’appliquent pas à cette demande.

## Fichiers à lire et à voir

1. `D:/ai-generation-video/docs/renard-bibliotheque-mouvements-v2.md` : utilisation, raccords et limites.
2. `D:/ai-generation-video/output/blender/mouvements-v2/manifest.json` : source de vérité pour les noms, durées, chemins, ancrages et boucles.
3. `D:/ai-generation-video/output/blender/mouvements-v2/renard-bibliotheque-mouvements-v2.mp4` et `planche-mouvements.jpg` : aperçu des mouvements réellement exportés.
4. `D:/ai-generation-video/blender/renard-bibliotheque-v2.blend` : source modifiable, 21 actions corporelles et accessoires séparés. Le fichier n’est pas un média lisible directement dans Remotion ; utilise les PNG exportés pour ce test.
5. `D:/ai-generation-video/assets/branding/renard-reference-validee.png` : seule référence esthétique approuvée. Le modèle 3D et le test d’intégration restent à évaluer ; ne les présente pas comme validés par l’utilisateur.

## Médias d’intégration

- Les animations du personnage se trouvent dans `D:/ai-generation-video/output/blender/mouvements-v2/frames/<id>/image-0001.png`, etc.
- Ce sont des PNG RGBA, **768 × 768, à 30 images/seconde**, avec la même caméra et la même échelle pour tous les clips. Le format carré est le canevas de l’élément à superposer ; la vidéo finale reste **1080 × 1920 à 30 i/s**.
- Les MP4 sont des aperçus avec fond ivoire : utilise les PNG pour conserver la transparence.
- Copie les dossiers nécessaires dans un nouveau sous-dossier de `public`, par exemple `public/mascotte/renard-mouvements-v2`, pour qu’ils soient servis par Remotion. Préserve les noms et adapte le préfixe des chemins du manifeste.
- Utilise un affichage d’image piloté par la frame Remotion, avec le composant `Img`. Pour une frame locale indexée à partir de 0, le numéro de fichier vaut `localFrame + 1`, complété sur quatre chiffres. Une boucle utilise le modulo de `frames`. Les gestes non bouclables ne doivent pas être répétés mécaniquement.
- Tu peux optimiser ensuite en vidéo avec transparence, après avoir validé le rendu PNG. Une conversion en MP4 H.264 ordinaire supprimerait la transparence.

## Placement et raccords : à respecter

- Crée une couche réutilisable qui reçoit l’action, la frame de début, la position du point d’appui, l’échelle et le sens. Blender anime le corps ; Remotion contrôle la place du personnage dans la composition.
- Utilise **l’ancrage du manifeste**, environ `(390, 659)` dans le canevas 768 × 768. Pour une échelle `k`, le coin de la couche est `(piedX - anchorX*k, piedY - anchorY*k)`. Le manifeste indique aussi la hauteur debout réellement occupée.
- Garde la même échelle pour les clips successifs. Ne recadre pas chaque image sur sa boîte visible : cela ferait sauter le personnage et ses accessoires. Une taille debout de 13 à 18 % de la hauteur vidéo est un point de départ, à ajuster à la lisibilité de l’option 1.
- La direction native est vers la droite. Six clips de locomotion disposent d’un `mirrorPattern` et d’un `mirrorAnchorPx` pour aller à gauche. Les autres gestes peuvent être retournés avec la couche complète. **Retourne aussi l’accessoire et l’ancrage**, jamais le personnage seul.
- Les champs `entry` et `exit` précisent les postures compatibles. Pour un parcours complet : `attente-quatre-pattes` → `demarrer-marche` → `marche` (boucles) → `arreter-marche` → `se-lever` → geste debout. Pour repartir : fin du geste → `se-baisser` → `demarrer-marche` → `marche` jusqu’à la sortie.
- Les gestes debout reviennent à la pose neutre. `retrait` et `reapparaitre` constituent une anticipation et un retour corporels ; l’opacité et le changement de position sont à réaliser dans Remotion.
- La marche est **sur place** : n’ajoute pas une trajectoire déjà rendue dans Blender. Le manifeste fournit `screenTravelPerCyclePixelsAtNativeScale` pour une boucle de 36 images et 1,08 unité Blender de déplacement virtuel. Multiplie ce vecteur par l’échelle d’affichage pour accorder le déplacement aux pas. Inverse sa composante horizontale pour le sens miroir. Les phases de démarrage et d’arrêt nécessitent une vitesse progressive et un contrôle visuel des appuis.
- Conserve un déplacement court et plausible. Ne compense pas un trajet trop long en faisant glisser rapidement le renard. Les grands changements de place peuvent passer par une sortie, une disparition ou une réapparition pendant une transition de la leçon.

## Accessoires et gestes disponibles

- `attente`, `attente-quatre-pattes` : boucles calmes ; `marche` : boucle de déplacement.
- `demarrer-marche`, `arreter-marche`, `se-lever`, `se-baisser` : raccords de locomotion.
- `presenter-gauche`, `presenter-droite`, `presenter-haut` : gestes vers le contenu.
- `reflechir`, `decouvrir`, `examiner-loupe`, `bravo`, `encourager`, `ecouter`, `a-toi`, `saluer`, `retrait`, `reapparaitre`, `regarder-haut` : interventions pédagogiques.
- `decouvrir` utilise les images indépendantes `accessoires/ampoule/image-XXXX.png`. `examiner-loupe` utilise `accessoires/loupe/image-XXXX.png`. Affiche chaque accessoire à **la même frame locale, même position, même échelle et même orientation que le canevas du personnage**. Les apparitions sont déjà animées dans leur alpha ; ne remplace pas l’ampoule ou la loupe par une nouvelle illustration.

## Exemple attendu sur l’option 1

Fais une version mesurée qui montre réellement la 3D : une courte entrée marchée avec arrêt et redressement, une présentation vers le tableau, une attente calme pendant la lecture, puis une réaction pertinente à la découverte et une conclusion encourageante avec salut. Ajuste ce scénario aux espaces et aux timings existants ; il ne faut pas utiliser les 21 actions dans une seule leçon. Une sortie puis une réapparition à un autre emplacement peut démontrer la mobilité sans traverser le texte.

Si le parcours ne tient pas dans l’introduction existante, ajuste la durée de cette introduction et recale la narration associée, en préservant les temps de lecture et de réflexion du corps de la leçon. Indique la nouvelle durée livrée. Préfère un trajet court correctement animé à une traversée accélérée de tout l’écran.

Privilégie les déplacements aux transitions. Pendant l’écoute, la lecture et la répétition, utilise les réactions discrètes. La mascotte reste un guide secondaire. Elle ne parle pas avec une synchronisation labiale : aucune animation labiale n’est livrée.

## Vérification et livraison

Rends un nouvel exemple complet dans le dossier de l’option 1, ainsi que quelques captures des entrées, raccords et gestes. Vérifie le rendu exporté : transparence sans rectangle, cadrage des oreilles et de la queue, absence de saut de taille, sens du geste, synchronisation des accessoires, pieds qui ne glissent pas excessivement et textes dégagés. Contrôle le son et les pauses pédagogiques.

Lis les limites consignées dans la documentation Blender. Les poids et volumes de la posture quadrupède restent ceux d’un personnage anthropomorphe stylisé ; si un défaut apparaît à la taille finale, indique l’action et la frame concernées pour une correction Blender. Ne masque pas un défaut en remplaçant le renard par une image fixe.

Livre la vidéo, des captures et une courte note sur les choix de placement. Aucun nouvel achat, nouvelle voix ni publication n’est demandé.
