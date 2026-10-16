"""ui_tab_quests.py - the main menu's Quests tab.

Built on first show by ``show_main_menu``: a card per quest in the catalog is
the single largest widget population in the menu. See ui_menu_ctx.MainMenuCtx
for the contract.
"""
from itertools import groupby

try:
    from aqt.qt import (  # type: ignore
        Qt,
        QCheckBox,
        QComboBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..core.constants import QUEST_DATA
from ..core.search_match import match_rank
from ..logic_pure.logic_pure import (
    apply_quest_route_choice_pure,
    can_attempt_quest_review_pure,
    quest_availability_state_pure,
    quest_catalog_sections_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_choices_pure,
    quest_journal_rows_pure,
    quest_locked_reasons_pure,
    quest_state_pure,
)
from .ui import CatalogFilterBar, dim_text_css


def _quest_match_rank(query: str, item: tuple[str, dict]) -> int | None:
    quest_id, quest = item
    return match_rank(
        query, quest.get("display_name", quest_id), quest_id,
        quest.get("start_point", ""),
        quest.get("requirements", ()),
        quest.get("unlocks", ()),
    )


def _quest_search_sections(rows, query: str):
    tiers = groupby(rows, key=lambda item: _quest_match_rank(query, item))
    return tuple(section for _tier, matches in tiers
                 for section in quest_catalog_sections_pure(tuple(matches)))


def build_quests_tab(ctx) -> "QWidget":
    """Return the Quests page."""
    player_data = ctx.player_data
    state = ctx.selection
    warn = ctx.warn_label
    on_save_skill = ctx.on_save_skill
    on_set_quest = ctx.on_set_quest
    on_set_quest_route_choice = ctx.on_set_quest_route_choice

    # ---- Quests tab --------------------------------------------------------
    quests_tab = QWidget()
    q_layout = QVBoxLayout(quests_tab)
    q_layout.setContentsMargins(12, 12, 12, 12)
    q_layout.setSpacing(8)

    quest_top = QWidget()
    quest_top_layout = QHBoxLayout(quest_top)
    quest_top_layout.setContentsMargins(0, 0, 0, 0)
    quest_points_label = QLabel(f"Quest points: {int(player_data.get('quest_points', 0) or 0)}")
    quest_points_label.setStyleSheet("font-weight: 600; color: palette(text);")
    sort_label = QLabel("Sort")
    sort_label.setStyleSheet(f"color: {dim_text_css(sort_label)};")
    quest_sort_combo = QComboBox()
    quest_sort_combo.setObjectName("questSortCombo")
    quest_sort_modes = (
        "Release Order",
        "Progress",
        "Difficulty",
        "Free/Members",
        "Timeline",
        "Length",
    )
    quest_sort_combo.addItems(list(quest_sort_modes))
    quest_top_layout.addWidget(quest_points_label)
    quest_top_layout.addStretch(1)
    quest_top_layout.addWidget(sort_label)
    quest_top_layout.addWidget(quest_sort_combo)
    q_layout.addWidget(quest_top)

    difficulty_order = {"Novice": 0, "Intermediate": 1, "Experienced": 2, "Master": 3, "Grandmaster": 4, "Special": 5}
    length_order = {
        "Short": 0,
        "Short to Medium": 1,
        "Medium": 2,
        "Medium to Long": 3,
        "Long": 4,
        "Long to Very Long": 5,
        "Very Long": 6,
        "Very, Very Long": 7,
    }
    timeline_order = {"Fifth Age": 0, "Ambiguous": 1, "Sixth Age": 2}

    quest_filter_bar = CatalogFilterBar(
        placeholder="Search quests",
        search_object_name="questSearchInput",
    )
    quest_search = quest_filter_bar.search_input

    hide_completed_cb = QCheckBox("Hide completed")
    hide_completed_cb.setObjectName("questHideCompletedCheck")
    hide_locked_cb = QCheckBox("Hide unable to start")
    hide_locked_cb.setObjectName("questHideLockedCheck")

    access_filter_combo = QComboBox()
    access_filter_combo.setObjectName("questAccessFilterCombo")
    access_filter_combo.addItems(("All access", "Free quests", "Members quests"))

    difficulty_filter_combo = QComboBox()
    difficulty_filter_combo.setObjectName("questDifficultyFilterCombo")
    difficulty_filter_combo.addItems(("All difficulties", *difficulty_order.keys()))

    length_filter_combo = QComboBox()
    length_filter_combo.setObjectName("questLengthFilterCombo")
    length_filter_combo.addItems(("All lengths", *length_order.keys()))

    timeline_filter_combo = QComboBox()
    timeline_filter_combo.setObjectName("questTimelineFilterCombo")
    timeline_filter_combo.addItems(("All timelines", *timeline_order.keys()))

    quest_filter_bar.summary_label.setObjectName("questFilterSummaryLabel")
    quest_filter_bar.add_filter(hide_completed_cb)
    quest_filter_bar.add_filter(hide_locked_cb)
    for label_text, combo in (
        ("Access", access_filter_combo),
        ("Difficulty", difficulty_filter_combo),
        ("Length", length_filter_combo),
        ("Timeline", timeline_filter_combo),
    ):
        quest_filter_bar.add_filter(combo, label_text)
    q_layout.addWidget(quest_filter_bar)

    quest_scroll = QScrollArea()
    quest_scroll.setWidgetResizable(True)
    quest_scroll.setStyleSheet("border: none;")
    quest_content = QWidget()
    quest_content_layout = QVBoxLayout(quest_content)
    quest_content_layout.setContentsMargins(0, 0, 0, 0)
    quest_content_layout.setSpacing(10)

    def _short_stage_blocker_text(reasons: tuple) -> str:
        if not reasons:
            return ""
        shown = [str(reason) for reason in reasons[:3]]
        extra = len(reasons) - len(shown)
        if extra > 0:
            shown.append(f"+{extra} more")
        return "Blocked: " + ", ".join(shown)

    def _quest_choice_button_name(quest_id: str, route_id: str) -> str:
        safe_route = "".join(ch if ch.isalnum() else "_" for ch in str(route_id).lower()).strip("_")
        return f"questChoice_{quest_id}_{safe_route}"

    def _short_choice_text(choice_rows: tuple) -> str:
        if not choice_rows:
            return ""
        labels = tuple(
            str(option.get("label") or option.get("route_id") or "")
            for option in tuple(choice_rows[0].get("options", ()) or ())
            if option
        )
        if not labels:
            return "Choose path"
        return "Choose path: " + " or ".join(labels)

    def _quest_status_text(quest_id: str, state: dict, quest: dict) -> str:
        if state.get("completed"):
            return "Completed"
        if state.get("started"):
            blocker_text = _short_stage_blocker_text(
                quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
            )
            if blocker_text:
                return blocker_text
            return f"Stage {int(state.get('progress', 0) or 0)}/{int(quest.get('stages', 1) or 1)}"
        return "Not started"

    def _quest_button_text(state: dict) -> str:
        if state.get("completed"):
            return "Completed"
        if state["started"] and state["progress"] > 0:
            return "Continue quest"
        return "Start quest"

    expanded_quests = {}

    def _quest_progress_rank(q_state: dict) -> int:
        if q_state.get("started") and not q_state.get("completed"):
            return 0
        if not q_state.get("completed"):
            return 1
        return 2

    def _quest_sort_key(item: tuple[str, dict], mode: str) -> tuple:
        quest_id, quest = item
        q_state = quest_state_pure(player_data, quest_id)
        release_key = str(quest.get("release_date", "9999-99-99"))
        release_order = int(quest.get("release_order", 9999) or 9999)
        name = str(quest.get("display_name", quest_id))
        if mode == "Progress":
            return (_quest_progress_rank(q_state), release_order, release_key, name)
        if mode == "Difficulty":
            return (difficulty_order.get(str(quest.get("difficulty", "")), 99), release_order, release_key, name)
        if mode == "Free/Members":
            return (1 if quest.get("members") else 0, release_order, release_key, name)
        if mode == "Timeline":
            return (timeline_order.get(str(quest.get("timeline", "")), 99), release_order, release_key, name)
        if mode == "Length":
            return (length_order.get(str(quest.get("length", "")), 99), release_order, release_key, name)
        return (release_order, release_key, name)

    def _short_lock_text(reasons: tuple) -> str:
        if not reasons:
            return ""
        shown = [str(reason) for reason in reasons[:5]]
        extra = len(reasons) - len(shown)
        if extra > 0:
            shown.append(f"+{extra} more")
        return "Requires: " + ", ".join(shown)

    def _quest_matches_filters(quest_id: str, quest: dict) -> bool:
        if _quest_match_rank(quest_filter_bar.query(), (quest_id, quest)) is None:
            return False
        availability = quest_availability_state_pure(player_data, quest_id, QUEST_DATA)
        if hide_completed_cb.isChecked() and availability == "completed":
            return False
        if hide_locked_cb.isChecked() and availability == "locked":
            return False

        access_filter = access_filter_combo.currentText()
        if access_filter == "Free quests" and quest.get("members"):
            return False
        if access_filter == "Members quests" and not quest.get("members"):
            return False

        difficulty_filter = difficulty_filter_combo.currentText()
        if difficulty_filter != "All difficulties" and str(quest.get("difficulty", "")) != difficulty_filter:
            return False

        length_filter = length_filter_combo.currentText()
        if length_filter != "All lengths" and str(quest.get("length", "")) != length_filter:
            return False

        timeline_filter = timeline_filter_combo.currentText()
        if timeline_filter != "All timelines" and str(quest.get("timeline", "")) != timeline_filter:
            return False
        return True

    def _clear_quest_cards() -> None:
        while quest_content_layout.count():
            item = quest_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _set_quest_route_choice(quest_id: str, route_id: str) -> None:
        if on_set_quest_route_choice is not None:
            if on_set_quest_route_choice(quest_id, route_id) is False:
                return
        else:
            new_data, ok = apply_quest_route_choice_pure(player_data, quest_id, QUEST_DATA, route_id)
            if not ok:
                return
            player_data.update(new_data)
        warn.setText("")
        _rebuild_quest_cards()

    def _set_quest_active(quest_id: str, button: QPushButton, status_label: QLabel) -> None:
        if quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA):
            return
        choice_text = _short_choice_text(quest_current_stage_choices_pure(player_data, quest_id, QUEST_DATA))
        if choice_text:
            warn.setText(choice_text)
            return
        if quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA) and not can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA):
            return
        if on_set_quest is not None and on_set_quest(quest_id) is False:
            return
        state["active"] = "Quests"
        on_save_skill("Quests")
        ctx.refresh("active_label")
        q_state = quest_state_pure(player_data, quest_id)
        quest = QUEST_DATA.get(quest_id, {})
        button.setText("Currently active")
        button.setEnabled(False)
        status_label.setText(_quest_status_text(quest_id, q_state, quest))

    def _add_quest_card(quest_id: str, quest: dict) -> None:
        q_state = quest_state_pure(player_data, quest_id)
        lock_reasons = () if q_state.get("completed") else quest_locked_reasons_pure(player_data, quest_id, QUEST_DATA)
        lock_text = _short_lock_text(lock_reasons)
        stage_blocker_reasons = () if q_state.get("completed") else quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        stage_blocker_text = _short_stage_blocker_text(stage_blocker_reasons)
        choice_rows = () if q_state.get("completed") else quest_current_stage_choices_pure(player_data, quest_id, QUEST_DATA)
        choice_text = _short_choice_text(choice_rows)
        active_this_quest = state["active"] == "Quests" and player_data.get("current_quest") == quest_id
        default_expanded = bool(choice_rows or (q_state.get("started") and not q_state.get("completed") and active_this_quest))
        expanded = expanded_quests.get(quest_id, default_expanded)

        card = QWidget()
        card.setObjectName(f"questCard_{quest_id}")
        card.setStyleSheet("border: 1px solid palette(mid); border-radius: 6px; background: palette(base);")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(6)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        toggle_btn = QPushButton("v" if expanded else ">")
        toggle_btn.setObjectName(f"questToggle_{quest_id}")
        toggle_btn.setFixedWidth(28)
        toggle_btn.setToolTip("Show or hide quest journal")
        title = QLabel(str(quest.get("display_name", quest_id)))
        title.setStyleSheet("font-weight: 700; color: palette(text);")
        title.setToolTip(stage_blocker_text or lock_text or str(quest.get("source", "")))
        status = QLabel(_quest_status_text(quest_id, q_state, quest))
        status.setObjectName(f"questStatus_{quest_id}")
        # A long blocker list wraps instead of widening the card past the tab.
        status.setWordWrap(True)
        status.setStyleSheet(f"color: {dim_text_css(status)};")
        quest_btn = QPushButton(_quest_button_text(q_state))
        quest_btn.setObjectName(f"questAction_{quest_id}")
        quest_review_ready = can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA)
        quest_btn.setEnabled(
            not q_state.get("completed")
            and state["active"] != "Quests"
            and not lock_reasons
            and not choice_rows
            and (not stage_blocker_reasons or quest_review_ready)
        )
        if lock_text:
            quest_btn.setToolTip(lock_text)
            header.setToolTip(lock_text)
        if stage_blocker_text:
            quest_btn.setToolTip(stage_blocker_text)
            header.setToolTip(stage_blocker_text)
        if active_this_quest:
            quest_btn.setText("Currently active")
            quest_btn.setEnabled(False)
        quest_btn.clicked.connect(lambda _=False, qid=quest_id, btn=quest_btn, lbl=status: _set_quest_active(qid, btn, lbl))
        header_layout.addWidget(toggle_btn)
        header_layout.addWidget(title)
        header_layout.addWidget(status, 1)
        header_layout.addWidget(quest_btn)
        card_layout.addWidget(header)

        body = QWidget()
        body.setObjectName(f"questBody_{quest_id}")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 4, 0, 0)
        body_layout.setSpacing(5)

        # Journal bodies are the bulk of this tab and start collapsed for all
        # but the active quest, so fill one only when it is actually shown.
        body_filled = {"done": False}

        def _fill_quest_body() -> None:
            if body_filled["done"]:
                return
            body_filled["done"] = True
            if not q_state.get("started"):
                start = QLabel(str(quest.get("start_point", "")))
                start.setWordWrap(True)
                start.setStyleSheet("color: palette(text);")
                body_layout.addWidget(start)
            requirements = tuple(quest.get("requirements", ()) or ())
            if requirements:
                req_label = QLabel("Requires: " + ", ".join(str(req) for req in requirements))
                req_label.setWordWrap(True)
                req_label.setStyleSheet(f"color: {dim_text_css(req_label)};")
                body_layout.addWidget(req_label)
            unlocks = tuple(quest.get("unlocks", ()) or ())
            if unlocks:
                unlock_label = QLabel("Unlocks: " + ", ".join(str(unlock) for unlock in unlocks))
                unlock_label.setWordWrap(True)
                unlock_label.setStyleSheet(f"color: {dim_text_css(unlock_label)};")
                body_layout.addWidget(unlock_label)
            for choice in choice_rows:
                prompt_label = QLabel(str(choice.get("prompt") or "Choose path"))
                prompt_label.setWordWrap(True)
                prompt_label.setStyleSheet("font-weight: 600; color: palette(text);")
                body_layout.addWidget(prompt_label)
                choice_row = QWidget()
                choice_row_layout = QHBoxLayout(choice_row)
                choice_row_layout.setContentsMargins(0, 0, 0, 0)
                choice_row_layout.setSpacing(6)
                for option in tuple(choice.get("options", ()) or ()):
                    route_id = str(option.get("route_id") or "")
                    label = str(option.get("label") or route_id or "Choose")
                    choice_btn = QPushButton(label)
                    choice_btn.setObjectName(_quest_choice_button_name(quest_id, route_id))
                    choice_btn.setToolTip(str(option.get("description") or label))
                    choice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    choice_btn.setStyleSheet(
                        "QPushButton { padding: 4px 10px; border: 1px solid palette(mid);"
                        " border-radius: 6px; color: palette(text); background: palette(base); }"
                        " QPushButton:hover { border-color: #4CAF50; }"
                    )
                    choice_btn.clicked.connect(
                        lambda _=False, qid=quest_id, rid=route_id: _set_quest_route_choice(qid, rid)
                    )
                    choice_row_layout.addWidget(choice_btn)
                choice_row_layout.addStretch(1)
                body_layout.addWidget(choice_row)
            for row in quest_journal_rows_pure(player_data, quest_id, QUEST_DATA):
                stage_label = QLabel(f"Stage {row['stage']}")
                stage_label.setStyleSheet("font-weight: 600; color: palette(text);")
                body_layout.addWidget(stage_label)
                for line in row.get("lines", ()):
                    text = str(line)
                    if row.get("completed"):
                        text = f"<s>{text}</s>"
                    line_label = QLabel(text)
                    line_label.setWordWrap(True)
                    line_label.setTextFormat(Qt.TextFormat.RichText)
                    line_label.setStyleSheet("color: palette(text);")
                    body_layout.addWidget(line_label)

        if expanded:
            _fill_quest_body()
        body.setVisible(expanded)
        card_layout.addWidget(body)

        def _toggle_quest() -> None:
            new_expanded = not body.isVisible()
            expanded_quests[quest_id] = new_expanded
            if new_expanded:
                _fill_quest_body()
            body.setVisible(new_expanded)
            toggle_btn.setText("v" if new_expanded else ">")

        toggle_btn.clicked.connect(_toggle_quest)
        quest_content_layout.addWidget(card)

    def _add_section_heading(title: str) -> None:
        heading = QLabel(title)
        heading.setObjectName(f"questSection_{title}")
        heading.setStyleSheet("font-weight: 700; color: palette(text); margin-top: 6px;")
        quest_content_layout.addWidget(heading)

    def _rebuild_quest_cards() -> None:
        _clear_quest_cards()
        mode = quest_sort_combo.currentText() or "Release Order"
        query = quest_filter_bar.query()
        visible_rows = sorted(
            (item for item in QUEST_DATA.items() if _quest_matches_filters(*item)),
            key=lambda item: (_quest_match_rank(query, item), _quest_sort_key(item, mode)),
        )
        visible_count = len(visible_rows)
        for section in _quest_search_sections(visible_rows, query):
            if section["title"]:
                _add_section_heading(section["title"])
            for quest_id, quest in section["rows"]:
                _add_quest_card(quest_id, quest)
        if visible_count == 0:
            empty_label = QLabel("No quests match the current filters.")
            empty_label.setObjectName("questEmptyFilterLabel")
            empty_label.setWordWrap(True)
            empty_label.setStyleSheet(f"color: {dim_text_css(empty_label)};")
            quest_content_layout.addWidget(empty_label)
        quest_filter_bar.set_count(visible_count, len(QUEST_DATA))
        quest_content_layout.addStretch(1)

    quest_sort_combo.currentTextChanged.connect(lambda _text: _rebuild_quest_cards())
    quest_search.textChanged.connect(lambda _text: _rebuild_quest_cards())
    hide_completed_cb.toggled.connect(lambda _checked: _rebuild_quest_cards())
    hide_locked_cb.toggled.connect(lambda _checked: _rebuild_quest_cards())
    for combo in (access_filter_combo, difficulty_filter_combo, length_filter_combo, timeline_filter_combo):
        combo.currentTextChanged.connect(lambda _text: _rebuild_quest_cards())
    _rebuild_quest_cards()
    quest_scroll.setWidget(quest_content)
    q_layout.addWidget(quest_scroll, 1)

    ctx.refreshers["quests"] = _rebuild_quest_cards
    return quests_tab
