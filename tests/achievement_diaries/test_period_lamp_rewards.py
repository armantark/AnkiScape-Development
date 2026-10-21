"""Independent period reward table and real shared-reducer boundary checks."""

import copy
import unittest
from dataclasses import fields

import pkg_alias  # noqa: F401
from ankiscape.core.constants import CLAIM_DATA, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.skill_registry import trainable_skill_definitions
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.achievement_diary_catalog import DIARY_FAMILIES
from ankiscape.data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG, DIARY_ALL_LAMP_CLAIM_IDS_BY_TIER,
    DIARY_LAMP_CLAIM_IDS_BY_TIER, DiaryLamp, DiaryTier, diary_lamp_claim_id,
    diary_lamp_claims_as_dict,
)
from ankiscape.data.achievement_diaries.lamp_rewards import apply_lamp_reward_overrides
from ankiscape.logic.achievement_diary_logic import achievement_cabinet_view_pure
from ankiscape.logic_pure.logic_pure_claims import (
    apply_claim_pure, apply_destroy_claim_pure, claim_rows_pure,
)

# Explicit independent oracle: every regional tier, in catalog/reward order.
EXPECTED = {
    "ardougne_easy": ((1000, 25),),
    "ardougne_medium": ((7500, 45),),
    "ardougne_hard": ((28000, 60),),
    "ardougne_elite": ((50000, 85), (50000, 85), (50000, 85), (50000, 85)),
    "falador_easy": ((1000, 30),),
    "falador_medium": ((5000, 40),),
    "falador_hard": ((10000, 50),),
    "falador_elite": ((50000, 84), (50000, 72), (30000, 90), (30000, 90)),
    "fremennik_easy": ((5000, 30),),
    "fremennik_medium": ((10000, 40),),
    "fremennik_hard": ((15000, 50),),
    "fremennik_elite": ((40000, 89), (30000, 86), (30000, 86), (30000, 86), (30000, 86)),
    "karamja_easy": ((1000, 30),),
    "karamja_medium": ((5000, 40),),
    "karamja_hard": ((10000, 50),),
    "karamja_elite": ((30000, 64), (55000, 87), (55000, 87)),
    "lumbridge_beginner": ((500, 1),),
    "lumbridge_easy": ((1000, 30),),
    "lumbridge_medium": ((1500, 35),),
    "lumbridge_hard": ((9000, 49),),
    "morytania_easy": ((4000, 25),),
    "morytania_medium": ((10000, 46),),
    "morytania_hard": ((20000, 65),),
    "morytania_elite": ((40000, 75), (50000, 80), (50000, 80)),
    "seers_easy": ((1000, 30),),
    "seers_medium": ((5000, 40),),
    "seers_hard": ((10000, 50),),
    "seers_elite": ((25000, 1), (30000, 83), (30000, 83), (30000, 83), (30000, 83)),
    "varrock_easy": ((1000, 30),),
    "varrock_medium": ((5000, 40),),
    "varrock_hard": ((10000, 50),),
    "varrock_elite": ((30000, 65), (40000, 88), (40000, 88), (40000, 88)),
}
# Independent source pins: wiki title, oldid, UTC, reward lines, archive URL,
# UTC, exact supporting archive lines. No production override table imports.
PINS = {
    "ardougne": ("Ardougne", "6579397", "2012-11-18T22:07:06Z", ("279", "480", "685", "795"),
                 "https://web.archive.org/web/20120614213944id_/http://www.tip.it:80/runescape/?page=ardougne_tasks.htm",
                 "2012-06-14T21:39:44Z", ("1021", "1083", "1144", "1205")),
    "falador": ("Falador", "6571459", "2012-11-18T05:31:03Z", ("158", "363", "535", "662-664"),
                "https://web.archive.org/web/20120419111015id_/http://www.tip.it/runescape/?page=falador_tasks.htm",
                "2012-04-19T11:10:15Z", ("888", "943", "1000", "1062")),
    "fremennik": ("Fremennik", "6555812", "2012-11-14T23:17:11Z", ("189", "342", "498", "636-637"),
                  "https://web.archive.org/web/20120328083655id_/http://www.tip.it:80/runescape/?page=fremennik_tasks.htm",
                  "2012-03-28T08:36:55Z", ("921", "982", "1040", "1108")),
    "karamja": ("Karamja", "6372400", "2012-10-09T03:25:58Z", ("171", "412", "576", "706-707"),
                "https://web.archive.org/web/20120805193609id_/http://www.tip.it:80/runescape/?page=karamja_tasks.htm",
                "2012-08-05T19:36:09Z", ("875", "929", "984", "1043")),
    "lumbridge": ("Lumbridge", "6549949", "2012-11-12T17:54:35Z", ("814", "938", "1050"),
                  "https://web.archive.org/web/20120419085553id_/http://www.tip.it/runescape/?page=lumbridge_tasks.htm",
                  "2012-04-19T08:55:53Z", ("1435", "1489", "1547")),
    "morytania": ("Morytania", "6530421", "2012-11-04T03:16:45Z", ("154", "360", "501", "621-622"),
                 "https://web.archive.org/web/20120703001723id_/http://www.tip.it:80/runescape/?page=morytania_tasks.htm",
                 "2012-07-03T00:17:23Z", ("954", "1019", "1083", "1145")),
    "seers": ("Seers%27_Village", "6504286", "2012-10-30T17:38:08Z", ("182", "341", "493", "616"),
              "https://web.archive.org/web/20120419110632id_/http://www.tip.it/runescape/?page=seers_village_tasks.htm",
              "2012-04-19T11:06:32Z", ("813", "874", "937", "994")),
    "varrock": ("Varrock", "6476032", "2012-10-26T14:55:51Z", ("256", "518", "697", "840-841"),
                "https://web.archive.org/web/20121025081303id_/http://www.tip.it:80/runescape/?page=varrock_tasks.htm",
                "2012-10-25T08:13:03Z", ("1054", "1115", "1176", "1238")),
}


