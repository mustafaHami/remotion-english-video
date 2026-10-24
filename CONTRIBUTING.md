# Contribution et livraison Git

Les options portent un numéro de format, pas un numéro de version. Utiliser option-1 à option-14 dans le code et les sorties. Une vidéo quotidienne possède un identifiant distinct (date, option et éventuellement sujet).

## Avant un commit

1. Lire les consignes et actualiser les références distantes. L’utilisateur est le seul développeur : `main` est la seule branche durable, sans branches de travail permanentes ni relecture de PR. Préserver les modifications locales et résoudre les divergences sans écrasement.
2. Vérifier `git status --short`, ne pas mélanger les travaux d’autres personnes.
3. Exécuter `npm run check`, `npm test`, `npm run verify`. Rendre et inspecter les options touchées par un changement visuel.
4. Consulter `git diff --check` et les fichiers ajoutés. Ajouter des chemins explicites ; exclure secrets, rendus, caches et fichiers Blender.
5. Commit court et descriptif : `feat: ...`, `fix: ...`, `docs: ...` ou `content: ...`.
6. Livrer sur `main`. La protection GitHub (PR, contrôle `quality`, historique linéaire) est conservée par choix de l’utilisateur du 24 octobre 2026, donc un push direct est refusé. La PR n’est qu’un passage technique : branche temporaire, push, PR, CI `quality` verte, fusion squash, suppression de la branche locale et distante, puis `main` local synchronisé et vérifié. Une demande de livraison sur `main` vaut accord pour cette fusion ; aucune relecture n’est attendue. Ne pas contourner ni modifier la protection.

Premier import dans un dépôt vide : un commit initial sur main et son push sont autorisés par l’utilisateur. Aucun force push n’est nécessaire.

La PR existe uniquement parce que la protection GitHub l’impose, pas comme convention de travail : aucune branche ne doit survivre à sa fusion. Les fichiers de production et d’historique doivent garder des identifiants stables ; ne pas committer les MP4 quotidiens. Un agent doit demander une résolution de conflit plutôt qu’écraser un classeur ou un historique.

## Secrets et médias

Les accès GitHub/plateformes viennent du gestionnaire de credentials ou de variables d’environnement. `.env` et configurations locales restent ignorés. Les ressources légères indispensables au rendu sont versionnées ; les exports volumineux restent sur le stockage de production. Les archives locales ne sont pas effacées.

## Règles du dépôt

Le workflow CI contrôle le typage, les invariants et les modèles. Conserver les protections existantes de main et le blocage des force pushes. Toute modification de ces protections nécessite une autorisation explicite distincte ; la préférence pour main ne les désactive pas. La procédure et l’éventuelle limitation de plan doivent être consignées ; ne pas prétendre qu’un fichier de consignes protège réellement la branche.
