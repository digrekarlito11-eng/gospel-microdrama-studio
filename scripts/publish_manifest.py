#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Générateur de videos-manifest.json (publish_manifest.py)
Scanne les fichiers ep-*_meta.json produits par la CI, fusionne éventuellement avec un
videos-manifest.json existant (pour les rendus ciblés d'un seul épisode), et écrit le
manifeste racine conforme au contrat PROJECT.md § Option 3 Interface Contracts.
"""

import argparse
import datetime
import glob
import json
import os
from typing import Any, Dict, Optional

DEFAULT_REPO = "digrekarlito11-eng/gospel-microdrama-studio"
DEFAULT_RELEASE_TAG = "episodes-v1"


def build_manifest(
    input_dir: str,
    release_tag: str = DEFAULT_RELEASE_TAG,
    repo: str = DEFAULT_REPO,
    merge_existing_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Scan `input_dir` recursively for `ep-*_meta.json` and construct canonical videos-manifest dict."""
    base_download = f"https://github.com/{repo}/releases/download/{release_tag}"
    release_url = f"https://github.com/{repo}/releases/tag/{release_tag}"

    episodes: Dict[str, Dict[str, Any]] = {}

    if merge_existing_path and os.path.exists(merge_existing_path):
        try:
            with open(merge_existing_path, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
            if isinstance(existing, dict) and isinstance(existing.get("episodes"), dict):
                episodes.update(existing["episodes"])
        except Exception as exc:
            print(f"Warning: could not merge existing manifest '{merge_existing_path}': {exc}")

    pattern = os.path.join(input_dir, "**", "ep-*_meta.json")
    meta_files = sorted(glob.glob(pattern, recursive=True))

    for meta_path in meta_files:
        with open(meta_path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
        ep_id = str(meta.get("id") or meta.get("episode_id") or "").strip().lower()
        if not ep_id:
            continue

        video_filename = meta.get("videoFilename") or f"{ep_id}.mp4"
        poster_filename = meta.get("posterFilename") or f"{ep_id}_poster.jpg"
        video_url = f"{base_download}/{video_filename}"
        poster_url = f"{base_download}/{poster_filename}"

        providers = meta.get("providers") or {"pollinations": 0, "aihorde": 0, "fallback": 0}
        episodes[ep_id] = {
            "id": ep_id,
            "videoUrl": video_url,
            "downloadUrl": video_url,
            "posterUrl": poster_url,
            "duration": round(float(meta.get("duration", 0.0)), 2),
            "sizeBytes": int(meta.get("sizeBytes", 0)),
            "resolution": str(meta.get("resolution", "1080x1920")),
            "hasBurnedSubtitles": bool(meta.get("hasBurnedSubtitles", True)),
            "providers": {
                "pollinations": int(providers.get("pollinations", 0)),
                "aihorde": int(providers.get("aihorde", 0)),
                "fallback": int(providers.get("fallback", 0)),
            },
        }
        if meta.get("sha256"):
            episodes[ep_id]["sha256"] = str(meta["sha256"])

    # Sort episodes canonically (ep-001 .. ep-011)
    sorted_episodes = {k: episodes[k] for k in sorted(episodes.keys())}

    return {
        "releaseTag": release_tag,
        "releaseUrl": release_url,
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "episodes": sorted_episodes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate root videos-manifest.json from verified episode metadata JSONs."
    )
    parser.add_argument("--input-dir", required=True, help="Directory containing ep-*_meta.json files")
    parser.add_argument("--output", default="videos-manifest.json", help="Output manifest JSON path")
    parser.add_argument("--release-tag", default=DEFAULT_RELEASE_TAG, help="GitHub Release tag")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo")
    parser.add_argument(
        "--merge-existing",
        default=None,
        help="Optional path to existing videos-manifest.json to preserve untouched episodes",
    )
    args = parser.parse_args()

    manifest = build_manifest(
        input_dir=args.input_dir,
        release_tag=args.release_tag,
        repo=args.repo,
        merge_existing_path=args.merge_existing,
    )
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(
        f"Published manifest {args.output}: releaseTag={manifest['releaseTag']}, "
        f"episodes={len(manifest['episodes'])} ({', '.join(manifest['episodes'].keys())})"
    )


if __name__ == "__main__":
    main()
