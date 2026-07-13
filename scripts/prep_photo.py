#!/usr/bin/env python3
"""
prep_photo.py <input.jpg> <output.png>
Removes background (rembg) and boosts local contrast (CLAHE) so the
subject reads clearly once converted to ASCII.
"""
import sys
import numpy as np
import cv2
from rembg import remove
from PIL import Image

CLIP_LIMIT = 2.5      # CLAHE strength -- higher = punchier local contrast
TILE_GRID = (8, 8)

def main():
    if len(sys.argv) != 3:
        print("usage: prep_photo.py <input.jpg> <output.png>")
        sys.exit(1)

    src_path, out_path = sys.argv[1], sys.argv[2]

    # 1. remove background
    with open(src_path, "rb") as f:
        input_bytes = f.read()
    result = remove(input_bytes)
    img = Image.open(__import__("io").BytesIO(result)).convert("RGBA")

    # 2. split alpha, apply CLAHE to the RGB part only
    rgb = np.array(img.convert("RGB"))
    alpha = np.array(img.split()[-1])

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID)
    l2 = clahe.apply(l)
    lab2 = cv2.merge((l2, a, b))
    rgb2 = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB)

    out = Image.fromarray(rgb2).convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    out.save(out_path)
    print(f"saved {out_path}  ({out.size[0]}x{out.size[1]})")

if __name__ == "__main__":
    main()
