#!/usr/bin/env python3
"""
make_ascii_svg.py
Reads source-prepped.png (bg removed + CLAHE'd) and writes avi-ascii.svg:
a monochrome ASCII portrait that types itself in, left to right, row by row.

Set STATIC=1 as an env var to render the FINAL frame only (no animation) --
useful for a quick preview instead of waiting for the reveal.
"""
import os
import numpy as np
from PIL import Image

SRC = "source-prepped.png"
OUT = "avi-ascii.svg"

COLS = 130            # ascii grid width (characters)
CHAR_W = 7             # px per character cell
CHAR_H = 14
FONT_SIZE = 13
COLOR = "#8b949e"      # single monochrome tone (GitHub muted gray)
BG = "transparent"

CONTRAST = 1.15
GAMMA = 0.9
WHITE_FLOOR = 235       # luminance >= this is treated as background -> space

ROW_DUR = 0.9           # seconds for one row to type across
STAGGER = 0.06          # delay between the start of each row

RAMP = " .:-=+*#%@"     # dark -> light is reversed below (dense chars = subject)

def load_luminance():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    rows = int(COLS * (h / w) * (CHAR_W / CHAR_H))
    small = img.resize((COLS, max(rows, 1)))
    arr = np.array(small).astype(np.float32)
    rgb, a = arr[..., :3], arr[..., 3]
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])
    lum = np.clip((lum - 128) * CONTRAST + 128, 0, 255)
    lum = 255 * (lum / 255) ** GAMMA
    lum[a < 40] = 255  # transparent -> background -> blank
    return lum

def lum_to_char(v):
    if v >= WHITE_FLOOR:
        return " "
    idx = int((1 - v / 255) * (len(RAMP) - 1))
    return RAMP[max(0, min(idx, len(RAMP) - 1))]

def build_rows(lum):
    rows = []
    for y in range(lum.shape[0]):
        line = "".join(lum_to_char(v) for v in lum[y])
        rows.append(line.rstrip())
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    return rows

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    static = os.environ.get("STATIC", "0") == "1"
    lum = load_luminance()
    rows = build_rows(lum)

    width = COLS * CHAR_W + 20
    height = len(rows) * CHAR_H + 20

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="{FONT_SIZE}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>text {{ fill: {COLOR}; white-space: pre; }}</style>',
    ]

    for i, row in enumerate(rows):
        y = 20 + i * CHAR_H
        row_w = len(row) * CHAR_W
        text = f'<text x="10" y="{y}">{esc(row)}</text>'
        if static or row_w == 0:
            svg.append(text)
            continue
        begin = round(i * STAGGER, 3)
        svg.append(
            f'<g><clipPath id="clip{i}"><rect x="0" y="{y-CHAR_H}" width="0" height="{CHAR_H+4}">'
            f'<animate attributeName="width" from="0" to="{row_w+10}" '
            f'begin="{begin}s" dur="{ROW_DUR}s" fill="freeze" calcMode="linear"/>'
            f'</rect></clipPath>'
            f'<g clip-path="url(#clip{i})">{text}</g></g>'
        )

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg))
    print(f"saved {OUT}  ({len(rows)} rows, static={static})")

if __name__ == "__main__":
    main()
