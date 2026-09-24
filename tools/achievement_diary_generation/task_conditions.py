"""Translate harvested source tasks into diary conditions.

Holds every curated condition override and the rules that split a task's
conditions into the deed itself and its ordinary access gates.
"""

from __future__ import annotations

import re

from tools.achievement_diary_generation.condition_keys import (
    QUEST_DATA,
    _import_attr,
    resolve_condition_key,
)


# AchievementDef.toRealSkillId(), translated to AnkiScape skill ids.
_SKILL_TYPE_IDS = {
    1: "attack",
    2: "strength",
    3: "ranged",
    4: "magic",
    5: "defense",
    6: "constitution",
    7: "prayer",
    8: "agility",
    9: "herblore",
    10: "thieving",
    11: "crafting",
    12: "runecrafting",
    13: "mining",
    14: "smithing",
    15: "fishing",
    16: "cooking",
    17: "firemaking",
    18: "woodcutting",
    19: "fletching",
    20: "slayer",
    21: "farming",
    22: "construction",
    23: "hunter",
    24: "summoning",
    25: "dungeoneering",
}


def _normalise_name(text: str) -> str:
    return "".join(re.findall(r"[a-z0-9]+", text.lower()))


_QUEST_IDS = {}
for _quest_id, _record in QUEST_DATA.items():
    if not isinstance(_record, dict):
        continue
    for _name in (_quest_id, str(_record.get("display_name", ""))):
        _normalised = _normalise_name(_name)
        _QUEST_IDS[_normalised] = _quest_id
        for _prefix in ("the", "a"):
            if _normalised.startswith(_prefix):
                _QUEST_IDS[_normalised[len(_prefix) :]] = _quest_id

# Exact action/counter translations for source tasks whose cache struct carries
# no ordinary skill or quest requirement. Every entry names a durable state seam
# already produced by the live engine; absent entries are deliberately omitted.
CONDITION_OVERRIDES = {
    538: (("hold_item", "Bronze pickaxe", 1, "Own a bronze pickaxe"),),
    546: (("ledger_action", "hunter:catch_crimson_swift", 1, "Catch a crimson swift"),),
    555: (("counter", "slayer_tasks_completed", 1, "Complete a Slayer assignment"),),
    562: (("ledger_action", "fletching:bronze_arrows", 1, "Fletch bronze arrows"),),
    564: (("ledger_action", "fletching:string_shortbow", 1, "Fletch a shortbow"),),
    566: (("ledger_action", "herblore:clean_guam", 1, "Clean guam"),),
    567: (("ledger_action", "herblore:finished_attack_potion", 1, "Brew an attack potion"),),
    574: (("ledger_action", "agility:burthorpe_course", 1, "Complete the Burthorpe Agility Course"),),
    197: (("ledger_action", "cooking:cook_spider_on_a_stick", 1, "Cook a spider on a stick"),),
    580: (("counter", "house_owned", 1, "Own a player house"),),
    582: (("ledger_action", "construction:crude_wooden_chair", 1, "Build a crude wooden chair"),),
    570: (("ledger_action", "runecrafting:craft_mind_runes", 1, "Craft mind runes"),),
    451: (("quest", "let_them_eat_pie", 1, "Complete Let Them Eat Pie"),),
    440: (("quest", "druidic_ritual", 1, "Complete Druidic Ritual"),),
    441: (("quest", "death_plateau", 1, "Complete Death Plateau"),),
}

# These three quest requirements are the described deed itself, rather than an
# access gate for some other world action. They are the quest-family analogue of
# the visibly labelled progression anchors.
QUEST_COMPLETION_SOURCE_IDS = frozenset({440, 441, 451})

