# specs/istqb/ : plans de test et cas de test ISTQB

Documents de **conception de test** au gabarit ISTQB / ISO 29119-3, un fichier
par vidéo/domaine métier (`<slug>.istqb.md`, même slug que la vidéo et la
spec), produits par la skill **`/video-to-istqb`** (Claude Code) ou son
équivalent Copilot (`.github/prompts/video-to-istqb.prompt.md`). Gabarit
partagé avec l'écosystème SAPFX / rf-test-agents / rf-web-recorder.

Sortie **indépendante** de la suite RF : depuis une même vidéo on produit la
suite (`/video-to-rf`), le plan ISTQB (cette skill), ou les deux.

Chaque document couvre les deux niveaux :

- **plan de test** : identifiant `TP-<slug>`, objectif et périmètre,
  préconditions et données observées, critères d'entrée/sortie, risques
  (dont les verdicts de fidélité visuelle quand ils existent) ;
- **cas de test** : un `TC-nn` par scénario, tableau
  `# | Action | Données | Résultat attendu`, postconditions, et un bloc
  `replay` YAML **normalisé** : actions neutres vis-à-vis du framework
  (`click`, `fill`, `press_key`, `assert_text`…), cible en langage humain
  (le libellé vu à l'écran), clé `evidence` propre à ce dépôt (frame et
  horodatage du storyboard qui prouvent l'étape), localisateur relégué en
  `hint` seulement quand les page objects le portent déjà (moteur = la
  stratégie : `css`, `testid`, `role`…). C'est ce bloc qui rend le cas
  rejouable par une IA avec n'importe quel framework de test.

Règles du répertoire :

- **Ancré dans l'observé** : chaque valeur, chaque attendu vient de la spec,
  du storyboard ou de la suite ; ce qu'aucune source n'appuie reste
  « à compléter ».
- **Résultats attendus indépendants de la locale** : comptages, états
  visibles, jamais un libellé localisé fragile.
- **Aucune attente fixe** dans les blocs replay : une attente est toujours
  une condition, jamais une durée.
- **Aucun secret** : un mot de passe vu ou dicté dans la vidéo devient
  `fill_secret`, sa valeur n'est JAMAIS recopiée (contrat `Secret:` en ligne
  de commande).
- Ces documents sont de la documentation : ils ne remplacent ni les specs
  (`specs/*.md`, la source de vérité des suites) ni les suites de
  `tests/robot/`, et restent hors du périmètre de `check_specs.py`.
