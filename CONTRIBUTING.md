# Contribution et livraison Git

Les options portent un numéro de format, pas un numéro de version. Utiliser option-1 à option-14 dans le code et les sorties. Une vidéo quotidienne possède un identifiant distinct (date, option et éventuellement sujet).

## Avant un commit

1. Lire les consignes ; créer une branche `feat/<sujet>`, `fix/<sujet>` ou `content/<date-option>` depuis la branche distante à jour.
2. Vérifier `git status --short`, ne pas mélanger les travaux d’autres personnes.
3. Exécuter `npm run check`, `npm test`, `npm run verify`. Rendre et inspecter les options touchées par un changement visuel.
4. Consulter `git diff --check` et les fichiers ajoutés. Ajouter des chemins explicites ; exclure secrets, rendus, caches et fichiers Blender.
5. Commit court et descriptif : `feat: ...`, `fix: ...`, `docs: ...` ou `content: ...`.
6. Push normal : `git push -u origin <branche>`, puis pull request vers main. Vérifier les contrôles GitHub avant fusion.

Premier import dans un dépôt vide : un commit initial sur main et son push sont autorisés par l’utilisateur. Aucun force push n’est nécessaire.

Les changements de code passent par une PR. Les fichiers de production et d’historique doivent garder des identifiants stables ; ne pas committer les MP4 quotidiens. Un agent doit demander une résolution de conflit plutôt qu’écraser un classeur ou un historique.

## Secrets et médias

Les accès GitHub/plateformes viennent du gestionnaire de credentials ou de variables d’environnement. `.env` et configurations locales restent ignorés. Les ressources légères indispensables au rendu sont versionnées ; les exports volumineux restent sur le stockage de production. Les archives locales ne sont pas effacées.

## Règles du dépôt

Le workflow CI contrôle le typage, les invariants et les modèles. Configurer les protections de main (PR, contrôle `quality`, blocage des force pushes) selon les possibilités du compte GitHub. La procédure et l’éventuelle limitation de plan doivent être consignées ; ne pas prétendre qu’un fichier de consignes protège réellement la branche.
