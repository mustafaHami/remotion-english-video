# Renard — expression V5 et premiers tests d’articulation

**Historique remplacé par la [bibliothèque de mouvements V2](renard-bibliotheque-mouvements-v2.md), créée le 18 octobre 2026 pour l’exemple de l’option 1. Le fichier principal renard-design-v2.blend contient désormais cette bibliothèque. Les deux clips V1 ci-dessous restent des tests historiques, avec leurs cadrages différents ; ne pas les utiliser pour la nouvelle intégration.**

16 octobre 2026. Proposition en cours, sans validation esthétique. L’utilisateur demande une dernière retouche du visage, puis le passage à l’articulation et aux premiers mouvements ; cette demande autorise la poursuite sans nouveau cycle d’approbation du design.

## Expression retenue pour avancer
Les ouvertures des yeux sont agrandies, avec iris ambrés et reflets discrets. Le sourire a un coin de joue relevé et une courbe descendante au milieu, au lieu de la diagonale de la V4. La zone crème rejoint le dessous du museau. La référence 2D reste la direction artistique.

Étude statique : [renard-expression-v5.blend](../blender/renard-expression-v5.blend). Image : [expression V5](../output/blender/v5/renard-v5-expression.png).

## Fichiers à ouvrir
- [renard-design-v2.blend](../blender/renard-design-v2.blend) : fichier principal demandé, ouvert sur la présentation souriante.
- [renard-presentation-v1.blend](../blender/renard-presentation-v1.blend) : test debout de cinq secondes.
- [renard-rig-v1.blend](../blender/renard-rig-v1.blend) : test de marche à quatre pattes, arrêt et regard, six secondes.
- Les versions précédentes sont conservées, dont la V4 complète dans output/blender/v5/avant.

Dans Blender, lancer la lecture de la chronologie. Les réglages enregistrés sont 1080 × 1920, 30 images/seconde, PNG RGBA transparent, rendu Cycles. Les aperçus de contrôle utilisent le moteur Workbench avec les couleurs du personnage, pour examiner le mouvement plus rapidement ; ils ne remplacent pas le rendu final des matériaux.

## Clips et trajectoires
| Fichier ouvert par défaut | Action du personnage | Action de trajectoire | Images | Durée |
|---|---|---|---|---|
| renard-rig-v1.blend | TEST_01 · Marche quadrupède, arrêt, regard | TRAJET_01 · Avancée indépendante | 1–180 | 6 s |
| renard-presentation-v1.blend | TEST_02 · Présentation souriante | TRAJET_02 · Présentation sur place | 1–150 | 5 s |

L’armature RIG · Renard porte l’action corporelle. L’objet TRAJECTOIRE · déplacement indépendant porte le déplacement global. La marche avance vers l’axe −Y. La caméra reste fixe. La séquence ralentit, pose les dernières pattes et termine par un regard vers le spectateur. La présentation lève une main ouverte, accompagne le geste du regard, sourit et revient au repos.

Les deux actions du personnage et leurs trajectoires sont conservées dans les fichiers. Les actions sont échantillonnées à chaque image ; les dupliquer avant de les retoucher. Pour changer d’action, choisir aussi la trajectoire correspondante.

## Contrôles
Le squelette comporte 59 os. Le corps est un maillage continu déformé par des poids, avec conservation des volumes ; il ne s’agit pas de déplacer des membres séparés. Le corps a été allégé à 81 820 sommets avant subdivision. Tête, oreilles, queue et foulard suivent également le squelette.

