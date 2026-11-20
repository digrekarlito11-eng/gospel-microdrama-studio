#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Wrapper rétrocompatible Edge-TTS (generate_tts_edge.py)
Délègue entièrement au moteur multi-personnages scripts/voice_engine.py.
"""

import argparse
import asyncio
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
if STUDIO_ROOT not in sys.path:
    sys.path.insert(0, STUDIO_ROOT)

from scripts.storyboards import get_storyboard
from scripts.voice_engine import synthesize_episode_voiceover


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Thin wrapper delegating to scripts/voice_engine.py."
    )
    parser.add_argument(
        "episode_id",
        nargs="?",
        default="ep-001",
        help="Episode ID (ep-001..ep-011)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Target output directory (default: episodes/<ep>/audio)",
    )
    parser.add_argument(
        "--offline-test-audio",
        action="store_true",
        help="LOCAL DRY-RUN ONLY: offline speech-cadence audio",
    )
    args = parser.parse_args()

    ep_id = args.episode_id.strip().lower()
    out_dir = args.output_dir or os.path.join(STUDIO_ROOT, "episodes", ep_id, "audio")
    sb = get_storyboard(ep_id)
    result = asyncio.run(
        synthesize_episode_voiceover(
            storyboard=sb,
            work_dir=out_dir,
            offline_test_audio=args.offline_test_audio,
        )
    )
    print(json.dumps({"episode_id": ep_id, "tts_mode": result["tts_mode"], "duration": result["total_duration"]}))


if __name__ == "__main__":
    main()
