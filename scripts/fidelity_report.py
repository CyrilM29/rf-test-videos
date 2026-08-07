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

"""Génère le rapport HTML de fidélité visuelle d'une suite (vidéo ↔ exécution).

Entrée : un manifest JSON écrit par la skill /finalize-rf (étape « fidélité
visuelle ») dans ``results/fidelity/<slug>/manifest.json`` :

    {
      "slug": "test-video-to-rf",
      "titre": "Parcours de consultation OrangeHRM",
      "date": "2026-07-27",
      "video": "videos/test-video-to-rf.mp4",
      "spec": "specs/test-video-to-rf.md",
      "suite": "tests/robot/ui/web/test-video-to-rf.robot",
      "runs": ["results/test-video-to-rf_live", "results/test-video-to-rf_live2"],
      "scenarios": [
        {
          "n": 1,
          "titre": "Connexion au portail",
          "timestamp": "00:15",
          "frame": "work/<slug>/frames/frame_003_t00m15.0s.jpg",
          "capture": "results/fidelity/<slug>/s1_dashboard.png",
          "verdict": "conforme",            // "conforme" | "écart"
          "note": "mêmes widgets ; utilisateur de démo différent (données)"
        }
      ]
    }

Sortie : ``results/fidelity/<slug>/report.html``, **autonome** : les frames
vidéo et les captures d'exécution sont embarquées en base64, le rapport reste
lisible et partageable après purge de ``work/`` et ``results/`` (chemins en
sont de simples références). Verdicts côte à côte, bilan en tête.

Usage :
    python scripts/fidelity_report.py test-video-to-rf
    python scripts/fidelity_report.py results/fidelity/test-video-to-rf/manifest.json
"""
from __future__ import annotations

import base64
import html
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIDELITY_DIR = PROJECT_ROOT / "results" / "fidelity"

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp"}

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
       background: #f4f5f7; color: #1f2328; }
header { background: #fff; border-bottom: 1px solid #d9dce1;
         padding: 24px 32px; }
