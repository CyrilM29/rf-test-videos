"""Prépare une ou plusieurs vidéos de tests manuels pour la skill /video-to-rf.

Produit, pour ``videos/mon-scenario.mp4`` :

    work/mon-scenario/
    ├── frames/frame_001_t00m00.0s.jpg   # une image par changement d'écran
    ├── audio.wav                        # piste audio 16 kHz mono (si présente)
    ├── audio_transcript.md              # voix off transcrite, horodatée
    ├── storyboard.md                    # frames + voix off fusionnées, chronologiques
    └── meta.json                        # index exact (frames, segments, durée, modèle)

Les frames sont extraites par détection de changement de scène ffmpeg
(``--scene``, défaut 0.10) ; si la vidéo est trop statique (moins de
``--min-frames`` scènes détectées), repli automatique sur un échantillonnage
à intervalle fixe (``--interval``). Les frames consécutives quasi identiques
sont écartées par hash perceptuel (dHash via Pillow ; ``--dedup 0`` pour
désactiver). L'audio est transcrit par faster-whisper sur CPU (``--model``,
défaut ``small`` — téléchargé au premier run dans
``%USERPROFILE%/.cache/huggingface``). Le ``storyboard.md`` aligne chaque
frame avec les segments de voix off prononcés jusqu'à la frame suivante :
c'est le document de lecture principal de la skill.

Usage :
    python scripts/prepare_video.py videos/mon-scenario.mp4
    python scripts/prepare_video.py videos/                 # batch : tout le dossier
    python scripts/prepare_video.py videos/x.mp4 --scene 0.2 --language fr --force
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_DIR = PROJECT_ROOT / "work"
# ≈1900 tokens visuels par frame 16:9 à cette largeur : texte UI lisible,
# coût de lecture maîtrisé.
FRAME_MAX_WIDTH = 1600
SHOWINFO_RE = re.compile(r"n:\s*(\d+)\s+pts:\s*-?\d+\s+pts_time:(-?[\d.]+)")
AUDIO_KEYS = ("audio", "audio_language", "audio_segments", "whisper_model")
VIDEO_EXTS = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".m4v"}
TRANSCRIPT_LINE_RE = re.compile(
    r"^- `\[(\d+):(\d+) → (\d+):(\d+)\]` (.+)$")


def die(msg: str) -> None:
    print(f"[ERREUR] {msg}")
    sys.exit(1)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def slugify(stem: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return slug or "video"


def ffprobe_duration(video: Path) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video)])
    if p.returncode != 0:
        die(f"ffprobe a échoué sur {video} :\n{p.stderr.strip()}")
    try:
        return float(p.stdout.strip())
    except ValueError:
        die(f"Durée illisible pour {video} : {p.stdout!r}")
        raise


def has_audio_stream(video: Path) -> bool:
    p = run(["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", str(video)])
    return p.returncode == 0 and p.stdout.strip() != ""


def fmt_frame_ts(t: float) -> str:
    m, s = divmod(max(t, 0.0), 60)
    return f"{int(m):02d}m{s:04.1f}s"


def fmt_clock(t: float) -> str:
    m, s = divmod(int(max(t, 0.0)), 60)
    return f"{m:02d}:{s:02d}"


def ffmpeg_extract(video: Path, frames_dir: Path, vf: str) -> list[float]:
    """Lance ffmpeg avec le graphe *vf* (qui DOIT contenir showinfo) et
    retourne les pts_time des frames écrites, dans l'ordre."""
    pattern = frames_dir / "tmp_%04d.jpg"
    p = run(["ffmpeg", "-hide_banner", "-y", "-i", str(video),
             "-vf", vf, "-fps_mode", "vfr", "-q:v", "3", str(pattern)])
    if p.returncode != 0:
        die(f"ffmpeg a échoué :\n{p.stderr[-2000:]}")
    return [float(m.group(2)) for m in SHOWINFO_RE.finditer(p.stderr)]


def dhash_file(path: Path) -> int | None:
    """dHash 64 bits d'une image (gradients horizontaux sur une vignette
    9×8 en niveaux de gris). None si Pillow n'est pas installé."""
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(path) as im:
        px = list(im.convert("L").resize((9, 8)).getdata())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (px[row * 9 + col] > px[row * 9 + col + 1])
    return bits


