"""Player-facing display fields for the pure Bank Claims projection."""

from .skill_registry import get_skill


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


def claim_display_fields(row: dict) -> dict:
    claim_type = row["claim_type"]
    title = _claim_title(row)
    if row["fixed_skill_id"] and claim_type == "xp_lamp":
        title = title.replace("XP lamp", f"{_skill_display(row['fixed_skill_id'])} lamp")
    tooltip = _claim_skill_tooltip(row) if claim_type == "xp_lamp" else _claim_bundle_tooltip(row)
    choose_skill = claim_type == "xp_lamp" and not row["fixed_skill_id"]
    return {
        "title": title,
        "metadata": _claim_metadata(row),
        "action_label": "Choose skill" if choose_skill else "Claim",
        "tooltip": tooltip,
        "icon_name": _claim_icon_name(row),
        "choose_skill": choose_skill,
    }
