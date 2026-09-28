#!/usr/bin/env python3
"""Generate source-backed AnkiScape Smithing data from local 2011Scape files."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple


ADDON_ROOT = Path(__file__).resolve().parents[1]
if str(ADDON_ROOT) not in sys.path:
    sys.path.insert(0, str(ADDON_ROOT))
from tools.generation.outputs import write_or_check
from tools.generation.source_digests import check_source_digests, save_source_digests, source_digest_manifest

SOURCE_DIGESTS = ADDON_ROOT / "generated" / "source_digests.json"
OUTPUT_NAME = "data/smithing_data.py"


DEFAULT_GAME_ROOT = Path("/Users/ArmanTarkhanian1/Downloads/game-main")
SMITHING_RELATIVE = Path("game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/smithing/data")
ITEMS_KT_RELATIVE = Path("game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt")
ITEMS_YML_RELATIVE = Path("data/cfg/items.yml")
DRAGON_SQ_SHIELD_PLUGIN_RELATIVE = Path(
    "game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/armor/dragon_sq_shield.plugin.kts"
)
CANNONBALL_WIKI_SOURCE = "https://runescape.wiki/w/Cannonball?oldid=6541276"


@dataclass(frozen=True)
class ItemMeta:
    item_id: int
    name: str
    tradeable: bool


@dataclass(frozen=True)
class SourceRecipe:
    recipe_id: str
    display_name: str
    station: str
    level: int
    exp: float
    requirements: Tuple[Tuple[str, int], ...]
    output_item: str
    output_qty: int
    source_item_id: int
    source: str
    source_enum: str
    tradeable: bool
    category: str
    bar_tier: Optional[str] = None
    smithing_type: Optional[str] = None
    bars_required: int = 0
    produced_amount: int = 1
    required_items: Tuple[Tuple[str, int], ...] = ()


def _slug(value: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", value.lower()))


def _split_top_level(raw: str) -> List[str]:
    parts: List[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(raw):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            part = raw[start:index].strip()
            if part:
                parts.append(part)
            start = index + 1
    tail = raw[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _enum_entries(text: str) -> Iterator[Tuple[str, str]]:
    body = text.split("companion object", 1)[0]
    for match in re.finditer(r"\n\s*([A-Z][A-Z0-9_]*)\s*\(", body):
        name = match.group(1)
        open_index = match.end() - 1
        depth = 0
        close_index = open_index
        for index in range(open_index, len(body)):
            char = body[index]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    close_index = index
                    break
        yield name, body[open_index + 1 : close_index]


def _named_args(raw: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for part in _split_top_level(raw):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _parse_items_constants(text: str) -> Dict[str, int]:
    constants: Dict[str, int] = {}
    for name, value in re.findall(r"const val ([A-Z0-9_]+) = (\d+)", text):
        constants[name] = int(value)
    return constants


def _parse_items_yml(text: str) -> Dict[int, ItemMeta]:
    items: Dict[int, ItemMeta] = {}
    current_id: Optional[int] = None
    current_name: Optional[str] = None
    current_tradeable = True

    def flush() -> None:
        nonlocal current_id, current_name, current_tradeable
        if current_id is not None and current_name is not None:
            items[current_id] = ItemMeta(current_id, current_name, current_tradeable)
        current_id = None
        current_name = None
        current_tradeable = True

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- id:"):
            flush()
            current_id = int(line.split(":", 1)[1].strip())
        elif line.startswith("name:"):
            current_name = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("tradeable:"):
            current_tradeable = line.split(":", 1)[1].strip().lower() == "true"
    flush()
    return items


def _resolve_item_id(value: str, item_constants: Mapping[str, int]) -> int:
    value = value.strip()
    if value.startswith("Items."):
        key = value.split(".", 1)[1]
        return item_constants[key]
    return int(value)


def _item_name(item_id: int, items: Mapping[int, ItemMeta]) -> str:
    if item_id == 4544:
        return "Bullseye lantern (unf)"
    try:
        return items[item_id].name
    except KeyError as exc:
        raise KeyError(f"No item metadata for id {item_id}") from exc


def _item_tradeable(item_id: int, items: Mapping[int, ItemMeta]) -> bool:
    return items.get(item_id, ItemMeta(item_id, f"item_{item_id}", True)).tradeable


def _parse_bar_types(text: str, item_constants: Mapping[str, int]) -> Dict[str, Dict[str, object]]:
    bars: Dict[str, Dict[str, object]] = {}
    for name, args in _enum_entries(text):
        values = _named_args(args)
        bars[name] = {
            "item_id": _resolve_item_id(values["item"], item_constants),
            "exp": float(values["experience"]),
            "level": int(values["levelRequired"]),
        }
    return bars


def _parse_smithing_types(text: str) -> Dict[str, Dict[str, int]]:
    types: Dict[str, Dict[str, int]] = {}
    for name, args in _enum_entries(text):
        values = _named_args(args)
        types[name] = {
            "bars_required": int(values["barRequirement"]),
            "produced_amount": int(values["producedAmount"]),
        }
    return types


def _parse_smelting(
    path: Path,
    text: str,
    item_constants: Mapping[str, int],
    items: Mapping[int, ItemMeta],
) -> Tuple[SourceRecipe, ...]:
    recipes: List[SourceRecipe] = []
    for enum_name, args in _enum_entries(text):
        values = _named_args(args)
        product_id = _resolve_item_id(values["product"], item_constants)
        primary_id = _resolve_item_id(values["primaryOre"], item_constants)
        secondary_id = _resolve_item_id(values.get("secondaryOre", "Items.COAL"), item_constants)
        secondary_count = int(values.get("secondaryCount", "1"))
        product_name = _item_name(product_id, items)
        requirements: List[Tuple[str, int]] = [(_item_name(primary_id, items), 1)]
        if secondary_count > 0:
            requirements.append((_item_name(secondary_id, items), secondary_count))
        recipes.append(
            SourceRecipe(
                recipe_id=f"smelt_{_slug(product_name)}",
                display_name=product_name,
                station="furnace",
                level=int(values["levelRequired"]),
                exp=float(values["experience"]),
                requirements=tuple(requirements),
                output_item=product_name,
                output_qty=1,
                source_item_id=product_id,
                source=str(path),
                source_enum=enum_name,
                tradeable=_item_tradeable(product_id, items),
                category="bar",
            )
        )
    return tuple(recipes)


def _parse_products(
    path: Path,
    text: str,
    bar_types: Mapping[str, Mapping[str, object]],
    smithing_types: Mapping[str, Mapping[str, int]],
    item_constants: Mapping[str, int],
    items: Mapping[int, ItemMeta],
) -> Tuple[SourceRecipe, ...]:
    recipes: List[SourceRecipe] = []
    for enum_name, args in _enum_entries(text):
        values = _named_args(args)
        if values:
            bar_type = values["barType"].split(".")[-1]
            smithing_type = values["smithingType"].split(".")[-1]
            result_id = _resolve_item_id(values["result"], item_constants)
            level = int(values["level"])
        else:
            positional = _split_top_level(args)
            bar_type = positional[0].split(".")[-1]
            smithing_type = positional[1].split(".")[-1]
            result_id = _resolve_item_id(positional[2], item_constants)
            level = int(positional[3])

        type_spec = smithing_types[smithing_type]
        bar_item_id = int(bar_types[bar_type]["item_id"])
        bar_name = _item_name(bar_item_id, items)
        result_name = _item_name(result_id, items)
        bars_required = int(type_spec["bars_required"])
        category = "tool" if smithing_type in {"TYPE_HATCHET", "TYPE_PICKAXE"} else "smithed"
        recipes.append(
            SourceRecipe(
                recipe_id="forge_bullseye_lantern" if result_id == 4544 else f"forge_{_slug(result_name)}",
                display_name=result_name,
                station="anvil",
                level=level,
                exp=float(bar_types[bar_type]["exp"]) * bars_required,
                requirements=((bar_name, bars_required),),
                output_item=result_name,
                output_qty=int(type_spec["produced_amount"]),
                source_item_id=result_id,
                source=str(path),
                source_enum=enum_name,
                tradeable=_item_tradeable(result_id, items),
                category=category,
                bar_tier=bar_type.lower(),
                smithing_type=smithing_type,
                bars_required=bars_required,
                produced_amount=int(type_spec["produced_amount"]),
            )
        )
    return tuple(recipes)


def _dragon_sq_shield_repair_recipe(
    source_path: Path,
    item_constants: Mapping[str, int],
    items: Mapping[int, ItemMeta],
) -> SourceRecipe:
    """Return the explicit anvil assembly bound by the live shield plugin."""
    left_half_id = item_constants["SHIELD_LEFT_HALF"]
    right_half_id = item_constants["SHIELD_RIGHT_HALF"]
    shield_id = item_constants["DRAGON_SQ_SHIELD"]
    return SourceRecipe(
        recipe_id="repair_dragon_sq_shield",
        display_name=_item_name(shield_id, items),
        station="anvil",
        level=60,
        exp=70.0,
        requirements=(
            (_item_name(left_half_id, items), 1),
            (_item_name(right_half_id, items), 1),
        ),
        output_item=_item_name(shield_id, items),
        output_qty=1,
        source_item_id=shield_id,
        source=str(source_path),
        source_enum="DRAGON_SQ_SHIELD",
        tradeable=_item_tradeable(shield_id, items),
        category="smithed",
    )


def _cannonball_recipe(
    item_constants: Mapping[str, int],
    items: Mapping[int, ItemMeta],
) -> SourceRecipe:
    cannonball_id = item_constants["CANNONBALL"]
    return SourceRecipe(
        recipe_id="forge_cannonballs",
        display_name="Cannonballs",
        station="furnace_process",
        level=35,
        exp=25.6,
        requirements=((_item_name(item_constants["STEEL_BAR"], items), 1),),
        output_item=_item_name(cannonball_id, items),
        output_qty=4,
        source_item_id=cannonball_id,
        source=CANNONBALL_WIKI_SOURCE,
        source_enum="CANNONBALL",
        tradeable=_item_tradeable(cannonball_id, items),
        category="ammunition",
        bar_tier="steel",
        bars_required=1,
        produced_amount=4,
        required_items=((_item_name(item_constants["AMMO_MOULD"], items), 1),),
    )


def _format_tuple(values: Sequence[str], indent: str = "    ") -> str:
    if not values:
        return "()"
    return "(\n" + "".join(f"{indent}{value},\n" for value in values) + ")"


def _recipe_repr(recipe: SourceRecipe) -> str:
    requirements = _format_tuple(
        [f"({material!r}, {amount})" for material, amount in recipe.requirements],
        "            ",
    )
    required_items = _format_tuple(
        [f"({material!r}, {amount})" for material, amount in recipe.required_items],
        "            ",
    )
    required_items_line = f"        required_items={required_items},\n" if recipe.required_items else ""
    return (
        "SmithingRecipe(\n"
        f"        id={recipe.recipe_id!r},\n"
        f"        display_name={recipe.display_name!r},\n"
        f"        station={recipe.station!r},\n"
        f"        level={recipe.level},\n"
        f"        base_exp={recipe.exp!r},\n"
        f"        requirements={requirements},\n"
        f"        output_item={recipe.output_item!r},\n"
        f"        output_qty={recipe.output_qty},\n"
        f"        source_item_id={recipe.source_item_id},\n"
        f"        source={recipe.source!r},\n"
        f"        source_enum={recipe.source_enum!r},\n"
        f"        tradeable={recipe.tradeable!r},\n"
        f"        category={recipe.category!r},\n"
        f"        bar_tier={recipe.bar_tier!r},\n"
        f"        smithing_type={recipe.smithing_type!r},\n"
        f"        bars_required={recipe.bars_required},\n"
        f"        produced_amount={recipe.produced_amount},\n"
        f"{required_items_line}"
        "    )"
    )


def _render_module(recipes: Sequence[SourceRecipe]) -> str:
    smelt_recipes = [recipe for recipe in recipes if recipe.station == "furnace"]
    recipe_rows = ",\n".join(_recipe_repr(recipe) for recipe in recipes)
    legacy_targets = {recipe.output_item: recipe.recipe_id for recipe in smelt_recipes}
    if "Adamant bar" in legacy_targets:
        legacy_targets["Adamantite bar"] = legacy_targets["Adamant bar"]
    if "Rune bar" in legacy_targets:
        legacy_targets["Runite bar"] = legacy_targets["Rune bar"]
    legacy_storage = {}
    if "Adamant bar" in legacy_targets:
        legacy_storage["Adamantite bar"] = "Adamant bar"
    if "Rune bar" in legacy_targets:
        legacy_storage["Runite bar"] = "Rune bar"

    return f'''"""2011Scape-sourced Smithing data for AnkiScape.

