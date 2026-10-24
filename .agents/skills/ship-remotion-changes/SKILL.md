---
name: ship-remotion-changes
description: Préparer un commit et une livraison sur main en respectant les contrôles, les protections GitHub et les exclusions du projet.
---

Lire CONTRIBUTING.md. L’utilisateur est le seul développeur : main est la seule branche durable, sans relecture de PR. Vérifier la branche, actualiser les références et préserver les travaux locaux sans rapport. Exécuter les contrôles requis et les rendus touchés. Inspecter git diff --check, les secrets et les fichiers ajoutés ; ne pas inclure output, caches ou Blender. Commit descriptif. La protection GitHub de main (PR + `quality`) est conservée par choix du 24 octobre 2026 : passer par une branche temporaire et une PR technique, attendre la CI verte, fusionner par squash, supprimer la branche locale et distante, puis synchroniser et vérifier main. Une demande de livraison sur main vaut accord pour cette fusion. Ne pas désactiver ni contourner les protections, pas de force push. Ce skill n’autorise ni publication sociale ni déploiement des services.
