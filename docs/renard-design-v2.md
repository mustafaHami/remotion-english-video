# Renard — historique design v2

**État actuel — 18 octobre 2026 : bibliothèque de 21 mouvements pour le test d’intégration sur l’option 1. Le fichier renard-design-v2.blend est une copie de renard-bibliotheque-v2.blend. Voir [la bibliothèque, les exports et les raccords](renard-bibliotheque-mouvements-v2.md) et [le prompt pour l’expert Remotion](prompt-expert-remotion-renard-option-1.md). Les propositions V2, V3 et V4 ci-dessous sont rejetées et conservées pour historique. Aucune validation esthétique acquise.**

Date : 11 octobre 2026. **Étape 1 : proposition d’apparence retouchée, non validée.**

La planche 2D approuvée a été examinée avant la construction. Le modèle v1 rejeté et son script n’ont pas été utilisés comme base. Cette livraison présente un nouveau modèle 3D statique ; elle ne constitue pas une validation de la fidélité du design ni une mascotte prête à marcher.

## Retouches 01 — retour utilisateur du 11 octobre 2026

**Version historique : retouches-01, rejetée.** Le retour utilisateur signale des yeux trop grands et effrayants, un museau trop massif et un dessin insuffisant des oreilles et des mains. La référence reste exclusivement [renard-expressions-v2-regard.png](../output/design/renard-expressions-v2-regard.png), examinée à nouveau avant les retouches.

- **Yeux** : largeur de l’ouverture réduite, moins de blanc exposé, iris ambre simple, pupilles et reflets mesurés ; retrait des fibres et cercles décoratifs de l’iris précédent. Paupières et sourcils plus fins. Les surfaces suivent le crâne et le regard est orienté vers le côté de la référence.
- **Museau et tête** : longueur et largeur réduites, truffe plus petite, suppression du volume inférieur saillant. La base de la tête est reconstruite à partir de sections longitudinales continues, avec transition vers le museau ; reprise des joues et de la marque crème pour conserver leur contour orange. Le sourire reste discret.
- **Oreilles** : silhouette triangulaire plus compacte, conque en volume, pointe sombre réduite et liseré extérieur fin. L’oreille proche est légèrement orientée pour que sa largeur soit lisible en trois quarts.
- **Mains** : paume affinée, quatre doigts de longueurs différenciées et pouce opposé, articulations légèrement courbées et extrémités arrondies. La résolution locale de construction et le lissage ont été ajustés pour conserver les espaces entre les doigts ; raccord au poignet repris.
- **Comparaison** : profil et trois quarts tournés vers la droite de l’image, comme la référence. La pose de contrôle conserve les bras relâchés ; les gestes de présentation, réflexion et satisfaction ne sont pas encore construits.

Les dimensions de construction de l’ouverture des yeux et de la projection maximale du museau ont été diminuées ; ce sont des paramètres de géométrie, pas une mesure de similitude du rendu avec la planche 2D. Aucune fidélité exacte ni validation utilisateur n’est déclarée.

Livraison de cette reprise : [comparaison avec la référence](../output/blender/v2/retouches-01/renard-v2-comparaison-reference.png), [cinq vues de contrôle](../output/blender/v2/retouches-01/renard-v2-planche.png), [visage](../output/blender/v2/retouches-01/renard-v2-visage.png), [main](../output/blender/v2/retouches-01/renard-v2-mains.png). Le fichier Blender actuel reste [renard-design-v2.blend](../blender/renard-design-v2.blend). La version précédente, ses images et son script sont conservés dans output/blender/v2/retouches-01/avant.

Les rapports de cette reprise sont dans [verification.json](../output/blender/v2/retouches-01/verification.json), [verification-reouverture.json](../output/blender/v2/retouches-01/verification-reouverture.json) et [verification-images.json](../output/blender/v2/retouches-01/verification-images.json). Scripts de comparaison et contrôle : scripts/render_fox_design_v2_revision_board.py et scripts/verify_fox_design_v2_revision.py.

