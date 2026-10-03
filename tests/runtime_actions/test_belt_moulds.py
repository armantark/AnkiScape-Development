"""Crafting and Smithing take their moulds from the 2012 tool belt, as quests and Farming do."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import CRAFTING_DATA, FLETCHING_DATA, QUEST_UNLOCK_RULES, SMITHING_DATA
from ankiscape.logic_pure.logic_pure import crafting_target_locked_reasons_pure, fletching_target_locked_reasons_pure, smithing_target_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_crafting_answer, handle_fletching_answer, handle_smithing_answer
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

    def test_long_kebbit_bolts_use_the_belt_chisel_without_consuming_a_bank_copy(self) -> None:
        target = "fletch_long_kebbit_bolts"
        for bank_chisels in (0, 2):
            with self.subTest(bank_chisels=bank_chisels):
                player = _crafter(
                    target, {"Long kebbit spike": 2, "Chisel": bank_chisels},
                    fletching_level=42, current_fletch=target,
                )
                self.assertEqual(fletching_target_locked_reasons_pure(player, target, FLETCHING_DATA), ())
                ok, calls = self._review(player, "fletching", handle_fletching_answer)
                self.assertTrue(ok, calls)
                self.assertEqual(player["inventory"], {"Long kebbit spike": 1, "Chisel": bank_chisels, "Long kebbit bolts": 6})
                self.assertAlmostEqual(player["fletching_exp"], 7.98)

    def test_belt_chisel_does_not_replace_a_missing_long_kebbit_spike(self) -> None:
        target = "fletch_long_kebbit_bolts"
        player = _crafter(target, {}, fletching_level=42, current_fletch=target)
        ok, calls = self._review(player, "fletching", handle_fletching_answer)
        self.assertFalse(ok)
        self.assertIn("Long kebbit spike", " ".join(calls["bankstanding_reasons"]))
        self.assertNotIn("Chisel", " ".join(calls["bankstanding_reasons"]))
        self.assertEqual(player["inventory"].get("Long kebbit spike", 0), 0)
        self.assertNotIn("Long kebbit bolts", player["inventory"])
        self.assertNotIn("fletching_exp", player)

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
