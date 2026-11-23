#!/usr/bin/env python3
"""News image entry for make.fun - news-image-20261123.

Copies the pre-rendered entry.png into the make.fun output directory and
validates it. Standard library only: no third-party packages are imported,
because the make.fun runner does not provide Pillow.

Usage:
    MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import hashlib
import os
import shutil
import struct
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
MAX_BYTES = 1024 * 1024          # 1 MiB
MAX_DIMENSION = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path):
    """Read width/height from the PNG IHDR chunk (stdlib only)."""
    with open(path, "rb") as fh:
        header = fh.read(33)
        fh.seek(-12, os.SEEK_END)
        trailer = fh.read(12)
    if header[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file: bad signature")
    if header[12:16] != b"IHDR":
        raise ValueError("not a PNG file: missing IHDR chunk")
    if trailer[4:8] != b"IEND":
        raise ValueError("not a PNG file: truncated, missing IEND chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(SOURCE):
        print("error: entry.png missing next to main.py", file=sys.stderr)
        return 1

    size = os.path.getsize(SOURCE)
    if size > MAX_BYTES:
        print("error: entry.png is %d bytes, over the 1 MiB limit"
              % size, file=sys.stderr)
        return 1

    width, height = png_dimensions(SOURCE)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print("error: entry.png is %dx%d, over the 1024x1024 limit"
              % (width, height), file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SOURCE, dest)

    # Verify the copy is byte-identical to the source.
    if sha256_file(SOURCE) != sha256_file(dest):
        print("error: copied entry.png differs from source",
              file=sys.stderr)
        return 1

    print("ok: wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (dest, width, height, size, sha256_file(dest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
