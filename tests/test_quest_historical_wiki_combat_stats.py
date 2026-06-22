import unittest

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


if __name__ == "__main__":
    unittest.main()
