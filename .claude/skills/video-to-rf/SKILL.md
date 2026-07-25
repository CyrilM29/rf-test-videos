---
name: video-to-rf
description: Transcrit une vidéo de test manuel en plan de test (specs/) puis en suite Robot Framework validée en dry-run. Argument = chemin de la vidéo (ex. videos/mon-scenario.mp4) ; les options éventuelles sont passées telles quelles à prepare_video.py (--model, --language, --scene…).
argument-hint: videos/<fichier>.mp4 [--language fr] [--model small]
---

# /video-to-rf — vidéo → spec → suite Robot Framework

Suivre TOUTES les étapes, dans l'ordre. Les conventions du CLAUDE.md
s'appliquent en permanence (1 : zéro localisateur dans les tests ; 2 : zéro
attente fixe ; 3 : assertions locale-indépendantes ; 4 : spec = source de
vérité ; 5 : keyword manquant explicite).

## 1. Préparer

- `$ARGUMENTS` = chemin de la vidéo + options éventuelles. Vérifier que le
  fichier existe ; sinon lister `videos/` et s'arrêter avec un message clair.
- Lancer (timeout ≥ 10 min : le premier run télécharge le modèle whisper) :
  `python scripts/prepare_video.py <vidéo> [options]`
- Le script imprime le dossier de travail `work/<slug>/`. Lire `meta.json`
  et `audio_transcript.md`.

## 2. Lire la vidéo (frames + voix off)

