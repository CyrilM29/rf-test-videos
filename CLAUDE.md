# CLAUDE.md

Guide pour les assistants IA travaillant dans ce dépôt. Le tenir exact — le
mettre à jour quand la structure ou les conventions changent.

## Langue

**Répondre en français** et rédiger les documents utilisateur en français.
Noms de keywords, identifiants techniques et code restent en anglais.

## Objet

Transcrire des **vidéos de tests manuels** en **suites Robot Framework**, sans
accès live au système sous test pendant la génération. L'organisation des
artefacts RF est calquée sur le projet `E:\QA_GenAI\SAP_library_custom`
(SAPFX) : plans de test Markdown lisibles métier (`specs/`) → suites générées
(`tests/robot/ui/…`) → localisateurs cantonnés aux page objects
(`resources/page_objects/`).

## Pipeline (skill `/video-to-rf <vidéo>`)

```text
videos/x.mp4                        (ou un dossier entier : mode batch)
  │  python scripts/prepare_video.py videos/x.mp4
  ▼
work/x/{frames/*.jpg, audio_transcript.md, storyboard.md, meta.json}
  │  lecture des frames dans l'ordre du storyboard (frames + voix off
  │  fusionnées ; quasi-doublons écartés par dHash)
  │  capitalisation : scripts/inventory_pages.py (keywords/locators existants)
  │  checkpoint librairies : canaux observés vs Library branchées —
  │  question à l'utilisateur si canal non couvert (hybridation possible)
  ▼
specs/x.md                          ← plan métier (gabarit : specs/README.md)
  │  mapping sur les keywords existants de resources/
  ▼
tests/robot/ui/<domaine>/x.robot    ← 1 test par scénario, zéro localisateur
resources/page_objects/…            ← keywords implémentés, locators TODO
  │
  ▼
robot --dryrun + check_specs.py + robocop   ← porte de sortie de /video-to-rf
  │  skill /finalize-rf : relevé des locators en live sur le SUT
  │  (serveur MCP robotmcp — .mcp.json) puis exécution réelle
  ▼
robot (exécution réelle)            ← rejouabilité prouvée (2 runs verts)
  ▼
fidélité visuelle                   ← frames vidéo ↔ captures d'exécution,
                                      verdict par scénario consigné dans la spec
                                      + rapport HTML autonome
                                      (results/fidelity/<slug>/report.html)
```

## Layout

| path | rôle |
| --- | --- |
| `docs/guide-utilisateur.md` | guide utilisateur (capture, skill, branchement SUT, FAQ) — à tenir en phase avec ce fichier |
| `videos/` | zone de dépôt des vidéos sources (gitignorées, jetables) |
| `work/<slug>/` | artefacts intermédiaires régénérables : frames, transcription, meta |
| `specs/` | plans de test métier — **source de vérité** des suites (gabarit dans son README) |
| `tests/robot/ui/<domaine>/` | suites générées ; domaine ∈ web \| fiori \| ecc \| desktop \| mobile |
| `resources/common.resource` | keywords transverses + import de la librairie de pilotage du SUT |
| `resources/page_objects/` | un `.resource` par écran — SEUL emplacement des localisateurs |
| `variables/env_local.py` | URLs/identifiants techniques d'environnement (jamais de secret) |
| `results/` | sorties robot (gitignorées) |
| `scripts/prepare_video.py` | frames (détection de scène ffmpeg, dédoublonnage dHash) + voix off (faster-whisper) + storyboard fusionné ; accepte une vidéo ou un dossier (batch) |
| `scripts/check_specs.py` | contrôle traçabilité spec ↔ suite (sha256) + conventions 1/2/4 — exécuté par la CI et les skills |
| `scripts/inventory_pages.py` | inventaire des page objects : keywords et état des locators (capitalisation ; `--json` pour les skills) |
| `scripts/fidelity_report.py` | rapport HTML autonome de fidélité visuelle (images base64) depuis `results/fidelity/<slug>/manifest.json` — écrit par /finalize-rf, schéma en tête du script |
| `robocop.toml` | config lint Robocop — les écarts acceptés y sont justifiés par les conventions du dépôt |
| `.github/workflows/ci.yml` | CI : check_specs + Robocop + dry-run de toutes les suites (aucun SUT requis) |
| `docs/etat-de-l-art.md` | positionnement vs V2S/GIFdroid, outils commerciaux, open source LLM — document de présentation |
| `.claude/skills/video-to-rf/` | la skill vidéo → spec → suite (dry-run) |
| `.claude/skills/finalize-rf/` | la skill de relevé des locators sur le SUT (via MCP robotmcp) + exécution réelle |
| `.mcp.json` | serveur MCP `robotmcp` (rf-mcp) — exécution RF live, inspection DOM ; chargé au démarrage de session |
| `robot.toml` | config RF partagée IDE (RobotCode) / CLI : `output-dir = results` |
| `.github/copilot-instructions.md` | instructions dépôt pour GitHub Copilot — renvoient vers CE fichier (référence unique) |
| `.github/prompts/*.prompt.md` | équivalents Copilot des deux skills — **toute évolution de workflow se reporte dans les deux** |
| `.vscode/` | `mcp.json` (robotmcp côté Copilot), `settings.json` (fix PYTHONIOENCODING des terminaux, prompt files), extensions recommandées |
| `scripts/setup.ps1` | bootstrap d'un nouveau poste : .venv, requirements, navigateurs Playwright, contrôle ffmpeg |

