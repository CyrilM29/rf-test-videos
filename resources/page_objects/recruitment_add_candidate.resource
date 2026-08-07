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
Documentation    Écran Recruitment > Add Candidate (formulaire) : créé depuis
...              specs/test-video-to-rf.md (vidéo [00:58 → 01:10]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Locators relevés en live sur le SUT via /finalize-rf (robotmcp)
${ADD_CANDIDATE_HEADER}        h6:has-text("Add Candidate")    # relevé SUT 2026-07-25
${ADD_CANDIDATE_FIRST_NAME}    input[name="firstName"]    # relevé SUT 2026-07-25
${ADD_CANDIDATE_EMAIL}         .oxd-input-group:has(label:has-text("Email")) input    # relevé SUT 2026-07-25, pas d'attribut name, ancré sur le label
${ADD_CANDIDATE_CANCEL}        button.oxd-button--ghost:has-text("Cancel")    # relevé SUT 2026-07-25, Cancel confirmé en live (écart spec levé)
${ADD_CANDIDATE_SAVE}          button[type="submit"]:has-text("Save")    # relevé SUT 2026-07-25


*** Keywords ***
Add Candidate Form Should Be Displayed
    [Documentation]    Vérifie l'affichage du formulaire d'ajout : champs
    ...                obligatoires Full Name et Email présents.
    ...                Source : specs/test-video-to-rf.md, vidéo [01:00].
    ...                TODO : relever les locators sur le SUT.
    Require Locator    ${ADD_CANDIDATE_FIRST_NAME}    specs/test-video-to-rf.md
    Require Locator    ${ADD_CANDIDATE_EMAIL}    specs/test-video-to-rf.md
    Wait For Elements State    ${ADD_CANDIDATE_FIRST_NAME}    visible
    Wait For Elements State    ${ADD_CANDIDATE_EMAIL}    visible

Cancel Candidate Creation
    [Documentation]    Abandonne la création (Cancel) et revient à la liste des
    ...                candidats. Écart spec : le clic exact se produit entre
    ...                deux frames : à confirmer sur le SUT.
    ...                Source : specs/test-video-to-rf.md, vidéo [01:00 → 01:05].
    ...                TODO : relever le locator sur le SUT.
    Require Locator    ${ADD_CANDIDATE_CANCEL}    specs/test-video-to-rf.md
    Click    ${ADD_CANDIDATE_CANCEL}
