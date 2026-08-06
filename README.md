# rf-test-videos : des vidéos de tests manuels aux suites Robot Framework

Déposer une vidéo dans `videos/`, lancer `/video-to-rf`, obtenir un **plan de
test métier** (`specs/`) et une **suite Robot Framework** validée en dry-run ;
puis `/finalize-rf` relève les localisateurs en direct sur le système sous
test (serveur MCP [rf-mcp](https://github.com/manykarim/rf-mcp)) et prouve la
rejouabilité par deux exécutions réelles vertes.

```text
vidéo (.mp4) → /video-to-rf → specs/<slug>.md → tests/robot/ui/… (dry-run vert)
                                             → page objects (locators TODO)
             → /finalize-rf → locators relevés sur le SUT → 2 runs réels verts
                            → fidélité visuelle vidéo ↔ exécution : verdicts
                              dans la spec + rapport HTML autonome
                              (results/fidelity/<slug>/report.html)
             → /video-to-istqb → specs/istqb/<slug>.istqb.md : plan de test +
                              cas de test ISTQB (tableau humain + bloc replay
                              YAML rejouable par une IA, quel que soit le
                              framework) ; suite RF, ISTQB ou les deux depuis
                              la même vidéo
```

Aucune instrumentation à la capture : n'importe quelle vidéo existante
(Teams, OBS, Game Bar) est exploitable : un créneau qu'aucun outil public ne
couvre à notre connaissance (comparaison détaillée : `docs/etat-de-l-art.md`).

Tout tourne en local : découpage d'images ffmpeg, transcription
faster-whisper (aucun envoi audio externe), génération par l'assistant IA de
VS Code. Fonctionne avec **Claude Code** (skills `.claude/skills/`) et avec
**GitHub Copilot** en mode agent (prompt files `.github/prompts/`, modèle
avec vision requis).

## Installation (nouveau poste, Windows)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```

Le script crée `.venv`, installe `requirements.txt`, télécharge les
navigateurs Playwright et vérifie ffmpeg (`winget install ffmpeg` s'il
manque). Ouvrir ensuite le dossier dans VS Code : les extensions
recommandées sont proposées automatiquement, les terminaux du projet sont
préconfigurés. Le premier `/video-to-rf` télécharge le modèle whisper
(~460 Mo, une seule fois).

## Utilisation

| Assistant | Transcription | Finalisation sur le SUT | Plan ISTQB |
| --- | --- | --- | --- |
| Claude Code | `/video-to-rf videos/x.mp4 --language fr` | `/finalize-rf x` (serveur MCP `.mcp.json`, chargé au démarrage de session) | `/video-to-istqb x` (hors ligne ; accepte aussi la vidéo brute) |
| GitHub Copilot (mode agent) | `/video-to-rf videos/x.mp4 --language fr` | `/finalize-rf x` (serveur MCP `.vscode/mcp.json`, à démarrer dans la vue MCP) | `/video-to-istqb x` |

- **Guide utilisateur** (enregistrer une bonne vidéo, options, brancher le
  SUT, FAQ) : `docs/guide-utilisateur.md`
- **Référence des conventions et du pipeline** (pour l'assistant comme pour
  le relecteur) : `CLAUDE.md`, les instructions Copilot
  (`.github/copilot-instructions.md`) y renvoient.

## Qualité

Chaque push sur `main` (et chaque PR) déclenche la CI
(`.github/workflows/ci.yml`) : traçabilité spec ↔ suite
(`scripts/check_specs.py`), lint Robocop (`robocop.toml`) et `robot --dryrun`
de toutes les suites. Les mêmes commandes tournent en local :

```powershell
python scripts/check_specs.py                  # sha256 des specs + conventions
python scripts/inventory_pages.py              # keywords/locators réutilisables
$env:PYTHONIOENCODING='utf-8'; python -m robocop check tests resources
```

## Exécuter les suites

```powershell
$env:PYTHONIOENCODING='utf-8'; robot -v "APP_PASSWORD:Secret:…" --outputdir results/x tests/robot/ui/web/x.robot
```

(Le préfixe d'encodage est inutile dans les terminaux VS Code du projet :
réglé par `.vscode/settings.json`. Les secrets se passent toujours en CLI,
jamais dans un fichier.)
