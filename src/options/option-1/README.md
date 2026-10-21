# Option 1 — Présent, passé, futur

Format de vidéo validé, pas une version. Modèle actif : Option1 dans Remotion Studio. L’exemple de référence dure 73.5 secondes.

## Contenu

rows : dix objets present/past/future ; writingPaths généré pour les nouvelles formes.

Copier content.json dans content/episodes pour chaque nouvelle vidéo. Lire docs/content-schema.md pour narration/timing. Modifier aussi les textes des clips ; scripts/prepare-audio.py régénère les fichiers associés. Ne pas modifier le code pour changer les mots ou phrases.

## Présentation

Renard de face et corps fixe en accueil/fin, salut et pouce animés. Polices/couleurs/cartes communes. Les rythmes spécifiques de ce format sont décrits dans docs/production.md et timing de content.json. Les données quotidiennes doivent respecter le nombre d’exemples du gabarit.

## Produire et contrôler

```sh
npm run render -- --option=1
python scripts/verify-video.py --option=1
```

Sortie : output/options/option-1/option-1.mp4 et preview.jpg. Pour un épisode inédit, utiliser --content et --output comme dans le README racine. Vérifier l’historique avant toute production destinée à publier ; les fixtures déjà publiées ne sont pas du contenu neuf.
