"""ui_tab_collections.py - passive collection records, beginning with Music Log."""

try:
    from aqt.qt import (  # type: ignore
        QComboBox,
        QHeaderView,
        QHBoxLayout,
        QLabel,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - non-Qt environment keeps imports safe
    pass

from ..logic.music_log_logic import music_log_view_pure
from .ui import CatalogFilterBar, dim_text_css


def build_collections_tab(ctx) -> "QWidget":
    """Return the Collections page with the complete passive Music Log."""

    page = QWidget()
    page.setObjectName("collectionsPage")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)

    heading = QHBoxLayout()
    title = QLabel("Collections")
    title.setStyleSheet("font-weight: 700; font-size: 15px; color: palette(text);")
    heading.addWidget(title)
    totals = QLabel("")
    totals.setObjectName("collectionsMusicTotals")
    totals.setStyleSheet(f"color: {dim_text_css(totals)};")
    heading.addWidget(totals)
    heading.addStretch(1)
    layout.addLayout(heading)

    filters = CatalogFilterBar(
        placeholder="Search track names, hints, or sources",
        search_object_name="collectionsMusicSearch",
    )
    state_box = QComboBox()
    state_box.setObjectName("collectionsMusicStateFilter")
    for label, value in (
        ("All", ""),
        ("Unlocked", "unlocked"),
        ("Locked", "locked"),
        ("Latent", "latent"),
    ):
        state_box.addItem(label, value)
    filters.add_filter(state_box, "State")
    layout.addWidget(filters)

    tracks = QTreeWidget()
    tracks.setObjectName("collectionsMusicTracks")
    tracks.setColumnCount(4)
    tracks.setHeaderLabels(("Track", "Hint", "Source", "State"))
    tracks.setRootIsDecorated(False)
    tracks.setAlternatingRowColors(True)
    tracks.setUniformRowHeights(True)
    tracks.setStyleSheet(
        "QTreeWidget { border: 1px solid palette(mid); border-radius: 8px;"
        " background: palette(base); color: palette(text); }"
    )
    header = tracks.header()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
    layout.addWidget(tracks, 1)

    def _render() -> None:
        view = music_log_view_pure(
            ctx.player_data,
            search=filters.query(),
            completion_filter=state_box.currentData() or "",
        )
        tracks.clear()
        items = []
        for row in view["tracks"]:
            item = QTreeWidgetItem(
                (row["name"], row["hint"], row["source"], row["status"])
            )
            for column in range(4):
                item.setToolTip(column, item.text(column))
            items.append(item)
        tracks.addTopLevelItems(items)
        totals.setText(
            f"{view['unlocked']}/{view['total']} unlocked · {view['latent']} latent"
        )
        filters.set_count(len(view["tracks"]), view["total"])

    filters.search_input.textChanged.connect(lambda _text: _render())
    state_box.currentIndexChanged.connect(lambda _index: _render())
    _render()
    ctx.refreshers["collections"] = _render
    return page