Le maillage reste une construction dense de revue d’apparence, à adapter pour les déformations. Aucune action, aucun rig ni animation ajouté. La référence incorporée est conservée et Untitled.blend reste intact. Aucun fichier de l’application Remotion n’est modifié.

## Fichiers livrés

- [Scène Blender éditable](../blender/renard-design-v2.blend).
- [Planche de revue : face, profil, trois quarts, visage](../output/blender/v2/renard-v2-planche.png).
- Rendus individuels RGBA : [face](../output/blender/v2/renard-v2-face.png), [profil](../output/blender/v2/renard-v2-profil.png), [trois quarts](../output/blender/v2/renard-v2-trois-quarts.png), [visage](../output/blender/v2/renard-v2-visage.png).
- [Rendu après réouverture du fichier enregistré](../output/blender/v2/renard-v2-verification-reouverture.png).
- Rapports : [construction](../output/blender/v2/verification.json), [réouverture et géométrie](../output/blender/v2/verification-reouverture.json), [images et transparence](../output/blender/v2/verification-images.json).
- Scripts dédiés : [construction](../scripts/build_fox_design_v2.py), [contrôle](../scripts/verify_fox_design_v2.py), [planche](../scripts/render_fox_design_v2_board.py).

Le fichier utilisateur **blender/Untitled.blend est inchangé**, vérifié par SHA-256 avant et après le travail : c07ea3121d866f07eed5303e23f599d163f3c1616e09beb519b5cf53928df4df. Aucun fichier Remotion, application ou audio n’a été modifié.

## Apparence proposée et revue attendue

Volumes élancés, museau allongé, grandes oreilles épaisses et pointues, joues effilées, queue longue avec démarcation crème angulaire. Corps terracotta, museau et poitrine crème, mains/avant-bras et bas des jambes anthracite. Foulard sauge avec col, pli et pan à franges.

Les yeux ambrés sont posés sur la surface du crâne ; les blancs, iris, pupilles, reflets, paupières et sourcils sont des objets distincts destinés aux futurs contrôles. Le sourire est discret. La pose de revue est debout avec les bras détendus ; elle ne reproduit pas les trois gestes de la planche.

Les corrections internes ont porté sur les yeux initialement trop saillants, les limites crénelées des couleurs, le volume du foulard, les doigts, les joues et les raccords aux épaules et aux hanches. Les images livrées sont des rendus de la géométrie Blender, sans retouche du personnage.

À comparer avec la référence approuvée : proportions tête/corps, longueur et largeur du museau, forme des yeux et regard, contours des oreilles et des joues, ampleur de la queue, découpe des marques et drapé du foulard. La perception du volume et les couleurs sous éclairage 3D restent à examiner par l’utilisateur. Les volumes arrière sont une construction cohérente proposée à partir de la seule planche disponible.

## Organisation de la scène

| Collection | Contenu |
| --- | --- |
| 01 — Renard · volumes | Corps continu incluant membres, mains et pieds ; tête et museau fusionnés ; oreilles et queue |
| 02 — Visage · regard et expression | Blancs des yeux, iris, pupilles, reflets, paupières, sourcils, truffe et sourire |
| 03 — Foulard | Col épais, pan, pli et franges |
| 04 — Studio · cameras et lumières | Cinq caméras orthographiques nommées et trois grandes lumières de studio |
| 90 — Construction · volumes sources | Volumes avant fusion, masqués pour le rendu et la vue ; à conserver pour les reprises |
| 99 — Référence approuvée | Planche 2D incorporée dans le .blend, masquée pour le rendu |

Le corps et la tête ont été fusionnés par remeshing puis lissés, avec subdivision conservée. Le corps, la tête et la queue sont chacun un seul maillage connecté et fermé selon le contrôle de réouverture. Les oreilles et éléments du visage sont séparés pour permettre des modifications et futurs contrôles ; cette séparation n’est pas une articulation.

Les matériaux sont procéduraux. Les attributs de points bib et gloves_boots contrôlent les couleurs du corps ; jaw contrôle le masque crème du museau. Le marquage angulaire de la queue utilise les coordonnées géométriques dans son matériau. Aucun fichier de texture externe n’est nécessaire. La référence est incorporée dans le .blend.

