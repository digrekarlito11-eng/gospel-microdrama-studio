#!/usr/bin/env python3
"""
Gospel Microdrama Studio — Générateur d'Images IA 100% Gratuit Bi-Fournisseur (image_generator.py)
Zéro clé API payante. Entrelace intelligemment deux moteurs IA gratuits :
  1. Pollinations Legacy Free (https://image.pollinations.ai/prompt/... — 576x1024, 1 req / 45s par IP)
  2. AI Horde Anonyme (https://aihorde.net/api/v2/generate/async, apikey 0000000000 — 384x640, 0 filigrane)
  3. Repli ultime PIL cinématographique « Abidjan Twilight Noir » dérivé de assets/cover.jpg
     (uniquement si les deux moteurs IA échouent après retries, ou via --provider fallback).
"""

import argparse
import base64
import hashlib
import io
import json
import math
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_COVER_PATH = os.path.join(STUDIO_ROOT, "assets", "cover.jpg")

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
POLLINATIONS_COOLDOWN_S = 46.5

AIHORDE_BASE = "https://aihorde.net/api/v2"
AIHORDE_ANON_KEY = "0000000000"
AIHORDE_CLIENT_AGENT = "AminaMicrodramaStudio:1.0:gospel-microdrama-studio"
AIHORDE_MODELS = [
    "ICBINP - I Can't Believe It's Not Photography",
    "Deliberate",
    "Dreamshaper",
    "AbsoluteReality",
    "Flux.1-Schnell fp8 (Compact)",
]

NEGATIVE_PROMPT = (
    "text, watermark, signature, logo, caption, subtitles, blurry, distorted face, "
    "extra limbs, deformed hands, cartoon, anime, lowres, ugly, monochrome gray"
)

# Per-mood RGB tint pairs (shadow_tint, highlight_tint) for cinematic PIL fallback
MOOD_PALETTES: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
    "twilight_tension": ((10, 18, 44), (230, 145, 45)),
    "sanctuary_prayer": ((12, 22, 52), (242, 196, 86)),
    "spiritual_warfare": ((22, 10, 32), (235, 110, 35)),
    "victory_dawn": ((18, 30, 62), (255, 206, 92)),
}


def _http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: float = 45.0,
) -> Tuple[int, Dict[str, str], bytes]:
    """Minimal zero-dependency HTTP helper returning (status_code, lower_headers, body_bytes)."""
    req_headers = {
        "User-Agent": "AminaMicrodramaStudio/1.0 (+https://github.com/digrekarlito11-eng/gospel-microdrama-studio)"
    }
    if headers:
        req_headers.update(headers)

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            return status, resp_headers, resp.read()
    except urllib.error.HTTPError as exc:
        resp_headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        body = b""
        try:
            body = exc.read()
        except Exception:
            pass
        return exc.code, resp_headers, body


def validate_image_bytes(
    raw_bytes: bytes,
    min_width: int = 300,
    min_height: int = 500,
    min_stddev: float = 12.0,
) -> Tuple[bool, str, Optional[Image.Image]]:
    """
    Validate downloaded AI image bytes with Pillow:
      - Non-corrupt image decodable to RGB
      - Portrait dimensions >= min_width x min_height
      - Visual complexity (global & center crop stddev > min_stddev) so blank/solid error banners fail
    """
    if not raw_bytes or len(raw_bytes) < 4096:
        return False, f"Image too small ({len(raw_bytes) if raw_bytes else 0} bytes)", None

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.load()
        img = img.convert("RGB")
    except Exception as exc:
        return False, f"Invalid/corrupt image: {exc}", None

    w, h = img.size
    if w < min_width or h < min_height:
        return False, f"Dimensions too small: {w}x{h} (min {min_width}x{min_height})", None
    if h <= w:
        return False, f"Not portrait aspect: {w}x{h}", None

    gray = img.convert("L")
    global_std = ImageStat.Stat(gray).stddev[0]
    if global_std <= min_stddev:
        return False, f"Low visual variance (stddev={global_std:.2f} <= {min_stddev})", None

    # Center 60% crop check catches white/black error screens with tiny border text
    cx0, cy0 = int(w * 0.2), int(h * 0.2)
    cx1, cy1 = int(w * 0.8), int(h * 0.8)
    center_std = ImageStat.Stat(gray.crop((cx0, cy0, cx1, cy1))).stddev[0]
    if center_std <= max(10.0, min_stddev * 0.8):
        return False, f"Low center variance (center_stddev={center_std:.2f})", None

    return True, "ok", img