h1 { margin: 0 0 6px; font-size: 22px; }
h1 small { font-weight: normal; color: #59636e; font-size: 14px; }
.meta { color: #59636e; font-size: 13px; line-height: 1.7; }
.meta code { background: #eff1f4; padding: 1px 5px; border-radius: 4px; }
.bilan { display: inline-block; margin-top: 10px; padding: 6px 14px;
         border-radius: 999px; font-weight: 600; font-size: 14px; }
.bilan.ok { background: #dcf5e4; color: #116329; }
.bilan.ko { background: #ffe1de; color: #a40e26; }
main { max-width: 1500px; margin: 0 auto; padding: 24px 32px 48px; }
.scenario { background: #fff; border: 1px solid #d9dce1; border-radius: 10px;
            margin-bottom: 28px; overflow: hidden; }
.scenario > .head { display: flex; align-items: baseline; gap: 12px;
                    padding: 14px 20px; border-bottom: 1px solid #eceef1; }
.scenario h2 { margin: 0; font-size: 16px; flex: 1; }
.ts { color: #59636e; font-size: 13px; white-space: nowrap; }
.badge { padding: 3px 12px; border-radius: 999px; font-size: 13px;
         font-weight: 600; white-space: nowrap; }
.badge.conforme { background: #dcf5e4; color: #116329; }
.badge.ecart { background: #ffe1de; color: #a40e26; }
.note { padding: 10px 20px; color: #454c54; font-size: 14px;
        border-bottom: 1px solid #eceef1; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
.pane { padding: 14px 20px 20px; min-width: 0; }
.pane + .pane { border-left: 1px solid #eceef1; }
.pane .label { font-size: 12px; font-weight: 600; text-transform: uppercase;
               letter-spacing: .05em; color: #59636e; margin-bottom: 8px; }
.pane img { width: 100%; height: auto; border: 1px solid #d9dce1;
            border-radius: 6px; display: block; }
.pane .path { font-size: 11px; color: #8b949e; margin-top: 6px;
              word-break: break-all; }
.missing { border: 1px dashed #c4c9d0; border-radius: 6px; padding: 40px 12px;
           text-align: center; color: #8b949e; font-size: 13px; }
footer { text-align: center; color: #8b949e; font-size: 12px;
         padding: 0 0 32px; }
@media (max-width: 900px) { .pair { grid-template-columns: 1fr; }
                            .pane + .pane { border-left: 0;
                                            border-top: 1px solid #eceef1; } }
"""


def die(msg: str) -> None:
    print(f"[ERREUR] {msg}")
    sys.exit(1)


def img_tag(rel_path: str | None) -> str:
    """Image embarquée en data URI ; placeholder si absente."""
    if not rel_path:
        return '<div class="missing">non fournie</div>'
    path = PROJECT_ROOT / rel_path
    mime = MIME.get(path.suffix.lower())
    if not path.is_file() or mime is None:
        return (f'<div class="missing">image introuvable&nbsp;: '
                f'{html.escape(str(rel_path))}</div>')
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return (f'<img src="data:{mime};base64,{data}" '
            f'alt="{html.escape(str(rel_path))}" loading="lazy">')


def render(manifest: dict) -> str:
    slug = manifest.get("slug", "?")
    scenarios = manifest.get("scenarios", [])
    n_ok = sum(1 for s in scenarios
               if str(s.get("verdict", "")).lower().startswith("conforme"))
    total = len(scenarios)
    all_ok = n_ok == total and total > 0
    bilan_cls = "ok" if all_ok else "ko"
    bilan_txt = (f"{n_ok}/{total} scénarios conformes"
                 + ("" if all_ok else " : écarts à traiter (voir la spec)"))

    meta_lines = []
    for label, key in (("Vidéo", "video"), ("Spec", "spec"),
                       ("Suite", "suite")):
        if manifest.get(key):
            meta_lines.append(
                f"{label} : <code>{html.escape(str(manifest[key]))}</code>")
    if manifest.get("runs"):
        runs = " · ".join(f"<code>{html.escape(str(r))}</code>"
                          for r in manifest["runs"])
        meta_lines.append(f"Runs réels verts : {runs}")

    blocks = []
    for s in scenarios:
        verdict = str(s.get("verdict", "?")).lower()
        cls = "conforme" if verdict.startswith("conforme") else "ecart"
        label = "conforme" if cls == "conforme" else "écart"
        ts = (f'<span class="ts">frame vidéo [{html.escape(str(s["timestamp"]))}]'
              f'</span>' if s.get("timestamp") else "")
        note = (f'<div class="note">{html.escape(str(s["note"]))}</div>'
                if s.get("note") else "")
        blocks.append(f"""
<section class="scenario">
  <div class="head">
    <h2>{s.get("n", "?")}. {html.escape(str(s.get("titre", "")))}</h2>
    {ts}
    <span class="badge {cls}">{label}</span>
  </div>
  {note}
  <div class="pair">
    <div class="pane">
      <div class="label">Vidéo (attendu)</div>
      {img_tag(s.get("frame"))}
      <div class="path">{html.escape(str(s.get("frame") or ""))}</div>
    </div>
    <div class="pane">
      <div class="label">Exécution réelle (observé)</div>
      {img_tag(s.get("capture"))}
      <div class="path">{html.escape(str(s.get("capture") or ""))}</div>
    </div>
  </div>
</section>""")

    titre = html.escape(str(manifest.get("titre") or slug))
    date = html.escape(str(manifest.get("date") or ""))
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fidélité visuelle : {html.escape(slug)}</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>Fidélité visuelle : {titre} <small>({html.escape(slug)}, {date})</small></h1>
  <div class="meta">{"<br>".join(meta_lines)}</div>
  <div class="bilan {bilan_cls}">{bilan_txt}</div>
</header>
<main>
{"".join(blocks)}
</main>
<footer>Rapport généré par scripts/fidelity_report.py : les différences de
données (compteurs, dates, contenus de listes) sont attendues&nbsp;: seuls les
écarts de structure ou de flux comptent.</footer>
</body>
</html>
"""


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        die("usage : python scripts/fidelity_report.py <slug | manifest.json>")

    arg = Path(sys.argv[1])
    manifest_path = (arg if arg.suffix == ".json"
                     else FIDELITY_DIR / arg.name / "manifest.json")
    if not manifest_path.is_file():
        die(f"manifest introuvable : {manifest_path}, la skill /finalize-rf "
            "l'écrit à l'étape « fidélité visuelle »")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"manifest illisible ({manifest_path}) : {e}")
        raise

    out = manifest_path.parent / "report.html"
    out.write_text(render(manifest), encoding="utf-8")
    scenarios = manifest.get("scenarios", [])
    n_ok = sum(1 for s in scenarios
               if str(s.get("verdict", "")).lower().startswith("conforme"))
    print(f"[OK] rapport -> {out} ({n_ok}/{len(scenarios)} conformes, "
          "images embarquées : autonome et partageable)")


if __name__ == "__main__":
    main()
