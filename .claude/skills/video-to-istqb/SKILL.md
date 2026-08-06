---
name: video-to-istqb
description: Rédige un plan de test + cas de test ISTQB (specs/istqb/, lisible humain ET rejouable par une IA quel que soit le framework) depuis une vidéo de test manuel, avec ou sans suite RF : vidéo brute (préparée au besoin), spec issue de /video-to-rf et suite générée sont des sources cumulables. Argument = slug, chemin de spec, ou chemin de vidéo.
argument-hint: <slug | specs/x.md | videos/x.mp4> [options prepare_video.py]
---

# /video-to-istqb : vidéo → plan de test et cas de test ISTQB

Concepteur de tests. Porté de l'agent `sap-istqb` du projet SAPFX (et de son
frère `rf-istqb`), adapté à la matière première de CE dépôt : la **preuve
vidéo**. Sortie INDÉPENDANTE de la suite RF : depuis une même vidéo on peut
produire la suite (`/video-to-rf`), le plan ISTQB (cette skill), ou les deux ;
quand les deux existent, chacun enrichit l'autre (traçabilité, hints). Aucune
session live, aucun accès au SUT. Les conventions du CLAUDE.md s'appliquent
en permanence (1 : zéro localisateur hors des champs `hint` ; 2 : zéro
attente fixe ; 3 : assertions locale-indépendantes ; 4 : la spec reste la
source de vérité ; jamais de tiret cadratin, U+2014).

## 1. Choisir les sources

- `$ARGUMENTS` = un slug (`demo-connexion`), un chemin de spec
  (`specs/demo-connexion.md`) ou un chemin de vidéo
  (`videos/demo-connexion.mp4`). Sans argument : lister `specs/*.md` (hors
  README.md) ET `videos/`, et demander quoi documenter.
- Trois états d'entrée possibles :
  - **La spec existe** (`specs/<slug>.md`) : c'est la source la plus riche
    (scénarios, données observées, vigilances, verdicts de fidélité).
  - **Seulement la vidéo préparée** (`work/<slug>/` présent) : partir du
    storyboard et des frames ; le document naîtra sans spec ni suite (la
    traçabilité le dira, et proposera `/video-to-rf`).
  - **Seulement la vidéo brute** (`videos/<fichier>.mp4`) : la préparer
    d'abord, comme `/video-to-rf` : `python scripts/prepare_video.py
    <vidéo> [options]` (timeout ≥ 10 min au premier run), puis lire
    `work/<slug>/storyboard.md` et TOUTES les frames dans l'ordre (lots de
    6 à 8 Read parallèles ; un modèle avec vision est requis : sinon
    s'arrêter et le dire). L'observé prime sur la voix off en cas de
    contradiction, l'écart est noté.
- Sources cumulables, par ordre de richesse (lire TOUT ce qui existe) :
  1. `specs/<slug>.md` : la spec issue de la vidéo.
  2. `work/<slug>/storyboard.md` + `meta.json` : la **preuve vidéo**
     (frames horodatées + voix off). C'est l'ancrage unique de ce dépôt :
     chaque étape peut citer sa frame (`evidence`).
  3. `tests/robot/ui/**/<slug>.robot` + ses page objects
     (`resources/page_objects/`) : pour la traçabilité, et pour les
     localisateurs réels quand `/finalize-rf` les a relevés.
- Aucune session live : la seule production autorisée hors `specs/istqb/`
  est le `work/<slug>/` de `prepare_video.py` (jetable, convention du
  dépôt).

## 2. Rédiger le document (gabarit partagé de l'écosystème)

Écrire `specs/istqb/<slug>.istqb.md` (créer le dossier au besoin ; contrat
détaillé : `specs/istqb/README.md`). UN document couvrant les deux niveaux
ISTQB (ISO 29119-3), en français :

- **En-tête** : titre métier ; blockquote de provenance (sources datées :
  spec, vidéo, suite) ; `- **Identifiant** : TP-<slug>` (kebab-case, accents
  translittérés) ; canal ; système/URL observé ; références.
- **1. Objectif et périmètre** : rédigés depuis la spec et la voix off
  (l'intention) ; hors périmètre explicite.
- **2. Préconditions et données de test** : état initial visible en début de
  vidéo, données observées de la spec. Une valeur lisible à l'écran dans un
  champ mot de passe ne se recopie JAMAIS (voir règles).
- **3. Critères d'entrée / de sortie.**
- **4. Cas de test** : un `TC-nn` par scénario de la spec, priorité
  justifiée, tableau `# | Action | Données | Résultat attendu`
  (résultats attendus locale-indépendants : comptages, états visibles,
  jamais un libellé localisé fragile), postconditions, puis le bloc
  `replay` YAML :

  ```yaml
  test_case: TC-01
  title: '<titre>'
  channel: web
  steps:
    - action: fill            # navigate, click, fill, fill_secret, select,
      target: 'champ Username' # check, uncheck, press_key, wait, api_call,
      value: 'Admin'           # assert_present, assert_text, assert_value,
      evidence: 'frame 03 @ 00:12'   # assert_count, locate, raw
      hint: {engine: 'css', locator: '#username'}
  ```

  `target` = le libellé humain vu à l'écran ; `evidence` (spécifique à ce
  dépôt) = la frame/horodatage du storyboard qui prouve l'étape ; `hint`
  SEULEMENT si un localisateur existe déjà dans les page objects (engine =
  sa stratégie : `css`, `testid`, `role`…) ; sinon pas de `hint`, avec la
  note « localisateur à relever (/finalize-rf) ». Jamais d'attente en durée :
  `wait` est une condition (chargement fini, élément visible).
