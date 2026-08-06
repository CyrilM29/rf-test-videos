# page_objects/ : un fichier `.resource` par écran

Seul emplacement du dépôt où vivent les **localisateurs** (convention 1) :
variables de locators + keywords propres à un écran. Les suites de
`tests/robot/` parlent métier et ne référencent que ces keywords.

Une vidéo ne montre jamais les localisateurs : tout keyword créé par
`/video-to-rf` naît donc avec des locators TODO (convention 5). Depuis le
checkpoint librairies de la skill, le **corps du keyword est écrit tout de
suite** avec la librairie du canal de l'écran ; chaque locator utilisé est
gardé par `Require Locator` (`common.resource`), qui échoue tant que la
variable est vide. Le `--dryrun` passe dans tous les états ; l'exécution
réelle n'est verte qu'une fois les locators relevés sur le SUT (inspecteur,
recorder…). Le corps `Fail Missing Locator` reste réservé aux keywords dont
l'action observée est trop incertaine pour être implémentée.

Hybridation multi-canaux : la librairie du canal principal vit dans
`common.resource` ; celle d'un canal secondaire (desktop, SAP…) s'importe en
`Library` **ici**, dans les seuls page objects de ce canal, jamais dans les
suites.

Gabarit (noms de keywords **en anglais**, convention SAPFX ; documentation en
français ; exemple avec Browser) :

```robotframework
*** Settings ***
Documentation    Écran de connexion : créé depuis specs/demo-connexion.md.
Resource         ../common.resource

*** Variables ***
# TODO locators à relever sur le SUT (non observables dans une vidéo)
${LOGIN_USER_FIELD}       ${EMPTY}    # TODO
${LOGIN_PASS_FIELD}       ${EMPTY}    # TODO
${LOGIN_SUBMIT_BUTTON}    ${EMPTY}    # TODO

*** Keywords ***
Log In With
    [Documentation]    Saisit identifiant/mot de passe et valide.
    ...                Source : specs/demo-connexion.md, vidéo [00:12 → 00:31].
    ...                TODO : relever les locators sur le SUT.
    [Arguments]    ${user}    ${password}
    Require Locator    ${LOGIN_USER_FIELD}    specs/demo-connexion.md
    Require Locator    ${LOGIN_PASS_FIELD}    specs/demo-connexion.md
    Require Locator    ${LOGIN_SUBMIT_BUTTON}    specs/demo-connexion.md
    Fill Text      ${LOGIN_USER_FIELD}    ${user}
    Fill Secret    ${LOGIN_PASS_FIELD}    $password
    Click          ${LOGIN_SUBMIT_BUTTON}
```
