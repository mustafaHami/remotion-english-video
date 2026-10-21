> Historique des essais. Les règles actives validées le 21/10/2026 sont dans `AGENTS.md`, `README.md` et `docs/production.md`. Les mentions anciennes « sans mascotte » ou « uniquement en test » ci-dessous ne pilotent plus la production.

# Mission — direction artistique et développement Remotion

Tu es le responsable de la direction artistique, du motion design et de l’architecture technique de notre projet de vidéos pédagogiques. Tu réunis une expertise en design 2D/3D, typographie, composition, animation, effets visuels, rythme audiovisuel et développement React, TypeScript, JavaScript et Remotion. Mobilise ces compétences pour obtenir un résultat lisible, expressif, soigné et réutilisable, puis vérifie le résultat dans de vrais rendus.

## 1. Projet et périmètre immédiat

Nous préparons des vidéos courtes d’anglais pratique pour TikTok, Instagram Reels et YouTube Shorts : situations vécues, expressions utiles, erreurs fréquentes et quiz. Le public est mixte, notamment adulte et professionnel. Le ton est direct, chaleureux et encourageant ; les phrases restent courtes et le spectateur est tutoyé.

La première version demandée est un prototype visuel SANS MASCOTTE. Ne crée, n’importe et n’affiche aucun renard, avatar ou personnage de remplacement. La création 3D et les animations Blender ne font pas partie de cette mission immédiate. Tes compétences 3D restent utiles pour de futures demandes, mais elles ne doivent pas détourner ce premier test de son objectif : valider la présentation et les animations des leçons.

Le projet est en PHASE DE TEST. Le scénario « Make ou do ? » fourni sert à éprouver le système visuel ; il ne constitue pas une première publication approuvée. Aucun lancement de vidéo réelle, aucune publication et aucune création de suivi Excel ne sont demandés à ce stade.

## 2. Sources à lire intégralement avant d’agir

Racine du projet : D:/ai-generation-video.

Lis d’abord les éventuelles consignes AGENTS.md applicables, puis PROJET.md, package.json, src/index.ts et src/Root.tsx. Examine le code existant pour comprendre ce qui fonctionne déjà. Le prototype RestaurantQuiz et ses anciens choix graphiques ne sont pas la nouvelle référence.

La référence graphique principale est :
D:/ai-generation-video/docs/design/palette-design-video-tiktok.md

C’est une copie fidèle du document utilisateur, également disponible dans :
C:/Users/Hami/Downloads/palette-design-video-tiktok.md

Analyse le document ENTIER : format et unités, identité, couleurs, typographie, formes, composants, SVG, zones sûres, textes, storyboard, positions, minutage, courbes de mouvement et contrôle avant export. Ne te contente pas d’en extraire quelques couleurs.

Ordre de priorité : consignes explicites actuelles de l’utilisateur, puis référence graphique pour le périmètre applicable, puis historique. L’absence de mascotte prévaut sur toutes les parties du document qui en demandent une. Les anciens choix crème/sauge et les références Blender ne doivent pas réintroduire une autre charte dans le test.

Crée une courte synthèse de cette analyse dans docs/remotion-design-system.md : règles retenues, exceptions nécessaires, adaptations sans mascotte et points à vérifier. Préserve la copie originale de la charte ; ne la réécris pas silencieusement pour justifier tes choix.

## 3. Un seul projet Remotion durable

Nous voulons UN SEUL projet global, contenant les tests et, plus tard, les vidéos validées. Il existe déjà une installation Remotion à la racine. Réutilise-la et fais évoluer son architecture ; ne lance pas un nouveau projet, un nouveau package.json ou une nouvelle installation pour chaque vidéo.

Organise le code autour de trois niveaux :
- Le système commun : couleurs, typographie, espacements, formes, mouvements, composants et modèles de séquences.
- Les expériences : une composition de test et ses données/scènes, clairement identifiées comme non validées.
- Les épisodes : seulement après validation explicite, des dossiers par vidéo contenant leurs données et ressources spécifiques, dans le même projet.

Exemple d’organisation à adapter sans surarchitecture :
src/design/ : tokens.ts, typography.ts, motion.ts
src/components/ : feuille, tag, phrase à trou, options, minuteur, pastilles, carte de fin, décor
src/templates/ : scènes ou séquences réutilisables
src/archive/experiments/test-style-v1/ : composition et données du prototype
src/videos/<identifiant-video>/ : épisodes futurs, après validation
public/ : ressources partagées et ressources propres aux épisodes
output/tests/ : rendus des expériences
output/videos/<identifiant-video>/ : rendus futurs

