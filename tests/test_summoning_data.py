import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.summoning_data import (
    SOURCE_DURATION_UNITS_PER_REVIEW,
    SUMMONING_ACTIONS,
    SUMMONING_ACTIONS_BY_ID,
    SUMMONING_POUCHES,
    SUMMONING_POUCHES_BY_ID,
    summoning_extra_items_as_dict,
)
from ankiscape.generated.summoning_data_generated import (
    SUMMONING_FAMILIAR_OLDID,
    SUMMONING_POUCH_OLDID,
    SUMMONING_SCROLL_OLDID,
)


class SummoningDataTests(unittest.TestCase):
    def test_full_surface_catalog_excludes_closed_session_rows(self):
        self.assertEqual(len(SUMMONING_POUCHES), 80)
        self.assertEqual(len(SUMMONING_ACTIONS), 145)
        self.assertEqual(
            sum(action.family == "infuse" for action in SUMMONING_ACTIONS), 78
        )
        self.assertEqual(
            sum(action.family == "scroll" for action in SUMMONING_ACTIONS), 67
        )
        searchable = " ".join(
            pouch.familiar_name + " " + pouch.pouch_name
            for pouch in SUMMONING_POUCHES
        ).casefold()
        for forbidden in (
            "bloodrager",
            "stormbringer",
            "hoardstalker",
            "skinweaver",
            "worldbearer",
            "deathslinger",
            "clay familiar",
        ):
            self.assertNotIn(forbidden, searchable)

    def test_pinned_wiki_revisions_and_source_shaped_pack_yak_row(self):
        self.assertEqual(SUMMONING_POUCH_OLDID, 6438719)
        self.assertEqual(SUMMONING_SCROLL_OLDID, 6520851)
        self.assertEqual(SUMMONING_FAMILIAR_OLDID, 6579789)
        pack_yak = SUMMONING_POUCHES_BY_ID["packyak"]
        self.assertEqual(pack_yak.level, 96)
        self.assertEqual(pack_yak.shards, 211)
        self.assertEqual(pack_yak.charm, "Crimson charm")
        self.assertEqual(pack_yak.tertiaries, ("Yak-hide",))
        self.assertEqual(pack_yak.creation_xp, 422.4)
        self.assertEqual(pack_yak.duration_source_minutes, 58)
        self.assertEqual(pack_yak.summoning_point_cost, 10)
        self.assertEqual(pack_yak.bob_capacity, 30)
        self.assertEqual(pack_yak.scroll_name, "Winter storage scroll")
        self.assertEqual(pack_yak.scroll_use_xp, 4.8)
        self.assertEqual(pack_yak.special_points, 12)

    def test_multi_tertiary_semantics_preserve_alternative_and_all_inputs(self):
        spirit_cobra = SUMMONING_POUCHES_BY_ID["spiritcobra"]
        self.assertEqual(
            spirit_cobra.tertiaries, ("Snake hide", "Snake hide (swamp)")
        )
        self.assertEqual(spirit_cobra.tertiary_mode, "any")

        ice_titan = SUMMONING_POUCHES_BY_ID["icetitan"]
        self.assertEqual(
            ice_titan.tertiaries, ("Air talisman", "Water talisman")
        )
        self.assertEqual(ice_titan.tertiary_mode, "all")

        wolpertinger = SUMMONING_POUCHES_BY_ID["wolpertinger"]
        self.assertEqual(
            wolpertinger.tertiaries, ("Raw rabbit", "Wolf bones")
        )
        self.assertEqual(wolpertinger.tertiary_mode, "all")

    def test_shared_scroll_targets_accept_each_matching_pouch(self):
        call_to_arms = SUMMONING_ACTIONS_BY_ID["scroll_calltoarms"]
        self.assertEqual(
            call_to_arms.input_items,
            (
                "Void ravager pouch",
                "Void shifter pouch",
                "Void spinner pouch",
                "Void torcher pouch",
            ),
        )
        self.assertEqual(call_to_arms.output_item, "Call to arms scroll")
        self.assertEqual(call_to_arms.output_quantity, 10)

        petrifying_gaze = SUMMONING_ACTIONS_BY_ID["scroll_petrifyinggaze"]
        self.assertEqual(len(petrifying_gaze.input_items), 7)

    def test_non_infusion_period_familiars_are_visible_but_not_craftable(self):
        non_craftable = {
            pouch.id: pouch.acquisition
            for pouch in SUMMONING_POUCHES
            if not pouch.craftable
        }
        self.assertEqual(
            non_craftable,
            {
                "meerkats": "Treasure Trails casket reward",
                "ghast": "Temple Trekking / Burgh de Rott Ramble reward",
            },
        )
        self.assertNotIn("infuse_meerkats", SUMMONING_ACTIONS_BY_ID)
        self.assertNotIn("infuse_ghast", SUMMONING_ACTIONS_BY_ID)
        ghast = SUMMONING_POUCHES_BY_ID["ghast"]
        self.assertEqual(ghast.summon_xp, 1.8)
        self.assertEqual(ghast.scroll_name, "Ghastly request scroll")
        self.assertEqual(ghast.scroll_use_xp, 0.9)
        self.assertEqual(ghast.special_points, 20)

    def test_review_lifetime_mapping_is_bounded_and_ratio_preserving(self):
        self.assertEqual(SOURCE_DURATION_UNITS_PER_REVIEW, 2)
        dreadfowl = SUMMONING_POUCHES_BY_ID["dreadfowl"]
        pack_yak = SUMMONING_POUCHES_BY_ID["packyak"]
        rune_minotaur = SUMMONING_POUCHES_BY_ID["runeminotaur"]
        self.assertEqual(dreadfowl.lifetime_reviews, 2)
        self.assertEqual(pack_yak.lifetime_reviews, 29)
        self.assertEqual(rune_minotaur.lifetime_reviews, 76)
        self.assertLess(
            dreadfowl.lifetime_reviews,
            pack_yak.lifetime_reviews,
        )
        self.assertLess(
            pack_yak.lifetime_reviews,
            rune_minotaur.lifetime_reviews,
        )

    def test_generated_items_preserve_source_ids(self):
        items = summoning_extra_items_as_dict()
        self.assertEqual(items["Pouch"]["source_item_id"], 12155)
        self.assertEqual(items["Spirit shards"]["source_item_id"], 12183)
        self.assertEqual(items["Spirit wolf pouch"]["source_item_id"], 12047)
        self.assertEqual(items["Howl scroll"]["source_item_id"], 12425)
        self.assertEqual(items["Ghast pouch"]["source_item_id"], 21444)
        self.assertEqual(items["Swamp toad"]["source_item_id"], 2150)
        self.assertFalse(items["Swamp toad"]["stackable"])
        self.assertTrue(items["Swamp toad"]["tradeable"])


if __name__ == "__main__":
    unittest.main()
