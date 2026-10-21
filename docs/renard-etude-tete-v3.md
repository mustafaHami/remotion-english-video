# Renard — étude de tête V3

16 octobre 2026. **V3 rejetée : yeux trop en avant, tête trop ronde et longue, bords d’oreilles insuffisamment sombres. Voir la [retouche V4](renard-etude-tete-v4.md), non validée.**

## Retour utilisateur et portée

La V2 et ses premières retouches sont rejetées : le personnage fait peur, le regard ne reproduit pas la référence, les oreilles sont trop longues et les pointes de joue ne correspondent pas au dessin approuvé. La V3 reprend la tête ; elle ne valide ni la mascotte complète, ni son articulation.

Référence unique : [renard-expressions-v2-regard.png](../output/design/renard-expressions-v2-regard.png). L’image a été examinée de nouveau avant cette reprise. Aucune image générée n’est utilisée à la place de la géométrie Blender.

## Fichiers

- [Étude de tête éditable](../blender/renard-etude-tete-v3.blend) : caméra trois quarts, rendu carré 1000 × 1000.
- [Scène complète V3 archivée](../output/blender/v4/avant/renard-design-v2.blend) : même tête V3 dans le contexte du corps précédent, caméra plein pied, 1080 × 1920 à 30 i/s. Le corps et les mains ne sont pas validés par cette livraison.
- [Comparaison avec la référence](../output/blender/v3/renard-v3-comparaison-tete.png).
- [Face, trois quarts et profil](../output/blender/v3/renard-v3-tete-planche.png).
- [Trois quarts individuel](../output/blender/v3/renard-v3-tete-trois-quarts.png), [face](../output/blender/v3/renard-v3-tete-face.png), [profil](../output/blender/v3/renard-v3-tete-profil.png).
- [Contexte plein pied](../output/blender/v3/renard-v3-contexte.png), fourni uniquement pour le contrôle du cadrage.
- [Vérifications de construction](../output/blender/v3/verification.json) et [contrôle de réouverture](../output/blender/v3/verification-reouverture.json).

La version rejetée antérieure à cette reprise est conservée dans output/blender/v3/avant/renard-design-v2.blend, avec son script. Untitled.blend est préservé ; son empreinte est contrôlée. Aucun fichier Remotion, application ou audio n’est modifié.

## Construction reprise

- Crâne et museau en surface continue ; volume frontal repris pour mieux loger les yeux et conserver la lecture de l’œil éloigné.
- Oreilles raccourcies, base triangulaire élargie relativement à la hauteur, racine prolongée dans le crâne. Chaque oreille est un maillage fermé avec une conque ; la couleur intérieure et le bord sombre appartiennent au matériau de la coque.
- Deux petites découpes de joue intégrées remplacent les longues pointes latérales. Pas de chevelure ajoutée.
- Cou soudé au volume de la tête ; l’ancienne extrémité de cou du corps est rentrée dans le foulard pour éviter une jointure visible sous le menton.
- Yeux continus : blancs, iris, pupilles et petit reflet sont calculés sur une même surface UV. Les disques d’iris et reflets en sphères séparées sont supprimés. Le rapport pupille sombre / iris et la teinte ambrée ont été repris à partir du gros plan de référence. Des logements peu profonds et des paupières fines relient le regard au visage.
- Orientation des faces des yeux et paupières contrôlée et corrigée. Les anneaux de surface précédents avaient une orientation incohérente avec leurs faces centrales, ce qui faussait l’éclairage.
- Truffe triangulaire arrondie et sourire fin. Matériaux mats terracotta, crème et anthracite ; éclairage neutre doux. Une contribution non éclairée modérée conserve les couleurs de l’illustration et limite l’aspect plastique.

## Modifications et contrôles disponibles

Les objets visibles de cette reprise portent le préfixe V3 dans les collections du personnage et du visage. Les matériaux des yeux s’appellent V3 · Œil · regard -1 et 1. Les nœuds de valeur Regard horizontal et Regard vertical déplacent le dessin de l’iris dans chaque œil ; ils ne sont pas animés. Les attributs inner, rim et height contrôlent l’intérieur, le bord et le dégradé des oreilles. L’attribut jaw contrôle la zone crème de la tête.

Ces paramètres facilitent les reprises du design. Ils ne constituent pas un rig facial ni une bibliothèque d’expressions. Le regard, les paupières, sourcils, oreilles et bouche devront être adaptés à une articulation cohérente après examen de l’apparence.

## Rendus et limites

Cycles, 32 échantillons et débruitage pour les vues de tête (48 dans le fichier de travail) ; PNG RGBA 1000 × 1000 avec transparence. Gestion de couleurs Standard ; lumière blanche légèrement chaude ; surfaces très rugueuses, reflets contenus. La scène de contexte garde les réglages verticaux 1080 × 1920, PNG RGBA, 30 i/s. Son petit aperçu plein pied est en 540 × 960.

La comparaison utilise un extrait de la planche approuvée et un cadrage de la véritable image rendue, sans retoucher le personnage rendu. La mise en volume reste une proposition à examiner. La fidélité des proportions, du regard et des silhouettes ne peut pas être déclarée validée par un contrôle technique.

Le corps, les mains, le drapé complet et la queue ne font pas l’objet d’une nouvelle validation dans cette étude. Les maillages d’étude restent denses et demandent une topologie de déformation étudiée. Aucun squelette, poids de peau, animation, marche, clignement ou export de clip n’est créé ou vérifié. Les actions demandées dans le brief initial restent à produire après la revue du design.

Scripts : scripts/sculpt_fox_head_v3.py construit l’étude depuis la copie précédente ; scripts/tune_fox_eyes_v3.py règle la pupille et l’ambre ; scripts/finish_fox_head_v3.py contrôle les orientations, produit les vues et enregistre la scène de contexte ; scripts/render_fox_head_v3_board.py compose la comparaison et la planche. La référence est incorporée dans le .blend ; les matériaux sont procéduraux, sans textures externes requises.
