# Option 14 — Les verbes à particule

Format de vidéo validé, pas une version. Modèle actif : Option14 dans Remotion Studio. L’exemple de référence dure 34 secondes.

## Contenu

phrasal : trois verbes à particule base/particle/phrase/fr/en/kind.

Copier content.json dans content/episodes pour chaque nouvelle vidéo. Lire docs/content-schema.md pour narration/timing. Modifier aussi les textes des clips ; scripts/prepare-audio.py régénère les fichiers associés. Ne pas modifier le code pour changer les mots ou phrases.

## Présentation

Renard de face et corps fixe en accueil/fin, salut et pouce animés. Polices/couleurs/cartes communes. Les rythmes spécifiques de ce format sont décrits dans docs/production.md et timing de content.json. Les données quotidiennes doivent respecter le nombre d’exemples du gabarit.

## Produire et contrôler

```sh
npm run render -- --option=14
python scripts/verify-video.py --option=14
```

Sortie : output/options/option-14/option-14.mp4 et preview.jpg. Pour un épisode inédit, utiliser --content et --output comme dans le README racine. Vérifier l’historique avant toute production destinée à publier ; les fixtures déjà publiées ne sont pas du contenu neuf.
