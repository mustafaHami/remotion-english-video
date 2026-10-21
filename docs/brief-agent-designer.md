## Contexte et mission
Nous créons des shorts d’anglais pratique pour TikTok, Instagram Reels et YouTube Shorts : restaurant, voyage, hôtel, magasin, situations quotidiennes, puis grammaire et quiz. Le public est mixte, notamment adulte et professionnel. La présentation doit être chaleureuse, expressive et soignée, avec un humour discret, sans esthétique enfantine.
Blender servira à créer et animer une mascotte réutilisable ; Remotion assemblera les leçons, les textes, les quiz, la voix et les transitions. Higgsfield est mis de côté. Ton travail se limite exclusivement à Blender : reproduire notre renard, préparer son articulation et créer ses animations. Tu ne dois pas développer, modifier ni réaliser la partie Remotion ; elle sera traitée par un autre agent.

## Références et fichiers
Le projet se trouve dans D:/ai-generation-video.
Lis PROJET.md et docs/mascotte.md pour comprendre les décisions.
Examine réellement assets/branding/renard-reference-validee.png avant de modéliser. Cette planche 2D est la référence esthétique approuvée. Sa copie historique est output/design/renard-expressions-v2-regard.png. Les trois attitudes montrées — réflexion, explication et satisfaction — sont des références, pas une limite de trois poses.
Le fichier de travail à ouvrir et reprendre est blender/renard-v1.blend. Corrige ou reconstruis son personnage selon la référence 2D approuvée, puis enregistre le résultat dans blender/renard-design-v2.blend pour conserver la version précédente. blender/Untitled.blend était uniquement un test d’installation : ce n’est pas une base de travail pour le designer.
L’apparence du modèle blender/renard-v1.blend et ses rendus output/blender/renard-3d-v1-*.png ont été explicitement rejetés. Le fichier renard-v1.blend reste le fichier de travail à reprendre, mais son design ne fait pas référence : seule l’image approuvée doit guider le résultat. Tu peux reconstruire entièrement la géométrie dans ce projet si nécessaire. Le script scripts/build_fox.py correspond à cette proposition rejetée ; ses choix ne doivent pas dicter le nouveau design.
Blender 5.2.2 LTS est installé dans C:/Program Files/Blender Foundation/Blender 5.2/blender.exe.
La partie Remotion est hors de ton périmètre : ne modifie ni src/RestaurantQuiz.tsx, ni src/Root.tsx, ni aucun autre fichier de l’application. La vidéo actuelle est un prototype jugé insatisfaisant, pas une direction graphique validée. La voix Windows utilisée a également été rejetée ; son remplacement sera traité séparément.

## Identité du renard
Conserve une silhouette élancée et des proportions adultes, un museau allongé, de grandes oreilles pointues et une longue queue expressive. Pelage terracotta/orange chaud ; museau, poitrine et pointe de queue crème ; avant-bras, mains et bas des jambes anthracite ; foulard vert sauge.
Les yeux ambrés doivent être attirants, vivants et expressifs, avec des reflets mesurés, des sourcils mobiles et un sourire discret. Personnalité : curieux, débrouillard, gentil, enthousiaste et encourageant.
Le renard doit être exactement le même personnage que sur l’image approuvée. Ne propose pas une réinterprétation libre ni une nouvelle direction artistique. Respecte le design avec le plus grand soin : silhouette, proportions, forme de la tête et du museau, yeux, oreilles, sourcils, couleurs, marques du pelage, queue et foulard. La mise en volume doit reproduire fidèlement ce design ; la création des volumes non visibles sur l’image doit rester cohérente avec lui. Travaille la silhouette, les transitions de volumes, le visage, les mains, les matériaux et l’éclairage. Une accumulation de primitives, des membres en cylindres assemblés, des raccords visibles, des éléments flottants ou des oreilles en plaques ne constituent pas le résultat recherché.
Évite les proportions de bébé, les yeux démesurés, l’effet peluche ou jouet en plastique et l’apparence effrayante. Ne remplace pas notre mascotte par un personnage de franchise. Son identité doit rester cohérente entre les épisodes.

