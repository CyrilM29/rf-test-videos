# Copyright 2026 Cyril Montiel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contrôle la traçabilité spec ↔ suite et les conventions du dépôt.

Vérifie, pour chaque suite de ``tests/robot/`` :

1. la présence d'une référence ``Spec: specs/<slug>.md (sha256:<12 hex>, <date>)``
   dans l'en-tête ``Documentation`` (convention 4) ;
2. que la spec référencée existe et que l'empreinte sha256 correspond au
   fichier actuel : une divergence signifie que la spec a changé sans
   régénération de la suite ;
3. qu'aucune ``Library`` n'est importée directement (convention 1 : les
   suites ne passent que par des ``Resource``) ;
4. qu'aucun localisateur (``id=``, ``css=``, ``xpath=``, ``//``…) ne traîne
   dans la suite (convention 1) ;
5. qu'aucun ``Sleep`` n'apparaît dans les suites ni les resources
   (convention 2).

Sortie : un rapport par fichier ; code retour 0 si tout est conforme,
1 sinon. Utilisé par la CI (.github/workflows/ci.yml) et par les skills.

Usage :
    python scripts/check_specs.py
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "robot"
RESOURCES_DIR = PROJECT_ROOT / "resources"

SPEC_REF_RE = re.compile(r"Spec:\s*(specs/[\w.-]+\.md)\s*\(sha256:([0-9a-f]{12})")
LIBRARY_RE = re.compile(r"^Library\s{2,}", re.MULTILINE)
SLEEP_LINE_RE = re.compile(r"^\s+Sleep(?:\s{2,}|\s*$)")
LOCATOR_RE = re.compile(
    r"^\s+\S.*?(?:\s{2,}|=\s*)(?:id=|css=|xpath=|css:|xpath:|//)\S",
    re.MULTILINE)


def spec_sha12(spec: Path) -> str:
    return hashlib.sha256(spec.read_bytes()).hexdigest()[:12]


def check_suite(suite: Path, errors: list[str]) -> None:
    rel = suite.relative_to(PROJECT_ROOT).as_posix()
    text = suite.read_text(encoding="utf-8")

    m = SPEC_REF_RE.search(text)
    if not m:
        errors.append(f"{rel} : aucune référence "
                      "`Spec: specs/<slug>.md (sha256:…)` dans l'en-tête "
                      "(convention 4)")
    else:
        spec = PROJECT_ROOT / m.group(1)
        if not spec.is_file():
            errors.append(f"{rel} : spec référencée introuvable, {m.group(1)}")
        else:
            actual = spec_sha12(spec)
            if actual != m.group(2):
                errors.append(
                    f"{rel} : sha256 de {m.group(1)} divergent, suite "
                    f"{m.group(2)}, spec actuelle {actual}. La spec a changé : "
                    "régénérer la suite (ou rafraîchir l'empreinte si la "
                    "régénération vient d'être faite).")

    if LIBRARY_RE.search(text):
        errors.append(f"{rel} : import `Library` direct dans une suite "
                      "(convention 1 : passer par common.resource ou un "
                      "page object)")
    if LOCATOR_RE.search(text):
        errors.append(f"{rel} : localisateur apparent (id=/css=/xpath=///) "
                      "dans une suite (convention 1 : les locators vivent "
                      "dans resources/page_objects/)")


def check_no_sleep(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(),
                             start=1):
        if SLEEP_LINE_RE.match(line):
            errors.append(f"{rel}:{n} : `Sleep` interdit (convention 2, "
                          "attente sur condition)")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    suites = sorted(TESTS_DIR.rglob("*.robot"))
    resources = sorted(RESOURCES_DIR.rglob("*.resource"))
    if not suites:
        print("[OK] aucune suite dans tests/robot/ : rien à contrôler")
        return 0

    errors: list[str] = []
    for suite in suites:
        check_suite(suite, errors)
    for path in [*suites, *resources]:
        check_no_sleep(path, errors)

    if errors:
        print(f"[KO] {len(errors)} problème(s) de conformité :\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[OK] {len(suites)} suite(s), {len(resources)} resource(s) : "
          "références de spec exactes, conventions 1/2/4 respectées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
