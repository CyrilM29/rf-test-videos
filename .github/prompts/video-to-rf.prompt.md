---
mode: agent
description: Transcrit une vidéo de test manuel en plan de test (specs/) puis en suite Robot Framework validée en dry-run. Argument = chemin de la vidéo (+ options prepare_video.py).
---

# /video-to-rf — vidéo → spec → suite Robot Framework

Suivre TOUTES les étapes, dans l'ordre. Les conventions de `CLAUDE.md`
s'appliquent en permanence (1 : zéro localisateur dans les tests ; 2 : zéro
attente fixe ; 3 : assertions locale-indépendantes ; 4 : spec = source de
vérité ; 5 : keyword manquant explicite ; 6 : `work/` et `results/`
jetables). **Un modèle avec vision est requis** (lecture de frames JPEG) —
sinon s'arrêter et le dire.

## 1. Préparer

- L'argument (texte après la commande) = chemin de la vidéo + options
  éventuelles. Vérifier que le fichier existe ; sinon lister `videos/` et
  s'arrêter avec un message clair.
- Lancer dans le terminal (long au premier run : téléchargement du modèle
  whisper) : `python scripts/prepare_video.py <vidéo> [options]`
- Lire `work/<slug>/meta.json` et `work/<slug>/audio_transcript.md`.

## 2. Lire la vidéo (frames + voix off)

- Lire TOUTES les frames de `work/<slug>/frames/` en ordre chronologique (le
  nom porte l'horodatage). Ne jamais sous-échantillonner en silence.
- La voix off donne l'intention, la frame donne l'observé ; en cas de
  contradiction, l'observé gagne et l'écart est noté. Ce qui est flou est
  noté comme tel — jamais inventé.

## 3. Checkpoint librairies (AVANT toute génération)

- Déduire les canaux en action (web, desktop, SAP, mobile, API… — plusieurs
  possibles) et inventorier les `Library` déjà branchées dans
  `resources/**/*.resource`.
- Canal non couvert → **s'arrêter et demander dans le chat** quelle(s)
  librairie(s) retenir (recommandation argumentée, hybridation possible :
  une librairie par canal). Acter : canal principal dans
  `resources/common.resource`, canal secondaire dans les seuls page objects
  de ses écrans, dépendance épinglée dans `requirements.txt`, ligne
  « Pilotage » dans la spec.

## 4. Écrire la spec

- `specs/<slug>.md` selon le gabarit de `specs/README.md`. Scénarios
  autonomes, étapes en langage métier (aucun id/CSS/XPath), données lues à
  l'écran dans « Données observées » / « Points de vigilance ».
- Inventorier les keywords existants (`*** Keywords ***` dans
  `resources/**/*.resource`) avant d'écrire ; manquants → section
  « Keywords métier manquants ».

## 5. Générer la suite

- `tests/robot/ui/<domaine>/<slug>.robot` (domaine : web par défaut,
  fiori/ecc si SAP, desktop, mobile). En-tête `Documentation` avec
  `Spec: specs/<slug>.md (sha256:<12 hex>, <date>)` et la commande
  d'exécution complète. Imports : `Resource` uniquement +
  `Variables    ../../../../variables/env_local.py`.
- `Test Tags    video-generated    <domaine>    <slug>`. Un test par
  scénario, rejouable seul ; valeurs métier observées en `*** Variables ***`.

## 6. Créer les keywords manquants

- Un `.resource` par écran dans `resources/page_objects/` (gabarit dans son
  README). Variables locators `${EMPTY}    # TODO` ; corps = implémentation
  réelle avec la librairie du canal, chaque locator gardé par
  `Require Locator    ${LOC}    specs/<slug>.md`. `Fail Missing Locator`
  réservé aux actions trop incertaines (écart noté dans la spec).
- Mettre à jour `variables/env_local.py` si la vidéo révèle l'URL du SUT.

## 7. Valider (obligatoire)

- `$env:PYTHONIOENCODING='utf-8'; robot --dryrun --outputdir results/dry_<slug> tests/robot/ui/<domaine>/<slug>.robot`
- RC ≠ 0 → corriger et relancer. Ne jamais livrer sans dry-run vert.

## 8. Rapport final

Scénarios produits ; librairie(s) retenue(s) ; keywords réutilisés vs créés ;
locators TODO à relever (suite : `/finalize-rf <slug>`) ; chemins spec +
suite + résultat du dry-run. Rappeler que l'exécution réelle échoue tant que
les TODO ne sont pas relevés — c'est voulu.