This module is generated by ``tools/generate_smithing_data.py`` from the local
2011Scape rev 667 Smithing plugin. Runtime imports only this checked-in Python
data; the emulator checkout is a development-time source audit input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


SMELTING_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/smithing/data/SmeltingData.kt"
)
BAR_TYPE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/smithing/data/BarType.kt"
)
SMITHING_TYPE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/smithing/data/SmithingType.kt"
)
BAR_PRODUCTS_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/smithing/data/BarProducts.kt"
)
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"


@dataclass(frozen=True)
class SmithingRecipe:
    id: str
    display_name: str
    station: str
    level: int
    base_exp: float
    requirements: Tuple[Tuple[str, int], ...]
    output_item: str
    output_qty: int
    source_item_id: int
    source: str
    source_enum: str
    tradeable: bool = True
    category: str = "smithed"
    bar_tier: Optional[str] = None
    smithing_type: Optional[str] = None
    bars_required: int = 0
    produced_amount: int = 1
    required_items: Tuple[Tuple[str, int], ...] = ()


SMITHING_RECIPES: Tuple[SmithingRecipe, ...] = (
    {recipe_rows}
)

SMITHING_RECIPES_BY_ID: Dict[str, SmithingRecipe] = {{recipe.id: recipe for recipe in SMITHING_RECIPES}}
DEFAULT_SMITHING_TARGET = "smelt_bronze_bar"
LEGACY_SMITHING_TARGETS: Mapping[str, str] = {legacy_targets!r}
LEGACY_BAR_STORAGE_MIGRATIONS: Mapping[str, str] = {legacy_storage!r}


