#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

Pipeline:
  1. Remove the background with rembg so only the subject remains.
  2. Composite the subject onto pure white (background -> the blank end of
     the ASCII ramp, so it prints as spaces).
  3. Boost local contrast on the subject with CLAHE so a flatly-lit face
     gets real highlights and shadows instead of a grey blob.

Run this once per photo:
    python scripts/prep_photo.py source-photo.jpg
Writes: source-prepped.png  (grayscale, consumed by make_ascii_svg.py)
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main(src: str, out: str = "source-prepped.png") -> None:
    img = Image.open(src).convert("RGBA")

    # 1. Cut out the subject.
    cut = remove(img).convert("RGBA")
    arr = np.array(cut).astype(np.float32)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3:4] / 255.0

    # 2. Composite onto pure white.
    white = np.full_like(rgb, 255.0)
    comp = (rgb * alpha + white * (1.0 - alpha)).astype(np.uint8)

    gray = cv2.cvtColor(comp, cv2.COLOR_RGB2GRAY)

    # 3. CLAHE contrast boost, then keep the background pure white so it
    #    maps to spaces in the ASCII ramp.
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    mask = (alpha[:, :, 0] > 0.1)
    out_arr = np.where(mask, enhanced, 255).astype(np.uint8)

    Image.fromarray(out_arr, mode="L").save(out)
    print(f"wrote {out}  ({out_arr.shape[1]}x{out_arr.shape[0]})")


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    main(source)
