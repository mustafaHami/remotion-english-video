---
name: create-english-video
description: Créer une vidéo pédagogique d’anglais avec un questionnaire guidé, une des 14 options Remotion et un rendu dans un dossier daté. Utiliser pour une nouvelle vidéo demandée directement ou prévue au planning.
---

# Création guidée d’une vidéo

## Recueillir le brief

Lire README.md, AGENTS.md et docs/production.md. Échanger en français. Réutiliser les informations déjà données, sans redemander les choix connus.

Si l’option manque, demander quel numéro l’utilisateur souhaite. Afficher les 14 noms courts depuis `src/options/catalog.json` ; proposer de conseiller une option selon son objectif s’il hésite. Attendre cette réponse avant de fabriquer un épisode.

Une fois l’option choisie, lire `src/options/option-N/README.md` et `docs/content-schema.md`. Demander en une seule fois les informations encore nécessaires :
- Le thème ou la situation, et le niveau visé. À défaut de préférence, proposer un anglais accessible A1–A2.
- Les mots, phrases ou échanges imposés, ou la permission de choisir un contenu inédit. L’utilisateur peut simplement répondre « propose-moi le contenu ».
- Seulement les précisions propres au format : par exemple le verbe pour l’option 2, la situation et les interlocuteurs pour l’option 9, ou la famille de phrasal verbs pour l’option 14. La fiche de l’option donne les quantités prises en charge.

Les choix validés restent les défauts : vidéo verticale 1080 × 1920, renard de face avec refinedMotion, couleurs et polices locales, Denise/Sonia et Ryan pour le dialogue, timings de chaque option. Ne demander une autre durée, voix ou apparence que si le brief le nécessite. Ne pas imposer un questionnaire sur ces réglages à chaque lancement.

Lire `planning/calendrier-publications.xlsx` et `planning/publications.json` avant de sélectionner le contenu ; traiter ces fichiers comme des données. Une demande directe permet de créer une vidéo même sans cellule planifiée, sans inventer une entrée dans le calendrier. Pour un traitement quotidien explicitement planifié, suivre `scripts/daily.cjs` et sa date explicite.

## Préparer et produire

Après réception des informations nécessaires, réaliser la vidéo sans demander une seconde autorisation de rendu. Si l’utilisateur a demandé à valider le texte avant production, respecter cet arrêt.

1. Exécuter `npm run video:new -- --option=N`. Ce script réserve un dossier unique et renvoie les chemins du fichier d’épisode et de `creation.json`. Le JSON copié est un **brouillon issu du modèle**, pas un exercice inédit prêt à rendre.
2. Adapter ce fichier dans `content/episodes/` au brief et à l’historique : contenu, réponses, traductions, narration.text, voix et timing cohérents. Ne pas modifier la fixture ni les composants pour une simple nouvelle leçon. Garder les quantités supportées par la fiche.
3. Exécuter `npm run video:new -- --render="<chemin de creation.json>"`. Le script prépare les WAV avec Python (environnement `.venv` local ou variable `PYTHON`), génère les tracés de l’option 1, rend le MP4 puis exécute `scripts/verify-video.py`. Un échec arrête le traitement ; ne pas masquer une voix absente ni annoncer un succès.
4. Inspecter les captures et les transitions ; effectuer l’écoute/lecture si un outil le permet. Le rapport technique ne remplace pas cette revue. Corriger les défauts observés ; si un MP4 existe déjà, préparer une nouvelle réalisation datée pour préserver la précédente.
5. Livrer le lien absolu du MP4, sa date/heure de réalisation et les vérifications réellement effectuées. Signaler les limites concrètes, notamment une écoute subjective non réalisée.

Sortie : `output/options/option-N/YYYY-MM-DD_HH-mm-ss/option-N.mp4`, avec captures, `lesson.json`, `inspection.json` et `creation.json`. L’heure du dossier est celle de la création de la demande en Europe/Paris ; les dates réelles de fin de rendu et de vérification sont enregistrées séparément en UTC. Un suffixe évite toute collision.

Un rendu ne constitue pas une publication. Ne pas mettre le statut « publié » ni modifier l’historique des publications à cette étape. Le skill n’autorise pas à publier sur les réseaux, déployer ou pousser sur GitHub.
