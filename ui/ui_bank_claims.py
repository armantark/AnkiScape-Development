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
from ..logic_pure.logic_pure import claim_rows_pure

# Every AnkiScape lamp is gone for good once destroyed, which is what the 2012
# Antique lamp's destroy prompt warned (Antique lamp oldid 6367339). The lamps
# 2012 let a player replace (Contact!, Carnillean, Dreamy) cannot be replaced
# here, so they take this warning rather than their own.
_DESTROY_LAMP_WARNING = "Are you sure you want to destroy the lamp? You won't be able to get another one."


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
        eligible = row["eligible_skill_ids"]
        minimum_level = row["minimum_level"]
        if not eligible:
            QMessageBox.warning(self.box, "No eligible skill", f"This lamp requires level {minimum_level} in an allowed skill.")
            return None
        return _ui._choose_xp_lamp_skill(
            self.box,
            row["title"],
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
        if row["choose_skill"]:
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
            f"{row['title']}\n\n{_DESTROY_LAMP_WARNING}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._after_command(self._on_destroy_claim(claim_id))

    def _row_copy(self, row: dict) -> QWidget:
        copy = QWidget()
        copy_layout = QVBoxLayout(copy)
        copy_layout.setContentsMargins(0, 0, 0, 0)
        copy_layout.setSpacing(1)
        label = QLabel(row["title"])
        label.setObjectName("bankClaimTitle")
        label.setStyleSheet("color: palette(text); font-weight: 600;")
        metadata = QLabel(row["metadata"])
        metadata.setObjectName("bankClaimMetadata")
        metadata.setStyleSheet(f"color: {dim_text_css(metadata)};")
        label.setToolTip(row["tooltip"])
        metadata.setToolTip(row["tooltip"])
        label.setWordWrap(True)
        metadata.setWordWrap(True)
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
        icon_path = self._item_icon_path(row["icon_name"])
        if icon_path:
            icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
            icon_label.setStyleSheet("")
        crl.addWidget(icon_label)
        crl.addWidget(self._row_copy(row), 1)
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
        claim_btn.setText(row["action_label"])
        claim_btn.setToolTip(row["tooltip"])
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