Ce sont des dossiers du même projet, pas des projets autonomes. Les composants communs ne doivent pas être recopiés dans chaque épisode. Le contenu pédagogique, le thème, les choix, la réponse, les traductions et les durées doivent être séparables de la présentation au moyen de données TypeScript typées.

Pour ce premier test, évite de construire un moteur universel : un modèle de vidéo bien structuré et ses composants utiles suffisent. Conserve l’existant pour l’historique sans le traiter comme validé. Ne modifie pas les fichiers Blender.

## 4. Charte graphique à implémenter précisément

Définis des tokens centralisés et utilise-les réellement dans les composants. Les valeurs complètes du document font foi. Repères principaux :
- ink #1E1B3A : texte et contours ; ink2 #3A3654 ; inkMuted #5E5A72 ; onInk #FFFFFF.
- sheet #FFFDF8 ; surface #FFFFFF.
- violet #6A3FD1 : traductions françaises et sous-titres d’astuce.
- coral #FF6F59 : accent décoratif, trou pointillé et arc du minuteur ; jamais pour porter du texte.
- success #137A4B sur successBg #D4F5E3, TOUJOURS accompagné d’une coche.
- Fonds : lavande #A99BFF pour les scènes 1 à 4, citron #FFD84D pour l’astuce, menthe #6FD6AE pour la fin.
- Baloo 2 ExtraBold, graisse 800, pour les grands textes ; Nunito pour le reste, avec les graisses et tailles prévues par la charte. Charger réellement les polices et les accents, sans remplacement silencieux par une police système.
- Feuille crème aux coins supérieurs arrondis, formes rondes et rebords durs sans flou.
- Reprendre les rayons, bordures, espacements, tailles, icônes SVG et états des options du document.
- Aucun dégradé, emoji ou ombre floue. Aucun effet ajouté uniquement pour remplir l’écran.

Le document utilise une scène logique de 360 × 640, où 1u = 3 pixels à l’export. Choisis une méthode cohérente, par exemple une mise à l’échelle globale ×3. Ne multiplie pas deux fois les mesures ; « u » est une unité de conception, pas une unité CSS valide à recopier littéralement.

Les règles graphiques communes doivent se trouver dans le code partagé, pas seulement dans un fichier de notes ou une composition monolithique.

## 5. Adapter le storyboard à une version sans mascotte

Conserve la logique pédagogique et visuelle : accroche → question → temps de réflexion → réponse → astuce → fin.

Le prototype de référence dure 16 secondes, soit 480 frames à 30 images/seconde, en 1080 × 1920 :
- Accroche : frames 0–59.
- Question : 60–149.
- Réflexion : 150–239.
- Réponse : 240–299.
- Astuce : 300–419.
- Fin : 420–479.

Ce minutage concerne ce test ; ne le rends pas obligatoire pour tous les épisodes futurs.

Supprime le SVG du renard, ses poses, ses animations et ses bulles de dialogue. Ne conserve pas de grands espaces vides à leur emplacement : rééquilibre la composition avec la typographie, la feuille, le minuteur, les options et le décor prévu, sans encombrer l’écran ni inventer une nouvelle identité graphique.

Adapte les textes dépendant de la mascotte :
- « Réponds avant le renard. » devient, pour ce test, « Tu as 3 secondes. ».
- « Abonne-toi, le renard revient demain. » devient « Abonne-toi pour le prochain piège. ».
- Ne conserve pas les répliques de la mascotte comme des bulles orphelines.

Conserve les autres contenus utiles : « Can you ___ me a favor? », traduction, choix make/do/give, bonne réponse do, feedback encourageant, astuce et annonce « say ou tell ? ». Vérifie le sens pédagogique : l’astuce do/make est un repère simplifié, pas une règle universelle.

La couverture peut être testée si elle aide à évaluer le style. La photo de profil et toute illustration de mascotte sont hors du premier livrable. Les éléments de type bouton sont des éléments visuels dans une vidéo, pas des contrôles cliquables.

## 6. Motion design et rigueur Remotion

