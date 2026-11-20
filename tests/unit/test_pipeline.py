#!/usr/bin/env python3
"""
Option 3 Motion-Cinema Pipeline — Comprehensive Python Unit Test Suite (tests/unit/test_pipeline.py)
Validates storyboards, free French Edge-TTS voice bible, ASS Safe-Zone captions,
dual-provider free AI image generator + PIL fallback, musical Afrogospel BGM,
manifest publisher, strict-production QA gate, and GitHub Actions workflow YAML.
"""

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

import yaml
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts import (  # noqa: E402
    afrogospel_bgm,
    image_generator,
    publish_manifest,
    storyboards,
    verify_episode,
    voice_engine,
)

EXPECTED_13_FREE_VOICES = {
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
}

FORBIDDEN_PAID_VOICES = {"fr-FR-AlainNeural", "fr-FR-ClaudeNeural"}


def _ffprobe_json(filepath: str) -> dict:
    res = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            filepath,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout)


def _volumedetect_mean_db(filepath: str) -> float:
    res = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            filepath,
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    match = re.search(r"mean_volume:\s*([-+]?\d+(?:\.\d+)?)\s*dB", res.stderr)
    if not match:
        raise AssertionError(f"volumedetect failed for {filepath}:\n{res.stderr}")
    return float(match.group(1))


