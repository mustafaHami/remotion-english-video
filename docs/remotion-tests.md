> Historique des essais. Les règles actives validées le 21/10/2026 sont dans `AGENTS.md`, `README.md` et `docs/production.md`. Les mentions anciennes « sans mascotte » ou « uniquement en test » ci-dessous ne pilotent plus la production.

# Tests Remotion — TestStyleV1

## Statut — 17 octobre 2026

Prototype sans mascotte proposé à l'utilisateur. **Style non validé ; aucune vidéo réelle lancée, aucun épisode, aucune publication, aucun suivi Excel.** Installation Remotion unique conservée. Ancien RestaurantQuiz disponible sous Historique ; fichiers Blender et ancienne voix inchangés.

## Livrables et organisation

- Composition : `TestStyleV1`, dans `Tests-non-valides`.
- MP4 : `output/tests/test-style-v1/test-style-v1.mp4`.
- Douze captures PNG : `output/tests/test-style-v1/captures/` (frames 30, 105, 175, 200, 230, 270, 307, 314, 375, 427, 450, 479).
- Planche : `output/tests/test-style-v1/planche-style-v1.jpg`.
- Mesures de mise en page : `output/tests/test-style-v1/layout-qa.json`.
- Métadonnées vidéo et planches de contrôle temporel : `output/tests/test-style-v1/qa/`.
- Règles retenues et adaptations : `docs/remotion-design-system.md` ; charte originale préservée.
- Tokens/typographie/mouvement : `src/design/`. Composants : `src/components/`. Modèle : `src/templates/GapQuiz.tsx`. Données typées et composition de test : `src/archive/experiments/test-style-v1/`.

## Choix techniques

Remotion 4.0.534 existant, React/TypeScript. Scène 360 × 640 agrandie ×3. Export H.264, 1080 × 1920, 30 i/s, 480 frames, 16 secondes, Rec.709, CRF18. Aucun audio dans cet essai. Polices variables Baloo 2 et Nunito officielles, locales, avec licences OFL et chargement bloquant ; aucune dépendance ajoutée. Types DOM.Iterable activés pour FontFaceSet.

Tout mouvement dépend de la frame. Les courbes « spring » et « bounce » du document sont des Bézier pour les entrées ; les swipes utilisent réellement `spring()` et ses paramètres vérifiés dans les types de la version installée. Les transitions déplacent le fond, la feuille et les contenus ensemble, avec un masque fixe des zones sûres pour les textes. Pas d'animation CSS autonome, aléatoire, horloge, flou, dégradé ou rotation typographique.

Le modèle est volontairement spécifique à ce format de test. Les contenus, choix, traductions, exemples et principales bornes temporelles sont typés et séparés. Les décalages fins d'entrée restent dans le modèle ; changer fortement la durée demandera une adaptation de sa timeline, sans recréer le projet.

## Contrôles et corrections

- `npm run check` : typage réussi.
- Rendu réel des 480 frames, plus captures en pleine résolution.
- MP4 final contrôlé par ffprobe puis décodé intégralement : H.264, 1080 × 1920, 30/1 i/s, 480 images, 16,000 s, yuv420p, bt709, plage vidéo TV ; 1 361 799 octets. Planches de contrôle construites depuis ce MP4, pas depuis une simulation séparée.
- Sonde DOM : 478 frames mesurées, chargement des deux polices confirmé, aucun débordement ou chevauchement de blocs détecté. Les frames 0–1 ne sont pas mesurées par la sonde (initialisation des polices) ; le rendu attend leur chargement. Les swipes sont contrôlés par masque et revue visuelle, pas par comparaison des boîtes hors écran.
- Captures inspectées : accroche, question, 3/2/1, réponse verte et coche, astuce, fin. Déclaration CSS de Baloo 2 corrigée après détection d'une police de secours. Note pédagogique repositionnée pour éliminer un chevauchement avec la dernière pastille.
- Vérification des mouvements : réorganisation de la carte, chute de « do », swipes et cloche revus sur des planches d'images décodées du MP4, frame par frame autour des transitions. Cette méthode ne constitue pas une lecture humaine continue à vitesse réelle dans un lecteur ; le rythme ressenti reste à évaluer avec l'utilisateur sur le MP4 livré.
- Textes : retours à la ligne locaux plutôt que réduction générale des tailles. Bonne réponse do ; do a favor est correct. Repère do/action et make/création explicitement présenté comme simplifié.
- Sécurité : x≤300 sous y=290 ; options rentrées pour leur rebond. Fin avancée pour que la carte reste posée plus d'une seconde. Les zones correspondent à la charte fournie pour TikTok ; pas de certification en situation dans les interfaces Reels/Shorts.

## Reprendre l'aperçu et rendre

Depuis `D:\ai-generation-video` :

