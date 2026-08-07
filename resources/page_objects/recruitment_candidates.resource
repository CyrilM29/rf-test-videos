*** Comments ***
Copyright 2026 Cyril Montiel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


*** Settings ***
Documentation    Écran Recruitment > Candidates (liste + filtres) : créé depuis
...              specs/test-video-to-rf.md (vidéo [00:38 → 01:10]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${CANDIDATES_HEADER}                     h5.oxd-table-filter-title:has-text("Candidates")    # relevé SUT 2026-07-25
${CANDIDATES_RECORD_COUNT}               .orangehrm-horizontal-padding span.oxd-text--span    # relevé SUT 2026-07-25 : « (n) Records Found » OU « No Records Found » (0)
${CANDIDATE_JOB_TITLE_SELECT}            .oxd-grid-item:has(label:has-text("Job Title")) .oxd-select-text    # relevé SUT 2026-07-25
${CANDIDATE_VACANCY_SELECT}              .oxd-grid-item:has(label:has-text("Vacancy")) .oxd-select-text    # relevé SUT 2026-07-25
${CANDIDATE_HIRING_MGR_SELECT}           .oxd-grid-item:has(label:has-text("Hiring Manager")) .oxd-select-text    # relevé SUT 2026-07-25
${CANDIDATE_STATUS_SELECT}               .oxd-grid-item:has(label:has-text("Status")) .oxd-select-text    # relevé SUT 2026-07-25
${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    .oxd-select-dropdown [role="option"] >> text="{value}"    # relevé SUT 2026-07-25 : validé avec Account Assistant et Automaton Tester
${CANDIDATE_SEARCH_BUTTON}               button[type="submit"]:has-text("Search")    # relevé SUT 2026-07-25
${CANDIDATE_RESET_BUTTON}                button[type="reset"]:has-text("Reset")    # relevé SUT 2026-07-25
${CANDIDATE_ADD_BUTTON}                  button.oxd-button--secondary:has-text("Add")    # relevé SUT 2026-07-25


*** Keywords ***
Candidates Page Should Be Displayed
    [Documentation]    Vérifie l'affichage de la liste des candidats.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:40].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${CANDIDATES_HEADER}    specs/test-video-to-rf.md
    Wait For Elements State    ${CANDIDATES_HEADER}    visible

Get Announced Candidate Count
    [Documentation]    Retourne le nombre de candidats annoncé par la page
    ...                (entier extrait : un état vide explicite vaut 0).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:40, 00:55].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${CANDIDATES_RECORD_COUNT}    specs/test-video-to-rf.md
    ${count}=    Get Integer From Label    ${CANDIDATES_RECORD_COUNT}
    RETURN    ${count}

Filter Candidates
    [Documentation]    Applique les 4 filtres (listes déroulantes custom) puis
    ...                lance la recherche. L'attente du rafraîchissement repose
    ...                sur l'auto-attente de Browser à la lecture suivante du
    ...                compteur : à confirmer sur le SUT (voir vigilance spec).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:40 → 00:55].
    ...                TODO : relever les locators sur le SUT.
    [Arguments]    ${job_title}    ${vacancy}    ${hiring_manager}    ${status}
    Require Locator    ${CANDIDATE_JOB_TITLE_SELECT}    specs/test-video-to-rf.md
    Require Locator    ${CANDIDATE_VACANCY_SELECT}    specs/test-video-to-rf.md
    Require Locator    ${CANDIDATE_HIRING_MGR_SELECT}    specs/test-video-to-rf.md
    Require Locator    ${CANDIDATE_STATUS_SELECT}    specs/test-video-to-rf.md
    Require Locator    ${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    specs/test-video-to-rf.md
    Require Locator    ${CANDIDATE_SEARCH_BUTTON}    specs/test-video-to-rf.md
    Click    ${CANDIDATE_JOB_TITLE_SELECT}
    ${option}=    Format String    ${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    value=${job_title}
    Click    ${option}
    Click    ${CANDIDATE_VACANCY_SELECT}
    ${option}=    Format String    ${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    value=${vacancy}
    Click    ${option}
    Click    ${CANDIDATE_HIRING_MGR_SELECT}
    ${option}=    Format String    ${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    value=${hiring_manager}
    Click    ${option}
    Click    ${CANDIDATE_STATUS_SELECT}
    ${option}=    Format String    ${CANDIDATE_DROPDOWN_OPTION_TEMPLATE}    value=${status}
    Click    ${option}
    Click    ${CANDIDATE_SEARCH_BUTTON}

Reset Candidate Filters
    [Documentation]    Réinitialise les filtres de recherche des candidats.
    ...                Source : specs/test-video-to-rf.md, vidéo [01:05].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${CANDIDATE_RESET_BUTTON}    specs/test-video-to-rf.md
    Click    ${CANDIDATE_RESET_BUTTON}

Open Add Candidate Form
    [Documentation]    Ouvre le formulaire d'ajout de candidat (+ Add).
    ...                Source : specs/test-video-to-rf.md, vidéo [00:58 → 01:00].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${CANDIDATE_ADD_BUTTON}    specs/test-video-to-rf.md
    Click    ${CANDIDATE_ADD_BUTTON}
