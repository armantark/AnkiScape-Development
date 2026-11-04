"""Version 126 preserves earned Witch progress and genuinely repairs missing deeds."""

import copy
import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import migrate_loaded_data, CURRENT_CONFIG_VERSION
from ankiscape.data.quest.witchs_house import (
    QUEST_ID, DIARY, MAGNET, CHEESE, READ_DIARY, PASS_GATE, RESUME_KEY,
    LEGACY_COMPLETED_KEY, RESUME_STAGES, EXPERIMENTS,
)
from ankiscape.logic_pure.logic_pure_quest import (
    quest_journal_rows_pure, apply_quest_combat_encounter_pure,
)
from .test_witchs_house import player_at, progress, wear_leather, train_for_experiments


def reload_player(player, version=None):
    data = json.loads(json.dumps(player))
    if version is not None:
        data['config_version'] = version
    return migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)


def earned_old_save(stage):
    player = train_for_experiments(reload_player(player_at(12)))
    player, ok, result = apply_quest_combat_encounter_pure(
        player, QUEST_ID, QUEST_DATA, EXPERIMENTS[0][0], rng=lambda: 0.5, ticks=1,
    )
    if not ok or result.get('quest_combat_completed'):
        raise AssertionError(result)
    player['quests'][QUEST_ID]['progress'] = stage
    player['inventory'].update({MAGNET: 1, CHEESE: 0, 'Coins': 23})
    player['quest_points'] = 7
    player['quest_action_proofs'] = ['Use cheese on the mouse hole and attach the magnet to the mouse']
    player['quest_combat_encounter_counts'][QUEST_ID] = {EXPERIMENTS[1][0]: 1}
    return player


class WitchsHouseStorageTest(unittest.TestCase):
    def test_old_incomplete_progress_zero_through_eleven_preserves_earned_custody_and_combat(self):
        self.assertEqual(CURRENT_CONFIG_VERSION, 126)
        for old_stage in range(12):
            with self.subTest(old_stage=old_stage):
                player = earned_old_save(old_stage)
                before = copy.deepcopy(player)
                migrated = reload_player(player, 125)
                self.assertEqual(player, before)
                self.assertEqual(migrated['quests'][QUEST_ID]['progress'], 3 if old_stage >= 4 else old_stage)
                self.assertEqual(migrated[RESUME_KEY], RESUME_STAGES.get(old_stage, 0))
                self.assertFalse(migrated[LEGACY_COMPLETED_KEY])
                for key in ('inventory', 'quest_points', 'constitution_exp', 'quest_action_proofs',
                            'quest_combat_encounters', 'quest_combat_encounter_counts', 'quest_combat_active_encounters'):
                    self.assertEqual(migrated[key], player[key], key)
                self.assertNotIn(READ_DIARY, migrated['quest_action_proofs'])
                self.assertNotIn(PASS_GATE, migrated['quest_action_proofs'])
                self.assertEqual(reload_player(migrated), migrated)

    def test_unstarted_and_completed_saves_get_no_new_items_proofs_or_rewards(self):
        for started, completed, stage in ((False, False, 0), (False, False, 8), (True, True, 12)):
            with self.subTest(completed=completed, stage=stage):
                player = earned_old_save(stage)
                player['quests'][QUEST_ID].update(started=started, completed=completed)
                migrated = reload_player(player, 125)
                self.assertEqual(migrated['quests'][QUEST_ID], player['quests'][QUEST_ID])
                self.assertEqual(migrated[LEGACY_COMPLETED_KEY], completed)
                self.assertEqual(migrated[RESUME_KEY], 0)
                for key in ('inventory', 'quest_action_proofs', 'quest_points', 'constitution_exp',
                            'quest_combat_active_encounters', 'quest_combat_encounter_counts'):
                    self.assertEqual(migrated[key], player[key], key)
                if completed:
                    rows = quest_journal_rows_pure(migrated, QUEST_ID, QUEST_DATA)
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(rows[0]['lines'], ('Harvey got his ball back.', 'Quest complete!'))
                    self.assertFalse(progress(migrated)[1])

    def test_reopen_at_each_remediation_step_then_real_worn_gate_resumes_atomically(self):
        for old_stage, resume in RESUME_STAGES.items():
            with self.subTest(old_stage=old_stage):
                player = reload_player(earned_old_save(old_stage), 125)
                original_combat = copy.deepcopy(player['quest_combat_active_encounters'])
                for step in (3, 4, 5, 6):
                    player = reload_player(player)
                    self.assertEqual(player[RESUME_KEY], resume)
                    self.assertEqual(player['quests'][QUEST_ID]['progress'], step)
                    self.assertEqual(reload_player(player), player)
                    if step < 6:
                        player, ok, _ = progress(player)
                        self.assertTrue(ok)
                before = copy.deepcopy(player)
                self.assertTrue(progress(player)[1])
                self.assertEqual(player, before)
                self.assertEqual(player[RESUME_KEY], resume)
                wear_leather(player)
                player, ok, completed = progress(player)
                self.assertTrue(ok)
                self.assertFalse(completed)
                self.assertEqual(player['quests'][QUEST_ID]['progress'], resume)
                self.assertEqual(player[RESUME_KEY], 0)
                self.assertEqual(player['quest_combat_active_encounters'], original_combat)
                self.assertEqual(player['inventory'][MAGNET], 1)
                self.assertEqual(player['inventory'][CHEESE], 0)
                self.assertEqual(player['inventory'][DIARY], 1)
                self.assertIn(READ_DIARY, player['quest_action_proofs'])
                self.assertIn(PASS_GATE, player['quest_action_proofs'])
                self.assertEqual(reload_player(player)[RESUME_KEY], 0)

    def test_version_126_sanitizes_only_invalid_scalars_without_remapping_progress(self):
        for stage in range(16):
            for resume in (0, 7, 8, 12, 14, 15, '12', True, None):
                player = player_at(stage)
                player[RESUME_KEY] = resume
                player[LEGACY_COMPLETED_KEY] = True
                migrated = reload_player(player, 126)
                valid = type(resume) is int and resume in range(8, 15) and stage in range(3, 7)
                self.assertEqual(migrated[RESUME_KEY], resume if valid else 0)
                self.assertEqual(migrated['quests'][QUEST_ID]['progress'], stage)
                self.assertFalse(migrated[LEGACY_COMPLETED_KEY])
                self.assertEqual(migrated['quest_action_proofs'], [])
        player = player_at(4)
        player['quests'][QUEST_ID]['started'] = False
        player[RESUME_KEY] = 12
        self.assertEqual(reload_player(player)[RESUME_KEY], 0)
        player['quests'][QUEST_ID].update(started=True, completed=True, progress=12)
        player[LEGACY_COMPLETED_KEY] = True
        reloaded = reload_player(player)
        self.assertTrue(reloaded[LEGACY_COMPLETED_KEY])
        self.assertEqual(reloaded[RESUME_KEY], 0)
