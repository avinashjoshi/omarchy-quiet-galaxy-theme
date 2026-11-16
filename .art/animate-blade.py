"""Animate the cinematic blade: uv run --with numpy --with pillow .art/animate-blade.py."""

from pathlib import Path
import subprocess

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FPS, SECONDS = 30, 8
OUTPUT = ROOT / "extras/backgrounds/19-hero-blade-live.mp4"


def prepare():
    image = Image.open(ROOT / "backgrounds/14-hero-blade.png").convert("RGB")
    # H.264 4:2:0 requires even dimensions; remove only the bottommost row.
    image = image.crop((0, 0, image.width // 2 * 2, image.height // 2 * 2))
    base = np.asarray(image).copy()
    box = (650, 405, 1025, 825)
    left, top, right, bottom = box
    original = base[top:bottom, left:right].astype(np.float32)
    y, x = np.mgrid[top:bottom, left:right].astype(np.float32)
    # Reconstruct the unlit air behind the blade from adjacent dark pixels.
    # Feather only the outer edges, preserving the hilt and the ground.
    blend = np.clip((x - 716) / 240, 0, 1)[..., None]
    air = original[:, 66:67] * (1 - blend) + original[:, 306:307] * blend
    mask = (1 - smoothstep(38, 110, abs(x - 836)))
    mask *= smoothstep(400, 435, y) * (1 - smoothstep(653, 668, y))
    unlit = original * (1 - mask[..., None]) + air * mask[..., None]
    return base, box, original, unlit, x, y


def smoothstep(start, end, value):
    value = np.clip((value - start) / (end - start), 0, 1)
    return value * value * (3 - 2 * value)


def frame_at(t, prepared):
    base, (left, top, right, bottom), original, unlit, x, y = prepared
    t %= SECONDS
    phase = 2 * np.pi * t / SECONDS
    # Off, ignite from emitter to tip, hold, retract, then rest before looping.
    length = smoothstep(0.8, 1.45, t) * (1 - smoothstep(6.2, 6.7, t))
    tip = 665 - 219 * length
    softness = 3 + abs(x - 836) * 0.7
    reveal = smoothstep(tip - softness, tip + softness, y) * min(1, length * 25)
    rgb = unlit + (original - unlit) * reveal[..., None]
    pulse = 0.60 * np.sin(phase * 2) + 0.25 * np.sin(phase * 7 + 0.8)
    blue = np.maximum(original[..., 2] - original[..., 0], 0)
    lit = np.clip(blue / 75, 0, 1)
    vertical = np.exp(-((y - 554) / 126) ** 8)
    axis = 836 + 1.4 * np.sin((y - 446) / 35 + phase * 4)
    aura = np.exp(-((x - axis) / (13 + 2 * np.sin(phase * 3))) ** 2) * vertical
    ripple = np.sin((y - 446) / 24 - phase * 6) * lit * vertical
    # Local light only: the camera, hilt, ground and dark margins stay still.
    delta = (lit * pulse * 9 + aura * (6 + pulse * 5) + ripple * 3) * reveal
    # A compact white-blue tip leads the extending blade, rather than fading
    # the entire sword in at once.
    moving = 1 if 0.8 < t < 1.45 or 6.2 < t < 6.7 else 0
    tip_glow = np.exp(-((x - 836) / 9) ** 2 - ((y - tip) / 7) ** 2)
    tip_glow *= moving * min(1, length * 12)
    rgb += delta[..., None] * np.array([0.30, 0.65, 1.0], dtype=np.float32)
    rgb += tip_glow[..., None] * np.array([110, 175, 230], dtype=np.float32)
    result = base.copy()
    result[top:bottom, left:right] = np.clip(rgb, 0, 255).astype(np.uint8)
    return result


def main():
    prepared = prepare()
    base = prepared[0]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{base.shape[1]}x{base.shape[0]}",
        "-r", str(FPS), "-i", "-", "-an",
        "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart", str(OUTPUT),
    ]
    # Check exact periodicity before encoding. No duplicate end frame is added.
    assert np.array_equal(frame_at(0, prepared), frame_at(SECONDS, prepared))
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for index in range(FPS * SECONDS):
            encoder.stdin.write(frame_at(index / FPS, prepared).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError("Video encoding failed")
    print(f"Saved {OUTPUT}: {SECONDS}s at {FPS}fps, {OUTPUT.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
