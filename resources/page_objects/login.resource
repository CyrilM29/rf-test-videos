*** Settings ***
Documentation    Écran de connexion OrangeHRM : créé depuis
...              specs/test-video-to-rf.md (vidéo [00:00 → 00:15]).
...              Corps implémentés avec Browser ; locators TODO à relever
...              sur le SUT (non observables en vidéo).
Resource         ../common.resource


*** Variables ***
# Chemin observé dans la barre d'adresse de la vidéo (donnée, pas un TODO).
${LOGIN_PAGE_PATH}         /web/index.php/auth/login
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${LOGIN_USERNAME_FIELD}    input[name="username"]    # relevé SUT 2026-07-25
${LOGIN_PASSWORD_FIELD}    input[name="password"]    # relevé SUT 2026-07-25
${LOGIN_SUBMIT_BUTTON}     button.orangehrm-login-button    # relevé SUT 2026-07-25


*** Keywords ***
Open Login Page
    [Documentation]    Ouvre un navigateur sur la page de connexion du SUT
    ...                (${SUT_BASE_URL}${LOGIN_PAGE_PATH}) et attend le
    ...                formulaire. Source : specs/test-video-to-rf.md,
    ...                vidéo [00:00]. TODO : relever le locator du champ.
    New Browser    ${SUT_BROWSER}    headless=${SUT_HEADLESS}
    New Context
    New Page    ${SUT_BASE_URL}${LOGIN_PAGE_PATH}
    Require Locator    ${LOGIN_USERNAME_FIELD}    specs/test-video-to-rf.md
    Wait For Elements State    ${LOGIN_USERNAME_FIELD}    visible

Log In With
    [Documentation]    Saisit identifiant/mot de passe et valide la connexion.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:00 → 00:10].
    ...                TODO : relever les locators sur le SUT.
    [Arguments]    ${user}    ${password}
    Require Locator    ${LOGIN_USERNAME_FIELD}    specs/test-video-to-rf.md
    Require Locator    ${LOGIN_PASSWORD_FIELD}    specs/test-video-to-rf.md
    Require Locator    ${LOGIN_SUBMIT_BUTTON}    specs/test-video-to-rf.md
    Fill Text    ${LOGIN_USERNAME_FIELD}    ${user}
    Fill Secret    ${LOGIN_PASSWORD_FIELD}    $password
    Click    ${LOGIN_SUBMIT_BUTTON}

Ensure Logged In
    [Documentation]    Remise en état pour un scénario rejouable seul : ouvre
    ...                navigateur + session ${user} si aucune session n'est
    ...                active (la librairie Browser ferme le contexte à la fin
    ...                de chaque test). Source : specs/test-video-to-rf.md,
    ...                scénarios 2 à 6.
    [Arguments]    ${user}    ${password}
    TRY
        ${url}=    Get Url
    EXCEPT
        # Aucune page active (la librairie ferme les pages à la fin de chaque
        # test, auto-close TEST) : on rouvre et on se connecte.
        Open Login Page
        Log In With    ${user}    ${password}
        RETURN
    END
    IF    'auth/login' in $url
        Log In With    ${user}    ${password}
    END
