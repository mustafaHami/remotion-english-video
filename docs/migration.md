# Migration vers les options stables — 21 octobre 2026

Validation utilisateur de l’ensemble des formats ; consolidation des règles finales. Les dossiers `output/tests/test-option-N` ont été déplacés, sans suppression, vers `output/options/option-N`. Les anciens fichiers versionnés de rendu restent présents localement ; le nouvel exemple porte simplement `option-N.mp4`.

Les sources des prototypes sont dans `src/archive/experiments`. Leurs imports ont été ajustés. Les modèles actifs sont désormais `src/options/option-N` et `ProductionLesson`, avec contenu injecté dans `LessonContentContext`. Les vues partagées ont été extraites dans `templates/LessonViews` ; les archives réexportent ces vues. Les entrées Studio historiques n’apparaissent plus dans le catalogue actif.

Les dernières règles du renard de face, du corps fixe, de la main et du pouce sont communes aux 14 options. Les quiz sont raccourcis avec une transformation déterministe de leur timeline ; les conversations et répétitions gardent leurs fenêtres spécifiques. Les voix du dialogue alternent Sonia/Ryan. Aucune source Blender n’a été modifiée.

Le registre initial contient exactement les deux publications déclarées du 20/10/2026. Aucun rendu exécuté pendant la migration n’est enregistré comme nouvelle publication.

Les vérifications effectives et les rendus disponibles sont consignés dans `docs/verification.md`. La préparation du VPS et des plateformes est explicitement reportée à `deploy/TODO-VPS.md` selon instruction utilisateur.
