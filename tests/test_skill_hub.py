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
        self.assertEqual(set(by_id), {"gathering", "artisan"})

        self.assertEqual(
            [card.display_name for card in by_id["gathering"].skills],
            ["Mining", "Woodcutting"],
        )
        self.assertEqual(
            [card.display_name for card in by_id["artisan"].skills],
            ["Smithing", "Crafting", "Fletching"],
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

        # A genuinely unimplemented skill stays visible-but-unselectable here.
        self.assertIn("slayer", cards)
        self.assertFalse(cards["slayer"].implemented)
        self.assertFalse(cards["slayer"].selectable_for_review)

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
        self.assertEqual(first_category_id(build_skill_hub(include_planned=False)), "gathering")


if __name__ == "__main__":
    unittest.main()
