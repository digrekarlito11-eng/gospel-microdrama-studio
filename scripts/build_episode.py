#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Wrapper rétrocompatible de rendu (build_episode.py)
Délègue entièrement au moteur Cinéma 2.5D scripts/render_episode.py.
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
if STUDIO_ROOT not in sys.path:
    sys.path.insert(0, STUDIO_ROOT)

from scripts.render_episode import render_episode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Thin wrapper delegating to scripts/render_episode.py."
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
        help="Output directory (default: build_out/<ep>)",
    )
    parser.add_argument(
        "--resolution",
        default="1080p",
        choices=("1080p", "720p"),
        help="Output resolution",
    )
    parser.add_argument(
        "--provider",
        default="auto",
        choices=("auto", "pollinations", "aihorde", "fallback"),
        help="Free AI image provider",
    )
    parser.add_argument(
        "--offline-test-audio",
        action="store_true",
        help="LOCAL DRY-RUN ONLY: offline voice cadence",
    )
    parser.add_argument("--release-tag", default="episodes-v1", help="Release tag")
    args = parser.parse_args()

    ep_id = args.episode_id.strip().lower()
    out_dir = args.output_dir or os.path.join(STUDIO_ROOT, "build_out", ep_id)
    render_episode(
        episode_id=ep_id,
        output_dir=out_dir,
        resolution=args.resolution,
        provider=args.provider,
        offline_test_audio=args.offline_test_audio,
        release_tag=args.release_tag,
    )


if __name__ == "__main__":
    main()
