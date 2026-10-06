"""Photo -> monochrome ASCII portrait SVG (ascii-portrait.svg). Run locally, only when the photo changes.

    python scripts/portrait.py photo.jpg --crop 0 .16 1 .72 --erase 0 .65 .3 1
    # --crop keeps a box, --erase blanks a box inside the crop (both as fractions of the photo)

The photo itself is never committed (.gitignore). Needs: rembg, opencv-python-headless, pillow, numpy.
"""
import argparse
from html import escape
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = Path(__file__).resolve().parent.parent / "ascii-portrait.svg"
W = 370                              # 370 + 490 (info card) = 860, the heatmap width
FONT, CW, LH = 6, 3.6, 6.4           # monospace glyphs are ~0.6em wide
COLS = int(W / CW)
RAMP = " .`:-=+*cs#%@"               # sparse -> dense


def grid(photo, crop, erase):
    img = Image.open(photo).convert("RGB")
    w, h = img.size
    box = [int(f * s) for f, s in zip(crop, (w, h, w, h))]
    img = img.crop(box)
    # 2x Lanczos plus an unsharp mask: phone photos are soft, and edges are what survive as glyphs
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    img = Image.fromarray(cv2.addWeighted(np.asarray(img), 1.6, cv2.GaussianBlur(np.asarray(img), (0, 0), 3), -0.6, 0))
    rgba = np.asarray(Image.open(BytesIO(remove(_png(img)))).convert("RGBA")).copy()   # isolate the subject
    if erase:                                                            # props the cut-out kept
        ex0, ey0, ex1, ey1 = [(int(f * s) - o) * 2 for f, s, o in zip(erase, (w, h, w, h), box[:2] * 2)]
        rgba[max(ey0, 0):max(ey1, 0), max(ex0, 0):max(ex1, 0), 3] = 0
    rows = int(W * rgba.shape[0] / rgba.shape[1] / LH)                 # keep the crop's aspect ratio
    grey = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    grey = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(grey)  # flat light -> real shadows
    grey = cv2.resize(grey, (COLS, rows), interpolation=cv2.INTER_AREA) / 255.0
    mask = cv2.resize(rgba[..., 3], (COLS, rows), interpolation=cv2.INTER_AREA) > 127
    lo, hi = np.percentile(grey[mask], (2, 98))                         # stretch over the subject only
    return np.clip((grey - lo) / (hi - lo), 0, 1), mask


def _png(img):
    b = BytesIO(); img.save(b, "PNG"); return b.getvalue()


def rows_for(grey, mask, dark_bg):
    """Dense glyphs carry ink: dark pixels on a light page, bright pixels on a dark page."""
    level = grey if dark_bg else 1 - grey
    idx = np.clip((level * (len(RAMP) - 1)).round().astype(int), 1, len(RAMP) - 1)   # subject never blank
    return ["".join(RAMP[i] if m else " " for i, m in zip(r, mr)).rstrip() for r, mr in zip(idx, mask)]


def svg(light, dark):
    H = round(len(light) * LH + 4)
    def group(cls, lines):
        return f'<g class="{cls}">' + "".join(
            f'<text x="0" y="{(k + 1) * LH:.1f}" style="animation-delay:{k * 35}ms">{escape(t)}</text>'
            for k, t in enumerate(lines) if t) + "</g>"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII art portrait of Akhil">
<style>
  text {{ font: {FONT}px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre; fill: #24292f;
          animation: in 140ms linear backwards; }}          /* visible unless the animation runs */
  @keyframes in {{ from {{ opacity: 0; }} }}
  .dk {{ display: none; }}
  @media (prefers-color-scheme: dark) {{ .lt {{ display: none; }} .dk {{ display: inline; }} text {{ fill: #c9d1d9; }} }}
  @media (prefers-reduced-motion: reduce) {{ text {{ animation: none; }} }}
</style>
{group("lt", light)}
{group("dk", dark)}
</svg>
'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--crop", nargs=4, type=float, default=(0, 0, 1, 1), metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--erase", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"))
    a = ap.parse_args()
    grey, mask = grid(a.photo, a.crop, a.erase)
    OUT.write_text(svg(rows_for(grey, mask, False), rows_for(grey, mask, True)))
    print(f"wrote {OUT.name}: {COLS}x{len(grey)} characters, subject covers {mask.mean():.0%}")
