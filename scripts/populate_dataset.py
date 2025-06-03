#!/usr/bin/env python3
"""Populate dataset directories from raw Google Earth screenshots."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image

# Reuse mask conversion helper
from convert_mask_screenshots import convert_mask


def process_polygon(
    idx: int,
    raw_path: Path,
    mask_path: Path,
    jpeg_root: Path,
    ann_root: Path,
    tolerance: int = 30,
) -> None:
    """Convert and copy a raw/mask pair into the dataset structure."""
    match = re.search(r"polygon_(\d+)_raw\.png$", raw_path.name)
    if not match:
        print(f"Skipping {raw_path}: unexpected filename")
        return
    # idx = int(match.group(1))
    polygon_name = f"polygon_{idx:04d}"

    out_img_dir = jpeg_root / polygon_name
    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_img = out_img_dir / "00000.jpg"
    Image.open(raw_path).convert("RGB").save(out_img)

    out_ann_dir = ann_root / polygon_name / "0"
    out_ann_dir.mkdir(parents=True, exist_ok=True)
    out_ann = out_ann_dir / "00000.png"
    convert_mask(mask_path, out_ann, tolerance=tolerance)

    print(f"Processed {polygon_name}")


def populate_dataset(
    input_root: Path, jpeg_root: Path, ann_root: Path, tolerance: int = 30
) -> None:
    for idx, raw_file in enumerate(input_root.rglob("*_raw.png")):
        mask_file = raw_file.with_name(raw_file.name.replace("_raw.png", "_mask.png"))
        if not mask_file.exists():
            print(f"Skipping {raw_file}: no corresponding mask")
            continue
        process_polygon(
            idx, raw_file, mask_file, jpeg_root, ann_root, tolerance=tolerance
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate dataset from raw screenshots"
    )
    parser.add_argument(
        "--input-dir",
        default="data/output",
        help="Directory containing raw screenshots",
    )
    parser.add_argument(
        "--jpeg-dir", default="dataset/JPEGImages", help="Output JPEGImages directory"
    )
    parser.add_argument(
        "--ann-dir", default="dataset/Annotations", help="Output Annotations directory"
    )
    parser.add_argument(
        "--tolerance", type=int, default=30, help="Mask color tolerance"
    )
    args = parser.parse_args()

    populate_dataset(
        Path(args.input_dir),
        Path(args.jpeg_dir),
        Path(args.ann_dir),
        tolerance=args.tolerance,
    )


if __name__ == "__main__":
    main()