def dedup_near_duplicates(files: list[Path], times: list[float],
                          threshold: int) -> tuple[list[Path], list[float], int]:
    """Écarte les frames consécutives quasi identiques (distance de Hamming
    entre dHash ≤ *threshold*). Retourne (fichiers, horodatages, écartées)."""
    if threshold <= 0 or len(files) < 2:
        return files, times, 0
    ref = dhash_file(files[0])
    if ref is None:
        print("[!!] Pillow absent : dédoublonnage perceptuel sauté "
              "(pip install pillow)")
        return files, times, 0
    keep_f, keep_t = [files[0]], [times[0]]
    for f, t in zip(files[1:], times[1:]):
        h = dhash_file(f)
        if h is not None and bin(h ^ ref).count("1") <= threshold:
            f.unlink()
            continue
        ref = h if h is not None else ref
        keep_f.append(f)
        keep_t.append(t)
    return keep_f, keep_t, len(files) - len(keep_f)


def extract_frames(video: Path, frames_dir: Path, duration: float, scene: float,
                   min_frames: int, max_frames: int, interval: float,
                   dedup: int) -> tuple[list[dict], float | None, int, int]:
    """Retourne (frames retenues, intervalle de repli utilisé ou None,
    frames écartées par sur-échantillonnage, doublons perceptuels écartés)."""
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    scale = f"scale='min({FRAME_MAX_WIDTH},iw)':-2"
    times = ffmpeg_extract(
        video, frames_dir,
        f"select='eq(n,0)+gt(scene,{scene})',showinfo,{scale}")
    fallback_used: float | None = None

    if len(times) < min_frames:
        # Vidéo trop statique pour la détection de scène : échantillonnage fixe.
        fallback_used = min(interval, max(duration / max(min_frames, 1), 0.5))
        for f in frames_dir.glob("tmp_*.jpg"):
            f.unlink()
        times = ffmpeg_extract(
            video, frames_dir, f"fps=1/{fallback_used},showinfo,{scale}")

    files = sorted(frames_dir.glob("tmp_*.jpg"))
    if len(files) != len(times):
        # showinfo et fichiers désynchronisés (rare) : approximation linéaire.
        times = [i * duration / max(len(files) - 1, 1)
                 for i in range(len(files))]

    files, times, dup_dropped = dedup_near_duplicates(files, times, dedup)

    keep = list(range(len(files)))
    if len(files) > max_frames:
        step = (len(files) - 1) / max(max_frames - 1, 1)
        keep = sorted({round(i * step) for i in range(max_frames)})
    dropped = len(files) - len(keep)

    frames: list[dict] = []
    for new_idx, old_idx in enumerate(keep, start=1):
        t = times[old_idx]
        name = f"frame_{new_idx:03d}_t{fmt_frame_ts(t)}.jpg"
        files[old_idx].rename(frames_dir / name)
        frames.append({"file": f"frames/{name}", "t": round(t, 2)})
    for f in frames_dir.glob("tmp_*.jpg"):  # non retenues
        f.unlink()
    return frames, fallback_used, dropped, dup_dropped


def write_transcript_stub(video: Path, out_dir: Path, reason: str) -> dict:
    (out_dir / "audio_transcript.md").write_text(
        f"# Transcription audio — {video.name}\n\n*{reason}*\n",
        encoding="utf-8")
    return {"audio": False, "audio_language": None,
            "audio_segments": 0, "whisper_model": None, "segments": []}


def parse_transcript_md(path: Path) -> list[dict]:
    """Relit les segments d'un audio_transcript.md existant (transcriptions
    produites avant l'ajout des segments dans meta.json)."""
    segments = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TRANSCRIPT_LINE_RE.match(line)
        if m:
            m1, s1, m2, s2, text = m.groups()
            segments.append({"start": int(m1) * 60 + int(s1),
                             "end": int(m2) * 60 + int(s2),
                             "text": text.strip()})
    return segments


