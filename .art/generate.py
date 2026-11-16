#!/usr/bin/env python3
"""Generate the Star Wars theme artwork: hairline drawings on near-black.

    uv run --with numpy --with pillow .art/generate.py [name ...]

Everything is procedural and original: no film stills, logos or third-party
images. Each wallpaper is the theme's darkest grey except for the few pixels
that draw the picture, and the share of drawn pixels is printed as it is
written. Colours are grey, crawl yellow and saber blue only, so nothing relies
on seeing red.

Writes backgrounds/*.png, unlock.png and preview-unlock.png next to this
directory. preview.png is a real screenshot; "protanopia-preview" re-renders
it as a protanope sees it.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
W, H = 3840, 2160

BASE = "#0b0b0c"  # darker_background in colors.toml
WINDOW = "#161617"  # background in colors.toml
GREY = "#8a8a8a"
PALE = "#c8c8c8"
YELLOW = "#ffe81f"
BLUE = "#80a2f8"


def rgb(value):
    value = value.lstrip("#")
    return np.array([int(value[i : i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def canvas(w=W, h=H):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x, y, np.zeros((h, w, 3), dtype=np.float32)


def stroke(distance, width):
    """Anti-aliased coverage of a line `width` px wide, given distance to its centre."""
    return np.clip(width / 2.0 - distance + 0.5, 0.0, 1.0)


def ring(x, y, cx, cy, radius, width):
    return stroke(np.abs(np.hypot(x - cx, y - cy) - radius), width)


def segment(x, y, ax, ay, bx, by, width):
    dx, dy = bx - ax, by - ay
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
    return stroke(np.hypot(x - (ax + t * dx), y - (ay + t * dy)), width), t


def paint(image, coverage, colour):
    return np.maximum(image, coverage[..., None] * rgb(colour))


def save(image, name):
    drawn = np.count_nonzero(image.any(axis=2)) / (image.shape[0] * image.shape[1])
    image = np.maximum(image, rgb(BASE))  # ink over the base grey
    data = (np.clip(image, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    path = ROOT / "backgrounds" / name
    Image.fromarray(data, mode="RGB").save(path, optimize=True)
    print(f"wrote {path.relative_to(ROOT)}  drawn pixels: {drawn:.3%}")


def twin_suns_art(x, y, image, cx, cy, unit, width, span=9.0):
    """Two suns over a horizon. `unit` is the larger sun's radius and the
    horizon reaches `span` units to either side."""
    horizon = cy + unit * 1.9
    half = unit * span
    line, t = segment(x, y, cx - half, horizon, cx + half, horizon, width)
    line *= np.clip(1.0 - np.abs(t - 0.5) * 2.0, 0.0, 1.0) ** 0.6  # fade out at both ends
    image = paint(image, line, GREY)
    image = paint(image, ring(x, y, cx - unit * 0.95, cy - unit * 0.25, unit, width), YELLOW)
    image = paint(image, ring(x, y, cx + unit * 1.25, cy + unit * 0.85, unit * 0.72, width), PALE)
    return image


def twin_suns():
    x, y, image = canvas()
    save(twin_suns_art(x, y, image, W * 0.5, H * 0.47, 78.0, 2.6), "1-twin-suns.png")


def lightspeed():
    """Sparse streaks leaving an empty vanishing point."""
    rng = np.random.default_rng(1977)
    scale = 2
    layers = {GREY: Image.new("L", (W * scale, H * scale)), BLUE: Image.new("L", (W * scale, H * scale))}
    draws = {colour: ImageDraw.Draw(layer) for colour, layer in layers.items()}
    cx, cy = W * scale / 2, H * scale / 2
    reach = np.hypot(cx, cy)
    for _ in range(150):
        angle = rng.uniform(0, 2 * np.pi)
        start = reach * rng.uniform(0.16, 1.0)
        length = start * rng.uniform(0.05, 0.22)
        colour = BLUE if rng.random() < 0.22 else GREY
        level = int(255 * rng.uniform(0.35, 1.0))
        ends = [
            (cx + np.cos(angle) * start, cy + np.sin(angle) * start),
            (cx + np.cos(angle) * (start + length), cy + np.sin(angle) * (start + length)),
        ]
        draws[colour].line(ends, fill=level, width=int(rng.integers(2, 5)))
    image = np.zeros((H, W, 3), dtype=np.float32)
    for colour, layer in layers.items():
        coverage = np.asarray(layer.reduce(scale), dtype=np.float32) / 255.0
        image = paint(image, coverage, colour)
    save(image, "2-lightspeed.png")


def starfield():
    """A few hundred single-pixel stars."""
    rng = np.random.default_rng(1980)
    image = np.zeros((H, W, 3), dtype=np.float32)
    count = 340
    xs, ys = rng.integers(0, W - 1, count), rng.integers(0, H - 1, count)
    level = (0.25 + 0.75 * rng.random(count) ** 2.2).astype(np.float32)
    tint = np.stack([rgb(c) for c in (PALE, PALE, PALE, PALE, PALE, PALE, YELLOW, BLUE)])
    colour = tint[rng.integers(0, len(tint), count)] * level[:, None]
    image[ys, xs] = colour
    big = level > 0.8  # the brightest get a 2x2 dot
    for dx, dy in ((1, 0), (0, 1), (1, 1)):
        image[ys[big] + dy, xs[big] + dx] = colour[big]
    save(image, "3-starfield.png")


def saber():
    """One blade: a hairline hilt and a thin line of light."""
    x, y, image = canvas()
    cy = H * 0.5
    hilt_a, hilt_b = W * 0.335, W * 0.385
    blade_end = W * 0.665
    half = 13.0

    # Tight blue halo, cut off where it would only be raising black to grey.
    core, _ = segment(x, y, hilt_b + 6, cy, blade_end, cy, 3.0)
    d = np.where((x >= hilt_b + 6) & (x <= blade_end), np.abs(y - cy), np.hypot(x - blade_end, y - cy))
    d = np.where(x < hilt_b + 6, 1e6, d)
    halo = np.exp(-((d / 5.0) ** 2)) * 0.75
    halo[halo < 0.03] = 0.0
    image = paint(image, halo, BLUE)
    image = paint(image, core, "#f2f2f2")

    width = 2.2
    for ax, ay, bx, by in (
        (hilt_a, cy - half, hilt_b, cy - half),
        (hilt_a, cy + half, hilt_b, cy + half),
        (hilt_a, cy - half, hilt_a, cy + half),
        (hilt_b, cy - half - 5, hilt_b, cy + half + 5),
        (hilt_a + 30, cy - half, hilt_a + 30, cy + half),
        (hilt_a + 44, cy - half, hilt_a + 44, cy + half),
        (hilt_a + 58, cy - half, hilt_a + 58, cy + half),
    ):
        image = paint(image, segment(x, y, ax, ay, bx, by, width)[0], GREY)
    image = paint(image, ring(x, y, hilt_b - 34, cy, 4.5, width), YELLOW)  # activation stud
    save(image, "4-saber.png")


def emblem():
    """unlock.png: the twin suns on transparency, for the boot splash."""
    size, scale = 420, 4
    x, y, image = canvas(size * scale, size * scale)
    centre = size * scale / 2
    image = twin_suns_art(x, y, image, centre, centre - 98, 300.0, 3.0 * scale, span=2.7)
    alpha = image.max(axis=2)
    colour = np.where(alpha[..., None] > 0, image / np.maximum(alpha[..., None], 1e-6), 0.0)
    rgba = (np.dstack([colour, alpha]) * 255.0 + 0.5).astype(np.uint8)
    Image.fromarray(rgba, mode="RGBA").resize((size, size), Image.LANCZOS).save(ROOT / "unlock.png", optimize=True)
    print("wrote unlock.png")


def unlock_preview():
    """preview-unlock.png: the boot splash as the unlock picker shows it."""
    scale = 2
    w, h = 1920 * scale, 1080 * scale
    page = Image.new("RGB", (w, h), WINDOW)
    logo = Image.open(ROOT / "unlock.png").convert("RGBA")
    logo = logo.resize((logo.width * scale, logo.height * scale), Image.LANCZOS)
    page.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
    draw = ImageDraw.Draw(page)
    text = tuple(int(c * 255) for c in rgb(PALE))
    # Password field with four typed dots, and a padlock to its left.
    draw.rectangle([818 * scale, 770 * scale, 1102 * scale, 816 * scale], outline=text, width=2 * scale)
    for i in range(4):
        cx, cy = (840 + i * 12) * scale, 793 * scale
        draw.ellipse([cx - 3 * scale, cy - 3 * scale, cx + 3 * scale, cy + 3 * scale], fill=text)
    draw.rounded_rectangle([769 * scale, 789 * scale, 801 * scale, 813 * scale], radius=4 * scale, fill=text)
    draw.arc([775 * scale, 775 * scale, 795 * scale, 801 * scale], 180, 360, fill=text, width=4 * scale)
    draw.ellipse([782 * scale, 797 * scale, 788 * scale, 803 * scale], fill=WINDOW)
    page.resize((1920, 1080), Image.LANCZOS).save(ROOT / "preview-unlock.png", optimize=True)
    print("wrote preview-unlock.png")


def protanopia_preview():
    """.art/preview-protanopia.png: preview.png through the same simulation
    cvd.py uses, to show what survives without red."""
    from cvd import PROTAN

    data = np.asarray(Image.open(ROOT / "preview.png").convert("RGB"), dtype=np.float32) / 255.0
    linear = np.where(data <= 0.04045, data / 12.92, ((data + 0.055) / 1.055) ** 2.4)
    seen = np.clip(linear @ PROTAN.T, 0.0, 1.0)
    out = np.where(seen <= 0.0031308, seen * 12.92, 1.055 * seen ** (1 / 2.4) - 0.055)
    Image.fromarray((out * 255.0 + 0.5).astype(np.uint8), mode="RGB").save(
        ROOT / ".art" / "preview-protanopia.png", optimize=True
    )
    print("wrote .art/preview-protanopia.png")


ART = {
    "twin-suns": twin_suns,
    "lightspeed": lightspeed,
    "starfield": starfield,
    "saber": saber,
    "emblem": emblem,
    "unlock-preview": unlock_preview,
    "protanopia-preview": protanopia_preview,
}

if __name__ == "__main__":
    (ROOT / "backgrounds").mkdir(exist_ok=True)
    for name in sys.argv[1:] or ART:
        ART[name]()
