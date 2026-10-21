# TODO à réaliser sur le VPS

L’utilisateur a demandé de rédiger et finaliser la documentation du serveur directement sur le VPS. Aucun accès serveur ni compte social n’a été fourni dans cette préparation.

- [ ] Relever l’OS, l’architecture, CPU, RAM, disque, répertoire de déploiement et utilisateur d’exécution.
- [ ] Choisir installation native ou Docker ; tester un rendu court et mesurer la concurrence adaptée (commencer à 2).
- [ ] Installer Node/Python/FFmpeg/Chromium et versions figées ; exécuter les contrôles depuis un clone vierge.
- [ ] Définir les volumes persistants : planning, content/episodes, public/audio/production, output et .runtime.
- [ ] Installer le mécanisme de mise à jour du Journal/Calendrier Excel et vérifier qu’un brief existant n’est pas écrasé.
- [ ] Renseigner les plateformes et comptes ; vérifier les API officielles, autorisations, types de comptes et possibilités de publication requises.
- [ ] Implémenter et tester l’adaptateur selon publishing-contract.md, d’abord sans publication publique.
- [ ] Conserver les secrets hors Git ; configurer les accès, renouvellements et sauvegardes.
- [ ] Installer l’agent Codex/Claude et ses skills depuis le dépôt ; définir le modèle et son accès sans inscrire de clé dans les fichiers versionnés.
- [ ] Configurer l’heure quotidienne et Europe/Paris, les changements d’heure, les verrous, journaux et notifications d’échec.
- [ ] Tester reprise après interruption, absence de brief, contenu déjà publié, résultat de publication incertain et restauration des sauvegardes.
- [ ] Documenter sur ce serveur les commandes effectives de déploiement, mise à jour et retour arrière.

Ne pas activer la publication quotidienne avant que ces points applicables soient vérifiés. Le dépôt prépare le protocole ; il ne prétend pas que le VPS ou les API sont déjà raccordés.