# Darkan confirms these tasks' exact tier membership. Their ordinary requirement
# pairs are absent from enum 3483 but present in the already-pinned pre-cutoff
# family tables, so retaining the earlier requirement predicates loses no source
# fidelity and avoids treating cache absence as evidence that a task was invalid.
CONDITION_OVERRIDES.update({
    0: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    125: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    188: (("skill_level", "fishing", 5, "Level 5 Fishing"),),
    192: (("skill_level", "agility", 40, "Level 40 Agility"),),
    209: (("quest", "shilo_village", 1, "Complete Shilo Village"),),
    97: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    107: (("quest", "dragon_slayer", 1, "Complete Dragon Slayer"),),
    952: (("counter", "temple_trekking.completions.trek_easy_easy", 1, "Take an easy companion through easy Temple Trekking routes"),),
    993: (("quest", "ritual_of_the_mahjarrat", 1, "Complete Ritual of the Mahjarrat"),),
    985: (
        ("skill_level", "runecrafting", 50, "Level 50 Runecrafting"),
        ("quest", "legacy_of_seergaze", 1, "Complete Legacy of Seergaze"),
    ),
    983: (("counter", "temple_trekking.completions.trek_hard_hard", 1, "Take a hard companion through hard Temple Trekking routes"),),
    963: (("quest", "ghosts_ahoy", 1, "Complete Ghosts Ahoy"),),
    971: (("quest", "in_search_of_the_myreque", 1, "Complete In Search of the Myreque"),),
    964: (("counter", "temple_trekking.completions.trek_medium_medium", 1, "Take a medium companion through medium Temple Trekking routes"),),
    965: (("counter", "temple_trekking.completions.ramble_any", 1, "Complete a Burgh de Rott Ramble"),),
    257: (("quest", "rune_mysteries", 1, "Complete Rune Mysteries"),),
    268: (("quest", "the_dig_site", 1, "Complete The Dig Site"),),
    267: (("skill_level", "construction", 10, "Level 10 Construction"),),
    291: (("quest", "garden_of_tranquillity", 1, "Complete Garden of Tranquillity"),),
})

# Exact terminal counters in the implemented activity families. Activities with
# no durable gameplay proof are omitted unless enum 3483 supplies an ordinary
# evaluable prerequisite of its own.
CONDITION_OVERRIDES.update({
    3000: (("counter", "tears_of_guthix.visits", 1, "Complete a Tears of Guthix visit"),),
    3001: (
        (
            "any_of", "", 1, "Complete a Conquest match",
            (
                ("counter", "conquest_games_won", 1, "Win a Conquest match"),
                ("counter", "conquest_games_lost", 1, "Lose a Conquest match"),
            ),
        ),
    ),
    3002: (("counter", "penguin_hide_and_seek.lifetime_spotted", 1, "Spy a penguin"),),
    3003: (("counter", "achievement_progress.skills.woodcutting.actions.evil_tree_fell", 1, "Fell an evil tree"),),
    3004: (("counter", "achievement_progress.skills.mining.actions.shooting_stars", 1, "Mine a shooting star"),),
    3005: (("counter", "achievement_progress.skills.hunter.actions.catch_baby_impling_puro_puro", 1, "Catch an impling in Puro-Puro"),),
    3006: (("counter", "vinesweeper.operations", 1, "Complete a Vinesweeper operation"),),
    3007: (("counter", "circus.lifetime_performances", 1, "Complete a circus performance"),),
    3009: (("quest", "all_fired_up", 1, "Complete All Fired Up"),),
    3010: (("counter", "skeletal_horror.kills", 1, "Defeat the Skeletal Horror"),),
    3012: (("counter", "great_orb_project.games_completed", 1, "Complete a Great Orb Project game"),),
    3013: (("counter", "pest_control_games_won", 1, "Win a Pest Control game"),),
    3014: (("counter", "castle_wars_games_played", 1, "Complete a Castle Wars game"),),
    3015: (("counter", "court_cases_attempts", 1, "Argue a court case"),),
    3017: (("counter", "fight_caves.clears", 1, "Clear the Fight Caves"),),
    3018: (("counter", "tzhaar_fight_pit_matches", 1, "Enter a Fight Pit match"),),
    3019: (("counter", "achievement_progress.skills.agility.outputs.Agility arena ticket", 1, "Earn an Agility arena ticket"),),
    3020: (("counter", "barbarian_assault_runs_completed", 1, "Complete a Barbarian Assault run"),),
    3022: (("counter", "shades_of_mortton_chests_opened", 1, "Open a Shades of Mort'ton chest"),),
    3023: (("counter", "barrows.chests_opened", 1, "Open a Barrows chest"),),
    3024: (("counter", "pyramid_plunder_runs_completed", 1, "Complete a Pyramid Plunder run"),),
    3025: (("counter", "sorceress_garden.successful_trips", 1, "Complete a Sorceress's Garden trip"),),
    3026: (("counter", "mage_training_arena.entries", 1, "Enter the Mage Training Arena"),),
    3027: (("counter", "duel_arena_matches", 1, "Enter a Duel Arena match"),),
    3028: (("counter", "fist_of_guthix.matches_started", 1, "Enter a Fist of Guthix match"),),
    3029: (("counter", "stealing_creation.games", 1, "Enter a Stealing Creation game"),),
    3030: (("counter", "soul_wars_games_played", 1, "Complete a Soul Wars game"),),
    3031: (("counter", "clan_wars_matches", 1, "Enter a Clan Wars match"),),
    3032: (
        (
            "any_of", "", 1, "Complete a Gnome Restaurant delivery",
            (
                (
                    "counter",
                    "gnome_restaurant.deliveries.easy",
                    1,
                    "Complete an easy delivery",
                ),
                (
                    "counter",
                    "gnome_restaurant.deliveries.hard",
                    1,
                    "Complete a hard delivery",
                ),
            ),
        ),
    ),
    3033: (
        (
            "counter",
            "mobilising_armies_games_played",
            1,
            "Complete a Mobilising Armies game",
        ),
    ),
    3034: (("counter", "warriors_guild.activity_reviews.warriors_guild_attack_dummy", 1, "Train in the Warriors' Guild"),),
})


