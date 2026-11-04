"""Exact catalog, provenance, registry and later-contract preservation."""

import copy
import hashlib
import json
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, QUEST_DATA
from ankiscape.data.quest import grand_tree as opening
from ankiscape.data.quest.catalog import _quest_from_catalog, _quest_with_stage_requirements
from ankiscape.data.quest.catalog_overrides import QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
from ankiscape.data.quest.contract import QuestStageRequirement
from ankiscape.data.quest.ledger import QUESTS_BY_ID
from ankiscape.data.quest_action_proof_data import QUEST_ACTION_PROOF_RULES
from ankiscape.data.quest_item_acquisition_data import quest_item_acquisition_extra_items_as_dict
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.quest_action_proofs import quest_action_proofs_after_event_pure

ROOT = Path(__file__).resolve().parents[2]
QUEST_ID = opening.QUEST_ID
ITEM_CASES = (
    (opening.BARK_SAMPLE, 783, '5912140', 'A sample of the bark from the Grand Tree.',
     'bark_sample', '2010-04-28T16:28:02Z', '6d8f1282e0bd80fe433bcbfcf752a23bd2a7a9e92edef2a4d7893a87d97deb96'),
    (opening.TRANSLATION_BOOK, 784, '6162857', 'A book to translate the ancient gnome language into English.',
     'translation_book', '2008-11-25T19:42:29Z', '8d0bac344f1fac79a4c6bf0e132f4ce88cf5764a77ec8ef3b31e431d34542bbc'),
    (opening.HAZELMERES_SCROLL, 786, '6154711', 'Hazelmere wrote something down on this scroll.',
     'hazelmeres_scroll', '2011-11-22T16:25:04Z', 'cbc83acbd991d7329401730a14eff68cf54002f066afacee7fa9f95d54aff9f2'),
)


