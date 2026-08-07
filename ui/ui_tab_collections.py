"""Collections tab: Music first, then the registry-backed combat drop log."""

try:
    from aqt.qt import (  # type: ignore
        QGraphicsOpacityEffect,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QScrollArea,
        QTreeWidget,
        QTreeWidgetItem,
        Qt,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from ..data.combat_data import COMBAT_ENEMY_DATA, COMBAT_TARGET_GROUP_ORDER
from ..logic.collection_log_logic import (
    collection_totals_pure,
    drop_log_view_pure,
)
from ..logic.music_log_logic import music_log_view_pure
from .ui import _clear_layout, _pixel_item_icon, dim_text_color, dim_text_css


_NODE_ROLE = Qt.ItemDataRole.UserRole if "Qt" in globals() else None


def build_collections_tab(ctx) -> "QWidget":
    """Build the settled left-family and right-detail Collections surface."""

    page = QWidget()
    page.setObjectName("collectionsPage")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)

    heading = QHBoxLayout()
    title = QLabel("Collections")
    title.setStyleSheet(
        "font-weight: 700; font-size: 15px; color: palette(text);"
    )
    heading.addWidget(title)
    global_totals = QLabel()
    global_totals.setObjectName("collectionsGlobalTotals")
    global_totals.setStyleSheet(f"color: {dim_text_css(global_totals)};")
    heading.addStretch(1)
    heading.addWidget(global_totals)
    layout.addLayout(heading)

    split = QHBoxLayout()
    split.setSpacing(10)
    layout.addLayout(split, 1)

    navigation = QTreeWidget()
    navigation.setObjectName("collectionsFamilyTree")
    navigation.setColumnCount(2)
    navigation.setHeaderHidden(True)
    navigation.setRootIsDecorated(True)
    navigation.setItemsExpandable(True)
    navigation.setFixedWidth(244)
    navigation.setColumnWidth(0, 184)
    navigation.header().setSectionResizeMode(
        0,
        QHeaderView.ResizeMode.Stretch,
    )
    navigation.header().setSectionResizeMode(
        1,
        QHeaderView.ResizeMode.ResizeToContents,
    )
    navigation.setStyleSheet(
        "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px; "
        "background: palette(base); color: palette(text); }"
    )
    split.addWidget(navigation)

    right = QWidget()
    right.setObjectName("collectionsDetailPanel")
    right_layout = QVBoxLayout(right)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(8)
    split.addWidget(right, 1)

    detail_heading = QHBoxLayout()
    detail_title = QLabel()
    detail_title.setObjectName("collectionsDetailTitle")
    detail_title.setStyleSheet(
        "font-weight: 700; font-size: 14px; color: palette(text);"
    )
    detail_heading.addWidget(detail_title)
    detail_heading.addStretch(1)
    family_totals = QLabel()
    family_totals.setObjectName("collectionsFamilyTotals")
    family_totals.setStyleSheet(f"color: {dim_text_css(family_totals)};")
    detail_heading.addWidget(family_totals)
    right_layout.addLayout(detail_heading)

    search_row = QHBoxLayout()
    search = QLineEdit()
    search.setObjectName("collectionsSearch")
    search.setPlaceholderText("Search this family…")
    search_row.addWidget(search, 1)
    search_count = QLabel()
    search_count.setObjectName("collectionsSearchCount")
    search_count.setStyleSheet(f"color: {dim_text_css(search_count)};")
    search_row.addWidget(search_count)
    right_layout.addLayout(search_row)

    body = QWidget()
    body.setObjectName("collectionsDetailBody")
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.addWidget(body, 1)

    nav_items: dict[str, QTreeWidgetItem] = {}

    def _node_key(item: QTreeWidgetItem | None) -> str:
        if item is None:
            return "music"
        return str(item.data(0, _NODE_ROLE) or "music")

    def _drop_view(target_id=None, query=""):
        return drop_log_view_pure(
            ctx.player_data,
            COMBAT_ENEMY_DATA,
            target_id=target_id,
            search=query,
            group_order=COMBAT_TARGET_GROUP_ORDER,
        )

    def _populate_navigation(selected_key: str = "music") -> None:
        totals = collection_totals_pure(ctx.player_data, COMBAT_ENEMY_DATA)
        full_drop_view = _drop_view()
        navigation.blockSignals(True)
        navigation.clear()
        nav_items.clear()

        music = QTreeWidgetItem(
            [
                "Music Log",
                f"{totals['music']['collected']}/{totals['music']['total']}",
            ]
        )
        music.setData(0, _NODE_ROLE, "music")
        navigation.addTopLevelItem(music)
        nav_items["music"] = music

        drops = QTreeWidgetItem(
            [
                "Boss/monster drop log",
                f"{totals['drop_log']['collected']}/{totals['drop_log']['total']}",
            ]
        )
        drops.setData(0, _NODE_ROLE, "drop_log")
        navigation.addTopLevelItem(drops)
        nav_items["drop_log"] = drops
        for target in full_drop_view["targets"]:
            target_id = str(target["target_id"])
            child = QTreeWidgetItem(
                [
                    str(target["name"]),
                    f"{target['collected']}/{target['total']}",
                ]
            )
            child.setData(0, _NODE_ROLE, f"target:{target_id}")
            drops.addChild(child)
            nav_items[f"target:{target_id}"] = child
        drops.setExpanded(True)
        navigation.setCurrentItem(
            nav_items.get(selected_key, nav_items["music"])
        )
        navigation.blockSignals(False)

    def _render_music(query: str) -> None:
        view = music_log_view_pure(ctx.player_data, search=query)
        detail_title.setText("Music Log")
        family_totals.setText(f"{view['unlocked']}/{view['total']}")
        tree = QTreeWidget()
        tree.setObjectName("collectionsMusicTracks")
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(False)
        tree.setAlternatingRowColors(True)
        tree.setUniformRowHeights(True)
        tree.setStyleSheet(
            "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px; "
            "background: palette(base); color: palette(text); }"
        )
        for row in view["tracks"]:
            item = QTreeWidgetItem([str(row["label"])])
            item.setData(0, _NODE_ROLE, int(row["track_id"]))
            if not row["unlocked"]:
                item.setForeground(0, dim_text_color(tree))
            tree.addTopLevelItem(item)
        body_layout.addWidget(tree, 1)
        search_count.setText(f"Showing {len(view['tracks'])}/{view['total']}")

    def _select_target_from_row(item: QTreeWidgetItem) -> None:
        target_id = str(item.data(0, _NODE_ROLE) or "")
        target_item = nav_items.get(f"target:{target_id}")
        if target_item is not None:
            navigation.setCurrentItem(target_item)

    def _render_drop_overview(query: str) -> None:
        view = _drop_view(query=query)
        detail_title.setText("Boss/monster drop log")
        family_totals.setText(f"{view['collected']}/{view['total']}")
        tree = QTreeWidget()
        tree.setObjectName("collectionsDropTargets")
        tree.setColumnCount(2)
        tree.setHeaderLabels(("Target", "Collected"))
        tree.setRootIsDecorated(False)
        tree.setAlternatingRowColors(True)
        tree.setUniformRowHeights(True)
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tree.header().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        for target in view["targets"]:
            item = QTreeWidgetItem(
                [
                    str(target["name"]),
                    f"{target['collected']}/{target['total']}",
                ]
            )
            item.setData(0, _NODE_ROLE, str(target["target_id"]))
            tree.addTopLevelItem(item)
        tree.itemActivated.connect(_select_target_from_row)
        body_layout.addWidget(tree, 1)
        search_count.setText(
            f"Showing {len(view['targets'])}/{len(_drop_view()['targets'])}"
        )

    def _render_drop_target(target_id: str, query: str) -> None:
        view = _drop_view(target_id=target_id, query=query)
        target = next(
            (
                row
                for row in _drop_view()["targets"]
                if row["target_id"] == target_id
            ),
            None,
        )
        if target is None:
            _render_drop_overview(query)
            return
        detail_title.setText(str(target["name"]))
        family_totals.setText(
            f"{target['collected']}/{target['total']} · {target['kills']} kills"
        )

        scroll = QScrollArea()
        scroll.setObjectName("collectionsDropRows")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        content = QWidget()
        content.setObjectName("collectionsDropRowsContent")
        rows_layout = QVBoxLayout(content)
        rows_layout.setContentsMargins(0, 0, 4, 0)
        rows_layout.setSpacing(4)
        for index, row in enumerate(view["rows"]):
            row_widget = QWidget()
            row_widget.setObjectName(
                f"collectionsDropRow::{target_id}::{index}"
            )
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(8, 5, 8, 5)
            row_layout.setSpacing(8)

            icon_label = QLabel("?")
            icon_label.setObjectName(
                f"collectionsDropIcon::{target_id}::{index}"
            )
            icon_label.setFixedWidth(28)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if row["state"] != "undiscovered":
                icon = _pixel_item_icon(str(row["item_name"]), 24)
                if icon is not None:
                    icon_label.setText("")
                    icon_label.setPixmap(icon.pixmap(24, 24))
            row_layout.addWidget(icon_label)

            name = QLabel(str(row["label"]))
            name.setObjectName(
                f"collectionsDropName::{target_id}::{index}"
            )
            name.setStyleSheet("color: palette(text);")
            row_layout.addWidget(name, 1)

            detail = QLabel()
            detail.setObjectName(
                f"collectionsDropCount::{target_id}::{index}"
            )
            if row["state"] == "collected":
                detail.setText(f"×{row['quantity_seen']}")
            elif row["state"] == "discovered":
                detail.setText("Not collected")
            detail.setStyleSheet(f"color: {dim_text_css(detail)};")
            row_layout.addWidget(detail)

            if row["state"] == "discovered":
                opacity = QGraphicsOpacityEffect(row_widget)
                opacity.setOpacity(0.58)
                row_widget.setGraphicsEffect(opacity)
            rows_layout.addWidget(row_widget)
        rows_layout.addStretch(1)
        scroll.setWidget(content)
        body_layout.addWidget(scroll, 1)
        search_count.setText(f"Showing {len(view['rows'])}/{target['total']}")

    def _render_right() -> None:
        _clear_layout(body_layout)
        key = _node_key(navigation.currentItem())
        query = search.text()
        if key == "music":
            _render_music(query)
        elif key == "drop_log":
            _render_drop_overview(query)
        else:
            _render_drop_target(key.removeprefix("target:"), query)

    def _selection_changed() -> None:
        search.blockSignals(True)
        search.clear()
        search.blockSignals(False)
        _render_right()

    def _refresh_all() -> None:
        selected_key = _node_key(navigation.currentItem())
        totals = collection_totals_pure(ctx.player_data, COMBAT_ENEMY_DATA)
        overall = totals["global"]
        global_totals.setText(
            f"Collected {overall['collected']} / {overall['total']} overall"
        )
        _populate_navigation(selected_key)
        _render_right()

    navigation.currentItemChanged.connect(lambda *_args: _selection_changed())
    search.textChanged.connect(lambda _text: _render_right())
    _refresh_all()
    ctx.refreshers["collections"] = _refresh_all
    return page
