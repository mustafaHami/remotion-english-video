# Option 2 — Un verbe et ses pronoms

Format de vidéo validé, pas une version. Modèle actif : Option2 dans Remotion Studio. L’exemple de référence dure 50.5 secondes.

## Contenu

verbSeries et verbExamples : une famille de sept formes et trois usages ; sélectionner verb.

Copier content.json dans content/episodes pour chaque nouvelle vidéo. Lire docs/content-schema.md pour narration/timing. Modifier aussi les textes des clips ; scripts/prepare-audio.py régénère les fichiers associés. Ne pas modifier le code pour changer les mots ou phrases.

## Présentation

Renard de face et corps fixe en accueil/fin, salut et pouce animés. Polices/couleurs/cartes communes. Les rythmes spécifiques de ce format sont décrits dans docs/production.md et timing de content.json. Les données quotidiennes doivent respecter le nombre d’exemples du gabarit.

## Produire et contrôler

```sh
npm run render -- --option=2
python scripts/verify-video.py --option=2
```

Sortie : output/options/option-2/option-2.mp4 et preview.jpg. Pour un épisode inédit, utiliser --content et --output comme dans le README racine. Vérifier l’historique avant toute production destinée à publier ; les fixtures déjà publiées ne sont pas du contenu neuf.

Variantes disponibles dans variants/have.json, can.json et could.json. Utiliser --content pour les rendre ou copier une variante dans un nouvel épisode.
