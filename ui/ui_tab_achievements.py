"""ui_tab_achievements.py - the main menu's Achievements tab.

Built on first show by ``show_main_menu`` rather than on open: one card per
achievement is over a thousand widgets and a scaled QPixmap each, which nobody
sees until they click the tab.
"""
import os

try:
    from aqt.qt import (  # type: ignore
        Qt,
        QHBoxLayout,
        QLabel,
        QPixmap,
        QProgressBar,
        QScrollArea,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

try:
    from .constants import ACHIEVEMENTS, current_dir
    from .achievement_metadata import (
        ACHIEVEMENT_DIFFICULTIES,
        achievement_difficulty_progress,
        achievement_progress,
        achievement_rows_for_difficulty,
    )
except Exception:
    from constants import ACHIEVEMENTS, current_dir  # type: ignore
    from achievement_metadata import (  # type: ignore
        ACHIEVEMENT_DIFFICULTIES,
        achievement_difficulty_progress,
        achievement_progress,
        achievement_rows_for_difficulty,
    )


def build_achievements_tab(ctx) -> "QWidget":
    """Return the Achievements page (inline, themed)."""
    player_data = ctx.player_data

    ach_tab = QWidget()
    a_layout = QVBoxLayout(ach_tab)
    a_layout.setContentsMargins(12, 12, 12, 12)
    a_layout.setSpacing(8)
    a_tabs = QTabWidget()
    a_tabs.setDocumentMode(True)

    def _make_achievement_card(title: str, desc: str, completed: bool) -> QWidget:
        card = QWidget()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(10)
        # Icon
        icon_label = QLabel()
        icon_path = os.path.join(current_dir, "icon", f"{title.lower().replace(' ', '_')}.png")
        pixmap = QPixmap(icon_path) if os.path.exists(icon_path) else QPixmap(os.path.join(current_dir, "icon", "achievement_icon.png"))
        icon_label.setPixmap(pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        card_layout.addWidget(icon_label)
        # Info
        info = QWidget()
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(2)
        name = QLabel(title)
        name.setStyleSheet("font-weight: 600;")
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        il.addWidget(name)
        il.addWidget(desc_label)
        card_layout.addWidget(info, 1)
        # Status
        status = QLabel("✓" if completed else "")
        status.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 700;")
        card_layout.addWidget(status, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # Themed card style (palette-aware)
        card.setStyleSheet(
            "border: 1px solid palette(mid); border-radius: 6px; background-color: palette(base);"
        )
        return card

    for difficulty in ACHIEVEMENT_DIFFICULTIES:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        rows = achievement_rows_for_difficulty(ACHIEVEMENTS, player_data, difficulty)
        done, total = achievement_difficulty_progress(ACHIEVEMENTS, player_data, difficulty)
        header = QLabel(f"{difficulty} • {done}/{total} completed")
        header.setStyleSheet("font-weight: 600; margin: 0 0 6px 0;")
        tab_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)
        for row in rows:
            card = _make_achievement_card(row.name, row.description, row.completed)
            cl.addWidget(card)
        cl.addStretch(1)
        scroll.setWidget(content)
        tab_layout.addWidget(scroll)
        a_tabs.addTab(tab, difficulty)

    a_layout.addWidget(a_tabs)

    completed_count, total_count, progress_percentage = achievement_progress(ACHIEVEMENTS, player_data)
    progress_row = QWidget()
    prl = QHBoxLayout(progress_row)
    prl.setContentsMargins(0, 0, 0, 0)
    prl.setSpacing(8)
    progress_label = QLabel(f"Completed: {completed_count}/{total_count} ({progress_percentage:.1f}%)")
    prl.addWidget(progress_label)
    progress_bar = QProgressBar()
    progress_bar.setValue(int(progress_percentage))
    progress_bar.setTextVisible(False)
    prl.addWidget(progress_bar, 1)
    a_layout.addWidget(progress_row)

    return ach_tab
