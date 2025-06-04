#!/usr/bin/env python3
"""Flatten annotation directories.

Move PNG files from ``polygon_*/0/`` into ``polygon_*``.

Usage:
    python scripts/flatten_annotation_dirs.py --ann-dir dataset/Annotations
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def flatten(ann_root: Path) -> None:
    """Flatten ``polygon_*`` folders under ``ann_root``."""
    for polygon_dir in ann_root.glob("polygon_*"):
        zero_dir = polygon_dir / "0"
        if not zero_dir.is_dir():
            continue
        for png_file in zero_dir.glob("*.png"):
            dest = polygon_dir / png_file.name
            dest_parent = dest.parent
            dest_parent.mkdir(parents=True, exist_ok=True)
            print(f"Moving {png_file} -> {dest}")
            shutil.move(str(png_file), dest)
        try:
            zero_dir.rmdir()
        except OSError:
            print(f"Could not remove {zero_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Flatten annotation directories by removing the '0' subdirectory"
    )
    parser.add_argument(
        "--ann-dir",
        default="dataset/Annotations",
        help="Path to Annotations directory",
    )
    args = parser.parse_args()

    flatten(Path(args.ann_dir))


if __name__ == "__main__":
    main()