## Caméras, orientations et export

- Face du personnage : **-Y** ; dos : +Y ; haut : +Z ; les côtés sont sur X. Origine du corps au centre ; pieds au voisinage de Z = 0. Les unités sont des unités de travail, sans échelle physique validée.
- Caméras : Caméra · face, Caméra · profil, Caméra · trois quarts, Caméra · détail visage, Caméra · détail main. La caméra active enregistrée est celle de trois quarts. Face et profil sont des vues axiales ; le trois quarts est légèrement plongeant.
- Fichier enregistré : **1080 × 1920, 100 %, 30 images/seconde, PNG RGBA 8 bits, fond transparent**, sortie dans output/blender/v2/retouches-01/renard-v2-.
- Moteur : Cycles, 48 échantillons, débruitage, éclairage de studio large ; gestion de couleurs AgX.
- Rendus de revue : **900 × 1100**, quatre PNG RGBA standard et un détail de main RGBA. La planche sur fond clair est un montage de ces rendus. Le détail visage est volontairement cadré sur la tête et le foulard.
- Le cadrage actuel présente le modèle pour examen. La taille de guide de 13–18 % d’un écran vertical n’a pas été testée dans une leçon et n’est pas validée ici.
- La plage 1–240 est un réglage de travail de huit secondes à 30 i/s. **Elle ne contient aucune animation.** Aucun export de clip ou aperçu vidéo animé n’a été produit à cette étape.

## Articulation et bibliothèque d’actions : état réel

**Aucun squelette, contrôleur, poids de déformation, shape key animée ni action n’est livré.** La scène ne doit pas être présentée comme animée ou prête à la marche. Les durées, contacts au sol et boucles restent à définir et tester après les retours sur l’apparence.

| Étape / action | État |
| --- | --- |
| Adaptation de la topologie pour les déformations | À réaliser après revue du design |
| Rig debout / quadrupède, mains, tête, queue, oreilles et visage | À créer et vérifier |
| Marche quadrupède, arrêt et regard — test 5 à 10 s | Priorité suivante après rig |
| Présentation gauche, droite, haut | À produire après le premier test de marche |
| Découverte avec ampoule indépendante | Priorité suivante ; accessoire non créé |
| Attente vivante et clignements | À produire |
| Passage debout / quatre pattes / retour | À produire |
| Entrée, traversée, arrêt, sortie et trajectoires séparées | À produire |
| Disparition et réapparition | À produire |
| Réflexion | À produire |
| Loupe indépendante | À produire ; accessoire non créé |
| Réponse correcte | À produire |
| Erreur et encouragement | À produire |
| Écoute et répétition | À produire |

Le remeshing donne une surface continue dense, utile pour cette revue d’apparence ; il ne remplace pas une topologie de déformation étudiée. La topologie des articulations et du visage, les poids, les collisions du foulard, les déformations debout/quadrupède et les contrôles du regard doivent être préparés avant les animations. Les masques procéduraux devront également être vérifiés sur les déformations, notamment la queue.

Les futurs clips seront nommés et documentés avec leur plage d’images, leur durée, leur orientation, leurs contrôles, les contacts et les raccords de boucle. La trajectoire globale sera séparée des gestes et de la locomotion autant que possible. L’ampoule et la loupe seront indépendantes. L’intégration Remotion reste entièrement hors de ce travail.

## Vérifications effectuées

Blender 5.2.2 LTS a chargé Untitled.blend, construit la proposition et enregistré un autre fichier. Les quatre rendus ont été examinés visuellement et corrigés au cours du travail. Le .blend final a été rouvert dans un processus Blender séparé, avec un nouveau rendu de contrôle. Les réglages sauvegardés, la référence incorporée, les composantes connectées et les bords non manifold des principaux volumes sont contrôlés dans les rapports. Les quatre PNG sont vérifiés comme RGBA avec transparence effective.

La prochaine décision porte exclusivement sur l’apparence : recueillir les retours sur ces vues, corriger le modèle, puis préparer l’articulation et le test prioritaire. Aucun statut d’apparence validée ou d’animation vérifiée n’est attribué à cette livraison.