- CTRL_global : placement général dans le rig ; l’objet TRAJECTOIRE sert au déplacement de la scène.
- CTRL_corps, CTRL_colonne, CTRL_poitrine, CTRL_cou, CTRL_tete : posture et orientation du corps et de la tête.
- CTRL_main.G/D, CTRL_pied.G/D : appuis des quatre membres, en cinématique inverse sans étirement.
- CTRL_coude.G/D et CTRL_genou.G/D : direction des articulations.
- CTRL_queue_0 à CTRL_queue_5 : courbe et mouvement de la queue.
- CTRL_oreille.G/D et pointes : réactions des oreilles.
- CTRL_foulard et CTRL_foulard_pointe : orientation du pan et mouvement secondaire.
- CTRL_regard : déplacement du regard, complété par les propriétés regard_horizontal et regard_vertical de l’armature.
- Propriétés clignement, sourire, curieux : formes de paupières, bouche et sourcils. doigts_G/D : fermeture des doigts ; les os individuels sont dans la collection Déformation.

Les courbes du visage et du foulard ont été converties en surfaces pour suivre les contrôles. La couleur de l’extrémité de la queue reste attachée à la géométrie pendant les mouvements.

## Vérifications et limites
Les fichiers ont été rouverts dans Blender 5.2.2 LTS. Les contrôles des quatre membres ont été évalués sur chaque image des deux clips. L’erreur maximale de suivi IK est d’environ 0,00030 unité pour la marche et 0,00377 pour la présentation. Aucun sommet du corps n’est sans poids ; l’écart maximal de normalisation est environ 0,00001. Les échantillons de déformation gardent le bas du corps au voisinage du sol, avec environ 0,002 unité de tolérance. Le déplacement nul des contrôles en phase d’appui est vérifié dans le calcul de marche ; cela ne constitue pas une mesure de perfection de la démarche.

Rapports : output/blender/rig-v1/verification-animation.json et verification-rig-finale.json. La référence est incorporée aux fichiers. Untitled.blend reste inchangé, empreinte SHA-256 c07ea3121d866f07eed5303e23f599d163f3c1616e09beb519b5cf53928df4df. Aucun fichier d’application Remotion ni audio modifié.

Ce sont les premiers tests de déformation. Les plis des hanches et des aisselles, la topologie des articulations et le visage demandent encore un travail ciblé avant des clips de production. La transition debout/quatre pattes n’est pas animée. Ampoule, loupe, marche dans l’autre sens et autres actions de la bibliothèque ne sont pas encore livrés. Les matériaux Cycles ne sont pas représentés fidèlement dans l’aperçu Workbench. Aucun clip n’est présenté comme validé ou prêt à publier.

## Aperçus livrés

- [Présentation souriante — 5 secondes](../output/blender/rig-v1/renard-presentation-test-v1.mp4), H.264, 540 × 960, 150 images à 30 i/s.
- [Marche, arrêt et regard — 6 secondes](../output/blender/rig-v1/renard-marche-test-v1.mp4), H.264, 1280 × 720, 180 images à 30 i/s.
- Images RGBA dans output/blender/rig-v1/presentation-frames et marche-frames ; fond ivoire uniquement dans les MP4 de contrôle. Encodage réalisé avec le séquenceur Blender.
- Les 330 images sont présentes, uniques, non vides, transparentes et sans bord coupé. Les caméras de marche ont été ajustées sur les bornes de toutes les poses, puis le rendu de marche recalculé. Les vidéos ont été rechargées dans Blender pour vérifier le nombre d’images et les dimensions. Rapports complémentaires : verification-images-clips.json, verification-video-presentation.json et verification-video-marche.json.
- Le sourire animé est maintenu sur un support de surface interne, puis suit le squelette. Une expression accentuée conserve ainsi le tracé de bouche visible.

Les fichiers s’ouvrent en vue caméra avec les couleurs du personnage. Lancer la chronologie pour lire le test. Réactiver les superpositions de la vue 3D pour afficher les contrôles. Les versions de travail antérieures et les images de diagnostic ne doivent pas être prises pour les derniers aperçus.

Les deux MP4 ont aussi été décodés dans Blender : une image du geste et une image de l’arrêt ont été réexportées et examinées. Captures : lecture-video-presentation.png et lecture-video-marche.png. Les tests montrent encore des plis marqués à la base des hanches et aux épaules ; la marche est un prototype technique, à reprendre avant une animation finale.
