#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Porte QA Automatisée (verify_episode.py)
Vérifie objectivement qu'un master .mp4 produit respecte toutes les exigences Cinéma 9:16 :
  - ffprobe : codec vidéo h264, pix_fmt yuv420p, résolution exacte 1080x1920 ou 720x1280,
    codec audio aac, durée >= 35s, taille > 500 Ko
  - Audio non muet : ffmpeg volumedetect mean_volume > -40 dB
  - 3 frames échantillonnées (15%, 50%, 85%) : variance stddev > 15 + diversité inter-frames > 3.0
  - Mode --strict-production (avec --meta) : tts_mode == "edge_tts" ET
    ratio d'images IA réelles (pollinations + aihorde) >= 50% des scènes
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageChops, ImageStat

VALID_DIMENSIONS = {(1080, 1920), (720, 1280)}


def _probe_streams(mp4_path: str) -> Dict[str, Any]:
    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        mp4_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def _detect_mean_volume_db(mp4_path: str) -> Optional[float]:
    cmd = [
        "ffmpeg", "-hide_banner", "-i", mp4_path,
        "-af", "volumedetect",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*([-+]?\d+(?:\.\d+)?)\s*dB", res.stderr)
    if not m:
        return None
    return float(m.group(1))


def _sample_frames(mp4_path: str, duration: float, fractions: Tuple[float, ...] = (0.15, 0.50, 0.85)) -> List[Image.Image]:
    frames: List[Image.Image] = []
    with tempfile.TemporaryDirectory(prefix="amina_qa_") as tmpdir:
        for idx, frac in enumerate(fractions):
            ts = max(0.5, min(duration - 0.5, duration * frac))
            out_png = os.path.join(tmpdir, f"frame_{idx}.png")
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", f"{ts:.2f}",
                    "-i", mp4_path,
                    "-vframes", "1",
                    out_png,
                ],
                check=True,
            )
            img = Image.open(out_png).convert("RGB")
            img.load()
            frames.append(img)
    return frames


