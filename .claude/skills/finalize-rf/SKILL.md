---
name: finalize-rf
description: Finalise une suite générée par /video-to-rf en relevant les locators TODO en direct sur le SUT via le serveur MCP robotmcp (rf-mcp), puis valide par une exécution réelle. Argument = slug ou chemin de la suite (ex. test-video-to-rf).
argument-hint: <slug | tests/robot/ui/<domaine>/<slug>.robot>
---

# /finalize-rf : relevé des locators sur le SUT et tests rejouables

Cette skill fait la passe que la vidéo ne peut pas faire : découvrir les
localisateurs sur le **SUT réel** et prouver la rejouabilité. Elle s'appuie
sur les outils MCP du serveur `robotmcp` (rf-mcp) : exécution de keywords RF
en live (`execute_step`), inspection du DOM (`get_page_source`,
`get_session_state`), suggestions (`analyze_scenario`).

Conventions CLAUDE.md toujours en vigueur, en particulier : locators
UNIQUEMENT dans `resources/page_objects/` ; jamais de `Sleep` ; spec = source
de vérité ; aucun secret écrit dans un fichier.

## 1. Préparer

- Résoudre `$ARGUMENTS` → suite `tests/robot/ui/<domaine>/<slug>.robot`,
  spec `specs/<slug>.md`, page objects référencés par la suite.
- Inventorier les locators à relever : Grep `\$\{EMPTY\}\s+# TODO` dans les
  page objects concernés. S'il n'y en a aucun, passer directement à
  l'étape 5 (validation).
- **Vérifier que les outils MCP `robotmcp` sont disponibles.** Sinon
  s'arrêter : le serveur est déclaré dans `.mcp.json` mais un serveur MCP ne
  se charge qu'au démarrage de session : demander à l'utilisateur de
  recharger la fenêtre VS Code / relancer la session, puis relancer la skill.
- Identifiants : lire la spec (« Préconditions », « Points de vigilance »).
  Si un secret est nécessaire et non public, le demander à l'utilisateur
  (AskUserQuestion) et ne JAMAIS l'écrire dans un fichier.

## 2. Ouvrir la session live

- Via `manage_session` / `execute_step` : importer la librairie du canal
  (celle de `common.resource` : Browser ici), ouvrir le navigateur en mode
  visible (`headless=False`) sur `SUT_BASE_URL` (lire
  `variables/env_local.py`).
- Dérouler la mise en condition minimale (ex. login) avec des `execute_step`
  unitaires : chaque étape observée avant la suivante.

## 3. Relever écran par écran (dans l'ordre des scénarios de la spec)

Pour chaque écran / page object :

- Naviguer jusqu'à l'écran (`execute_step`).
- Inspecter le DOM (`get_page_source`, `analyze_scenario`) et choisir des
  locators **robustes**, dans cet ordre de préférence : `id=` stable >
  `name=` > attribut `data-*` > CSS court et signifiant > XPath en dernier
  recours (et jamais un XPath positionnel fragile). Jamais un texte localisé
  seul si un ancrage technique existe.
- **Valider chaque locator en live** avant de l'écrire : `execute_step` avec
  `Get Element Count` (== 1 attendu), puis l'action réelle du keyword
  (Click, Fill Text…) pour vérifier le comportement.
- Gabarits paramétrables (`{module}`, `{value}`, `{status}`) : valider avec
  au moins deux valeurs différentes avant de les retenir.
- Renseigner la variable dans le page object : remplacer `${EMPTY}` par le
  locator validé et remplacer le commentaire `# TODO` par
  `# relevé SUT <date>`. Ne PAS toucher aux corps des keywords ni aux
  suites.

## 4. Traiter les écarts

- Si le SUT contredit un corps de keyword ou une étape de la spec (bouton
  absent, flux différent, champ renommé…) : consigner l'écart dans la
  section « Écarts constatés à la génération » de la spec, PUIS corriger le
  page object en conséquence. La spec reste la source de vérité (convention
  4) : la suite ne se retouche pas à la main.
- Toute modification de la spec → **rafraîchir l'empreinte** `sha256:<12 hex>`
  dans l'en-tête `Documentation` de la suite
  (`(Get-FileHash specs\<slug>.md -Algorithm SHA256).Hash.Substring(0,12).ToLower()`) ;
  `python scripts/check_specs.py` vérifie la concordance.

## 5. Valider (obligatoire : rejouabilité prouvée)

- Dry-run d'abord :
  `$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry_<slug> tests/robot/ui/<domaine>/<slug>.robot`
- Puis **exécution réelle complète**, secrets en CLI :
  `$env:PYTHONIOENCODING='utf-8'; robot -v APP_PASSWORD:<secret> --outputdir results/<slug> tests/robot/ui/<domaine>/<slug>.robot`
- Échec → diagnostiquer via `results/<slug>/log.html` et la session live,
  corriger (locator, attente sur condition manquante, jamais un `Sleep`),
  relancer. **Deux exécutions réelles vertes consécutives** pour conclure à
  la rejouabilité (données volatiles de démo ≠ test instable).

## 6. Preuve de fidélité visuelle (vidéo ↔ exécution)

La rejouabilité (runs verts) ne prouve pas encore que la suite rejoue **ce
que la vidéo montre**. Fermer cette boucle :

- Prérequis : `work/<slug>/storyboard.md` et ses frames. S'ils ont été
  purgés (`work/` est jetable), les régénérer si la vidéo est encore là
  (`python scripts/prepare_video.py videos/<slug>.*`) ; sinon sauter l'étape
  en le notant dans le rapport.
- Pour chaque scénario de la spec : rejouer en session live (`execute_step`)
  jusqu'à l'écran de fin de scénario, prendre une capture
  (`Take Screenshot`), puis la **comparer visuellement** (Read des deux
  images côte à côte : l'outil `visual_check` de robotmcp peut aider) à la
  frame du storyboard correspondant à l'horodatage de fin du scénario.
- Verdict par scénario : `conforme` (même écran, même état métier) ou
  `écart` (décrire : élément déplacé, libellé changé, flux différent…). Les
  différences de **données** (compteurs, listes) sont attendues : le jeu de
  données a changé depuis l'enregistrement ; seul l'écart de **structure ou
  de flux** compte.
- Produire le **rapport HTML** : écrire
  `results/fidelity/<slug>/manifest.json` (captures dans le même dossier ;
  schéma documenté en tête de `scripts/fidelity_report.py` : un objet par
  scénario : n, titre, timestamp, frame, capture, verdict
  `conforme`|`écart`, note) puis lancer
  `python scripts/fidelity_report.py <slug>` →
  `results/fidelity/<slug>/report.html`, autonome (images embarquées en
  base64 : partageable, survit à la purge de `work/` et des captures).
- Consigner aussi le bilan dans la section « Fidélité visuelle » de la spec
  (date, verdict par scénario) : la spec reste l'artefact durable, le
  rapport HTML est la vue partageable. Un écart de flux → aussi dans
  « Écarts constatés à la génération », et rafraîchir le sha256 (étape 4).

## 7. Rapport final

Terminer par : locators renseignés / restants (avant → après) ; écarts
consignés dans la spec ; résultat des exécutions réelles (chemins
`results/<slug>/`) ; bilan de fidélité visuelle par scénario + chemin du
rapport HTML (`results/fidelity/<slug>/report.html`) ; keywords dont
le corps a dû être ajusté ; rappel que les locators relevés enrichissent les
page objects partagés (`python scripts/inventory_pages.py` pour l'inventaire
à jour). Fermer la session live (`manage_session`).
