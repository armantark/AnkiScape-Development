import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.collection_log_logic import (
    collection_totals_pure,
    drop_log_view_pure,
)


_ENEMIES = {
    "chicken": {
        "display_name": "Chicken",
        "level": 1,
        "group": "Lumbridge",
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "slots": (
                        {"item": "Feather", "quantity": 5, "slots": 8},
                        {
                            "table": {
                                "slots": (
                                    {"item": "Rare gem", "quantity": 1, "slots": 1},
                                )
                            },
                            "slots": 1,
                        },
                    )
                },
            ),
        },
    },
    "empty": {
        "display_name": "No-drop target",
        "level": 2,
        "group": "Elsewhere",
        "drops": {},
    },
    "hidden_encounter": {
        "display_name": "Hidden encounter",
        "level": 99,
        "group": "Elsewhere",
        "encounter_only": True,
        "drops": {"guaranteed": (("Hidden trophy", 1),)},
    },
}


class TestCollectionLogLogic(unittest.TestCase):
    def test_target_stays_concealed_until_killed_then_observations_collect(self):
        player = {
            "combat_kill_counts": {},
            "combat_observed_drops": {},
            "music_log": {"version": 1, "unlocked_tracks": []},
        }

        hidden = drop_log_view_pure(player, _ENEMIES, target_id="chicken")

        self.assertEqual(hidden["total"], 3)
        self.assertEqual(hidden["collected"], 0)
        self.assertEqual([row["label"] for row in hidden["rows"]], ["???"] * 3)
        self.assertTrue(all(row["state"] == "undiscovered" for row in hidden["rows"]))

        player["combat_kill_counts"] = {"chicken": 1}
        player["combat_observed_drops"] = {
            "chicken": {
                "Feather": {"times_seen": 2, "quantity_seen": 10},
            }
        }
        revealed = drop_log_view_pure(player, _ENEMIES, target_id="chicken")

        self.assertEqual(
            [(row["label"], row["state"]) for row in revealed["rows"]],
            [
                ("Bones", "discovered"),
                ("Feather", "collected"),
                ("Rare gem", "discovered"),
            ],
        )
        feather = revealed["rows"][1]
        self.assertEqual(feather["times_seen"], 2)
        self.assertEqual(feather["quantity_seen"], 10)

    def test_family_and_global_totals_use_only_drop_registry_rows(self):
        player = {
            "combat_kill_counts": {"chicken": 1},
            "combat_observed_drops": {
                "chicken": {
                    "Feather": {"times_seen": 1, "quantity_seen": 5},
                    "Stale item": {"times_seen": 1, "quantity_seen": 1},
                }
            },
            "music_log": {"version": 1, "unlocked_tracks": []},
        }

        view = drop_log_view_pure(player, _ENEMIES)
        totals = collection_totals_pure(player, _ENEMIES)

        self.assertEqual(len(view["targets"]), 1)
        self.assertEqual(view["targets"][0]["target_id"], "chicken")
        self.assertEqual((view["collected"], view["total"]), (1, 3))
        self.assertEqual(totals["drop_log"], {"collected": 1, "total": 3})
        self.assertEqual(totals["global"]["collected"], 1)
        self.assertEqual(
            totals["global"]["total"],
            totals["music"]["total"] + 3,
        )

        player["combat_kill_counts"]["hidden_encounter"] = 1
        revealed = drop_log_view_pure(player, _ENEMIES)
        self.assertEqual(
            [row["target_id"] for row in revealed["targets"]],
            ["chicken", "hidden_encounter"],
        )

    def test_hidden_item_names_do_not_participate_in_search(self):
        player = {
            "combat_kill_counts": {},
            "combat_observed_drops": {},
            "music_log": {"version": 1, "unlocked_tracks": []},
        }

        view = drop_log_view_pure(
            player,
            _ENEMIES,
            target_id="chicken",
            search="Rare gem",
        )

        self.assertEqual(view["rows"], ())


if __name__ == "__main__":
    unittest.main()