def verify_episode(
    mp4_path: str,
    meta_path: Optional[str] = None,
    strict_production: bool = False,
    min_duration: float = 35.0,
    min_size_kb: int = 500,
    min_mean_volume_db: float = -40.0,
    min_frame_stddev: float = 15.0,
    min_frame_diff: float = 3.0,
) -> Tuple[bool, Dict[str, Any]]:
    """Run all automated media and production integrity checks. Returns (passed, report)."""
    errors: List[str] = []
    checks: Dict[str, Any] = {}

    if not os.path.exists(mp4_path):
        return False, {"passed": False, "errors": [f"MP4 file not found: {mp4_path}"], "checks": {}}

    file_size = os.path.getsize(mp4_path)
    checks["sizeBytes"] = file_size
    if file_size <= min_size_kb * 1024:
        errors.append(f"File too small: {file_size} bytes (min > {min_size_kb * 1024} bytes)")

    try:
        probe = _probe_streams(mp4_path)
    except Exception as exc:
        return False, {"passed": False, "errors": [f"ffprobe failed: {exc}"], "checks": checks}

    streams = probe.get("streams", [])
    fmt = probe.get("format", {})
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = float(fmt.get("duration") or 0.0)
    checks["duration"] = round(duration, 2)
    if duration < min_duration:
        errors.append(f"Duration too short: {duration:.2f}s (min {min_duration:.1f}s)")

    if not v_stream:
        errors.append("Missing video stream")
    else:
        v_codec = v_stream.get("codec_name")
        pix_fmt = v_stream.get("pix_fmt")
        width = int(v_stream.get("width") or 0)
        height = int(v_stream.get("height") or 0)
        checks["video"] = {
            "codec": v_codec,
            "pix_fmt": pix_fmt,
            "width": width,
            "height": height,
        }
        if v_codec != "h264":
            errors.append(f"Invalid video codec: {v_codec} (expected h264)")
        if pix_fmt != "yuv420p":
            errors.append(f"Invalid pix_fmt: {pix_fmt} (expected yuv420p)")
        if (width, height) not in VALID_DIMENSIONS:
            errors.append(
                f"Invalid resolution: {width}x{height} (expected 1080x1920 or 720x1280)"
            )

    if not a_stream:
        errors.append("Missing audio stream")
    else:
        a_codec = a_stream.get("codec_name")
        checks["audio"] = {
            "codec": a_codec,
            "sample_rate": a_stream.get("sample_rate"),
            "channels": a_stream.get("channels"),
        }
        if a_codec != "aac":
            errors.append(f"Invalid audio codec: {a_codec} (expected aac)")

    # Loudness check (reject silent tracks)
    mean_vol = _detect_mean_volume_db(mp4_path)
    checks["meanVolumeDb"] = mean_vol
    if mean_vol is None:
        errors.append("Could not detect audio mean_volume via volumedetect")
    elif mean_vol <= min_mean_volume_db:
        errors.append(
            f"Audio track is silent/too quiet: mean_volume={mean_vol:.1f} dB (must be > {min_mean_volume_db:.1f} dB)"
        )

    # Visual frame variance & diversity check at 15%, 50%, 85%
    if duration >= 2.0 and v_stream:
        try:
            frames = _sample_frames(mp4_path, duration, (0.15, 0.50, 0.85))
            stddevs = [round(ImageStat.Stat(im.convert("L")).stddev[0], 2) for im in frames]
            checks["frameStddevs"] = stddevs
            for idx, sd in enumerate(stddevs):
                if sd <= min_frame_stddev:
                    errors.append(
                        f"Sampled frame #{idx + 1} has low variance (stddev={sd:.2f} <= {min_frame_stddev})"
                    )

            # Resize small for fast diversity check (mean absolute pixel diff across pairs)
            small = [im.resize((180, 320)) for im in frames]
            pair_diffs: List[float] = []
            for i in range(len(small)):
                for j in range(i + 1, len(small)):
                    diff_img = ImageChops.difference(small[i], small[j]).convert("L")
                    mean_diff = ImageStat.Stat(diff_img).mean[0]
                    pair_diffs.append(round(mean_diff, 2))
            checks["framePairDiffs"] = pair_diffs
            if not pair_diffs or max(pair_diffs) <= min_frame_diff:
                errors.append(
                    f"Video frames appear frozen/static (max pair diff={max(pair_diffs) if pair_diffs else 0:.2f} <= {min_frame_diff})"
                )
        except Exception as exc:
            errors.append(f"Frame sampling/inspection failed: {exc}")

    # Strict production checks (CI / Release gate)
    if strict_production:
        if not meta_path or not os.path.exists(meta_path):
            errors.append("--strict-production requires an existing --meta JSON file")
        else:
            try:
                with open(meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
            except Exception as exc:
                errors.append(f"Could not read meta JSON ({meta_path}): {exc}")
                meta = {}

            tts_mode = meta.get("tts_mode")
            providers = meta.get("providers") or {}
            n_poll = int(providers.get("pollinations", 0))
            n_horde = int(providers.get("aihorde", 0))
            n_fb = int(providers.get("fallback", 0))
            total_sc = n_poll + n_horde + n_fb
            real_ai_ratio = (n_poll + n_horde) / total_sc if total_sc > 0 else 0.0

            checks["production"] = {
                "tts_mode": tts_mode,
                "providers": providers,
                "realAiRatio": round(real_ai_ratio, 3),
            }

            if tts_mode != "edge_tts":
                errors.append(
                    f"Strict production failed: tts_mode='{tts_mode}' (expected 'edge_tts')"
                )
            if total_sc < 1 or real_ai_ratio < 0.50:
                errors.append(
                    f"Strict production failed: real AI image ratio={real_ai_ratio:.1%} "
                    f"(pollinations={n_poll}, aihorde={n_horde}, fallback={n_fb}; minimum 50% required)"
                )

    passed = len(errors) == 0
    return passed, {
        "passed": passed,
        "file": mp4_path,
        "strictProduction": strict_production,
        "checks": checks,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify rendered AMINA Motion-Cinema MP4 quality.")
    parser.add_argument("mp4_path", help="Path to rendered episode .mp4")
    parser.add_argument("--meta", default=None, help="Path to ep-XXX_meta.json")
    parser.add_argument(
        "--strict-production",
        action="store_true",
        help="Enforce real Edge-TTS and >=50%% real AI image providers from --meta",
    )
    parser.add_argument("--min-duration", type=float, default=35.0, help="Minimum duration in seconds")
    parser.add_argument("--min-size-kb", type=int, default=500, help="Minimum file size in KB")
    args = parser.parse_args()

    passed, report = verify_episode(
        mp4_path=args.mp4_path,
        meta_path=args.meta,
        strict_production=args.strict_production,
        min_duration=args.min_duration,
        min_size_kb=args.min_size_kb,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