- **5. Traçabilité** : tableau TC ↔ scénario de la spec ↔ vidéo (plage
  d'horodatages) ↔ suite générée (et son marqueur `Spec: … sha256`).
  Nommer les écarts : scénario sans suite, suite sans locators relevés,
  étape vue en vidéo mais absente de la spec.
- **6. Risques et points de vigilance** : repris de la spec (vigilances,
  verdicts de fidélité visuelle), plus les génériques : dérive des
  localisateurs des `hint`, jamais de `time.sleep` au rejeu.

## Règles (jamais enfreintes)

- **Ancré dans l'observé** : chaque valeur, chaque attendu vient de la spec,
  du storyboard ou de la suite. Ce qu'aucune source n'appuie reste
  « à compléter » avec une question d'une ligne pour l'humain.
- **Jamais de secret** : un mot de passe saisi dans la vidéo devient
  `fill_secret` (note : « valeur à fournir au rejeu, contrat `Secret:` en
  ligne de commande »), même si la valeur est lisible à l'écran ou dictée
  en voix off. Aucun identifiant réel dans le document.
- **Localisateurs cantonnés aux `hint`** : le tableau humain parle métier
  (miroir de la convention 1 : les suites les cantonnent aux page objects de
  `resources/`).
- Cette skill n'écrit QUE sous `specs/istqb/` (plus, au besoin, le
  `work/<slug>/` jetable produit par `prepare_video.py`) : jamais dans
  `tests/`, `resources/` ni `specs/*.md`.
- Relancer la skill sur les mêmes sources MET À JOUR le document existant
  (identifiant stable).

## 3. Auto-contrôle puis rapport

- Vérifier : gabarit respecté, chaque TC a tableau ET bloc replay, zéro
  cadratin (`python scripts/check_no_em_dash.py specs/istqb/<slug>.istqb.md`),
  rien d'inventé, aucun localisateur hors `hint`, aucune durée d'attente,
  aucun secret.
- Rapport (en français) : chemin du document, liste des TC (id, titre,
  priorité, scénario source), écarts de traçabilité, et chaque
  « à compléter » restant avec sa question.
