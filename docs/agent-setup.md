# Codex et Claude Code

AGENTS.md contient les règles partagées. CLAUDE.md utilise `@AGENTS.md` pour éviter les instructions divergentes. Les procédures communes sont sous .agents/skills ; les entrées .claude/skills sont synchronisées par `node scripts/sync-skills.cjs` et contrôlées dans CI. Ne modifier qu’une copie canonique.

Les skills du dépôt doivent être disponibles depuis un clone vierge : aucune procédure ne doit dépendre seulement d’un skill installé dans le profil Windows de l’auteur. Le poste ou VPS doit disposer des outils décrits dans README. La compétence Spreadsheets de l’environnement reste utile pour l’édition vérifiée du classeur ; son installation sur le VPS est à documenter sur place.

Sources consultées le 21/10/2026 :
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/skills
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://www.remotion.dev/docs/docker
