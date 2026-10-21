# Renard — bibliothèque Blender pour l’exemple Remotion de l’option 1

18 octobre 2026. L’utilisateur demande la création des mouvements dans Blender et un prompt destiné à son expert Remotion. L’intégration de la leçon sera réalisée par cet expert. Aucun fichier d’application Remotion ni audio n’est modifié dans cette livraison.

## Fichiers actuels

- **Source modifiable** : `D:/ai-generation-video/blender/renard-bibliotheque-v2.blend`.
- **Fichier principal habituel** : `D:/ai-generation-video/blender/renard-design-v2.blend`, copie identique de cette source. L’ancien principal est conservé dans `output/blender/mouvements-v2/avant/renard-design-v2.blend`.
- **Exports et manifeste** : `D:/ai-generation-video/output/blender/mouvements-v2/`.
- **Passation à copier** : `D:/ai-generation-video/docs/prompt-expert-remotion-renard-option-1.md`.
- **Aperçu de toutes les actions** : `output/blender/mouvements-v2/renard-bibliotheque-mouvements-v2.mp4`.
- **Référence verticale** : `output/blender/mouvements-v2/reference-verticale-1080x1920.mp4`.
- **Planche** : `output/blender/mouvements-v2/planche-mouvements.jpg`.

La référence esthétique approuvée reste `assets/branding/renard-reference-validee.png`. La V5 du visage sert de base à cette bibliothèque ; la demande de poursuivre les mouvements n’équivaut pas à une validation de tous les volumes de la version 3D. Les fichiers V1 et leurs aperçus sont conservés pour l’historique.

## Actions livrées

Chaque action corporelle porte le préfixe `MVT_` dans Blender. Les deux objets d’accessoires ont chacun leur action `ACC_<id>_<accessoire>`. Les actions sont conservées avec un utilisateur fictif ; elles restent disponibles même lorsqu’elles ne sont pas actives.

| Identifiant | Images à 30 i/s | Durée | Usage |
|---|---:|---:|---|
| attente | 120 | 4 s | Respiration, regard, oreilles, queue et clignements ; boucle |
| attente-quatre-pattes | 120 | 4 s | Attente quadrupède ; boucle |
| marche | 36 | 1,2 s | Cycle sur place ; boucle |
| demarrer-marche | 36 | 1,2 s | Préparation depuis la pose quadrupède |
| arreter-marche | 36 | 1,2 s | Arrêt et pose des appuis |
| se-lever | 60 | 2 s | Quatre pattes vers debout, avec repositionnement des pieds |
| se-baisser | 60 | 2 s | Retour à quatre pattes |
| presenter-gauche | 90 | 3 s | Main ouverte et regard vers la gauche |
| presenter-droite | 90 | 3 s | Main ouverte et regard vers la droite |
| presenter-haut | 90 | 3 s | Présentation vers le haut |
| reflechir | 120 | 4 s | Main au menton, index, regard et sourcils |
| decouvrir | 90 | 3 s | Réaction de découverte, regard vers l’ampoule et présentation |
| examiner-loupe | 120 | 4 s | Prise et déplacement de la loupe, regard attentif |
| bravo | 90 | 3 s | Sourire, hochement et pouce levé |
| encourager | 90 | 3 s | Surprise douce puis geste rassurant |
| ecouter | 90 | 3 s | Main vers l’oreille et posture d’écoute |
| a-toi | 90 | 3 s | Invitation à répéter, main vers le spectateur |
| saluer | 90 | 3 s | Salut de la main ; entrée ou au revoir |
| retrait | 36 | 1,2 s | Anticipation corporelle d’une disparition |
| reapparaitre | 36 | 1,2 s | Retour de l’anticipation vers la pose debout |
| regarder-haut | 90 | 3 s | Réaction à un élément situé en haut |

Total du personnage : **1 680 images, soit 56 secondes d’actions** avant répétition des boucles. Les six clips de locomotion disposent aussi d’une copie miroir PNG pour l’autre sens. L’ampoule et la loupe ajoutent respectivement 90 et 120 images transparentes indépendantes.

