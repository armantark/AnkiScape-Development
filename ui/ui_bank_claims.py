"""Bank Claims: the Bank tab's inbox of rewards waiting to be claimed."""

from typing import Optional

try:
    from aqt.qt import (  # type: ignore
        QHBoxLayout,
        QIcon,
        QLabel,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        Qt,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from . import ui as _ui
from .ui import _clear_layout, dim_text_css
from ..core.skill_registry import get_skill
from ..logic_pure.logic_pure import _skill_level_for_reward, claim_rows_pure

# Every AnkiScape lamp is gone for good once destroyed, which is what the 2012
# Antique lamp's destroy prompt warned (Antique lamp oldid 6367339). The lamps
# 2012 let a player replace (Contact!, Carnillean, Dreamy) cannot be replaced
# here, so they take this warning rather than their own.
_DESTROY_LAMP_WARNING = "Are you sure you want to destroy the lamp? You won't be able to get another one."


def _skill_display(skill_id: str) -> str:
    skill = get_skill(skill_id)
    return skill.display_name if skill is not None else skill_id.replace("_", " ").title()


def _claim_skill_tooltip(row: dict) -> str:
    options = tuple(str(skill_id) for skill_id in row.get("skill_options", ()) or ())
    minimum_level = int(row.get("minimum_level", 1) or 1)
    if not options:
        return ""
    if row.get("fixed_skill_id"):
        label = f"Pays {_skill_display(str(row['fixed_skill_id']))}"
    elif len(options) > 8:
        label = "Choose: Any listed skill"
    else:
        label = "Choose: " + ", ".join(_skill_display(skill_id) for skill_id in options[:8])
    if minimum_level > 1:
        return f"{label}. Minimum level: {minimum_level}."
    return f"{label}."


def _xp_claim_metadata(row: dict) -> str:
    amount = float(row.get("xp_amount", 0) or 0)
    amount_text = f"{int(amount):,}" if amount.is_integer() else f"{amount:,.1f}"
    if str(row.get("claim_type")) == "xp_lamp":
        tooltip = _claim_skill_tooltip(row)
        return f"{amount_text} XP lamp" + (f" · {tooltip}" if tooltip else "")
    skill_options = tuple(row.get("skill_options", ()) or ())
    skill_name = _skill_display(str(skill_options[0])) if skill_options else "Skill"
    items = tuple(row.get("items", ()) or ())
    return f"{amount_text} {skill_name} XP · {len(items)} item rewards"


def _bundle_metadata(row: dict) -> str:
    items = tuple(row.get("items", ()) or ())
    preview = []
    for item in items[:3]:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            preview.append(f"{item[0]} x{item[1]}")
    if len(items) > len(preview):
        preview.append(f"+{len(items) - len(preview)} more")
    item_count = len(items)
    suffix = f" - {', '.join(preview)}" if preview else ""
    return f"{item_count} item stack{'s' if item_count != 1 else ''}{suffix}"


def _claim_metadata(row: dict) -> str:
    claim_type = str(row.get("claim_type", "item"))
    if claim_type in {"xp_lamp", "skill_reward"}:
        return _xp_claim_metadata(row)
    if claim_type == "item_bundle":
        return _bundle_metadata(row)
    return "Ready to claim"


def _claim_bundle_tooltip(row: dict) -> str:
    items = tuple(row.get("items", ()) or ())
    lines = []
    for item in items:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            lines.append(f"{item[0]} x{item[1]}")
    return "\n".join(lines)


def _claim_icon_name(row: dict) -> str:
    item_name = str(row.get("item_name", row.get("display_name", "")))
    if str(row.get("claim_type", "item")) in {"item_bundle", "skill_reward"}:
        items = tuple(row.get("items", ()) or ())
        first = items[0] if items else ()
        if isinstance(first, (tuple, list)) and first and isinstance(first[0], str):
            item_name = first[0]
    return item_name


def _claim_title(row: dict) -> str:
    item_name = str(row.get("item_name", row.get("display_name", "")))
    if str(row.get("claim_type", "item")) in {"xp_lamp", "item_bundle", "skill_reward"}:
        return str(row.get("display_name", item_name))
    return f"{row.get('display_name', item_name)} x{row.get('quantity', 1)}"


class _BankClaims:
    """The Bank Claims box and the commands its rows run.

    Only actionable rows render. A lamp with one allowed skill pays it on
    Claim; a choice lamp opens the shared icon-grid chooser even when one
    skill is eligible, so the player can still train another first. Every lamp
    can be destroyed after a confirmation, and both commands are undoable.
    """

    def __init__(self, player_data, item_icon_path, on_claim_reward, on_destroy_claim, refresh_views):
        self._player_data = player_data
        self._item_icon_path = item_icon_path
        self._on_claim_reward = on_claim_reward
        self._on_destroy_claim = on_destroy_claim
        self._refresh_views = refresh_views
        self.box = QWidget()
        self.box.setObjectName("bankClaimsBox")
        self.box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._layout = QVBoxLayout(self.box)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

    def _choose_skill(self, row: dict) -> Optional[str]:
        options = tuple(str(skill_id) for skill_id in row.get("skill_options", ()) or ())
        minimum_level = int(row.get("minimum_level", 1) or 1)
        eligible = [skill_id for skill_id in options if _skill_level_for_reward(self._player_data, skill_id) >= minimum_level]
        if not eligible:
            QMessageBox.warning(self.box, "No eligible skill", f"This lamp requires level {minimum_level} in an allowed skill.")
            return None
        return _ui._choose_xp_lamp_skill(
            self.box,
            str(row.get("display_name", "Claim XP lamp")),
            eligible,
        )

    def _after_command(self, changed: bool) -> None:
        if changed:
            self.populate()
            self._refresh_views()

    def _claim(self, row: dict) -> None:
        claim_id = row.get("claim_id")
        if self._on_claim_reward is None or not isinstance(claim_id, str):
            return
        selected_skill_id = None
        if str(row.get("claim_type", "item")) == "xp_lamp" and not row.get("fixed_skill_id"):
            selected_skill_id = self._choose_skill(row)
            if selected_skill_id is None:
                return
        self._after_command(self._on_claim_reward(claim_id, selected_skill_id))

    def _destroy(self, row: dict) -> None:
        claim_id = row.get("claim_id")
        if self._on_destroy_claim is None or not isinstance(claim_id, str):
            return
        answer = QMessageBox.question(
            self.box,
            "Destroy lamp?",
            f"{_claim_title(row)}\n\n{_DESTROY_LAMP_WARNING}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._after_command(self._on_destroy_claim(claim_id))

    def _row_copy(self, row: dict) -> QWidget:
        claim_type = str(row.get("claim_type", "item"))
        copy = QWidget()
        copy_layout = QVBoxLayout(copy)
        copy_layout.setContentsMargins(0, 0, 0, 0)
        copy_layout.setSpacing(1)
        label = QLabel(_claim_title(row))
        label.setObjectName("bankClaimTitle")
        label.setStyleSheet("color: palette(text); font-weight: 600;")
        metadata = QLabel(_claim_metadata(row))
        metadata.setObjectName("bankClaimMetadata")
        metadata.setStyleSheet(f"color: {dim_text_css(metadata)};")
        if claim_type in {"xp_lamp", "item_bundle", "skill_reward"}:
            tooltip = _claim_skill_tooltip(row) if claim_type == "xp_lamp" else _claim_bundle_tooltip(row)
            label.setToolTip(tooltip)
            metadata.setToolTip(tooltip)
        copy_layout.addWidget(label)
        copy_layout.addWidget(metadata)
        return copy

    def _row(self, row: dict) -> QWidget:
        claim_row = QWidget()
        claim_row.setObjectName("bankClaimRow")
        crl = QHBoxLayout(claim_row)
        crl.setContentsMargins(6, 4, 6, 4)
        crl.setSpacing(8)
        icon_label = QLabel()
        icon_label.setObjectName("bankClaimIcon")
        icon_label.setFixedSize(28, 28)
        icon_label.setStyleSheet("background: rgba(255, 255, 255, 0.08); border: 1px solid palette(mid); border-radius: 4px;")
        icon_path = self._item_icon_path(_claim_icon_name(row))
        if icon_path:
            icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
            icon_label.setStyleSheet("")
        crl.addWidget(icon_label)
        crl.addWidget(self._row_copy(row))
        crl.addStretch(1)
        if row.get("destroyable"):
            destroy_btn = QPushButton("Destroy")
            destroy_btn.setObjectName("bankClaimDestroy")
            destroy_btn.setToolTip("Destroy this lamp for good.")
            destroy_btn.clicked.connect(lambda _checked=False: self._destroy(row))
            crl.addWidget(destroy_btn)
        claim_btn = QPushButton("Choose skill")
        claim_btn.setObjectName("bankClaimAction")
        # Sized for the longer label so the Destroy buttons line up in one column.
        claim_btn.setMinimumWidth(claim_btn.sizeHint().width())
        if str(row.get("claim_type", "item")) == "xp_lamp":
            claim_btn.setToolTip(_claim_skill_tooltip(row))
            if row.get("fixed_skill_id"):
                claim_btn.setText("Claim")
        else:
            claim_btn.setText("Claim")
        claim_btn.clicked.connect(lambda _checked=False: self._claim(row))
        crl.addWidget(claim_btn)
        return claim_row

    def populate(self) -> None:
        _clear_layout(self._layout)
        rows = claim_rows_pure(self._player_data, _ui.CLAIM_DATA)
        actionable = [row for row in rows if row.get("eligible")]
        if not rows:
            self.box.setVisible(False)
            return
        self.box.setVisible(True)
        header = QLabel("Bank Claims")
        header.setObjectName("bankClaimsHeader")
        header.setStyleSheet("font-weight: 600; color: palette(text);")
        self._layout.addWidget(header)
        max_claim_height = header.sizeHint().height()

        # Locked claims render nothing at all: a reward the player cannot claim
        # is not actionable, so a locked-only save is "caught up" here.
        if not actionable:
            empty = QLabel("All Bank Claims caught up.")
            empty.setObjectName("bankClaimsCaughtUp")
            empty.setStyleSheet(f"color: {dim_text_css(empty)};")
            self._layout.addWidget(empty)
            self.box.setMaximumHeight(max_claim_height + self._layout.spacing() + empty.sizeHint().height() + 4)
            return

        rows_host = QWidget()
        rows_host.setObjectName("bankClaimsRows")
        rows_layout = QVBoxLayout(rows_host)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(4)
        for row in actionable:
            rows_layout.addWidget(self._row(row))

        scroll = QScrollArea()
        scroll.setObjectName("bankClaimsScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea#bankClaimsScrollArea { border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(rows_host)
        row_height = max(rows_host.sizeHint().height() // len(actionable), 42)
        scroll_height = (row_height * 3) + 10
        scroll.setMaximumHeight(scroll_height)
        self._layout.addWidget(scroll)
        max_claim_height += self._layout.spacing() + scroll_height
        self.box.setMaximumHeight(max_claim_height + 4)


def build_bank_claims_box(player_data, item_icon_path, on_claim_reward, on_destroy_claim, refresh_views):
    """Return the Bank Claims box and the callback that repopulates it."""
    claims = _BankClaims(player_data, item_icon_path, on_claim_reward, on_destroy_claim, refresh_views)
    return claims.box, claims.populate
