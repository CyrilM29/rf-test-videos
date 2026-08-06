---
mode: agent
description: Rédige un plan de test + cas de test ISTQB (specs/istqb/) depuis une vidéo de test manuel, avec ou sans suite RF (vidéo brute préparée au besoin, spec et suite cumulables). Argument = slug, chemin de spec, ou chemin de vidéo.
---

# /video-to-istqb : vidéo → plan de test et cas de test ISTQB

Concepteur de tests, sortie INDÉPENDANTE de la suite RF : depuis une même
vidéo on peut produire la suite (`/video-to-rf`), le plan ISTQB (ce prompt),
ou les deux. Aucune session live. Conventions de `CLAUDE.md` en permanence
(zéro localisateur hors `hint`, zéro attente fixe, assertions
locale-indépendantes, jamais de tiret cadratin U+2014). **Un modèle avec
vision est requis** si la vidéo doit être lue : sinon s'arrêter et le dire.

## 1. Sources

- Argument = slug, `specs/<slug>.md` ou `videos/<fichier>.mp4` ; sans
  argument, lister `specs/*.md` et `videos/` et demander.
- Spec présente = source la plus riche ; sinon vidéo préparée
  (`work/<slug>/`) ; sinon vidéo brute : lancer
  `python scripts/prepare_video.py <vidéo>` puis lire
  `work/<slug>/storyboard.md` et TOUTES les frames dans l'ordre.
- Cumuler ce qui existe : spec + storyboard/frames (preuve horodatée) +
  suite générée et page objects (traçabilité, localisateurs relevés).

## 2. Rédiger `specs/istqb/<slug>.istqb.md` (contrat : specs/istqb/README.md)

UN document français, gabarit ISTQB / ISO 29119-3 partagé de l'écosystème :
en-tête (provenance datée, `TP-<slug>` translittéré, canal, système) ;
1. Objectif et périmètre ; 2. Préconditions et données ; 3. Critères
d'entrée/sortie ; 4. Cas de test : un `TC-nn` par scénario, priorité
justifiée, tableau `# | Action | Données | Résultat attendu`
(locale-indépendant), postconditions, bloc `replay` YAML normalisé
(`click`/`fill`/`fill_secret`/`press_key`/`wait`/`assert_*`… ; `target` =
libellé humain vu à l'écran ; `evidence` = frame/horodatage ; `hint` = le
localisateur des page objects s'il existe, sinon note « à relever,
/finalize-rf ») ; 5. Traçabilité TC ↔ spec ↔ vidéo ↔ suite (écarts nommés) ;
6. Risques (vigilances de la spec, fidélité visuelle, dérive des hints).

## Règles

Rien d'inventé (« à compléter » + question sinon) ; un mot de passe vu ou
dicté dans la vidéo devient `fill_secret`, valeur JAMAIS recopiée (contrat
`Secret:` en ligne de commande) ; aucune durée d'attente ; n'écrit que sous
`specs/istqb/` (plus le `work/` jetable) ; relancer met à jour le document.

## 3. Auto-contrôle puis rapport

Gabarit respecté, tableau + replay par TC,
`python scripts/check_no_em_dash.py specs/istqb/<slug>.istqb.md`, puis
rapport en français : chemin, liste des TC (id, titre, priorité, source),
écarts de traçabilité, « à compléter » restants avec leur question.
