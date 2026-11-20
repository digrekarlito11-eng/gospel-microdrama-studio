#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Moteur de Rendu Cinéma 2.5D FFmpeg (render_episode.py)
Orchestre la production complète 100% gratuite d'un épisode (ep-001 .. ep-011) :
  1. Chargement du storyboard canonique (scripts/storyboards.py)
  2. Synthèse vocale française multi-personnages + sous-titres dynamiques ASS/SRT (scripts/voice_engine.py)
  3. Génération des 8-10 scènes IA bi-fournisseur Pollinations + AI Horde + repli PIL (scripts/image_generator.py)
  4. Synthèse musicale Afrogospel adaptée à l'humeur & BPM (scripts/afrogospel_bgm.py)
  5. Animation 2.5D Ken Burns 2x supersampled (sans -loop 1!), transitions xfade 0.45s,
     étalonnage Abidjan Twilight Noir, incrustation ASS + barre dorée, mixage sidechaincompress + loudnorm
  6. Export universel H.264/AAC +faststart : {ep_id}.mp4, {ep_id}_poster.jpg,
     {ep_id}_contact_sheet.jpg, {ep_id}_meta.json
"""

import argparse
import asyncio
import datetime
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
if STUDIO_ROOT not in sys.path:
    sys.path.insert(0, STUDIO_ROOT)

from scripts.afrogospel_bgm import generate_afrogospel_bgm
from scripts.image_generator import SceneImageGenerator
from scripts.storyboards import get_storyboard
from scripts.voice_engine import (
    escape_ass_path_for_ffmpeg,
    probe_audio_duration,
    synthesize_episode_voiceover,
)

FPS = 24
XFADE_DURATION = 0.45

RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "1080p": (1080, 1920),
    "720p": (720, 1280),
}


def _zoompan_expr(motion: str, frames: int, width: int, height: int) -> str:
    """
    Build silky 2.5D Ken Burns zoompan filter expression.
    Enforces minimum zoom >= 1.08 and top-weighted vertical framing (y=(ih-ih/zoom)*0.35)
    to crop out any bottom-right Pollinations logo mark cleanly while keeping faces centered.
    """
    d = max(1, frames - 1)
    if motion == "zoom_in":
        z = f"1.08+0.12*(on/{d})"
        x = "iw/2-(iw/zoom/2)"
        y = "(ih-ih/zoom)*0.35"
    elif motion == "zoom_out":
        z = f"1.20-0.12*(on/{d})"
        x = "iw/2-(iw/zoom/2)"
        y = "(ih-ih/zoom)*0.35"
    elif motion == "pan_left":
        z = "1.16"
        x = f"(iw-iw/zoom)*(1-on/{d})"
        y = "(ih-ih/zoom)*0.35"
    elif motion == "pan_right":
        z = "1.16"
        x = f"(iw-iw/zoom)*(on/{d})"
        y = "(ih-ih/zoom)*0.35"
    elif motion == "push_in_dramatic":
        z = f"1.08+0.18*(on/{d})"
        x = "iw/2-(iw/zoom/2)"
        y = "(ih-ih/zoom)*0.30"
    elif motion == "tilt_up":
        z = "1.18"
        x = "iw/2-(iw/zoom/2)"
        y = f"(ih-ih/zoom)*(0.60-0.40*(on/{d}))"
    else:
        z = f"1.08+0.12*(on/{d})"
        x = "iw/2-(iw/zoom/2)"
        y = "(ih-ih/zoom)*0.35"

    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={width}x{height}:fps={FPS}"


def _render_scene_clip(
    image_path: str,
    motion: str,
    duration: float,
    width: int,
    height: int,
    output_clip: str,
) -> float:
    """
    Render a single 2.5D animated scene clip from a single-frame image input (NEVER -loop 1!).
    Uses 2x supersampling (2160x3840 for 1080p) + unsharp + zoompan @ 24fps.
    """
    frames = max(24, int(round(duration * FPS)))
    actual_dur = frames / float(FPS)
    ss_w, ss_h = width * 2, height * 2
    zp = _zoompan_expr(motion, frames, width, height)

    vf = (
        f"scale={ss_w}:{ss_h}:force_original_aspect_ratio=increase,"
        f"crop={ss_w}:{ss_h},"
        f"unsharp=5:5:0.5:5:5:0.0,"
        f"{zp},"
        f"scale=in_range=full:out_range=tv:out_color_matrix=bt709,"
        f"settb=AVTB,setpts=PTS-STARTPTS,fps={FPS},format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", image_path,
        "-vf", vf,
        "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-an",
        output_clip,
    ]
    subprocess.run(cmd, check=True)
    return actual_dur


def _assemble_master_video(
    scene_clips: List[Tuple[str, float, str]],
    voiceover_path: str,
    bgm_path: str,
    ass_path: str,
    width: int,
    height: int,
    output_mp4: str,
) -> float:
    """
    Combine animated scene clips with exact xfade offsets, Abidjan Twilight Noir color grade,
    burned-in ASS subtitles, animated gold bottom progress bar, sidechaincompress ducked BGM,
    and loudnorm broadcast mastering into universal mobile/web H.264/AAC +faststart MP4.
    """
    if not scene_clips:
        raise ValueError("No scene clips provided for assembly")

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for clip_path, _, _ in scene_clips:
        cmd.extend(["-i", clip_path])

    vo_idx = len(scene_clips)
    bgm_idx = len(scene_clips) + 1
    cmd.extend(["-i", voiceover_path, "-i", bgm_path])

    filters: List[str] = []
    n_clips = len(scene_clips)

    # Normalize timestamps & format of each clip before xfade
    for i in range(n_clips):
        filters.append(f"[{i}:v]settb=AVTB,fps={FPS},format=yuv420p[v{i}]")

    # Chain xfade transitions with exact cumulative offsets
    if n_clips == 1:
        total_vid_dur = scene_clips[0][1]
        last_v = "[v0]"
    else:
        cum_dur = scene_clips[0][1]
        prev_label = "[v0]"
        for i in range(1, n_clips):
            _, dur_i, trans = scene_clips[i]
            offset = max(0.1, cum_dur - XFADE_DURATION)
            out_label = f"[xf{i}]"
            safe_trans = trans if trans in ("fade", "dissolve", "smoothleft", "fadeblack") else "fade"
            filters.append(
                f"{prev_label}[v{i}]xfade=transition={safe_trans}:duration={XFADE_DURATION:.3f}:offset={offset:.3f}{out_label}"
            )
            cum_dur = offset + dur_i
            prev_label = out_label
        total_vid_dur = cum_dur
        last_v = prev_label

    # Abidjan Twilight Noir color grading + vignette
    grade = (
        "eq=contrast=1.08:saturation=1.14:brightness=-0.02,"
        "colorbalance=rs=0.04:gs=0.01:bs=-0.04:rm=0.02:bm=-0.02,"
        "vignette=angle=PI/5"
    )
    escaped_ass = escape_ass_path_for_ffmpeg(ass_path)
    filters.append(f"{last_v}{grade},ass='{escaped_ass}'[subbed]")

    # Animated Abidjan Gold bottom progress bar (#D4AF37, 12px tall at 1080p, 8px at 720p)
    bar_h = 12 if height >= 1900 else 8
    bar_y = height - bar_h
    filters.append(f"color=c=0xD4AF37:s={width}x{bar_h}:r={FPS}:d={total_vid_dur:.3f}[pbar]")
    filters.append(
        f"[subbed][pbar]overlay=x='-W+W*(t/{total_vid_dur:.3f})':y={bar_y}:shortest=1,"
        f"scale=out_range=tv:out_color_matrix=bt709,format=yuv420p[vout]"
    )

    # Broadcast audio mix: sidechaincompress ducking of Afrogospel BGM under dialogue + loudnorm
    filters.append(
        f"[{vo_idx}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        f"volume=1.08,asplit=2[vo_main][vo_sc]"
    )
    filters.append(
        f"[{bgm_idx}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
        f"volume=0.38[bgm_pre]"
    )
    filters.append(
        "[bgm_pre][vo_sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=400[bgm_ducked]"
    )
    filters.append(
        "[vo_main][bgm_ducked]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )

    filter_complex = ";".join(filters)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-shortest",
        output_mp4,
    ])
    subprocess.run(cmd, check=True)
    return probe_audio_duration(output_mp4)


def _extract_poster(video_path: str, duration: float, poster_path: str) -> str:
    """Extract a crisp 9:16 JPEG poster frame at ~20% into the rendered episode."""
    ts = max(1.0, min(duration - 1.5, duration * 0.20))
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{ts:.2f}",
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "3",
            poster_path,
        ],
        check=True,
    )
    return poster_path


def _build_contact_sheet(scene_image_paths: List[str], contact_sheet_path: str) -> str:
    """Build a crisp QA contact sheet JPEG grid of all scene artworks via Pillow."""
    if not scene_image_paths:
        return contact_sheet_path
    cols = 3 if len(scene_image_paths) <= 9 else 4
    rows = math.ceil(len(scene_image_paths) / cols)
    tw, th = 270, 480
    sheet = Image.new("RGB", (cols * tw, rows * th), (7, 7, 9))
    for idx, img_p in enumerate(scene_image_paths):
        try:
            im = Image.open(img_p).convert("RGB")
            thumb = ImageOps.fit(im, (tw, th), method=Image.Resampling.LANCZOS)
            r = idx // cols
            c = idx % cols
            sheet.paste(thumb, (c * tw, r * th))
        except Exception:
            continue
    sheet.save(contact_sheet_path, format="JPEG", quality=88)
    return contact_sheet_path


def _sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render_episode(
    episode_id: str,
    output_dir: str,
    resolution: str = "1080p",
    provider: str = "auto",
    offline_test_audio: bool = False,
    release_tag: str = "episodes-v1",
    keep_work: bool = False,
) -> Dict[str, Any]:
    """Run full end-to-end Option 3 Motion-Cinema rendering for one episode."""
    if resolution not in RESOLUTIONS:
        raise ValueError(f"Unsupported resolution '{resolution}'. Choose from {list(RESOLUTIONS.keys())}")
    width, height = RESOLUTIONS[resolution]

    sb = get_storyboard(episode_id)
    ep_id = sb["episode_id"]
    os.makedirs(output_dir, exist_ok=True)
    work_dir = os.path.join(output_dir, f"_work_{ep_id}")
    scenes_dir = os.path.join(work_dir, "scenes")
    clips_dir = os.path.join(work_dir, "clips")
    os.makedirs(scenes_dir, exist_ok=True)
    os.makedirs(clips_dir, exist_ok=True)

    print("=" * 68)
    print(f"AMINA MOTION-CINEMA PIPELINE | {ep_id.upper()} : {sb['title']}")
    print(f"Resolution: {width}x{height}@{FPS}fps | Provider: {provider} | OfflineAudio: {offline_test_audio}")
    print("=" * 68)

    # 1. Multi-character French TTS & TikTok ASS/SRT captions
    print("\n[1/5] Synthesizing multi-character voiceover & dynamic ASS captions...")
    voice_res = asyncio.run(
        synthesize_episode_voiceover(
            storyboard=sb,
            work_dir=work_dir,
            offline_test_audio=offline_test_audio,
        )
    )
    total_audio_dur = float(voice_res["total_duration"])
    print(
        f"  -> Voiceover ready ({voice_res['tts_mode']}): {total_audio_dur:.2f}s "
        f"across {len(voice_res['scenes'])} scenes."
    )

    # 2. Dual-provider free AI scene images (Pollinations + AI Horde + PIL fallback)
    print("\n[2/5] Generating vertical 9:16 cinematic scene illustrations...")
    img_gen = SceneImageGenerator(provider=provider)
    scene_records, provider_stats = img_gen.generate_episode_scenes(sb, scenes_dir)
    print(f"  -> Scene images ready. Provider stats: {json.dumps(provider_stats)}")

    # 3. Musical Afrogospel BGM matching episode mood & BPM
    print("\n[3/5] Synthesizing musical Afrogospel BGM score...")
    bgm_path = os.path.join(work_dir, "bgm_afrogospel.mp3")
    generate_afrogospel_bgm(
        output_path=bgm_path,
        mood=sb["mood"],
        bpm=float(sb["bpm"]),
        duration=total_audio_dur + 4.0,
    )
    print(f"  -> Afrogospel BGM ready: mood={sb['mood']}, bpm={sb['bpm']}")

    # 4. Per-scene 2.5D Ken Burns 2x supersampled animation
    print("\n[4/5] Rendering 2.5D Ken Burns animated clips (2x supersampled, 24fps)...")
    timing_by_scene = {t["scene_id"]: t for t in voice_res["scenes"]}
    rendered_clips: List[Tuple[str, float, str]] = []
    n_scenes = len(sb["scenes"])

    for idx, (scene, rec) in enumerate(zip(sb["scenes"], scene_records)):
        scene_id = scene["scene_id"]
        audio_dur = float(timing_by_scene[scene_id]["duration"])
        # Extend non-final scenes by XFADE_DURATION so cumulative xfade length matches exact audio duration!
        clip_target_dur = audio_dur + (XFADE_DURATION if idx < n_scenes - 1 else 0.0)
        clip_path = os.path.join(clips_dir, f"{scene_id}_25d.mp4")
        print(f"  -> Clip {idx + 1}/{n_scenes} ({scene_id}, motion={scene['motion']}, dur={clip_target_dur:.2f}s)...")
        actual_dur = _render_scene_clip(
            image_path=rec["path"],
            motion=scene["motion"],
            duration=clip_target_dur,
            width=width,
            height=height,
            output_clip=clip_path,
        )
        rendered_clips.append((clip_path, actual_dur, scene.get("transition", "fade")))

    # 5. Final cinema master assembly + poster + contact sheet + metadata
    print("\n[5/5] Assembling master MP4 (xfade + Twilight Noir grade + ASS + ducking + loudnorm)...")
    final_mp4 = os.path.join(output_dir, f"{ep_id}.mp4")
    final_poster = os.path.join(output_dir, f"{ep_id}_poster.jpg")
    final_contact = os.path.join(output_dir, f"{ep_id}_contact_sheet.jpg")
    final_meta = os.path.join(output_dir, f"{ep_id}_meta.json")
    final_ass = os.path.join(output_dir, f"{ep_id}_captions.ass")
    final_srt = os.path.join(output_dir, f"{ep_id}_captions.srt")

    final_dur = _assemble_master_video(
        scene_clips=rendered_clips,
        voiceover_path=voice_res["voiceover_path"],
        bgm_path=bgm_path,
        ass_path=voice_res["ass_path"],
        width=width,
        height=height,
        output_mp4=final_mp4,
    )
    _extract_poster(final_mp4, final_dur, final_poster)
    _build_contact_sheet([r["path"] for r in scene_records], final_contact)
    shutil.copy2(voice_res["ass_path"], final_ass)
    shutil.copy2(voice_res["srt_path"], final_srt)

    size_bytes = os.path.getsize(final_mp4)
    meta: Dict[str, Any] = {
        "id": ep_id,
        "episode_id": ep_id,
        "episode_number": sb["episode_number"],
        "title": sb["title"],
        "duration": round(final_dur, 2),
        "sizeBytes": size_bytes,
        "resolution": f"{width}x{height}",
        "fps": FPS,
        "hasBurnedSubtitles": True,
        "tts_mode": voice_res["tts_mode"],
        "providers": provider_stats,
        "sceneCount": n_scenes,
        "mood": sb["mood"],
        "bpm": sb["bpm"],
        "sha256": _sha256_file(final_mp4),
        "releaseTag": release_tag,
        "videoFilename": os.path.basename(final_mp4),
        "posterFilename": os.path.basename(final_poster),
        "contactSheetFilename": os.path.basename(final_contact),
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(final_meta, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)

    if not keep_work:
        shutil.rmtree(work_dir, ignore_errors=True)

    print("\n" + "=" * 68)
    print(f"RENDER COMPLETE: {final_mp4}")
    print(f"  Duration : {meta['duration']}s | Size: {size_bytes / (1024 * 1024):.2f} MB | Res: {meta['resolution']}")
    print(f"  TTS Mode : {meta['tts_mode']} | Providers: {json.dumps(provider_stats)}")
    print(f"  Poster   : {final_poster}")
    print(f"  Meta     : {final_meta}")
    print("=" * 68)
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a complete 9:16 Option 3 Motion-Cinema episode (100% free)."
    )
    parser.add_argument("--episode", default="ep-001", help="Episode ID (ep-001..ep-011)")
    parser.add_argument("--output-dir", required=True, help="Output directory for MP4, poster, meta")
    parser.add_argument(
        "--resolution",
        default="1080p",
        choices=("1080p", "720p"),
        help="Vertical output resolution (1080p=1080x1920, 720p=720x1280)",
    )
    parser.add_argument(
        "--provider",
        default="auto",
        choices=("auto", "pollinations", "aihorde", "fallback"),
        help="Free AI image provider strategy",
    )
    parser.add_argument(
        "--offline-test-audio",
        action="store_true",
        help="LOCAL DRY-RUN ONLY: offline voice cadence (rejected by verify_episode --strict-production)",
    )
    parser.add_argument("--release-tag", default="episodes-v1", help="Target GitHub Release tag")
    parser.add_argument("--keep-work", action="store_true", help="Keep intermediate work directory")
    args = parser.parse_args()

    render_episode(
        episode_id=args.episode,
        output_dir=args.output_dir,
        resolution=args.resolution,
        provider=args.provider,
        offline_test_audio=args.offline_test_audio,
        release_tag=args.release_tag,
        keep_work=args.keep_work,
    )


if __name__ == "__main__":
    main()
