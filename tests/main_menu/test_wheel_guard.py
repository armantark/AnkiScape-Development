from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_ge_tab
if HAS_AQT:
    from aqt.qt import (
        QAbstractSpinBox,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QLabel,
        QPoint,
        QPointF,
        QScrollArea,
        QSpinBox,
        Qt,
        QVBoxLayout,
        QWheelEvent,
        QWidget,
    )
from tests.main_menu import fixtures


def _wheel(widget, delta: int) -> None:
    centre = widget.rect().center()
    QApplication.sendEvent(
        widget,
        QWheelEvent(
            QPointF(centre),
            QPointF(widget.mapToGlobal(centre)),
            QPoint(0, 0),
            QPoint(0, delta),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        ),
    )


def _choice(widget):
    return widget.currentIndex() if isinstance(widget, QComboBox) else widget.value()


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class WheelGuardSceneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def _scene(self, guarded: bool):
        from ankiscape.ui.ui_text_fit import guard_wheel

        dialog = QDialog()
        self.addCleanup(dialog.deleteLater)
        if guarded:
            guard_wheel(dialog)
        dialog.resize(300, 200)
        scroll = QScrollArea()
        QVBoxLayout(dialog).addWidget(scroll)
        body = QWidget()
        column = QVBoxLayout(body)
        spin = QSpinBox()
        spin.setValue(5)
        combo = QComboBox()
        combo.addItems(["a", "b", "c"])
        combo.setCurrentIndex(1)
        for widget in (spin, combo, *(QLabel(str(row)) for row in range(40))):
            column.addWidget(widget)
        scroll.setWidget(body)
        scroll.setWidgetResizable(True)
        dialog.show()
        for _ in range(4):
            QApplication.processEvents()
        return scroll, spin, combo

    def test_wheel_over_a_box_scrolls_the_page_and_keeps_the_choice(self) -> None:
        scroll, spin, combo = self._scene(guarded=True)
        bar = scroll.verticalScrollBar()
        for box in (spin, combo):
            before = (_choice(box), bar.value())
            _wheel(box, -120)
            self.assertEqual(_choice(box), before[0])
            self.assertGreater(bar.value(), before[1])

    def test_a_window_that_did_not_opt_in_keeps_the_native_wheel(self) -> None:
        _scroll, spin, combo = self._scene(guarded=False)
        for box in (spin, combo):
            before = _choice(box)
            _wheel(box, -120)
            self.assertNotEqual(_choice(box), before)


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWheelGuardTest(fixtures.MainMenuWidgetTest):
    def _assert_wheel_changes_nothing(self, boxes) -> None:
        self.assertTrue(boxes)
        for box in boxes:
            for delta in (120, -120):
                with self.subTest(box=box.objectName(), delta=delta):
                    before = _choice(box)
                    _wheel(box, delta)
                    self.assertEqual(_choice(box), before)

    def test_settings_boxes_ignore_the_wheel(self) -> None:
        self.dialog.findChild(QCheckBox, "settingsWorldDayFollowToggle").setChecked(False)
        QApplication.processEvents()
        self._assert_wheel_changes_nothing(
            [
                self.dialog.findChild(QSpinBox, "settingsActionMultiplierSpin"),
                self.dialog.findChild(QSpinBox, "settingsWorldDayCardsSpin"),
            ]
        )

    def test_grand_exchange_boxes_ignore_the_wheel(self) -> None:
        _open_ge_tab(self.dialog)
        self._assert_wheel_changes_nothing(
            [self.dialog.findChild(QSpinBox, name) for name in ("geOfferQuantitySpin", "geOfferPriceSpin")]
        )

    def test_boxes_built_in_a_loop_ignore_the_wheel(self) -> None:
        dialog = self._open(_make_player_data(), current_skill="Mining")
        self._open_activity_detail(dialog, "fishing_trawler")
        loop_built = [dialog.findChild(QSpinBox, f"fishingTrawler{name}Spin") for name in ("Paste", "Rope", "Buckets")]
        self._assert_wheel_changes_nothing(loop_built)

    def test_every_box_and_list_in_the_menu_ignores_the_wheel(self) -> None:
        _open_ge_tab(self.dialog)
        self._assert_wheel_changes_nothing(
            [*self.dialog.findChildren(QAbstractSpinBox), *self.dialog.findChildren(QComboBox)]
        )