def transcribe(video: Path, out_dir: Path, model_name: str,
               language: str | None) -> dict:
    wav = out_dir / "audio.wav"
    p = run(["ffmpeg", "-hide_banner", "-y", "-i", str(video),
             "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    if p.returncode != 0:
        die(f"Extraction audio impossible :\n{p.stderr[-1500:]}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die("faster-whisper n'est pas installé : pip install faster-whisper")
        raise

    print(f"[..] transcription ({model_name}, CPU int8) — "
          "le premier run télécharge le modèle…")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(str(wav), language=language,
                                           vad_filter=True)

    lines = []
    segments: list[dict] = []
    for seg in segments_iter:
        text = seg.text.strip()
        if text:
            lines.append(
                f"- `[{fmt_clock(seg.start)} → {fmt_clock(seg.end)}]` {text}")
            segments.append({"start": round(seg.start, 2),
                             "end": round(seg.end, 2), "text": text})

    body = "\n".join(lines) if lines else "*Aucune parole détectée.*"
    (out_dir / "audio_transcript.md").write_text(
        f"# Transcription audio — {video.name}\n\n"
        f"- **Modèle** : {model_name} (faster-whisper, CPU int8)\n"
        f"- **Langue détectée** : {info.language} "
        f"(probabilité {info.language_probability:.2f})\n\n"
        f"## Segments\n\n{body}\n",
        encoding="utf-8")
    return {"audio": True, "audio_language": info.language,
            "audio_segments": len(lines), "whisper_model": model_name,
            "segments": segments}


def write_storyboard(out_dir: Path, video: Path, frames: list[dict],
                     segments: list[dict], duration: float) -> Path:
    """Fusionne frames et voix off en un déroulé chronologique unique —
    le document de lecture principal de /video-to-rf."""
    lines = [
        f"# Storyboard — {video.name}",
        "",
        "Déroulé chronologique généré par `prepare_video.py` : une section par",
        "frame (changement d'écran), suivie de la voix off prononcée entre",
        "cette frame et la suivante. La voix off donne l'**intention**, la",
        "frame donne l'**observé** ; en cas de contradiction, l'observé gagne.",
        "",
    ]
    for i, fr in enumerate(frames):
        t0 = fr["t"]
        t1 = frames[i + 1]["t"] if i + 1 < len(frames) else duration + 1
        lines.append(f"## [{fmt_clock(t0)}] {fr['file']}")
        segs = [s for s in segments
                if (s["start"] < t1 if i == 0 else t0 <= s["start"] < t1)]
        if segs:
            lines.extend(
                f"> `[{fmt_clock(s['start'])} → {fmt_clock(s['end'])}]` "
                f"{s['text']}" for s in segs)
        else:
            lines.append("*(pas de voix off sur ce segment)*")
        lines.append("")
    path = out_dir / "storyboard.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def process_video(video: Path, args: argparse.Namespace) -> str:
    """Traite une vidéo ; retourne le slug de son dossier work/."""
    slug = slugify(video.stem)
    out_dir = WORK_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video)

    frames, fallback, dropped, dup_dropped = extract_frames(
        video, out_dir / "frames", duration, args.scene,
        args.min_frames, args.max_frames, args.interval, args.dedup)
    mode = (f"repli échantillonnage 1 frame/{fallback:.1f}s" if fallback
            else f"détection de scène, seuil {args.scene}")
    print(f"[OK] {len(frames)} frames -> {out_dir / 'frames'} ({mode})")
    if dup_dropped:
        print(f"[OK] {dup_dropped} frames quasi identiques écartées "
              f"(dHash, seuil {args.dedup})")
    if dropped:
        print(f"[!!] {dropped} frames écartées (plafond --max-frames "
              f"{args.max_frames}, échantillonnage uniforme)")

    transcript = out_dir / "audio_transcript.md"
    meta_path = out_dir / "meta.json"
    old_meta: dict = {}
    if meta_path.is_file():
        try:
            old_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old_meta = {}

    if transcript.is_file() and not args.force:
        audio_info = {k: old_meta.get(k) for k in AUDIO_KEYS}
        audio_info["segments"] = (old_meta.get("segments")
                                  or parse_transcript_md(transcript))
        print(f"[OK] transcription existante conservée ({transcript}) — "
              "--force pour la refaire")
    elif not has_audio_stream(video):
        audio_info = write_transcript_stub(
            video, out_dir, "La vidéo ne contient aucune piste audio.")
        print("[OK] aucune piste audio dans la vidéo")
    elif args.no_audio:
        audio_info = write_transcript_stub(
            video, out_dir, "Transcription désactivée (--no-audio).")
        print("[OK] transcription sautée (--no-audio)")
    else:
        audio_info = transcribe(video, out_dir, args.model, args.language)
        print(f"[OK] {audio_info['audio_segments']} segments audio "
              f"({audio_info['audio_language']}) -> {transcript}")

    storyboard = write_storyboard(out_dir, video, frames,
                                  audio_info.get("segments") or [], duration)
    print(f"[OK] storyboard -> {storyboard}")

    meta = {
        "video": str(video).replace("\\", "/"),
        "slug": slug,
        "duration_s": round(duration, 2),
        "scene_threshold": args.scene,
        "fallback_interval_used": round(fallback, 2) if fallback else None,
        "dedup_threshold": args.dedup,
        "dedup_dropped": dup_dropped,
        "n_frames": len(frames),
        "frames": frames,
        "storyboard": "storyboard.md",
        **audio_info,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[OK] meta -> {meta_path}")
    voice = "voix off transcrite" if meta.get("audio") else "pas de voix off"
    print(f"\nPrêt pour la transcription : work/{slug}/ "
          f"({len(frames)} frames, {voice})")
    return slug


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source",
                    help="vidéo (ex: videos/mon-scenario.mp4) ou dossier de "
                         "vidéos à traiter en lot (ex: videos/)")
    ap.add_argument("--scene", type=float, default=0.10,
                    help="seuil de détection de scène ffmpeg (défaut 0.10)")
    ap.add_argument("--min-frames", type=int, default=8,
                    help="en dessous, repli sur l'échantillonnage fixe (défaut 8)")
    ap.add_argument("--max-frames", type=int, default=120,
                    help="au-dessus, échantillonnage uniforme (défaut 120)")
    ap.add_argument("--interval", type=float, default=5.0,
                    help="intervalle (s) du repli à échantillonnage fixe (défaut 5.0)")
    ap.add_argument("--dedup", type=int, default=2,
                    help="distance dHash max pour écarter une frame quasi "
                         "identique à la précédente ; 0 désactive (défaut 2 — "
                         "prudent : une saisie clavier change peu de pixels)")
    ap.add_argument("--model", default="small",
                    help="modèle faster-whisper : tiny/base/small/medium/large-v3 (défaut small)")
    ap.add_argument("--language", default=None,
                    help="langue de la voix off (ex: fr) ; défaut : détection auto")
    ap.add_argument("--no-audio", action="store_true",
                    help="ne pas transcrire l'audio")
    ap.add_argument("--force", action="store_true",
                    help="retranscrire l'audio même si audio_transcript.md existe")
    args = ap.parse_args()

    source = Path(args.source)
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        die("ffmpeg/ffprobe introuvables dans le PATH")

    if source.is_dir():
        videos = sorted(p for p in source.iterdir()
                        if p.suffix.lower() in VIDEO_EXTS)
        if not videos:
            die(f"aucune vidéo ({', '.join(sorted(VIDEO_EXTS))}) dans {source}")
        print(f"[..] mode batch : {len(videos)} vidéo(s) dans {source}\n")
    elif source.is_file():
        videos = [source]
    else:
        die(f"vidéo ou dossier introuvable : {source}")
        raise SystemExit  # inatteignable — pour l'analyse statique

    slugs = []
    for i, video in enumerate(videos, start=1):
        if len(videos) > 1:
            print(f"===== [{i}/{len(videos)}] {video.name} =====")
        slugs.append(process_video(video, args))
        if len(videos) > 1:
            print()
    if len(videos) > 1:
        print(f"[OK] batch terminé : {len(slugs)} dossier(s) work/ prêts — "
              + ", ".join(slugs))


if __name__ == "__main__":
    main()