class TestStoryboardsAndCharacters(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bible_path = os.path.join(REPO_ROOT, "bible", "characters.json")
        with open(cls.bible_path, "r", encoding="utf-8") as fh:
            cls.bible = json.load(fh)
        cls.valid_speaker_ids = {c["id"] for c in cls.bible["characters"]}

    def test_all_11_storyboards_structure_prompts_and_dialogues(self) -> None:
        expected_ids = [f"ep-{i:03d}" for i in range(1, 12)]
        self.assertEqual(storyboards.get_all_episode_ids(), expected_ids)

        for idx, ep_id in enumerate(expected_ids, start=1):
            sb = storyboards.get_storyboard(ep_id)
            self.assertEqual(sb["episode_id"], ep_id)
            self.assertEqual(sb["episode_number"], idx)
            self.assertTrue(sb["title"].strip())
            self.assertTrue(sb["hook"].strip())
            self.assertTrue(sb["cliffhanger"].strip())
            self.assertIn("+225 07 00 88 95 14", sb["cta"])
            self.assertIn(sb["mood"], storyboards.VALID_MOODS)
            self.assertGreater(sb["bpm"], 50)

            scenes = sb["scenes"]
            self.assertGreaterEqual(len(scenes), 8, f"{ep_id} must have >= 8 scenes")
            self.assertLessEqual(len(scenes), 10, f"{ep_id} must have <= 10 scenes")

            seen_scene_ids = set()
            for sc in scenes:
                sid = sc["scene_id"]
                self.assertNotIn(sid, seen_scene_ids, f"Duplicate scene_id {sid} in {ep_id}")
                seen_scene_ids.add(sid)

                prompt = sc["prompt"]
                self.assertGreater(len(prompt.strip()), 80, f"{ep_id}/{sid} prompt too short")
                self.assertIn("Abidjan Twilight Noir", prompt)
                self.assertIn("no watermark", prompt.lower())
                self.assertIn("no text", prompt.lower())
                self.assertIn("9:16", prompt)

                self.assertIn(sc["motion"], storyboards.VALID_MOTIONS)
                self.assertIn(sc["transition"], storyboards.VALID_TRANSITIONS)

                dialogue = sc["dialogue"]
                self.assertTrue(len(dialogue) >= 1, f"{ep_id}/{sid} must have dialogue")
                for line in dialogue:
                    self.assertIn(
                        line["speaker"],
                        self.valid_speaker_ids,
                        f"Unknown speaker '{line['speaker']}' in {ep_id}/{sid}",
                    )
                    self.assertTrue(
                        isinstance(line["text"], str) and len(line["text"].strip()) >= 5,
                        f"Empty/too-short dialogue text in {ep_id}/{sid}",
                    )

        with self.assertRaises(KeyError):
            storyboards.get_storyboard("ep-999")

    def test_ep002_matches_canonical_chapter2_and_has_zero_iphone_draft(self) -> None:
        ep2 = storyboards.get_storyboard("ep-002")
        combined_text = " ".join(
            [
                ep2["title"],
                ep2["hook"],
                ep2["cliffhanger"],
                *(sc["title"] for sc in ep2["scenes"]),
                *(sc["prompt"] for sc in ep2["scenes"]),
                *(line["text"] for sc in ep2["scenes"] for line in sc["dialogue"]),
            ]
        ).lower()

        # Canonical Chapter 2 elements: market stall destroyed, 300 000 FCFA, Koffi's villa, automatic lock
        self.assertIn("marché", combined_text)
        self.assertIn("étal", combined_text)
        self.assertTrue(
            "300 000" in combined_text or "trois cent mille" in combined_text,
            "ep-002 must reference the 300 000 FCFA market debt from Chapter 2",
        )
        self.assertIn("koffi", combined_text)
        self.assertTrue(
            "villa" in combined_text or "résidence" in combined_text,
            "ep-002 must include Koffi's luxury villa from Chapter 2",
        )
        self.assertIn("verrou", combined_text)

        # Must NEVER contain legacy non-canonical iPhone draft artifacts
        for forbidden in ("iphone", "15 pro", "tablette"):
            self.assertNotIn(
                forbidden,
                combined_text,
                f"Legacy draft term '{forbidden}' must not appear in canonical ep-002",
            )

    def test_characters_bible_uses_only_13_verified_free_french_edge_tts_voices(self) -> None:
        raw_text = json.dumps(self.bible)
        for bad_voice in FORBIDDEN_PAID_VOICES:
            self.assertNotIn(bad_voice, raw_text, f"Invalid/paid voice {bad_voice} found in bible/characters.json")

        declared_free = set(self.bible.get("verified_free_edge_tts_french_voices", []))
        self.assertEqual(len(declared_free), 13)
        self.assertEqual(declared_free, EXPECTED_13_FREE_VOICES)
        self.assertEqual(set(voice_engine.VERIFIED_FRENCH_VOICES), EXPECTED_13_FREE_VOICES)

        self.assertGreaterEqual(len(self.bible["characters"]), 13)
        for ch in self.bible["characters"]:
            vp = ch["voice_profile"]
            self.assertEqual(vp["engine"], "edge-tts")
            self.assertIn(
                vp["voice_id"],
                EXPECTED_13_FREE_VOICES,
                f"Character {ch['id']} uses unverified voice {vp['voice_id']}",
            )
            self.assertNotIn(vp["voice_id"], FORBIDDEN_PAID_VOICES)


class TestVoiceEngineAndAssSubtitles(unittest.TestCase):
    def test_clean_text_for_ass_strips_emojis_and_braces_while_preserving_french(self) -> None:
        dirty = "🔥 {\\c&H00FF00&}Amina prie à Yopougon — « Psaume 91 » ! 🙏✨  \n  C'est l'heure."
        cleaned = voice_engine.clean_text_for_ass(dirty)
        self.assertNotIn("{", cleaned)
        self.assertNotIn("}", cleaned)
        self.assertNotIn("🔥", cleaned)
        self.assertNotIn("🙏", cleaned)
        self.assertNotIn("✨", cleaned)
        self.assertIn("Amina prie à Yopougon — « Psaume 91 » !", cleaned)
        self.assertIn("C'est l'heure.", cleaned)
        self.assertNotIn("  ", cleaned)

    def test_escape_ass_path_for_ffmpeg_escapes_colons_quotes_and_slashes(self) -> None:
        escaped = voice_engine.escape_ass_path_for_ffmpeg("/tmp/amina's:dir/sub:captions.ass")
        self.assertIn("\\:", escaped)
        self.assertIn("\\'", escaped)
        self.assertNotIn("\\/", escaped)
        self.assertTrue(escaped.endswith("sub\\:captions.ass"))

    def test_ass_safe_zone_gold_highlight_and_untouched_episode_srt(self) -> None:
        # Hash all existing episodes/ep-*/subtitles.srt before generation
        srt_hashes_before = {}
        for i in range(1, 12):
            p = os.path.join(REPO_ROOT, "episodes", f"ep-{i:03d}", "subtitles.srt")
            with open(p, "rb") as fh:
                srt_hashes_before[p] = hashlib.sha256(fh.read()).hexdigest()

        sb = storyboards.get_storyboard("ep-001")
        profiles = voice_engine.load_character_profiles()
        timed_lines = [
            {
                "scene_id": "s01",
                "speaker": "narrator",
                "text": "À Yopougon, quand la nuit tombe, deux prédateurs fixent son prix.",
                "start": 0.5,
                "end": 4.2,
                "duration": 3.7,
                "words": voice_engine.compute_proportional_word_timings(
                    "À Yopougon, quand la nuit tombe, deux prédateurs fixent son prix.", 3.7
                ),
            },
            {
                "scene_id": "s02",
                "speaker": "char_amina",
                "text": "Seigneur, je ne céderai jamais devant l'ennemi ! 🔥 {test}",
                "start": 4.6,
                "end": 8.0,
                "duration": 3.4,
                "words": voice_engine.compute_proportional_word_timings(
                    "Seigneur, je ne céderai jamais devant l'ennemi ! 🔥 {test}", 3.4
                ),
            },
        ]

        with tempfile.TemporaryDirectory(prefix="amina_test_ass_") as tmpdir:
            ass_path = os.path.join(tmpdir, "captions.ass")
            srt_path = os.path.join(tmpdir, "captions.srt")
            voice_engine.generate_ass_and_srt(sb, timed_lines, 12.0, profiles, ass_path, srt_path)

            with open(ass_path, "r", encoding="utf-8") as fh:
                ass_content = fh.read()

            # PlayRes 1080x1920 Safe-Zone checks
            self.assertIn("PlayResX: 1080", ass_content)
            self.assertIn("PlayResY: 1920", ass_content)
            # TikTokSub style enforces MarginL=60, MarginR=140, MarginV=440
            self.assertRegex(ass_content, r"Style:\s*TikTokSub,DejaVu Sans,54,.*,60,140,440,1")
            # Active-word Abidjan Gold highlight (#D4AF37 -> BGR &H0037AFD4&)
            self.assertIn("{\\c&H0037AFD4&}", ass_content)
            self.assertIn("+225 07 00 88 95 14", ass_content)
            # Emojis and raw user braces stripped
            self.assertNotIn("🔥", ass_content)
            self.assertNotIn("{test}", ass_content)
            self.assertIn("(test)", ass_content)

            # Matching SRT written inside tmpdir
            self.assertTrue(os.path.exists(srt_path))
            with open(srt_path, "r", encoding="utf-8") as fh:
                srt_content = fh.read()
            self.assertIn("-->", srt_content)
            self.assertIn("[AMINA]", srt_content)

        # Verify zero modifications to repo episodes/ep-*/subtitles.srt
        for p, expected_hash in srt_hashes_before.items():
            with open(p, "rb") as fh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), expected_hash, f"{p} was unexpectedly modified")

        # Also verify voice_engine.py source never targets subtitles.srt
        with open(os.path.join(REPO_ROOT, "scripts", "voice_engine.py"), "r", encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn('"subtitles.srt"', src)
        self.assertNotIn("'subtitles.srt'", src)

    def test_resolve_verified_voice_falls_back_cleanly(self) -> None:
        resolved = voice_engine._resolve_verified_voice(
            "char_koffi",
            "fr-FR-AlainNeural",
            {"fr-FR-HenriNeural", "fr-FR-DeniseNeural"},
        )
        self.assertEqual(resolved, "fr-FR-HenriNeural")


class TestImageGenerator(unittest.TestCase):
    def test_free_endpoints_and_zero_paid_pollinations_domain(self) -> None:
        self.assertEqual(image_generator.POLLINATIONS_BASE, "https://image.pollinations.ai/prompt")
        self.assertEqual(image_generator.AIHORDE_BASE, "https://aihorde.net/api/v2")
        self.assertEqual(image_generator.AIHORDE_ANON_KEY, "0000000000")

        src_path = os.path.join(REPO_ROOT, "scripts", "image_generator.py")
        with open(src_path, "r", encoding="utf-8") as fh:
            code_lines = [
                ln for ln in fh.readlines() if not ln.strip().startswith("#") and "NEVER uses gen.pollinations.ai" not in ln
            ]
        self.assertNotIn("gen.pollinations.ai", "".join(code_lines))

    def test_pil_fallback_produces_valid_non_blank_9x16_portrait(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amina_test_img_") as tmpdir:
            out_img = os.path.join(tmpdir, "s01.jpg")
            image_generator.render_pil_fallback(
                output_path=out_img,
                episode_id="ep-001",
                scene_id="s01",
                scene_index=0,
                mood="twilight_tension",
            )
            self.assertTrue(os.path.exists(out_img))
            ok, reason = image_generator.validate_image_file(out_img)
            self.assertTrue(ok, f"PIL fallback failed validation: {reason}")

            with Image.open(out_img) as im:
                w, h = im.size
                self.assertEqual((w, h), (576, 1024))
                self.assertAlmostEqual(w / h, 9 / 16, places=2)

    def test_validate_image_bytes_rejects_blank_and_landscape_adversarial_inputs(self) -> None:
        # Solid black 576x1024 image -> must fail low variance check
        buf_blank = io.BytesIO()
        Image.new("RGB", (576, 1024), (10, 10, 10)).save(buf_blank, format="JPEG", quality=95)
        ok_blank, _reason_blank, _ = image_generator.validate_image_bytes(buf_blank.getvalue())
        self.assertFalse(ok_blank, "Blank/solid image must be rejected")

        # Landscape 1024x576 image -> must fail portrait check
        buf_land = io.BytesIO()
        img_land = Image.new("RGB", (1024, 576), (20, 40, 80))
        for x in range(0, 1024, 16):
            for y in range(0, 576, 16):
                img_land.putpixel((x, y), (255, 200, 50))
        img_land.save(buf_land, format="JPEG", quality=95)
        ok_land, _reason_land, _ = image_generator.validate_image_bytes(buf_land.getvalue())
        self.assertFalse(ok_land, "Landscape image must be rejected")

        # Corrupt bytes -> must fail
        ok_corrupt, _, _ = image_generator.validate_image_bytes(b"not-a-valid-jpeg" * 400)
        self.assertFalse(ok_corrupt, "Corrupt image bytes must be rejected")


class TestAfrogospelBgm(unittest.TestCase):
    def test_short_duration_synthesis_produces_valid_non_silent_stereo_mp3(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amina_test_bgm_") as tmpdir:
            out_mp3 = os.path.join(tmpdir, "test_bgm.mp3")
            afrogospel_bgm.generate_afrogospel_bgm(
                output_path=out_mp3,
                mood="sanctuary_prayer",
                bpm=92,
                duration=10.0,
            )
            self.assertTrue(os.path.exists(out_mp3))
            self.assertGreater(os.path.getsize(out_mp3), 100_000)

            probe = _ffprobe_json(out_mp3)
            a_stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
            self.assertEqual(a_stream["codec_name"], "mp3")
            self.assertEqual(int(a_stream["channels"]), 2)
            self.assertEqual(int(a_stream["sample_rate"]), 44100)
            self.assertGreaterEqual(float(probe["format"]["duration"]), 9.5)

            mean_db = _volumedetect_mean_db(out_mp3)
            self.assertGreater(mean_db, -30.0, f"Synthesized BGM too quiet ({mean_db} dB)")

    def test_committed_ep001_bgm_is_real_stereo_music_not_mono_pink_noise(self) -> None:
        bgm_path = os.path.join(REPO_ROOT, "episodes", "ep-001", "audio", "bgm_gospel.mp3")
        self.assertTrue(os.path.exists(bgm_path), f"Missing committed BGM: {bgm_path}")

        probe = _ffprobe_json(bgm_path)
        a_stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
        self.assertEqual(a_stream["codec_name"], "mp3")
        self.assertEqual(int(a_stream["channels"]), 2, "Committed bgm_gospel.mp3 must be stereo (2ch), not mono")
        self.assertEqual(int(a_stream["sample_rate"]), 44100)
        self.assertGreaterEqual(float(probe["format"]["duration"]), 60.0)

        mean_db = _volumedetect_mean_db(bgm_path)
        self.assertGreater(
            mean_db,
            -30.0,
            f"Committed bgm_gospel.mp3 mean_volume={mean_db} dB (looks like old -38 dB pink noise)",
        )


class TestPublishManifest(unittest.TestCase):
    def test_manifest_schema_and_merge_existing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amina_test_manifest_") as tmpdir:
            in_dir_1 = os.path.join(tmpdir, "run1", "cinema-ep-001")
            os.makedirs(in_dir_1, exist_ok=True)
            with open(os.path.join(in_dir_1, "ep-001_meta.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "id": "ep-001",
                        "duration": 72.345,
                        "sizeBytes": 12345678,
                        "resolution": "1080x1920",
                        "hasBurnedSubtitles": True,
                        "providers": {"pollinations": 5, "aihorde": 4, "fallback": 0},
                        "sha256": "abc123",
                    },
                    fh,
                )

            manifest_path = os.path.join(tmpdir, "videos-manifest.json")
            m1 = publish_manifest.build_manifest(input_dir=os.path.join(tmpdir, "run1"))
            self.assertEqual(m1["releaseTag"], "episodes-v1")
            self.assertEqual(
                m1["releaseUrl"],
                "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/tag/episodes-v1",
            )
            self.assertRegex(m1["generatedAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
            self.assertEqual(list(m1["episodes"].keys()), ["ep-001"])

            ep1 = m1["episodes"]["ep-001"]
            self.assertEqual(
                ep1["videoUrl"],
                "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1/ep-001.mp4",
            )
            self.assertEqual(ep1["downloadUrl"], ep1["videoUrl"])
            self.assertEqual(
                ep1["posterUrl"],
                "https://github.com/digrekarlito11-eng/gospel-microdrama-studio/releases/download/episodes-v1/ep-001_poster.jpg",
            )
            self.assertEqual(ep1["duration"], 72.34)
            self.assertEqual(ep1["sizeBytes"], 12345678)
            self.assertEqual(ep1["resolution"], "1080x1920")
            self.assertTrue(ep1["hasBurnedSubtitles"])
            self.assertEqual(ep1["providers"], {"pollinations": 5, "aihorde": 4, "fallback": 0})

            with open(manifest_path, "w", encoding="utf-8") as fh:
                json.dump(m1, fh)

            # Second run renders only ep-004 and merges with existing manifest via CLI
            in_dir_2 = os.path.join(tmpdir, "run2", "cinema-ep-004")
            os.makedirs(in_dir_2, exist_ok=True)
            with open(os.path.join(in_dir_2, "ep-004_meta.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "id": "ep-004",
                        "duration": 64.5,
                        "sizeBytes": 11000000,
                        "resolution": "1080x1920",
                        "hasBurnedSubtitles": True,
                        "providers": {"pollinations": 4, "aihorde": 5, "fallback": 0},
                    },
                    fh,
                )

            subprocess.run(
                [
                    sys.executable,
                    os.path.join(REPO_ROOT, "scripts", "publish_manifest.py"),
                    "--input-dir",
                    os.path.join(tmpdir, "run2"),
                    "--output",
                    manifest_path,
                    "--merge-existing",
                    manifest_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with open(manifest_path, "r", encoding="utf-8") as fh:
                merged = json.load(fh)

            self.assertEqual(list(merged["episodes"].keys()), ["ep-001", "ep-004"])
            self.assertEqual(merged["episodes"]["ep-001"]["sizeBytes"], 12345678)
            self.assertEqual(merged["episodes"]["ep-004"]["duration"], 64.5)


class TestVerifyEpisodeAntiCheat(unittest.TestCase):
    @staticmethod
    def _create_valid_test_mp4(mp4_path: str) -> None:
        """Synthesize a fast 4s 720x1280 H.264/yuv420p + AAC audible moving-pattern MP4 via ffmpeg."""
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=720x1280:rate=24:duration=4",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=44100:duration=4",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "ultrafast",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-ac",
                "2",
                mp4_path,
            ],
            check=True,
        )

    def test_strict_production_rejects_offline_tts_low_ai_ratio_and_missing_meta(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amina_test_qa_") as tmpdir:
            mp4_path = os.path.join(tmpdir, "ep-001.mp4")
            self._create_valid_test_mp4(mp4_path)

            # 1. Valid strict production metadata -> PASS
            good_meta = os.path.join(tmpdir, "good_meta.json")
            with open(good_meta, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "id": "ep-001",
                        "tts_mode": "edge_tts",
                        "providers": {"pollinations": 4, "aihorde": 4, "fallback": 1},
                    },
                    fh,
                )
            passed_ok, report_ok = verify_episode.verify_episode(
                mp4_path=mp4_path,
                meta_path=good_meta,
                strict_production=True,
                min_duration=3.0,
                min_size_kb=20,
            )
            self.assertTrue(passed_ok, f"Expected valid production MP4 to pass, got errors: {report_ok['errors']}")

            # 2. tts_mode != 'edge_tts' -> MUST FAIL
            bad_tts_meta = os.path.join(tmpdir, "bad_tts_meta.json")
            with open(bad_tts_meta, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "id": "ep-001",
                        "tts_mode": "offline_test",
                        "providers": {"pollinations": 5, "aihorde": 4, "fallback": 0},
                    },
                    fh,
                )
            passed_tts, report_tts = verify_episode.verify_episode(
                mp4_path=mp4_path,
                meta_path=bad_tts_meta,
                strict_production=True,
                min_duration=3.0,
                min_size_kb=20,
            )
            self.assertFalse(passed_tts)
            self.assertTrue(any("tts_mode" in err for err in report_tts["errors"]))

            # 3. < 50% real AI scenes -> MUST FAIL
            low_ai_meta = os.path.join(tmpdir, "low_ai_meta.json")
            with open(low_ai_meta, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "id": "ep-001",
                        "tts_mode": "edge_tts",
                        "providers": {"pollinations": 2, "aihorde": 1, "fallback": 6},
                    },
                    fh,
                )
            passed_ai, report_ai = verify_episode.verify_episode(
                mp4_path=mp4_path,
                meta_path=low_ai_meta,
                strict_production=True,
                min_duration=3.0,
                min_size_kb=20,
            )
            self.assertFalse(passed_ai)
            self.assertTrue(any("50%" in err for err in report_ai["errors"]))

            # 4. Missing --meta in strict mode -> MUST FAIL
            passed_nometa, report_nometa = verify_episode.verify_episode(
                mp4_path=mp4_path,
                meta_path=None,
                strict_production=True,
                min_duration=3.0,
                min_size_kb=20,
            )
            self.assertFalse(passed_nometa)
            self.assertTrue(any("--meta" in err for err in report_nometa["errors"]))


class TestGitHubActionsWorkflow(unittest.TestCase):
    def test_produce_season_cinema_workflow_contract_and_zero_paid_secrets(self) -> None:
        wf_path = os.path.join(REPO_ROOT, ".github", "workflows", "produce-season-cinema.yml")
        self.assertTrue(os.path.exists(wf_path))
        with open(wf_path, "r", encoding="utf-8") as fh:
            raw_yaml = fh.read()

        doc = yaml.safe_load(raw_yaml)
        self.assertIsInstance(doc, dict)

        # Permissions
        self.assertEqual(doc.get("permissions", {}).get("contents"), "write")

        # Job structure: plan -> render (11-way matrix) -> publish
        jobs = doc.get("jobs", {})
        self.assertIn("plan", jobs)
        self.assertIn("render", jobs)
        self.assertIn("publish", jobs)

        render_job = jobs["render"]
        self.assertEqual(render_job.get("needs"), "plan")
        strategy = render_job.get("strategy", {})
        self.assertEqual(strategy.get("max-parallel"), 11)
        self.assertIs(strategy.get("fail-fast"), False)
        self.assertIn("fromJson(needs.plan.outputs.episodes)", str(strategy.get("matrix", {}).get("episode", "")))

        # Verify plan references get_all_episode_ids() which yields all 11 episodes ep-001..ep-011
        plan_text = json.dumps(jobs["plan"])
        self.assertIn("get_all_episode_ids", plan_text)
        self.assertEqual(storyboards.get_all_episode_ids(), [f"ep-{i:03d}" for i in range(1, 12)])

        # Verify render step requirements
        render_text = json.dumps(render_job)
        self.assertIn("edge-tts>=7.3.1", render_text)
        self.assertIn("scripts/render_episode.py", render_text)
        self.assertIn("--strict-production", render_text)

        # Verify publish step requirements
        publish_job = jobs["publish"]
        self.assertEqual(publish_job.get("needs"), "render")
        self.assertEqual(publish_job.get("permissions", {}).get("contents"), "write")
        publish_text = json.dumps(publish_job)
        self.assertIn("gh release", publish_text)
        self.assertIn("scripts/publish_manifest.py", publish_text)
        self.assertIn("--merge-existing", publish_text)
        self.assertIn("[skip ci]", publish_text)
        self.assertIn("--strict-production", publish_text)

        # Strict 100% Free Option 3 Guard: ONLY secrets.GITHUB_TOKEN allowed, ZERO paid API keys!
        secret_refs = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", raw_yaml))
        self.assertEqual(
            secret_refs,
            {"GITHUB_TOKEN"},
            f"Option 3 workflow must ONLY reference secrets.GITHUB_TOKEN, found: {secret_refs}",
        )

        forbidden_paid_tokens = [
            "OPENAI_API_KEY",
            "ELEVENLABS",
            "AZURE_SPEECH",
            "KLING_API",
            "RUNWAY_API",
            "LUMA_API",
            "REPLICATE_API",
            "FAL_KEY",
            "PIKA_API",
            "SUNO_API",
            "POLLINATIONS_API_KEY",
            "gen.pollinations.ai",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
        ]
        upper_yaml = raw_yaml.upper()
        for token in forbidden_paid_tokens:
            self.assertNotIn(
                token.upper(),
                upper_yaml,
                f"Paid API reference '{token}' must NOT appear in Option 3 workflow",
            )


if __name__ == "__main__":
    unittest.main()