## Commandes

```powershell
python scripts/prepare_video.py videos/x.mp4                    # frames + transcription + storyboard
python scripts/prepare_video.py videos/                         # batch : tout le dossier
python scripts/prepare_video.py videos/x.mp4 --scene 0.2 --model base --language fr
python scripts/check_specs.py                                   # traçabilité spec <-> suite
python scripts/inventory_pages.py                               # capitalisation page objects
python scripts/fidelity_report.py <slug>                        # rapport HTML fidélité visuelle
$env:PYTHONIOENCODING='utf-8'; python -m robocop check tests resources    # lint (robocop.toml)
$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry_x tests/robot/ui/web/x.robot
$env:PYTHONIOENCODING='utf-8'; robot --outputdir results/x tests/robot/ui/web/x.robot
```

## Conventions (à ne pas casser — héritées de SAPFX)

1. **Aucun localisateur dans les tests.** Ids, CSS, XPath vivent dans
   `resources/page_objects/` ; les tests parlent métier. Les suites
   n'importent jamais une `Library` directement — uniquement des `Resource`.
   La librairie du canal principal s'importe dans `common.resource` (Browser
   depuis le 2026-07-25) ; en cas d'hybridation multi-canaux (web + desktop,
   web + SAP…), la librairie d'un canal secondaire s'importe dans les seuls
   page objects des écrans de ce canal.
2. **Jamais d'attente fixe** (`Sleep`). Toujours un keyword d'attente sur
   condition — une vidéo ne montre pas les temps de réponse réels du SUT.
3. **Assertions indépendantes de la locale.** Nombres extraits, comptages,
   ids techniques — jamais un libellé localisé lu dans la vidéo. Assertions
   **relationnelles** (filtré < total, valeur mesurée dans le même run)
   plutôt que constantes recopiées de la vidéo : le jeu de données du SUT
   aura changé depuis l'enregistrement.
4. **La spec est la source de vérité.** Chaque suite référence sa spec
   (`Spec: specs/x.md (sha256:…, date)`). Flux qui change → refaire/mettre à
   jour la spec puis régénérer ; on n'édite pas les localisateurs à la main
   dans les tests. Toute divergence relevée pendant la génération va dans la
   section « Écarts constatés à la génération » de la spec.
5. **Un keyword manquant est explicite, jamais inventé.** Listé dans la spec
   (« Keywords métier manquants »), créé en page object avec locators
   `${EMPTY}    # TODO` et pour corps l'**implémentation réelle** dans la
   librairie du canal (choisie au checkpoint), chaque locator gardé par
   `Require Locator    ${LOC}    specs/<slug>.md` (`common.resource`) — le
   `--dryrun` passe, l'exécution réelle échoue tant que le localisateur n'a
   pas été relevé sur le SUT. Le corps `Fail Missing Locator` reste réservé
   aux keywords dont l'action est trop incertaine pour être implémentée
   (écart noté dans la spec). Noms de keywords en anglais, documentation en
   français (convention SAPFX).
6. **`work/` et `results/` sont jetables**, régénérables, jamais committés ;
   une vidéo n'est pas un artefact durable — la spec et la suite le sont.

## Pièges connus

- **`PYTHONIOENCODING=utf-8:surrogateescape` casse la console de robot** sur
  ce poste (`LookupError: unknown encoding` dès `robot --version`). Les
  terminaux VS Code du projet sont réglés via `.vscode/settings.json` ;
  ailleurs, toujours préfixer : `$env:PYTHONIOENCODING='utf-8'; robot …`.
- **Premier run whisper** : télécharge le modèle (~460 Mo pour `small`) dans
  `%USERPROFILE%\.cache\huggingface`. `--model base` (~140 Mo) est un repli
  plus léger ; `--language fr` fiabilise la détection sur une voix faible.
- **Vidéo trop statique** (peu de changements d'écran) : la détection de
  scène rend < 8 frames → `prepare_video.py` bascule tout seul sur un
  échantillonnage à intervalle fixe ; sinon ajuster `--scene`.
- **Le dédoublonnage dHash peut écarter une étape** qui ne diffère que par
  une saisie clavier (très peu de pixels changent) : si des étapes manquent
  au storyboard, relancer avec `--dedup 0`. Pillow absent → dédoublonnage
  sauté avec un avertissement (pas d'échec).
- **Browser (Playwright) exige `rfbrowser init` après le pip install**
  (téléchargement des navigateurs) ; sans lui, tout `robot` qui importe la
  librairie échoue au chargement.
- **Une vidéo ne montre jamais les localisateurs.** Tout keyword créé depuis
  une vidéo naît avec un locator TODO (convention 5) ; le relevé se fait
  ensuite sur le SUT via `/finalize-rf` (session live robotmcp), hors du
  périmètre de la transcription.
- **Un serveur MCP ne se charge qu'au démarrage de session** : après ajout ou
  modification de `.mcp.json`, recharger la fenêtre VS Code avant d'utiliser
  les outils `robotmcp`. Au lancement, le serveur logge des erreurs de
  plugins SAP (`sap_robotmcp` → `No module named 'sapfx_common'`) et l'absence
  de SeleniumLibrary : bénin ici, le canal web passe par Browser.
