"""Bank grid columns: as many 54 px cells as the grid's width holds, up to 12.

A fixed 12-column grid needed 648 px, which with the detail column forced the
Bank tab past the 720 px minimum dialog width and scrolled it sideways.
"""

BANK_CELL_PX = 54
BANK_MAX_COLUMNS = 12


def bank_grid_columns(grid_scroll) -> int:
    usable = grid_scroll.width() - grid_scroll.verticalScrollBar().sizeHint().width()
    return max(1, min(BANK_MAX_COLUMNS, usable // BANK_CELL_PX))


def fit_bank_grid_columns(grid_scroll, grid_layout) -> int:
    """Size the grid's columns to its width; the column after the last absorbs the slack."""
    columns = bank_grid_columns(grid_scroll)
    for column in range(BANK_MAX_COLUMNS + 1):
        grid_layout.setColumnMinimumWidth(column, BANK_CELL_PX if column < columns else 0)
        grid_layout.setColumnStretch(column, int(column == columns))
    return columns