def _kill_any_of(label: str, verb: str, enemy_ids: tuple) -> tuple:
    """An ``any_of`` over the kill counters of one species' level variants.

    The period wrote several tasks as "kill a giant rat"; AnkiScape stores one
    counter per level variant, so the honest predicate is the disjunction over
    every variant of that species rather than an arbitrary pick of one.
    """

    from ankiscape.core.constants import COMBAT_ENEMY_DATA

    alternatives = []
    for enemy_id in enemy_ids:
        display = str(COMBAT_ENEMY_DATA[enemy_id]["display_name"]).lower()
        level = re.search(r"_level_(\d+)$", enemy_id)
        if level:
            display = f"{display} (level {level.group(1)})"
        article = "an" if display[0] in "aeiou" else "a"
        alternatives.append(
            (
                "counter",
                f"combat_kill_counts.{enemy_id}",
                1,
                f"{verb} {article} {display}",
            )
        )
    return ("any_of", "", 1, label, tuple(alternatives))


# Source tasks the cache states as a disjunction, or that name one period NPC
# AnkiScape stores as several level variants. Each was previously omitted for
# want of a predicate that could express "any of these".
CONDITION_OVERRIDES.update({
    190: (
        (
            "any_of", "", 1, "Attempt a TzHaar Fight Pit match or the Fight Caves",
            (
                ("counter", "tzhaar_fight_pit_matches", 1, "Enter a Fight Pit match"),
                ("counter", "fight_caves.total_kills", 1, "Land a Fight Caves kill"),
            ),
        ),
    ),
    953: (
        _kill_any_of(
            "Kill a Slayer Tower ground-floor monster",
            "Kill",
            ("crawling_hand", "banshee", "infernal_mage"),
        ),
    ),
    85: (
        _kill_any_of(
            "Defeat a zombie",
            "Defeat",
            tuple(f"zombie_level_{level}" for level in (13, 18, 24, 25, 30, 44, 53)),
        ),
    ),
    93: (
        _kill_any_of(
            "Kill a giant rat",
            "Kill",
            ("giant_rat", "giant_rat_level_6", "giant_rat_level_26"),
        ),
    ),
    123: (
        _kill_any_of("Kill a duck", "Kill", ("duck_land", "duck_water")),
    ),
})

# Kudos is a weighted sum over three append-only museum records, so no leaf
# holds it and a counter would read zero forever. Task 268 was already shipped
# on its quest half alone; the Kudos half it always stated is now evaluated too.
CONDITION_OVERRIDES.update({
    300: (
        ("derived_value", "varrock_museum_kudos", 153, "Earn 153 Kudos"),
    ),
    268: (
        ("quest", "the_dig_site", 1, "Complete The Dig Site"),
        ("derived_value", "varrock_museum_kudos", 50, "Earn 50 Kudos"),
    ),
})