## Présence dans les vidéos
Le renard est un petit guide secondaire : environ 13 à 18 % de la hauteur d’une vidéo constitue un point de départ à tester, pas une règle définitivement validée. Il doit rester lisible sans masquer les phrases.
Il ne doit pas rester figé dans un coin. Il traverse la scène, entre, sort, disparaît et réapparaît selon le scénario, en bas, à gauche ou en haut. Place les grands déplacements aux transitions ; pendant la lecture et la répétition, privilégie des réactions mesurées.
La participation du spectateur passe par le quiz et la répétition orale ; ce n’est pas une interface cliquable.

## Bibliothèque d’animations à préparer
1. Attente vivante : respiration subtile, clignements, petites réactions des oreilles et de la queue, regard attentif ; boucle calme.
2. Marche à quatre pattes : vraie démarche avec contacts au sol, articulation des membres, transfert du poids et mouvement de la queue ; permettre les deux directions.
3. Passage debout/quatre pattes et retour : transition crédible, sans écrasement des épaules, des hanches ou du foulard.
4. Entrée, traversée, arrêt et sortie : depuis les bords de la scène. Séparer autant que possible l’animation corporelle de la trajectoire à l’écran pour varier les placements dans Remotion.
5. Disparition et réapparition : anticipation, retrait ou sortie, puis retour à une autre position, éventuellement en haut. Un effet discret peut être composé dans Remotion plutôt que intégré au corps.
6. Réflexion : regard vers les choix, tête inclinée, main au menton, réactions des sourcils et des oreilles.
7. Découverte avec une petite ampoule : regarder l’endroit où l’ampoule apparaît, réagir avec les yeux et les sourcils, sourire, puis regarder la réponse et faire un geste de découverte. L’ampoule reste un accessoire indépendant, avec apparition et lumière synchronisables.
8. Présentation : montrer la question ou la réponse par un geste clair, regarder la zone visée, puis revenir vers le spectateur ; variantes gauche, droite et haut.
9. Loupe : la suivre du regard ou l’utiliser pour examiner les choix, puis réagir ; accessoire séparé et contrôlable.
10. Réponse correcte : sourire, hochement de tête, pouce levé ou approbation, réaction légère de la queue.
11. Erreur et encouragement : surprise douce, puis geste rassurant, sans moquerie.
12. Écoute et répétition : posture attentive, invitation à écouter, geste « à toi », puis attente calme.
Les expressions doivent aussi mobiliser le regard, les paupières, les sourcils, la bouche, les oreilles et la queue, pas seulement changer la pose globale.

## Ordre de travail et livrables
1. Créer une proposition 3D soignée et montrer des rendus de face, profil, trois quarts et un détail du visage. Faire examiner son apparence avant de multiplier les animations.
2. Après les retours, préparer un squelette et des contrôles adaptés aux postures debout et quadrupède : corps, tête, membres, queue, oreilles, regard, sourcils et bouche. Vérifier les déformations ; des pièces séparées ne constituent pas à elles seules un personnage articulé.
3. Produire un test de 5 à 10 secondes : marche à quatre pattes, arrêt et regard vers un élément. Tester ensuite la présentation et la découverte avec ampoule. Ces actions sont prioritaires.
4. Construire progressivement les autres actions comme des clips nommés, avec départs/fins cohérents et boucles propres si nécessaire.
5. Préparer uniquement les exports Blender pour une intégration ultérieure réalisée par un autre agent : référence vidéo 1080 × 1920 à 30 images/seconde, caméra stable, personnage sur fond transparent lorsque possible, par exemple en séquences PNG RGBA. Fournir des aperçus vidéo et vérifier les exports dans Blender. Ne réalise pas l’intégration Remotion.
6. Livrer le fichier .blend éditable, ses ressources nécessaires, les aperçus et une documentation des actions, durées, orientations, contrôles, réglages d’export et limites restantes. Rendus dans output/blender/v2 ; documentation dans docs/renard-design-v2.md.
Distingue les propositions des validations. Ne présente pas le personnage comme animé ou prêt à marcher sans avoir vérifié les rendus. L’objectif est une mascotte cohérente et expressive, réutilisable sur de nombreux épisodes sans recréer son apparence à chaque leçon.
