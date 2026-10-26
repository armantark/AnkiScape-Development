"""Seven period searches through generation, runtime resolution and saved reopen."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core import constants
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data import treasure_trails_data as data
from ankiscape.logic import treasure_trails_logic as trails
from ankiscape.runtime.runtime_actions import handle_utility_answer
from ankiscape.tools.native.player_data import migrated_player_data
from tests import test_runtime_actions as runtime_helpers
from tests.treasure_trails import SEARCH_ROWS, finite_draws


# Integration baseline: nine original rows plus six main NPC clues. Freeze every
# pre-addition field, including the original shared source string and order.
BASELINE_SOURCE = (
    "RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); "
    "Clue scroll (easy) oldid=6333359 (2012-10-02T09:39:55Z); "
    "Treasure Trails/Guide/Simple clues oldid=6579176 (2012-11-18T16:48:49Z); "
    "Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); "
    "Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); "
    "Darkan TreasureTrailsManager.java and "
    "data/npcs/drops/treasure_trails/easy_casket.json"
)
BASELINE_ROWS = (
    ("simple_port_sarim_sailor", "simple", "One of the sailors in Port Sarim is your next destination.", (), False),
    ("simple_varrock_palace_crate", "simple", "Search for a crate in Varrock Palace.", (), False),
    ("simple_lumbridge_goblin_house", "simple", "Search the boxes in the Goblin house near Lumbridge.", (), False),
    ("simple_grand_tree_mushrooms", "simple", "Dig near some giant mushrooms behind the Grand Tree.", (), False),
    ("map_clock_tower_crates", "map", "Map: crates stacked behind the Clock tower building south of Ardougne Castle.", (), False),
    ("map_lumberyard_crate", "map", "Map: the crate in the storage area behind the Lumberyard sawmill operator, north-east of Varrock.", (), False),
    ("emote_duel_arena_bow", "emote", "Bow or curtsy in the lobby of the Duel Arena. Equip an iron chainbody, leather chaps and a coif.", ("Iron chainbody", "Leather chaps", "Coif"), False),
    ("emote_port_sarim_cheer", "emote", "Cheer for the monks at Port Sarim. Equip a coif, steel plateskirt and a sapphire necklace.", ("Coif", "Steel plateskirt", "Sapphire necklace"), False),
    ("emote_burthorpe_games_room_cheer", "emote", "Cheer at the Burthorpe Games Room. Have nothing equipped at all when you do.", (), True),
    ("simple_lumbridge_hans", "simple", "Speak to Hans.", (), False),
    ("simple_camelot_sir_kay", "simple", "Speak to Sir Kay in Camelot Castle.", (), False),
    ("simple_varrock_blue_moon_bartender", "simple", "Speak to the bartender of the Blue Moon Inn in Varrock.", (), False),
    ("simple_port_sarim_rusty_anchor_bartender", "simple", "Talk to the bartender of the Rusty Anchor in Port Sarim.", (), False),
    ("simple_falador_squire", "simple", "Talk to the Squire in the White Knights' castle in Falador.", (), False),
    ("simple_al_kharid_zeke", "simple", "Talk to Zeke in Al Kharid.", (), False),
)
ROOT = Path(__file__).resolve().parents[2]
CLUE = "Clue scroll (easy)"
CASKET = "Casket (easy)"


def expected_row(step_id, kind, text, equipment=(), bare=False):
    return dict(step_id=step_id, kind=kind, text=text, equipment=equipment,
                bare=bare, source=BASELINE_SOURCE)


def selection_draw(step_id):
    keys = list(data.TREASURE_TRAILS_EASY_STEPS)
    return (keys.index(step_id) + 0.5) / len(keys)


def held_clue_save():
    save = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    save.update(inventory={CLUE: 1, "Coins": 73, "Logs": 4}, equipment={},
                activity_session={"active_id": ""}, treasure_trail={},
                treasure_trail_retained={})
    return migrate_loaded_data(save, constants.ORE_DATA, constants.ITEM_DEFINITIONS)


def start_generated(test, step_ids):
    draws = (0.0 if len(step_ids) == 1 else 0.25,)
    draws += tuple(selection_draw(step_id) for step_id in step_ids)
    save, ok, info = trails.apply_treasure_trails_command_pure(
        held_clue_save(), "start_from_bank", {"tier": "easy"}, finite_draws(draws)
    )
    test.assertTrue(ok, info)
    test.assertEqual(save["treasure_trail"]["steps"], list(step_ids))
    test.assertEqual(save["treasure_trail"]["index"], 0)
    test.assertEqual(save["treasure_trail_retained"], {})
    test.assertEqual(save["activity_session"], {"active_id": "treasure_trail"})
    test.assertEqual(save["current_utility"], "treasure_trail")
    test.assertEqual(save["treasure_trails_started"], 1)
    return save


def answer_step(test, save):
    calls = {"xp": [], "saves": 0, "errors": [], "activity": []}
    before_exp = {key: value for key, value in save.items() if key.endswith("_exp")}
    test.assertTrue(handle_utility_answer(runtime_helpers._context(save, calls)))
    test.assertEqual(calls["errors"], [])
    test.assertEqual(calls["xp"], [])
    test.assertEqual({key: value for key, value in save.items() if key.endswith("_exp")}, before_exp)
    test.assertEqual(calls["saves"], 1)
    return calls


def assert_finished(test, save):
    expected = held_clue_save()["inventory"]
    expected.pop(CLUE)
    expected[CASKET] = 1
    test.assertEqual(save["inventory"], expected)
    test.assertEqual(save["treasure_trail"], {})
    test.assertEqual(save["activity_session"], {"active_id": ""})
    test.assertEqual(save["treasure_trails_completed"], 1)
    test.assertEqual(save["treasure_trails_started"], 1)


def reopen(save):
    return migrate_loaded_data(json.loads(json.dumps(save)), constants.ORE_DATA,
                               constants.ITEM_DEFINITIONS)


def assert_persisted(test, before, after):
    for key in ("config_version", "treasure_trail", "treasure_trail_retained",
                "inventory", "activity_session", "current_utility",
                "treasure_trails_started", "treasure_trails_completed",
                "treasure_trails_caskets_opened"):
        test.assertEqual(after[key], before[key], key)


def resume_without_draw(test, save):
    def unexpected_draw():
        raise AssertionError("Resuming retained progress must not generate a trail")

    resumed, ok, info = trails.apply_treasure_trails_command_pure(
        save, "start_from_bank", {"tier": "easy"}, unexpected_draw
    )
    test.assertTrue(ok, info)
    test.assertEqual(resumed["treasure_trail"], save["treasure_trail_retained"])
    test.assertEqual(resumed["treasure_trail_retained"], {})
    test.assertEqual(resumed["treasure_trails_started"], save["treasure_trails_started"])
    test.assertEqual(resumed["activity_session"], {"active_id": "treasure_trail"})
    return resumed


def abandon_and_reopen(test, save):
    expected = copy.deepcopy(save["treasure_trail"])
    abandoned, ok, info = trails.apply_treasure_trails_command_pure(save, "abandon")
    test.assertTrue(ok, info)
    test.assertEqual(abandoned["treasure_trail"], {})
    test.assertEqual(abandoned["treasure_trail_retained"], expected)
    test.assertEqual(abandoned["activity_session"], {"active_id": ""})
    loaded = reopen(abandoned)
    assert_persisted(test, abandoned, loaded)
    return resume_without_draw(test, loaded)


class SevenSearchesTest(unittest.TestCase):
    def test_registry_adds_exactly_seven_searches(self):
        expected = [expected_row(*row) for row in BASELINE_ROWS]
        expected += [expected_row(step_id, "simple", text) for step_id, text in SEARCH_ROWS]
        registry = data.TREASURE_TRAILS_EASY_STEPS
        self.assertEqual(len(registry), 22)
        self.assertEqual(list(registry), [row["step_id"] for row in expected])
        self.assertEqual(list(registry.values()), expected)
        self.assertEqual(data.TREASURE_TRAILS_SOURCE, BASELINE_SOURCE)
        module = ast.parse(Path(data.__file__).read_text())
        assignment = next(node for node in module.body if isinstance(node, ast.AnnAssign)
                          and getattr(node.target, "id", "") == "TREASURE_TRAILS_EASY_STEPS")
        calls = assignment.value.generators[0].iter.elts
        ids = [ast.literal_eval(call.args[0]) for call in calls]
        self.assertEqual(len(ids), 22)
        self.assertEqual(len(ids), len(set(ids)), "Duplicate _step hidden by dict construction")
        self.assertEqual(ids, list(registry))

    def test_all_seven_start_read_advance_and_finish(self):
        for step_id, text in SEARCH_ROWS:
            with self.subTest(step_id=step_id):
                save = start_generated(self, (step_id, step_id))
                self.assertEqual(trails.treasure_trails_view_pure(save)["step"]["text"], text)
                inventory_before = copy.deepcopy(save["inventory"])
                first = answer_step(self, save)
                self.assertFalse(first.get("deactivated", False))
                self.assertEqual(save["treasure_trail"]["index"], 1)
                self.assertEqual(save["inventory"], inventory_before)
                self.assertEqual(save["treasure_trails_completed"], 0)
                self.assertEqual(save["activity_session"], {"active_id": "treasure_trail"})
                self.assertEqual(trails.treasure_trails_view_pure(save)["step"]["text"], text)
                self.assertTrue(answer_step(self, save)["deactivated"])
                assert_finished(self, save)

    def test_all_seven_earned_caskets_open(self):
        for step_id, _text in SEARCH_ROWS:
            with self.subTest(step_id=step_id):
                save = start_generated(self, (step_id,))
                answer_step(self, save)
                assert_finished(self, save)
                expected_inventory = copy.deepcopy(save["inventory"])
                expected_inventory.pop(CASKET)
                opened, ok, info = trails.apply_treasure_trails_command_pure(
                    save, "open_casket", {"tier": "easy"}, finite_draws((0.0,) + (0.5,) * 6)
                )
                self.assertTrue(ok, info)
                self.assertNotIn(CASKET, opened["inventory"])
                self.assertTrue(info["rewards"])
                for item, amount in info["rewards"].items():
                    self.assertGreater(amount, 0)
                    expected_inventory[item] = expected_inventory.get(item, 0) + amount
                self.assertEqual(opened["inventory"], expected_inventory)
                self.assertEqual(opened["treasure_trails_caskets_opened"], 1)
                self.assertEqual(opened["treasure_trails_completed"], 1)

    def test_new_active_saves_reopen(self):
        for step_id, text in SEARCH_ROWS:
            with self.subTest(step_id=step_id):
                save = start_generated(self, (step_id, step_id))
                answer_step(self, save)
                loaded = reopen(save)
                assert_persisted(self, save, loaded)
                self.assertEqual(loaded["treasure_trail"]["index"], 1)
                self.assertEqual(loaded["treasure_trail"]["steps"], [step_id, step_id])
                self.assertEqual(trails.treasure_trails_view_pure(loaded)["step"]["text"], text)

    def test_new_retained_saves_resume(self):
        for step_id, text in SEARCH_ROWS:
            with self.subTest(step_id=step_id):
                save = start_generated(self, (step_id, step_id))
                answer_step(self, save)
                resumed = abandon_and_reopen(self, save)
                self.assertEqual(resumed["treasure_trail"], save["treasure_trail"])
                self.assertEqual(resumed["treasure_trail"]["index"], 1)
                self.assertEqual(trails.treasure_trails_view_pure(resumed)["step"]["text"], text)
                answer_step(self, resumed)
                assert_finished(self, resumed)

    def test_baseline_active_and_retained_saves_reopen(self):
        for step_id, _kind, text, _equipment, _bare in BASELINE_ROWS:
            with self.subTest(step_id=step_id):
                save = start_generated(self, ("simple_port_sarim_sailor", step_id))
                answer_step(self, save)
                loaded = reopen(save)
                assert_persisted(self, save, loaded)
                self.assertEqual(loaded["treasure_trail"]["index"], 1)
                self.assertEqual(loaded["treasure_trail"]["steps"], ["simple_port_sarim_sailor", step_id])
                resumed = abandon_and_reopen(self, loaded)
                self.assertEqual(resumed["treasure_trail"], save["treasure_trail"])
                self.assertEqual(trails.treasure_trails_view_pure(resumed)["step"]["text"], text)

    def test_registered_art_and_provenance(self):
        provenance = json.loads((ROOT / "assets_provenance.json").read_text())
        bindings = (
            (constants.UTILITY_ACTIVITY_DATA["treasure_trail"]["icon_path"],
             "activityicons/treasure_trail.png", "b4a46740be3354a77543cfed31eb5b2756ebd74fb6c3a57c69cd808cc3c0bee0",
             "Mg treasuretrails.jpg", "2008-07-28T14:53:49Z", "rs3"),
            (constants.TREASURE_TRAILS_ITEM_IMAGES[CASKET],
             "activityitems/casket_easy.png", "a4f404b09451717e98434baa18564747af28d87d72eaf74f97e1b25dab73123a",
             "Casket.png", "2010-10-04T04:04:13Z", "rs3"),
            (constants.COMBAT_ITEM_IMAGES[CLUE],
             "combatitems/clue_scroll_easy.png", "9ec85a114b04bf018311457874f959f8b64eb7b13a3abba52f5bf4815fcc7278",
             "Clue scroll (easy).png", "2019-04-11T12:15:25Z", "osrs"),
        )
        for binding, relative, digest, title, timestamp, wiki in bindings:
            with self.subTest(asset=relative):
                path = Path(binding)
                self.assertEqual(path.resolve(), (ROOT / relative).resolve())
                contents = path.read_bytes()
                self.assertTrue(contents.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertEqual(hashlib.sha256(contents).hexdigest(), digest)
                self.assertEqual(provenance[relative]["file_title"], title)
                self.assertEqual(provenance[relative]["timestamp"], timestamp)
                self.assertEqual(provenance[relative]["source_wiki"], wiki)

    def test_retained_fixture_uses_supported_save_merge(self):
        save = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
        save.update(inventory={CLUE: 1}, equipment={})
        step_ids = ["simple_hemenster_crate", "simple_port_khazard_cart_crate"]
        save, ok, info = trails.apply_treasure_trails_command_pure(
            save, "start_from_bank", {"tier": "easy"},
            finite_draws((0.25, selection_draw(step_ids[0]), selection_draw(step_ids[1])))
        )
        self.assertTrue(ok, info)
        self.assertEqual(save["treasure_trail"]["steps"], step_ids)
        self.assertEqual(save["treasure_trail"]["index"], 0)
        generated = copy.deepcopy(save["treasure_trail"])

        abandoned, ok, info = trails.apply_treasure_trails_command_pure(save, "abandon")
        self.assertTrue(ok, info)
        self.assertEqual(abandoned["treasure_trail"], {})
        self.assertEqual(abandoned["activity_session"], {"active_id": ""})
        self.assertEqual(abandoned["inventory"], {CLUE: 1})
        self.assertEqual(abandoned["treasure_trail_retained"], generated)
        self.assertEqual(abandoned["treasure_trails_started"], 1)
        self.assertEqual(abandoned["treasure_trails_completed"], 0)
        self.assertEqual(abandoned["treasure_trails_caskets_opened"], 0)
        overrides = {key: abandoned[key] for key in (
            "activity_session", "current_utility", "equipment", "inventory",
            "treasure_trail", "treasure_trail_retained", "treasure_trails_caskets_opened",
            "treasure_trails_completed", "treasure_trails_last_result", "treasure_trails_started",
        )}
        serialized = json.dumps(overrides, sort_keys=True, separators=(",", ":"))
        self.assertEqual(
            hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
            "f71db8322622d3dde0d85d406c0838bb96ed7735664cee4f24d95ac609b9c2ef",
        )

        loaded = migrated_player_data(json.loads(serialized))
        self.assertEqual(loaded["treasure_trail_retained"], generated)
        self.assertEqual(loaded["treasure_trail"], {})
        self.assertEqual(loaded["inventory"][CLUE], 1)
        self.assertEqual(loaded["inventory"].get(CASKET, 0), 0)
        resumed = resume_without_draw(self, loaded)
        self.assertEqual(resumed["treasure_trail"], generated)
        self.assertEqual(resumed["treasure_trail"]["steps"], step_ids)
        self.assertEqual(resumed["treasure_trail"]["index"], 0)
        self.assertEqual(resumed["treasure_trails_started"], 1)
        self.assertEqual(resumed["treasure_trail_retained"], {})
        self.assertEqual(resumed["activity_session"], {"active_id": "treasure_trail"})
        self.assertEqual(resumed["current_utility"], "treasure_trail")
        self.assertEqual(trails.treasure_trails_view_pure(resumed)["step"]["text"],
                         "Search for a crate in a building in Hemenster.")
