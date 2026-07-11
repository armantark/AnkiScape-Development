import unittest

from skill_hub import (
    CATEGORY_DISPLAY_NAMES,
    CATEGORY_ORDER,
    build_skill_hub,
    first_category_id,
)


class TestSkillHubViewModel(unittest.TestCase):
    def test_normal_mode_shows_only_playable_categories_and_skills(self):
        hub = build_skill_hub(include_planned=False)
        by_id = {cat.category_id: cat for cat in hub}

        # Only the categories that currently have implemented skills should show.
        self.assertEqual(set(by_id), {"combat", "gathering", "artisan", "support"})

        self.assertEqual(
            [card.display_name for card in by_id["gathering"].skills],
            ["Mining", "Woodcutting", "Fishing", "Hunter"],
        )
        self.assertEqual([card.display_name for card in by_id["support"].skills], ["Prayer"])
        self.assertEqual([card.display_name for card in by_id["combat"].skills], ["Magic"])
        self.assertEqual(
            [card.display_name for card in by_id["artisan"].skills],
            ["Smithing", "Crafting", "Fletching", "Firemaking", "Cooking", "Runecrafting", "Herblore", "Construction"],
        )
        for cat in hub:
            for card in cat.skills:
                self.assertTrue(card.implemented)
                self.assertTrue(card.selectable_for_review)

    def test_category_order_is_stable_and_combat_precedes_support(self):
        hub = build_skill_hub(include_planned=True)
        rendered = [cat.category_id for cat in hub]
        self.assertEqual(rendered, [c for c in CATEGORY_ORDER if c in set(rendered)])
        self.assertLess(rendered.index("combat"), rendered.index("support"))

    def test_developer_mode_exposes_planned_skills_as_unselectable(self):
        hub = build_skill_hub(include_planned=True)
        cards = {card.skill_id: card for cat in hub for card in cat.skills}

        # Fletching's frontend target panel has landed, so it is now a fully
        # playable, selectable hub skill rather than a hidden backend pilot.
        self.assertIn("fletching", cards)
        self.assertTrue(cards["fletching"].implemented)
        self.assertTrue(cards["fletching"].selectable_for_review)
        self.assertIn("firemaking", cards)
        self.assertTrue(cards["firemaking"].implemented)
        self.assertTrue(cards["firemaking"].selectable_for_review)
        self.assertIn("fishing", cards)
        self.assertTrue(cards["fishing"].implemented)
        self.assertTrue(cards["fishing"].selectable_for_review)
        self.assertIn("cooking", cards)
        self.assertTrue(cards["cooking"].implemented)
        self.assertTrue(cards["cooking"].selectable_for_review)
        self.assertIn("runecrafting", cards)
        self.assertTrue(cards["runecrafting"].implemented)
        self.assertTrue(cards["runecrafting"].selectable_for_review)
        self.assertIn("hunter", cards)
        self.assertTrue(cards["hunter"].implemented)
        self.assertTrue(cards["hunter"].selectable_for_review)

        # A genuinely unimplemented skill stays visible-but-unselectable here.
        self.assertIn("slayer", cards)
        self.assertFalse(cards["slayer"].implemented)
        self.assertFalse(cards["slayer"].selectable_for_review)
        self.assertTrue(cards["prayer"].implemented)
        self.assertTrue(cards["prayer"].selectable_for_review)
        self.assertTrue(cards["magic"].implemented)
        self.assertTrue(cards["magic"].selectable_for_review)
        for skill_id in ("summoning",):
            self.assertIn(skill_id, cards)
            self.assertFalse(cards[skill_id].implemented)
            self.assertFalse(cards[skill_id].selectable_for_review)
        self.assertEqual(cards["magic"].surface_state, "complete")
        self.assertEqual(cards["prayer"].surface_state, "complete")
        for skill_id in ("attack", "constitution", "defense", "ranged", "strength"):
            self.assertNotIn(skill_id, cards)

        # Implemented skills remain trainable in developer mode.
        self.assertTrue(cards["mining"].selectable_for_review)

    def test_empty_utility_category_is_omitted_until_actions_exist(self):
        for include_planned in (False, True):
            hub = build_skill_hub(include_planned=include_planned)
            self.assertNotIn("utility", {cat.category_id for cat in hub})

    def test_display_names_are_defined_for_every_ordered_category(self):
        for category_id in CATEGORY_ORDER:
            self.assertIn(category_id, CATEGORY_DISPLAY_NAMES)

    def test_first_category_id_handles_empty_and_populated_hubs(self):
        self.assertEqual(first_category_id(()), "")
        self.assertEqual(first_category_id(build_skill_hub(include_planned=False)), "combat")


if __name__ == "__main__":
    unittest.main()
