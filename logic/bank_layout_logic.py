"""Pure Bank presentation state over the canonical flat inventory."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any


MAIN_BANK_TAB_ID = "main"
BANK_SORT_MODES = (
    "manual",
    "mru",
    "date_added",
    "alphabetical",
    "quantity",
    "value",
)
BANK_DROP_MODES = ("swap", "insert")


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError, OverflowError):
        return max(minimum, default)


def _answered_reviews(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def default_bank_layout_state_pure() -> dict[str, Any]:
    return {
        "version": 1,
        "tabs": [
            {
                "id": MAIN_BANK_TAB_ID,
                "name": "All",
                "icon_item": "",
            }
        ],
        "items": {},
        "selected_tab": MAIN_BANK_TAB_ID,
        "sort_mode": "manual",
        "auto_categories": True,
        "drop_mode": "swap",
        "next_tab_id": 1,
    }


def _positive_inventory(inventory: Any) -> dict[str, int]:
    if not isinstance(inventory, Mapping):
        return {}
    clean: dict[str, int] = {}
    for item_name, quantity in inventory.items():
        if not isinstance(item_name, str) or not item_name:
            continue
        amount = _int(quantity)
        if amount > 0:
            clean[item_name] = amount
    return clean


def _normalize_positions(state: dict[str, Any]) -> None:
    tab_ids = [tab["id"] for tab in state["tabs"]]
    items = state["items"]
    for tab_id in tab_ids:
        names = [name for name, row in items.items() if row["tab_id"] == tab_id]
        names.sort(key=lambda name: (items[name]["position"], name.casefold()))
        for position, name in enumerate(names):
            items[name]["position"] = position


def _delete_empty_custom_tabs(state: dict[str, Any]) -> None:
    occupied = {row["tab_id"] for row in state["items"].values()}
    state["tabs"] = [
        tab
        for tab in state["tabs"]
        if tab["id"] == MAIN_BANK_TAB_ID or tab["id"] in occupied
    ]
    valid_ids = {tab["id"] for tab in state["tabs"]}
    if state["selected_tab"] not in valid_ids:
        state["selected_tab"] = MAIN_BANK_TAB_ID


def reconcile_bank_layout_state_pure(
    raw_state: Any,
    inventory: Any,
    *,
    answered_reviews: int = 0,
) -> dict[str, Any]:
    """Sanitize saved layout and reconcile it against positive Bank stacks.

    The two item timestamps are integer snapshots of the shared answered-review
    clock. An unchanged quantity never advances MRU, even if a later reconcile
    happens much later.
    """

    current_review = _int(answered_reviews)
    raw = raw_state if isinstance(raw_state, Mapping) else {}
    state = default_bank_layout_state_pure()

    tabs: list[dict[str, str]] = [state["tabs"][0]]
    seen_ids = {MAIN_BANK_TAB_ID}
    raw_tabs = raw.get("tabs")
    if isinstance(raw_tabs, (list, tuple)):
        for raw_tab in raw_tabs:
            if not isinstance(raw_tab, Mapping):
                continue
            tab_id = str(raw_tab.get("id", "")).strip()[:48]
            if tab_id == MAIN_BANK_TAB_ID:
                state["tabs"][0]["icon_item"] = str(
                    raw_tab.get("icon_item", "")
                ).strip()[:160]
                continue
            if not tab_id or tab_id in seen_ids:
                continue
            name = str(raw_tab.get("name", "")).strip()[:40] or "Bank tab"
            icon_item = str(raw_tab.get("icon_item", "")).strip()[:160]
            tabs.append({"id": tab_id, "name": name, "icon_item": icon_item})
            seen_ids.add(tab_id)
    state["tabs"] = tabs

    inventory_rows = _positive_inventory(inventory)
    raw_items = raw.get("items")
    raw_items = raw_items if isinstance(raw_items, Mapping) else {}
    items: dict[str, dict[str, Any]] = {}
    main_tail = 1 + max(
        (
            _int(raw_row.get("position"))
            for item_name, raw_row in raw_items.items()
            if item_name in inventory_rows
            and isinstance(raw_row, Mapping)
            and (
                str(raw_row.get("tab_id", MAIN_BANK_TAB_ID))
                == MAIN_BANK_TAB_ID
                or str(raw_row.get("tab_id", MAIN_BANK_TAB_ID)) not in seen_ids
            )
        ),
        default=-1,
    )
    for item_name, quantity in inventory_rows.items():
        raw_row = raw_items.get(item_name)
        if isinstance(raw_row, Mapping):
            tab_id = str(raw_row.get("tab_id", MAIN_BANK_TAB_ID))
            if tab_id not in seen_ids:
                tab_id = MAIN_BANK_TAB_ID
            position = _int(raw_row.get("position"))
            added_review = min(current_review, _int(raw_row.get("added_review")))
            previous_quantity = _int(raw_row.get("quantity"))
            used_review = min(current_review, _int(raw_row.get("used_review")))
            if previous_quantity != quantity:
                used_review = current_review
        else:
            tab_id = MAIN_BANK_TAB_ID
            position = main_tail
            main_tail += 1
            added_review = current_review
            used_review = current_review
        items[item_name] = {
            "tab_id": tab_id,
            "position": position,
            "added_review": added_review,
            "used_review": used_review,
            "quantity": quantity,
        }
    state["items"] = items

    owned = set(inventory_rows)
    for tab in state["tabs"]:
        if tab["icon_item"] not in owned:
            tab["icon_item"] = ""

    selected_tab = str(raw.get("selected_tab", MAIN_BANK_TAB_ID))
    state["selected_tab"] = selected_tab if selected_tab in seen_ids else MAIN_BANK_TAB_ID
    sort_mode = str(raw.get("sort_mode", "manual"))
    state["sort_mode"] = sort_mode if sort_mode in BANK_SORT_MODES else "manual"
    state["auto_categories"] = bool(raw.get("auto_categories", True))
    drop_mode = str(raw.get("drop_mode", "swap"))
    state["drop_mode"] = drop_mode if drop_mode in BANK_DROP_MODES else "swap"
    state["next_tab_id"] = _int(raw.get("next_tab_id"), 1, minimum=1)

    _normalize_positions(state)
    _delete_empty_custom_tabs(state)
    return state


def reconcile_bank_layout_for_player_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    data = dict(player_data or {})
    data["bank_layout"] = reconcile_bank_layout_state_pure(
        data.get("bank_layout"),
        data.get("inventory"),
        answered_reviews=_answered_reviews(data),
    )
    return data


def _copied_state(state: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(state))


def _tab_item_names(state: Mapping[str, Any], tab_id: str) -> list[str]:
    items = state.get("items") if isinstance(state, Mapping) else {}
    if not isinstance(items, Mapping):
        return []
    names = [
        name
        for name, row in items.items()
        if isinstance(name, str)
        and isinstance(row, Mapping)
        and row.get("tab_id") == tab_id
    ]
    names.sort(key=lambda name: (_int(items[name].get("position")), name.casefold()))
    return names


def move_bank_item_pure(
    state: Mapping[str, Any],
    item_name: str,
    destination_tab_id: str,
    destination_position: int,
    mode: str,
) -> dict[str, Any]:
    updated = _copied_state(state)
    items = updated.get("items")
    tabs = updated.get("tabs")
    if not isinstance(items, dict) or item_name not in items or not isinstance(tabs, list):
        return updated
    if destination_tab_id not in {tab.get("id") for tab in tabs if isinstance(tab, Mapping)}:
        return updated
    drop_mode = mode if mode in BANK_DROP_MODES else "swap"
    source_tab_id = str(items[item_name]["tab_id"])
    source_position = _int(items[item_name]["position"])
    destination_names = _tab_item_names(updated, destination_tab_id)
    if drop_mode == "swap":
        position = min(_int(destination_position), len(destination_names))
        if position < len(destination_names):
            occupant = destination_names[position]
            if occupant == item_name:
                return updated
            items[occupant]["tab_id"] = source_tab_id
            items[occupant]["position"] = source_position
        items[item_name]["tab_id"] = destination_tab_id
        items[item_name]["position"] = position
    else:
        if source_tab_id == destination_tab_id:
            destination_names = [name for name in destination_names if name != item_name]
        position = min(_int(destination_position), len(destination_names))
        insertion_order = list(destination_names)
        insertion_order.insert(position, item_name)
        for index, name in enumerate(insertion_order):
            items[name]["tab_id"] = destination_tab_id
            items[name]["position"] = index

    _normalize_positions(updated)
    _delete_empty_custom_tabs(updated)
    return updated


def create_bank_tab_pure(
    state: Mapping[str, Any], item_name: str
) -> tuple[dict[str, Any], str]:
    updated = _copied_state(state)
    items = updated.get("items")
    if not isinstance(items, dict) or item_name not in items:
        return updated, ""
    next_id = _int(updated.get("next_tab_id"), 1, minimum=1)
    existing_ids = {tab.get("id") for tab in updated.get("tabs", ()) if isinstance(tab, Mapping)}
    while f"tab-{next_id}" in existing_ids:
        next_id += 1
    tab_id = f"tab-{next_id}"
    updated.setdefault("tabs", []).append(
        {"id": tab_id, "name": f"Tab {next_id}", "icon_item": ""}
    )
    updated["next_tab_id"] = next_id + 1
    updated = move_bank_item_pure(updated, item_name, tab_id, 0, "insert")
    updated["selected_tab"] = tab_id
    return updated, tab_id


def delete_bank_tab_pure(state: Mapping[str, Any], tab_id: str) -> dict[str, Any]:
    updated = _copied_state(state)
    if tab_id == MAIN_BANK_TAB_ID:
        return updated
    if tab_id not in {tab.get("id") for tab in updated.get("tabs", ()) if isinstance(tab, Mapping)}:
        return updated
    main_tail = len(_tab_item_names(updated, MAIN_BANK_TAB_ID))
    for item_name in _tab_item_names(updated, tab_id):
        updated["items"][item_name]["tab_id"] = MAIN_BANK_TAB_ID
        updated["items"][item_name]["position"] = main_tail
        main_tail += 1
    updated["tabs"] = [tab for tab in updated["tabs"] if tab.get("id") != tab_id]
    if updated.get("selected_tab") == tab_id:
        updated["selected_tab"] = MAIN_BANK_TAB_ID
    _normalize_positions(updated)
    return updated


def rename_bank_tab_pure(
    state: Mapping[str, Any], tab_id: str, name: str
) -> dict[str, Any]:
    updated = _copied_state(state)
    clean_name = str(name).strip()[:40]
    if not clean_name or tab_id == MAIN_BANK_TAB_ID:
        return updated
    for tab in updated.get("tabs", ()):
        if tab.get("id") == tab_id:
            tab["name"] = clean_name
            break
    return updated


def set_bank_tab_icon_pure(
    state: Mapping[str, Any],
    tab_id: str,
    item_name: str,
    inventory: Any,
) -> dict[str, Any]:
    updated = _copied_state(state)
    owned = _positive_inventory(inventory)
    if item_name not in owned:
        return updated
    for tab in updated.get("tabs", ()):
        if tab.get("id") == tab_id:
            tab["icon_item"] = item_name
            break
    return updated


def reorder_bank_tab_pure(
    state: Mapping[str, Any], tab_id: str, destination_index: int
) -> dict[str, Any]:
    updated = _copied_state(state)
    if tab_id == MAIN_BANK_TAB_ID:
        return updated
    tabs = updated.get("tabs")
    if not isinstance(tabs, list):
        return updated
    source_index = next((index for index, tab in enumerate(tabs) if tab.get("id") == tab_id), -1)
    if source_index < 1:
        return updated
    tab = tabs.pop(source_index)
    target = min(max(1, _int(destination_index)), len(tabs))
    tabs.insert(target, tab)
    return updated


def bank_sections_pure(
    state: Mapping[str, Any],
    inventory: Any,
    tab_id: str,
    sort_mode: str,
    *,
    auto_categories: bool,
    categories: Mapping[str, str] | None = None,
    values: Mapping[str, int] | None = None,
) -> list[dict[str, Any]]:
    inventory_rows = _positive_inventory(inventory)
    state_items = state.get("items") if isinstance(state, Mapping) else {}
    state_items = state_items if isinstance(state_items, Mapping) else {}
    categories = categories if isinstance(categories, Mapping) else {}
    values = values if isinstance(values, Mapping) else {}
    mode = sort_mode if sort_mode in BANK_SORT_MODES else "manual"

    rows = []
    for item_name in _tab_item_names(state, tab_id):
        if item_name not in inventory_rows:
            continue
        saved = state_items[item_name]
        rows.append(
            {
                "name": item_name,
                "quantity": inventory_rows[item_name],
                "category": str(categories.get(item_name, "Other")),
                "value": _int(values.get(item_name)),
                "position": _int(saved.get("position")),
                "added_review": _int(saved.get("added_review")),
                "used_review": _int(saved.get("used_review")),
            }
        )

    key = {
        "manual": lambda row: (row["position"], row["name"].casefold()),
        "mru": lambda row: (-row["used_review"], row["name"].casefold()),
        "date_added": lambda row: (-row["added_review"], row["name"].casefold()),
        "alphabetical": lambda row: (row["name"].casefold(),),
        "quantity": lambda row: (-row["quantity"], row["name"].casefold()),
        "value": lambda row: (-row["value"], row["name"].casefold()),
    }[mode]

    if not auto_categories:
        return [{"label": "", "items": sorted(rows, key=key)}]

    section_order: list[str] = []
    section_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        label = row["category"]
        if label not in section_rows:
            section_order.append(label)
            section_rows[label] = []
        section_rows[label].append(row)
    return [
        {"label": label, "items": sorted(section_rows[label], key=key)}
        for label in section_order
    ]
