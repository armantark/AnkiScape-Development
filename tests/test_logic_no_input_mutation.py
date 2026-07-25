"""Per-module input-immutability gates for the shallow working-copy sweep.

Each activity module's mutators open with a working copy of the save.  Where
that copy is only a base for keys the module's own `sanitize_*` helper rebuilds
from scratch, deep-copying the whole save is wasted work — but the moment a
mutator writes *through* a nested value it did not rebuild, a shallow copy
corrupts the caller's live save instead.

One gate per module, in the same order the sweep converted them.  Each gate
guards that module's working-copy entry points and replays the module's own
existing test file with the guard installed, because those tests are what
actually reach the mutation paths.  See tests/immutability_gate.py for why the
replay is used instead of hand-written fixtures.

Every gate here passed against the deep-copying code before the conversion
landed; a gate that only passes afterwards is asserting the wrong thing.
"""

import unittest

try:  # pragma: no cover - import shim matches the rest of the suite
    from ..immutability_gate import assert_direct_calls, replay_module_suite
except ImportError:  # pragma: no cover
    from immutability_gate import (  # type: ignore
        assert_direct_calls,
        replay_module_suite,
    )

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import default_player_data

from ankiscape.logic import barbarian_assault_logic
from ankiscape.logic import barrows_logic
from ankiscape.logic import castle_wars_logic
from ankiscape.logic import circus_logic
from ankiscape.logic import court_cases_logic
from ankiscape.logic import equipment_instance_logic
from ankiscape.logic import fight_caves_logic
from ankiscape.logic import fish_flingers_logic
from ankiscape.logic import fishing_trawler_logic
from ankiscape.logic import fist_of_guthix_logic
from ankiscape.logic import flash_powder_factory_logic
from ankiscape.logic import gnome_ball_logic
from ankiscape.logic import great_orb_project_logic
from ankiscape.logic import managing_miscellania_logic
from ankiscape.logic import penguin_hide_and_seek_logic
from ankiscape.logic import pest_control_logic
from ankiscape.logic import pet_logic
from ankiscape.logic import phoenix_lair_logic
from ankiscape.logic import pyramid_plunder_logic
from ankiscape.logic import shades_of_mortton_logic
from ankiscape.logic import slayer_logic
from ankiscape.logic import sorceress_garden_logic
from ankiscape.logic import soul_wars_logic
from ankiscape.logic import stealing_creation_logic
from ankiscape.logic import stronghold_player_safety_logic
from ankiscape.logic import trouble_brewing_logic
from ankiscape.logic import tzhaar_fight_pit_logic
from ankiscape.logic import varrock_museum_logic
from ankiscape.logic import vinesweeper_logic
from ankiscape.logic import warriors_guild_logic
from ankiscape.logic import werewolf_skullball_logic


def _player() -> dict:
    return default_player_data(ORE_DATA, ITEM_DEFINITIONS)


def _guild_player_in_cyclops_room() -> dict:
    data = _player()
    data["warriors_guild"] = {"in_cyclops_room": True, "cyclossus_pending": True}
    return data


# Three entry points no existing suite reaches, so the gate would otherwise
# accept them without ever running their write paths.  Attribute access is
# deliberate: it resolves to the guarded wrapper installed by the replay.
_DIRECT_CALLS = {
    "court_cases_logic": (
        (
            "set_court_cases_policy_pure",
            _player,
            lambda d: court_cases_logic.set_court_cases_policy_pure(d, None),
            ("court_cases_policy",),
        ),
    ),
    "flash_powder_factory_logic": (
        (
            "set_flash_powder_factory_policy_pure",
            _player,
            lambda d: flash_powder_factory_logic.set_flash_powder_factory_policy_pure(
                d, automation_mode="advanced"
            ),
            ("agility_flash_powder_factory_policy",),
        ),
    ),
    "warriors_guild_logic": (
        (
            "leave_warriors_guild_cyclops_room_pure",
            _guild_player_in_cyclops_room,
            lambda d: warriors_guild_logic.leave_warriors_guild_cyclops_room_pure(d),
            ("warriors_guild",),
        ),
    ),
}