- Lire les frames de `work/<slug>/frames/` en **ordre chronologique** (le nom
  porte l'horodatage : `frame_012_t01m23.5s.jpg`), par lots de 6 à 8 appels
  Read en parallèle par message. Lire **toutes** les frames — si la vidéo en
  produisait trop, le script a déjà échantillonné et l'a dit ; ne jamais
  sous-échantillonner davantage en silence.
- Croiser chaque frame avec les segments de voix off qui l'encadrent
  (horodatages) : la voix off donne l'**intention**, la frame donne
  l'**observé**. En cas de contradiction, l'observé gagne et l'écart est noté.
- Tenir un relevé étape par étape : `[t]` écran visible, action déduite du
  passage frame N → N+1, données saisies (valeurs lues à l'écran), résultat
  visible. Ce qui est flou ou incertain est noté comme tel — jamais inventé.

## 3. Choisir la ou les librairies de pilotage (checkpoint — AVANT toute génération)

- Déduire du relevé de l'étape 2 les **canaux en action** dans la vidéo :
  web, desktop, SAP GUI, Fiori, mobile, appels API visibles… Une vidéo peut
  en mêler plusieurs (ex. saisie web puis vérification dans un client lourd).
- Inventorier les librairies déjà branchées : Grep `^Library` dans
  `resources/**/*.resource`.
- **Chaque canal observé couvert par une librairie déjà branchée** →
  continuer sans question.
- **Sinon, s'arrêter et demander** (AskUserQuestion) avant d'écrire quoi que
  ce soit : proposer les librairies candidates par canal (web : Browser,
  SeleniumLibrary ; SAP : librairies SAPFX ; desktop, mobile…), avec une
  recommandation argumentée — y compris l'**hybridation** quand plusieurs
  canaux cohabitent (une librairie par canal, pas une librairie unique forcée).
- Acter la décision :
  - librairie du canal **principal** → `Library` dans
    `resources/common.resource` ;
  - librairie propre à un canal **secondaire** → `Library` dans les seuls
    page objects des écrans de ce canal (jamais dans les suites — convention 1
    inchangée : les suites n'importent que des `Resource`) ;
  - dépendance décommentée/épinglée dans `requirements.txt` (installer et
    vérifier — ex. Browser exige `rfbrowser init` après le pip install) ;
  - décision reportée dans la spec (ligne « Pilotage » de l'en-tête).

## 4. Écrire la spec

- `specs/<slug>.md` selon le gabarit de `specs/README.md` (mêmes sections que
  le projet SAPFX + « Source vidéo » + « Pilotage » + horodatage par
  scénario).
- Découper le flux en scénarios autonomes (un objectif métier chacun,
  rejouable seul).
- Étapes en langage métier ; AUCUN id/CSS/XPath dans les étapes. Ce qui est
  lu à l'écran (libellés, valeurs, volumétries, formats) va dans « Données
  observées » et « Points de vigilance ».
- Inventorier les keywords existants AVANT d'écrire : chercher les sections
  `*** Keywords ***` dans `resources/**/*.resource` (Grep). Chaque étape
  référence un keyword existant quand il y en a un ; sinon l'inscrire dans
  « Keywords métier manquants » du scénario.

## 5. Générer la suite

- Chemin : `tests/robot/ui/<domaine>/<slug>.robot` ; domaine déduit de la
  vidéo — `web` par défaut, `fiori`/`ecc` si SAP, `desktop`, `mobile`.
- En-tête `Documentation` : titre métier, périmètre, référence
  `Spec: specs/<slug>.md (sha256:<12 hex>, <date du jour>)` — sha calculé par
  `(Get-FileHash specs\<slug>.md -Algorithm SHA256).Hash.Substring(0,12).ToLower()`
  — puis la commande d'exécution complète.
- Imports (jamais de `Library` en direct) :
  `Resource    ../../../../resources/common.resource`, les page objects
  concernés, `Variables    ../../../../variables/env_local.py`.
- `Test Tags    video-generated    <domaine>    <slug>`.
- Un test par scénario, dans l'ordre du plan ; chaque test rejouable seul
  (état ramené en `[Setup]` si besoin). Assertions relationnelles et
  locale-indépendantes ; les valeurs métier observées deviennent des
  `*** Variables ***` de la suite (ce sont des données, pas des
  localisateurs).

## 6. Créer les keywords manquants

- Dans `resources/page_objects/<écran>.resource` (un fichier par écran,
  gabarit dans son README, `Resource    ../common.resource` en tête ; si
  l'écran relève d'un canal secondaire, la `Library` de ce canal s'importe
  ici) : variables locators `${EMPTY}    # TODO` + keywords documentés
  (`[Documentation]` = rôle + `specs/<slug>.md` + horodatage vidéo).
- **Corps des keywords : l'implémentation réelle** avec la librairie du canal
  de l'écran (étape 3), chaque locator utilisé étant gardé par
  `Require Locator    ${LOCATOR}    specs/<slug>.md` (`common.resource`) —
  le `--dryrun` passe, l'exécution réelle échoue tant que le locator est
  vide. Zéro `Sleep` : attentes sur condition de la librairie. Réserver le
  corps `Fail Missing Locator    specs/<slug>.md` aux seuls keywords dont
  l'implémentation ne peut pas être écrite (action incertaine dans la vidéo —
  le noter dans la spec). Noms de keywords en **anglais** (convention SAPFX) ;
  documentation en français.
- Mettre à jour `variables/env_local.py` si la vidéo révèle l'URL ou le host
  du SUT (valeur observée, en commentaire sa provenance).

## 7. Valider (obligatoire)

- `$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry_<slug> tests/robot/ui/<domaine>/<slug>.robot`
- RC ≠ 0 → corriger (keyword non résolu, import cassé) et relancer. Ne
  jamais livrer sans dry-run vert.

## 8. Rapport final

Terminer par : scénarios produits ; librairie(s) retenue(s) à l'étape 3 ;
keywords réutilisés vs créés (implémentés avec locators TODO vs corps
`Fail Missing Locator`) ; liste des localisateurs à relever sur le SUT ;
chemins spec + suite + résultat du dry-run. Rappeler que l'exécution réelle
échouera tant que les TODO ne sont pas renseignés (convention 5) — c'est
voulu.