1. `npm run dev`, puis ouvrir `http://localhost:3000/TestStyleV1`.
2. `npm run check` pour vérifier les types.
3. `npm run render:test` pour régénérer les captures et le MP4. Le navigateur Chromium local doit pouvoir communiquer avec le serveur local ; un environnement restreint peut nécessiter l'autorisation d'exécution correspondante.
4. `npm run stills:test` pour les captures seules.
5. `python scripts/inspect-style-video.py` pour vérifier le MP4 et reconstruire les planches de contrôle (Pillow déjà disponible ; outils vidéo fournis avec Remotion).

Ne pas utiliser `npm run render` pour cet essai : cette commande historique cible encore RestaurantQuiz.

## Retours et décisions en attente

Aucun retour reçu sur TestStyleV1. À valider explicitement : direction graphique globale, densité et tailles, rythme des 16 secondes, adaptation sans mascotte, place de la nuance pédagogique, puis traitement audio éventuel. L'export et la réussite des contrôles techniques n'approuvent pas le style. Les futurs dossiers d'épisodes resteront dans ce même projet après validation explicite.

## Retour utilisateur et test v2 — 17 octobre 2026

L'utilisateur apprécie la base v1, demande davantage de design, les textes sur une ligne et une recherche sur l'apprentissage/l'attention, incluant TikTok, Instagram, Reddit, X et Facebook. Ce retour n'autorise pas le lancement d'une vidéo réelle. Recherche et proposition argumentée dans recherche-attention-apprentissage-v2.md, avec distinction entre études, recommandations des plateformes et témoignages ; accès public insuffisant sur X et groupes Facebook.

Deux MP4 H.264 Rec.709, 1080 × 1920, 30 i/s, 22 secondes (660 frames), sans audio :

- output/tests/test-style-v2-tiktok/test-style-v2-tiktok.mp4
- output/tests/test-style-v2-instagram/test-style-v2-instagram.mp4

Chaque dossier contient 12 captures pleine résolution, une planche planche-test-style-v2-<plateforme>.jpg, layout-qa.json, un aperçu schématique apercu-zones-sures.jpg et les métadonnées/planches de mouvements dans qa/. Les rendus sont des expériences du même projet.

Contrôles : typage réussi ; 660 frames mesurées par variante, aucun débordement ou chevauchement de blocs détecté, polices chargées. La sonde attend désormais les polices avant de mesurer les premières frames. Décodage complet des deux MP4 : H.264, yuv420p, bt709, 30/1, 660 frames, 22 s. Captures des phrases, de la réponse, des deux duos, du nouvel essai et des mémos inspectées ; swipes et corrections revus sur planches décodées. Les textes sont effectivement sur une ligne, sans scaleX. Le premier contour de fiche était coupé par le masque ; fiche ramenée à 280u avant les exports finaux.

Lecture temporelle contrôlée par frames autour des événements ; pas de lecture humaine continue à vitesse réelle attestée. Aucun résultat réel de rétention, d'apprentissage ou de plateforme n'est disponible. Aucun test sur compte publié, aucun accès aux interfaces connectées TikTok/Instagram et aucun suivi Excel. Les aperçus des zones sûres sont des schémas de contrôle, pas des captures d'applications.

Relancer : npm run render:test:v2:tiktok ou npm run render:test:v2:instagram. Aperçus : http://localhost:3000/TestStyleV2-TikTok et http://localhost:3000/TestStyleV2-Instagram après npm run dev. Inspecter : python scripts/inspect-style-video.py --variant=tiktok (ou instagram).

À valider : direction « fiche de poche », titres et phrase sur une ligne, contraste plus marqué, rythme de 22 s, intérêt du nouvel essai et des accroches distinctes. Nom du concept et audio restent des propositions. Aucune validation finale du style.

## Classement des 14 idées et derniers retours

L'utilisateur apprécie la logique de la v2, mais juge le second exercice encombrant, les trois secondes trop rapides, la carte insuffisamment allongée et la hiérarchie trop chargée en titres/tags. Il demande une présentation plus propre et visuelle, avec un foyer d'attention clair et une meilleure utilisation de la largeur. Un exercice par vidéo, deux au maximum ; varier les formats. Couleurs, boutons et fontes demeurent les repères, les autres détails de la charte sont une inspiration adaptable.

Catalogue : output/tests/README.md. Dossiers test-option-1 à test-option-14 avec un exemple concret chacun. Les anciennes idées 5 et 9 sont fusionnées sous « anglais en situation » (option 5). Les verbes à particule constituent l'option 14. Les trois références visuelles utilisateur sont associées aux options 1–3. Les exports v2 existants sont copiés dans l'option 4 comme références antérieures à ces retours ; les sources et leurs liens restent conservés.

Choix explicite : « Un dossier par idée, puis tester les idées une à une ». Les fiches sont préparées pour ces futurs essais ; aucun lot de 14 vidéos n'a été créé. Le classement ne valide aucun prototype supplémentaire et ne déclenche aucune publication.

## Option 1 — premier prototype de conjugaison

