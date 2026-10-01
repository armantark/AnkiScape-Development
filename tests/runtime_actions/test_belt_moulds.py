"""Crafting and Smithing take their moulds from the 2012 tool belt, as quests and Farming do."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import CRAFTING_DATA, QUEST_UNLOCK_RULES, SMITHING_DATA
from ankiscape.logic_pure.logic_pure import crafting_target_locked_reasons_pure, smithing_target_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_crafting_answer, handle_smithing_answer
from ankiscape.runtime.runtime_actions_carried_overlay import run_answer_with_carried_overlay
from tests.test_runtime_actions import _bankstanding_context


def _crafter(target: str, inventory: dict, **extra) -> dict:
    return {
        "inventory": dict(inventory),
        "crafting_level": 60,
        "crafting_exp": 0,
        "smithing_level": 60,
        "smithing_exp": 0,
        "current_craft": target,
        "current_smith": target,
        "completed_achievements": [],
        **extra,
    }


class BeltMouldTest(unittest.TestCase):
    def _review(self, player_data, skill: str, handler):
        calls = {"xp": [], "saves": 0, "errors": []}
        ok = run_answer_with_carried_overlay(_bankstanding_context(player_data, calls), skill, handler)
        return ok, calls

    def test_added_chain_link_mould_crafts_silvthril_chain_from_the_belt(self) -> None:
        bars = {"Silver bar": 2, "Mithril bar": 2}
        player_data = _crafter("silver_silvthrill_chain", bars, toolbelt_added=["Chain link mould"])
        self.assertEqual(
            crafting_target_locked_reasons_pure(player_data, "silver_silvthrill_chain", CRAFTING_DATA, QUEST_UNLOCK_RULES),
            (),
        )

        ok, calls = self._review(player_data, "crafting", handle_crafting_answer)

        self.assertTrue(ok, calls)
        self.assertEqual(player_data["inventory"], {"Silver bar": 1, "Mithril bar": 1, "Silvthril chain": 1})
        self.assertEqual(player_data["crafting_exp"], 100.0)
        self.assertNotIn("bankstanding", calls)

    def test_chain_link_mould_neither_added_nor_banked_still_blocks_the_chain(self) -> None:
        player_data = _crafter("silver_silvthrill_chain", {"Silver bar": 1, "Mithril bar": 1})
        self.assertIn(
            "materials",
            crafting_target_locked_reasons_pure(player_data, "silver_silvthrill_chain", CRAFTING_DATA, QUEST_UNLOCK_RULES),
        )

        ok, calls = self._review(player_data, "crafting", handle_crafting_answer)

        self.assertFalse(ok)
        self.assertIn("Chain link mould", " ".join(calls["bankstanding_reasons"]))
        self.assertEqual(player_data["inventory"], {"Silver bar": 1, "Mithril bar": 1})

    def test_always_on_ring_mould_needs_no_bank_copy(self) -> None:
        player_data = _crafter("jewellery_gold_ring", {"Gold bar": 3})

        ok, calls = self._review(player_data, "crafting", handle_crafting_answer)

        self.assertTrue(ok, calls)
        self.assertEqual(player_data["inventory"], {"Gold bar": 2, "Gold ring": 1})

    def test_added_ammo_mould_casts_cannonballs_from_the_belt(self) -> None:
        player_data = _crafter(
            "forge_cannonballs",
            {"Steel bar": 2},
            toolbelt_added=["Ammo mould"],
            quests={"dwarf_cannon": {"started": True, "completed": True, "progress": 13}},
        )
        self.assertEqual(
            smithing_target_locked_reasons_pure(player_data, "forge_cannonballs", SMITHING_DATA, QUEST_UNLOCK_RULES),
            (),
        )

        ok, calls = self._review(player_data, "smithing", handle_smithing_answer)

        self.assertTrue(ok, calls)
        self.assertEqual(player_data["inventory"], {"Steel bar": 1, "Cannonball": 4})


if __name__ == "__main__":
    unittest.main()
