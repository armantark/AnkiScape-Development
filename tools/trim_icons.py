#!/usr/bin/env python3
"""Trim transparent padding from small scraped item sprites, in place.

Why this exists: wiki item sprites are tightly-cropped art centered on a large
transparent canvas (e.g. Flax's real art is ~30x23 inside a 64x64 file). Inside
a fixed icon box they therefore render much smaller than the legacy full-frame
icons. Rather than doing per-paint cropping math at runtime, we bake the fix into
the asset once: trim each small sprite to its opaque bounding box so the UI can
display it with a plain ``QIcon(path)`` like every other icon.

Scope guard: only images whose largest side is ``<= MAX_DIM`` are touched. The
legacy crafted photos are 1000-1500px and already fill the frame; trimming them
would change their appearance, so they are left alone. The tool is idempotent —
re-running skips images that are already tight.

Backends: prefers Pillow; falls back to PyQt6's ``QImage`` so it runs in the Qt
test venv (``.venv-qt``) without extra dependencies. This is a developer-only
tool and is never imported by the add-on runtime.

Usage (default trims crafteditems/ and fletcheditems/ under the add-on root):
    .venv-qt/bin/python tools/trim_icons.py
    .venv-qt/bin/python tools/trim_icons.py --dry-run
    .venv-qt/bin/python tools/trim_icons.py crafteditems
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional, Sequence, Tuple

ADDON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIRS = ("crafteditems", "fletcheditems")
# Only small padded sprites need trimming; large full-frame photos are left as-is.
MAX_DIM = 256
# Alpha at or below this is treated as transparent padding.
ALPHA_THRESHOLD = 8

# (left, top, right, bottom) opaque bounds, inclusive of the cropped box width.
BBox = Tuple[int, int, int, int]


def _bbox_pillow(path: str) -> Optional[Tuple[Tuple[int, int], BBox]]:
    from PIL import Image  # type: ignore

    with Image.open(path) as opened:
        image = opened.convert("RGBA")
        size = (image.width, image.height)
        alpha = image.getchannel("A")
        # point(): map alpha <= threshold -> 0 so getbbox ignores faint padding.
        mask = alpha.point(lambda a: 255 if a > ALPHA_THRESHOLD else 0)
        box = mask.getbbox()  # (left, upper, right, lower) or None
    if box is None:
        return None
    return size, box


def _crop_pillow(path: str, box: BBox) -> None:
    from PIL import Image  # type: ignore

    with Image.open(path) as opened:
        image = opened.convert("RGBA").crop(box)
        image.save(path, format="PNG")


def _bbox_qt(path: str) -> Optional[Tuple[Tuple[int, int], BBox]]:
    from aqt.qt import QImage  # type: ignore

    img = QImage(path)
    if img.isNull():
        return None
    w, h = img.width(), img.height()
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            if (img.pixel(x, y) >> 24) & 0xFF > ALPHA_THRESHOLD:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
    if max_x < min_x or max_y < min_y:
        return None
    # Pillow-style box: right/bottom are exclusive.
    return (w, h), (min_x, min_y, max_x + 1, max_y + 1)


def _crop_qt(path: str, box: BBox) -> None:
    from aqt.qt import QImage, QRect  # type: ignore

    img = QImage(path)
    left, top, right, bottom = box
    cropped = img.copy(QRect(left, top, right - left, bottom - top))
    cropped.save(path, "PNG")


def _select_backend() -> Tuple[str, object, object]:
    try:
        import PIL  # type: ignore  # noqa: F401

        return "Pillow", _bbox_pillow, _crop_pillow
    except Exception:
        pass
    try:
        import aqt  # type: ignore  # noqa: F401

        return "Qt", _bbox_qt, _crop_qt
    except Exception as exc:  # pragma: no cover - no backend available
        raise SystemExit(
            "Neither Pillow nor PyQt6 (aqt) is importable. Run with `.venv-qt/bin/python` "
            "or `uv run`."
        ) from exc


def _iter_pngs(directory: str) -> List[str]:
    if not os.path.isdir(directory):
        return []
    return [
        os.path.join(directory, name)
        for name in sorted(os.listdir(directory))
        if name.lower().endswith(".png")
    ]


def trim_directory(directory: str, *, dry_run: bool) -> Tuple[int, int, int]:
    """Trim padded sprites in one directory. Returns (trimmed, skipped, ignored)."""
    backend_name, bbox_fn, crop_fn = _select_backend()
    trimmed = skipped = ignored = 0
    for path in _iter_pngs(directory):
        result = bbox_fn(path)  # type: ignore[operator]
        if result is None:
            ignored += 1
            continue
        (w, h), box = result
        if max(w, h) > MAX_DIM:
            ignored += 1  # large full-frame icon; leave it alone
            continue
        left, top, right, bottom = box
        if (right - left, bottom - top) == (w, h):
            skipped += 1  # already tight
            continue
        rel = os.path.relpath(path, ADDON_ROOT)
        action = "would trim" if dry_run else "trimmed"
        print(f"  {action} {rel}: {w}x{h} -> {right - left}x{bottom - top}")
        if not dry_run:
            crop_fn(path, box)  # type: ignore[operator]
        trimmed += 1
    print(f"[{backend_name}] {directory}: {trimmed} trimmed, {skipped} already tight, {ignored} left as-is")
    return trimmed, skipped, ignored


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dirs",
        nargs="*",
        default=list(DEFAULT_DIRS),
        help="Folders (relative to the add-on root) to trim. Defaults to crafteditems and fletcheditems.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing.")
    args = parser.parse_args(argv)

    total = 0
    for name in args.dirs:
        directory = name if os.path.isabs(name) else os.path.join(ADDON_ROOT, name)
        trimmed, _skipped, _ignored = trim_directory(directory, dry_run=args.dry_run)
        total += trimmed
    print(f"Done. {total} sprite(s) {'would be ' if args.dry_run else ''}trimmed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
