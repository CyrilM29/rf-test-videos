*** Settings ***
Documentation    Écran Leave > Leave List : créé depuis
...              specs/test-video-to-rf.md (vidéo [00:33 → 00:38]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${LEAVE_LIST_HEADER}             h5.oxd-table-filter-title:has-text("Leave List")    # relevé SUT 2026-07-25
${LEAVE_STATUS_FILTER}           .oxd-grid-item:has(label:has-text("Show Leave with Status")) .oxd-select-text    # relevé SUT 2026-07-25, composant custom ancré sur son label
${LEAVE_STATUS_OPTION_TEMPLATE}    .oxd-select-dropdown [role="option"] >> text="{status}"    # relevé SUT 2026-07-25 : validé avec Pending Approval et Rejected
${LEAVE_SEARCH_BUTTON}           button[type="submit"]:has-text("Search")    # relevé SUT 2026-07-25
${LEAVE_RESULT_AREA}             .orangehrm-container    # relevé SUT 2026-07-25 : porte la grille OU l'état vide


*** Keywords ***
Leave List Page Should Be Displayed
    [Documentation]    Vérifie l'affichage de la page Leave List.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:35].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${LEAVE_LIST_HEADER}    specs/test-video-to-rf.md
    Wait For Elements State    ${LEAVE_LIST_HEADER}    visible

Search Leaves With Status
    [Documentation]    Sélectionne le statut donné (période par défaut
    ...                conservée) et lance la recherche.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:35].
    ...                TODO : relever les locators sur le SUT.
    [Arguments]    ${status}
    Require Locator    ${LEAVE_STATUS_FILTER}    specs/test-video-to-rf.md
    Require Locator    ${LEAVE_STATUS_OPTION_TEMPLATE}    specs/test-video-to-rf.md
    Require Locator    ${LEAVE_SEARCH_BUTTON}    specs/test-video-to-rf.md
    Click    ${LEAVE_STATUS_FILTER}
    ${option}=    Format String    ${LEAVE_STATUS_OPTION_TEMPLATE}    status=${status}
    Click    ${option}
    Click    ${LEAVE_SEARCH_BUTTON}

Leave Search Result Should Be Displayed
    [Documentation]    Vérifie qu'un état résultat est affiché après recherche :
    ...                grille de congés OU état vide explicite (en vidéo :
    ...                résultat vide) : le locator couvre les deux états.
    ...                Attente sur condition, jamais de Sleep.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:35 → 00:38].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${LEAVE_RESULT_AREA}    specs/test-video-to-rf.md
    Wait For Elements State    ${LEAVE_RESULT_AREA}    visible
