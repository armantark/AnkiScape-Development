"""Claim presentation keeps the reward concise and the choice explicit."""
import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic_pure.logic_pure_claims import claim_rows_pure


class ClaimDisplayTest(unittest.TestCase):
    def test_choice_and_fixed_lamps_keep_rules_in_tooltips_and_unmet_levels_on_rows(self):
        claims = {
            "any": {"claim_type": "xp_lamp", "xp_amount": 1000, "minimum_level": 75},
            "group": {"claim_type": "xp_lamp", "xp_amount": 500, "skill_options": ("agility", "thieving")},
            "fixed": {"claim_type": "xp_lamp", "xp_amount": 1000, "skill_options": ("agility",), "minimum_level": 75},
        }
        rows = {row["claim_id"]: row for row in claim_rows_pure({}, claims)}
        self.assertEqual(rows["any"]["tooltip"], "Choose any skill. Minimum level: 75.")
        self.assertEqual(rows["any"]["metadata"], "1,000 XP · Any skill · Minimum level: 75")
        self.assertEqual(rows["group"]["tooltip"], "Choose: Agility, Thieving.")
        self.assertEqual(rows["group"]["metadata"], "500 XP · Agility, Thieving")
        self.assertEqual(rows["fixed"]["metadata"], "1,000 XP · Agility · Minimum level: 75")
        rows = {row["claim_id"]: row for row in claim_rows_pure({"agility_level": 75}, claims)}
        self.assertEqual(rows["fixed"]["metadata"], "1,000 XP · Agility")
        self.assertEqual(rows["any"]["metadata"], "1,000 XP · Any skill")
        self.assertEqual(rows["fixed"]["tooltip"], "Pays Agility. Minimum level: 75.")

    def test_item_bundle_and_skill_reward_keep_their_display_rules(self):
        claims = {
            "item": {"item_name": "Wicked hood", "display_name": "Hood", "quantity": 1},
            "bundle": {"claim_type": "item_bundle", "display_name": "Supplies", "items": (("Coins", 10), ("Shark", 2))},
            "reward": {"claim_type": "skill_reward", "display_name": "Agility reward", "items": (("Coins", 5),), "xp_amount": 20000, "skill_options": ("agility",)},
        }
        rows = {row["claim_id"]: row for row in claim_rows_pure({}, claims)}
        self.assertEqual((rows["item"]["title"], rows["item"]["metadata"], rows["item"]["icon_name"]), ("Hood x1", "Ready to claim", "Wicked hood"))
        self.assertEqual((rows["bundle"]["title"], rows["bundle"]["metadata"], rows["bundle"]["icon_name"]), ("Supplies", "2 item stacks - Coins x10, Shark x2", "Coins"))
        self.assertEqual(rows["bundle"]["tooltip"], "Coins x10\nShark x2")
        self.assertEqual((rows["reward"]["title"], rows["reward"]["metadata"], rows["reward"]["icon_name"]), ("Agility reward", "20,000 Agility XP · 1 item rewards", "Coins"))
        self.assertTrue(all(row["action_label"] == "Claim" for row in rows.values()))
