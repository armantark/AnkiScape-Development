"""ui_tab_achievements.py - the main menu's Achievement Cabinet.

Built on first show by ``show_main_menu`` rather than on open: the Cabinet
renders every task in every tier, which nobody sees until they click the tab.

This replaced a flat list of 168 fabricated skill-progression rows in four
invented difficulty buckets. Two things about that list were wrong beyond the
content: it occupied the surface the real diary system belongs on, and it
displayed a completion percentage whose denominator moved whenever an
achievement was added — the exact figure the 2026-07-16 semantics contract
forbids diary gear from consuming. Neither survives here. The only counts shown
are a tier's own ``done/total`` over its fixed task list.

The panel is deliberately thin. Every enable, every status string and every lamp
option comes from ``achievement_cabinet_view_pure``; nothing here re-derives a
rule the logic layer owns.
"""

try:
    from aqt.qt import (  # type: ignore
        Qt,
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..logic.achievement_diary_logic import achievement_cabinet_view_pure
from .ui import CatalogFilterBar, _clear_layout, dim_text_css


def build_achievements_tab(ctx) -> "QWidget":
    """Return the Achievement Cabinet page."""
    player_data = ctx.player_data
    on_command = getattr(ctx, "on_achievement_diary_command", None)

    page = QWidget()
    page.setObjectName("achievementCabinet")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)

    heading = QHBoxLayout()
    heading.setSpacing(8)
    title = QLabel("Achievement Cabinet")
    title.setStyleSheet("font-weight: 700; font-size: 15px; color: palette(text);")
    heading.addWidget(title)
    totals = QLabel("")
    totals.setObjectName("cabinetTotals")
    totals.setStyleSheet(f"color: {dim_text_css(totals)};")
    heading.addWidget(totals)
    heading.addStretch(1)
    seal = QLabel("")
    seal.setObjectName("cabinetTaskmasterSeal")
    heading.addWidget(seal)
    layout.addLayout(heading)

    filters = CatalogFilterBar(
        placeholder="Search tasks by name or deed",
        search_object_name="cabinetSearch",
    )
    family_box = QComboBox()
    family_box.setObjectName("cabinetFamilyFilter")
    tier_box = QComboBox()
    tier_box.setObjectName("cabinetTierFilter")
    state_box = QComboBox()
    state_box.setObjectName("cabinetStateFilter")
    for label, value in (("All", ""), ("Incomplete", "incomplete"), ("Complete", "complete")):
        state_box.addItem(label, value)
    filters.add_filter(family_box, "Family")
    filters.add_filter(tier_box, "Tier")
    filters.add_filter(state_box, "State")
    layout.addWidget(filters)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("border: none;")
    body = QWidget()
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setSpacing(10)
    scroll.setWidget(body)
    layout.addWidget(scroll, 1)

    def _run(action_id: str, payload: dict) -> None:
        if on_command is None:
            return
        on_command(action_id, payload)
        _render()

    def _task_row(task: dict) -> "QWidget":
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 5, 8, 5)
        row_layout.setSpacing(8)

        pin = QToolButton()
        pin.setText("★" if task["pinned"] else "☆")
        pin.setToolTip("Pin this task to the top of its tier")
        pin.setEnabled(on_command is not None)
        pin.clicked.connect(
            lambda _=False, tid=task["task_id"]: _run("pin_task", {"task_id": tid})
        )
        row_layout.addWidget(pin)

        text = QWidget()
        text_layout = QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        name = QLabel(task["name"])
        name.setStyleSheet("font-weight: 600; color: palette(text);")
        text_layout.addWidget(name)
        detail = QLabel(task["description"])
        detail.setWordWrap(True)
        detail.setStyleSheet(f"color: {dim_text_css(detail)};")
        text_layout.addWidget(detail)
        if task["requirements"]:
            requirement = QLabel(" · ".join(task["requirements"]))
            requirement.setWordWrap(True)
            requirement.setStyleSheet(f"color: {dim_text_css(requirement)};")
            text_layout.addWidget(requirement)
        row_layout.addWidget(text, 1)

        if task["staged"] and not task["completed"]:
            progress = QLabel(f"{task['have']}/{task['need']}")
            progress.setStyleSheet(f"color: {dim_text_css(progress)};")
            row_layout.addWidget(progress)
        status = QLabel("✓" if task["completed"] else "")
        status.setStyleSheet("color: #4CAF50; font-size: 15px; font-weight: 700;")
        row_layout.addWidget(
            status, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        row.setStyleSheet(
            "border: 1px solid palette(mid); border-radius: 6px;"
            " background-color: palette(base);"
        )
        return row

    def _tier_block(tier: dict) -> "QWidget":
        block = QWidget()
        block_layout = QVBoxLayout(block)
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.setSpacing(5)

        header = QHBoxLayout()
        header.setSpacing(8)
        label = QLabel(f"{tier['name']} · {tier['done']}/{tier['total']}")
        label.setStyleSheet("font-weight: 600; color: palette(text);")
        header.addWidget(label)
        status = QLabel(tier["status"])
        status.setObjectName(f"cabinetStatus_{tier['tier_id']}")
        status.setStyleSheet(f"color: {dim_text_css(status)};")
        header.addWidget(status)
        header.addStretch(1)

        lamp_box = None
        if tier["lamp"] and tier["lamp"]["choice_required"] and not tier["claimed"]:
            lamp_box = QComboBox()
            lamp_box.setObjectName(f"cabinetLamp_{tier['tier_id']}")
            for skill_id in tier["lamp"]["options"]:
                lamp_box.addItem(skill_id.replace("_", " ").title(), skill_id)
            lamp_box.setToolTip(f"{tier['lamp']['experience']:,} experience lamp")
            header.addWidget(lamp_box)

        claim = QPushButton("Claim")
        claim.setObjectName(f"cabinetClaim_{tier['tier_id']}")
        claim.setEnabled(bool(tier["ready"]) and on_command is not None)
        claim.clicked.connect(
            lambda _=False, tid=tier["tier_id"], box=lamp_box: _run(
                "claim_tier",
                {
                    "tier_id": tid,
                    "lamp_skill": box.currentData() if box is not None else "",
                },
            )
        )
        header.addWidget(claim)
        block_layout.addLayout(header)

        reward = QLabel(f"{tier['reward_item']} — {tier['reward_summary']}")
        reward.setWordWrap(True)
        reward.setStyleSheet(f"color: {dim_text_css(reward)};")
        block_layout.addWidget(reward)

        bar = QProgressBar()
        bar.setMaximum(max(1, tier["total"]))
        bar.setValue(tier["done"])
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        block_layout.addWidget(bar)

        for task in tier["tasks"]:
            block_layout.addWidget(_task_row(task))
        return block

    def _render() -> None:
        _clear_layout(body_layout)
        view = achievement_cabinet_view_pure(
            player_data,
            family_filter=family_box.currentData() or "",
            tier_filter=tier_box.currentData() or "",
            completion_filter=state_box.currentData() or "",
            search=filters.query(),
        )
        if family_box.count() == 0:
            family_box.addItem("All", "")
            for family_id, name in view["filters"]["families"]:
                family_box.addItem(name, family_id)
            tier_box.addItem("All", "")
            for tier_name in view["filters"]["tiers"]:
                tier_box.addItem(tier_name, tier_name)

        totals.setText(f"{view['completed']}/{view['total']} tasks")
        seal.setText("Taskmaster" if view["taskmaster"] else "")
        seal.setStyleSheet(
            "color: #C9A227; font-weight: 700;" if view["taskmaster"] else ""
        )
        seal.setToolTip(
            "Every regional task complete" if view["taskmaster"] else ""
        )

        shown = 0
        for family in view["families"]:
            card = QWidget()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(8)
            name = QLabel(family["name"])
            name.setStyleSheet("font-weight: 700; color: palette(text);")
            card_layout.addWidget(name)
            for tier in family["tiers"]:
                shown += len(tier["tasks"])
                card_layout.addWidget(_tier_block(tier))
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("color: palette(mid);")
                card_layout.addWidget(line)
            card.setStyleSheet(
                "border: 1px solid palette(mid); border-radius: 8px;"
                " background-color: palette(alternate-base);"
            )
            body_layout.addWidget(card)
        body_layout.addStretch(1)
        filters.set_count(shown, view["total"])

    filters.search_input.textChanged.connect(lambda _text: _render())
    for box in (family_box, tier_box, state_box):
        box.currentIndexChanged.connect(lambda _index: _render())

    _render()
    ctx.refreshers["achievements"] = _render
    return page
