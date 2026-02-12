#!/usr/bin/env python3
"""
Generate imagevs_lure.pdf: each stimulus image displayed side-by-side with its lure.
Uses PIL only (no matplotlib) for fast PDF generation.
"""

import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Paths
STIMULI_DIR = Path(__file__).parent / "STIMULI"
OUTPUT_PDF = Path(__file__).parent / "imagevs_lure.pdf"

# Page dimensions (points at 72 DPI equivalently scaled for images)
PAGE_WIDTH = 612   # 8.5 inches
PAGE_HEIGHT = 432  # 6 inches (half for each image in landscape-like layout)
MARGIN = 20
MAX_IMG_HEIGHT = 350


def find_image_lure_pairs():
    """Find all Image/Lure pairs in the stimuli directory."""
    pairs = []
    image_pattern = re.compile(r"Image_(\d+)\.(jpg|jpeg|png)$", re.I)
    lure_pattern = re.compile(r"Lure_(\d+)\.(jpg|jpeg|png)$", re.I)

    for root, dirs, files in os.walk(STIMULI_DIR):
        images = {}
        lures = {}
        for f in files:
            imatch = image_pattern.match(f)
            lmatch = lure_pattern.match(f)
            if imatch:
                images[int(imatch.group(1))] = os.path.join(root, f)
            if lmatch:
                lures[int(lmatch.group(1))] = os.path.join(root, f)

        for num in sorted(images.keys()):
            if num in lures:
                pairs.append((images[num], lures[num], num))

    return sorted(pairs, key=lambda x: x[2])


def make_side_by_side(img_path, lure_path, num):
    """Create a side-by-side composite image (Image | Lure) with labels."""
    img = Image.open(img_path).convert("RGB")
    lure = Image.open(lure_path).convert("RGB")

    # Resize to fit within half page each
    half_w = (PAGE_WIDTH - 3 * MARGIN) // 2
    h = min(MAX_IMG_HEIGHT, img.height, lure.height)

    def resize_to_fit(im, max_w, max_h):
        r = min(max_w / im.width, max_h / im.height)
        nw, nh = int(im.width * r), int(im.height * r)
        return im.resize((nw, nh), Image.Resampling.LANCZOS)

    img = resize_to_fit(img, half_w, h)
    lure = resize_to_fit(lure, half_w, h)

    # Same height for row, add space for labels
    label_h = 28
    row_h = max(img.height, lure.height) + label_h
    total_w = img.width + MARGIN + lure.width
    composite = Image.new("RGB", (total_w, row_h), (255, 255, 255))
    composite.paste(img, (0, label_h))
    composite.paste(lure, (img.width + MARGIN, label_h))

    # Add labels
    draw = ImageDraw.Draw(composite)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except OSError:
        font = ImageFont.load_default()
    draw.text((img.width // 2 - 25, 4), f"Image {num}", fill=(0, 0, 0), font=font)
    draw.text((img.width + MARGIN + lure.width // 2 - 25, 4), f"Lure {num}", fill=(0, 0, 0), font=font)

    return composite


def main():
    pairs = find_image_lure_pairs()
    if not pairs:
        print("No Image/Lure pairs found.")
        return

    print(f"Found {len(pairs)} Image/Lure pairs")

    pages = []
    for img_path, lure_path, num in pairs:
        try:
            page = make_side_by_side(img_path, lure_path, num)
            pages.append(page)
        except Exception as e:
            print(f"Warning: Could not process pair {num}: {e}")

    if pages:
        pages[0].save(OUTPUT_PDF, save_all=True, append_images=pages[1:])
        print(f"Saved: {OUTPUT_PDF} ({len(pages)} pages)")
    else:
        print("No pages generated.")
