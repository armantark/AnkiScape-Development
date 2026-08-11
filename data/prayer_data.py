"""Pre-EOC Prayer training, prayer-book, and curse data.

Runtime code imports only this checked-in module.  Emulator checkouts and pinned
wiki revisions are development-time evidence and are never runtime dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple


GAME_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main"
PRAYER_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/prayer/prayer.kt"
PRAYER_MECHANICS_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/prayer/Prayers.kt"
BONE_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/prayer/burying/BoneData.kt"
ASH_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/prayer/scattering/AshData.kt"
MELEE_FORMULA_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt"
RANGED_FORMULA_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/RangedCombatFormula.kt"
MAGIC_FORMULA_SOURCE = f"{GAME_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MagicCombatFormula.kt"
DARKAN_ROOT = "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
SAP_SOURCE = f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/skills/prayer/Sap.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
LEECH_SOURCE = f"{DARKAN_ROOT}/src/main/java/com/rs/game/content/skills/prayer/Leech.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
CURSE_MANAGER_SOURCE = f"{DARKAN_ROOT}/src/main/java/com/rs/game/model/entity/player/managers/CurseManager.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
PRAYER_MANAGER_SOURCE = f"{DARKAN_ROOT}/src/main/java/com/rs/game/model/entity/player/managers/PrayerManager.kt @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
DEFLECT_SOURCE = f"{DARKAN_ROOT}/src/main/java/com/rs/game/model/entity/player/Player.java:2140-2146 @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
ANCIENT_CURSES_SOURCE = "RuneScape Wiki Ancient Curses oldid=6535713 (2012-11-05)"
IMPIOUS_ASHES_SOURCE = "RuneScape Wiki Impious ashes oldid=6105641 (2012-08-18)"
ACCURSED_ASHES_SOURCE = "RuneScape Wiki Accursed ashes oldid=6105640 (2012-08-18)"
INFERNAL_ASHES_SOURCE = "RuneScape Wiki Infernal ashes oldid=6529055 (2012-11-03)"
ECTOFUNTUS_SOURCE = "RuneScape Wiki Ectofuntus oldid=6544994 (2012-11-09)"
CHIVALRY_SOURCE = "RuneScape Wiki Chivalry oldid=6268775 (2012-09-19)"
PIETY_SOURCE = "RuneScape Wiki Piety oldid=6268774 (2012-09-19)"
RAPID_RENEWAL_SOURCE = "RuneScape Wiki Rapid Renewal oldid=6268753 (2012-09-19)"
RAPID_RESTORE_SOURCE = "RuneScape Wiki Rapid Restore oldid=6268755 (2012-09-19)"
REDEMPTION_SOURCE = "RuneScape Wiki Redemption oldid=6292830 (2012-09-24)"

DEFAULT_PRAYER_TARGET = "bury_bones"
PRAYER_GROUP_ORDER = ("Bury", "Scatter", "Ectofuntus", "Gilded altar")
PRAYER_UI_METHOD_ORDER = ("base", "ectofuntus", "gilded_hosted", "gilded_owned")
PRAYER_UPTIME_POLICIES = {"off": 0.0, "40": 0.4, "70": 0.7, "100": 1.0}
GRIND_BONES_BATCH_SIZE = 9
COLLECT_SLIME_BATCH_SIZE = 28
ECTOFUNTUS_MULTIPLIER = 4.0
ECTOFUNTUS_TOKEN_REWARD = 5
GILDED_ALTAR_MULTIPLIER = 3.5
AUTO_PRAYER_TICKS_PER_ITEM = 2  # Source burial action waits two game ticks per item.


@dataclass(frozen=True)
class PrayerMaterial:
    id: str
    item_name: str
    xp: float
    kind: str
    bonemeal_item: Optional[str]
    source: str


_BONES = (
    ("bones", "Bones", 4.5), ("wolf_bones", "Wolf bones", 4.5),
    ("burnt_bones", "Burnt bones", 4.5), ("monkey_bones", "Monkey bones", 5.0),
    ("bat_bones", "Bat bones", 5.3), ("zogre_bones", "Zogre bones", 12.5),
    ("big_bones", "Big bones", 15.0), ("jogre_bones", "Jogre bones", 15.0),
    ("shaikahan_bones", "Shaikahan bones", 25.0),
    ("baby_dragon_bones", "Baby dragon bones", 30.0),
    ("wyvern_bones", "Wyvern bones", 50.0), ("dragon_bones", "Dragon bones", 72.0),
    ("fayrg_bones", "Fayrg bones", 84.0), ("raurg_bones", "Raurg bones", 96.0),
    ("dagannoth_bones", "Dagannoth bones", 125.0), ("ourg_bones", "Ourg bones", 140.0),
    ("frost_dragon_bones", "Frost dragon bones", 180.0),
    ("ancient_bones", "Ancient bones", 200.0),
)


def _bonemeal_name(item_name: str) -> str:
    return "Bonemeal" if item_name == "Bones" else item_name.removesuffix(" bones") + " bonemeal"


PRAYER_MATERIALS: Tuple[PrayerMaterial, ...] = tuple(
    PrayerMaterial(
        material_id,
        item_name,
        xp,
        "bone",
        None if material_id == "ancient_bones" else _bonemeal_name(item_name),
        f"{BONE_SOURCE}: {material_id.upper()}",
    )
    for material_id, item_name, xp in _BONES
) + (
    PrayerMaterial("impious_ashes", "Impious ashes", 4.0, "ash", None, IMPIOUS_ASHES_SOURCE),
    PrayerMaterial("accursed_ashes", "Accursed ashes", 12.5, "ash", None, ACCURSED_ASHES_SOURCE),
    PrayerMaterial("infernal_ashes", "Infernal ashes", 62.5, "ash", None, INFERNAL_ASHES_SOURCE),
)
PRAYER_MATERIALS_BY_ID = {material.id: material for material in PRAYER_MATERIALS}

# Pinned 100%-drop families. Combat only wires members already present in its
# target catalog; this audit table prevents modern/OSRS family expansion.
ASH_100_PERCENT_DROPPERS = {
    "Impious ashes": {
        "droppers": ("Imp", "Icefiend", "Killerwatt", "Pyrefiend"),
        "source": IMPIOUS_ASHES_SOURCE,
    },
    "Accursed ashes": {
        "droppers": ("Lesser demon", "Greater demon", "Death spawn", "Fungal mage", "Evil spirit"),
        "source": ACCURSED_ASHES_SOURCE,
    },
    "Infernal ashes": {
        "droppers": ("Black demon", "Abyssal demon", "Tormented demon", "Nechryael", "Demon bosses"),
        "source": INFERNAL_ASHES_SOURCE,
    },
}


def prayer_targets_as_dict() -> Dict[str, dict]:
    targets: Dict[str, dict] = {}
    for material in PRAYER_MATERIALS:
        base_method = "bury" if material.kind == "bone" else "scatter"
        base_group = "Bury" if material.kind == "bone" else "Scatter"
        targets[f"{base_method}_{material.id}"] = {
            "id": f"{base_method}_{material.id}", "display_name": material.item_name,
            "material_id": material.id, "material_kind": material.kind,
            "method": base_method, "group": base_group, "level": 1,
            "requirements": {material.item_name: 1}, "byproducts": {},
            "exp": material.xp, "source": material.source,
        }
        if material.kind == "ash" or material.bonemeal_item:
            ecto_input = material.bonemeal_item or material.item_name
            byproducts = {"Bucket": 1}
            if material.bonemeal_item:
                byproducts["Empty pot"] = 1
            targets[f"ectofuntus_{material.id}"] = {
                "id": f"ectofuntus_{material.id}", "display_name": material.item_name,
                "material_id": material.id, "material_kind": material.kind,
                "method": "ectofuntus", "group": "Ectofuntus", "level": 1,
                "requirements": {ecto_input: 1, "Bucket of slime": 1},
                "byproducts": byproducts, "outputs": {"Ecto-token": ECTOFUNTUS_TOKEN_REWARD},
                "exp": material.xp * ECTOFUNTUS_MULTIPLIER,
                "source": f"{material.source}; {ECTOFUNTUS_SOURCE}: 4x XP and 5 tokens/worship",
            }
        if material.id != "ancient_bones":
            targets[f"gilded_altar_{material.id}"] = {
                "id": f"gilded_altar_{material.id}", "display_name": material.item_name,
                "material_id": material.id, "material_kind": material.kind,
                "method": "gilded_altar", "group": "Gilded altar", "level": 1,
                "requirements": {material.item_name: 1}, "byproducts": {},
                "base_exp": material.xp, "exp": material.xp * GILDED_ALTAR_MULTIPLIER,
                "source": f"{material.source}; RuneScape Wiki Prayer oldid=6539264: lit gilded altar 3.5x",
            }
    return targets


PRAYER_TARGETS = prayer_targets_as_dict()


def resolve_prayer_selection_pure(material_id: str, ui_method_id: str) -> Optional[Tuple[str, Optional[str]]]:
    material = PRAYER_MATERIALS_BY_ID.get(material_id)
    if material is None:
        return None
    if ui_method_id == "base":
        method = "bury" if material.kind == "bone" else "scatter"
        target_id = f"{method}_{material.id}"
        mode = None
    elif ui_method_id == "ectofuntus":
        target_id = f"ectofuntus_{material.id}"
        mode = None
    elif ui_method_id in {"gilded_hosted", "gilded_owned"}:
        target_id = f"gilded_altar_{material.id}"
        mode = "owned" if ui_method_id == "gilded_owned" else "hosted"
    else:
        return None
    return (target_id, mode) if target_id in PRAYER_TARGETS else None


def prayer_selection_from_target_pure(target_id: str, gilded_mode: str = "hosted") -> Optional[Tuple[str, str]]:
    spec = PRAYER_TARGETS.get(target_id)
    if spec is None:
        return None
    material_id = str(spec["material_id"])
    method = spec.get("method")
    if method in {"bury", "scatter"}:
        return material_id, "base"
    if method == "ectofuntus":
        return material_id, "ectofuntus"
    if method == "gilded_altar":
        return material_id, "gilded_owned" if gilded_mode == "owned" else "gilded_hosted"
    return None


def prayer_utility_activities_as_dict() -> Dict[str, dict]:
    rows: Dict[str, dict] = {
        "collect_ectofuntus_slime": {
            "display_name": "Collect Ectofuntus slime", "requirements": {"Bucket": 1},
            "output_item": "Bucket of slime", "output_qty": 1,
            "batch_size": COLLECT_SLIME_BATCH_SIZE, "group": "prayer_preparation",
            "source": f"{ECTOFUNTUS_SOURCE}; AnkiScape pacing knob: 28 buckets/review",
        }
    }
    for material in PRAYER_MATERIALS:
        if material.kind != "bone" or not material.bonemeal_item:
            continue
        rows[f"grind_prayer_{material.id}"] = {
            "display_name": f"Grind {material.item_name.lower()}",
            "requirements": {material.item_name: 1, "Empty pot": 1},
            "output_item": material.bonemeal_item, "output_qty": 1,
            "batch_size": GRIND_BONES_BATCH_SIZE, "group": "prayer_preparation",
            "source": f"{material.source}; {ECTOFUNTUS_SOURCE}; AnkiScape pacing knob: 9/review",
        }
    return rows


def prayer_extra_items_as_dict() -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    for material in PRAYER_MATERIALS:
        material_item = {"category": "material", "source": material.source, "exp": material.xp}
        if material.item_name == "Wyvern bones":
            material_item.update({"item_id": 6812, "noted_item_id": 6816})
            material_item["source"] += "; cache rev 742 items 6812/6816; Wyvern bones oldid=6105610"
        items[material.item_name] = material_item
        if material.bonemeal_item:
            bonemeal = {"category": "material", "source": f"{material.source}; {ECTOFUNTUS_SOURCE}"}
            if material.bonemeal_item == "Bonemeal":
                bonemeal["item_id"] = 4255
            elif material.bonemeal_item == "Wyvern bonemeal":
                bonemeal["item_id"] = 6810
            items[material.bonemeal_item] = bonemeal
    for name in ("Bucket", "Bucket of slime", "Empty pot", "Ecto-token"):
        items[name] = {"category": "material", "source": ECTOFUNTUS_SOURCE}
    return items


@dataclass(frozen=True)
class CombatPrayer:
    id: str
    display_name: str
    book: str
    level: int
    drain: float
    groups: Tuple[str, ...]
    effects: Tuple[Tuple[str, float], ...]
    source: str
    quest_gate: Optional[str] = None
    conflicts: Tuple[str, ...] = ()
    defence_level: int = 1


def _p(pid, name, level, drain_effect, groups=(), effects=(), gate=None, conflicts=(), defence_level=1):
    sources = [f"{PRAYER_SOURCE}: {pid.upper()}"]
    effect_names = {effect for effect, _value in effects}
    if effect_names.intersection({"attack", "strength", "defence"}):
        sources.append(MELEE_FORMULA_SOURCE)
    if any(effect.startswith("ranged") for effect in effect_names):
        sources.append(RANGED_FORMULA_SOURCE)
    if "magic" in effect_names:
        sources.append(MAGIC_FORMULA_SOURCE)
    if pid == "rapid_restore":
        sources.append(RAPID_RESTORE_SOURCE)
    if pid == "redemption":
        sources.append(REDEMPTION_SOURCE)
    if pid == "rapid_renewal":
        sources.append(RAPID_RENEWAL_SOURCE)
    if pid == "chivalry":
        sources.append(CHIVALRY_SOURCE)
    if pid == "piety":
        sources.append(PIETY_SOURCE)
    return CombatPrayer(
        pid,
        name,
        "standard",
        level,
        float(drain_effect),
        tuple(groups),
        tuple(effects),
        "; ".join(sources),
        gate,
        tuple(conflicts),
        int(defence_level),
    )


STANDARD_PRAYERS: Tuple[CombatPrayer, ...] = (
    _p("thick_skin", "Thick Skin", 1, 30, ("defence",), (("defence", 1.05),), conflicts=("melee_combat",)),
    _p("burst_of_strength", "Burst of Strength", 4, 30, ("strength",), (("strength", 1.05),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("clarity_of_thought", "Clarity of Thought", 7, 30, ("attack",), (("attack", 1.05),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("sharp_eye", "Sharp Eye", 8, 30, ("ranged_combat",), (("ranged", 1.05),), conflicts=("attack", "strength", "magic_combat", "melee_combat")),
    _p("mystic_will", "Mystic Will", 9, 30, ("magic_combat",), (("magic", 1.05),), conflicts=("attack", "strength", "ranged_combat", "melee_combat")),
    _p("rock_skin", "Rock Skin", 10, 60, ("defence",), (("defence", 1.10),), conflicts=("melee_combat",)),
    _p("superhuman_strength", "Superhuman Strength", 13, 60, ("strength",), (("strength", 1.10),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("improved_reflexes", "Improved Reflexes", 16, 60, ("attack",), (("attack", 1.10),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("rapid_restore", "Rapid Restore", 19, 10, ("rapid_restore",), (("rapid_restore", 2.0),)),
    _p("rapid_heal", "Rapid Heal", 22, 20, ("rapid_heal",), (("rapid_heal", 2.0),), conflicts=("rapid_renewal",)),
    _p("protect_item", "Protect Item", 25, 20, (), (("protect_item", 1.0),)),
    _p("hawk_eye", "Hawk Eye", 26, 60, ("ranged_combat",), (("ranged", 1.10),), conflicts=("attack", "strength", "magic_combat", "melee_combat")),
    _p("mystic_lore", "Mystic Lore", 27, 60, ("magic_combat",), (("magic", 1.10),), conflicts=("attack", "strength", "ranged_combat", "melee_combat")),
    _p("steel_skin", "Steel Skin", 28, 120, ("defence",), (("defence", 1.15),), conflicts=("melee_combat",)),
    _p("ultimate_strength", "Ultimate Strength", 31, 120, ("strength",), (("strength", 1.15),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("incredible_reflexes", "Incredible Reflexes", 34, 120, ("attack",), (("attack", 1.15),), conflicts=("ranged_combat", "magic_combat", "melee_combat")),
    _p("protect_from_summoning", "Protect from Summoning", 35, 120, ("summoning_overhead",), (("protect_summoning", 1.0),), conflicts=("exclusive_overhead",)),
    _p("protect_from_magic", "Protect from Magic", 37, 120, ("protection_overhead",), (("protect_magic", 1.0),), conflicts=("exclusive_overhead",)),
    _p("protect_from_missiles", "Protect from Missiles", 40, 120, ("protection_overhead",), (("protect_ranged", 1.0),), conflicts=("exclusive_overhead",)),
    _p("protect_from_melee", "Protect from Melee", 43, 120, ("protection_overhead",), (("protect_melee", 1.0),), conflicts=("exclusive_overhead",)),
    _p("eagle_eye", "Eagle Eye", 44, 120, ("ranged_combat",), (("ranged", 1.15),), conflicts=("attack", "strength", "magic_combat", "melee_combat")),
    _p("mystic_might", "Mystic Might", 45, 120, ("magic_combat",), (("magic", 1.15),), conflicts=("attack", "strength", "ranged_combat", "melee_combat")),
    _p("retribution", "Retribution", 46, 30, ("exclusive_overhead",), (("retribution", 1.0),), conflicts=("protection_overhead", "summoning_overhead")),
    _p("redemption", "Redemption", 49, 60, ("exclusive_overhead",), (("redemption", 1.0),), conflicts=("protection_overhead", "summoning_overhead")),
    _p("smite", "Smite", 52, 180, ("exclusive_overhead",), (("smite", 1.0),), conflicts=("protection_overhead", "summoning_overhead")),
    _p(
        "chivalry",
        "Chivalry",
        60,
        240,
        ("melee_combat",),
        (("attack", 1.15), ("strength", 1.18), ("defence", 1.20)),
        "knight_waves",
        conflicts=("attack", "strength", "defence", "ranged_combat", "magic_combat"),
        defence_level=65,
    ),
    _p("rapid_renewal", "Rapid Renewal", 65, 230, ("rapid_renewal",), (("rapid_heal", 5.0),), conflicts=("rapid_heal",)),
    _p(
        "piety",
        "Piety",
        70,
        240,
        ("melee_combat",),
        (("attack", 1.20), ("strength", 1.23), ("defence", 1.25)),
        "knight_waves",
        conflicts=("attack", "strength", "defence", "ranged_combat", "magic_combat"),
        defence_level=70,
    ),
    _p("rigour", "Rigour", 74, 240, ("ranged_combat",), (("ranged_attack", 1.20), ("ranged_strength", 1.23), ("defence", 1.25)), conflicts=("attack", "strength", "defence", "magic_combat", "melee_combat"), defence_level=70),
    _p("augury", "Augury", 77, 240, ("magic_combat",), (("magic", 1.25), ("defence", 1.25)), conflicts=("attack", "strength", "defence", "ranged_combat", "melee_combat"), defence_level=70),
)


def _c(pid, name, level, seconds, groups=(), effects=(), conflicts=()):
    # At zero prayer bonus the 2011 counter resistance is 60.  The drain timer
    # fires every two 0.6-second game ticks, so 720/seconds counter units per
    # timer event reproduces the pinned wiki's displayed-point cadence while
    # retaining the authentic equipment-bonus resistance formula.
    sources = [ANCIENT_CURSES_SOURCE, PRAYER_MANAGER_SOURCE]
    if pid.startswith("sap_"):
        sources.extend((SAP_SOURCE, CURSE_MANAGER_SOURCE))
    if pid.startswith("leech_"):
        sources.extend((LEECH_SOURCE, CURSE_MANAGER_SOURCE))
    if pid.startswith("deflect_"):
        sources.append(DEFLECT_SOURCE)
    return CombatPrayer(
        pid,
        name,
        "curses",
        level,
        720.0 / seconds,
        tuple(groups),
        tuple(effects),
        "; ".join(sources),
        "the_temple_at_senntisten",
        tuple(conflicts),
    )


CURSES: Tuple[CombatPrayer, ...] = (
    _c("curse_protect_item", "Protect Item", 50, 1.8, (), (("protect_item", 1.0),)),
    _c("sap_warrior", "Sap Warrior", 50, .24, ("sap_warrior",), (("sap_warrior", 1.0),)),
    _c("sap_ranger", "Sap Ranger", 52, .24, ("sap_ranger",), (("sap_ranger", 1.0),)),
    _c("sap_mage", "Sap Mage", 54, .24, ("sap_mage",), (("sap_mage", 1.0),)),
    _c("sap_spirit", "Sap Spirit", 56, .24, ("sap_spirit",), (("sap_spirit", 1.0),)),
    _c("berserker", "Berserker", 59, 1.8, ("restoration",), (("berserker", 1.15),)),
    _c("deflect_summoning", "Deflect Summoning", 62, .3, ("summoning_overhead",), (("protect_summoning", 1.0),), conflicts=("exclusive_overhead",)),
    _c("deflect_magic", "Deflect Magic", 65, .3, ("protection_overhead",), (("protect_magic", 1.0), ("deflect", .06)), conflicts=("exclusive_overhead",)),
    _c("deflect_missiles", "Deflect Missiles", 68, .3, ("protection_overhead",), (("protect_ranged", 1.0), ("deflect", .06)), conflicts=("exclusive_overhead",)),
    _c("deflect_melee", "Deflect Melee", 71, .3, ("protection_overhead",), (("protect_melee", 1.0), ("deflect", .06)), conflicts=("exclusive_overhead",)),
    _c("leech_attack", "Leech Attack", 74, .36, ("leech_attack",), (("leech_attack", 1.0),)),
    _c("leech_ranged", "Leech Ranged", 76, .36, ("leech_ranged",), (("leech_ranged", 1.0),)),
    _c("leech_magic", "Leech Magic", 78, .36, ("leech_magic",), (("leech_magic", 1.0),)),
    _c("leech_defence", "Leech Defence", 80, .36, ("leech_defence",), (("leech_defence", 1.0),)),
    _c("leech_strength", "Leech Strength", 82, .36, ("leech_strength",), (("leech_strength", 1.0),)),
    _c("leech_energy", "Leech Energy", 84, .36, ("leech_energy",), (("leech_energy", 1.0),)),
    _c("leech_special_attack", "Leech Special Attack", 86, .36, ("leech_special_attack",), (("leech_special", 1.0),)),
    _c("wrath", "Wrath", 89, 1.2, ("exclusive_overhead",), (("wrath", 1.0),), conflicts=("protection_overhead", "summoning_overhead")),
    _c("soul_split", "Soul Split", 92, .2, ("exclusive_overhead",), (("soul_split", .20),), conflicts=("protection_overhead", "summoning_overhead")),
    _c("turmoil", "Turmoil", 95, .2, ("turmoil",), (("turmoil", 1.0),)),
)
COMBAT_PRAYERS = STANDARD_PRAYERS + CURSES
COMBAT_PRAYERS_BY_ID = {prayer.id: prayer for prayer in COMBAT_PRAYERS}


def combat_prayers_as_dict() -> Dict[str, dict]:
    return {prayer.id: asdict(prayer) for prayer in COMBAT_PRAYERS}
