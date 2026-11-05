"""The Elder Kiln's authored opening: gates, stage-1 deed, journal copy and provenance."""

import re
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest import elder_kiln as source
from ankiscape.data.quest.catalog import _apply_stage_item_name_overrides, _catalog_stage_requirements
from ankiscape.data.quest.serializers import _stage_requirement_dict
from ankiscape.data.quest.stage_cleanups import QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID
from ankiscape.data.quest_action_proof_data import ELDER_KILN_HATCH_PROOF, QUEST_ACTION_PROOF_RULES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

QUEST_ID = "the_elder_kiln"
PROOF = ELDER_KILN_HATCH_PROOF
GENERATED = next(row for row in PRE_EOC_QUEST_CATALOG if row["id"] == QUEST_ID)
SENTINEL = "Complete The Elder Kiln stage 1 objective"
ENTRY_LEVELS = {"magic": 75, "agility": 60, "mining": 41}


def player(progress=0, *, started=False, completed=False, levels=None, proofs=()):
    """A save whose earned XP matches the levels it claims."""
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for skill_id, level in {**ENTRY_LEVELS, **(levels or {})}.items():
        data[f"{skill_id}_level"] = level
        data[f"{skill_id}_exp"] = EXP_TABLE[level - 1]
    data["quests"][QUEST_ID] = dict(started=started, completed=completed, progress=progress)
    data["current_quest"] = QUEST_ID
    data["quest_action_proofs"] = sorted(proofs)
    return data