# Existing durable state that the initial harvest could not name. Geography and
# NPC choreography are dropped only where the distinctive deed remains intact.
CONDITION_OVERRIDES.update({
    13: (
        ("ledger_action_family", "summoning:infuse", 1, "Infuse a Summoning pouch"),
    ),
    15: (
        (
            "shop_transaction",
            "buy|aemads_adventuring_supplies|aemads_adventuring_supplies:9:227",
            1,
            "Buy a vial of water from Aemad and Kortan",
        ),
    ),
    115: (
        ("hold_item", "Amulet of farming (8)", 1, "Own an amulet of farming"),
    ),
    116: (("hold_item", "Beer", 1, "Own a stat-boosting beer"),),
    121: (
        ("ledger_action", "utility:draw_bucket_of_water", 1, "Draw a bucket of water"),
    ),
    124: (("combat_kill", "highwayman", 1, "Kill a highwayman"),),
    135: (("combat_kill", "ice_giant", 1, "Kill an ice giant"),),
    149: (
        ("skill_level", "slayer", 72, "Level 72 Slayer"),
        ("combat_kill", "skeletal_wyvern", 1, "Kill a skeletal wyvern"),
    ),
    153: (("combat_kill", "rock_crab", 5, "Kill five rock crabs"),),
    161: (("combat_kill", "black_unicorn", 1, "Kill an adult black unicorn"),),
    544: (
        (
            "state_equals",
            "farm_patches.taverley_potato.last_crop_id",
            1,
            "Plant potatoes in Taverley",
            "potato",
        ),
    ),
    551: (
        ("equipped_item", "hands|Spiked gauntlets", 1, "Wear spiked gauntlets"),
    ),
    557: (
        (
            "state_equals",
            "summoning_state.active_follower.entity_id",
            1,
            "Summon a spirit wolf",
            "spiritwolf",
        ),
    ),
})


# The Ranging Guild tasks retain their source level gate, but level 40 alone is
# not the deed: one requires over 1,000 tickets; the other requires an exchange
# purchase.
CONDITION_OVERRIDES.update({
    238: (
        ("skill_level", "ranged", 40, "Level 40 Ranged"),
        ("hold_item", "Archery ticket", 1001, "Hold over 1,000 archery tickets"),
    ),
    239: (
        ("skill_level", "ranged", 40, "Level 40 Ranged"),
        (
            "counter",
            "ranging_guild.exchange_purchases",
            1,
            "Buy a Ranging Guild reward",
        ),
    ),
})


# Contract-limited telemetry added at the existing coarse event seams. Every key
# below has exactly one diary consumer; unrelated shop and Fight Caves events do
# not grow parallel ledgers.
CONDITION_OVERRIDES.update({
    129: (
        (
            "shop_transaction",
            "buy|waynes_chains|waynes_chains:3:1107",
            1,
            "Buy a black chainbody from Wayne's Chains",
        ),
        ("equipped_item", "body|Black chainbody", 1, "Wear a black chainbody"),
    ),
    79: (
        (
            "shop_transaction",
            "sell|lumbridge_fishing_supplies|lumbridge_fishing_supplies:6:317",
            1,
            "Sell raw shrimps to Lumbridge Fishing Supplies",
        ),
    ),
    212: (
        (
            "counter",
            "fight_caves.kill_counts.ket_zek",
            1,
            "Kill a Ket-Zek in the Fight Caves",
        ),
    ),
    230: (
        (
            "any_of",
            "",
            1,
            "Buy a candle from the candle-maker",
            (
                (
                    "shop_transaction",
                    "buy|candle_shop|candle_shop:0:36",
                    1,
                    "Buy a candle from the candle-maker",
                ),
                (
                    "shop_transaction",
                    "buy|candle_with_black_shop|candle_with_black_shop:0:36",
                    1,
                    "Buy a black candle from the candle-maker",
                ),
            ),
        ),
    ),
    263: (
        (
            "shop_transaction",
            "vendor_action||benny_buy_varrock_herald",
            1,
            "Buy a Varrock Herald from Benny",
        ),
    ),
})

