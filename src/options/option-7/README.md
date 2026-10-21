# Option 7 — Les mots qui vont ensemble

Format de vidéo validé, pas une version. Modèle actif : Option7 dans Remotion Studio. L’exemple de référence dure 34 secondes.

## Contenu

associations : trois groupes verb/rest/fr/en.

Copier content.json dans content/episodes pour chaque nouvelle vidéo. Lire docs/content-schema.md pour narration/timing. Modifier aussi les textes des clips ; scripts/prepare-audio.py régénère les fichiers associés. Ne pas modifier le code pour changer les mots ou phrases.

## Présentation

Renard de face et corps fixe en accueil/fin, salut et pouce animés. Polices/couleurs/cartes communes. Les rythmes spécifiques de ce format sont décrits dans docs/production.md et timing de content.json. Les données quotidiennes doivent respecter le nombre d’exemples du gabarit.

## Produire et contrôler

```sh
npm run render -- --option=7
python scripts/verify-video.py --option=7
```

Sortie : output/options/option-7/option-7.mp4 et preview.jpg. Pour un épisode inédit, utiliser --content et --output comme dans le README racine. Vérifier l’historique avant toute production destinée à publier ; les fixtures déjà publiées ne sont pas du contenu neuf.
