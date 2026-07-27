*** Settings ***
Documentation    Parcours de consultation OrangeHRM — connexion, référentiels
...              (utilisateurs système, employés), congés en attente et
...              filtrage des candidats au recrutement, jusqu'à l'ouverture du
...              formulaire d'ajout de candidat (démo publique OrangeHRM OS 5.9).
...              Pilotage : Browser (Playwright) via common.resource.
...
...              Spec: specs/test-video-to-rf.md (sha256:0f4691ce36e8, 2026-07-27)
...
...              Exécution (mot de passe jamais committé — convention projet) :
...              $env:PYTHONIOENCODING='utf-8'; robot -v APP_PASSWORD:admin123
...              --outputdir results/test-video-to-rf
...              tests/robot/ui/web/test-video-to-rf.robot
Resource         ../../../../resources/common.resource
Resource         ../../../../resources/page_objects/login.resource
Resource         ../../../../resources/page_objects/navigation.resource
Resource         ../../../../resources/page_objects/dashboard.resource
Resource         ../../../../resources/page_objects/admin_system_users.resource
Resource         ../../../../resources/page_objects/pim_employee_list.resource
Resource         ../../../../resources/page_objects/leave_list.resource
Resource         ../../../../resources/page_objects/recruitment_candidates.resource
Resource         ../../../../resources/page_objects/recruitment_add_candidate.resource
Variables        ../../../../variables/env_local.py
Test Tags        video-generated    web    test-video-to-rf


*** Variables ***
# Données métier observées dans la vidéo (ce sont des données, pas des locators).
${APP_USER}                    Admin
# Mot de passe passé en CLI : -v APP_PASSWORD:admin123 (public, affiché par la
# démo elle-même — mais jamais committé, convention env_local.py).
${APP_PASSWORD}                ${EMPTY}
${LEAVE_STATUS_PENDING}        Pending Approval
${FILTER_JOB_TITLE}            Account Assistant
${FILTER_VACANCY}              Junior Account Assistant
${FILTER_HIRING_MANAGER}       Rahul Patil
${FILTER_STATUS}               Rejected


*** Test Cases ***
Connexion Au Portail OrangeHRM
    [Documentation]    Scénario 1 — vidéo [00:00 → 00:15] : connexion avec le
    ...                compte de test et arrivée sur le tableau de bord.
    [Setup]    Open Login Page
    Log In With    ${APP_USER}    ${APP_PASSWORD}
    Dashboard Should Be Displayed

Consultation Des Utilisateurs Systeme
    [Documentation]    Scénario 2 — vidéo [00:15 → 00:28] : la liste des
    ...                utilisateurs système est affichée ; compteur annoncé > 0
    ...                et égal au nombre de lignes (relationnel, même run).
    [Setup]    Ensure Logged In    ${APP_USER}    ${APP_PASSWORD}
    Go To Module    Admin
    System Users Page Should Be Displayed
    ${announced}=    Get Announced System Users Count
    ${displayed}=    Get Displayed System Users Row Count
    Should Be True    ${announced} > 0
    Should Be Equal As Integers    ${announced}    ${displayed}

Consultation De La Liste Des Employes
    [Documentation]    Scénario 3 — vidéo [00:28 → 00:33] : la liste des
    ...                employés est affichée ; compteur annoncé > 0 et ≥ lignes
    ...                de la première page (grille paginée).
    [Setup]    Ensure Logged In    ${APP_USER}    ${APP_PASSWORD}
    Go To Module    PIM
    Employee List Page Should Be Displayed
    ${announced}=    Get Announced Employee Count
    ${displayed}=    Get Displayed Employee Row Count
    Should Be True    ${announced} > 0
    Should Be True    ${announced} >= ${displayed}

Recherche Des Conges En Attente
    [Documentation]    Scénario 4 — vidéo [00:33 → 00:38] : recherche des
    ...                congés au statut « Pending Approval » sur la période par
    ...                défaut ; un état résultat (grille ou vide explicite) est
    ...                affiché — en vidéo le résultat était vide.
    [Setup]    Ensure Logged In    ${APP_USER}    ${APP_PASSWORD}
    Go To Module    Leave
    Leave List Page Should Be Displayed
    Search Leaves With Status    ${LEAVE_STATUS_PENDING}
    Leave Search Result Should Be Displayed

Filtrage Des Candidats Au Recrutement
    [Documentation]    Scénario 5 — vidéo [00:38 → 00:58] : le nombre de
    ...                candidats filtrés (poste/offre/responsable/statut) est
    ...                inférieur ou égal au total sans filtre, mesurés dans le
    ...                même run (en vidéo : 60 puis 0 — non rejoués en dur).
    [Setup]    Ensure Logged In    ${APP_USER}    ${APP_PASSWORD}
    Go To Module    Recruitment
    Candidates Page Should Be Displayed
    ${total}=    Get Announced Candidate Count
    Filter Candidates    ${FILTER_JOB_TITLE}    ${FILTER_VACANCY}
    ...    ${FILTER_HIRING_MANAGER}    ${FILTER_STATUS}
    ${filtered}=    Get Announced Candidate Count
    Should Be True    ${filtered} <= ${total}
    [Teardown]    Reset Candidate Filters

Ouverture Puis Abandon Du Formulaire D Ajout De Candidat
    [Documentation]    Scénario 6 — vidéo [00:58 → 01:10] : le formulaire Add
    ...                Candidate s'affiche, l'abandon ramène à la liste avec un
    ...                compteur inchangé (aucune création).
    [Setup]    Ensure Logged In    ${APP_USER}    ${APP_PASSWORD}
    Go To Module    Recruitment
    Candidates Page Should Be Displayed
    ${before}=    Get Announced Candidate Count
    Open Add Candidate Form
    Add Candidate Form Should Be Displayed
    Cancel Candidate Creation
    Candidates Page Should Be Displayed
    ${after}=    Get Announced Candidate Count
    Should Be Equal As Integers    ${before}    ${after}