Périmètre explicitement limité par l'utilisateur à l'option 1 afin d'évaluer le design, les cartes, les boutons, les fontes, les couleurs et le style. Aucune nouvelle vidéo créée pour les options 2–14.

Composition TestOption1 : 1080 × 1920, 30 i/s, 870 frames, 29 s. Sortie output/options/option-1/test-option-1.mp4, accompagnée de 12 captures, planche et contrôles dans le même dossier. Silencieux pour cet essai. Modèle TenseWorksheet, données typées optionOne, composant partagé WrittenText et stylo SVG. Nunito 800 réellement vectorisée, sans substitution de police ; tracés et position du stylo calculés uniquement depuis la frame et des chemins précalculés.

Les trois formes initiales sont I am, I do, I have. Passé : I was, I did, I had. Futur : I will be, I will do, I will have. Deux pauses de cinq secondes (frames 30–179 et 390–539), écriture séquentielle des six réponses, tableau complet maintenu plus de quatre secondes. Repère final explicitement limité à ce tableau : « Le futur ici : will + verbe. »

Contrôles réalisés : npm run check réussi ; captures des étapes clés inspectées et 12 captures pleine résolution livrées ; sonde de mise en page sur les 870 frames, aucune erreur de débordement ou de chevauchement détectée, deux polices chargées. Export contrôlé puis intégralement décodé : H.264, 1080 × 1920, 30/1 i/s, 870 images, 29 s, yuv420p, Rec.709. Le trait partiel et le stylo sont contrôlés dans les séquences de frames décodées. Les zones mobiles restent une convention conservatrice issue de la charte, pas une capture d'interface actuelle. Le rythme ressenti à vitesse réelle reste à évaluer avec l'utilisateur ; aucune lecture humaine continue n'est attestée.

Reproduction : npm run render:option:1 ; captures seules : npm run stills:option:1. Aperçu : npm run dev puis http://localhost:3000/TestOption1. Inspection de l'export : python scripts/inspect-style-video.py --option=1. Les captures seules n'écrasent plus le rapport du rendu complet.

À valider : dimensions de la fiche, hiérarchie épurée, taille des mots, contraste des onglets, rendu et vitesse du stylo, durée des pauses et durée totale. Le prototype ne vaut pas validation du système graphique. La production des autres options attend cette étape.

## Option 1 — révision dix verbes et centrage

Retour utilisateur : agrandir la fiche, proposer au minimum dix mots, supprimer le vide à droite et centrer les colonnes, les pastilles et le guide inférieur. Cette révision remplace le tableau à trois verbes pour la validation en cours. Le premier rendu et ses contrôles sont conservés dans output/options/option-1/archive-v1/.

Livraison : output/options/option-1/test-option-1-v2.mp4, 53 secondes, 1 590 images à 30 i/s, 1080 × 1920, H.264, sans audio. Dix verbes : be, do, have, go, see, take, eat, write, play, watch. Deux pauses de cinq secondes précèdent les écritures séquentielles ; le tableau complet reste visible plus de six secondes. Carte élargie et agrandie, trois colonnes strictement égales, textes centrés selon leurs contours visibles, titre et guide inférieur centrés sur le cadre entier. La réservation latérale TikTok du premier essai est retirée pour cette comparaison graphique ; la projection mobile reste schématique et ne certifie pas une interface publiée.

Contrôles réalisés : typage réussi ; rendu des 1 590 images, zéro violation de mise en page ; écart maximal de centrage mesuré de 0,054 pixel au format final. Export décodé intégralement et métadonnées vérifiées : 1 590 images, 53 secondes, 1 598 382 octets. Un contrôle de présence des textes sur le MP4 couvre 30 910 cellules déjà complétées au fil des images : aucune disparition, ratio minimal d'encre conservée de 89,74 %. Rapports dans layout-qa-v2.json et qa-v2/visibility-qa.json.

Une disparition des réponses précédentes pendant l'écriture a été observée sur un premier export de cette révision, puis corrigée avant livraison : chaque mot terminé est désormais une image SVG autonome, isolée des masques SVG de l'écriture active. Les captures et les planches issues du MP4 corrigé ont été inspectées, notamment pendant la première réponse et la dernière ligne. Le contrôle par images ne constitue pas une lecture humaine continue à vitesse réelle ; le rythme ressenti et le design restent à valider par l'utilisateur. Les options 2–14 restent en attente.

Reproduction inchangée : npm run render:option:1 ; npm run stills:option:1 ; python scripts/inspect-style-video.py --option=1. Les données et la configuration de rendu se trouvent dans src/archive/experiments/test-option-1/rows.json et render-config.json.

## Suite autorisée — prototypes des options 2 à 14

Retour utilisateur : « Pour cette partie, ça m’a l’air assez propre. On peut continuer pour les autres vues. » La V2 de l’option 1 est donc la base graphique retenue pour cette déclinaison. Les autres formats restent à évaluer individuellement ; aucune publication ni création d’épisode réel n’est autorisée. Le MP4 de l’option 1 est conservé.

