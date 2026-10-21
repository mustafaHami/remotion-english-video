# Renard frontal — exemple 2D articulé dans Blender

19 octobre 2026. L’utilisateur fournit une nouvelle planche frontale avec deux poses et choisit explicitement **« Dessin 2D articulé dans Blender »**. Cette livraison conserve cette illustration comme texture ; il ne s’agit pas d’un modèle 3D en volume.

## Ouvrir et regarder

- Fichier autonome : `D:/ai-generation-video/blender/renard-frontal-2d-articule.blend`.
- Aperçu animé : `D:/ai-generation-video/output/blender/renard-frontal-2d/renard-frontal-2d-exemple.mp4`.
- Rendu de la pose de référence : `D:/ai-generation-video/output/blender/renard-frontal-2d/renard-frontal-reference.png`.
- Séquence transparente : `output/blender/renard-frontal-2d/frames/image-0001.png` à `image-0180.png`.
- Source originale conservée : `assets/branding/renard-frontal-reference-2026-10-19.png`, copie sans modification de la pièce jointe.

Le fichier s’ouvre de face sur la planche complète, avec les deux poses et le regard direct. L’image 1 correspond à la pose de référence. Lancer la chronologie pour lire l’exemple de **6 secondes, 180 images à 30 i/s**. Le salut a lieu dans la première moitié ; le renard au pouce levé réagit dans la seconde. Respiration, queue, inclinaison de tête et clignements restent mesurés.

## Structure modifiable

Les collections `01 · Salut` et `02 · Pouce levé` contiennent chacune un maillage 2D continu et un squelette de **22 os**. Les mouvements déforment réellement le maillage, avec des poids autour des articulations ; ce ne sont pas seulement deux images déplacées dans le cadre. Les UV conservent le dessin fourni. Chaque pose possède sa propre action : `2D · Salut et clignement` et `2D · Approbation et clignement`.

Contrôles : placement global, corps, tête, oreilles, yeux, bras et avant-bras levés, main levée, bras bas, queue en deux parties, foulard et jambes. Les mouvements de l’exemple portent principalement sur le haut du corps et la queue ; les pieds restent stables. Les paupières sont des éléments 2D supplémentaires, visibles uniquement pendant les clignements. Au repos, le dessin d’origine reste visible.

Pour modifier une pose, sélectionner son objet `RIG`, passer en mode Pose et activer les superpositions de la vue pour voir les os. Les deux personnages sont indépendants. Les actions contiennent les images clés modifiables. La caméra principale est `CAM · Les deux poses · référence exacte`. Les caméras `CAM · Salut seul` et `CAM · Pouce levé seul` sont aussi disponibles ; régler alors la sortie sur **887 × 887** pour conserver leur cadrage carré.

La texture est incorporée au `.blend`. Le dessin reste utilisable si le fichier est déplacé sans le dossier temporaire d’origine. Les PNG sont en **1774 × 887 RGBA**, au même format que la planche fournie. Le MP4 est un aperçu sur fond ivoire ; la scène et les PNG gardent leur transparence.

Le MP4 mesure 1774 × 888 : une ligne de fond est ajoutée pour l’encodage H.264, sans modifier le format des PNG ni de la scène Blender.

## Contrôles et portée

Le fichier `.blend` a été rouvert dans Blender pour contrôler les deux armatures, les actions, les poids et la texture incorporée. Les 180 PNG sont contrôlés en taille et en transparence ; le MP4 est rechargé dans Blender pour vérifier le format et la durée, puis une image en est décodée. Les rapports sont dans `verification-source.json`, `verification-images.json` et `verification-video.json`.

L’illustration source n’est pas redessinée. Les opérations de filtrage et de transparence du rendu Blender peuvent produire de petits écarts sur les contours par rapport aux pixels du PNG original ; le rapport compare les images sur fond clair. Cette livraison est un exemple frontal avec deux poses indépendantes et des gestes légers, pas une bibliothèque de marche ou un personnage permettant un changement de vue en volume. Les fichiers Remotion et la bibliothèque 3D précédente ne sont pas modifiés.