## Formats et ancrage

Les médias d’intégration sont des **séquences PNG RGBA de 768 × 768 pixels à 30 i/s**, rendues dans Blender avec les matériaux du personnage. Le carré est le canevas de l’élément à superposer, pas le format de la leçon. La référence vidéo verticale est en 1080 × 1920 à 30 i/s.

Tous les clips utilisent une caméra orthographique identique : `Bibliothèque · caméra fixe`. L’échelle du personnage reste identique entre postures. Le point d’appui de référence est environ **(390,07 ; 659,00)** dans le canevas. Les coordonnées exactes et la hauteur debout réellement occupée figurent dans `manifest.json`.

Ne jamais recadrer les images individuellement selon leur alpha, ni agrandir la posture quadrupède pour lui donner la hauteur de la posture debout. Pour placer le point d’appui à `(x, y)` avec une échelle `k`, placer le coin du canevas à `(x - anchorX*k, y - anchorY*k)`. Les accessoires utilisent exactement le même canevas et le même placement.

Le fichier `image-0001.png` représente la frame locale Remotion 0. Une boucle de N images se lit avec `(frameLocale % N) + 1`. Les actions non bouclables reviennent généralement à une pose de raccord ; les champs `entry` et `exit` du manifeste sont à consulter avant l’assemblage.

Les MP4 ont un fond ivoire pour être regardés facilement. Ils ne conviennent pas à une superposition transparente. Utiliser les PNG pour le premier test.

## Trajectoires et sens

Le rig et les PNG restent à l’origine. `TRAJECTOIRE · déplacement indépendant` est présent dans le fichier, sans action active. Blender anime le corps ; Remotion calcule les trajets à l’écran.

La marche est un cycle de 36 images, avec des appuis diagonaux et une phase d’appui de 64 %. La translation virtuelle correspondant au cycle est de **1,08 unité Blender vers −Y**. Le manifeste contient sa projection en pixels, `screenTravelPerCyclePixelsAtNativeScale`. Elle sert à régler la vitesse d’écran, multipliée par l’échelle du personnage. La projection inclut une composante verticale correspondant au sol vu par la caméra ; une trajectoire strictement horizontale est un choix graphique dont les appuis doivent être contrôlés à la taille finale.

Le sens natif est vers la droite. Les dossiers `frames/miroir-...` sont des copies miroir du canevas complet pour les six clips de locomotion. Leur ancrage horizontal devient `768 - anchorX`. Les autres gestes peuvent être retournés avec la couche complète et l’accessoire. Un geste de présentation change alors également de direction.

Les clips de démarrage et d’arrêt adaptent l’amplitude des pas. Remotion doit accompagner ces phases par une vitesse progressive et vérifier les appuis dans le montage. Une sortie ou une réapparition convient mieux à un changement important d’emplacement qu’un déplacement trop rapide du personnage.

## Raccords prévus

Entrée marchée : attente quadrupède → démarrage → cycle de marche répété → arrêt → se lever → geste debout. Départ : fin neutre du geste → se baisser → démarrage → marche jusqu’à la sortie.

Les gestes de présentation, réflexion, découverte, loupe, approbation, encouragement, écoute, répétition et salut partent et reviennent debout. Les boucles d’attente peuvent occuper les temps pédagogiques. La fin d’un geste peut être suivie d’un autre geste ou de l’attente sans modifier l’échelle.

`retrait` termine dans une petite anticipation ; `reapparaitre` commence dans cette même pose et revient debout. Le changement de position et l’opacité sont à composer dans Remotion. Ces deux actions ne contiennent pas d’effet magique ni de disparition rendue dans le corps.

## Accessoires indépendants

L’ampoule (`ACCESSOIRE · Ampoule`) et la loupe (`ACCESSOIRE · Loupe`) se trouvent dans `09 — Accessoires animés · indépendants`. Leurs éléments sont de véritables objets Blender modifiables. Leurs transformations sont animées séparément, en synchronisation avec le personnage.

