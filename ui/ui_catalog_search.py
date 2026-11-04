"""Search entry and filter controls shared by the catalog pages."""

from ..core.search_match import match_rank
from .ui_palette import dim_text_css

try:
    from aqt.qt import QEvent, QLabel, QLineEdit, Qt, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - keep catalog modules importable without Qt
    HAS_QT = False
else:
    HAS_QT = True


if HAS_QT:
    from .ui_flow_layout import FlowLayout as WidgetFlowLayout
    from .ui_text_fit import LeadRowLayout, side_pair

    class SearchLineEdit(QLineEdit):
        """Select the whole query on a double click so it can be replaced."""

        def mouseDoubleClickEvent(self, event):
            super().mouseDoubleClickEvent(event)
            if event.button() == Qt.MouseButton.LeftButton:
                self.selectAll()

    class CatalogFilterBar(QWidget):
        """Shared search/filter chrome for catalog-like pages.

        Pages retain ownership of searchable metadata and filter predicates.
        This widget standardizes text entry, clear/Escape behavior, optional
        page filters, and the visible/total summary without knowing what a row
        means or how a result is rendered.
        """

        def __init__(
            self,
            *,
            placeholder: str,
            search_object_name: str,
            parent=None,
        ):
            super().__init__(parent)
            self.setObjectName(f"{search_object_name}Bar")
            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(8)

            search_row = LeadRowLayout()
            search_row.setContentsMargins(0, 0, 0, 0)
            search_row.setSpacing(8)

            self.search_input = SearchLineEdit()
            self.search_input.setObjectName(search_object_name)
            self.search_input.setPlaceholderText(placeholder)
            self.search_input.setClearButtonEnabled(True)
            self.search_input.setStyleSheet(
                "QLineEdit { padding: 7px 10px; border: 1px solid palette(mid);"
                " border-radius: 8px; color: palette(text); background: palette(base); }"
            )
            self.search_input.installEventFilter(self)
            self.search_input.setMinimumWidth(self.search_input.fontMetrics().horizontalAdvance(placeholder) + 56)
            search_row.addWidget(self.search_input)

            self.summary_label = QLabel("")
            self.summary_label.setObjectName(f"{search_object_name}Summary")
            self.summary_label.setStyleSheet(f"color: {dim_text_css(self.summary_label)};")
            search_row.addWidget(self.summary_label)
            root.addLayout(search_row)

            self.filter_row = QWidget()
            # Filters wrap onto more lines rather than squeezing at 720 px. The
            # gap between filters is three times a label's gap to its own box,
            # so each label reads as part of its box, not of the filter before.
            self.filter_layout = WidgetFlowLayout(self.filter_row, h_spacing=12, v_spacing=8)
            self.filter_row.setVisible(False)
            root.addWidget(self.filter_row)

        def eventFilter(self, watched, event):  # type: ignore[no-untyped-def]
            if (
                watched is self.search_input
                and event.type() == QEvent.Type.KeyPress
                and event.key() == Qt.Key.Key_Escape
                and self.search_input.text()
            ):
                self.search_input.clear()
                event.accept()
                return True
            return super().eventFilter(watched, event)

        def add_filter(self, widget: QWidget, label: str = "") -> None:
            self.filter_row.setVisible(True)
            if label:
                widget = side_pair(label, widget, f"color: {dim_text_css(widget)};")
            self.filter_layout.addWidget(widget)

        def query(self) -> str:
            return self.search_input.text().strip().casefold()

        def matches_text(self, *values: object) -> bool:
            return match_rank(self.query(), *values) is not None

        def set_count(self, visible: int, total: int) -> None:
            self.summary_label.setText(f"Showing {int(visible)}/{int(total)}")
            self.summary_label.setMinimumWidth(self.summary_label.sizeHint().width())

else:
    class SearchLineEdit:
        pass

    class CatalogFilterBar:
        # The tab modules import this at module scope, so it must exist without
        # Qt or `import ui_tab_shop` fails outright instead of degrading.
        def __init__(self, *, placeholder: str = "", search_object_name: str = "", parent=None):
            pass

        def add_filter(self, widget, label: str = "") -> None:
            pass

        def query(self) -> str:
            return ""

        def matches_text(self, *values: object) -> bool:
            return True

        def set_count(self, visible: int, total: int) -> None:
            pass
