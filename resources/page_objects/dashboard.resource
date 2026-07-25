*** Settings ***
Documentation    Tableau de bord OrangeHRM — créé depuis
...              specs/test-video-to-rf.md (vidéo [00:10 → 00:20]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${DASHBOARD_HEADER}     h6.oxd-topbar-header-breadcrumb-module:has-text("Dashboard")    # relevé SUT 2026-07-25
${USER_PROFILE_MENU}    .oxd-userdropdown-tab    # relevé SUT 2026-07-25


*** Keywords ***
Dashboard Should Be Displayed
    [Documentation]    Vérifie l'arrivée sur le tableau de bord : en-tête du
    ...                module Dashboard et menu utilisateur présents (session
    ...                ouverte). Aucune assertion sur les widgets (volatils).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:10 → 00:20].
    ...                TODO : relever les locators sur le SUT.
    Require Locator    ${DASHBOARD_HEADER}    specs/test-video-to-rf.md
    Require Locator    ${USER_PROFILE_MENU}    specs/test-video-to-rf.md
    Wait For Elements State    ${DASHBOARD_HEADER}    visible
    Wait For Elements State    ${USER_PROFILE_MENU}    visible