class OpeningCatalogTest(unittest.TestCase):
    def test_requirements_are_exact_defaults_and_later_objects_survive(self):
        quest = QUESTS_BY_ID[QUEST_ID]
        rows = quest.stage_requirements
        expected = (
            QuestStageRequirement(1, "Receive Narnode's commission and take the Bark sample to Hazelmere for examination.",
                                  required_actions=opening.PROOFS[:2], source=opening.STAGE_SOURCES[1]),
            QuestStageRequirement(2, "Translate Hazelmere's scroll, report to Narnode and warn Glough.",
                                  required_actions=opening.PROOFS[2:], source=opening.STAGE_SOURCES[2]),
        )
        self.assertEqual(rows[:2], expected)
        before = copy.deepcopy(rows)
        composed = opening.compose_grand_tree_requirements(QUEST_ID, rows)
        self.assertEqual(composed, rows)
        self.assertEqual(opening.compose_grand_tree_requirements(QUEST_ID, composed), composed)
        self.assertEqual(rows, before)
        for original, retained in zip(rows[2:], composed[2:]):
            self.assertIs(retained, original)
        self.assertIs(opening.compose_grand_tree_requirements('other', rows), rows)

    def test_later_contract_matches_frozen_baseline(self):
        q = QUEST_DATA[QUEST_ID]
        actual = {k: v for k, v in q.items() if k not in ('stage_requirements', 'journal_stages')}
        actual['stage_requirements'] = [r for r in q['stage_requirements'] if r['stage'] > 2]
        actual['journal_stages'] = {str(k): v for k, v in q['journal_stages'].items() if k > 2}
        self.assertEqual(json.loads(json.dumps(actual)), json.loads(Path(__file__).with_name('later_contract.json').read_text()))
        self.assertEqual(q['required_skills'], ({'skill_id': 'agility', 'display_name': 'Agility', 'level': 25},))
        self.assertTrue(q['members'])
        self.assertEqual(q['required_quests'], ())
        self.assertEqual(q['stage_requirements'][2]['required_actions'], ('Complete The Grand Tree stage 3 objective',))

    def test_five_events_require_full_prefix_and_four_ordered_bundles(self):
        self.assertEqual(opening.PROOFS, (
            "Receive Narnode's commission, Bark sample and Translation book",
            "Have Hazelmere examine the Bark sample and receive Hazelmere's scroll",
            "Translate Hazelmere's scroll with the Translation book",
            "Report Hazelmere's translated message to Narnode",
            "Warn Glough of the Daconia rocks and hear his instruction to report back",
        ))
        self.assertEqual(tuple(opening.REVIEW_BUNDLES), ('commission', 'examination', 'translation', 'report_warning'))
        self.assertEqual(tuple(opening.REVIEW_BUNDLES.values()),
                         ((opening.EVENTS[0],), (opening.EVENTS[1],), (opening.EVENTS[2],), opening.EVENTS[3:]))
        for index, name in enumerate(('commission', 'examination', 'translation', 'report', 'warning')):
            event = ('quest_service', 'grand_tree_' + name)
            self.assertEqual(opening.EVENTS[index], event)
            self.assertEqual(QUEST_ACTION_PROOF_RULES[event], (opening.PROOFS[:index], (opening.PROOFS[index],)))
            self.assertEqual(quest_action_proofs_after_event_pure(opening.PROOFS[:index], *event), sorted(opening.PROOFS[:index + 1]))
            for missing in range(index):
                prefix = list(opening.PROOFS[:index])
                prefix.remove(opening.PROOFS[missing])
                self.assertEqual(quest_action_proofs_after_event_pure(prefix, *event), sorted(prefix))
        for event in (('quest', QUEST_ID), ('quest_stage', QUEST_ID + ':Complete The Grand Tree stage 1 objective'),
                      ('quest_stage', QUEST_ID + ':Complete The Grand Tree stage 2 objective')):
            self.assertEqual(quest_action_proofs_after_event_pure([], *event), [])

    def test_exact_items_and_functional_registry_icons(self):
        extra = quest_item_acquisition_extra_items_as_dict()
        for name, item_id, oldid, examine, stem, date, digest in ITEM_CASES:
            with self.subTest(name=name):
                row = opening.GRAND_TREE_OPENING_ITEMS[name]
                self.assertEqual(set(row), {'category', 'item_id', 'stackable', 'tradeable', 'examine', 'source'})
                self.assertEqual({k: v for k, v in row.items() if k != 'source'},
                                 dict(category='material', item_id=item_id, stackable=False, tradeable=False, examine=examine))
                for pin in (oldid, '43c971faa9f3947f18db7269c80560e4be46de27', '309/build 727', '544/build 742'):
                    self.assertIn(pin, row['source'])
                self.assertEqual(extra[name], row)
                self.assertIsNot(extra[name], row)
                definitions = [i for i in ITEM_DEFINITIONS if i.display_name == name]
                self.assertEqual(len(definitions), 1)
                definition = definitions[0]
                self.assertEqual((definition.source_item_id, definition.stackable, definition.tradeable), (item_id, False, False))
                path = ROOT / 'data/quest/assets' / (stem + '.png')
                self.assertEqual(Path(definition.asset_path), path)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                provenance = json.loads(path.with_suffix('.provenance.json').read_text())
                self.assertEqual(provenance['timestamp'], date)
                self.assertEqual(provenance['sha256'], digest)
                self.assertEqual(provenance['sha1'], hashlib.sha1(path.read_bytes()).hexdigest())
                self.assertEqual(provenance['actual_sha1'], provenance['sha1'])
                self.assertEqual(provenance['size'], len(path.read_bytes()))
                self.assertIn('2014', provenance['date_limit'])
                self.assertEqual(provenance['saved_path'], str(path.relative_to(ROOT)))

    def test_journal_text_is_owned_by_existing_composition_in_either_order(self):
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == QUEST_ID)
        mapping = json.loads((ROOT / 'data/quest/grand_tree_sources.json').read_text())['item1380_source_mapping']
        message = tuple(row['display'] for row in mapping['statements'])
        self.assertEqual(message, ("A man came to me with the King's seal", 'I gave the man Daconia rocks',
                                   'and Daconia rocks will kill the tree!'))
        for inserted in (False, True):
            self._assert_journal_composition(raw, message, inserted)

    def _assert_journal_composition(self, raw, message, inserted):
        replacements = QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID
        with patch.dict(replacements):
            if not inserted:
                replacements.pop(QUEST_ID, None)
            quest = _quest_with_stage_requirements(_quest_from_catalog(raw), raw)
        expected = {s['stage']: tuple(s['journal']) for s in raw['journal_stages']}
        if inserted:
            expected[2] = expected[2][:1] + message + expected[2][1:]
        before = tuple(asdict(s) for s in quest.journal_stages)
        opening.compose_grand_tree_requirements(QUEST_ID, quest.stage_requirements)
        self.assertEqual({s.stage: s.journal for s in quest.journal_stages}, expected)
        self.assertEqual(tuple(asdict(s) for s in quest.journal_stages), before)
