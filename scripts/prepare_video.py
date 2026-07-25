"""Prépare une vidéo de test manuel pour la skill /video-to-rf.

Produit, pour ``videos/mon-scenario.mp4`` :

    work/mon-scenario/
    ├── frames/frame_001_t00m00.0s.jpg   # une image par changement d'écran
    ├── audio.wav                        # piste audio 16 kHz mono (si présente)
    ├── audio_transcript.md              # voix off transcrite, horodatée
    └── meta.json                        # index exact (frames, durée, modèle)

Les frames sont extraites par détection de changement de scène ffmpeg
(``--scene``, défaut 0.10) ; si la vidéo est trop statique (moins de
``--min-frames`` scènes détectées), repli automatique sur un échantillonnage
à intervalle fixe (``--interval``). L'audio est transcrit par faster-whisper
sur CPU (``--model``, défaut ``small`` — téléchargé au premier run dans
``%USERPROFILE%/.cache/huggingface``).

Usage :
    python scripts/prepare_video.py videos/mon-scenario.mp4
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


def extract_frames(video: Path, frames_dir: Path, duration: float, scene: float,
                   min_frames: int, max_frames: int, interval: float,
                   ) -> tuple[list[dict], float | None, int]:
    """Retourne (frames retenues, intervalle de repli utilisé ou None,
    nombre de frames écartées par sur-échantillonnage)."""
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
    return frames, fallback_used, dropped


def write_transcript_stub(video: Path, out_dir: Path, reason: str) -> dict:
    (out_dir / "audio_transcript.md").write_text(
        f"# Transcription audio — {video.name}\n\n*{reason}*\n",
        encoding="utf-8")
    return {"audio": False, "audio_language": None,
            "audio_segments": 0, "whisper_model": None}


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
    segments, info = model.transcribe(str(wav), language=language,
                                      vad_filter=True)

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            lines.append(
                f"- `[{fmt_clock(seg.start)} → {fmt_clock(seg.end)}]` {text}")

    body = "\n".join(lines) if lines else "*Aucune parole détectée.*"
    (out_dir / "audio_transcript.md").write_text(
        f"# Transcription audio — {video.name}\n\n"
        f"- **Modèle** : {model_name} (faster-whisper, CPU int8)\n"
        f"- **Langue détectée** : {info.language} "
        f"(probabilité {info.language_probability:.2f})\n\n"
        f"## Segments\n\n{body}\n",
        encoding="utf-8")
    return {"audio": True, "audio_language": info.language,
            "audio_segments": len(lines), "whisper_model": model_name}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="chemin de la vidéo (ex: videos/mon-scenario.mp4)")
    ap.add_argument("--scene", type=float, default=0.10,
                    help="seuil de détection de scène ffmpeg (défaut 0.10)")
    ap.add_argument("--min-frames", type=int, default=8,
                    help="en dessous, repli sur l'échantillonnage fixe (défaut 8)")
    ap.add_argument("--max-frames", type=int, default=120,
                    help="au-dessus, échantillonnage uniforme (défaut 120)")
    ap.add_argument("--interval", type=float, default=5.0,
                    help="intervalle (s) du repli à échantillonnage fixe (défaut 5.0)")
    ap.add_argument("--model", default="small",
                    help="modèle faster-whisper : tiny/base/small/medium/large-v3 (défaut small)")
    ap.add_argument("--language", default=None,
                    help="langue de la voix off (ex: fr) ; défaut : détection auto")
    ap.add_argument("--no-audio", action="store_true",
                    help="ne pas transcrire l'audio")
    ap.add_argument("--force", action="store_true",
                    help="retranscrire l'audio même si audio_transcript.md existe")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.is_file():
        die(f"vidéo introuvable : {video}")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        die("ffmpeg/ffprobe introuvables dans le PATH")

    slug = slugify(video.stem)
    out_dir = WORK_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video)

    frames, fallback, dropped = extract_frames(
        video, out_dir / "frames", duration, args.scene,
        args.min_frames, args.max_frames, args.interval)
    mode = (f"repli échantillonnage 1 frame/{fallback:.1f}s" if fallback
            else f"détection de scène, seuil {args.scene}")
    print(f"[OK] {len(frames)} frames -> {out_dir / 'frames'} ({mode})")
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

    meta = {
        "video": str(video).replace("\\", "/"),
        "slug": slug,
        "duration_s": round(duration, 2),
        "scene_threshold": args.scene,
        "fallback_interval_used": round(fallback, 2) if fallback else None,
        "n_frames": len(frames),
        "frames": frames,
        **audio_info,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[OK] meta -> {meta_path}")
    voice = "voix off transcrite" if meta.get("audio") else "pas de voix off"
    print(f"\nPrêt pour la transcription : work/{slug}/ "
          f"({len(frames)} frames, {voice})")


if __name__ == "__main__":
    main()
