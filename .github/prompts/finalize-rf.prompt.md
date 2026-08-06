---
mode: agent
description: Finalise une suite générée par /video-to-rf en relevant les locators TODO en direct sur le SUT via le serveur MCP robotmcp, puis prouve la rejouabilité par deux exécutions réelles vertes. Argument = slug ou chemin de la suite.
---

# /finalize-rf : relevé des locators sur le SUT et tests rejouables

Conventions de `CLAUDE.md` en vigueur, notamment : locators UNIQUEMENT dans
`resources/page_objects/` ; jamais de `Sleep` ; spec = source de vérité ;
aucun secret écrit dans un fichier.

## 1. Préparer

- Résoudre l'argument → suite `tests/robot/ui/<domaine>/<slug>.robot`, spec
  `specs/<slug>.md`, page objects référencés.
- Inventorier les locators `${EMPTY}    # TODO` (recherche dans les page
  objects). Aucun → passer à l'étape 5.
- **Vérifier que les outils MCP `robotmcp` sont disponibles** (serveur
  déclaré dans `.vscode/mcp.json` : le démarrer depuis la vue MCP de VS Code
  si besoin). Indisponibles → s'arrêter et demander de le démarrer.
- Identifiants : lire la spec ; secret non public → le demander dans le chat,
  ne JAMAIS l'écrire dans un fichier.

## 2. Ouvrir la session live

- `analyze_scenario` (crée la session, réutiliser son session_id partout),
  puis `execute_step` unitaires : ouvrir le navigateur du canal (librairie de
  `common.resource`) sur `SUT_BASE_URL` (`variables/env_local.py`) et
  dérouler la mise en condition (login…), chaque étape observée.

## 3. Relever écran par écran (ordre des scénarios de la spec)

- Naviguer (`execute_step`), inspecter (`get_session_state` avec
  page_source/ARIA), choisir des locators robustes : `id=` stable > `name=` >
  `data-*` > CSS court signifiant > XPath en dernier recours. Jamais un texte
  localisé seul si un ancrage technique existe.
- **Valider chaque locator en live avant écriture** : `Get Element Count`
  (== 1) puis l'action réelle du keyword. Gabarits (`{module}`, `{value}`,
  `{status}`) : valider avec au moins deux valeurs.
- Écrire dans le page object : `${EMPTY}` → locator validé, commentaire
  `# relevé SUT <date>`. Ne PAS toucher aux corps des keywords ni aux suites.

## 4. Traiter les écarts

- SUT contredit un corps de keyword ou la spec → consigner dans « Écarts
  constatés à la génération » de la spec, PUIS corriger le page object.
  Rafraîchir le sha256 de la spec dans l'en-tête de la suite
  (`python scripts/check_specs.py` vérifie la concordance).

## 5. Valider (obligatoire : rejouabilité prouvée)

- Dry-run, puis exécution réelle complète (secrets en CLI :
  `robot -v APP_PASSWORD:<secret> …`). Échec → diagnostiquer via
  `results/<slug>/log.html` + session live, corriger (jamais un `Sleep`),
  relancer. **Deux exécutions réelles vertes consécutives** exigées.

## 6. Preuve de fidélité visuelle (vidéo ↔ exécution)

- Prérequis : `work/<slug>/storyboard.md` + frames (les régénérer via
  `python scripts/prepare_video.py videos/<slug>.*` si purgés ; vidéo absente
  → sauter en le notant).
- Par scénario de la spec : rejouer en session live jusqu'à l'écran de fin,
  capture (`Take Screenshot`), comparaison visuelle avec la frame du
  storyboard à l'horodatage de fin (l'outil `visual_check` de robotmcp peut
  aider). Verdict `conforme` | `écart` : les différences de données sont
  attendues, seuls comptent structure et flux.
- Rapport HTML : écrire `results/fidelity/<slug>/manifest.json` (schéma en
  tête de `scripts/fidelity_report.py`) puis
  `python scripts/fidelity_report.py <slug>` →
  `results/fidelity/<slug>/report.html` (autonome, images embarquées).
- Bilan aussi dans la section « Fidélité visuelle » de la spec (date +
  verdicts : artefact durable) ; écart de flux → aussi dans « Écarts… » +
  rafraîchir le sha256 (étape 4).

## 7. Rapport final

Locators renseignés/restants (avant → après) ; écarts consignés ; résultats
des runs (`results/<slug>/`) ; bilan de fidélité visuelle par scénario +
chemin du rapport HTML ;
corps de keywords ajustés ; les locators relevés enrichissent les page
objects partagés (`python scripts/inventory_pages.py`). Fermer la session
live (`Close Browser    ALL`).