Treize nouveaux MP4 sont livrés dans output/tests/test-option-N/test-option-N.mp4, avec six captures pleine résolution chacun, une planche issue de l’export, un rapport de mise en page et des métadonnées/planches de mouvements dans qa/. Galerie locale autonome : output/tests/index.html ; catalogue : output/tests/README.md ; vue d’ensemble : apercu-14-options.jpg. Les anciennes références de l’option 4 sont conservées.

| Option | Présentation | Durée |
| --- | --- | --- |
| 2 | To be : sept pronoms et flèches progressives | 30 s |
| 3 | Dix paires d’opposés, une ligne active | 37 s |
| 4 | Can you do me a favor? Deux choix, un seul exercice | 22 s |
| 5 | Restaurant : demander l’addition | 24 s |
| 6 | Say/tell : deux constructions et destinataire | 27 s |
| 7 | Associations de mots qui se rejoignent | 27 s |
| 8 | Retirer am, fermer l’espace, confirmer I agree. | 20 s |
| 9 | Deux bulles de mini-dialogue sans personnage | 23 s |
| 10 | Écoute, répétition, seconde écoute | 22 s |
| 11 | Retrouver une phrase sans choix | 20 s |
| 12 | Transfert facultatif : do my homework | 28 s |
| 13 | Mémo de deux expressions avec objets SVG | 24 s |
| 14 | Get off the bus : mot ajouté et flèche de sortie | 25 s |

Architecture : mêmes tokens et polices locales ; OptionPrimitives fournit la fiche, les textes, pastilles, flèches, pauses et objets. OptionBoards, OptionExercises et OptionListening organisent les vues ; données et configuration dans src/archive/experiments/options. Aucun nouveau projet, aucune mascotte, aucune modification Blender. Les instructions et boutons sont des éléments visuels de vidéo. Les pauses de recherche durent cinq à sept secondes ; pas de second exercice systématique. Le tableau à dix verbes ne devient pas une obligation artificielle de dix éléments pour chaque format à une phrase.

Contrôles effectivement réalisés : typage réussi ; 9 870 images des nouveaux rendus mesurées, zéro violation de mise en page ou de chargement de police. Centre des blocs communs mesuré à x=180u, écart maximal enregistré nul à la précision DOM de ce contrôle. Treize MP4 H.264, 1080 × 1920, 30/1 i/s, yuv420p et bt709 ; tous décodés intégralement. Durée cumulée 329 secondes, 8 483 006 octets. Synthèse dans output/tests/options-render-summary.json et qa/inspection.json de chaque option.

Corrections après inspection des captures : en-têtes et pronoms de l’option 2 réalignés ; signes + masqués avant leur entrée dans les options 7 et 14 ; coche replacée à côté du texte ; phrase redondante retirée de l’option 4 ; liaison de told me remontée pour ne pas traverser la traduction. La revue des mouvements de l’option 8 a ensuite révélé un changement trop brusque de phrase : retrait du mot, fermeture de l’espace et arrivée de la coche sont maintenant continus. Rendu de cette seule option régénéré puis décodé ; 120 images de transition contrôlées par pixels, aucune image sans phrase, ratio d’encre minimal 93,59 % de la référence. Les planches d’étapes de tous les nouveaux formats et la transition corrigée ont été inspectées visuellement.

Audio de l’option 10 : un fichier de 2,04 secondes, phrase The bill, please., voix synthétique provisoire en-GB-SoniaNeural à −10 %, générée avec edge-tts dans le cache local. Aucun service payant utilisé et aucune voix Windows Zira réutilisée. Les enregistrements Tatoeba envisagés n’ont pas été intégrés : les métadonnées indiquaient CC BY-NC-ND 3.0 ; pages de recherche conservées dans qa/audio-research. Le fichier généré et sa provenance sont dans public/audio/options. Deux lectures à 3s et 14s ; onde calculée depuis les échantillons décodés, pas une décoration aléatoire. Piste AAC du MP4 vérifiée : RMS des deux écoutes ≈0,049, silence de 7s à 14s mesuré à zéro, pic ≈0,335, pas d’écrêtage. Aucune écoute humaine attestée ; qualité de prononciation et voix finale restent à apprécier par l’utilisateur.

Limites de validation : revue temporelle par images décodées, sans lecture humaine continue à vitesse réelle. Aucun résultat de rétention, test d’apprentissage ou essai dans une interface mobile publiée. Le centrage sur le cadre entier reprend la décision de l’option 1 ; les contrôles ne certifient pas les surimpressions actuelles de TikTok/Reels. Le style commun est retenu pour poursuivre les tests, pas pour déduire que les treize nouvelles vues sont approuvées.

