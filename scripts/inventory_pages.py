"""Inventaire des page objects : keywords disponibles et état des locators.

Balaye ``resources/page_objects/*.resource`` et liste, par écran :

- les **keywords** exposés (réutilisables tels quels par une nouvelle suite) ;
- les **locators** et leur état — ``relevé`` (déjà validé en live sur le SUT
  via /finalize-rf), ``TODO`` (à relever), ou ``donnée`` (variable de page qui
  n'est pas un localisateur).

C'est l'outil de **capitalisation** du dépôt : avant de créer un keyword
depuis une nouvelle vidéo, /video-to-rf consulte cet inventaire — un écran
déjà couvert avec locators relevés se réutilise sans repasser par le SUT.

Usage :
    python scripts/inventory_pages.py            # rapport lisible
    python scripts/inventory_pages.py --json     # sortie machine (skills)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAGE_OBJECTS_DIR = PROJECT_ROOT / "resources" / "page_objects"

SECTION_RE = re.compile(r"^\*\*\*\s*(\w[\w ]*?)\s*\*\*\*", re.IGNORECASE)
VARIABLE_RE = re.compile(r"^\$\{(\w+)\}\s{2,}(.*?)(?:\s{2,}#\s*(.*))?$")
DOC_RE = re.compile(r"^\s+\[Documentation\]\s+(.*)$")


def parse_resource(path: Path) -> dict:
    keywords: list[dict] = []
    variables: list[dict] = []
    section = None
    current_kw: dict | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(raw)
        if m:
            section = m.group(1).lower()
            current_kw = None
            continue
        if section and section.startswith("variable"):
            m = VARIABLE_RE.match(raw)
            if m:
                name, value, comment = m.group(1), m.group(2), m.group(3) or ""
                if value == "${EMPTY}" or "TODO" in comment.upper():
                    status = "TODO"
                elif "relevé" in comment.lower():
                    status = "relevé"
                else:
                    status = "donnée"
                variables.append({"name": name, "value": value,
                                  "status": status})
        elif section and section.startswith("keyword"):
            if raw and not raw[0].isspace() and not raw.startswith("#"):
                current_kw = {"name": raw.strip(), "doc": ""}
                keywords.append(current_kw)
            elif current_kw is not None and not current_kw["doc"]:
                m = DOC_RE.match(raw)
                if m:
                    current_kw["doc"] = m.group(1).strip()

    todo = [v["name"] for v in variables if v["status"] == "TODO"]
    releves = [v["name"] for v in variables if v["status"] == "relevé"]
    return {
        "file": path.relative_to(PROJECT_ROOT).as_posix(),
        "screen": path.stem,
        "keywords": keywords,
        "locators_releves": releves,
        "locators_todo": todo,
        "ready": not todo,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true",
                    help="sortie JSON (consommée par les skills)")
    args = ap.parse_args()

    files = sorted(PAGE_OBJECTS_DIR.glob("*.resource"))
    screens = [parse_resource(f) for f in files]

    if args.json:
        print(json.dumps(screens, ensure_ascii=False, indent=2))
        return 0

    if not screens:
        print("Aucun page object dans resources/page_objects/ — "
              "premier passage : tout sera à créer.")
        return 0

    n_kw = sum(len(s["keywords"]) for s in screens)
    n_ok = sum(len(s["locators_releves"]) for s in screens)
    n_todo = sum(len(s["locators_todo"]) for s in screens)
    print(f"Inventaire page objects — {len(screens)} écran(s), "
          f"{n_kw} keyword(s), locators : {n_ok} relevé(s), {n_todo} TODO\n")
    for s in screens:
        badge = "prêt (réutilisable sans SUT)" if s["ready"] else \
            f"{len(s['locators_todo'])} locator(s) TODO"
        print(f"## {s['screen']} — {badge}")
        for kw in s["keywords"]:
            doc = f" — {kw['doc']}" if kw["doc"] else ""
            print(f"  - {kw['name']}{doc}")
        if s["locators_todo"]:
            print(f"  TODO : {', '.join(s['locators_todo'])}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