def smithing_recipes_as_dict() -> Dict[str, Dict[str, object]]:
    return {{
        recipe.id: {{
            "display_name": recipe.display_name,
            "station": recipe.station,
            "level": recipe.level,
            "exp": recipe.base_exp,
            "requirements": dict(recipe.requirements),
            "output_item": recipe.output_item,
            "output_qty": recipe.output_qty,
            "source_item_id": recipe.source_item_id,
            "source": recipe.source,
            "source_enum": recipe.source_enum,
            "tradeable": recipe.tradeable,
            "category": recipe.category,
            "bar_tier": recipe.bar_tier,
            "smithing_type": recipe.smithing_type,
            "bars_required": recipe.bars_required,
            "produced_amount": recipe.produced_amount,
            "required_items": dict(recipe.required_items),
        }}
        for recipe in SMITHING_RECIPES
    }}


def smithing_bars_as_dict() -> Dict[str, Dict[str, object]]:
    bars: Dict[str, Dict[str, object]] = {{}}
    for recipe in SMITHING_RECIPES:
        if recipe.station != "furnace":
            continue
        requirements = dict(recipe.requirements)
        bars[recipe.output_item] = {{
            "display_name": recipe.display_name,
            "level": recipe.level,
            "exp": recipe.base_exp,
            "requirements": requirements,
            "ore_required": requirements,
            "output_item": recipe.output_item,
            "output_qty": recipe.output_qty,
            "source_item_id": recipe.source_item_id,
            "source": recipe.source,
            "source_enum": recipe.source_enum,
            "tradeable": recipe.tradeable,
        }}
    return bars


