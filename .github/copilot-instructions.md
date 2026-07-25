# Instructions dépôt — rf-test-videos

Ce dépôt transcrit des **vidéos de tests manuels** en **suites Robot
Framework**. La référence unique du fonctionnement est **`CLAUDE.md`** à la
racine (pipeline, layout, conventions 1 à 6, pièges connus) : la lire et
l'appliquer intégralement, quel que soit l'assistant utilisé.

Rappels essentiels (détail dans `CLAUDE.md`) :

- **Répondre en français** ; noms de keywords en anglais, documentation des
  keywords en français (convention SAPFX).
- **Aucun localisateur hors de `resources/page_objects/`** ; les suites
  n'importent que des `Resource`, jamais une `Library`.
- **Jamais d'attente fixe (`Sleep`)** — attentes sur condition.
- **Assertions relationnelles et indépendantes de la locale** (les données de
  la démo changent entre l'enregistrement vidéo et l'exécution).
- **`specs/` est la source de vérité** : flux qui change → mettre à jour la
  spec puis régénérer ; ne pas retoucher les suites à la main.
- Un keyword créé depuis une vidéo naît avec des **locators TODO gardés par
  `Require Locator`** ; le relevé se fait sur le SUT via le serveur MCP
  `robotmcp` (config Copilot : `.vscode/mcp.json`).
- `robot` : dans un terminal hors VS Code, préfixer
  `$env:PYTHONIOENCODING='utf-8';` (piège connu du poste d'origine ; les
  terminaux VS Code du projet sont déjà réglés via `.vscode/settings.json`).

Workflows outillés (prompt files, à invoquer dans le chat en mode agent) :

- `/video-to-rf` — `.github/prompts/video-to-rf.prompt.md` : vidéo → spec →
  suite validée en dry-run. Nécessite un modèle avec vision (lecture des
  frames JPEG).
- `/finalize-rf` — `.github/prompts/finalize-rf.prompt.md` : relevé des
  locators en live sur le SUT (outils MCP robotmcp) + exécution réelle.

Ces prompt files sont les équivalents des skills Claude Code
(`.claude/skills/…`) : toute évolution de workflow se reporte dans les deux.
