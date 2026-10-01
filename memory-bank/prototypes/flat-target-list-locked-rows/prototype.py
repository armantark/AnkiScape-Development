"""PROTOTYPE ONLY (ruling 4.29.6): three ways to stop long locked rows in the
flat Skills target list from clipping, applied live to the real Skills dialog.

Run from the repo root:
    .venv-qt/bin/python memory-bank/prototypes/flat-target-list-locked-rows/prototype.py
    (add --skill fishing, --dark, or --capture to write the PNGs offscreen)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import qt_variant_switcher as sw  # noqa: E402

VARIANTS = {
    "A": "Wrap the row",
    "B": "Name line + lock line",
    "C": "Short row, reason in tooltip and Details",
}
LOCK_SPLIT = " — Locked: "
ORIGINAL_TEXT_ROLE = 0x0100 + 50  # Qt.UserRole + 50


def player_data(level: int) -> dict:
    from ankiscape.core.constants import EXP_TABLE
    from tests.test_main_menu_widget import _make_player_data

    data = _make_player_data()
    for key in [key for key in data if key.endswith("_level")]:
        data[key] = level
        data[key.replace("_level", "_exp")] = float(EXP_TABLE[level - 1])
    return data


def open_dialog(skill: str, level: int):
    from tests.test_main_menu_widget import MainMenuWidgetTest

    MainMenuWidgetTest.setUpClass()
    harness = MainMenuWidgetTest(methodName="runTest")
    harness.setUp()
    dialog = harness._open(player_data(level), current_skill=skill.title())
    dialog._prototype_harness = harness
    return dialog


def target_list(dialog, skill: str):
    from aqt.qt import QListWidget

    return dialog.findChild(QListWidget, f"{skill}TargetTree")


def lock_reasons(item) -> str:
    for line in (item.toolTip() or "").splitlines():
        if line.startswith("Locked due to:"):
            return line.split(":", 1)[1].strip()
    return ""


def is_locked(item) -> bool:
    from aqt.qt import Qt

    return not (item.flags() & Qt.ItemFlag.ItemIsEnabled)


def short_label(text: str) -> str:
    """Name only: drop the lock suffix and fold extra catches into '+N more',
    keeping a trailing location so sibling rows stay distinguishable."""
    name = text.split(LOCK_SPLIT)[0]
    head, sep, rest = name.partition("/")
    if not sep:
        return name
    extra = rest.count("/") + 1
    location = ""
    if rest.endswith(")") and " (" in rest:
        tail = rest[rest.rindex(" (") + 1:]
        if not tail.startswith("(Lvl"):
            location = f" {tail}"
    return f"{head} +{extra} more{location}"


def two_line_delegate_class():
    from aqt.qt import (
        QFontMetrics,
        QIcon,
        QRect,
        QSize,
        QStyle,
        QStyledItemDelegate,
        QStyleOptionViewItem,
        Qt,
    )

    flags = int(Qt.TextFlag.TextWordWrap.value | Qt.AlignmentFlag.AlignLeft.value | Qt.AlignmentFlag.AlignTop.value)

    class NameAndLockDelegate(QStyledItemDelegate):
        """Variant B: the name on the first line, every lock reason from the
        tooltip on a smaller second line; both wrap at the painted width."""

        PAD = 4
        ICON = 28

        def _parts(self, index):
            text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
            name = text.split(LOCK_SPLIT)[0]
            locked = not (index.flags() & Qt.ItemFlag.ItemIsEnabled)
            reason = ""
            if locked:
                tip = str(index.data(Qt.ItemDataRole.ToolTipRole) or "")
                reasons = [line.split(":", 1)[1].strip() for line in tip.splitlines() if line.startswith("Locked due to:")]
                reason = f"Locked: {reasons[0]}" if reasons else ""
            return name, reason, locked

        def _fonts(self, option):
            small = option.font.__class__(option.font)
            small.setPointSizeF(max(option.font.pointSizeF() - 1.5, 7.0))
            return option.font, small

        def _rects(self, option, index):
            name, reason, _locked = self._parts(index)
            name_font, small = self._fonts(option)
            rect = option.rect
            text_left = rect.left() + self.PAD + self.ICON + 6
            width = max(rect.right() - self.PAD - text_left, 40)
            name_h = QFontMetrics(name_font).boundingRect(QRect(0, 0, width, 10000), flags, name).height()
            name_rect = QRect(text_left, rect.top() + self.PAD, width, name_h)
            reason_rect = QRect(text_left, name_rect.bottom() + 2, width, 0)
            if reason:
                reason_h = QFontMetrics(small).boundingRect(QRect(0, 0, width, 10000), flags, reason).height()
                reason_rect.setHeight(reason_h)
            bottom = (reason_rect.bottom() if reason else name_rect.bottom()) + self.PAD
            height = max(bottom - rect.top() + 1, self.ICON + 2 * self.PAD)
            return name_rect, reason_rect, height

        def sizeHint(self, option, index):  # type: ignore[no-untyped-def]
            sized = QStyleOptionViewItem(option)
            self.initStyleOption(sized, index)
            sized.rect = QRect(0, 0, self.parent().viewport().width(), 100)
            return QSize(sized.rect.width(), self._rects(sized, index)[2])

        def paint(self, painter, option, index):  # type: ignore[no-untyped-def]
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            name, reason, locked = self._parts(index)
            icon = QIcon(opt.icon)  # opt.icon is a live reference, cleared just below
            opt.text = ""
            opt.icon = QIcon()
            style = opt.widget.style() if opt.widget else None
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)
            name_rect, reason_rect, _height = self._rects(opt, index)
            icon_rect = QRect(opt.rect.left() + self.PAD, opt.rect.top() + self.PAD, self.ICON, self.ICON)
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter, QIcon.Mode.Disabled if locked else QIcon.Mode.Normal)
            group = opt.palette.ColorGroup.Disabled if locked else opt.palette.ColorGroup.Normal
            name_font, small = self._fonts(opt)
            painter.save()
            painter.setPen(opt.palette.color(group, opt.palette.ColorRole.Text))
            painter.setFont(name_font)
            painter.drawText(name_rect, flags, name)
            if reason:
                painter.setFont(small)
                painter.drawText(reason_rect, flags, reason)
            painter.restore()

        def text_fits(self, option, index) -> bool:
            name_rect, reason_rect, height = self._rects(option, index)
            return height <= option.rect.height()

    return NameAndLockDelegate


def shorten_rows(lst) -> None:
    for index in range(lst.count()):
        row = lst.item(index)
        mark = "\u2713 " if row.text().startswith("\u2713 ") else ""
        row.setText(mark + short_label(row.text().removeprefix(mark)))


def reset(lst) -> None:
    from aqt.qt import QStyledItemDelegate, Qt

    lst.setItemDelegate(QStyledItemDelegate(lst))
    lst.setWordWrap(False)
    lst.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    for index in range(lst.count()):
        item = lst.item(index)
        original = item.data(ORIGINAL_TEXT_ROLE)
        if original is None:
            item.setData(ORIGINAL_TEXT_ROLE, item.text())
        else:
            item.setText(original)


def wrap(lst) -> None:
    from aqt.qt import QListWidget, Qt
    from ankiscape.ui.ui_tab_shop_widgets import WrappedRowDelegate

    lst.setWordWrap(True)
    lst.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    lst.setResizeMode(QListWidget.ResizeMode.Adjust)
    lst.setItemDelegate(WrappedRowDelegate(lst))


def apply_variant(dialog, skill: str, key: str) -> None:
    from aqt.qt import QListWidget, Qt

    lst = target_list(dialog, skill)
    reset(lst)
    if key == "A":
        wrap(lst)
    elif key == "B":
        lst.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lst.setResizeMode(QListWidget.ResizeMode.Adjust)
        lst.setItemDelegate(two_line_delegate_class()(lst))
    else:
        shorten_rows(lst)
        # A row can still outgrow a narrow list, so the short form keeps the wrap fallback.
        wrap(lst)
        if not getattr(lst, "_prototype_c_hooked", False):
            lst._prototype_c_hooked = True
            # Production's click handler rewrites every label in full.
            lst.itemClicked.connect(lambda _item: lst._prototype_variant == "C" and shorten_rows(lst))
    lst._prototype_variant = key
    lst.doItemsLayout()


def longest_locked(lst):
    locked = [lst.item(i) for i in range(lst.count()) if is_locked(lst.item(i))]
    return max(locked, key=lambda item: len(item.data(ORIGINAL_TEXT_ROLE) or item.text()))


def describe(dialog, skill: str) -> str:
    from aqt.qt import QStyle, QStyleOptionViewItem, Qt, QRect

    lst = target_list(dialog, skill)
    delegate = lst.itemDelegate()
    wrap_flags = int(Qt.TextFlag.TextWordWrap.value)
    lines = [
        f"dialog {dialog.width()}x{dialog.height()}  list viewport {lst.viewport().width()}x{lst.viewport().height()}"
        f"  sideways scroll range {lst.horizontalScrollBar().maximum()}"
    ]
    clipped = 0
    for index in range(lst.count()):
        item = lst.item(index)
        if not is_locked(item):
            continue
        model_index = lst.indexFromItem(item)
        option = QStyleOptionViewItem()
        lst.initViewItemOption(option)
        delegate.initStyleOption(option, model_index)
        option.rect = lst.visualItemRect(item)
        if hasattr(delegate, "text_fits"):
            fits = delegate.text_fits(option, model_index)
        else:
            text_rect = lst.style().subElementRect(QStyle.SubElement.SE_ItemViewItemText, option, lst)
            needed = option.fontMetrics.boundingRect(QRect(0, 0, text_rect.width(), 10000), wrap_flags, item.text())
            fits = (
                lst.horizontalScrollBar().maximum() == 0
                and needed.width() <= text_rect.width()
                and needed.height() <= text_rect.height()
            )
        clipped += not fits
        lines.append(f"  {'fits ' if fits else 'CLIPS'} h={option.rect.height():>3}  {item.text()!r}")
    lines.append(f"locked rows clipped: {clipped}")
    return "\n".join(lines)


def show_row(dialog, skill: str) -> None:
    lst = target_list(dialog, skill)
    row = longest_locked(lst)
    lst.scrollToItem(row, lst.ScrollHint.PositionAtCenter)
    sw.pump()


def capture() -> None:
    from aqt.qt import QApplication

    app = QApplication.instance() or QApplication([])
    failures = []
    for skill in ("agility", "fishing"):
        for theme in ("light", "dark"):
            sw.apply_theme(theme)
            for width in (720, 900):
                for key in VARIANTS:
                    dialog = open_dialog(skill, 85)
                    dialog.show()
                    dialog.resize(width, 560)
                    sw.pump()
                    apply_variant(dialog, skill, key)
                    sw.pump()
                    show_row(dialog, skill)
                    state = describe(dialog, skill)
                    name = f"{skill}-{key}-{theme}-{width}x560.png"
                    dialog.grab().save(str(HERE / name))
                    print(f"--- {name}\n{state}")
                    if not state.endswith("clipped: 0"):
                        failures.append(name)
                    dialog.hide()
                    dialog.deleteLater()
                    sw.pump()
    app.processEvents()
    print("FAILURES:", failures or "none")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", choices=("agility", "fishing"), default="agility")
    parser.add_argument("--level", type=int, default=85)
    parser.add_argument("--dark", action="store_true", help="Fusion dark palette instead of the OS look")
    parser.add_argument("--capture", action="store_true", help="write every variant PNG offscreen and exit")
    args = parser.parse_args()
    sw.prepare_qt(args.capture)
    from aqt.qt import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    if args.capture:
        capture()
        return
    if args.dark:
        sw.apply_theme("dark")
    dialog = open_dialog(args.skill, args.level)
    dialog.setWindowTitle(f"PROTOTYPE 4.29.6 — {args.skill.title()} target list")
    dialog.show()
    dialog.resize(720, 560)
    sw.pump()

    def _apply(key: str) -> str:
        apply_variant(dialog, args.skill, key)
        show_row(dialog, args.skill)
        return describe(dialog, args.skill)

    dialog._switcher = sw.make_switcher(VARIANTS, _apply, dialog)
    app.exec()


if __name__ == "__main__":
    main()
