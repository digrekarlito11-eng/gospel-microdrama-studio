#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Moteur Voix Multi-Personnages Français & Sous-Titres ASS (voice_engine.py)
- Utilise edge-tts>=7.3.1 exclusivement sur des voix françaises Neural gratuites vérifiées
  (validation dynamique via edge_tts.list_voices() + repli vérifié).
- Capture WordBoundary lorsqu'émis ; sinon mesure exacte ffprobe + découpage proportionnel par mot.
- ANTI-TRICHE : En mode production (défaut), toute erreur Edge-TTS après retries échoue bruyamment
  (jamais de silence anullsrc ni de bip 440Hz silencieux). Un drapeau explicite --offline-test-audio
  existe uniquement pour les smoke tests locaux VM et marque tts_mode="offline_test".
- Génère captions.ass (style TikTok/Reels Abidjan Gold Safe-Zone) + captions.srt dans output_dir
  (NE touche JAMAIS episodes/ep-XXX/subtitles.srt).
"""

import argparse
import array
import asyncio
import json
import math
import os
import re
import subprocess
import tempfile
import wave
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_BIBLE_PATH = os.path.join(STUDIO_ROOT, "bible", "characters.json")

VERIFIED_FRENCH_VOICES = [
    "fr-FR-DeniseNeural",
    "fr-FR-EloiseNeural",
    "fr-FR-VivienneMultilingualNeural",
    "fr-FR-HenriNeural",
    "fr-FR-RemyMultilingualNeural",
    "fr-BE-CharlineNeural",
    "fr-BE-GerardNeural",
    "fr-CH-ArianeNeural",
    "fr-CH-FabriceNeural",
    "fr-CA-SylvieNeural",
    "fr-CA-AntoineNeural",
    "fr-CA-JeanNeural",
    "fr-CA-ThierryNeural",
]

# Safe fallback voices by gender if a specific verified voice is temporarily absent from list_voices()
FEMALE_FALLBACKS = ["fr-FR-DeniseNeural", "fr-FR-VivienneMultilingualNeural", "fr-BE-CharlineNeural", "fr-FR-EloiseNeural"]
MALE_FALLBACKS = ["fr-FR-HenriNeural", "fr-FR-RemyMultilingualNeural", "fr-BE-GerardNeural", "fr-CA-JeanNeural"]

FEMALE_SPEAKERS = {"narrator", "char_amina", "char_helene", "char_sarah", "char_voisine", "char_eleve", "char_kevin"}

# Distinct base frequencies (Hz) for offline dry-run speech-cadence synthesis ONLY
OFFLINE_CHAR_PITCH_HZ = {
    "narrator": 215.0,
    "char_amina": 255.0,
    "char_helene": 195.0,
    "char_koffi": 118.0,
    "char_zagba": 148.0,
    "char_sarah": 270.0,
    "char_kevin": 310.0,
    "char_proprietaire": 132.0,
    "char_acolyte": 162.0,
    "char_chauffeur": 136.0,
    "char_medecin": 142.0,
    "char_voisine": 235.0,
    "char_eleve": 280.0,
    "char_homme_main": 124.0,
}


def clean_text_for_ass(text: str) -> str:
    """
    Strip emojis, non-BMP/symbol glyphs unsupported by DejaVu Sans, and ASS brace tokens
    while preserving French accents, punctuation, guillemets, and dashes.
    """
    if not text:
        return ""
    # Neutralize ASS override braces
    cleaned = text.replace("{", "(").replace("}", ")")
    # Remove non-BMP emojis and dingbat/pictograph blocks
    cleaned = re.sub(
        r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE00-\uFE0F\u200D]",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def escape_ass_path_for_ffmpeg(filepath: str) -> str:
    """Safely escape a filesystem path for FFmpeg's `ass=` filter expression."""
    p = os.path.abspath(filepath).replace("\\", "/")
    p = p.replace(":", "\\:")
    p = p.replace("'", "\\'")
    return p


