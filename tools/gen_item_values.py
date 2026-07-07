#!/usr/bin/env python3
"""Turn a DumpDarkanItemValues.java dump into item_values_generated.py.

Pipeline (needs a JDK that can run the Darkan core jar — class-file v68, i.e.
JDK 24+; JDK 25 works):

    javac -cp <core.jar:deps> -d <out> tools/DumpDarkanItemValues.java
    java  -cp <out:core.jar:deps> DumpDarkanItemValues <cache/> 30000 raw.json
    python3 tools/gen_item_values.py raw.json item_values_generated.py

Names can repeat across item ids (noted/charged variants); we keep the highest
value per name and mark a name stackable if any variant is.
"""

import json
import sys
from pathlib import Path


def build(raw_path: Path, out_path: Path) -> tuple[int, int]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))["items"]
    values: dict[str, int] = {}
    stackable: set[str] = set()
    for row in raw.values():
        name = row.get("name")
        if not isinstance(name, str) or not name:
            continue
        value = int(row.get("value", 0) or 0)
        if value > 0:
            values[name] = max(values.get(name, 0), value)
        if row.get("stackable"):
            stackable.add(name)

    lines = [
        '"""Generated from the Darkan cache by tools/DumpDarkanItemValues.java.',
        "",
        "Item store values (ItemDefinitions.getValue) and the cache stackable flag,",
        "keyed by item name. Regenerate with that tool + tools/gen_item_values.py.",
        'Do not hand-edit."""',
        "",
        "ITEM_VALUES_GENERATED = {",
    ]
    lines += [f"    {name!r}: {values[name]}," for name in sorted(values)]
    lines += ["}", "", "STACKABLE_ITEM_NAMES_GENERATED = frozenset({"]
    lines += [f"    {name!r}," for name in sorted(stackable)]
    lines += ["})", ""]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return len(values), len(stackable)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: gen_item_values.py <raw-json> <output-py>")
    n_values, n_stackable = build(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"wrote {n_values} values, {n_stackable} stackable names")
