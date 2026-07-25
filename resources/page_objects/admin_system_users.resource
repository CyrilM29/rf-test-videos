*** Settings ***
Documentation    Écran Admin > User Management > System Users — créé depuis
...              specs/test-video-to-rf.md (vidéo [00:15 → 00:28]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${SYSTEM_USERS_HEADER}          h5.oxd-table-filter-title:has-text("System Users")    # relevé SUT 2026-07-25
${SYSTEM_USERS_RECORD_COUNT}    .orangehrm-horizontal-padding span.oxd-text--span    # relevé SUT 2026-07-25 — libellé « (n) Records Found », ancrage structurel
${SYSTEM_USERS_GRID_ROWS}       .oxd-table-body > .oxd-table-card    # relevé SUT 2026-07-25


*** Keywords ***
System Users Page Should Be Displayed
    [Documentation]    Vérifie l'affichage de la page System Users.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:25].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${SYSTEM_USERS_HEADER}    specs/test-video-to-rf.md
    Wait For Elements State    ${SYSTEM_USERS_HEADER}    visible

Get Announced System Users Count
    [Documentation]    Retourne le nombre d'enregistrements annoncé par la page
    ...                (entier extrait du libellé, jamais le libellé localisé).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:25].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${SYSTEM_USERS_RECORD_COUNT}    specs/test-video-to-rf.md
    ${count}=    Get Integer From Label    ${SYSTEM_USERS_RECORD_COUNT}
    RETURN    ${count}

Get Displayed System Users Row Count
    [Documentation]    Retourne le nombre de lignes affichées dans la grille.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:25].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${SYSTEM_USERS_GRID_ROWS}    specs/test-video-to-rf.md
    ${count}=    Get Element Count    ${SYSTEM_USERS_GRID_ROWS}
    RETURN    ${count}