def format_ass_time(seconds: float) -> str:
    """Format seconds as ASS timestamp `H:MM:SS.cs`."""
    s = max(0.0, float(seconds))
    hrs = int(s // 3600)
    mins = int((s % 3600) // 60)
    secs = int(s % 60)
    cs = int(round((s - math.floor(s)) * 100))
    if cs >= 100:
        secs += 1
        cs -= 100
    if secs >= 60:
        mins += 1
        secs -= 60
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


def format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp `HH:MM:SS,mmm`."""
    s = max(0.0, float(seconds))
    hrs = int(s // 3600)
    mins = int((s % 3600) // 60)
    secs = int(s % 60)
    ms = int(round((s - math.floor(s)) * 1000))
    if ms >= 1000:
        secs += 1
        ms -= 1000
    if secs >= 60:
        mins += 1
        secs -= 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def probe_audio_duration(filepath: str) -> float:
    """Measure exact audio duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return max(0.1, float(res.stdout.strip()))


def load_character_profiles(bible_path: str = DEFAULT_BIBLE_PATH) -> Dict[str, Dict[str, Any]]:
    """Load character definitions and voice profiles from bible/characters.json."""
    with open(bible_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    profiles: Dict[str, Dict[str, Any]] = {}
    for ch in data.get("characters", []):
        vp = ch.get("voice_profile", {})
        profiles[ch["id"]] = {
            "id": ch["id"],
            "name": ch.get("name", ch["id"]),
            "display_label": ch.get("display_label", ""),
            "voice_id": vp.get("voice_id", "fr-FR-DeniseNeural"),
            "pitch": vp.get("pitch", "+0Hz"),
            "rate": vp.get("rate", "+0%"),
            "subtitle_color": vp.get("subtitle_color", "&H00FFFFFF"),
        }
    return profiles


def compute_proportional_word_timings(text: str, total_duration: float) -> List[Dict[str, Any]]:
    """Compute proportional word timings weighted by character length across a line duration."""
    words = [w for w in clean_text_for_ass(text).split() if w]
    if not words:
        return []
    weights = [max(2, len(re.sub(r"[^\wÀ-ÿ]", "", w))) for w in words]
    total_w = float(sum(weights))
    timings: List[Dict[str, Any]] = []
    cursor = 0.0
    for w, wt in zip(words, weights):
        dur = total_duration * (wt / total_w)
        timings.append({"word": w, "start": cursor, "end": cursor + dur})
        cursor += dur
    if timings:
        timings[-1]["end"] = total_duration
    return timings


async def _fetch_available_french_voices() -> set:
    """Query live Edge-TTS voice list and return set of available French ShortNames."""
    import edge_tts

    voices = await edge_tts.list_voices()
    return {
        v["ShortName"]
        for v in voices
        if isinstance(v, dict) and str(v.get("ShortName", "")).startswith("fr-")
    }


def _resolve_verified_voice(
    speaker_id: str,
    requested_voice: str,
    available_voices: Optional[set],
) -> str:
    """Resolve a character voice against live available French Edge-TTS voices."""
    if available_voices:
        if requested_voice in available_voices:
            return requested_voice
        fallbacks = FEMALE_FALLBACKS if speaker_id in FEMALE_SPEAKERS else MALE_FALLBACKS
        for cand in fallbacks:
            if cand in available_voices:
                return cand
        # Last resort: any available French voice
        return sorted(available_voices)[0]
    if requested_voice in VERIFIED_FRENCH_VOICES:
        return requested_voice
    return FEMALE_FALLBACKS[0] if speaker_id in FEMALE_SPEAKERS else MALE_FALLBACKS[0]


async def _synthesize_line_edge_tts(
    text: str,
    voice: str,
    pitch: str,
    rate: str,
    output_mp3: str,
    max_attempts: int = 4,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Synthesize one French dialogue line via edge-tts>=7.3.1 with exponential backoff retries.
    Captures WordBoundary events if emitted; falls back to ffprobe duration + proportional word timings.
    Raises RuntimeError if all attempts fail (NEVER silently emits silence in production).
    """
    import edge_tts

    last_err: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        word_boundaries: List[Dict[str, Any]] = []
        audio_chunks = bytearray()
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                pitch=pitch,
                rate=rate,
                boundary="WordBoundary",
            )
            async for chunk in communicate.stream():
                ctype = chunk.get("type")
                if ctype == "audio":
                    audio_chunks.extend(chunk["data"])
                elif ctype == "WordBoundary":
                    offset_s = float(chunk.get("offset", 0)) / 10_000_000.0
                    dur_s = float(chunk.get("duration", 0)) / 10_000_000.0
                    w_txt = clean_text_for_ass(str(chunk.get("text", "")))
                    if w_txt:
                        word_boundaries.append(
                            {
                                "word": w_txt,
                                "start": offset_s,
                                "end": offset_s + max(0.06, dur_s),
                            }
                        )

            if len(audio_chunks) < 512:
                raise RuntimeError(f"Edge-TTS returned empty audio ({len(audio_chunks)} bytes)")

            os.makedirs(os.path.dirname(os.path.abspath(output_mp3)), exist_ok=True)
            with open(output_mp3, "wb") as fh:
                fh.write(audio_chunks)

            duration = probe_audio_duration(output_mp3)
            if not word_boundaries:
                word_boundaries = compute_proportional_word_timings(text, duration)
            else:
                # Clamp last boundary cleanly to measured audio duration
                word_boundaries[-1]["end"] = max(word_boundaries[-1]["end"], duration)
            return duration, word_boundaries

        except Exception as exc:
            last_err = exc
            if attempt < max_attempts:
                backoff = min(12.0, 1.5 * (2 ** (attempt - 1)))
                print(
                    f"    [Edge-TTS] Attempt {attempt}/{max_attempts} failed ({exc}); "
                    f"retrying in {backoff:.1f}s..."
                )
                await asyncio.sleep(backoff)

    raise RuntimeError(
        f"Edge-TTS synthesis failed after {max_attempts} attempts for voice={voice}: {last_err}"
    )


def _synthesize_line_offline_test(
    speaker_id: str,
    text: str,
    output_mp3: str,
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    LOCAL VM DRY-RUN ONLY (--offline-test-audio).
    Synthesizes an audible formant-modulated syllable cadence track matching the spoken word count
    and speaker pitch so FFmpeg mixing/ducking/subtitles can be smoke-tested behind a MITM proxy.
    Always marked `tts_mode = "offline_test"` so strict production QA rejects it!
    """
    sr = 22050
    words = [w for w in clean_text_for_ass(text).split() if w]
    base_hz = OFFLINE_CHAR_PITCH_HZ.get(speaker_id, 185.0)
    duration = max(1.8, sum(max(0.22, len(w) * 0.058) for w in words))
    n_samples = int(round(duration * sr))
    pcm = array.array("h")

    two_pi = 2.0 * math.pi
    word_timings = compute_proportional_word_timings(text, duration)
    # Build audible speech-like vowel formant bursts per word
    samples = [0.0] * n_samples
    for w_idx, wt in enumerate(word_timings):
        i0 = max(0, int(wt["start"] * sr))
        i1 = min(n_samples, int(wt["end"] * sr))
        span = max(1, i1 - i0)
        # Pitch inflection contour across sentence
        contour = 1.0 + 0.08 * math.sin(w_idx * 1.1) - 0.06 * (w_idx / max(1, len(word_timings)))
        f0 = base_hz * contour
        f1 = f0 * 2.5
        f2 = f0 * 4.2
        phase0 = 0.0
        phase1 = 0.0
        phase2 = 0.0
        for k in range(span):
            u = k / span
            # Smooth syllable envelope with slight gap between words
            env = math.sin(math.pi * min(1.0, u * 1.08)) ** 0.7 if u < 0.92 else 0.0
            vib = 1.0 + 0.015 * math.sin(two_pi * 5.2 * (k / sr))
            phase0 += two_pi * (f0 * vib) / sr
            phase1 += two_pi * f1 / sr
            phase2 += two_pi * f2 / sr
            val = (
                0.55 * math.sin(phase0)
                + 0.30 * math.sin(phase1)
                + 0.15 * math.sin(phase2)
            ) * env * 0.42
            samples[i0 + k] = val

    for s in samples:
        pcm.append(max(-32767, min(32767, int(s * 32000))))

    os.makedirs(os.path.dirname(os.path.abspath(output_mp3)), exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    try:
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", wav_path,
                "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                output_mp3,
            ],
            check=True,
        )
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass

    measured = probe_audio_duration(output_mp3)
    return measured, compute_proportional_word_timings(text, measured)


def _make_silence_mp3(duration: float, output_mp3: str) -> None:
    dur = max(0.05, float(duration))
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", f"{dur:.3f}",
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            output_mp3,
        ],
        check=True,
    )


def _concat_audio_segments(segment_paths: List[str], output_mp3: str) -> float:
    """Concatenate normalized stereo 44.1kHz segments into master voiceover.mp3 using FFmpeg concat filter."""
    if not segment_paths:
        raise ValueError("Cannot concatenate empty audio segment list")

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for p in segment_paths:
        cmd.extend(["-i", p])

    n = len(segment_paths)
    norm_streams = "".join(
        f"[{i}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}];"
        for i in range(n)
    )
    concat_inputs = "".join(f"[a{i}]" for i in range(n))
    fc = f"{norm_streams}{concat_inputs}concat=n={n}:v=0:a=1[outa]"

    cmd.extend([
        "-filter_complex", fc,
        "-map", "[outa]",
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        output_mp3,
    ])
    subprocess.run(cmd, check=True)
    return probe_audio_duration(output_mp3)


def generate_ass_and_srt(
    storyboard: Dict[str, Any],
    timed_lines: List[Dict[str, Any]],
    total_duration: float,
    profiles: Dict[str, Dict[str, Any]],
    ass_path: str,
    srt_path: str,
) -> Tuple[str, str]:
    """
    Build dynamic TikTok/Reels ASS subtitles (PlayRes 1080x1920, DejaVu Sans Bold, Safe-Zone
    MarginL=60 MarginR=140 MarginV=440, 3-5 word chunks with Abidjan Gold active-word highlight,
    speaker label accents, Intro Hook card 0.0-3.0s, Outro Cliffhanger + Book CTA) and matching SRT.
    """
    ep_short = clean_text_for_ass(storyboard.get("short_title", storyboard["episode_id"].upper()))
    hook_txt = clean_text_for_ass(storyboard.get("hook", ""))
    cliff_txt = clean_text_for_ass(storyboard.get("cliffhanger", ""))
    cta_txt = clean_text_for_ass(storyboard.get("cta", "Commandez le roman : +225 07 00 88 95 14"))

    ass_header = """[Script Info]
Title: AMINA L'Autel De Yopougon — Option 3 Cinema Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookHeader,DejaVu Sans,46,&H0037AFD4,&H00FFFFFF,&H00080A14,&HA0070709,-1,0,0,0,100,100,1,0,3,4,2,8,70,110,250,1
Style: SeriesBadge,DejaVu Sans,30,&H00E8DFC8,&H00FFFFFF,&H00080A14,&H800A1128,-1,0,0,0,100,100,1,0,1,3,1,7,60,120,165,1
Style: SpeakerTag,DejaVu Sans,34,&H0037AFD4,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,4,2,2,60,140,565,1
Style: TikTokSub,DejaVu Sans,54,&H00FFFFFF,&H0037AFD4,&H00000000,&H90070709,-1,0,0,0,100,100,0,0,1,5,2,2,60,140,440,1
Style: OutroCliff,DejaVu Sans,44,&H00FFFFFF,&H0037AFD4,&H00080A14,&HB00A1128,-1,0,0,0,100,100,1,0,3,4,2,5,70,110,0,1
Style: OutroCTA,DejaVu Sans,36,&H0037AFD4,&H00FFFFFF,&H00000000,&HC0070709,-1,0,0,0,100,100,1,0,3,4,2,2,60,120,255,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_events: List[str] = []
    srt_entries: List[str] = []
    srt_idx = 1

    # Layer 0: Subtle persistent episode badge top-left
    ass_events.append(
        f"Dialogue: 0,{format_ass_time(0.0)},{format_ass_time(total_duration)},SeriesBadge,,0,0,0,,"
        f"AMINA • {ep_short}"
    )

    # Layer 0: Intro Episode Title + Hook banner (0.0 - 3.0s)
    intro_end = min(3.0, max(1.5, total_duration - 4.0))
    if hook_txt:
        ass_events.append(
            f"Dialogue: 0,{format_ass_time(0.0)},{format_ass_time(intro_end)},HookHeader,,0,0,0,,"
            f"{{\\fad(250,350)}}{ep_short}\\N{{\\c&H00FFFFFF&\\fs38}}{hook_txt}"
        )

    # Layer 1: Dynamic 3-5 word chunks with active-word Abidjan Gold highlight (&H0037AFD4&)
    outro_start = max(intro_end + 1.0, total_duration - 3.6)

    for line in timed_lines:
        sp_id = line["speaker"]
        prof = profiles.get(sp_id, {})
        sp_label = clean_text_for_ass(prof.get("display_label", ""))
        sp_color = prof.get("subtitle_color", "&H0037AFD4")
        line_start = float(line["start"])
        line_end = float(line["end"])
        words = line.get("words") or compute_proportional_word_timings(line["text"], line_end - line_start)

        # SRT entry for the full line
        srt_text = clean_text_for_ass(line["text"])
        if sp_label:
            srt_display = f"[{sp_label}] {srt_text}"
        else:
            srt_display = srt_text
        srt_entries.append(
            f"{srt_idx}\n{format_srt_time(line_start)} --> {format_srt_time(line_end)}\n{srt_display}\n"
        )
        srt_idx += 1

        # Speaker tag for non-narrator dialogue
        if sp_label:
            tag_end = min(line_end, outro_start - 0.1) if line_start < outro_start - 0.2 else line_end
            if tag_end > line_start + 0.05:
                ass_events.append(
                    f"Dialogue: 1,{format_ass_time(line_start)},{format_ass_time(tag_end)},SpeakerTag,,0,0,0,,"
                    f"{{\\c{sp_color}&}}{sp_label}"
                )

        # Group words into 4-word chunks (3-5 words per screen)
        chunk_size = 4
        for c_start in range(0, len(words), chunk_size):
            chunk = words[c_start : c_start + chunk_size]
            if not chunk:
                continue
            for active_i, active_w in enumerate(chunk):
                w_start = line_start + float(active_w["start"])
                if active_i + 1 < len(chunk):
                    w_end = line_start + float(chunk[active_i + 1]["start"])
                else:
                    w_end = line_start + float(active_w["end"])
                w_end = max(w_start + 0.08, min(w_end, line_end))

                rendered_tokens: List[str] = []
                for idx_t, tok in enumerate(chunk):
                    w_clean = clean_text_for_ass(tok["word"])
                    if idx_t == active_i:
                        # Active word in bright Abidjan Gold (#D4AF37 -> BGR &H0037AFD4&)
                        rendered_tokens.append(f"{{\\c&H0037AFD4&}}{w_clean}{{\\c&H00FFFFFF&}}")
                    else:
                        rendered_tokens.append(w_clean)

                ass_line_text = " ".join(rendered_tokens)
                ass_events.append(
                    f"Dialogue: 1,{format_ass_time(w_start)},{format_ass_time(w_end)},TikTokSub,,0,0,0,,"
                    f"{ass_line_text}"
                )

    # Layer 2: Outro Cliffhanger + Book CTA (last ~3.6 seconds)
    if cliff_txt:
        ass_events.append(
            f"Dialogue: 2,{format_ass_time(outro_start)},{format_ass_time(total_duration)},OutroCliff,,0,0,0,,"
            f"{{\\fad(300,250)}}{cliff_txt}"
        )
    if cta_txt:
        ass_events.append(
            f"Dialogue: 2,{format_ass_time(outro_start)},{format_ass_time(total_duration)},OutroCTA,,0,0,0,,"
            f"{{\\fad(300,200)}}{cta_txt}"
        )

    os.makedirs(os.path.dirname(os.path.abspath(ass_path)), exist_ok=True)
    with open(ass_path, "w", encoding="utf-8") as fh:
        fh.write(ass_header + "\n".join(ass_events) + "\n")

    with open(srt_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(srt_entries))

    return ass_path, srt_path


async def synthesize_episode_voiceover(
    storyboard: Dict[str, Any],
    work_dir: str,
    bible_path: str = DEFAULT_BIBLE_PATH,
    offline_test_audio: bool = False,
) -> Dict[str, Any]:
    """
    Synthesize full multi-character French voiceover + captions.ass + captions.srt for an episode.
    Returns dict with:
      - voiceover_path, ass_path, srt_path
      - total_duration
      - tts_mode ("edge_tts" | "offline_test")
      - scenes: [{"scene_id", "start", "end", "duration"}]
      - lines: timed line list
    """
    os.makedirs(work_dir, exist_ok=True)
    lines_dir = os.path.join(work_dir, "tts_lines")
    os.makedirs(lines_dir, exist_ok=True)

    profiles = load_character_profiles(bible_path)
    available_voices: Optional[set] = None

    if not offline_test_audio:
        try:
            available_voices = await _fetch_available_french_voices()
            print(f"  [Voice] Live Edge-TTS verified {len(available_voices)} French voices.")
        except Exception as exc:
            raise RuntimeError(
                f"Edge-TTS voice list query failed in production mode ({exc}). "
                "Verify internet access and edge-tts>=7.3.1 (use --offline-test-audio only for local dry-runs)."
            ) from exc

    segments: List[str] = []
    timed_lines: List[Dict[str, Any]] = []
    scene_timings: List[Dict[str, Any]] = []

    cursor = 0.0
    seg_counter = 0

    # Brief 0.45s cinematic intro breath before first spoken word
    intro_pad = 0.45
    intro_sil = os.path.join(lines_dir, f"seg_{seg_counter:03d}_intro_sil.mp3")
    _make_silence_mp3(intro_pad, intro_sil)
    segments.append(intro_sil)
    cursor += probe_audio_duration(intro_sil)
    seg_counter += 1

    scenes = storyboard["scenes"]
    for s_idx, scene in enumerate(scenes):
        scene_id = scene["scene_id"]
        scene_start = cursor
        for l_idx, line in enumerate(scene["dialogue"]):
            speaker = line["speaker"]
            text = line["text"]
            pause_after = float(line.get("pause_after", 0.35))
            prof = profiles.get(speaker)
            if not prof:
                raise KeyError(f"Speaker '{speaker}' not found in {bible_path}")

            line_mp3 = os.path.join(lines_dir, f"seg_{seg_counter:03d}_{scene_id}_{l_idx:02d}_{speaker}.mp3")
            seg_counter += 1

            if offline_test_audio:
                dur, words = _synthesize_line_offline_test(speaker, text, line_mp3)
            else:
                voice_id = _resolve_verified_voice(speaker, prof["voice_id"], available_voices)
                print(f"  [TTS {scene_id}] [{speaker}] ({voice_id}): {text[:56]}...")
                dur, words = await _synthesize_line_edge_tts(
                    text=text,
                    voice=voice_id,
                    pitch=prof["pitch"],
                    rate=prof["rate"],
                    output_mp3=line_mp3,
                )

            segments.append(line_mp3)
            line_start = cursor
            line_end = cursor + dur
            cursor = line_end

            timed_lines.append(
                {
                    "scene_id": scene_id,
                    "speaker": speaker,
                    "text": text,
                    "start": round(line_start, 3),
                    "end": round(line_end, 3),
                    "duration": round(dur, 3),
                    "words": words,
                }
            )

            if pause_after > 0.05:
                pause_mp3 = os.path.join(lines_dir, f"seg_{seg_counter:03d}_pause.mp3")
                seg_counter += 1
                _make_silence_mp3(pause_after, pause_mp3)
                segments.append(pause_mp3)
                cursor += probe_audio_duration(pause_mp3)

        # Ensure every visual scene lasts at least 4.5s (plus extra 2.5s outro breath on final scene)
        min_scene_dur = 6.2 if s_idx == len(scenes) - 1 else 4.5
        elapsed = cursor - scene_start
        if s_idx == len(scenes) - 1:
            # Always give at least 2.2s tail after final line for the Outro Cliffhanger + CTA card
            extra_tail = max(2.2, min_scene_dur - elapsed)
        else:
            extra_tail = max(0.0, min_scene_dur - elapsed)

        if extra_tail > 0.08:
            tail_mp3 = os.path.join(lines_dir, f"seg_{seg_counter:03d}_tail.mp3")
            seg_counter += 1
            _make_silence_mp3(extra_tail, tail_mp3)
            segments.append(tail_mp3)
            cursor += probe_audio_duration(tail_mp3)

        scene_timings.append(
            {
                "scene_id": scene_id,
                "start": round(scene_start, 3),
                "end": round(cursor, 3),
                "duration": round(cursor - scene_start, 3),
            }
        )

    voiceover_path = os.path.join(work_dir, "voiceover.mp3")
    total_duration = _concat_audio_segments(segments, voiceover_path)

    # Adjust last scene end slightly to match exact concatenated voiceover duration
    if scene_timings:
        drift = total_duration - scene_timings[-1]["end"]
        scene_timings[-1]["end"] = round(total_duration, 3)
        scene_timings[-1]["duration"] = round(max(4.5, scene_timings[-1]["duration"] + drift), 3)

    ass_path = os.path.join(work_dir, "captions.ass")
    srt_path = os.path.join(work_dir, "captions.srt")
    generate_ass_and_srt(
        storyboard=storyboard,
        timed_lines=timed_lines,
        total_duration=total_duration,
        profiles=profiles,
        ass_path=ass_path,
        srt_path=srt_path,
    )

    tts_mode = "offline_test" if offline_test_audio else "edge_tts"
    return {
        "episode_id": storyboard["episode_id"],
        "tts_mode": tts_mode,
        "voiceover_path": voiceover_path,
        "ass_path": ass_path,
        "srt_path": srt_path,
        "total_duration": round(total_duration, 3),
        "scenes": scene_timings,
        "lines": timed_lines,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-character French Edge-TTS voice & TikTok ASS caption generator."
    )
    parser.add_argument("--episode", default="ep-001", help="Episode ID (ep-001..ep-011)")
    parser.add_argument("--output-dir", required=True, help="Work/output directory for voiceover & captions")
    parser.add_argument("--bible", default=DEFAULT_BIBLE_PATH, help="Path to bible/characters.json")
    parser.add_argument(
        "--offline-test-audio",
        action="store_true",
        help="LOCAL DRY-RUN ONLY: synthesize offline speech-cadence audio (rejected by strict QA)",
    )
    args = parser.parse_args()

    from scripts.storyboards import get_storyboard  # type: ignore

    sb = get_storyboard(args.episode)
    result = asyncio.run(
        synthesize_episode_voiceover(
            storyboard=sb,
            work_dir=args.output_dir,
            bible_path=args.bible,
            offline_test_audio=args.offline_test_audio,
        )
    )
    meta_out = os.path.join(args.output_dir, "voice_timings.json")
    with open(meta_out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(
        f"Voice synthesis complete ({result['tts_mode']}): {result['voiceover_path']} "
        f"({result['total_duration']}s, {len(result['lines'])} lines)"
    )


if __name__ == "__main__":
    main()
