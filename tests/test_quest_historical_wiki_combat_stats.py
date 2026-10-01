import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import QUEST_DATA
from ankiscape.logic_pure import logic_pure_quest
from tools import audit_quest_combat_stat_gaps as gap_audit
from tools import audit_quest_historical_wiki_combat_stats as wiki_audit


KHazard_SCORPION_2012 = """
{{Infobox Monster
|name = Khazard scorpion
|level = 44
|LP = 290
|attack style = Crush
|max hit = 50 (approx)
}}
"""


SOURCE_BACKED_MELEE_STATS = """
{{Infobox Monster
|name = Sourced melee creature
|level = 44
|LP = 290
|attack style = Crush
|attack = 31
|strength = 35
|defence = 29
|max hit = 50
}}
"""


def _gap(display_name: str, level: int = 44) -> gap_audit.CombatGap:
    return gap_audit.CombatGap(
        quest_id="proof_quest",
        quest_name="Proof Quest",
        stage=2,
        display_name=display_name,
        level=level,
        quantity=1,
        source_text=f"{display_name} - level {level}",
        source="https://runescape.wiki/w/Proof_Quest?oldid=1",
    )


class TestQuestHistoricalWikiCombatStats(unittest.TestCase):
    def test_infobox_lp_and_style_only_do_not_satisfy_resolver_stats(self):
        stats, configs = wiki_audit.parse_monster_infobox_metadata(KHazard_SCORPION_2012)

        self.assertEqual(stats, {"hitpoints": 290})
        self.assertEqual(configs, {"attack_style": "melee", "max_hit": "50"})
        self.assertFalse(wiki_audit.metadata_has_resolver_stats(stats, configs))

    def test_explicit_hidden_melee_stats_are_detected_as_resolver_ready(self):
        stats, configs = wiki_audit.parse_monster_infobox_metadata(SOURCE_BACKED_MELEE_STATS)

        self.assertEqual(stats["attack"], 31)
        self.assertEqual(stats["strength"], 35)
        self.assertEqual(stats["defence"], 29)
        self.assertTrue(wiki_audit.metadata_has_resolver_stats(stats, configs))

    def test_title_candidates_include_monster_variant_and_strip_variant_suffix(self):
        self.assertEqual(
            wiki_audit.title_candidates("Lava monster (Elder Kiln)"),
            ("Lava monster (Elder Kiln)", "Lava monster (Elder Kiln) (monster)", "Lava monster", "Lava monster (monster)"),
        )

    def test_gap_audit_prefers_resolver_ready_historical_page_when_available(self):
        pages = {
            "Khazard scorpion": wiki_audit.HistoricalRevision(
                requested_title="Khazard scorpion",
                resolved_title="Khazard scorpion",
                oldid=6372282,
                timestamp="2012-10-09T00:43:09Z",
                content=KHazard_SCORPION_2012,
            ),
            "Sourced melee creature": wiki_audit.HistoricalRevision(
                requested_title="Sourced melee creature",
                resolved_title="Sourced melee creature",
                oldid=1,
                timestamp="2012-10-09T00:43:09Z",
                content=SOURCE_BACKED_MELEE_STATS,
            ),
        }

        rows = wiki_audit.audit_gaps(
            (_gap("Khazard scorpion"), _gap("Sourced melee creature")),
            fetch_revision=pages.get,
        )

        self.assertEqual(rows[0].status, "historical_wiki_metadata_only")
        self.assertEqual(rows[1].status, "historical_wiki_resolver_stats_available")
        self.assertEqual(rows[1].source_url, "https://runescape.wiki/w/Sourced_melee_creature?oldid=1")

    def test_count_draynor_uses_owned_garlic_without_mutating_source_stats(self):
        target_id = "quest:vampyre_slayer:vampyre_slayer_count_draynor_37"
        captured = []

        def resolve_once(data, enemies, *_args, **_kwargs):
            captured.append(dict(enemies[target_id]["stats"]))
            return data, True, {
                "reason": "combat_burst",
                "killed": False,
                "died": False,
                "enemy_lifepoints": 100,
            }

        for inventory, carried, expected in (
            ({"Stake": 1, "Stake hammer": 1}, {}, (25, 30)),
            ({"Stake": 1, "Stake hammer": 1, "Garlic": 1}, {}, (20, 25)),
            ({"Stake": 1, "Stake hammer": 1}, {target_id: {"Garlic": 1}}, (25, 30)),
        ):
            player = {
                "inventory": inventory,
                "carried_inventory": carried,
                "quests": {"vampyre_slayer": {"started": True, "progress": 3, "completed": False}},
                "attack_level": 40,
                "strength_level": 40,
                "defense_level": 35,
                "constitution_level": 40,
            }
            with patch.object(logic_pure_quest, "apply_combat_burst_pure", side_effect=resolve_once):
                _, ok, _ = logic_pure_quest.apply_quest_combat_encounter_pure(
                    player, "vampyre_slayer", QUEST_DATA
                )
            self.assertTrue(ok)
            self.assertEqual((captured[-1]["strength"], captured[-1]["defence"]), expected)

        encounter = QUEST_DATA["vampyre_slayer"]["stage_requirements"][2]["combat_encounters"][0]
        self.assertEqual((encounter["npc_stats"]["strength"], encounter["npc_stats"]["defence"]), (25, 30))


if __name__ == "__main__":
    unittest.main()
