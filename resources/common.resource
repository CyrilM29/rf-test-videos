*** Settings ***
Documentation    Keywords transverses du projet : setup/teardown génériques et
...              helpers indépendants de l'écran. Les keywords liés à UN écran
...              vivent dans page_objects/<écran>.resource, et les
...              localisateurs n'ont leur place QUE là-bas (convention 1).
...
...              Librairie de pilotage du SUT : Browser (Playwright), choisie
...              le 2026-07-25. Les suites générées n'importent jamais une
...              Library directement : elles passent par ce fichier.
Library          String
Library          Browser


*** Keywords ***
Fail Missing Locator
    [Documentation]    Corps standard d'un keyword de page object créé depuis
    ...                une vidéo, tant que ses localisateurs n'ont pas été
    ...                relevés sur le SUT (convention 5) : passe en --dryrun,
    ...                échoue en exécution réelle avec un message qui pointe
    ...                la spec d'origine.
    [Arguments]    ${spec}
    Fail    msg=Localisateurs à relever sur le SUT : voir ${spec}

Require Locator
    [Documentation]    Garde-fou d'un keyword de page object dont le corps est
    ...                déjà implémenté avec la librairie de pilotage mais dont
    ...                le localisateur n'a pas encore été relevé sur le SUT
    ...                (convention 5) : passe en --dryrun, échoue en exécution
    ...                réelle tant que la variable de locator est vide, avec un
    ...                message qui pointe la spec d'origine.
    [Arguments]    ${locator}    ${spec}
    IF    $locator == ''
        Fail    msg=Localisateur à relever sur le SUT : voir ${spec}
    END

Get Integer From Label
    [Documentation]    Extrait le premier entier d'un libellé lu à l'écran
    ...                (« (4) Records Found » → 4) ; retourne 0 si aucun
    ...                chiffre (état vide type « No Records Found »). Sert les
    ...                assertions locale-indépendantes (convention 3) : on ne
    ...                compare jamais le libellé lui-même.
    [Arguments]    ${locator}
    ${text}=    Get Text    ${locator}
    ${count}=    Evaluate    (lambda m: int(m.group()) if m else 0)(re.search('[0-9]+', $text))    modules=re
    RETURN    ${count}