Reproduction : npm run render:options ; une seule vue : npm run render:options -- --options=8 ; captures seules : npm run stills:options ; inspection des MP4 : npm run inspect:options ; reconstruire la galerie : python scripts/build-options-catalog.py. Les rendus ordinaires utilisent seulement le fichier audio local et ne contactent pas de service vocal. Pour voir la galerie dans un navigateur : ouvrir index.html ou servir output/tests avec python -m http.server 3011 --bind 127.0.0.1 --directory output/tests. Un serveur local a été lancé en arrière-plan pour l’aperçu dans l’application ; son PID est conservé dans .npm-cache/options-preview.pid.

## V3 — davantage d’exemples, durée et prononciation

Nouveau retour : l’option 2 est trop lente pour une notion simple ; garder un seul verbe par vidéo et décliner be, have, can et could. Les formats courts doivent durer au moins 35–40 secondes avec deux à trois exemples ; le dialogue doit être plus développé. L’utilisateur demande aussi d’entendre les mots et les formes conjuguées. Ces instructions remplacent le précédent plafond de deux exercices dans cette phase de test. La durée demandée est un choix éditorial utilisateur, pas une règle générale des plateformes.

Livraison réelle : 17 nouveaux MP4 dans les mêmes quatorze dossiers. Les fichiers antérieurs sont conservés. V3 principale : test-option-N-v3.mp4 ; trois déclinaisons supplémentaires dans test-option-2 : test-option-2-v3-have.mp4, test-option-2-v3-can.mp4 et test-option-2-v3-could.mp4. Galerie : output/tests/index-v3.html et index.html ; ancienne galerie conservée dans index-v2.html. Catalogue : catalogue-v3.md, README.md et en-tête V3 de chaque dossier. Six captures pleine résolution, une planche issue du MP4 et un dossier qa-v3 (ou qa-v3-have/can/could) accompagnent chaque vidéo.

Durées : 65 secondes pour le tableau à dix verbes (option 1), 43 secondes pour les dix opposés (option 3), 42 secondes pour les quinze autres exports. Les quatre verbes de l’option 2 ont chacun un tableau plus rapide (48 frames entre les formes, première forme à 2s) puis trois phrases d’usage. Can/could restent des modaux sans infinitif en to ; could est ici limité à la capacité passée. Trois exemples se succèdent dans les formats courts. Le dialogue comprend huit répliques en quatre paires, soit 42 secondes. L’option 12 garde un modèle puis deux essais. Les verbes à particule présentent get off the bus, pick up a bag et go down the stairs, une expression par carte.

Voix : 120 placements de prononciation à partir de 105 clips WAV uniques, voix neuronale provisoire en-GB-SoniaNeural à −5 %. Les clips sont générés une fois puis conservés localement dans public/audio/options-v3 avec provenance, durées et empreintes. Aucun nouvel accès utilisateur ni service payant nécessaire pour ces essais ; aucun choix de voix définitif n’est déduit de leur création. Les fichiers sources sont à 24 kHz, mono, PCM 16 bits ; seule la marge silencieuse autour des paroles est raccourcie, avec 150 ms conservées de chaque côté des blocs audibles. Les rendus ordinaires ne contactent aucun service de synthèse.

Synchronisation : cinq secondes de recherche avant la révélation des quiz, puis lecture de la bonne phrase ; aucune lecture des formulations incorrectes. Le tableau fait entendre les paires présent/passé puis les futurs. Les associations et verbes à particule sont prononcés, puis repris dans une phrase. Le dialogue laisse finir chaque enregistrement avant le fondu de sa carte. L’option 10 fait entendre trois phrases, chacune deux fois, avec 160 frames de répétition silencieuse (5,33 secondes) entre ses deux écoutes.

Contrôles effectués : typage réussi ; 22 140 images mesurées, zéro violation de mise en page ou de chargement des polices. Écart maximal de centrage enregistré : 0,054 pixel au format final. Les dix-sept MP4 sont H.264, 1080 × 1920, 30 i/s, yuv420p, bt709, avec une piste AAC ; vidéo et audio intégralement décodés. Cumul : 738 secondes, 49 948 391 octets. Les 120 fenêtres de prononciation contiennent du signal, les fenêtres de pause sont contrôlées, ainsi que les trois silences de répétition et la fin des huit répliques avant transition. Pic audio maximal : 0,40762, sans écrêtage. Synthèse : options-v3-summary.json ; mesures détaillées et métadonnées dans les dossiers qa-v3*.

Corrections pendant la revue : espace entre traduction et exemple du mémo augmenté après collision détectée ; taille de deux phrases longues de could adaptée localement à 26u ; captures finales choisies pour montrer les huit répliques et les dernières réponses. Un problème de lecture CP1252 des JSON UTF-8 a ensuite été détecté visuellement dans le titre des opposés et dans le texte de quatre contractions envoyé à la voix. Tous les nouveaux scripts lisent explicitement en UTF-8 ; les apostrophes envoyées à la synthèse sont normalisées et les textes suspects bloquent la préparation. Les quatre clips concernés ont été régénérés, puis seules les six vidéos touchées par ces corrections ou l’ajustement de taille ont été réexportées et contrôlées. Les planches finales et transitions représentatives ont été inspectées après décodage.