# First owner-approved deed tranche. These predicates replace requirement gates
# only where durable gameplay already proves the translated deed. Context that
# the existing ledgers cannot prove (one-action batch size, equipment used,
# production from scratch, or a duplicate region-specific deed) stays gated for
# a later narrow-telemetry tranche rather than receiving inferred credit.
CONDITION_OVERRIDES.update({
    5: (("ledger_action", "utility:fishing_trawler", 1, "Complete a Fishing Trawler duty"),),
    29: (("ledger_action", "magic:watchtower_teleport", 1, "Cast Watchtower Teleport"),),
    40: (("combat_kill", "shadow_warrior", 1, "Kill a shadow warrior"),),
    44: (("ledger_action", "magic:ourania_teleport", 1, "Cast Ourania Teleport"),),
    50: (("ledger_action", "magic:ardougne_teleport", 1, "Cast Ardougne Teleport"),),
    52: (("ledger_action", "hunter:catch_red_salamander", 1, "Catch a red salamander"),),
    56: (("ledger_output", "utility:Raw manta ray", 1, "Catch a manta ray in Fishing Trawler"),),
    84: (("ledger_output", "fishing:Raw pike", 1, "Catch a pike"),),
    86: (("ledger_output", "smithing:Steel bar", 1, "Smelt a steel bar"),),
    88: (("ledger_output", "runecrafting:Water rune", 1, "Craft a water rune"),),
    99: (("ledger_output", "crafting:Clay ring", 1, "Create a clay ring"),),
    104: (("ledger_output", "cooking:Lobster", 1, "Cook a lobster"),),
    105: (("ledger_output", "fishing:Raw salmon", 1, "Catch a salmon"),),
    108: (("ledger_output", "smithing:Steel longsword", 1, "Smith a steel longsword"),),
    109: (("ledger_action", "magic:lumbridge_teleport", 1, "Cast Lumbridge Teleport"),),
    110: (("ledger_action", "firemaking:willow_logs", 1, "Light a willow-log fire"),),
    112: (("ledger_action", "mining:silver", 1, "Mine silver ore"),),
    113: (("ledger_output", "smithing:Silver bar", 1, "Smelt a silver bar"),),
    114: (("ledger_action", "crafting:silver_unstrung_symbol", 1, "Craft a holy symbol"),),
    125: (("ledger_output", "runecrafting:Mind tiara", 1, "Make a mind tiara"),),
    134: (("combat_kill", "black_knight", 1, "Kill a Black Knight"),),
    139: (("ledger_output", "smithing:Blurite limbs", 1, "Smith blurite crossbow limbs"),),
    152: (("combat_kill", "cave_crawler", 1, "Kill a cave crawler"),),
    165: (("ledger_output", "crafting:Vial", 3, "Make three vials"),),
    171: (("ledger_output", "cooking:Cheese wheel", 1, "Make cheese"),),
    175: (("ledger_action", "agility:barbarian_normal", 1, "Complete the Barbarian Outpost Agility Course"),),
    179: (("ledger_action", "magic:bake_pie", 1, "Bake a pie using Magic"),),
    184: (("ledger_action", "mining:gold", 1, "Mine gold ore"),),
    199: (("ledger_output", "woodcutting:Teak logs", 1, "Cut teak logs"),),
    200: (("ledger_output", "woodcutting:Mahogany logs", 1, "Cut mahogany logs"),),
    201: (("ledger_output", "fishing:Raw karambwan", 1, "Catch a karambwan"),),
    214: (("ledger_output", "runecrafting:Nature rune", 1, "Craft nature runes"),),
    226: (("ledger_output", "crafting:Bow string", 5, "Spin five bow strings"),),
    232: (("ledger_output", "fishing:Raw mackerel", 1, "Catch a mackerel"),),
    243: (
        ("ledger_output", "fishing:Raw bass", 1, "Catch a bass"),
        ("ledger_output", "cooking:Bass", 1, "Cook a bass"),
    ),
    246: (("ledger_output", "woodcutting:Yew logs", 5, "Cut five sets of yew logs"),),
    247: (("ledger_action", "fletching:string_magic_shortbow", 1, "String a magic shortbow"),),
    250: (("ledger_action", "firemaking:magic_logs", 1, "Burn a magic log"),),
    253: (("ledger_output", "fishing:Raw shark", 5, "Catch five sharks"),),
    271: (("ledger_action", "mining:limestone", 1, "Mine limestone"),),
    272: (("ledger_output", "fishing:Raw trout", 1, "Catch a trout"),),
    288: (("ledger_action", "magic:varrock_teleport", 1, "Cast Varrock Teleport"),),
    302: (("ledger_output", "crafting:Air battlestaff", 1, "Craft an air battlestaff"),),
    305: (("ledger_output", "construction:Varrock teleport tablet", 1, "Make a Varrock Teleport tablet"),),
    309: (("ledger_output", "fishing:Raw rocktail", 1, "Catch a rocktail"),),
    310: (("ledger_output", "cooking:Rocktail", 1, "Cook a rocktail"),),
    311: (("ledger_action", "mining:concentrated_gold", 1, "Mine concentrated gold"),),
    314: (("ledger_action", "magic:string_jewellery", 1, "Cast String Jewellery"),),
    323: (("ledger_output", "herblore:Ranging mix (2)", 1, "Make a ranging mix"),),
    336: (("ledger_action", "magic:fertile_soil", 1, "Cast Fertile Soil"),),
    357: (("ledger_action", "firemaking:yew_logs", 1, "Burn a yew log"),),
    945: (("ledger_output", "cooking:Thin snail meat", 1, "Cook a thin snail"),),
    962: (("ledger_output", "woodcutting:Bark", 1, "Obtain bark from a hollow tree"),),
    972: (("ledger_action", "smithing:forge_cannonballs", 1, "Make a batch of cannonballs"),),
    986: (("combat_kill", "abyssal_demon", 1, "Kill an abyssal demon"),),
    987: (("ledger_output", "runecrafting:Blood rune", 1, "Craft blood runes"),),
    3003: (("ledger_action", "woodcutting:evil_tree_fell", 1, "Fell an evil tree"),),
    3004: (("ledger_action", "mining:shooting_stars", 1, "Mine a shooting star"),),
    3005: (("ledger_action", "hunter:catch_baby_impling_puro_puro", 1, "Catch an impling in Puro-Puro"),),
    3019: (("ledger_output", "agility:Agility arena ticket", 1, "Earn an Agility arena ticket"),),
})


