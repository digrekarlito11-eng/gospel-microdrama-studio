#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Synthétiseur Musical Afrogospel (afrogospel_bgm.py)
Génère des bandes originales musicales harmoniques et chaleureuses (Rhodes/piano électrique,
nappe de cordes gospel, basse mélodique, percussions Afrogospel subtiles) en pur Python + FFmpeg,
sans aucune dépendance externe ni API payante.

Quatre ambiances dramatiques :
  - twilight_tension   : Abidjan nocturne, accords mineurs 9e cinématographiques, groove discret
  - sanctuary_prayer   : Autel de prière, piano worship doux, nappes célestes soutenues
  - spiritual_warfare  : Combat invisible, basse profonde, pulsation tendue, tensions harmoniques
  - victory_dawn       : Triomphe et aube nouvelle, hymne Afrogospel majeur lumineux et entraînant
"""

import argparse
import array
import math
import os
import subprocess
import tempfile
import wave
from typing import Dict, List, Tuple

SAMPLE_RATE = 22050  # Fast pure-Python synthesis; upsampled cleanly to 44.1kHz stereo by FFmpeg

# MIDI note -> frequency helper
def midi_to_hz(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


# Mood definitions: chord progressions (4 bars), bass roots, melody motifs (MIDI notes), percussion profile
MOOD_CONFIGS: Dict[str, Dict] = {
    "twilight_tension": {
        "default_bpm": 100,
        # Dm9 -> Bbmaj7 -> Gm9 -> A7sus4
        "chords": [
            [50, 57, 60, 64, 65],  # Dm9
            [46, 53, 57, 62, 65],  # Bbmaj7
            [43, 50, 53, 57, 58],  # Gm9
            [45, 52, 55, 57, 62],  # A7sus4
        ],
        "bass": [38, 34, 31, 33],
        "melody_b": [69, 65, 64, 62, 65, 69, 72, 69, 67, 65, 62, 60, 64, 62, 60, 57],
        "kick_steps": (0, 6, 8, 14),
        "clave_steps": (3, 10, 12),
        "shaker_level": 0.045,
        "kick_level": 0.24,
        "pad_warmth": 0.22,
    },
    "sanctuary_prayer": {
        "default_bpm": 78,
        # Fmaj9 -> Dm9 -> Bbmaj7 -> C9sus4
        "chords": [
            [53, 57, 60, 64, 67],  # Fmaj9
            [50, 57, 60, 64, 65],  # Dm9
            [46, 53, 57, 62, 65],  # Bbmaj7
            [48, 55, 58, 62, 65],  # C9sus4
        ],
        "bass": [41, 38, 34, 36],
        "melody_b": [72, 69, 67, 65, 69, 72, 74, 72, 70, 69, 65, 62, 67, 69, 72, 67],
        "kick_steps": (0, 8),
        "clave_steps": (4, 12),
        "shaker_level": 0.022,
        "kick_level": 0.14,
        "pad_warmth": 0.28,
    },
    "spiritual_warfare": {
        "default_bpm": 112,
        # Cm9 -> Abmaj7 -> Fm9 -> G7b9/sus4
        "chords": [
            [48, 55, 58, 62, 63],  # Cm9
            [44, 51, 55, 60, 63],  # Abmaj7
            [41, 48, 51, 55, 56],  # Fm9
            [43, 50, 53, 55, 59],  # G7
        ],
        "bass": [36, 32, 29, 31],
        "melody_b": [67, 63, 62, 60, 63, 67, 70, 67, 65, 63, 60, 58, 62, 60, 59, 55],
        "kick_steps": (0, 3, 6, 8, 11, 14),
        "clave_steps": (2, 6, 10, 14),
        "shaker_level": 0.055,
        "kick_level": 0.30,
        "pad_warmth": 0.20,
    },
    "victory_dawn": {
        "default_bpm": 115,
        # Gmaj9 -> Em9 -> Cmaj9 -> D9sus4
        "chords": [
            [55, 59, 62, 66, 69],  # Gmaj9
            [52, 59, 62, 66, 67],  # Em9
            [48, 55, 59, 62, 64],  # Cmaj9
            [50, 57, 60, 64, 67],  # D9sus4
        ],
        "bass": [43, 40, 36, 38],
        "melody_b": [71, 74, 76, 74, 71, 69, 71, 74, 72, 71, 67, 64, 69, 71, 74, 71],
        "kick_steps": (0, 6, 8, 10, 14),
        "clave_steps": (3, 6, 10, 12),
        "shaker_level": 0.050,
        "kick_level": 0.24,
        "pad_warmth": 0.24,
    },
}


def _add_rhodes_note(
    left: List[float],
    right: List[float],
    start_idx: int,
    dur_samples: int,
    freq: float,
    amp: float,
    pan: float = 0.0,
) -> None:
    """Synthesize a warm Rhodes electric piano tone (fundamental + soft bell tine)."""
    n_total = len(left)
    end_idx = min(n_total, start_idx + dur_samples)
    if start_idx >= n_total or end_idx <= start_idx:
        return

    two_pi = 2.0 * math.pi
    w1 = two_pi * freq / SAMPLE_RATE
    w2 = two_pi * (freq * 2.0) / SAMPLE_RATE
    w3 = two_pi * (freq * 3.0) / SAMPLE_RATE
    w_tine = two_pi * (freq * 7.0) / SAMPLE_RATE
    trem_w = two_pi * 3.2 / SAMPLE_RATE

    gain_l = amp * math.sqrt(0.5 * (1.0 - pan))
    gain_r = amp * math.sqrt(0.5 * (1.0 + pan))
    attack_s = max(1, int(0.012 * SAMPLE_RATE))
    decay_rate = 1.65 / max(0.25, dur_samples / SAMPLE_RATE)
    tine_decay = 9.5 / SAMPLE_RATE
    rel_start = max(0, dur_samples - int(0.08 * SAMPLE_RATE))
    rel_len = max(1, dur_samples - rel_start)

    for i in range(end_idx - start_idx):
        t = i / SAMPLE_RATE
        env = math.exp(-decay_rate * t)
        if i < attack_s:
            env *= i / attack_s
        if i > rel_start:
            env *= max(0.0, 1.0 - (i - rel_start) / rel_len)

        trem = 0.92 + 0.08 * math.sin(trem_w * i)
        tine = 0.14 * math.exp(-tine_decay * i) * math.sin(w_tine * i)
        sample = (
            0.72 * math.sin(w1 * i)
            + 0.20 * math.sin(w2 * i)
            + 0.06 * math.sin(w3 * i)
            + tine
        ) * env * trem

        idx = start_idx + i
        left[idx] += sample * gain_l
        right[idx] += sample * gain_r


def _add_pad_chord(
    left: List[float],
    right: List[float],
    start_idx: int,
    dur_samples: int,
    notes: List[int],
    amp: float,
) -> None:
    """Warm stereo gospel string/organ pad with gentle slow swell and slight detune."""
    n_total = len(left)
    end_idx = min(n_total, start_idx + dur_samples)
    if start_idx >= n_total or end_idx <= start_idx:
        return

    two_pi = 2.0 * math.pi
    attack = max(1, int(0.35 * SAMPLE_RATE))
    release = max(1, int(0.35 * SAMPLE_RATE))
    rel_start = max(0, dur_samples - release)
    per_note_amp = amp / max(1, len(notes))

    # Precompute angular velocities for left/right gently detuned voices
    voice_params = []
    for idx_n, m in enumerate(notes):
        f = midi_to_hz(m)
        w_l = two_pi * (f * 0.9985) / SAMPLE_RATE
        w_r = two_pi * (f * 1.0015) / SAMPLE_RATE
        w2_l = w_l * 2.0
        w2_r = w_r * 2.0
        phase = idx_n * 0.7
        voice_params.append((w_l, w_r, w2_l, w2_r, phase))

    lfo_w = two_pi * 0.35 / SAMPLE_RATE
    span = end_idx - start_idx
    for i in range(span):
        env = 1.0
        if i < attack:
            env = i / attack
        elif i > rel_start:
            env = max(0.0, 1.0 - (i - rel_start) / release)
        breath = 0.88 + 0.12 * math.sin(lfo_w * i)
        scale = per_note_amp * env * breath
        sl = 0.0
        sr = 0.0
        for w_l, w_r, w2_l, w2_r, ph in voice_params:
            sl += 0.82 * math.sin(w_l * i + ph) + 0.18 * math.sin(w2_l * i + ph)
            sr += 0.82 * math.sin(w_r * i + ph) + 0.18 * math.sin(w2_r * i + ph)
        pos = start_idx + i
        left[pos] += sl * scale
        right[pos] += sr * scale


def _add_bass_note(
    left: List[float],
    right: List[float],
    start_idx: int,
    dur_samples: int,
    freq: float,
    amp: float,
) -> None:
    """Warm deep melodic bass (fundamental + 2nd harmonic warmth)."""
    n_total = len(left)
    end_idx = min(n_total, start_idx + dur_samples)
    if start_idx >= n_total or end_idx <= start_idx:
        return

    two_pi = 2.0 * math.pi
    w1 = two_pi * freq / SAMPLE_RATE
    w2 = two_pi * (freq * 2.0) / SAMPLE_RATE
    attack = max(1, int(0.015 * SAMPLE_RATE))
    rel_start = max(0, dur_samples - int(0.06 * SAMPLE_RATE))
    rel_len = max(1, dur_samples - rel_start)

    for i in range(end_idx - start_idx):
        t = i / SAMPLE_RATE
        env = math.exp(-1.1 * t)
        if i < attack:
            env *= i / attack
        if i > rel_start:
            env *= max(0.0, 1.0 - (i - rel_start) / rel_len)
        s = (0.80 * math.sin(w1 * i) + 0.20 * math.sin(w2 * i)) * env * amp
        idx = start_idx + i
        left[idx] += s
        right[idx] += s


def _add_soft_kick(left: List[float], right: List[float], start_idx: int, amp: float) -> None:
    """Warm rounded Afrogospel kick drum with pitch envelope 115Hz -> 46Hz."""
    dur = int(0.18 * SAMPLE_RATE)
    end_idx = min(len(left), start_idx + dur)
    phase = 0.0
    for i in range(end_idx - start_idx):
        t = i / SAMPLE_RATE
        freq = 46.0 + 70.0 * math.exp(-32.0 * t)
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        env = math.exp(-15.0 * t)
        if i < 40:
            env *= i / 40.0
        s = math.sin(phase) * env * amp
        idx = start_idx + i
        left[idx] += s
        right[idx] += s


def _add_clave(left: List[float], right: List[float], start_idx: int, amp: float, pan: float = 0.25) -> None:
    """Soft West African wooden rim/clave percussive tap."""
    dur = int(0.055 * SAMPLE_RATE)
    end_idx = min(len(left), start_idx + dur)
    two_pi = 2.0 * math.pi
    w1 = two_pi * 880.0 / SAMPLE_RATE
    w2 = two_pi * 1760.0 / SAMPLE_RATE
    gl = amp * math.sqrt(0.5 * (1.0 - pan))
    gr = amp * math.sqrt(0.5 * (1.0 + pan))
    for i in range(end_idx - start_idx):
        t = i / SAMPLE_RATE
        env = math.exp(-55.0 * t)
        s = (0.75 * math.sin(w1 * i) + 0.25 * math.sin(w2 * i)) * env
        idx = start_idx + i
        left[idx] += s * gl
        right[idx] += s * gr


def _add_shaker(left: List[float], right: List[float], start_idx: int, amp: float, seed: int, pan: float = -0.25) -> None:
    """Gentle high-passed deterministic shaker grain."""
    dur = int(0.045 * SAMPLE_RATE)
    end_idx = min(len(left), start_idx + dur)
    gl = amp * math.sqrt(0.5 * (1.0 - pan))
    gr = amp * math.sqrt(0.5 * (1.0 + pan))
    state = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    prev = 0.0
    for i in range(end_idx - start_idx):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        noise = ((state / 0x3FFFFFFF) - 1.0)
        # Simple 1st-order highpass for crisp light shaker
        hp = noise - 0.82 * prev
        prev = noise
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / max(1, dur)) * math.exp(-26.0 * t)
        s = hp * env
        idx = start_idx + i
        left[idx] += s * gl
        right[idx] += s * gr


def _render_four_bar_section(
    cfg: Dict,
    bpm: float,
    full_arrangement: bool,
) -> Tuple[List[float], List[float]]:
    """Synthesize a 4-bar stereo musical loop (Section A = intimate, Section B = full Afrogospel groove)."""
    effective_bpm = max(65.0, min(138.0, float(bpm)))
    # For high-tempo entries (>118 BPM), use half-time harmonic feel so chords breathe musically
    beat_sec = 60.0 / effective_bpm
    bar_sec = beat_sec * 4.0
    step_sec = beat_sec / 4.0  # 16th notes
    total_sec = bar_sec * 4.0
    n_samples = int(round(total_sec * SAMPLE_RATE))

    left = [0.0] * n_samples
    right = [0.0] * n_samples

    chords = cfg["chords"]
    bass_roots = cfg["bass"]
    melody = cfg["melody_b"]

    for bar_idx in range(4):
        bar_start = int(round(bar_idx * bar_sec * SAMPLE_RATE))
        bar_len = int(round(bar_sec * SAMPLE_RATE))
        chord = chords[bar_idx]
        bass_midi = bass_roots[bar_idx]

        # 1. Warm sustained gospel pad across the whole bar
        _add_pad_chord(left, right, bar_start, bar_len, chord, cfg["pad_warmth"])

        # 2. Rhodes electric piano chords (warm rolling gospel strum on beat 1 & syncopated beat 3.5)
        for n_i, midi_note in enumerate(chord):
            strum_offset = int(n_i * 0.022 * SAMPLE_RATE)
            pan = -0.35 + (0.70 * n_i / max(1, len(chord) - 1))
            _add_rhodes_note(
                left, right,
                bar_start + strum_offset,
                int(bar_len * 0.88),
                midi_to_hz(midi_note),
                0.15 if not full_arrangement else 0.16,
                pan=pan,
            )

        # Syncopated Rhodes anticipation on 16th step 10 (Afrogospel bounce)
        sync_start = bar_start + int(round(10 * step_sec * SAMPLE_RATE))
        for n_i, midi_note in enumerate(chord[1:]):
            _add_rhodes_note(
                left, right,
                sync_start + int(n_i * 0.015 * SAMPLE_RATE),
                int(round(6 * step_sec * SAMPLE_RATE)),
                midi_to_hz(midi_note),
                0.095,
                pan=0.2 if n_i % 2 == 0 else -0.2,
            )

        # 3. Deep melodic bass (beat 1 + octave/fifth Afrogospel pickup)
        _add_bass_note(
            left, right,
            bar_start,
            int(round(6 * step_sec * SAMPLE_RATE)),
            midi_to_hz(bass_midi),
            0.28,
        )
        _add_bass_note(
            left, right,
            bar_start + int(round(6 * step_sec * SAMPLE_RATE)),
            int(round(4 * step_sec * SAMPLE_RATE)),
            midi_to_hz(bass_midi + 7),
            0.20,
        )
        _add_bass_note(
            left, right,
            bar_start + int(round(10 * step_sec * SAMPLE_RATE)),
            int(round(6 * step_sec * SAMPLE_RATE)),
            midi_to_hz(bass_midi),
            0.24,
        )

        # 4. Expressive melody & Afrogospel percussion in Section B (or subtle pulse in Section A)
        if full_arrangement:
            for beat_i in range(4):
                m_note = melody[(bar_idx * 4 + beat_i) % len(melody)]
                # Gentle syncopation on beats 2 & 4
                sub_step = beat_i * 4 + (1 if beat_i in (1, 3) else 0)
                m_start = bar_start + int(round(sub_step * step_sec * SAMPLE_RATE))
                _add_rhodes_note(
                    left, right,
                    m_start,
                    int(round(4.2 * step_sec * SAMPLE_RATE)),
                    midi_to_hz(m_note),
                    0.125,
                    pan=0.18 if beat_i % 2 == 0 else -0.18,
                )

            for step in range(16):
                s_idx = bar_start + int(round(step * step_sec * SAMPLE_RATE))
                if step in cfg["kick_steps"]:
                    _add_soft_kick(left, right, s_idx, cfg["kick_level"])
                if step in cfg["clave_steps"]:
                    _add_clave(left, right, s_idx, 0.085, pan=0.28 if step % 2 == 0 else -0.22)
                if step % 2 == 0:
                    accent = 1.0 if step % 4 == 2 else 0.55
                    _add_shaker(left, right, s_idx, cfg["shaker_level"] * accent, bar_idx * 31 + step)
        else:
            # Section A: subtle heartbeat kick & gentle shaker so intro feels alive and musical
            for step in (0, 8):
                s_idx = bar_start + int(round(step * step_sec * SAMPLE_RATE))
                _add_soft_kick(left, right, s_idx, cfg["kick_level"] * 0.65)
            for step in (2, 6, 10, 14):
                s_idx = bar_start + int(round(step * step_sec * SAMPLE_RATE))
                _add_shaker(left, right, s_idx, cfg["shaker_level"] * 0.5, bar_idx * 17 + step)

    return left, right


def generate_afrogospel_bgm(
    output_path: str,
    mood: str = "twilight_tension",
    bpm: float = 100.0,
    duration: float = 75.0,
) -> str:
    """
    Generate a lush, genuinely musical stereo Afrogospel MP3 soundtrack at `output_path`.
    """
    if mood not in MOOD_CONFIGS:
        mood = "twilight_tension"
    cfg = MOOD_CONFIGS[mood]
    use_bpm = float(bpm) if bpm and bpm > 0 else float(cfg["default_bpm"])
    target_duration = max(10.0, float(duration))

    # Synthesize Section A (intimate) and Section B (full groove), then arrange A-B-B-A-B...
    sec_a_l, sec_a_r = _render_four_bar_section(cfg, use_bpm, full_arrangement=False)
    sec_b_l, sec_b_r = _render_four_bar_section(cfg, use_bpm, full_arrangement=True)

    target_samples = int(round((target_duration + 0.5) * SAMPLE_RATE))
    pattern = [(sec_a_l, sec_a_r), (sec_b_l, sec_b_r), (sec_b_l, sec_b_r), (sec_a_l, sec_a_r)]

    full_l: List[float] = []
    full_r: List[float] = []
    p_idx = 0
    while len(full_l) < target_samples:
        chunk_l, chunk_r = pattern[p_idx % len(pattern)]
        full_l.extend(chunk_l)
        full_r.extend(chunk_r)
        p_idx += 1

    full_l = full_l[:target_samples]
    full_r = full_r[:target_samples]

    # Soft peak normalization with gentle tanh warmth
    peak = max(1e-6, max(max(abs(x) for x in full_l), max(abs(x) for x in full_r)))
    scale = 0.85 / peak
    pcm = array.array("h")
    for l_val, r_val in zip(full_l, full_r):
        sl = math.tanh(l_val * scale * 1.15)
        sr = math.tanh(r_val * scale * 1.15)
        pcm.append(max(-32767, min(32767, int(sl * 32000))))
        pcm.append(max(-32767, min(32767, int(sr * 32000))))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    try:
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm.tobytes())

        fade_out_start = max(0.5, target_duration - 2.2)
        # Warm stereo mastering: subtle hall echo, gentle EQ, fade in/out, broadcast loudness
        af_chain = (
            f"aresample=44100,"
            f"highpass=f=35,"
            f"lowpass=f=11500,"
            f"aecho=0.85:0.86:48|82:0.28|0.18,"
            f"equalizer=f=220:t=q:w=1.2:g=1.5,"
            f"equalizer=f=3200:t=q:w=1.5:g=-1.5,"
            f"afade=t=in:st=0:d=1.4,"
            f"afade=t=out:st={fade_out_start:.2f}:d=2.2,"
            f"loudnorm=I=-18:TP=-2.0:LRA=9"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", wav_path,
            "-t", f"{target_duration:.2f}",
            "-af", af_chain,
            "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            output_path,
        ]
        subprocess.run(cmd, check=True)
    finally:
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize musical Afrogospel BGM soundtrack (pure Python + FFmpeg)."
    )
    parser.add_argument(
        "--mood",
        default="twilight_tension",
        choices=list(MOOD_CONFIGS.keys()),
        help="Dramatic musical mood",
    )
    parser.add_argument("--bpm", type=float, default=0.0, help="Tempo in BPM (0 = mood default)")
    parser.add_argument("--duration", type=float, default=75.0, help="Track duration in seconds")
    parser.add_argument("--output", required=True, help="Output MP3 filepath")
    args = parser.parse_args()

    out = generate_afrogospel_bgm(
        output_path=args.output,
        mood=args.mood,
        bpm=args.bpm,
        duration=args.duration,
    )
    size_kb = os.path.getsize(out) / 1024.0
    print(f"Generated musical Afrogospel BGM: {out} ({size_kb:.1f} KB, mood={args.mood}, dur={args.duration}s)")


if __name__ == "__main__":
    main()