def expected_ids(tier_id):
    original = f"achievement_diary_{tier_id}_xp_lamp"
    return tuple(original if i == 1 else f"{original}_{i}" for i in range(1, len(EXPECTED[tier_id]) + 1))


def fresh_claimed(tier_id):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data["achievement_diaries"]["claimed_tiers"] = [tier_id]
    data["claims"].update({key: {"claimed": False} for key in expected_ids(tier_id)})
    return data


class PeriodLampRewardsTest(unittest.TestCase):
    def test_exact_catalog_identifiers_rewards_and_source_pins(self):
        tiers = {t.id: t for f in ACHIEVEMENT_DIARY_CATALOG for t in f.tiers if t.lamps}
        self.assertEqual(list(tiers), list(EXPECTED))
        claims = diary_lamp_claims_as_dict()
        ids = tuple(key for tier_id in EXPECTED for key in expected_ids(tier_id))
        self.assertEqual(len(ids), 53)
        self.assertEqual(tuple(claims), ids)
        self.assertEqual(len(DIARY_LAMP_CLAIM_IDS_BY_TIER), 32)
        for family in ACHIEVEMENT_DIARY_CATALOG:
            for tier in family.tiers:
                self._assert_tier_reward_definitions(family, tier, claims)

    def _assert_tier_reward_definitions(self, family, tier, claims):
        if not tier.lamps:
            self.assertNotIn(tier.id, EXPECTED)
            return
        rewards = EXPECTED[tier.id]
        self.assertEqual(tuple((lamp.experience, lamp.minimum_level) for lamp in tier.lamps), rewards)
        self.assertEqual(DIARY_ALL_LAMP_CLAIM_IDS_BY_TIER[tier.id], expected_ids(tier.id))
        self.assertEqual(DIARY_LAMP_CLAIM_IDS_BY_TIER[tier.id], expected_ids(tier.id)[0])
        for index, (reward, lamp, claim_id) in enumerate(zip(rewards, tier.lamps, expected_ids(tier.id)), 1):
            with self.subTest(claim_id=claim_id):
                self._assert_lamp_claim(family, tier, index, reward, lamp, claims[claim_id])

    def _assert_lamp_claim(self, family, tier, index, reward, lamp, claim):
        xp, floor = reward
        claim_id = expected_ids(tier.id)[index - 1]
        self.assertEqual(CLAIM_DATA[claim_id], claim)
        self.assertEqual(claim["id"], claim_id)
        self.assertEqual(claim["xp_amount"], xp)
        self.assertEqual(claim["minimum_level"], floor)
        self.assertEqual(claim["quantity"], 1)
        self.assertEqual(claim["skill_options"], ())
        self.assertEqual(lamp.skills, ())
        self.assertEqual(claim["required_diary_tier"], tier.id)
        self.assertEqual(claim["required_quest"], "")
        self.assertEqual(claim["required_runecrafting_level"], 0)
        self.assertEqual(claim["claim_type"], "xp_lamp")
        count = len(EXPECTED[tier.id])
        suffix = f" {index} of {count}" if count > 1 else ""
        self.assertEqual(claim["display_name"], f"{family.name} {tier.name}: reward lamp{suffix} ({xp:,} XP)")
        if floor == 1:
            self.assertEqual(lamp.source, "")
            self.assertEqual(claim["source"], tier.source or family.source)
            return
        self.assertEqual(claim["source"], lamp.source)
        self._assert_lamp_source_pin(family.id, tier.id, lamp.source)

    def _assert_lamp_source_pin(self, family_id, tier_id, source):
        name, oldid, date, lines, archive, archive_date, archive_lines = PINS[family_id]
        index = ("easy", "medium", "hard", "elite").index(tier_id.rsplit("_", 1)[1])
        for pin in (f"https://runescape.wiki/w/index.php?title={name}_achievements&oldid={oldid}",
                    date, f"lines {lines[index]}", archive, archive_date,
                    f"lines {archive_lines[index]}"):
            self.assertIn(pin, source)

    def test_overlay_is_idempotent_and_preserves_every_non_lamp_field(self):
        once = apply_lamp_reward_overrides(DIARY_FAMILIES)
        self.assertEqual(once, ACHIEVEMENT_DIARY_CATALOG)
        self.assertEqual(apply_lamp_reward_overrides(once), once)
        self.assertEqual(tuple(f.id for f in once), tuple(f.id for f in DIARY_FAMILIES))
        for old_family, family in zip(DIARY_FAMILIES, once):
            self._assert_family_preserved(old_family, family)

    def _assert_family_preserved(self, old_family, family):
        self.assertEqual(tuple(t.id for t in family.tiers), tuple(t.id for t in old_family.tiers))
        for field in fields(family):
            if field.name != "tiers":
                self.assertIs(getattr(old_family, field.name), getattr(family, field.name))
        for old, tier in zip(old_family.tiers, family.tiers):
            self._assert_non_lamp_tier_preserved(old, tier)

    def _assert_non_lamp_tier_preserved(self, old, tier):
        for field in fields(tier):
            if field.name not in {"lamp", "extra_lamps"}:
                self.assertIs(getattr(old, field.name), getattr(tier, field.name))
        if tier.id in {"lumbridge_beginner", "seers_elite"}:
            self.assertIs(tier.lamp, old.lamp)
            self.assertEqual(tier.lamp.minimum_level, 1)

    def test_existing_positional_constructors_and_original_identifiers_remain_compatible(self):
        lamp = DiaryLamp(100, 2, ("mining",))
        tier = DiaryTier("synthetic", "Easy", 1, "", "", (), lamp, "source", (), 12)
        self.assertEqual(tier.lamps, (lamp,))
        self.assertEqual(tier.designed_task_count, 12)
        self.assertEqual(lamp.source, "")
        self.assertEqual(DiaryTier("empty", "Empty", 1, "", "", ()).lamps, ())
        self.assertEqual(diary_lamp_claim_id("falador_elite"), "achievement_diary_falador_elite_xp_lamp")
        self.assertEqual(diary_lamp_claim_id("falador_elite", 2), "achievement_diary_falador_elite_xp_lamp_2")
        for index in (0, -1):
            with self.assertRaises(ValueError):
                diary_lamp_claim_id("falador_elite", index)

    def test_each_sourced_lamp_refuses_below_and_pays_once_at_its_exact_floor(self):
        trainable = {s.id for s in trainable_skill_definitions()}
        for tier_id, rewards in EXPECTED.items():
            for claim_id, (xp, floor) in zip(expected_ids(tier_id), rewards):
                if floor == 1:
                    continue
                with self.subTest(claim_id=claim_id):
                    data = fresh_claimed(tier_id)
                    data["mining_level"] = floor - 1
                    before = copy.deepcopy(data)
                    row = next(r for r in claim_rows_pure(data, CLAIM_DATA) if r["claim_id"] == claim_id)
                    self.assertEqual(set(row["skill_options"]), trainable)
                    self.assertNotIn("mining", row["eligible_skill_ids"])
                    refused, ok = apply_claim_pure(data, claim_id, CLAIM_DATA, "mining")
                    self.assertFalse(ok)
                    self.assertEqual(refused, before)
                    self.assertEqual(data, before)
                    data["mining_level"] = floor
                    before = copy.deepcopy(data)
                    row = next(r for r in claim_rows_pure(data, CLAIM_DATA) if r["claim_id"] == claim_id)
                    self.assertIn("mining", row["eligible_skill_ids"])
                    paid, ok = apply_claim_pure(data, claim_id, CLAIM_DATA, "mining")
                    self.assertTrue(ok)
                    self.assertEqual(data, before)
                    self.assertEqual(paid["mining_exp"] - before["mining_exp"], xp)
                    expected_claims = copy.deepcopy(before["claims"])
                    expected_claims[claim_id]["claimed"] = True
                    self.assertEqual(paid["claims"], expected_claims)
                    again, ok = apply_claim_pure(paid, claim_id, CLAIM_DATA, "mining")
                    self.assertFalse(ok)
                    self.assertEqual(again, paid)

    def test_sibling_lamps_choose_different_skills_and_destroy_independently(self):
        ids = expected_ids("falador_elite")
        data = fresh_claimed("falador_elite")
        data.update(mining_level=84, attack_level=72)
        data, ok = apply_claim_pure(data, ids[0], CLAIM_DATA, "mining")
        self.assertTrue(ok)
        data, ok = apply_claim_pure(data, ids[1], CLAIM_DATA, "attack")
        self.assertTrue(ok)
        self.assertEqual(data["mining_exp"], 50000)
        self.assertEqual(data["attack_exp"], 50000)
        before = copy.deepcopy(data)
        destroyed, ok = apply_destroy_claim_pure(data, ids[2], CLAIM_DATA)
        self.assertTrue(ok)
        self.assertEqual(data, before)
        self.assertTrue(destroyed["claims"][ids[2]]["forfeited"])
        for sibling in (ids[0], ids[1], ids[3]):
            self.assertEqual(destroyed["claims"][sibling], before["claims"][sibling])
        self.assertFalse(apply_destroy_claim_pure(destroyed, ids[2], CLAIM_DATA)[1])
        self.assertFalse(apply_claim_pure(destroyed, ids[2], CLAIM_DATA, "mining")[1])

    def test_cabinet_preserves_original_scalars_and_projects_each_individual_lamp(self):
        view = achievement_cabinet_view_pure(fresh_claimed("falador_elite"))
        tiers = {t["tier_id"]: t for f in view["families"] for t in f["tiers"]}
        for tier_id, rewards in EXPECTED.items():
            tier = tiers[tier_id]
            self.assertEqual(tier["lamp"]["claim_id"], expected_ids(tier_id)[0])
            self.assertEqual(tier["lamp"]["experience"], rewards[0][0])
            self.assertEqual(tier["lamp"]["minimum_level"], rewards[0][1])
            for lamp, claim_id, (xp, floor) in zip(tier["lamps"], expected_ids(tier_id), rewards):
                self.assertEqual(lamp, {"claim_id": claim_id, "experience": xp, "minimum_level": floor,
                                       "description": f"A {xp:,} XP reward lamp for an eligible level {floor}+ skill will be placed in Bank Claims."})
            if len(rewards) > 1:
                entries = "; ".join(f"{xp:,} XP (level {floor}+)" for xp, floor in rewards)
                self.assertEqual(tier["lamp"]["description"], f"{len(rewards)} reward lamps will be placed in Bank Claims: {entries}.")
            else:
                self.assertEqual(tier["lamp"], tier["lamps"][0])
