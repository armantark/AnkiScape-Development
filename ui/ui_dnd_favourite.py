"""The Activities surface's routes to the reviewer badge's watched Distractions.

The tree row's right-click menu is the primary route; the star on the open
detail card is the secondary one. Both toggle through the add-on's
``on_favourite_dnd`` and draw what ``dnd_favourites_logic`` decides.
"""

from ..logic.dnd_favourites_logic import (
    dnd_favourite_context_menu_view_pure,
    dnd_favourite_detail_button_view_pure,
)

try:
    from aqt.qt import QMenu, Qt, QToolButton  # type: ignore
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    pass


class DndFavouriteControls:
    """The detail card's star and the tree's right-click menu for one Activities surface."""

    def __init__(self, player_data: dict, tree, on_favourite_dnd, open_card_id, show_error_message):
        self._player_data = player_data
        self._tree = tree
        self._on_favourite_dnd = on_favourite_dnd
        self._open_card_id = open_card_id
        self._show_error_message = show_error_message
        self.button = QToolButton()
        self.button.setObjectName("activityFavouriteButton")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(lambda _checked=False: self.toggle())

    def attach_row_menu(self) -> None:
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._open_row_menu)

    def refresh(self, activity_id: object, show_detail: bool) -> None:
        view = dnd_favourite_detail_button_view_pure(
            self._player_data,
            activity_id,
            show_detail=show_detail,
            can_toggle=self._on_favourite_dnd is not None,
        )
        self.button.setVisible(bool(view["visible"]))
        self.button.setEnabled(bool(view["enabled"]))
        if not view["visible"]:
            return
        self.button.setText(str(view["text"]))
        self.button.setToolTip(str(view["tooltip"]))
        self.button.setAccessibleName(str(view["tooltip"]))

    def toggle(self, activity_id: object = "") -> None:
        target = str(activity_id or self._open_card_id() or "")
        if self._on_favourite_dnd is None or not target:
            return
        result = self._on_favourite_dnd(target) or {}
        if not result.get("ok", False):
            self._show_error_message(
                "Reviewer badge",
                str(result.get("message", "That Distraction cannot be watched.")),
            )
        self.refresh(target, target == str(self._open_card_id() or ""))

    def _row_menu(self, activity_id: object) -> "QMenu":
        view = dnd_favourite_context_menu_view_pure(
            self._player_data,
            activity_id,
            can_toggle=self._on_favourite_dnd is not None,
        )
        menu = QMenu(self._tree)
        if not view["visible"]:
            return menu
        target = str(activity_id or "")
        action = menu.addAction(str(view["label"]))
        action.setObjectName("activityNotificationToggleAction")
        action.setEnabled(bool(view["enabled"]))
        action.triggered.connect(lambda _checked=False: self.toggle(target))
        return menu

    def _open_row_menu(self, pos) -> None:
        item = self._tree.itemAt(pos)
        if item is None:
            return
        menu = self._row_menu(item.data(0, Qt.ItemDataRole.UserRole))
        if menu.isEmpty():
            return
        menu.exec(self._tree.viewport().mapToGlobal(pos))
