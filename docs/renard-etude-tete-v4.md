> V4 rejetée lors du retour suivant : bouche inadaptée, yeux trop petits, manque de chaleur. Voir [expression V5 et articulation](renard-rig-v1.md). Le fichier principal porte maintenant la V5 articulée ; cette page décrit une version historique.

# Renard — retouche de tête V4

Statut : proposition statique du 16 octobre 2026, apparence non validée. La planche 2D approuvée reste la référence ; aucune version 3D ne la remplace.

## Retour traité
Yeux placés trop en avant, tête trop ronde et trop longue, contours anthracite des oreilles trop peu visibles. La V3 est conservée pour comparaison.

## Modifications
- Crâne raccourci à l’arrière, voûte abaissée et moins bombée ; museau raccourci avec truffe et sourire repositionnés.
- Ouvertures des yeux et iris réduits ; plans du visage reculés avec transitions adoucies ; yeux légèrement encastrés. Le rebord orange rapporté a été retiré : le contour appartient désormais au volume sculpté. Iris et pupilles sont sur une seule surface par œil.
- Oreilles abaissées et raccourcies ; bord externe anthracite élargi et pointe sombre plus étendue. Une coque fermée par oreille, avec intérieur concave.
- Raccords des petites pointes des joues repris pour supprimer le vide apparu pendant les essais.

## Fichiers
- Travail principal : [V4 complète archivée](../output/blender/v5/avant/renard-design-v2.blend).
- Étude avec caméra rapprochée : [renard-etude-tete-v4.blend](../blender/renard-etude-tete-v4.blend).
- Rendus et comparaisons : [output/blender/v4](../output/blender/v4).
- Scène précédente conservée : output/blender/v4/avant/renard-design-v2.blend.

L’étude comporte des caméras de face, profil et trois quarts. Le profil avant/après utilise la même caméra, la même échelle et le même éclairage. La comparaison avec la référence juxtapose une illustration 2D et un rendu 3D ; elle ne constitue pas une correspondance géométrique exacte.

## Utilisation et limites
Scènes organisées par volumes, visage, foulard, studio, sources de construction et référence incorporée. Le fichier principal est réglé en 1080 × 1920, 30 i/s, PNG RGBA transparent ; l’étude de tête est en 1000 × 1000. L’aperçu du corps est en 540 × 960.

Cette retouche concerne la tête. Le corps, les mains et le foulard restent des volumes de travail déjà proposés, sans nouvelle validation. Aucun squelette ni animation ; la topologie de déformation et les contrôles d’expression restent à préparer après examen du design. La ressemblance à la référence n’est pas présentée comme définitive.

Construction : scripts/sculpt_fox_head_v4.py à partir de output/blender/v3/avant/renard-design-v2.blend ; raccord des orbites par scripts/close_fox_eye_sockets_v4.py, qui produit output/blender/v4/candidat-raccord-yeux.blend ; finition et exports de ce candidat par scripts/finish_fox_head_v4.py ; contrôle de réouverture par scripts/verify_fox_head_v4.py. Le contrôle est limité à la scène statique et aux images produites.

## Vérifications réalisées

Les deux fichiers ont été rouverts dans Blender 5.2.2 LTS. Un rendu supplémentaire a été produit après réouverture de l’étude. Les vues de face, profil, trois quarts et le contexte du corps ont été examinés. Les PNG sont en RGBA avec transparence.

Le volume de tête, les coques d’oreilles et le corps conservé ne présentent aucune arête non fermée ni face de surface nulle dans ce contrôle. Les deux surfaces oculaires ont des normales cohérentes et aucune face de surface nulle. Le raccord sous les yeux a été repris après un premier contrôle : l’écart mesuré au support est maintenant compris entre environ 0,004 et 0,008 unité Blender.

La longueur du volume tête/museau suivant son axe avant-arrière est réduite de 25,7 % par rapport à la V3, mesurée sur les bornes de la géométrie. Il s’agit d’une mesure de forme, pas d’un score de fidélité à la référence.

Référence incorporée au fichier, aucune armature ni action. Le fichier utilisateur Untitled.blend conserve son empreinte SHA-256 initiale : c07ea3121d866f07eed5303e23f599d163f3c1616e09beb519b5cf53928df4df. Aucun fichier Remotion ou audio modifié. Rapports : output/blender/v4/verification.json, verification-reouverture.json et verification-images.json.
