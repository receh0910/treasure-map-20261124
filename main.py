#!/usr/bin/env python3
"""Entrypoint: copy entry.png to $MAKEFUN_OUTPUT_DIR/entry.png.

Standard library only. Deterministic: the output is a byte copy of the
bundled entry.png, so two runs produce identical files.
"""
import hashlib
import os
import shutil
import sys

PNG_SIGNATURE = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
SOURCE = "entry.png"


def sha256_of(path):
    """Return the hex SHA-256 digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not os.path.isfile(SOURCE):
        print(f"error: {SOURCE} not found next to main.py", file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as handle:
        header = handle.read(8)
    if header != PNG_SIGNATURE:
        print("error: entry.png has a bad PNG signature", file=sys.stderr)
        return 1
    size = os.path.getsize(SOURCE)
    if size > 1048576:
        print(f"error: entry.png is {size} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    print(f"wrote {dest} ({size} bytes, sha256={sha256_of(dest)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
