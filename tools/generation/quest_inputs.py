"""Load portable quest inputs without losing the catalog's source field order."""

from functools import lru_cache
import gzip
import json
from pathlib import Path
from typing import Dict, Tuple


@lru_cache(maxsize=1)
def load_sources(path: Path) -> Dict[str, object]:
    with gzip.open(path, "rt", encoding="utf-8") as source:
        return json.load(source)


def journals(sources) -> Dict[str, Tuple[Dict[str, object], ...]]:
    return {
        quest_id: tuple({"stage": stage["stage"], "journal": tuple(stage["journal"])} for stage in stages)
        for quest_id, stages in sources["journals"].items()
    }


def npc_stats(sources, table: str, canonical_root: Path) -> Dict[Tuple[str, int], Dict[str, object]]:
    # pprint wrapping depends on path lengths, so canonicalize before formatting.
    return {
        (name, level): {
            **payload,
            **{
                field: {key: payload[field][key] for key in order}
                for field, order in payload["field_order"].items()
            },
            "source": "; ".join(str(canonical_root / path) for path in payload["source"].split("; ")),
        }
        for name, level, payload in sources[table]
    }