Limites : aucune écoute humaine ni lecture humaine continue à vitesse réelle n’est attestée. Les contrôles audio vérifient le signal, les silences et le placement, pas une reconnaissance automatique des mots ni un jugement de timbre ou d’intonation. L’utilisateur doit encore apprécier la voix, la difficulté, les exemples et le rythme. Aucune vidéo publiée, aucun résultat de rétention ou d’apprentissage mesuré, aucune certification d’interface mobile ; le centrage sur le cadre entier de la base retenue est conservé.

Reproduction : npm run render:options:v3 ; une seule option : npm run render:options:v3 -- --options=5 ; une seule déclinaison : npm run render:options:v3 -- --keys=2-could ; captures : npm run stills:options:v3. Contrôle : npm run inspect:options:v3, ou python scripts/inspect-v3.py --keys=5. Galerie après contrôle : python scripts/build-v3-catalog.py. Préparation des données : python scripts/prepare-v3.py ; régénération facultative des lectures : python scripts/generate-v3-audio.py (utilise le cache local et nécessite le réseau seulement pour un clip absent). Les compositions et contenus V3 sont dans src/archive/experiments/options-v3, dans le même projet Remotion.
# Essais vocaux ciblés V4 — 17 octobre 2026

Demande utilisateur : deux interlocuteurs distincts dans l’option 9 ; une consigne parlée au début de l’option 4. Même projet, mêmes cartes, palette et polices ; aucune mascotte. Tests à valider par l’utilisateur.

- Option 4 : `output/options/option-4/test-option-4-v4.mp4`, 45 secondes. Denise (`fr-FR-DeniseNeural`) annonce « Quel verbe manque ? Choisis la bonne réponse. » à 0,2 seconde. Le premier temps de réflexion silencieux va de 5 à 10 secondes ; les deux suivants durent aussi cinq secondes. Sonia lit les trois réponses anglaises. La première carte est prolongée de trois secondes pour préserver le temps de réflexion.
- Option 9 : `output/options/option-9/test-option-9-v4.mp4`, 42 secondes. Sonia (`en-GB-SoniaNeural`) pour les répliques impaires, Ryan (`en-GB-RyanNeural`) pour les paires. Huit répliques, quatre cartes ; chaque voix reste attachée au même interlocuteur. Les clips finissent avant les transitions.

Ressources générées avec edge-tts, débit -5 %, volume Remotion 0,85 ; cinq nouveaux clips locaux, extraits Sonia réutilisés sans modification. Provenance dans `public/audio/options-v4/provenance.json`. Données et compositions dans `src/archive/experiments/options-v4`. Rendu : `npm run render:options:v4` ; vérification : `npm run inspect:options:v4`. Galerie `output/tests/index-v4.html` ; V3 préservée dans `index-v3.html`.

Vérifications effectuées : typage TypeScript réussi ; 2 610 frames mesurées, zéro erreur de mise en page et centrage exact ; décodage intégral vidéo/audio des deux MP4 H.264/AAC 1080 × 1920, 30 fps, BT.709. Les douze passages vocaux sont présents, sans chevauchement ni saturation (pics 0,293 / 0,403). Consigne audible dans la première seconde ; trois fenêtres de réflexion de cinq secondes silencieuses. Alternance Sonia/Ryan contrôlée dans le manifeste et fin de chaque réplique avant le fondu. Planches de captures inspectées visuellement. Pas d’écoute humaine ni de lecture animée subjective effectuée ; le naturel des voix reste à évaluer par l’utilisateur.

# Essais V5 avec mascotte — 18 octobre 2026

Demande utilisateur : exemples sur les options 1, 4 et 9 avec le renard fourni dans `C:/Users/Hami/Downloads/Planche de la mascotte-html`. Cette demande remplace l’exclusion historique de mascotte pour ces trois essais. Le README du dossier est traité comme documentation de référence, pas comme une nouvelle autorité sur le projet. Aucun code de son runtime HTML n’est exécuté ou importé. Les tracés SVG et couleurs du renard sont conservés ; les animations autonomes sont remplacées par des transformations déterministes calculées à chaque frame.

Ouverture de cinq secondes avec Denise en français et pose salut ; exercice existant conservé ; fin de sept secondes sur fond menthe, pastille « Bravo ! » avec coche et texte vert, renard en pose bravo puis salut. L’option 1 dure 77 secondes ; les options 4 et 9 durent 54 secondes. Option 4 conserve les trois phrases, dont « Can you do me a favor? », et cinq secondes de recherche silencieuse par phrase. La consigne est maintenant portée par l’ouverture, sans répétition. Option 9 conserve huit répliques avec Sonia et Ryan. Pas de renard superposé aux exercices afin de garder les réponses lisibles.