def smithing_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    items: Dict[str, Dict[str, object]] = {{}}
    for recipe in SMITHING_RECIPES:
        if recipe.station == "furnace":
            continue
        items[recipe.output_item] = {{
            "category": recipe.category,
            "level": recipe.level,
            "exp": recipe.base_exp,
            "source": recipe.source,
            "item_id": recipe.source_item_id,
            "tradeable": recipe.tradeable,
        }}
    return items


def smithing_output_items() -> Tuple[str, ...]:
    seen: Dict[str, None] = {{}}
    for recipe in SMITHING_RECIPES:
        seen.setdefault(recipe.output_item, None)
    return tuple(seen)


def smithing_smelt_recipe_ids() -> Tuple[str, ...]:
    return tuple(recipe.id for recipe in SMITHING_RECIPES if recipe.station == "furnace")


def smithing_forge_recipe_ids() -> Tuple[str, ...]:
    return tuple(recipe.id for recipe in SMITHING_RECIPES if recipe.station == "anvil")
'''


def generate(
    game_root: Path,
    output_path: Path,
    *,
    provenance_root: Optional[Path] = None,
    accept_source_change: bool = False,
    digest_manifest: Path = SOURCE_DIGESTS,
    check: bool = False,
) -> int:
    if provenance_root is None:
        provenance_root = game_root
    smithing_path = game_root / SMITHING_RELATIVE
    sources = [game_root / path for path in (
        ITEMS_KT_RELATIVE,
        ITEMS_YML_RELATIVE,
        SMITHING_RELATIVE / "BarType.kt",
        SMITHING_RELATIVE / "SmithingType.kt",
        SMITHING_RELATIVE / "SmeltingData.kt",
        SMITHING_RELATIVE / "BarProducts.kt",
        DRAGON_SQ_SHIELD_PLUGIN_RELATIVE,
    )]
    source_bytes = {path: path.read_bytes() for path in sources}
    digests = check_source_digests(
        digest_manifest, OUTPUT_NAME, source_bytes, source_root=game_root,
        accept_source_change=accept_source_change,
    )
    texts = {path: content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
             for path, content in source_bytes.items()}
    item_constants = _parse_items_constants(texts[game_root / ITEMS_KT_RELATIVE])
    items = _parse_items_yml(texts[game_root / ITEMS_YML_RELATIVE])
    bar_types = _parse_bar_types(texts[smithing_path / "BarType.kt"], item_constants)
    smithing_types = _parse_smithing_types(texts[smithing_path / "SmithingType.kt"])
    smelting = _parse_smelting(smithing_path / "SmeltingData.kt", texts[smithing_path / "SmeltingData.kt"], item_constants, items)
    products = _parse_products(smithing_path / "BarProducts.kt", texts[smithing_path / "BarProducts.kt"],
                               bar_types, smithing_types, item_constants, items)
    dragon_sq_shield_repair = _dragon_sq_shield_repair_recipe(
        game_root / DRAGON_SQ_SHIELD_PLUGIN_RELATIVE,
        item_constants,
        items,
    )
    cannonballs = _cannonball_recipe(item_constants, items)
    rendered = _render_module(
        tuple(smelting) + tuple(products) + (dragon_sq_shield_repair, cannonballs)
    )
    if game_root != provenance_root:
        rendered = rendered.replace(str(game_root), str(provenance_root))
    if check:
        return write_or_check(
            {output_path: rendered, digest_manifest: source_digest_manifest(digest_manifest, OUTPUT_NAME, digests)},
            check=True,
        )
    write_or_check({output_path: rendered}, check=False)
    save_source_digests(digest_manifest, OUTPUT_NAME, digests)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path)
    parser.add_argument("--output", type=Path, default=ADDON_ROOT / "data" / "smithing_data.py")
    parser.add_argument("--accept-source-change", action="store_true")
    parser.add_argument("--digest-manifest", type=Path, default=SOURCE_DIGESTS)
    parser.add_argument("--check", action="store_true", help="compare with the existing files instead of writing")
    args = parser.parse_args(argv)
    if args.game_root is None:
        game_root = Path(os.environ.get("ANKISCAPE_GAME_MAIN", DEFAULT_GAME_ROOT))
        provenance_root = DEFAULT_GAME_ROOT
    else:
        game_root = args.game_root
        provenance_root = args.game_root
    return generate(
        game_root, args.output, provenance_root=provenance_root,
        accept_source_change=args.accept_source_change, digest_manifest=args.digest_manifest,
        check=args.check,
    )


if __name__ == "__main__":
    raise SystemExit(main())