class ElderKilnCatalogTest(unittest.TestCase):
    def test_entry_gates_readout_and_no_opening_resources(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(
            {row["skill_id"]: row["level"] for row in quest["required_skills"]}, ENTRY_LEVELS,
        )
        self.assertEqual(
            quest["requirements"],
            ("Agility 60 (boosts do not work)", "Magic 75 (boosts do not work)", "Mining 41"),
        )
        self.assertEqual(quest["required_quests"], ())
        self.assertEqual(GENERATED["required_quests"], ())
        self.assertEqual(quest["required_quest_points"], 0)
        self.assertEqual(quest["required_items"], {})
        self.assertEqual(quest["start_inventory"], {})

    def test_stage_one_replaces_the_sentinel_with_the_hatch_deed_only(self):
        generated_stage_one = GENERATED["stage_requirements"][0]
        self.assertEqual(generated_stage_one["required_actions"], (SENTINEL,))
        opening = QUEST_DATA[QUEST_ID]["stage_requirements"][0]
        self.assertEqual(opening["required_actions"], (PROOF,))
        for key in (
            "required_inventory", "required_tools", "consumed_inventory", "produced_inventory",
            "required_inventory_options", "consumed_inventory_options", "auto_actions",
            "required_routes", "combat_encounters", "required_skills",
        ):
            self.assertFalse(opening[key], key)
        self.assertFalse(opening["repeatable_until_consumed"])

    def test_sole_cleanup_names_only_the_sentinel_and_the_proof(self):
        cleanups = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID[QUEST_ID]
        self.assertIs(cleanups, source.ELDER_KILN_STAGE_CLEANUPS)
        (cleanup,) = cleanups
        self.assertEqual(cleanup.stage, 1)
        self.assertEqual(cleanup.remove_required_actions, (SENTINEL,))
        self.assertEqual(cleanup.add_required_actions, (PROOF,))
        self.assertIn(source.SOURCE_W["url"], cleanup.source)
        self.assertIn(source.SOURCE_Q["url"], cleanup.source)
        untouched = {
            name: value for name, value in vars(cleanup).items()
            if name not in {"stage", "remove_required_actions", "add_required_actions", "source"}
        }
        self.assertTrue(untouched)
        self.assertFalse(any(untouched.values()), untouched)

    def test_actual_proof_rule_and_no_automatic_or_alternative_producer(self):
        self.assertEqual(PROOF, "Hatch TzHaar-Mej-Jeh’s egg")
        self.assertIs(source.ELDER_KILN_HATCH_PROOF, PROOF)
        self.assertEqual(QUEST_ACTION_PROOF_RULES[("quest_activity", "elder_kiln_first_egg")], ((), (PROOF,)))
        self.assertEqual(source.HATCH_EVENT, ("quest_activity", "elder_kiln_first_egg"))
        producers = [event for event, (_needs, emits) in QUEST_ACTION_PROOF_RULES.items() if PROOF in emits]
        self.assertEqual(producers, [source.HATCH_EVENT])
        for quest_id, quest in QUEST_DATA.items():
            for row in quest["stage_requirements"]:
                self.assertNotIn(PROOF, row["auto_actions"], quest_id)

    def test_six_stages_and_later_requirements_rewards_and_unlocks_unchanged(self):
        quest = QUEST_DATA[QUEST_ID]
        self.assertEqual(GENERATED["stages"], 6)
        self.assertEqual(len(quest["stage_requirements"]), 6)
        self.assertEqual(sorted(quest["journal_stages"]), [1, 2, 3, 4, 5, 6])
        self.assertEqual(quest["stages"], 7)
        baseline = tuple(_stage_requirement_dict(row) for row in _apply_stage_item_name_overrides(
            _catalog_stage_requirements(GENERATED["stage_requirements"])))
        self.assertEqual(quest["stage_requirements"][1:], baseline[1:])
        self.assertEqual(baseline[0]["required_actions"], (SENTINEL,))
        for key in ("point_reward", "xp_rewards", "unlocks"):
            self.assertEqual(quest[key], GENERATED[key], key)
        self.assertEqual(quest["rewards"], {"Tokkul-Zo": 1})
        self.assertEqual(len(quest["lamp_rewards"]), 1)
        self.assertEqual(quest["lamp_rewards"][0]["amount"], 100000.0)
        self.assertEqual(len(quest["stage_requirements"][4]["combat_encounters"]), 17)

    def test_journal_relocates_offer_and_hatching_without_touching_later_lines(self):
        journal = QUEST_DATA[QUEST_ID]["journal_stages"]
        generated = {row["stage"]: tuple(row["journal"]) for row in GENERATED["journal_stages"]}
        self.assertEqual(journal[1], (source.BEFORE_OFFER_COPY,))
        self.assertEqual(journal[2], ("Mej-Jeh wants me to retrieve Ga’al-Jeh from the Main Plaza, west of the Birthing Pool.",))
        self.assertEqual(generated[3][0], source.GENERATED_HATCHING_LINE)
        self.assertEqual(journal[3], generated[3][1:])
        self.assertEqual(len(journal[3]), 4)
        for stage in (4, 5, 6):
            self.assertEqual(journal[stage], generated[stage])
        flattened = " ".join(line for lines in journal.values() for line in lines)
        for heading in ("1 Walkthrough", "Offer to help hatch the egg.", source.GENERATED_HATCHING_LINE):
            self.assertNotIn(heading, flattened)

    def test_exact_opening_copy(self):
        self.assertEqual(source.REQUEST_COPY, (
            "TzHaar-Mej-Jeh’s egg is dying because it is too cold. The other Mejs think it is beyond help, "
            "but he believes it can survive. He asks me to help hatch it."))
        self.assertEqual(source.BEFORE_OFFER_COPY, (
            "Speak to TzHaar-Mej-Jeh at the Birthing Pool in north-east TzHaar City and offer to help hatch his egg."))
        self.assertEqual(source.AFTER_OFFER_COPY, "I have agreed to help Mej-Jeh and Mej-Ak hatch the egg.")
        self.assertEqual(source.INSTRUCTIONS_COPY, (
            "Use fire spells to warm the egg and water spells to cool it. Keep the temperature between the moving "
            "markers so the hatching percentage rises. The Mejs help with fire when it is too cold, so watch for "
            "overheating. Reach 100% to hatch the egg. If progress falls back to 0%, start again. No items or player "
            "runes are needed, and this activity gives no Magic experience."))
        self.assertEqual(source.EXERCISE_COPY, (
            "The egg changes when you cast or choose to wait. Closing this window pauses your attempt."))
        self.assertEqual(source.SUCCESS_COPY, (
            "The egg has hatched as a Ga’al, without its parent’s inherited memories. "
            "Mej-Ak has taken him away toward the Fight Pits."))
        self.assertEqual(source.LEGACY_COPY, "This journal has no recorded hatching deed for the opening.")
        self.assertEqual(source.FAILURE_COPY, "The hatching progress fell to 0%. Start again.")
        self.assertEqual(source.SPELL_LABELS, (
            "Fire Bolt", "Fire Blast", "Fire Wave", "Water Bolt", "Water Blast", "Water Wave"))
        self.assertEqual(source.HELPER_NAMES, ("Mej-Ak", "Mej-Jeh"))


PLACEHOLDERS = {
    "INITIAL_HEAT": ("initial_heat", 0),
    "INITIAL_PROGRESS": ("initial_progress", 0),
    "INITIAL_BAND": ("initial_band", 1),
    "HEAT_BOUNDS": ("heat_bounds", (0, 100)),
    "SPELL_DELTAS": ("spell_deltas", (5, 10, 25, -5, -10, -25)),
    "BANDS": ("bands", ((20, 40), (55, 70), (80, 90))),
    "PROGRESS_STEP": ("progress_step", 1),
    "COOLING_STEP": ("cooling_step", 1),
    "MARKER_INTERVAL": ("marker_interval", 20),
    "HELPER_INITIAL_DELAY": ("helper_initial_delay", (0, 25)),
    "HELPER_WARNING": ("helper_warning", 5),
    "HELPER_COOLDOWN": ("helper_cooldown", 50),
    "HELPER_HEAT": ("helper_heat", 25),
}


class ElderKilnProvenanceTest(unittest.TestCase):
    def test_every_numeric_constant_carries_its_own_registered_marker(self):
        lines = Path(source.__file__).read_text(encoding="utf-8").splitlines()
        register = (Path(__file__).resolve().parents[2] / "memory-bank" / "placeholder-values.md").read_text(encoding="utf-8")
        for name, (suffix, value) in PLACEHOLDERS.items():
            with self.subTest(name=name):
                self.assertEqual(getattr(source, name), value)
                index = next(i for i, line in enumerate(lines) if line.startswith(f"{name} = "))
                marker = f"# PLACEHOLDER(quests.elder_kiln.{suffix}): "
                self.assertTrue(lines[index - 1].startswith(marker), lines[index - 1])
                row = next(line for line in register.splitlines() if line.startswith(f"| `quests.elder_kiln.{suffix}` |"))
                for needle in ("b1e16caf5ceadc5780d6222b80bc561ac60daf01", "original D", "Unverified for the period",
                               "Independent pre-2012-11-20 gameplay or server evidence", "324–348"):
                    self.assertIn(needle, row)
        markers = sorted(re.findall(r"PLACEHOLDER\((quests\.elder_kiln\.[a-z_]+)\)", "\n".join(lines)))
        self.assertEqual(len(markers), 13)
        self.assertEqual(markers, sorted(f"quests.elder_kiln.{suffix}" for suffix, _ in PLACEHOLDERS.values()))
        self.assertEqual(source.PROGRESS_COMPLETE, 100)
        self.assertNotIn("PLACEHOLDER", lines[next(i for i, line in enumerate(lines) if line.startswith("PROGRESS_COMPLETE")) - 1])

    def test_source_identities(self):
        self.assertEqual((source.SOURCE_W["oldid"], source.SOURCE_W["timestamp"], source.SOURCE_W["sha256"]), (
            6579162, "2012-11-18T16:32:05Z", "edfc7a09036a7e3b48c395bb1926b6df0dbedab29d201af614822f3d6394da8a"))
        self.assertEqual((source.SOURCE_Q["oldid"], source.SOURCE_Q["timestamp"], source.SOURCE_Q["sha256"]), (
            5706348, "2012-06-03T04:51:41Z", "e763201d3fd9ba7b62260c7596deac2ca7a48b1bf1c4e3114a3303c99570eef5"))
        self.assertEqual((source.SOURCE_R["capture"], source.SOURCE_R["sha256"]), (
            "20120218052431", "e195afbf2da16711fbc3bb61cbb4d43dde63cfecc8eea547721fe3d71d432251"))
        self.assertEqual((source.SOURCE_T["capture"], source.SOURCE_T["sha256"]), (
            "20121117012923", "baff250e99834d3e12a964d2a200a045390691244db80cf7c343d9058a9ba87b"))
        self.assertEqual((source.SOURCE_D["revision"], source.SOURCE_D["sha256"], source.SOURCE_D["algorithm_commit"],
                          source.SOURCE_D["success_wait_commit"]), (
            "517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed",
            "4fde07c225cdac045cdec23fa6a6b5386fd2ec832cf14e0de583b7c726bf0851",
            "b1e16caf5ceadc5780d6222b80bc561ac60daf01", "aec071d34c8bd52f9ddbdeb36e8c8b01cfdbffa5"))
        self.assertEqual((source.SOURCE_CLIENT["interface"], source.SOURCE_CLIENT["sha256"]), (
            1247, "87e79878d40769f860f75811e4dc273e4abcd08dc736df7438bdd6ecf08091f6"))
        self.assertTrue(source.SOURCE_W["url"].endswith("oldid=6579162"))
        self.assertTrue(source.SOURCE_Q["url"].endswith("oldid=5706348"))
        self.assertTrue(source.SOURCE_R["url"].startswith("https://web.archive.org/web/20120218052431id_/"))
        self.assertTrue(source.SOURCE_T["url"].startswith("https://web.archive.org/web/20121117012923id_/"))

    def test_qualifications_stay_beside_the_constants(self):
        text = Path(source.__file__).read_text(encoding="utf-8")
        needles = ["W58 says the marker gap narrows", "unconditionally", "recoverable", "not a recovered grace",
                   "not degrees", "not server-time parity", "none of them is a verified period mechanic"]
        found = [needle for needle in needles if needle in text]
        self.assertEqual(found, needles)


if __name__ == "__main__":
    unittest.main()
