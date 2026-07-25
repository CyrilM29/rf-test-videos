*** Settings ***
Documentation    Écran PIM > Employee List — créé depuis
...              specs/test-video-to-rf.md (vidéo [00:28 → 00:33]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${EMPLOYEE_LIST_HEADER}          h5.oxd-table-filter-title:has-text("Employee Information")    # relevé SUT 2026-07-25 — titre du panneau de filtres PIM
${EMPLOYEE_LIST_RECORD_COUNT}    .orangehrm-horizontal-padding span.oxd-text--span    # relevé SUT 2026-07-25 — ancrage structurel
${EMPLOYEE_LIST_GRID_ROWS}       .oxd-table-body > .oxd-table-card    # relevé SUT 2026-07-25


*** Keywords ***
Employee List Page Should Be Displayed
    [Documentation]    Vérifie l'affichage de la liste des employés.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:30].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${EMPLOYEE_LIST_HEADER}    specs/test-video-to-rf.md
    Wait For Elements State    ${EMPLOYEE_LIST_HEADER}    visible

Get Announced Employee Count
    [Documentation]    Retourne le nombre d'employés annoncé par la page
    ...                (entier extrait du libellé, jamais le libellé localisé).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:30].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${EMPLOYEE_LIST_RECORD_COUNT}    specs/test-video-to-rf.md
    ${count}=    Get Integer From Label    ${EMPLOYEE_LIST_RECORD_COUNT}
    RETURN    ${count}

Get Displayed Employee Row Count
    [Documentation]    Retourne le nombre de lignes affichées sur la première
    ...                page de la grille (grille paginée).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:30].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${EMPLOYEE_LIST_GRID_ROWS}    specs/test-video-to-rf.md
    ${count}=    Get Element Count    ${EMPLOYEE_LIST_GRID_ROWS}
    RETURN    ${count}