Compositions dans `src/archive/experiments/options-v5`, composant partagé `src/components/FoxMascot.tsx`. Voix d’accueil/fin locales dans `public/audio/options-v5`, extraits anglais existants réutilisés. Sorties `output/tests/test-option-N/test-option-N-v5.mp4` pour N=1,4,9 ; anciennes versions conservées. Galerie `output/tests/index-v5.html`. Préparation : `python scripts/prepare-v5.py` ; rendu : `node scripts/render-options.cjs --revision=5` ; inspection : `python scripts/inspect-v3.py --revision=5`. Toujours en phase de test, sans publication ni validation implicite.

Vérifications effectuées : typage réussi ; trois MP4 réellement rendus puis intégralement décodés en vidéo et audio, H.264/AAC 1080 × 1920, 30 fps, BT.709 ; 5 550 frames contrôlées sans erreur de mise en page, erreur maximale de centrage 0,054 pixel. Les 37 passages vocaux attendus sont présents, sans chevauchement ni saturation ; annonces audibles dans la première seconde, cinq secondes de réflexion silencieuse conservées pour chacune des trois phrases de l’option 4, alternance Sonia/Ryan et fins de répliques contrôlées pour l’option 9. Planches de captures des trois essais inspectées visuellement. Pas d’écoute humaine ni de lecture animée subjective effectuée. Premier export interrompu par une référence audio incorrecte : chemin corrigé, exports finaux et contrôles réussis ensuite.



## Option 4 rapide V6 - 18 octobre 2026

Retour utilisateur : rythme trop lent, raccourcir l'accroche et avancer au plus tard deux secondes apres la reponse. Essai limite a l'option 4 ; options 1 et 9 inchangees. V6 de 26,5 s (795 frames) contre 54 s pour V5 : accroche parlee de 2 s, trois cartes de 6,5 s, conclusion avec renard de 5 s. Chaque carte : presentation 1,5 s, recherche silencieuse 3 s, reponse 2 s exactement avant la carte suivante (ou la conclusion). Les trois phrases, les voix et le design sont conserves ; aucune prononciation coupee. Ce rythme court remplace le minimum historique de 35-40 s pour cet essai demande par l'utilisateur.

Rendu : output/options/option-4/test-option-4-v6.mp4. Anciennes versions preservees. Typage reussi ; 795 frames mesurees sans erreur de mise en page, centrage exact ; decodage integral H.264/AAC 1080 x 1920, 30 fps ; cinq passages vocaux presents et sans chevauchement, trois recherches silencieuses de trois secondes verifiees, pics audio sous 0,372. Planche de captures inspectee visuellement ; pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test. Relance : node scripts/render-options.cjs --revision=6 ; inspection : python scripts/inspect-v3.py --revision=6.


## Option 4 V7 - 33 secondes

Retour du 18 octobre 2026 : utilisateur satisfait du design et du rythme V6 ; demande trois secondes entre exercices et au moins 33 s. V7 uniquement pour option 4 : accroche 2 s, trois cartes de 8,5 s (presentation 1,5 s, recherche silencieuse 4 s, reponse 3 s), conclusion 5,5 s. Total exact 33 s. Ajustement du temps de recherche annonce a l'utilisateur pour atteindre la duree sans modifier le design. Composant FastGapLesson partage avec V6 ; anciens exports preserves, options 1/9 inchangees.

MP4 output/options/option-4/test-option-4-v7.mp4 rendu et integralement decode, H.264/AAC 1080 x 1920 30 fps, 990 frames. Typage reussi, zero erreur de mise en page, centrage exact ; cinq clips vocaux presents sans chevauchement ni coupure, trois pauses de recherche silencieuses verifiees et passage apres trois secondes de reponse. Captures inspectees visuellement. Pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test ; aucune publication.


## Option 3 V8 - renard original, 19 octobre 2026

Demande utilisateur : mettre a jour uniquement le test option 3 en tenant compte des derniers retours et remplacer le petit renard par celui de output/design/renard-expressions-v2-regard.png, avec les memes intentions de mouvement. Source examinee ; le renard 2D adulte avec echarpe sauge et yeux ambres est la reference, pas le modele Blender. Deux poses transparentes adaptees depuis cette reference via l'outil image_gen integre, preservees dans public/mascots/original-fox-v8/poses.png ; consigne de generation dans prompt.txt. Le fichier source est intact. Pas de pipeline CLI/API externe pour les images.

Animation 2D : avant-bras isole par masque SVG et rotation deterministe, legere respiration du corps, petit saut de satisfaction via Bookend ; pose pouce leve pour bravo, puis retour au coucou. Les poses sont des adaptations generees de l'illustration fournie, pas un rig 3D ni un export Blender. Composant OriginalFoxMascot reutilisable ; accueil et fin partages avec les essais precedents via un emplacement de mascotte parametrable.

Video de 42,5 s : accueil parle 2 s, tableau de dix paires 35 s (presentation 1 s, recherche silencieuse 4 s, puis une revelation toutes les 3 s), fin verte 5,5 s. Denise annonce l'exercice en francais, Sonia prononce les dix paires en anglais. Les dix mots et leurs opposes sont conserves ; pas de mascotte superposee aux reponses. Sortie output/options/option-3/test-option-3-v8.mp4. Anciennes versions et autres options preservees.