def validate_image_file(
    filepath: str,
    min_width: int = 300,
    min_height: int = 500,
    min_stddev: float = 12.0,
) -> Tuple[bool, str]:
    if not os.path.exists(filepath):
        return False, "File does not exist"
    with open(filepath, "rb") as fh:
        ok, reason, _ = validate_image_bytes(
            fh.read(),
            min_width=min_width,
            min_height=min_height,
            min_stddev=min_stddev,
        )
    return ok, reason


def deterministic_seed(episode_id: str, scene_id: str) -> int:
    digest = hashlib.sha256(f"{episode_id}:{scene_id}:amina-opt3".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 2_000_000_000


def render_pil_fallback(
    output_path: str,
    episode_id: str,
    scene_id: str,
    scene_index: int,
    mood: str = "twilight_tension",
    cover_path: str = DEFAULT_COVER_PATH,
    size: Tuple[int, int] = (576, 1024),
) -> str:
    """
    High-craft Abidjan Twilight Noir cinematic composite derived from assets/cover.jpg.
    Used ONLY as last-resort fallback if both free AI providers fail, or in --provider fallback dry-runs.
    Produces distinct framing, warm amber/gold + midnight blue lighting, twilight glow, bokeh, and vignette.
    """
    w, h = size
    seed = deterministic_seed(episode_id, scene_id)
    rng = random.Random(seed)
    shadow_rgb, highlight_rgb = MOOD_PALETTES.get(mood, MOOD_PALETTES["twilight_tension"])

    if os.path.exists(cover_path):
        base = Image.open(cover_path).convert("RGB")
        # Trim top 18% and bottom 22% book-cover typography zones so fallback artwork is pure imagery (zero text)
        raw_w, raw_h = base.size
        base = base.crop((0, int(raw_h * 0.18), raw_w, int(raw_h * 0.78)))
        # Vary crop region, gentle zoom, and optional horizontal mirror per scene so consecutive shots differ clearly
        bw, bh = base.size
        crop_scale = rng.uniform(0.68, 0.94)
        cw = max(120, int(bw * crop_scale))
        ch = max(200, int(bh * crop_scale))
        # Ensure portrait proportion before final fit
        max_x = max(0, bw - cw)
        max_y = max(0, bh - ch)
        x0 = rng.randint(0, max_x) if max_x > 0 else 0
        y0 = rng.randint(0, max_y) if max_y > 0 else 0
        cropped = base.crop((x0, y0, x0 + cw, y0 + ch))
        if scene_index % 2 == 1:
            cropped = ImageOps.mirror(cropped)
        canvas = ImageOps.fit(cropped, (w, h), method=Image.Resampling.LANCZOS)
        # Subtle atmospheric depth blur + richness
        if scene_index % 3 == 2:
            canvas = canvas.filter(ImageFilter.GaussianBlur(radius=1.2))
    else:
        # Procedural twilight sky + architectural skyline silhouette if cover missing
        canvas = Image.new("RGB", (w, h), shadow_rgb)
        draw_bg = ImageDraw.Draw(canvas)
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(shadow_rgb[0] * (1 - t) + highlight_rgb[0] * t * 0.65)
            g = int(shadow_rgb[1] * (1 - t) + highlight_rgb[1] * t * 0.55)
            b = int(shadow_rgb[2] * (1 - t) + highlight_rgb[2] * t * 0.40)
            draw_bg.line([(0, y), (w, y)], fill=(r, g, b))
        # Add skyline blocks for genuine structure & contrast
        for i in range(14):
            bx0 = int(i * (w / 14))
            bx1 = bx0 + rng.randint(32, 68)
            by0 = rng.randint(int(h * 0.45), int(h * 0.78))
            draw_bg.rectangle([bx0, by0, bx1, h], fill=(8, 12, 24))
            for wy in range(by0 + 18, h - 20, 28):
                for wx in range(bx0 + 8, bx1 - 10, 18):
                    if rng.random() > 0.45:
                        draw_bg.rectangle([wx, wy, wx + 8, wy + 12], fill=highlight_rgb)

    # Blend mood-graded duotone layer for Abidjan Twilight Noir cohesion
    gray = canvas.convert("L")
    graded = ImageOps.colorize(gray, black=shadow_rgb, white=highlight_rgb)
    canvas = Image.blend(canvas, graded, alpha=rng.uniform(0.32, 0.52))
    canvas = ImageEnhance.Contrast(canvas).enhance(rng.uniform(1.12, 1.28))
    canvas = ImageEnhance.Color(canvas).enhance(rng.uniform(1.05, 1.25))

    # Add atmospheric twilight light beam + warm bokeh orbs
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    glow_cx = int(w * rng.uniform(0.2, 0.8))
    glow_cy = int(h * rng.uniform(0.18, 0.52))
    for radius in range(280, 30, -35):
        alpha = int(14 * (1.0 - radius / 300.0))
        draw.ellipse(
            [glow_cx - radius, glow_cy - radius, glow_cx + radius, glow_cy + radius],
            fill=(highlight_rgb[0], highlight_rgb[1], highlight_rgb[2], max(2, alpha)),
        )

    # Subtle city bokeh lights
    for _ in range(18):
        bx = rng.randint(20, w - 20)
        by = rng.randint(int(h * 0.12), int(h * 0.86))
        br = rng.randint(8, 34)
        ba = rng.randint(18, 52)
        col = highlight_rgb if rng.random() > 0.35 else (255, 224, 150)
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(col[0], col[1], col[2], ba))

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=9))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")

    # Dark cinematic vignette around edges & safe-zone readability gradient at top/bottom
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vig)
    for y in range(0, int(h * 0.22)):
        a = int(125 * (1.0 - y / (h * 0.22)))
        vdraw.line([(0, y), (w, y)], fill=(5, 8, 18, a))
    for y in range(int(h * 0.68), h):
        a = int(170 * ((y - h * 0.68) / (h * 0.32)))
        vdraw.line([(0, y), (w, y)], fill=(5, 8, 18, a))

    canvas = Image.alpha_composite(canvas.convert("RGBA"), vig).convert("RGB")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    canvas.save(output_path, format="JPEG", quality=92)
    return output_path


