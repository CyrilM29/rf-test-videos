# Instructions dépôt : rf-test-videos

Ce dépôt transcrit des **vidéos de tests manuels** en **suites Robot
Framework**. La référence unique du fonctionnement est **`CLAUDE.md`** à la
racine (pipeline, layout, conventions 1 à 6, pièges connus) : la lire et
l'appliquer intégralement, quel que soit l'assistant utilisé.

Rappels essentiels (détail dans `CLAUDE.md`) :

- **Répondre en français** ; noms de keywords en anglais, documentation des
  keywords en français (convention SAPFX).
- **Aucun localisateur hors de `resources/page_objects/`** ; les suites
  n'importent que des `Resource`, jamais une `Library`.
- **Jamais d'attente fixe (`Sleep`)** : attentes sur condition.
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

Never use the em dash (« — ») anywhere in this repo (docs, READMEs, specs,
docstrings, comments, emitted strings, workflows, config): use a colon, a
comma, parentheses, or split the sentence (French puts a space before the
colon, English does not). Enforced by `scripts/check_no_em_dash.py`.

Workflows outillés (prompt files, à invoquer dans le chat en mode agent) :

- `/video-to-rf`, `.github/prompts/video-to-rf.prompt.md` : vidéo → spec →
  suite validée en dry-run. Nécessite un modèle avec vision (lecture des
  frames JPEG).
- `/finalize-rf`, `.github/prompts/finalize-rf.prompt.md` : relevé des
  locators en live sur le SUT (outils MCP robotmcp) + exécution réelle.
- `/video-to-istqb`, `.github/prompts/video-to-istqb.prompt.md` : vidéo (ou
  spec/suite existantes) → plan de test + cas de test ISTQB sous
  `specs/istqb/` (hors ligne, sortie indépendante de la suite RF ; bloc
  replay YAML rejouable par une IA quel que soit le framework).

Ces prompt files sont les équivalents des skills Claude Code
(`.claude/skills/…`) : toute évolution de workflow se reporte dans les deux.

## Mémoire (trois couches qui coexistent)

1. **Mémoire du projet (ce dépôt, publiable)** : `memory/` à la racine,
   faits durables du projet, **anonymisés** (aucune donnée personnelle, aucun
   chemin machine, aucune URL privée) ; index `memory/MEMORY.md`, règles dans
   `memory/README.md`.
2. **Base privée inter-projets** : `E:\QA_GenAI\agent-memory\` (ajouter le
   dossier au workspace VS Code pour un accès natif) : profil et préférences
   de l'utilisateur, spécificités du poste, faits transverses, recherches
   web ; contrat dans son `PROTOCOLE.md`. Jamais publiée.
3. **Mémoire automatique de Claude Code** (Claude seulement) : ne pas la
   dupliquer.

Lire les deux index en début de tâche. Fait nouveau : publiable et propre au
projet → couche 1 ; personnel, lié au poste ou inter-projets → couche 2. Une
fiche par fait, index mis à jour dans la même opération, jamais de secrets :
nulle part.
