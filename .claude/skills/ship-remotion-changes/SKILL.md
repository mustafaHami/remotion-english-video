---
name: ship-remotion-changes
description: Préparer un commit et une livraison sur main en respectant les contrôles, les protections GitHub et les exclusions du projet.
---

Lire CONTRIBUTING.md. Choix utilisateur confirmé le 23 octobre 2026 : main est la branche de travail et de livraison par défaut, sans branches permanentes supplémentaires. Vérifier la branche, actualiser les références et préserver les travaux locaux sans rapport. Exécuter les contrôles requis et les rendus touchés. Inspecter git diff --check, les secrets et les fichiers ajoutés ; ne pas inclure output, caches ou Blender. Commit descriptif et push normal. Si les protections GitHub exigent une PR et la CI, utiliser une branche temporaire, attendre les contrôles et fusionner par squash uniquement avec autorisation de fusion. Après vérification de main, supprimer la branche intégrée lorsque le nettoyage est autorisé et synchroniser le checkout. Ne pas désactiver les protections ni faire de force push. Une demande de push ne vaut pas automatiquement autorisation de fusion. Ce skill n’autorise ni publication sociale ni déploiement.
