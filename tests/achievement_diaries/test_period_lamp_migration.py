"""Legacy payments, forfeiture and missing Elite lamps across real save loads."""

import copy
import unittest
from itertools import product

import pkg_alias  # noqa: F401
from ankiscape.core.constants import CLAIM_DATA, CONSTITUTION_STARTING_EXP, ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import CURRENT_CONFIG_VERSION, default_player_data, migrate_loaded_data
from ankiscape.data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG
from ankiscape.logic.achievement_diaries.lamp_migration import migrate_missing_diary_lamps_pure
from ankiscape.logic_pure.logic_pure_claims import apply_claim_pure, apply_destroy_claim_pure, claim_rows_pure
from tests.achievement_diaries.test_period_lamp_rewards import EXPECTED, expected_ids

ELITES = tuple(tier_id for tier_id in EXPECTED if tier_id.endswith("_elite"))
ORIGINAL_STATES = ({"claimed": False}, {"claimed": True}, {"claimed": False, "forfeited": True})


def load(data):
    return migrate_loaded_data(copy.deepcopy(data), ORE_DATA, ITEM_DEFINITIONS)


def xp_and_equipment(data):
    xp = {key: value for key, value in data.items() if key.endswith("_exp")}
    # Full loads also run the existing v111 starting-XP migration. Compare
    # against that established baseline; the lamp migration itself pays no XP.
    if data["config_version"] < 111:
        xp["constitution_exp"] += CONSTITUTION_STARTING_EXP
    return (xp,
            {key: value for key, value in data["inventory"].items() if value}, data["equipment"])


class PeriodLampMigrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fresh = default_player_data(ORE_DATA, ITEM_DEFINITIONS)

    def _legacy(self, version, tier_id):
        data = copy.deepcopy(self.fresh)
        data["config_version"] = version
        data["achievement_diaries"]["claimed_tiers"] = [tier_id]
        data["mining_exp"] = 123456.0
        data["attack_exp"] = 654321.0
        # Pre-v111 saves record earned Constitution XP without starting XP.
        data["constitution_exp"] = 0
        data["inventory"]["Coins"] = 271
        tier = next((t for f in ACHIEVEMENT_DIARY_CATALOG for t in f.tiers if t.id == tier_id), None)
        if tier is not None and tier.reward_item:
            data["inventory"][tier.reward_item] = 1
        return data

    def test_v106_v107_v124_add_only_missing_elite_lamps_for_every_original_state(self):
        self.assertEqual(CURRENT_CONFIG_VERSION, 125)
        for version, tier_id, original in product((106, 107, 124), ELITES, ORIGINAL_STATES):
            with self.subTest(version=version, tier_id=tier_id, original=original):
                self._assert_legacy_reward(version, tier_id, original)

    def _assert_legacy_reward(self, version, tier_id, original):
        data = self._legacy(version, tier_id)
        ids = expected_ids(tier_id)
        data["claims"][ids[0]] = copy.deepcopy(original)
        before = copy.deepcopy(data)
        migrated = load(data)
        self.assertEqual(data, before)
        self.assertEqual(xp_and_equipment(migrated), xp_and_equipment(before))
        self.assertEqual(migrated["achievement_diaries"]["claimed_tiers"], [tier_id])
        expected_original = dict(original)
        if version < 107:
            expected_original["claimed"] = True
        self.assertEqual(migrated["claims"][ids[0]], expected_original)
        for claim_id in ids[1:]:
            self.assertEqual(migrated["claims"][claim_id], {"claimed": False})
        available = {
            row["claim_id"] for row in claim_rows_pure(migrated, CLAIM_DATA)
            if row["eligible"] and row["claim_id"].startswith("achievement_diary_")
        }
        expected_available = set(ids[1:])
        if not expected_original.get("claimed") and not expected_original.get("forfeited"):
            expected_available.add(ids[0])
        self.assertEqual(available, expected_available)
        if tier_id == "falador_elite":
            self._assert_falador_assignment(migrated, expected_original)

    def _assert_falador_assignment(self, migrated, original):
        ids = expected_ids("falador_elite")
        self.assertEqual(tuple((CLAIM_DATA[key]["xp_amount"], CLAIM_DATA[key]["minimum_level"]) for key in ids),
                         ((50000, 84), (50000, 72), (30000, 90), (30000, 90)))
        migrated["attack_level"] = 72
        before = copy.deepcopy(migrated)
        self.assertFalse(apply_claim_pure(migrated, ids[0], CLAIM_DATA, "attack")[1])
        paid, ok = apply_claim_pure(migrated, ids[1], CLAIM_DATA, "attack")
        self.assertTrue(ok)
        self.assertEqual(paid["attack_exp"] - before["attack_exp"], 50000)
        self.assertEqual(paid["claims"][ids[0]], original)
        self.assertEqual(migrated, before)

    def test_existing_additional_claim_states_are_preserved_for_every_old_version(self):
        for version in (106, 107, 124):
            for tier_id in ELITES:
                for state in ORIGINAL_STATES:
                    with self.subTest(version=version, tier_id=tier_id, additional=state):
                        data = self._legacy(version, tier_id)
                        ids = expected_ids(tier_id)
                        data["claims"][ids[1]] = copy.deepcopy(state)
                        migrated = load(data)
                        self.assertEqual(migrated["claims"][ids[1]], state)
                        self.assertEqual(xp_and_equipment(migrated), xp_and_equipment(data))
                        for claim_id in ids[2:]:
                            self.assertEqual(migrated["claims"][claim_id], {"claimed": False})

    def test_absent_pre_v107_original_is_retired_without_repaying_any_experience(self):
        for tier_id in ELITES:
            with self.subTest(tier_id=tier_id):
                data = self._legacy(106, tier_id)
                ids = expected_ids(tier_id)
                self.assertNotIn(ids[0], data["claims"])
                migrated = load(data)
                self.assertEqual(migrated["claims"][ids[0]], {"claimed": True})
                self.assertEqual(xp_and_equipment(migrated), xp_and_equipment(data))
                for claim_id in ids[1:]:
                    self.assertEqual(migrated["claims"][claim_id], {"claimed": False})
                migrated["mining_level"] = 99
                self.assertFalse(apply_claim_pure(migrated, ids[0], CLAIM_DATA, "mining")[1])

    def test_missing_lamp_migration_itself_changes_only_the_missing_claim_entries(self):
        for version in (106, 107, 124):
            for tier_id in ELITES:
                data = self._legacy(version, tier_id)
                ids = expected_ids(tier_id)
                data["claims"][ids[0]] = {"claimed": True}
                before = copy.deepcopy(data)
                migrate_missing_diary_lamps_pure(data, version)
                expected = copy.deepcopy(before)
                expected["claims"].update({key: {"claimed": False} for key in ids[1:]})
                self.assertEqual(data, expected)
                # No tasks, equipment, experience or original state changes.
                data["claims"] = before["claims"]
                self.assertEqual(data, before)

    def test_current_and_future_migration_is_noop_and_does_not_rebuild_missing_claims(self):
        for version in (125, 126):
            for tier_id in ELITES:
                for original in ORIGINAL_STATES:
                    with self.subTest(version=version, tier_id=tier_id, original=original):
                        data = self._legacy(version, tier_id)
                        ids = expected_ids(tier_id)
                        data["claims"][ids[0]] = copy.deepcopy(original)
                        before = copy.deepcopy(data)
                        migrate_missing_diary_lamps_pure(data, version)
                        self.assertEqual(data, before)
                        migrated = load(data)
                        self.assertEqual(migrated["claims"][ids[0]], original)
                        for claim_id in ids[1:]:
                            self.assertNotIn(claim_id, migrated["claims"])
                        self.assertEqual(xp_and_equipment(migrated), xp_and_equipment(before))

    def test_spent_and_destroyed_additional_lamps_survive_second_load(self):
        for version in (106, 107, 124):
            for tier_id in ELITES:
                with self.subTest(version=version, tier_id=tier_id):
                    data = load(self._legacy(version, tier_id))
                    data["mining_level"] = 99
                    ids = expected_ids(tier_id)
                    data, ok = apply_claim_pure(data, ids[1], CLAIM_DATA, "mining")
                    self.assertTrue(ok)
                    data, ok = apply_destroy_claim_pure(data, ids[2], CLAIM_DATA)
                    self.assertTrue(ok)
                    before = copy.deepcopy(data)
                    reloaded = load(data)
                    self.assertEqual(reloaded["claims"], before["claims"])
                    self.assertEqual(xp_and_equipment(reloaded), xp_and_equipment(before))
                    self.assertFalse(apply_claim_pure(reloaded, ids[1], CLAIM_DATA, "mining")[1])
                    self.assertFalse(apply_claim_pure(reloaded, ids[2], CLAIM_DATA, "mining")[1])
                    self.assertFalse(apply_destroy_claim_pure(reloaded, ids[2], CLAIM_DATA)[1])

    def test_unclaimed_tiers_are_gated_and_unrelated_claim_sanitation_is_unchanged(self):
        for version in (106, 107, 124, 125, 126):
            data = self._legacy(version, "not_a_diary_tier")
            data["achievement_diaries"]["claimed_tiers"].append("falador_easy")
            data["claims"]["unrelated_unknown_claim"] = {"claimed": True}
            data["claims"][expected_ids("falador_elite")[1]] = False
            migrated = load(data)
            self.assertNotIn("unrelated_unknown_claim", migrated["claims"])
            self.assertNotIn("achievement_diary_not_a_diary_tier_xp_lamp", migrated["claims"])
            self.assertEqual(migrated["claims"][expected_ids("falador_elite")[1]], {"claimed": False})
            migrated["mining_level"] = 99
            for tier_id in ELITES:
                for claim_id in expected_ids(tier_id):
                    self.assertFalse(apply_claim_pure(migrated, claim_id, CLAIM_DATA, "mining")[1])
                    self.assertFalse(apply_destroy_claim_pure(migrated, claim_id, CLAIM_DATA)[1])
            self.assertEqual(xp_and_equipment(migrated), xp_and_equipment(data))
