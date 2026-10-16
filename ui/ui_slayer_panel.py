"""ui_slayer_panel.py - the Slayer management page: Assignment, Masters, Rewards.

The panel is thin: which masters show, which are locked and why, which can
assign now, and which master `Get assignment` asks all come from
``slayer_masters_view_pure``.
"""

try:
    from aqt.qt import (  # type: ignore
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        Qt,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass

from ..data.slayer_data import DEFAULT_SLAYER_MASTER_ID, SLAYER_FAMILIES_BY_ID
from ..logic.slayer_logic import (
    sanitize_slayer_state_pure,
    slayer_master_persona_pure,
    slayer_masters_view_pure,
)
from .ui import _set_slayer_master_chathead, dim_text_css


def build_slayer_panel(
    player_data, *, run_command, commands_enabled, on_assigned, open_in_combat
) -> "QWidget":
    """Return the Slayer page. ``run_command(action_id, payload)`` reports its
    own refusal; ``on_assigned`` rerenders the page after a new task."""
    data = sanitize_slayer_state_pure(player_data)
    view = slayer_masters_view_pure(data)

    def _get_assignment(master_id: str) -> None:
        result = run_command("get_assignment", {"master_id": master_id})
        if result.get("ok", False):
            on_assigned()

    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    slayer_tabs = QTabWidget()
    slayer_tabs.setObjectName("slayerManagementTabs")
    slayer_tabs.setDocumentMode(True)
    slayer_tabs.addTab(
        _assignment_tab(data, view, commands_enabled, _get_assignment, open_in_combat),
        "Assignment",
    )
    slayer_tabs.addTab(_masters_tab(view, commands_enabled, _get_assignment), "Masters")
    slayer_tabs.addTab(_rewards_tab(data), "Rewards")
    layout.addWidget(slayer_tabs, 1)
    return container


def _assignment_tab(data, view, commands_enabled, get_assignment, open_in_combat) -> "QWidget":
    assignment = data.get("slayer_assignment") or {}
    family = SLAYER_FAMILIES_BY_ID.get(str(assignment.get("family_id", "") or ""))
    remaining = int(assignment.get("remaining", 0) or 0)

    assignment_tab = QWidget()
    assignment_layout = QVBoxLayout(assignment_tab)
    assignment_layout.setContentsMargins(10, 10, 10, 10)
    assignment_layout.setSpacing(10)
    if family is not None and remaining > 0:
        card = QWidget()
        card.setObjectName("slayerActiveAssignmentCard")
        card.setStyleSheet(
            "QWidget#slayerActiveAssignmentCard {"
            " border: 1px solid #4CAF50; border-radius: 9px;"
            " background: rgba(76,175,80,0.10); }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        speaker_row = QHBoxLayout()
        speaker_row.setContentsMargins(0, 0, 0, 0)
        speaker_row.setSpacing(10)
        master_name, chathead_asset_path = slayer_master_persona_pure(
            data, str(assignment.get("master_id", DEFAULT_SLAYER_MASTER_ID))
        )
        assignment_chathead = QLabel()
        assignment_chathead.setObjectName("slayerAssignmentChathead")
        _set_slayer_master_chathead(assignment_chathead, chathead_asset_path)
        speaker_row.addWidget(assignment_chathead, 0, Qt.AlignmentFlag.AlignTop)
        title = QLabel(family.display_name)
        title.setStyleSheet("color: palette(text); font-size: 14px; font-weight: 700;")
        speaker_row.addWidget(title, 1, Qt.AlignmentFlag.AlignVCenter)
        card_layout.addLayout(speaker_row)
        progress = QLabel(
            f"{remaining} of {int(assignment.get('initial_count', remaining) or remaining)} remaining"
            f" · assigned by {master_name}"
        )
        progress.setObjectName("slayerAssignmentProgress")
        progress.setStyleSheet(f"color: {dim_text_css(progress)};")
        card_layout.addWidget(progress)
        assignment_layout.addWidget(card)

        open_combat = QPushButton("Open in Combat")
        open_combat.setObjectName("slayerOpenCombatButton")
        open_combat.setToolTip(
            "Open Combat with Current Slayer task only enabled. No encounter starts."
        )
        open_combat.clicked.connect(lambda _=False: open_in_combat())
        assignment_layout.addWidget(open_combat)
    else:
        selected = view["selected"]
        master_name = selected["display_name"]
        if selected["id"] != DEFAULT_SLAYER_MASTER_ID:
            request = "a new task"
        elif master_name == "Turael":
            request = "a beginner task; after While Guthix Sleeps, Spria fills this role"
        else:
            request = "a beginner task"
        empty = QLabel(f"You do not have an active assignment.\nAsk {master_name} for {request}.")
        empty.setObjectName("slayerAssignmentEmptyState")
        empty.setWordWrap(True)
        empty.setStyleSheet(f"color: {dim_text_css(empty)};")
        assignment_layout.addWidget(empty)
        get_assignment_button = QPushButton("Get assignment")
        get_assignment_button.setObjectName("slayerGetAssignmentButton")
        get_assignment_button.setEnabled(commands_enabled)
        get_assignment_button.clicked.connect(
            lambda _=False, master_id=selected["id"]: get_assignment(master_id)
        )
        assignment_layout.addWidget(get_assignment_button)
    completed = QLabel(
        f"Assignments completed: {int(data.get('slayer_tasks_completed', 0) or 0)}"
    )
    completed.setObjectName("slayerCompletedCount")
    completed.setStyleSheet(f"color: {dim_text_css(completed)};")
    assignment_layout.addWidget(completed)
    assignment_layout.addStretch(1)
    return assignment_tab


def _masters_tab(view, commands_enabled, get_assignment) -> "QWidget":
    scroll = QScrollArea()
    scroll.setObjectName("slayerMastersScroll")
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sheet = QWidget()
    sheet.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    masters_layout = QVBoxLayout(sheet)
    masters_layout.setContentsMargins(10, 10, 10, 10)
    masters_layout.setSpacing(8)
    for row in view["masters"]:
        masters_layout.addWidget(
            _master_card(row, view["assignment_active"], commands_enabled, get_assignment)
        )
    masters_layout.addStretch(1)
    scroll.setWidget(sheet)
    return scroll


def _master_card(row, assignment_active, commands_enabled, get_assignment) -> "QWidget":
    card = QWidget()
    card.setObjectName(f"slayerMaster_{row['id']}")
    card.setStyleSheet(
        f"QWidget#slayerMaster_{row['id']} {{"
        " border: 1px solid palette(mid); border-radius: 9px;"
        " background: palette(base); }"
    )
    card_layout = QHBoxLayout(card)
    card_layout.setContentsMargins(12, 10, 12, 10)
    card_layout.setSpacing(10)
    chathead = QLabel()
    chathead.setObjectName("slayerMasterChathead")
    _set_slayer_master_chathead(chathead, row["chathead_asset_path"])
    card_layout.addWidget(chathead, 0, Qt.AlignmentFlag.AlignTop)

    copy = QVBoxLayout()
    copy.setSpacing(4)
    locked_reasons = row["locked_reasons"]
    title = QLabel(row["display_name"])
    title.setObjectName("slayerMasterName")
    title_color = dim_text_css(title) if locked_reasons else "palette(text)"
    title.setStyleSheet(f"color: {title_color}; font-weight: 700;")
    copy.addWidget(title)
    note = QLabel(f"{row['family_count']} possible assignments")
    note.setWordWrap(True)
    note.setStyleSheet(f"color: {dim_text_css(note)};")
    copy.addWidget(note)
    if locked_reasons:
        requirements = QLabel("Requires: " + " · ".join(locked_reasons))
        requirements.setObjectName("slayerMasterLockedReasons")
        requirements.setWordWrap(True)
        requirements.setStyleSheet("color: palette(text);")
        copy.addWidget(requirements)
    button = QPushButton("Active task" if assignment_active else "Get assignment")
    button.setObjectName("slayerMasterAssignmentButton")
    button.setEnabled(commands_enabled and row["enabled"])
    button.clicked.connect(lambda _=False, master_id=row["id"]: get_assignment(master_id))
    copy.addWidget(button, 0, Qt.AlignmentFlag.AlignLeft)
    card_layout.addLayout(copy, 1)
    return card


def _rewards_tab(data) -> "QWidget":
    rewards_tab = QWidget()
    rewards_layout = QVBoxLayout(rewards_tab)
    rewards_layout.setContentsMargins(10, 10, 10, 10)
    rewards_layout.setSpacing(8)
    smoking_complete = bool(
        ((data.get("quests", {}) or {}).get("smoking_kills", {}) or {}).get("completed")
    )
    if not smoking_complete:
        lock = QLabel(
            "Complete Smoking Kills to activate Slayer points, streak rewards, "
            "assignment skips and blocks, and the reward shop."
        )
        lock.setObjectName("slayerRewardsSmokingKillsLock")
        lock.setWordWrap(True)
        lock.setStyleSheet(
            "color: palette(text); border: 1px solid rgba(255,183,77,0.55);"
            " border-radius: 8px; background: rgba(255,183,77,0.08);"
            " padding: 10px;"
        )
        rewards_layout.addWidget(lock)
    else:
        points = QLabel(f"Slayer points: {int(data.get('slayer_points', 0) or 0)}")
        points.setObjectName("slayerPointsBalance")
        points.setStyleSheet("color: palette(text); font-weight: 700;")
        rewards_layout.addWidget(points)
        availability = QLabel("Reward purchases will appear here as they become available.")
        availability.setWordWrap(True)
        availability.setStyleSheet(f"color: {dim_text_css(availability)};")
        rewards_layout.addWidget(availability)
    rewards_layout.addStretch(1)
    return rewards_tab