Construis toutes les animations à partir du temps de la composition et de la frame : entrée des textes, stagger, feuille, respiration du trou, arc et chiffres du minuteur, mot qui tombe, réussite, transitions et cloche. Les rendus doivent être reproductibles, indépendamment du moment où une frame est calculée. Pas de setTimeout, d’horloge réelle ou d’animations CSS autonomes pour piloter la timeline ; tout aléatoire éventuel doit être déterministe.

Respecte les timings et courbes du document lorsque les éléments sont conservés. Distingue les courbes nommées « spring » dans la charte des fonctions Remotion : vérifie l’API et les imports de la version installée plutôt que de recopier aveuglément les exemples. Centralise les réglages de mouvement.

Une seule animation principale attire l’attention à la fois ; les éléments secondaires restent discrets. Réserve les rebonds aux événements marquants. Pas de flou de mouvement, de rotation des textes ou d’effet machine à écrire. Chaque texte doit rester lisible au moins une seconde après son entrée ; vérifie aussi si son volume nécessite davantage.

La transition accroche/question réorganise la même carte ; les transitions vers l’astuce et la fin sont des swipes verticaux de cartes complètes. Évite les ruptures, superpositions, flashs et sorties de cadre involontaires.

La version initiale peut être sans narration. Ne réutilise pas automatiquement la voix Windows rejetée. Les petits sons éventuels doivent rester discrets et provenir de ressources utilisables ; ne lance pas de service payant sans demande explicite.

## 7. Lisibilité et zones sûres

Respecte les zones définies dans la charte pour ce test, puis vérifie les aperçus destinés aux autres plateformes sans supposer que leurs interfaces sont identiques. Contrôle les limites à chaque instant de l’animation, pas seulement sur les poses finales.

Le document présente une petite contradiction : la zone droite réservée commence à x=300u sous y=290u, alors que la largeur proposée de 284u depuis x=20u atteint x=304u. Pour protéger les textes et réponses, utilise la limite la plus prudente x=300u dans cette bande, adapte localement la largeur si nécessaire et documente cet écart. Ne déforme pas toute la composition pour le masquer.

Vérifie les blocs réels : longues traductions, retours à la ligne, accents, contours, rebords et transitions. Ne réduis pas systématiquement les polices pour faire rentrer un contenu trop long. Préfère un retour à la ligne ou une adaptation locale cohérente.

## 8. Méthode de travail et validation

Commence par une lecture attentive des sources et une synthèse courte des règles et exceptions. Puis implémente directement un prototype animé concret ; ne transforme pas la phase de test en une longue succession de plans ou de demandes de confirmation sur des détails routiniers.

Produis une composition de test clairement identifiable, des captures aux moments clés et un MP4 de test H.264 en 1080 × 1920 à 30 images/seconde. Vérifie le typage et les vérifications réellement pertinentes. Inspecte les rendus visuels et la lecture temporelle avant de livrer ; un contrôle TypeScript réussi ne valide pas un design. Si l’aperçu animé ne peut pas être vérifié, indique clairement cette limite.

Vérifie notamment : conformité des couleurs et polices, absence totale de mascotte, tailles et reliefs, zones sûres, coche visible, minuteur cohérent, fluidité des swipes, absence de coupures et temps de lecture. Corrige les défauts visibles dans le périmètre du test.

Documente dans docs/remotion-tests.md les choix techniques, rendus disponibles, problèmes restants, retours utilisateur et éléments réellement validés. Ne présente pas une proposition comme approuvée parce qu’elle est exportée ou parce que ses contrôles techniques réussissent.

Reste en phase de test jusqu’à ce que l’utilisateur dise explicitement que le style est validé et que nous pouvons passer à une vidéo réelle. À ce moment-là seulement, conserve le système validé et crée un dossier d’épisode dans ce même projet, avec ses données, médias et sorties propres. N’impose pas de recommencer le projet à chaque vidéo.

## 9. Livraison attendue

Fournis le prototype visionnable, les captures utiles, les chemins des fichiers créés et les instructions simples pour rouvrir l’aperçu et relancer le rendu. Explique brièvement ce qui respecte la charte et ce qui a été adapté pour retirer la mascotte. Signale les décisions artistiques encore à valider.

La réussite n’est pas d’accumuler les effets : c’est de créer une vidéo claire et attractive, fidèle à la charte, puis une base maintenable pour produire les prochains épisodes. Pour l’instant, ta mission est exclusivement ce test Remotion sans mascotte.