# (module, guarded working-copy entry points, suites that drive them)
_MODULE_GATES = (
    (
        equipment_instance_logic,
        ("sanitize_equipment_instance_state_pure",),
        ("tests.test_equipment_instance_logic", "tests.test_barrows"),
    ),
    (
        fish_flingers_logic,
        ("sync_fish_flingers_tickets_pure",),
        ("tests.test_fish_flingers",),
    ),
    (
        slayer_logic,
        ("sanitize_slayer_state_pure",),
        ("tests.test_slayer_logic",),
    ),
    (
        stealing_creation_logic,
        ("ensure_stealing_creation_state_pure",),
        ("tests.test_stealing_creation",),
    ),
    (
        warriors_guild_logic,
        (
            "apply_warriors_guild_activity_pure",
            "enter_warriors_guild_cyclops_room_pure",
            "leave_warriors_guild_cyclops_room_pure",
            "set_warriors_guild_policy_pure",
            "consume_warriors_guild_cyclops_tokens_pure",
            "apply_warriors_guild_cyclops_kills_pure",
            "apply_warriors_guild_cyclossus_kills_pure",
            "show_warriors_guild_defender_pure",
        ),
        ("tests.test_warriors_guild",),
    ),
    (
        pet_logic,
        (
            "acquire_pet_pure",
            "let_out_pet_pure",
            "store_active_pet_pure",
            "release_pet_pure",
            "hatch_phoenix_egg_pure",
            "advance_active_pet_pure",
        ),
        ("tests.test_pet_logic", "tests.test_phoenix_lair", "tests.test_combat_logic"),
    ),
    (
        flash_powder_factory_logic,
        (
            "enter_flash_powder_factory_pure",
            "set_flash_powder_factory_policy_pure",
            "apply_flash_powder_factory_review_pure",
            "leave_flash_powder_factory_pure",
            "redeem_flash_powder_factory_xp_pure",
            "redeem_flash_powder_factory_item_pure",
            "convert_rogue_kit_pure",
        ),
        ("tests.test_flash_powder_factory",),
    ),
    (
        stronghold_player_safety_logic,
        (
            "apply_stronghold_player_safety_review_pure",
            "apply_stronghold_player_safety_command_pure",
        ),
        ("tests.test_stronghold_player_safety", "tests.test_runtime_actions"),
    ),
    (
        pyramid_plunder_logic,
        (
            "enter_pyramid_plunder_pure",
            "set_pyramid_plunder_priority_pure",
            "apply_pyramid_plunder_review_pure",
            "leave_pyramid_plunder_pure",
        ),
        ("tests.test_pyramid_plunder",),
    ),
    (
        shades_of_mortton_logic,
        (
            "set_shades_of_mortton_policy_pure",
            "enter_shades_of_mortton_pure",
            "leave_shades_of_mortton_pure",
            "apply_shades_of_mortton_review_pure",
            "light_shades_altar_pure",
            "bless_shades_item_pure",
            "make_shades_pyre_logs_pure",
            "open_shades_bronze_chest_pure",
        ),
        ("tests.test_shades_of_mortton", "tests.test_runtime_actions"),
    ),
    (
        castle_wars_logic,
        (
            "set_castle_wars_policy_pure",
            "leave_castle_wars_pure",
            "apply_castle_wars_review_pure",
            "deploy_castle_wars_ballista_pure",
            "deploy_castle_wars_chinchompa_pure",
            "buy_castle_wars_reward_pure",
            "sell_castle_wars_reward_pure",
        ),
        ("tests.test_castle_wars", "tests.test_runtime_actions"),
    ),
    (
        soul_wars_logic,
        (
            "set_soul_wars_policy_pure",
            "enter_soul_wars_pure",
            "apply_soul_wars_review_pure",
            "leave_soul_wars_pure",
            "buy_soul_wars_charms_pure",
        ),
        ("tests.test_soul_wars", "tests.test_runtime_actions"),
    ),
    (
        pest_control_logic,
        (
            "set_pest_control_policy_pure",
            "leave_pest_control_pure",
            "apply_pest_control_review_pure",
            "buy_void_seal_pure",
        ),
        ("tests.test_pest_control", "tests.test_runtime_actions"),
    ),
    (
        barbarian_assault_logic,
        (
            "complete_barbarian_assault_tutorial_pure",
            "set_barbarian_assault_policy_pure",
            "enter_barbarian_assault_pure",
            "apply_barbarian_assault_review_pure",
            "leave_barbarian_assault_pure",
            "buy_runner_boots_pure",
        ),
        ("tests.test_barbarian_assault", "tests.test_runtime_actions"),
    ),
    (
        great_orb_project_logic,
        (
            "set_great_orb_project_policy_pure",
            "enter_great_orb_project_pure",
            "apply_great_orb_project_review_pure",
            "leave_great_orb_project_pure",
            "buy_great_orb_project_reward_pure",
        ),
        ("tests.test_great_orb_project",),
    ),
    (
        fishing_trawler_logic,
        (
            "set_fishing_trawler_policy_pure",
            "enter_fishing_trawler_pure",
            "apply_fishing_trawler_review_pure",
            "leave_fishing_trawler_pure",
        ),
        ("tests.test_fishing_trawler",),
    ),
    (
        trouble_brewing_logic,
        (
            "set_trouble_brewing_policy_pure",
            "enter_trouble_brewing_pure",
            "apply_trouble_brewing_review_pure",
            "leave_trouble_brewing_pure",
            "buy_trouble_brewing_reward_pure",
        ),
        ("tests.test_trouble_brewing", "tests.test_runtime_actions"),
    ),
    (
        tzhaar_fight_pit_logic,
        (
            "set_tzhaar_fight_pit_policy_pure",
            "enter_tzhaar_fight_pit_pure",
            "apply_tzhaar_fight_pit_review_pure",
            "leave_tzhaar_fight_pit_pure",
        ),
        ("tests.test_tzhaar_fight_pit",),
    ),
    (
        werewolf_skullball_logic,
        (
            "set_werewolf_skullball_policy_pure",
            "enter_werewolf_skullball_pure",
            "apply_werewolf_skullball_review_pure",
            "leave_werewolf_skullball_pure",
        ),
        ("tests.test_werewolf_skullball",),
    ),
    (
        gnome_ball_logic,
        (
            "enter_gnome_ball_pure",
            "apply_gnome_ball_review_pure",
            "leave_gnome_ball_pure",
        ),
        ("tests.test_gnome_ball",),
    ),
    (
        court_cases_logic,
        (
            "set_court_cases_policy_pure",
            "enter_court_case_pure",
            "select_court_trial_choice_pure",
            "leave_court_case_pure",
            "apply_court_case_review_pure",
        ),
        ("tests.test_court_cases",),
    ),
    (
        fight_caves_logic,
        ("apply_fight_caves_command_pure", "apply_fight_caves_review_pure"),
        ("tests.test_fight_caves",),
    ),
    (
        phoenix_lair_logic,
        (
            "apply_phoenix_lair_command_pure",
            "apply_phoenix_lair_review_pure",
            "resolve_phoenix_egg_choice_pure",
        ),
        ("tests.test_phoenix_lair",),
    ),
    (
        barrows_logic,
        ("apply_barrows_command_pure", "apply_barrows_review_pure"),
        ("tests.test_barrows",),
    ),
    (
        vinesweeper_logic,
        ("apply_vinesweeper_review_pure", "apply_vinesweeper_command_pure"),
        ("tests.test_vinesweeper",),
    ),
    (
        circus_logic,
        ("apply_circus_command_pure", "apply_circus_review_pure"),
        ("tests.test_circus", "tests.test_runtime_actions"),
    ),
    (
        varrock_museum_logic,
        ("apply_varrock_museum_review_pure", "apply_varrock_museum_command_pure"),
        ("tests.test_varrock_museum",),
    ),
    (
        sorceress_garden_logic,
        ("apply_sorceress_garden_review_pure", "apply_sorceress_garden_command_pure"),
        ("tests.test_sorceress_garden",),
    ),
    (
        penguin_hide_and_seek_logic,
        ("apply_penguin_review_pure", "apply_penguin_command_pure"),
        ("tests.test_penguin_hide_and_seek",),
    ),
    (
        managing_miscellania_logic,
        (
            "apply_managing_miscellania_review_pure",
            "apply_managing_miscellania_command_pure",
        ),
        ("tests.test_managing_miscellania", "tests.test_runtime_actions"),
    ),
    (
        fist_of_guthix_logic,
        ("_build_combat_player",),
        ("tests.test_fist_of_guthix_logic",),
    ),
)


class TestLogicHelpersDoNotMutateTheirInput(unittest.TestCase):
    """One gate per converted module; see _MODULE_GATES for the wiring."""


def _make_gate(module, functions, suites):
    direct = _DIRECT_CALLS.get(module.__name__.rpartition(".")[2], ())

    def gate(self):
        assert_direct_calls(self, direct)
        replay_module_suite(
            self,
            module,
            functions,
            suites,
            extra_calls=[
                (lambda case=case: case[2](case[1]())) for case in direct
            ],
        )

    gate.__doc__ = f"{module.__name__} must not write through the save it is given."
    return gate


for _module, _functions, _suites in _MODULE_GATES:
    setattr(
        TestLogicHelpersDoNotMutateTheirInput,
        f"test_{_module.__name__.rpartition('.')[2]}_does_not_mutate_input",
        _make_gate(_module, _functions, _suites),
    )


if __name__ == "__main__":
    unittest.main()
