"""Capture the external NPC shop inputs and decode only their private copies."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


DEFAULT_DARKAN_SHOPS = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops")
DEFAULT_DARKAN_CONTENT = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content")
DEFAULT_DARKAN_CACHE = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-cache")
DEFAULT_DARKAN_JAVA_HOME = Path("/Users/ArmanTarkhanian1/Documents/2012scape with bots/.jdks/jdk-24.0.2+12/Contents/Home")
DEFAULT_DARKAN_CORE_JAR = Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/rs.darkan/core/2.0.5/5a13ad7bada8a9b1587bfa72fb013283102c6b7d/core-2.0.5.jar")
DEFAULT_DARKAN_DEPENDENCY_JARS = (
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/it.unimi.dsi/fastutil/8.5.15/1e885b40c9563ab0d3899b871fd0b30e958705dc/fastutil-8.5.15.jar"),
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-api/2.20.0/1fe6082e660daf07c689a89c94dc0f49c26b44bb/log4j-api-2.20.0.jar"),
    Path("/Users/ArmanTarkhanian1/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-core/2.20.0/eb2a9a47b1396e00b5eee1264296729a70565cc0/log4j-core-2.20.0.jar"),
)
DEFAULT_2011_ITEMS = Path("/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml")

DARKAN_PRICE_HELPER = Path(__file__).resolve().parents[1] / "DumpDarkanShopPriceInputs.java"


@dataclass(frozen=True)
class CapturedShopInputs:
    directory: Path
    shops: Path
    items: Path
    cache: Path
    core_jar: Path
    dependency_jars: tuple[Path, ...]
    digests: dict[str, str]


def _source_members(shops: Path, items: Path, cache: Path, jars: tuple[Path, ...]) -> dict[str, Path]:
    for directory in (shops, cache):
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing NPC shop source directory: {directory}")
    shop_files = sorted(shops.glob("*.json"))
    if not shop_files:
        raise ValueError(f"No top-level NPC shop JSON sources: {shops}")
    master_index = cache / "main_file_cache.idx255"
    if not master_index.is_file():
        raise FileNotFoundError(f"Missing NPC shop cache index: {master_index}")
    members = {"game-main/data/cfg/items.yml": items, "darkan/cache/main_file_cache.dat2": cache / "main_file_cache.dat2"}
    members.update({f"darkan/shops/{path.name}": path for path in shop_files})
    members.update({
        f"darkan/cache/{path.name}": path for path in sorted(cache.iterdir())
        if re.fullmatch(r"main_file_cache\.idx[0-9]+", path.name)
    })
    members.update({f"darkan/decoder/classpath/{ordinal:04d}": path for ordinal, path in enumerate(jars)})
    return members


def _copy_and_hash(source: Path, destination: Path) -> str:
    if not source.is_file():
        raise FileNotFoundError(f"Missing NPC shop source file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with source.open("rb") as original, destination.open("wb") as captured:
        while block := original.read(1024 * 1024):
            captured.write(block)
            digest.update(block)
    return digest.hexdigest()


@contextmanager
def capture_source_inputs(
    shops: Path, items: Path, cache: Path, core_jar: Path, dependency_jars: Iterable[Path],
) -> Iterator[CapturedShopInputs]:
    jars = (core_jar, *dependency_jars)
    members = _source_members(shops, items, cache, jars)
    with tempfile.TemporaryDirectory(prefix="ankiscape-shop-inputs-") as directory:
        snapshot = Path(directory)
        destinations = {
            name: snapshot / (name + ".jar" if name.startswith("darkan/decoder/classpath/") else name)
            for name in members
        }
        digests = {name: _copy_and_hash(source, destinations[name]) for name, source in members.items()}
        classpath = tuple(destinations[f"darkan/decoder/classpath/{ordinal:04d}"] for ordinal in range(len(jars)))
        yield CapturedShopInputs(
            snapshot, snapshot / "darkan/shops", destinations["game-main/data/cfg/items.yml"],
            snapshot / "darkan/cache", classpath[0], classpath[1:], digests,
        )


def _raw_item_id(raw_item: dict[str, Any]) -> int:
    raw_item_ref = raw_item.get("item", -1)
    if isinstance(raw_item_ref, dict):
        return int(raw_item_ref.get("id", -1) or -1)
    return int(raw_item_ref)


def collect_source_shop_item_ids(darkan_shops: Path) -> set[int]:
    item_ids: set[int] = set()
    for path in sorted(darkan_shops.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        for raw_item in raw.get("items", []):
            if isinstance(raw_item, dict):
                item_id = _raw_item_id(raw_item)
                if item_id >= 0:
                    item_ids.add(item_id)
    return item_ids


def _java_tool(java_home: Path, name: str) -> str:
    tool_path = java_home / "bin" / name
    return str(tool_path if tool_path.exists() else name)


def _darkan_cache_arg(cache_path: Path) -> str:
    raw = str(cache_path)
    return raw if raw.endswith(os.sep) else raw + os.sep


def load_darkan_shop_price_inputs(
    cache_path: Path,
    item_ids: Iterable[int],
    *,
    core_jar: Path,
    dependency_jars: Iterable[Path],
    java_home: Path,
) -> dict[int, dict[str, Any]]:
    ids = sorted({int(item_id) for item_id in item_ids if int(item_id) >= 0})
    if not ids:
        return {}
    required_paths = [cache_path, core_jar, DARKAN_PRICE_HELPER, *dependency_jars]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Darkan price extraction input(s): " + ", ".join(missing))

    classpath = os.pathsep.join(str(path) for path in [core_jar, *dependency_jars])
    with tempfile.TemporaryDirectory(prefix="ankiscape-shop-prices-") as temp_dir:
        temp = Path(temp_dir)
        class_dir = temp / "classes"
        class_dir.mkdir()
        ids_path = temp / "item_ids.txt"
        output_path = temp / "prices.json"
        ids_path.write_text("\n".join(str(item_id) for item_id in ids) + "\n", encoding="utf-8")

        try:
            subprocess.run(
                [
                    _java_tool(java_home, "javac"),
                    "-cp",
                    classpath,
                    "-d",
                    str(class_dir),
                    str(DARKAN_PRICE_HELPER),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    _java_tool(java_home, "java"),
                    "-cp",
                    os.pathsep.join([str(class_dir), classpath]),
                    "DumpDarkanShopPriceInputs",
                    _darkan_cache_arg(cache_path),
                    str(ids_path),
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or str(exc)).strip()
            raise RuntimeError(f"Darkan shop price extraction failed: {detail}") from exc

        parsed = json.loads(output_path.read_text(encoding="utf-8"))
    rows = parsed.get("items", {})
    return {int(item_id): dict(row) for item_id, row in rows.items() if isinstance(row, dict)}