def _quest_id(source_name: str) -> str:
    return _QUEST_IDS.get(_normalise_name(source_name.replace("_", " ")), "")


def _requirement_conditions(task: dict) -> list[tuple]:
    conditions: list[tuple] = []
    for requirement in task.get("requirements", ()):
        kind = requirement.get("kind")
        if kind == "skill":
            skill_id = _SKILL_TYPE_IDS.get(int(requirement.get("skill_type", 0)))
            level = int(requirement.get("level", 0))
            if skill_id and level > 1:
                display = skill_id.replace("_", " ").title()
                conditions.append(
                    ("skill_level", skill_id, level, f"Level {level} {display}")
                )
        elif kind == "quest":
            source_name = str(requirement.get("quest", ""))
            quest_id = _quest_id(source_name)
            if quest_id:
                display = str(
                    QUEST_DATA[quest_id].get(
                        "display_name", quest_id.replace("_", " ").title()
                    )
                )
                conditions.append(("quest", quest_id, 1, f"Complete {display}"))
    return conditions


def _source_conditions(task: dict) -> list[tuple]:
    """The pre-firewall ordering signal, retained to keep roster identity stable."""

    override = CONDITION_OVERRIDES.get(int(task["id"]))
    return list(override) if override is not None else _requirement_conditions(task)


def _access_gates(task: dict) -> list[tuple]:
    task_id = int(task["id"])
    if task_id in QUEST_COMPLETION_SOURCE_IDS:
        return []

    gates = _requirement_conditions(task)
    seen = {gate[:3] for gate in gates}
    for condition in CONDITION_OVERRIDES.get(task_id, ()):
        if condition[0] not in {"skill_level", "quest"} or condition[:3] in seen:
            continue
        gates.append(condition)
        seen.add(condition[:3])
    return gates


def _conditions(task: dict) -> list[tuple]:
    task_id = int(task["id"])
    override = CONDITION_OVERRIDES.get(task_id, ())
    if task_id in QUEST_COMPLETION_SOURCE_IDS:
        return list(override)
    return [
        condition
        for condition in override
        if condition[0] not in {"skill_level", "quest"}
    ]


def _condition_src(condition: tuple) -> str:
    """Serialise one condition, refusing any key the runtime never writes."""

    kind, key, amount, label = condition[:4]
    expected = condition[4] if kind == "state_equals" and len(condition) > 4 else None
    error = resolve_condition_key(kind, key, expected)
    if error:
        raise SystemExit(f"unresolvable diary condition ({label}): {error}")
    if kind == "derived_value":
        ceiling = _import_attr(
            "ankiscape.logic.achievement_diary_derived", "DIARY_DERIVED_VALUE_CEILINGS"
        )[key]
        if amount > ceiling:
            raise SystemExit(
                f"derived_value {key!r} threshold {amount} is above the implemented"
                f" ceiling {ceiling}, so the row could never complete"
            )
    head = f"DiaryCondition({kind!r}, {key!r}, {amount}, {label!r}"
    if kind == "state_equals":
        return f"{head}, expected={expected!r})"
    if kind == "any_of":
        alternatives = condition[4] if len(condition) > 4 else ()
        return f"{head}, ({_alternatives_src(label, alternatives)},))"
    return f"{head})"


def _alternatives_src(label: str, alternatives: tuple) -> str:
    """Serialise an ``any_of`` body: one level of at least one alternative."""

    if not alternatives:
        raise SystemExit(f"any_of condition {label!r} carries no alternatives")
    if any(alternative[0] == "any_of" for alternative in alternatives):
        raise SystemExit(f"any_of condition {label!r} nests another any_of")
    return ", ".join(_condition_src(alternative) for alternative in alternatives)