class SceneImageGenerator:
    """Dual-provider 100% free AI scene generator with smart Pollinations + AI Horde interleaving."""

    def __init__(
        self,
        provider: str = "auto",
        cover_path: str = DEFAULT_COVER_PATH,
        pollinations_cooldown: float = POLLINATIONS_COOLDOWN_S,
        aihorde_timeout: float = 150.0,
    ) -> None:
        self.provider = provider
        self.cover_path = cover_path
        self.pollinations_cooldown = pollinations_cooldown
        self.aihorde_timeout = aihorde_timeout
        self._next_pollinations_ts: float = 0.0

    def _pollinations_wait_needed(self) -> float:
        return max(0.0, self._next_pollinations_ts - time.monotonic())

    def fetch_pollinations(
        self,
        prompt: str,
        seed: int,
        output_path: str,
        allow_wait: bool = True,
        max_retries: int = 2,
    ) -> Tuple[bool, str]:
        """
        Fetch a 576x1024 vertical AI image from legacy free Pollinations endpoint.
        Strictly respects HTTP 402/429 + Retry-After (45s/IP bucket) and NEVER uses gen.pollinations.ai.
        """
        encoded = urllib.parse.quote(prompt, safe="")
        url = (
            f"{POLLINATIONS_BASE}/{encoded}"
            f"?width=576&height=1024&model=flux&nologo=true&seed={seed}"
        )

        for attempt in range(1, max_retries + 1):
            wait_s = self._pollinations_wait_needed()
            if wait_s > 0:
                if not allow_wait:
                    return False, f"Pollinations cooldown active ({wait_s:.1f}s remaining)"
                print(f"    [Pollinations] Waiting {wait_s:.1f}s for free IP bucket...")
                time.sleep(wait_s)

            try:
                status, headers, body = _http_request(url, method="GET", timeout=75.0)
            except Exception as exc:
                self._next_pollinations_ts = time.monotonic() + 8.0
                if attempt < max_retries:
                    time.sleep(3.0 * attempt)
                    continue
                return False, f"Pollinations network error: {exc}"

            if status == 200:
                ok, reason, img = validate_image_bytes(body, min_width=300, min_height=500, min_stddev=12.0)
                self._next_pollinations_ts = time.monotonic() + self.pollinations_cooldown
                if ok and img is not None:
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    img.save(output_path, format="JPEG", quality=93)
                    return True, "ok"
                return False, f"Pollinations image failed validation: {reason}"

            if status in (402, 429):
                retry_hdr = headers.get("retry-after", "")
                try:
                    retry_after = float(retry_hdr)
                except (ValueError, TypeError):
                    retry_after = self.pollinations_cooldown
                retry_after = max(5.0, min(90.0, retry_after + 2.0))
                self._next_pollinations_ts = time.monotonic() + retry_after
                if not allow_wait or attempt >= max_retries:
                    return False, f"Pollinations HTTP {status} (Retry-After={retry_after:.0f}s)"
                print(f"    [Pollinations] HTTP {status}, respecting Retry-After={retry_after:.0f}s...")
                continue

            if status >= 500 and attempt < max_retries:
                time.sleep(4.0 * attempt)
                continue

            return False, f"Pollinations HTTP {status}"

        return False, "Pollinations exhausted retries"

    def fetch_aihorde(
        self,
        prompt: str,
        seed: int,
        output_path: str,
        max_retries: int = 2,
    ) -> Tuple[bool, str]:
        """
        Generate a 384x640 vertical photorealistic AI image via AI Horde anonymous API
        (apikey: 0000000000, zero watermark, 20 steps, nsfw: False, censor_nsfw: True).
        """
        headers = {
            "apikey": AIHORDE_ANON_KEY,
            "Client-Agent": AIHORDE_CLIENT_AGENT,
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": f"{prompt} ### {NEGATIVE_PROMPT}",
            "params": {
                "width": 384,
                "height": 640,
                "steps": 16,
                "cfg_scale": 7.0,
                "sampler_name": "k_euler",
                "n": 1,
                "seed": str(seed),
            },
            "nsfw": False,
            "censor_nsfw": True,
            "trusted_workers": False,
            "slow_workers": True,
            "r2": True,
            "shared": False,
            "models": AIHORDE_MODELS,
        }

        for attempt in range(1, max_retries + 1):
            try:
                status, _, body = _http_request(
                    f"{AIHORDE_BASE}/generate/async",
                    method="POST",
                    headers=headers,
                    json_body=payload,
                    timeout=30.0,
                )
            except Exception as exc:
                if attempt < max_retries:
                    time.sleep(3.0 * attempt)
                    continue
                return False, f"AI Horde submit error: {exc}"

            if status not in (200, 202):
                msg = body.decode("utf-8", errors="ignore")[:180]
                if status in (429, 500, 502, 503) and attempt < max_retries:
                    time.sleep(6.0 * attempt)
                    continue
                return False, f"AI Horde submit HTTP {status}: {msg}"

            try:
                job_id = json.loads(body.decode("utf-8")).get("id")
            except Exception as exc:
                return False, f"AI Horde invalid JSON response: {exc}"

            if not job_id:
                return False, "AI Horde returned empty job id"

            # Poll check endpoint
            deadline = time.monotonic() + self.aihorde_timeout
            done = False
            while time.monotonic() < deadline:
                time.sleep(4.0)
                try:
                    c_status, _, c_body = _http_request(
                        f"{AIHORDE_BASE}/generate/check/{job_id}",
                        method="GET",
                        headers={"Client-Agent": AIHORDE_CLIENT_AGENT},
                        timeout=20.0,
                    )
                except Exception:
                    continue

                if c_status != 200:
                    continue
                try:
                    chk = json.loads(c_body.decode("utf-8"))
                except Exception:
                    continue

                if chk.get("faulted") or not chk.get("is_possible", True):
                    break
                if chk.get("done"):
                    done = True
                    break

            if not done:
                if attempt < max_retries:
                    continue
                return False, f"AI Horde job {job_id} timed out or faulted"

            # Fetch final image status
            try:
                s_status, _, s_body = _http_request(
                    f"{AIHORDE_BASE}/generate/status/{job_id}",
                    method="GET",
                    headers={"Client-Agent": AIHORDE_CLIENT_AGENT},
                    timeout=25.0,
                )
            except Exception as exc:
                if attempt < max_retries:
                    continue
                return False, f"AI Horde status fetch error: {exc}"

            if s_status != 200:
                if attempt < max_retries:
                    continue
                return False, f"AI Horde status HTTP {s_status}"

            try:
                status_json = json.loads(s_body.decode("utf-8"))
                gens = status_json.get("generations") or []
            except Exception as exc:
                return False, f"AI Horde status parse error: {exc}"

            if not gens:
                if attempt < max_retries:
                    continue
                return False, "AI Horde returned no generations"

            gen0 = gens[0]
            if gen0.get("censored"):
                if attempt < max_retries:
                    continue
                return False, "AI Horde output was censored"

            img_ref = gen0.get("img", "")
            raw_bytes: bytes = b""
            if img_ref.startswith("http://") or img_ref.startswith("https://"):
                try:
                    d_status, _, raw_bytes = _http_request(img_ref, method="GET", timeout=40.0)
                    if d_status != 200:
                        raw_bytes = b""
                except Exception:
                    raw_bytes = b""
            elif img_ref:
                try:
                    raw_bytes = base64.b64decode(img_ref)
                except Exception:
                    raw_bytes = b""

            ok, reason, img = validate_image_bytes(raw_bytes, min_width=300, min_height=500, min_stddev=12.0)
            if ok and img is not None:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                img.save(output_path, format="JPEG", quality=93)
                return True, f"ok ({gen0.get('model', 'aihorde')})"

            if attempt < max_retries:
                continue
            return False, f"AI Horde image failed validation: {reason}"

        return False, "AI Horde exhausted retries"

    def generate_scene_image(
        self,
        episode_id: str,
        scene: Dict[str, Any],
        scene_index: int,
        mood: str,
        output_path: str,
    ) -> Tuple[str, str]:
        """
        Generate one vertical scene image and return `(provider_used, detail)`.
        `provider_used` is one of `'pollinations'`, `'aihorde'`, `'fallback'`.
        """
        scene_id = scene["scene_id"]
        prompt = scene["prompt"]
        seed = deterministic_seed(episode_id, scene_id)

        if self.provider == "fallback":
            render_pil_fallback(
                output_path=output_path,
                episode_id=episode_id,
                scene_id=scene_id,
                scene_index=scene_index,
                mood=mood,
                cover_path=self.cover_path,
            )
            return "fallback", "explicit fallback mode"

        if self.provider == "pollinations":
            ok, msg = self.fetch_pollinations(prompt, seed, output_path, allow_wait=True, max_retries=3)
            if ok:
                return "pollinations", msg
            render_pil_fallback(output_path, episode_id, scene_id, scene_index, mood, self.cover_path)
            return "fallback", f"pollinations failed ({msg}); used PIL fallback"

        if self.provider == "aihorde":
            ok, msg = self.fetch_aihorde(prompt, seed, output_path, max_retries=2)
            if ok:
                return "aihorde", msg
            render_pil_fallback(output_path, episode_id, scene_id, scene_index, mood, self.cover_path)
            return "fallback", f"aihorde failed ({msg}); used PIL fallback"

        # Default "auto": Smart Interleaving between Pollinations (576x1024, 1/45s) & AI Horde (384x640, ~10-25s)
        poll_wait = self._pollinations_wait_needed()
        if poll_wait <= 2.0:
            # Pollinations bucket is ready -> use it immediately!
            ok, msg = self.fetch_pollinations(prompt, seed, output_path, allow_wait=True, max_retries=1)
            if ok:
                return "pollinations", msg
            print(f"    [Auto] Pollinations failed on {scene_id} ({msg}) -> failover to AI Horde")
            ok_h, msg_h = self.fetch_aihorde(prompt, seed, output_path, max_retries=2)
            if ok_h:
                return "aihorde", msg_h
        else:
            # Pollinations bucket is refilling -> use AI Horde right away with zero idle time!
            ok_h, msg_h = self.fetch_aihorde(prompt, seed, output_path, max_retries=2)
            if ok_h:
                return "aihorde", msg_h
            print(f"    [Auto] AI Horde failed on {scene_id} ({msg_h}) -> failover to Pollinations")
            ok_p, msg_p = self.fetch_pollinations(prompt, seed, output_path, allow_wait=True, max_retries=2)
            if ok_p:
                return "pollinations", msg_p

        # Both free AI providers failed after retries -> cinematic PIL fallback
        print(f"    [Auto] Both AI providers failed for {scene_id}; rendering Abidjan Twilight Noir PIL composite.")
        render_pil_fallback(output_path, episode_id, scene_id, scene_index, mood, self.cover_path)
        return "fallback", "both AI providers failed; used PIL fallback"

    def generate_episode_scenes(
        self,
        storyboard: Dict[str, Any],
        scenes_dir: str,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Generate all scenes for an episode and return (scene_records, provider_stats)."""
        os.makedirs(scenes_dir, exist_ok=True)
        ep_id = storyboard["episode_id"]
        mood = storyboard.get("mood", "twilight_tension")
        stats = {"pollinations": 0, "aihorde": 0, "fallback": 0}
        records: List[Dict[str, Any]] = []

        for idx, scene in enumerate(storyboard["scenes"]):
            scene_id = scene["scene_id"]
            out_path = os.path.join(scenes_dir, f"{scene_id}.jpg")
            print(f"  [Image {idx + 1}/{len(storyboard['scenes'])}] {scene_id} — {scene['title']}...")
            used, detail = self.generate_scene_image(
                episode_id=ep_id,
                scene=scene,
                scene_index=idx,
                mood=mood,
                output_path=out_path,
            )
            stats[used] = stats.get(used, 0) + 1
            ok, v_msg = validate_image_file(out_path)
            if not ok:
                # Guarantee valid visual file
                render_pil_fallback(out_path, ep_id, scene_id, idx, mood, self.cover_path)
                if used != "fallback":
                    stats[used] = max(0, stats[used] - 1)
                    stats["fallback"] += 1
                    used = "fallback"
                    detail = f"post-check fallback ({v_msg})"
            print(f"    -> provider={used} ({detail})")
            records.append(
                {
                    "scene_id": scene_id,
                    "path": out_path,
                    "provider": used,
                    "detail": detail,
                }
            )

        return records, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate free AI scene images for an episode.")
    parser.add_argument("--episode", default="ep-001", help="Episode ID (ep-001..ep-011)")
    parser.add_argument("--output-dir", required=True, help="Directory to store scene JPGs")
    parser.add_argument(
        "--provider",
        default="auto",
        choices=("auto", "pollinations", "aihorde", "fallback"),
        help="Image provider mode",
    )
    args = parser.parse_args()

    from scripts.storyboards import get_storyboard  # type: ignore

    sb = get_storyboard(args.episode)
    gen = SceneImageGenerator(provider=args.provider)
    records, stats = gen.generate_episode_scenes(sb, args.output_dir)
    print("Provider stats:", json.dumps(stats))
    with open(os.path.join(args.output_dir, "image_providers.json"), "w", encoding="utf-8") as fh:
        json.dump({"episode_id": args.episode, "providers": stats, "scenes": records}, fh, indent=2)


if __name__ == "__main__":
    main()
