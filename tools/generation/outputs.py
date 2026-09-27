"""Write generated files, or prove the checked-in files already match them."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


def write_or_check(outputs: Mapping[Path, str], *, check: bool) -> int:
    """Write each changed output, or with ``check`` only name it and return 1.

    ``--check`` is the fixed output-identity proof for generator refactors. It
    compares bytes in memory, so unlike a hand-built ``find | shasum`` manifest
    its verdict cannot depend on the working directory or on how paths are
    spelled.
    """
    changed = [path for path, text in outputs.items() if not path.exists() or path.read_bytes() != text.encode("utf-8")]
    for path in changed:
        if check:
            print(f"differs: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(outputs[path].encode("utf-8"))
            print(f"wrote {path}")
    if not check:
        return 0
    print(f"OUTPUT_CHECK: {len(outputs) - len(changed)} of {len(outputs)} files unchanged")
    return 1 if changed else 0
