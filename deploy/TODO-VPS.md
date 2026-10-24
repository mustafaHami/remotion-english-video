# TODO à réaliser sur le VPS

État au 24 octobre 2026. Les preuves sont dans [n8n/OPERATIONS.md](n8n/OPERATIONS.md), [VIDEO-PREVIEW.md](n8n/VIDEO-PREVIEW.md), [BUFFER.md](n8n/BUFFER.md), [PUBLICATION.md](n8n/PUBLICATION.md) et [TRACKING.md](n8n/TRACKING.md). Une case cochée renvoie à une preuve consignée ; une case vide reste à faire.

## Fait

- [x] Relevé du serveur (OS, architecture, RAM, dépôt, comptes de service) : OPERATIONS.md.
- [x] Installation native : Node, Python, FFmpeg, Chromium et bibliothèques ; contrôles du projet réussis sur le VPS.
- [x] Persistance : états SQLite, médias privés, planning et sauvegardes sous `/var/lib` et `/var/backups/englizy`.
- [x] Suivi Excel/Journal sans écrasement des briefs : `englizy-tracking`, TRACKING.md.
- [x] Comptes Instagram, TikTok et YouTube raccordés par Buffer ; publication réelle avec accord exact vérifiée le 24/10/2026.
- [x] Secrets hors Git (`/var/lib/englizy/secrets`, identifiants n8n), sauvegardes cohérentes testées en isolement.
- [x] Agent Codex installé sous `englizy-worker` avec le skill du dépôt.
- [x] Choix Codex/Claude par `/modele`, relance après quota épuisé et nettoyage contrôlé (code et tests) : [MODELS.md](n8n/MODELS.md).
- [ ] Claude sur le VPS : jeton `claude setup-token` à saisir par l'utilisateur, puis premier diagnostic et première vidéo réels.
- [x] Europe/Paris, récapitulatif 09:00, verrous, journaux et notifications d’échec.
- [x] Légendes Buffer écrites par épisode (bloc `social`), plus de texte figé.

## Partiel ou à faire

- [ ] Fermer Samba (ports 139/445 ouverts sur toutes les interfaces, `ufw` inactif) ou le restreindre au VPN/LAN ; vérifier le pare-feu de l’hébergeur.
- [ ] Rotation et copie hors site des sauvegardes (elles contiennent les secrets).
- [ ] Renouveler la clé API n8n avant le 21/12/2026.
- [ ] Mesurer la concurrence de rendu au-delà de 2 et tester depuis un clone vierge avec versions figées (Node 24 sur le VPS, Node 22 en CI).
- [ ] Tests réels restants : clic sur un bouton Telegram, MP4 volumineux, panne du fournisseur de voix, session Codex ou Claude expirée, message reçu pendant une coupure.
- [ ] Horaire quotidien de création ou de publication : non activé, uniquement sur demande explicite.

Ne pas activer de publication planifiée avant que ces points applicables soient vérifiés.
