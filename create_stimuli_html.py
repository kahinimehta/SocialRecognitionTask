#!/usr/bin/env python3
"""
Create a compact HTML file visualizing all Image vs Lure stimulus pairs.
Designed for few pages when printed (12 pairs per page).
"""

import html as html_module
import os
from pathlib import Path

STIMULI_DIR = Path(__file__).parent / "STIMULI"
OUTPUT_HTML = Path(__file__).parent / "stimuli_image_vs_lure.html"
PAIRS_PER_PAGE = 18  # 6 columns × 3 rows
IMG_HEIGHT = 75  # pixels


def find_image_lure_pairs():
    """Find all Image_XXX.jpg and Lure_XXX.jpg pairs in STIMULI directory."""
    pairs = []
    for root, dirs, files in os.walk(STIMULI_DIR):
        rel_root = Path(root).relative_to(STIMULI_DIR)
        parts = rel_root.parts
        images = {f for f in files if f.startswith("Image_") and f.endswith(".jpg")}
        lures = {f for f in files if f.startswith("Lure_") and f.endswith(".jpg")}
        for img_file in images:
            num = img_file.replace("Image_", "").replace(".jpg", "")
            lure_file = f"Lure_{num}.jpg"
            if lure_file in lures:
                img_path = Path(root) / img_file
                lure_path = Path(root) / lure_file
                category = parts[0] if len(parts) > 0 else ""
                item_name = parts[-1] if len(parts) > 1 else category or "Root"
                pairs.append((category, item_name, img_path, lure_path))
    pairs.sort(key=lambda p: int(p[2].name.replace("Image_", "").replace(".jpg", "")))
    return pairs


def create_html():
    pairs = find_image_lure_pairs()
    print(f"Found {len(pairs)} Image/Lure pairs")
    if not pairs:
        print("No pairs found.")
        return

    project_root = Path(__file__).parent

    html = ['<!DOCTYPE html><html><head><meta charset="utf-8"><title>Image vs Lure Stimuli</title>']
    html.append("""
<style>
* { box-sizing: border-box; }
body { font-family: system-ui, sans-serif; font-size: 10px; margin: 0; padding: 8px; }
.page { display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px 8px; margin-bottom: 12px; }
.pair { border: 1px solid #ccc; padding: 4px; text-align: center; break-inside: avoid; }
.pair-row { display: flex; gap: 4px; align-items: center; justify-content: center; min-height: """ + str(IMG_HEIGHT + 20) + """px; }
.pair-row img { max-height: """ + str(IMG_HEIGHT) + """px; max-width: 100%; object-fit: contain; }
.pair-label { font-weight: bold; margin-bottom: 2px; }
.pair-images { display: flex; gap: 4px; justify-content: center; }
.pair-images span { font-size: 8px; color: #666; }
@media print {
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
}
</style>
</head><body>""")

    for i in range(0, len(pairs), PAIRS_PER_PAGE):
        chunk = pairs[i : i + PAIRS_PER_PAGE]
        html.append('<div class="page">')
        for category, item_name, img_path, lure_path in chunk:
            rel_img = img_path.relative_to(project_root).as_posix()
            rel_lure = lure_path.relative_to(project_root).as_posix()
            num = img_path.name.replace("Image_", "").replace(".jpg", "")
            html.append(f'''
<div class="pair">
  <div class="pair-label">{html_module.escape(f"{category} / {item_name}")}</div>
  <div class="pair-row">
    <div><span>Img</span><br><img src="{rel_img}" alt="Image {num}"></div>
    <div><span>Lure</span><br><img src="{rel_lure}" alt="Lure {num}"></div>
  </div>
</div>''')
        html.append("</div>")

    html.append("</body></html>")

    OUTPUT_HTML.write_text("".join(html), encoding="utf-8")
    pages = (len(pairs) + PAIRS_PER_PAGE - 1) // PAIRS_PER_PAGE
    print(f"Saved: {OUTPUT_HTML} ({len(pairs)} pairs, ~{pages} pages when printed)")


if __name__ == "__main__":
    create_html()
