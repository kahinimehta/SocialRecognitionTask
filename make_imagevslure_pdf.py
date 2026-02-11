#!/usr/bin/env python3
"""Generate ImagevsLure.pdf: each image pictured next to its lure. Run from repo root. Deleted after use."""

import os
import re
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib import image as mpimg

STIMULI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "STIMULI")
OUT_PDF = os.path.join(STIMULI_DIR, "ImagevsLure.pdf")

def find_pairs():
    """Return list of (stimulus_num, image_path, lure_path) for 1..100."""
    pairs = []
    for num in range(1, 101):
        img_name = f"Image_{num:03d}.jpg"
        lure_name = f"Lure_{num:03d}.jpg"
        img_path = lure_path = None
        for root, dirs, files in os.walk(STIMULI_DIR):
            # Skip non-image dirs
            if "Amy.png" in files or "Ben.png" in files or "Image_Similarity" in files:
                continue
            for f in files:
                if f == img_name:
                    img_path = os.path.join(root, f)
                if f == lure_name:
                    lure_path = os.path.join(root, f)
            if img_path and lure_path:
                break
        if img_path and lure_path and os.path.isfile(img_path) and os.path.isfile(lure_path):
            pairs.append((num, img_path, lure_path))
    return sorted(pairs, key=lambda x: x[0])

def main():
    pairs = find_pairs()
    if not pairs:
        print("No image/lure pairs found in", STIMULI_DIR)
        return
    # 5 pairs per page: each row = one pair (Image | Lure), 5 rows per page
    n_per_page = 5
    with PdfPages(OUT_PDF) as pdf:
        for i in range(0, len(pairs), n_per_page):
            page_pairs = pairs[i : i + n_per_page]
            fig, axes = plt.subplots(n_per_page, 2, figsize=(8, 2 * n_per_page))
            if n_per_page == 1:
                axes = axes.reshape(1, -1)
            for row, (num, img_path, lure_path) in enumerate(page_pairs):
                for col, (path, label) in enumerate([(img_path, "Image"), (lure_path, "Lure")]):
                    ax = axes[row, col]
                    try:
                        img = mpimg.imread(path)
                        ax.imshow(img)
                    except Exception as e:
                        ax.text(0.5, 0.5, f"Error\n{e}", ha="center", va="center", fontsize=8)
                    ax.set_title(f"Pair {num}: {label}", fontsize=9)
                    ax.axis("off")
            plt.suptitle("Image & Lure Pairs", fontsize=12, y=1.02)
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    print("Saved", OUT_PDF)

if __name__ == "__main__":
    main()
