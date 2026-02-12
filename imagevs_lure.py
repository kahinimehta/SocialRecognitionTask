#!/usr/bin/env python3
"""
Generate imagevs_lure.pdf: each stimulus image displayed side-by-side with its lure.
"""

import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image

# Paths
STIMULI_DIR = Path(__file__).parent / "STIMULI"
OUTPUT_PDF = Path(__file__).parent / "imagevs_lure.pdf"


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


def main():
    pairs = find_image_lure_pairs()
    if not pairs:
        print("No Image/Lure pairs found.")
        return

    print(f"Found {len(pairs)} Image/Lure pairs")

    rcParams["font.size"] = 10
    rcParams["axes.titlesize"] = 12

    n_pages = len(pairs)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    with plt.rc_context({"figure.max_open_warning": 0}):
        with plt.ioff():
            # Use PdfPages for multi-page PDF
            from matplotlib.backends.backend_pdf import PdfPages

            with PdfPages(OUTPUT_PDF) as pdf:
                for img_path, lure_path, num in pairs:
                    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

                    # Load images
                    try:
                        img = Image.open(img_path)
                        lure = Image.open(lure_path)
                    except Exception as e:
                        print(f"Warning: Could not load pair {num}: {e}")
                        plt.close(fig)
                        continue

                    # Display Image (left)
                    axes[0].imshow(img)
                    axes[0].set_title(f"Image {num:03d}")
                    axes[0].axis("off")

                    # Display Lure (right)
                    axes[1].imshow(lure)
                    axes[1].set_title(f"Lure {num:03d}")
                    axes[1].axis("off")

                    # Add category label from path (e.g., biganimal/Alligator)
                    rel_path = os.path.relpath(os.path.dirname(img_path), STIMULI_DIR)
                    fig.suptitle(rel_path, fontsize=11, y=1.02)

                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches="tight", dpi=150)
                    plt.close(fig)

    print(f"Saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
