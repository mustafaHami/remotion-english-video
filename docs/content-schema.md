# Contenu paramétrable

Chaque `src/options/option-N/content.json` est un exemple complet à copier dans `content/episodes/`.

- `option` : numéro entier de 1 à 14.
- `title` : titre court visible dans la vidéo.
- `introText` : courte consigne française ; égale au texte de la première voix.
- `timing` : durées en frames à 30 fps (accueil, leçon, fin, pages et révélations).
- `lessonData` : seulement les données spécifiques au format, documentées dans son README.
- `narration` : clips ordonnés avec `role`, `text`, `voice`, `start`, puis `src`, `duration`, `peaks` après préparation.
- `verb` facultatif pour l’option 2 : be, have, can ou could.
- `writingPaths` pour une nouvelle liste de verbes en option 1, créé par le script de tracés.
- `social` : légendes de partage écrites par l’agent, obligatoires pour une vidéo créée depuis Telegram. `youtubeTitle` (1 à 100 caractères, sans `<` ni `>`) et `captions` avec exactement `instagram`, `tiktok` et `youtube` (1 à 2 000 caractères, aucun lien, 30 hashtags au plus). Elles ne sont pas rendues et n’entrent pas dans l’empreinte du MP4 : les corriger n’exige pas de nouveau rendu.

```json
"social": {
  "youtubeTitle": "10 verbes anglais : présent, passé et futur",
  "captions": {"instagram": "…", "tiktok": "…", "youtube": "… #Shorts"}
}
```

Les nombres de lignes font partie des gabarits : dix verbes/paires, huit répliques ou trois exemples. Un changement de structure est un travail de modèle à tester, pas une modification quotidienne implicite.

## Modifier un épisode

Modifier les données et les textes de ses clips, puis lancer `python scripts/prepare-audio.py --content <fichier>`. Le nom WAV est dérivé de la voix, du débit et du texte ; une ancienne voix associée à un nouveau texte est rejetée par les contrôles. Un clip trop long provoque une erreur de chevauchement : adapter la fenêtre, jamais tronquer l’audio.

Les contrôles rapprochent les phrases visibles de la narration. Les chemins audio doivent rester sous public. Les champs `kind` de l’option 14 restent bus, bag ou stairs ; ajouter une nouvelle illustration exige un composant testé.

Pour l’option 2, ne pas mélanger les familles dans un épisode : sélectionner `verb`, reprendre les sept formes et les trois exemples correspondants dans `verbSeries`, et synchroniser les dix clips. Les modaux can/could n’emploient pas « to ».
