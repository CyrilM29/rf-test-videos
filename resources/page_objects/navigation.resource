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
Documentation    Menu latéral OrangeHRM (Admin, PIM, Leave, Recruitment…) :
...              créé depuis specs/test-video-to-rf.md (vidéo [00:15 → 00:40]).
...              Corps implémentés avec Browser ; locators TODO.
Resource         ../common.resource


*** Variables ***
# Gabarit avec {module} (Format String) : validé avec Admin et PIM
${SIDEBAR_MENU_ITEM_TEMPLATE}    a.oxd-main-menu-item >> text="{module}"    # relevé SUT 2026-07-25


*** Keywords ***
Go To Module
    [Documentation]    Ouvre un module depuis le menu latéral (ex. Admin, PIM,
    ...                Leave, Recruitment). L'attente d'arrivée est portée par
    ...                le keyword « … Should Be Displayed » de l'écran cible.
    ...                Source : specs/test-video-to-rf.md, vidéo [00:15 → 00:40].
    ...                TODO : relever le gabarit de locator sur le SUT.
    [Arguments]    ${module}
    Require Locator    ${SIDEBAR_MENU_ITEM_TEMPLATE}    specs/test-video-to-rf.md
    ${item}=    Format String    ${SIDEBAR_MENU_ITEM_TEMPLATE}    module=${module}
    Click    ${item}