- `accessoires/ampoule/image-XXXX.png` accompagne `decouvrir` à la même frame locale.
- `accessoires/loupe/image-XXXX.png` accompagne `examiner-loupe` à la même frame locale.

Les apparitions et retraits sont animés par la taille de l’accessoire ; les images de début et de fin peuvent donc être entièrement transparentes. La loupe possède un cerclage et un manche, avec un centre ouvert pour laisser les éléments observés lisibles. L’ampoule utilise un matériau lumineux ; aucun éclairage de la leçon n’est incorporé au PNG du personnage.

## Ouvrir et sélectionner un clip dans Blender

Ouvrir `blender/renard-bibliotheque-v2.blend`. Le fichier démarre sur l’attente debout. Sélectionner l’action `MVT_<id>` sur `RIG · Renard`, puis les deux actions d’accessoires correspondantes si besoin ; régler la fin de chronologie sur le nombre d’images indiqué.

Le script `scripts/select_fox_motion_v2.py` fait cette sélection avec `--clip <id>` lorsqu’il est exécuté par Blender. `scripts/export_fox_library_v2.py` permet de réexporter un clip avec `--only <id>` ; `--accessories` produit uniquement sa passe d’accessoire. Les contrôles de rig de la V1 restent disponibles : corps, colonne, poitrine, cou, tête, mains et pieds IK, pôles, oreilles, queue, foulard, regard, clignement, sourire et sourcils. Les doigts, pouces et index disposent de contrôles de fermeture distincts.

Les drivers des yeux s’observent en rendu ou en aperçu matériau ; les couleurs statiques du mode solide ne constituent pas une vérification du regard animé. Les rendus d’intégration utilisent Eevee, avec les matériaux de la scène ; les anciens tests Workbench ne sont pas les exports de cette bibliothèque.

## Vérification et limites

Les contrôles de toutes les actions sont évalués sur leurs 1 680 images. Les rapports sont dans `verification-rig.json`, `verification-boucles-appuis.json`, `verification-exports.json` et `verification-videos.json`.

Les 23 vidéos ont été rechargées dans Blender pour vérifier leurs dimensions, leur nombre d’images et leurs 30 i/s. La bibliothèque complète dure 56 secondes ; la référence verticale dure 16,4 secondes. Neuf images ont aussi été décodées depuis les MP4 livrés, dont les gestes avec accessoires, le salut, la présentation en haut et la vue verticale ; ces captures sont dans `lecture-video-*.png`. La transparence et le cadrage sont contrôlés sur toutes les images PNG. `verification-decodage-videos.json` consigne les captures réelles des fichiers encodés.

Les trois boucles retrouvent exactement leurs contrôles à la frame virtuelle suivante. Les contrôles en appui de la marche restent immobiles, à moins d’un millionième d’unité, lorsqu’on applique la translation virtuelle prévue. Les échantillons de surface donnent un écart au sol d’environ 0,022 unité aux doigts en appui et −0,002 unité aux pieds ; le suivi des contrôles ne prouve pas à lui seul une perfection anatomique de la démarche.

Le suivi IK maximal de l’ensemble est d’environ 0,0028 unité pendant la respiration debout ; la marche et les transitions de posture restent sous 0,0004 unité. Les principaux raccords de posture sont comparés dans le rapport. Le maillage continu et son articulation sont conservés, avec un lissage local ajouté aux hanches et aux épaules. Ce lissage ne constitue pas une nouvelle retopologie : la flexion profonde du personnage anthropomorphe conserve des volumes stylisés aux hanches et doit être examinée à la taille de l’exemple final.

La bibliothèque est livrée pour le **test d’intégration sur l’option 1**, sans validation esthétique ou autorisation de publication implicite. Aucune synchronisation labiale n’est produite. Les déplacements, l’opacité de disparition et la mise en page de la leçon appartiennent au travail Remotion.
