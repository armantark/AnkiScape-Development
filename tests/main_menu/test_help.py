from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_named_label,
    _find_named_line_edit,
    _find_named_list,
    _find_named_widget,
    _list_texts,
    _make_player_data,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QColor, QEvent, QPalette, QTextBrowser, QToolButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_contextual_help_maps_every_primary_tab_without_changing_page(self) -> None:
        expected_titles = {
            "Skills": "Skills and training",
            "Shop": "NPC shops",
            "Grand Exchange": "Grand Exchange",
            "Quests": "Quests",
            "Bank": "Bank and inventory actions",
            "Equipment": "Equipment and familiars",
            "Stats": "Stats",
            "Challenges": "Daily Challenges",
            "Achievements": "Achievements",
            "Collections": "Collections",
            "Settings": "Settings",
        }
        tabs = _find_main_tabs(self.dialog)
        button = self.dialog.findChild(QToolButton, "mainMenuHelpButton")
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        topic_title = _find_named_label(self.dialog, "helpTopicTitle")
        self.assertIsNotNone(button)
        self.assertTrue(panel.isHidden())
        original_width = self.dialog.width()

        for index in range(tabs.count()):
            with self.subTest(tab=tabs.tabText(index)):
                tabs.setCurrentIndex(index)
                QApplication.processEvents()
                selected_index = tabs.currentIndex()
                button.click()
                QApplication.processEvents()

                self.assertFalse(panel.isHidden())
                self.assertEqual(tabs.currentIndex(), selected_index)
                self.assertEqual(
                    topic_title.text(),
                    expected_titles[tabs.tabText(index)],
                )
                self.assertEqual(
                    button.toolTip(),
                    f"Help for {tabs.tabText(index)} (F1)",
                )

        self.assertGreaterEqual(self.dialog.width(), original_width)
        self.assertTrue(button.shortcut().toString())
        self.dialog.findChild(QToolButton, "helpCloseButton").click()
        QApplication.processEvents()
        self.assertTrue(panel.isHidden())
        self.assertEqual(self.dialog.width(), original_width)

    def test_help_search_escape_empty_state_and_topic_navigation(self) -> None:
        from aqt.qt import QKeyEvent, QTextBrowser, QUrl

        _find_main_tabs(self.dialog).setCurrentIndex(0)
        self.dialog.findChild(QToolButton, "mainMenuHelpButton").click()
        QApplication.processEvents()

        search = _find_named_line_edit(self.dialog, "helpSearch")
        topic_list = _find_named_list(self.dialog, "helpTopicList")
        empty = _find_named_label(self.dialog, "helpEmptyState")
        search.setText("familiar duration")
        QApplication.processEvents()
        self.assertEqual(
            set(_list_texts(topic_list)),
            {"Simulated time", "Summoning and familiars"},
        )
        topic_list.itemClicked.emit(topic_list.item(0))
        QApplication.processEvents()
        self.assertEqual(search.text(), "familiar duration")
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Simulated time",
        )
        self.assertEqual(
            _find_named_label(self.dialog, "helpSearchSummary").text(),
            "",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()
        self.assertEqual(search.text(), "familiar duration")
        self.assertEqual(set(_list_texts(topic_list)), {"Simulated time", "Summoning and familiars"})
        self.dialog.findChild(QToolButton, "helpForwardButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Simulated time",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()

        search.setText("definitely-not-help-content")
        QApplication.processEvents()
        self.assertTrue(topic_list.isHidden())
        self.assertFalse(empty.isHidden())
        self.assertIn("No help topics match", empty.text())

        escape = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertEqual(search.text(), "")
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        self.assertIs(panel.results_stack.currentWidget(), topic_list)
        self.assertIn("Using AnkiScape", _list_texts(topic_list))

        self.dialog.show()
        search.setFocus()
        QApplication.processEvents()
        down = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Down,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, down)
        QApplication.processEvents()
        self.assertEqual(topic_list.currentRow(), 0)
        self.assertIs(QApplication.focusWidget(), topic_list)

        panel.open_topic("skills")
        body = self.dialog.findChild(QTextBrowser, "helpTopicBody")
        body.anchorClicked.emit(QUrl("help:automation"))
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Casual and Advanced automation",
        )
        self.dialog.findChild(QToolButton, "helpBackButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Skills and training",
        )
        self.dialog.findChild(QToolButton, "helpForwardButton").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(self.dialog, "helpTopicTitle").text(),
            "Casual and Advanced automation",
        )

        search.setFocus()
        rejected: list[bool] = []
        self.dialog.rejected.connect(lambda: rejected.append(True))
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertTrue(panel.isHidden())
        self.assertEqual(rejected, [])

    def test_help_drawer_clamps_right_edge_to_the_available_screen(self) -> None:
        screen = self.dialog.screen() or QApplication.primaryScreen()
        self.assertIsNotNone(screen)
        available = screen.availableGeometry()
        self.dialog.resize(720, 540)
        self.dialog.move(available.right() - 40, available.top())

        self.dialog.findChild(QToolButton, "mainMenuHelpButton").click()
        QApplication.processEvents()

        self.assertGreaterEqual(self.dialog.x(), available.left())
        self.assertLessEqual(
            self.dialog.x() + self.dialog.width() - 1,
            available.right(),
        )

    def test_help_missing_topic_falls_back_home_or_fails_visibly_in_developer_mode(self) -> None:
        panel = _find_named_widget(self.dialog, "helpCenterPanel")
        title = _find_named_label(self.dialog, "helpTopicTitle")

        self.assertFalse(panel.open_topic("does-not-exist"))
        self.assertEqual(title.text(), "Broken Help reference")
        self.assertIn(
            "Unknown help topic",
            self.dialog.findChild(QTextBrowser, "helpTopicBody").toPlainText(),
        )

        panel._developer_mode = False
        self.assertTrue(panel.open_topic("does-not-exist"))
        self.assertEqual(title.text(), "Using AnkiScape")

    def test_help_dim_text_uses_the_dark_theme_text_role(self) -> None:
        original_palette = QApplication.palette()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
        dark.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
        dark.setColor(QPalette.ColorRole.Mid, QColor(8, 8, 8))
        QApplication.setPalette(dark)
        try:
            dialog = self._open(_make_player_data())
            dialog.findChild(QToolButton, "mainMenuHelpButton").click()
            QApplication.processEvents()
            empty = _find_named_label(dialog, "helpEmptyState")
            self.assertIn("rgba(238, 238, 238", empty.styleSheet())
            self.assertNotIn("color: palette(mid)", empty.styleSheet())
            dialog.deleteLater()
        finally:
            QApplication.setPalette(original_palette)
