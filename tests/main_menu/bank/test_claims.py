from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_bank_grid,
    _find_gear_list,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_bank_tab,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_bank_claims_expose_eligible_wicked_hood_claim(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["quests"]["rune_mysteries"] = {"started": True, "progress": 6, "completed": True}
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Wicked hood x1", labels)
        self.assertIn("Ready to claim", labels)
        # Locked claims are not rendered at all: a reward the player cannot
        # claim is not actionable information on the Bank tab.
        self.assertFalse(any("locked reward" in label for label in labels), labels)
        self.assertEqual(
            [lbl for lbl in dialog.findChildren(QLabel)
             if lbl.objectName() == "bankClaimsLockedSummary"],
            [],
        )
        self.assertIsNotNone(_find_named_widget(dialog, "bankClaimsScrollArea"))
        metadata = _find_named_label(dialog, "bankClaimMetadata")
        self.assertNotIn("palette(mid)", metadata.styleSheet())
        claim_btn = next(
            btn for btn in dialog.findChildren(QPushButton)
            if btn.text() == "Claim"
        )
        self.assertTrue(claim_btn.isEnabled())
        claim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._claim_calls[-1], ("wicked_hood", None))

    def test_bank_claims_use_the_shared_icon_chooser_for_a_diary_lamp(self) -> None:
        from ankiscape.data.achievement_diary_data import (
            ACHIEVEMENT_DIARY_CATALOG,
            diary_lamp_claim_id,
        )

        pd = dict(_make_player_data(), agility_level=30)
        family = next(family for family in ACHIEVEMENT_DIARY_CATALOG if family.id == "varrock")
        tier = family.tiers[0]
        pd["achievement_diaries"] = {"claimed_tiers": [tier.id]}
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        title = f"{family.name} {tier.name}: reward lamp ({tier.lamp.experience:,} XP)"
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertIn(title, labels)
        self.assertTrue(
            any(label.startswith(f"{tier.lamp.experience:,} XP ·") for label in labels)
        )
        choose = next(
            button
            for button in dialog.findChildren(QPushButton)
            if button.text() == "Choose skill"
        )
        with patch.object(
            self._ui,
            "_choose_xp_lamp_skill",
            return_value="agility",
        ) as chooser:
            choose.click()
        QApplication.processEvents()

        self.assertEqual(
            self._claim_calls[-1],
            (diary_lamp_claim_id(tier.id), "agility"),
        )
        parent, chooser_title, eligible_skill_ids = chooser.call_args.args
        self.assertEqual(parent.objectName(), "bankClaimsBox")
        self.assertEqual(chooser_title, title)
        self.assertIn("agility", eligible_skill_ids)

    def test_bank_death_office_reclaim_row_uses_combat_office_state(self) -> None:
        pd = _make_player_data()
        pd["inventory"]["Coins"] = 250
        pd["death_office"] = {"items": ["Bronze sword", "Cape"], "source": "combat_stacked_grave"}
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Death's Office", labels)
        self.assertIn("2 reclaimed gear items", labels)
        self.assertIn("Cost: 200 Coins · Bank: 250 Coins", labels)
        row = _find_named_widget(dialog, "deathOfficeRow")
        self.assertIsNotNone(row)
        reclaim_btn = dialog.findChild(QPushButton, "deathOfficeReclaimAction")
        self.assertIsNotNone(reclaim_btn)
        self.assertTrue(reclaim_btn.isEnabled())
        reclaim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._death_office_calls, [True])

    def test_bank_claims_expose_tutorial_starter_kit_bundle(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Tutorial Island starter kit", labels)
        self.assertTrue(
            any(label.startswith("11 item stacks - Bronze sword x1, Wooden shield x1, Shortbow x1") for label in labels),
            labels,
        )
        metadata = _find_named_label(dialog, "bankClaimMetadata")
        self.assertIn("Tinderbox x1", metadata.toolTip())
        claim_btn = next(
            btn for btn in dialog.findChildren(QPushButton)
            if btn.text() == "Claim"
        )
        claim_btn.click()
        QApplication.processEvents()
        self.assertEqual(self._claim_calls[-1], ("tutorial_island_starter_kit", None))

    def test_bank_claims_hide_locked_rows_entirely(self) -> None:
        pd = _make_player_data()
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("Tutorial Island starter kit", labels)
        self.assertNotIn("Wicked hood x1", labels)
        # The old summary named one arbitrary locked reward and counted the
        # rest as "N more hidden", which the player could not act on.
        self.assertFalse(any("locked reward" in label for label in labels), labels)
        self.assertEqual(
            [lbl for lbl in dialog.findChildren(QLabel)
             if lbl.objectName() == "bankClaimsLockedSummary"],
            [],
        )
        self.assertEqual(
            len([w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"]),
            1,
            "only actionable claims should render as individual action rows",
        )

    def test_bank_claims_locked_only_save_reads_as_caught_up(self) -> None:
        # Removing the locked summary left this save rendering a bare "Bank
        # Claims" header with nothing under it.
        pd = _make_player_data()
        pd.setdefault("claims", {})["tutorial_island_starter_kit"] = {"claimed": True}
        dialog = self._open(pd)
        _open_bank_tab(dialog)

        labels = [lbl.text() for lbl in dialog.findChildren(QLabel)]
        self.assertIn("Bank Claims", labels)
        self.assertIn("All Bank Claims caught up.", labels)
        self.assertEqual(
            [w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"],
            [],
        )

    def test_bank_claims_inbox_is_capped_above_inventory(self) -> None:
        pd = _make_player_data()
        pd["inventory"] = {"Logs": 5}
        original_claim_data = self._ui.CLAIM_DATA
        self._ui.CLAIM_DATA = {
            f"test_claim_{i}": {
                "display_name": f"Test reward {i}",
                "claim_type": "item",
                "item_name": f"Test reward {i}",
                "quantity": 1,
            }
            for i in range(5)
        }
        try:
            dialog = self._open(pd)
            _open_bank_tab(dialog)
        finally:
            self._ui.CLAIM_DATA = original_claim_data

        claim_rows = [w for w in dialog.findChildren(QWidget) if w.objectName() == "bankClaimRow"]
        self.assertEqual(len(claim_rows), 5)
        scroll = _find_named_widget(dialog, "bankClaimsScrollArea")
        claims_box = _find_named_widget(dialog, "bankClaimsBox")
        self.assertLessEqual(scroll.maximumHeight(), 160)
        self.assertLessEqual(claims_box.maximumHeight(), 210)
        self.assertIsNot(_find_bank_grid(dialog), _find_gear_list(dialog))