Verifications effectuees : typage reussi, 1275 frames mesurees sans erreur de mise en page, centrage exact ; MP4 H.264/AAC 1080 x 1920 30 fps BT.709 integralement decode ; douze passages vocaux presents, pas de chevauchement ou saturation (pic 0,408), recherche silencieuse et cadence de trois secondes controlees. Planches des scenes et de huit poses de mouvement decodees depuis le MP4 inspectees visuellement. Pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test. Relance : node scripts/render-options.cjs --revision=8 ; inspection : python scripts/inspect-v3.py --revision=8.


## Option 3 V9 - fleches et renard de face

Correction demandee le 19 octobre 2026 : symboles entre colonnes mal places et renard a presenter de face. Nouveau PairConnector : SVG symetrique de 34 x 18 u, centre local x=168 (global x=180), centre vertical de chaque ligne de 25 u ; apparition des deux pointes ensemble pour eviter un rendu temporairement unilateral. Le controle de mise en page mesure aussi l'alignement vertical des connecteurs visibles. Option V9 uniquement ; autres versions conservent leur rendu anterieur.

Renard de face prepare via image_gen integre depuis la reference originale et les poses V8 : tete et corps frontaux, regard direct, echarpe sauge et yeux ambres conserves. Deux poses transparentes dans public/mascots/original-fox-v9/poses-front.png, consigne dans prompt.txt. Nouveau FrontalFoxMascot : rotation d'avant-bras pilotee par frames, masque d'articulation, respiration et felicitation, puis au revoir. Chaque pose est isolee dans sa cellule SVG pour exclure tout fragment de la pose voisine. Images sources et V8 preservees.

Export effectif : output/options/option-3/test-option-3-v9.mp4, 42,5 s, rythme et voix identiques a V8. Typage reussi ; 1275 frames controlees, zero erreur de mise en page et centrage exact, alignement vertical des dix connecteurs valide. Decodage integral H.264/AAC 1080 x 1920, 30 fps, BT.709 ; douze voix presentes sans coupure ou chevauchement. Planches des scenes et de quatre positions du renard decodees depuis le MP4 inspectees visuellement. Pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test.


## Option 3 V10 - gestes localises, corps immobile

Retour utilisateur : le flottement vertical parait artificiel, seule la main doit saluer ; le pouce des felicitations doit agir au lieu de rester fixe. V10 reutilise exactement les images de face V9, sans nouvelle generation d'image. Mode refinedMotion : suppression du mouvement sinusoidal du corps ; salut limite et amorti au lieu d'une boucle continue ; geste du bras au pouce avec petite anticipation, montee, seconde impulsion discrete et retour. Le bras est articule a l'epaule, avec un masque ajuste pour preserver le torse et eviter les fragments.

Bookend staticMascot desactive le saut de la mascotte et les translations d'entree de sa carte : le corps reste en place des la premiere frame. L'arrivee de la conclusion reste verte, sans retour transitoire a la lavande. La main reprend le salut pour l'au revoir. Voix, dix paires, fleches centrees et duree de 42,5 s conserves. Anciennes versions et autres options preserves ; aucun changement de contenu pedagogique ni de source Blender.

Sortie : output/options/option-3/test-option-3-v10.mp4. Typage reussi ; mesures des 1275 frames sans erreur de mise en page, centrage exact ; decodage complet du MP4 H.264/AAC 1080 x 1920, 30 fps. Les douze clips vocaux sont presents sans chevauchement. Controle de stabilite pixel du visage et des pieds sur les 60 frames d'accueil et 90 frames de felicitations : ecarts moyens inferieurs a 0,05/255 (compression), corps fixe. Planches decodees des gestes inspectees visuellement. Pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test.


## Option 4 V11 - renard de face et gestes corriges

Demande utilisateur : mettre a jour et rendre l'option 4 avec les derniers ajustements du renard. FastGapLesson reutilise avec un parametre refinedMascot : accueil et fin avec FrontalFoxMascot refinedMotion, corps fixe, salut de la main, geste du pouce anime puis au revoir. Les trois phrases, dont Can you do me a favor?, les voix et le rythme V7 sont conserves : 33 secondes, recherche silencieuse de quatre secondes par phrase, reponse de trois secondes. Sources d'images V9 reutilisees sans nouvelle generation. Anciennes versions et autres options preservees.

Sortie : output/options/option-4/test-option-4-v11.mp4. Typage reussi, rendu effectif et decodage integral H.264/AAC 1080 x 1920 a 30 fps ; 990 frames mesurees, zero erreur de mise en page et centrage exact. Cinq passages vocaux presents sans coupure ou chevauchement ; trois recherches silencieuses et passage apres trois secondes de reponse controles. Planche de captures inspectee visuellement. Pas d'ecoute humaine ni de lecture animee subjective. Toujours en phase de test.
