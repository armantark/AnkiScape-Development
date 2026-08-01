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
from .ui import CatalogFilterBar, _clear_layout, _set_slayer_master_chathead, dim_text_css

# How many track rows the Music Log card leaves on screen when collapsed. The
# dialog is about 560 logical points tall, so the families below the card must
# stay reachable without scrolling past a wall of music. The remaining rows are
# built and hidden rather than dropped, so every track has a route.
MUSIC_ROWS_SHOWN = 12


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

        items = ", ".join(tier["reward_items"])
        reward = QLabel(
            f"{items} — {tier['reward_summary']}" if items else tier["reward_summary"]
        )
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

    def _card(title: str) -> "tuple[QWidget, QVBoxLayout]":
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(6)
        heading_label = QLabel(title)
        heading_label.setStyleSheet("font-weight: 700; color: palette(text);")
        card_layout.addWidget(heading_label)
        card.setStyleSheet(
            "border: 1px solid palette(mid); border-radius: 8px;"
            " background-color: palette(alternate-base);"
        )
        return card, card_layout

    def _taskmaster_card(presentation: dict) -> "QWidget":
        """The one-time presentation. It grants nothing; it says the thing."""

        card, card_layout = _card(presentation["title"])
        body_label = QLabel(presentation["body"])
        body_label.setWordWrap(True)
        body_label.setStyleSheet("color: palette(text);")
        card_layout.addWidget(body_label)
        acknowledge = QPushButton("Accept the seal")
        acknowledge.setObjectName("cabinetTaskmasterAcknowledge")
        acknowledge.setEnabled(on_command is not None)
        acknowledge.clicked.connect(lambda _=False: _run("acknowledge_taskmaster", {}))
        card_layout.addWidget(acknowledge)
        card.setStyleSheet(
            "border: 2px solid #C9A227; border-radius: 8px;"
            " background-color: palette(alternate-base);"
        )
        return card

    def _cape_row(row: dict) -> "QWidget":
        line = QWidget()
        line_layout = QHBoxLayout(line)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(8)

        # A vertical text block rather than one long line: the Completionist
        # row's reason is its whole outstanding requirement list, which pushes
        # the page into a sideways scroll at the real dialog width if it has to
        # share a line with the name, the master and the price.
        text = QWidget()
        text_layout = QVBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        name = QLabel(row["name"] + (" ★" if row.get("keepsake") else ""))
        name.setStyleSheet("color: palette(text);")
        text_layout.addWidget(name)
        detail = QLabel(f"{row['master']} · {row['price']:,} coins")
        detail.setWordWrap(True)
        detail.setStyleSheet(f"color: {dim_text_css(detail)};")
        text_layout.addWidget(detail)
        if row["reason"]:
            status = QLabel(row["reason"])
            status.setWordWrap(True)
            status.setStyleSheet(f"color: {dim_text_css(status)};")
            text_layout.addWidget(status)
        line_layout.addWidget(text, 1)
        return line

    def _capes_card(capes: dict) -> "QWidget":
        card, card_layout = _card("Capes and Distinctions")
        if capes["keepsake_cape"]:
            keepsake = QLabel(
                f"First 99: {capes['keepsake_cape']} — the Cabinet keeps its untrimmed artwork."
            )
            keepsake.setObjectName("cabinetKeepsake")
            keepsake.setWordWrap(True)
            keepsake.setStyleSheet(f"color: {dim_text_css(keepsake)};")
            card_layout.addWidget(keepsake)
        for row in capes["skillcapes"]:
            card_layout.addWidget(_cape_row(row))
        for row in capes["distinctions"]:
            card_layout.addWidget(_cape_row(row))
        outstanding = QLabel(
            " · ".join(
                f"{item['label']}{' (latent)' if item['latent'] else ''}"
                for item in capes["completionist"]
                if not item["met"]
            )
            or "Every Completionist requirement is met."
        )
        outstanding.setObjectName("cabinetCompletionistRequirements")
        outstanding.setWordWrap(True)
        outstanding.setStyleSheet(f"color: {dim_text_css(outstanding)};")
        card_layout.addWidget(outstanding)
        if capes["latent_skills"]:
            names = ", ".join(
                skill_id.replace("_", " ").title() for skill_id in capes["latent_skills"]
            )
            latent = QLabel(
                f"{names} sold a cape before the cutoff but has no training loop"
                " yet, so it has no cape row and no place in the all-skills gate."
            )
            latent.setObjectName("cabinetLatentSkills")
            latent.setWordWrap(True)
            latent.setStyleSheet(f"color: {dim_text_css(latent)};")
            card_layout.addWidget(latent)
        return card

    def _music_card(music: dict) -> "QWidget":
        """The whole log, with only its first rows on screen until asked.

        Every track is built, so no track can be permanently invisible; the rows
        past the first ``MUSIC_ROWS_SHOWN`` are simply hidden until the toggle
        is pressed, which keeps the card short enough that the diary families
        below it stay reachable in a 560-point dialog.
        """

        heading = f"Music Log · {music['unlocked']}/{music['total']} tracks"
        if music["latent"]:
            heading += f" · {music['latent']} latent"
        card, card_layout = _card(heading)

        overflow: list = []
        for index, track in enumerate(music["tracks"]):
            latent = " (latent — its feature has not shipped)" if track["latent"] else ""
            line = QLabel(
                f"{'♪' if track['unlocked'] else '·'} {track['name']}"
                f" — {track['hint']}{latent}"
            )
            line.setObjectName(f"cabinetTrack_{track['track_id']}")
            line.setWordWrap(True)
            line.setStyleSheet(
                "color: palette(text);" if track["unlocked"] else f"color: {dim_text_css(line)};"
            )
            card_layout.addWidget(line)
            if index >= MUSIC_ROWS_SHOWN:
                line.setVisible(False)
                overflow.append(line)

        if overflow:
            toggle = QToolButton()
            toggle.setObjectName("cabinetMusicShowAll")
            toggle.setCheckable(True)
            toggle.setText(f"Show all {len(music['tracks'])} tracks")
            toggle.setStyleSheet(f"border: none; color: {dim_text_css(toggle)};")

            def _toggle(checked: bool, rows=overflow, button=toggle) -> None:
                for row in rows:
                    row.setVisible(checked)
                button.setText(
                    "Show fewer tracks" if checked else f"Show all {len(rows) + MUSIC_ROWS_SHOWN} tracks"
                )

            toggle.toggled.connect(_toggle)
            card_layout.addWidget(toggle)
        return card

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

        if view["taskmaster_presentation"]["show"]:
            body_layout.addWidget(_taskmaster_card(view["taskmaster_presentation"]))
        body_layout.addWidget(_capes_card(view["capes"]))
        body_layout.addWidget(_music_card(view["music"]))

        shown = 0
        for family in view["families"]:
            card = QWidget()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(8)
            family_header = QHBoxLayout()
            family_header.setSpacing(8)
            taskmaster = family["taskmaster"]
            if taskmaster["show"]:
                portrait = QLabel()
                portrait.setObjectName(
                    f"cabinetTaskmasterPortrait_{family['family_id']}"
                )
                portrait.setFixedSize(48, 48)
                _set_slayer_master_chathead(
                    portrait, taskmaster["chathead_asset_path"]
                )
                family_header.addWidget(portrait)

            identity = QVBoxLayout()
            identity.setContentsMargins(0, 0, 0, 0)
            identity.setSpacing(1)
            name = QLabel(family["name"])
            name.setStyleSheet("font-weight: 700; color: palette(text);")
            identity.addWidget(name)
            if taskmaster["show"]:
                rewarder = QLabel(f"Reward handed over by {taskmaster['name']}")
                rewarder.setObjectName(
                    f"cabinetTaskmasterName_{family['family_id']}"
                )
                rewarder.setStyleSheet(f"color: {dim_text_css(rewarder)};")
                identity.addWidget(rewarder)
            family_header.addLayout(identity, 1)
            card_layout.addLayout(family_header)
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
