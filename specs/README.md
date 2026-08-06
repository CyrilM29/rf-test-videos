# specs/ : plans de test issus des vidéos

Plans de test **lisibles métier**, au format Markdown, produits par la skill
`/video-to-rf` (lecture des frames + voix off d'une vidéo de test manuel) et
consommés pour générer les suites de `tests/robot/ui/…`. Format hérité du
projet SAPFX (`E:\QA_GenAI\SAP_library_custom\specs\`).

Règles du répertoire :

- **Un fichier par vidéo/domaine métier**, kebab-case, même slug que la vidéo
  (`videos/demo-connexion.mp4` → `specs/demo-connexion.md`).
- Rédigé **en français** ; noms de keywords et ids techniques en anglais.
- Un plan décrit des **scénarios en langage métier**, jamais d'id d'élément
  ni de CSS/XPath dans les étapes (convention 1) ; ce qui est lu à l'écran va
  dans « Données observées » / « Points de vigilance », comme notes factuelles
  pour la génération.
- Un plan est **ancré dans l'observé** : uniquement ce que la vidéo montre ou
  dit (voix off). Ce qui est incertain est marqué comme tel, jamais inventé.
- La suite générée référence son plan (sha256) ; quand le flux métier change,
  on refait/met à jour le plan puis on régénère : on n'édite pas les
  localisateurs à la main dans les tests (convention 4).
- Le sous-répertoire `istqb/` accueille les **plans de test + cas de test
  ISTQB** (`<slug>.istqb.md`) produits par `/video-to-istqb` : documentation
  de conception au gabarit ISTQB / ISO 29119-3, bloc `replay` YAML normalisé
  rejouable par une IA quel que soit le framework, clé `evidence` citant la
  frame vidéo. Voir `specs/istqb/README.md` ; ces documents ne remplacent
  pas les plans ci-dessus et restent hors du périmètre de `check_specs.py`.

Gabarit d'un plan :

```markdown
# <Titre métier>

- **Canal** : web | fiori | ecc | desktop | mobile (plusieurs si hybride)
- **Pilotage** : <librairie(s) retenue(s) au checkpoint, par canal>
- **Système / URL** : <observé dans la vidéo>
- **Source vidéo** : `videos/<fichier>` (durée mm:ss, voix off fr | aucune)
- **Préconditions** : <déduites de l'état initial visible : session, données…>

## Données observées

<valeurs réellement visibles ou dites : comptes, libellés, volumétries,
formats, messages, notes factuelles pour la génération>

## Scénarios

### 1. <Nom du scénario>
- **Horodatage vidéo** : [mm:ss → mm:ss]
- **Étapes** : numérotées, une étape = de préférence un keyword métier existant.
- **Résultat attendu** : assertions indépendantes de la locale, relationnelles.
- **Keywords métier manquants** : à créer en page objects (locators TODO).

## Points de vigilance

## Écarts constatés à la génération

## Fidélité visuelle

<renseignée par /finalize-rf : date du contrôle, verdict par scénario
(conforme | écart) en comparant les frames de la vidéo aux captures de
l'exécution réelle : les écarts de données sont attendus, seuls comptent
structure et flux>
```
