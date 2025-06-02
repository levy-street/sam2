#!/usr/bin/env python3
"""Convert magenta mask screenshots to binary mask PNGs."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

MAGENTA = np.array([255, 0, 255], dtype=np.uint8)


def convert_mask(src: Path, dst: Path, tolerance: int = 30) -> None:
    """Convert a single screenshot mask to binary.

    Pixels that are within ``tolerance`` of the magenta color are treated as
    foreground.  ``tolerance`` is applied per channel.
    """

    img = Image.open(src).convert("RGB")
    arr = np.array(img, dtype=np.int16)
    diff = np.abs(arr - MAGENTA)
    binary = (diff <= tolerance).all(axis=-1).astype(np.uint8) * 255
    Image.fromarray(binary).save(dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert mask screenshots to binary masks")
    parser.add_argument("--input-dir", required=True, help="Directory containing *_mask.png files")
    parser.add_argument("--output-dir", required=True, help="Output directory for binary masks")
    parser.add_argument(
        "--tolerance",
        type=int,
        default=30,
        help="Maximum per-channel difference from magenta to consider as foreground",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    for mask_file in input_dir.rglob("*_mask.png"):
        rel = mask_file.relative_to(input_dir)
        out_file = output_dir / rel
        out_file.parent.mkdir(parents=True, exist_ok=True)
        convert_mask(mask_file, out_file, tolerance=args.tolerance)
        print(f"Saved {out_file}")


if __name__ == "__main__":
    main()
