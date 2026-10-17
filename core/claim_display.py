"""Player-facing display fields for the pure Bank Claims projection."""

from .skill_registry import get_skill, trainable_skill_definitions


def _skill_display(skill_id: str) -> str:
    skill = get_skill(skill_id)
    return skill.display_name if skill is not None else skill_id.replace("_", " ").title()


def _lamp_skills(row: dict) -> str:
    if row["fixed_skill_id"]:
        return _skill_display(row["fixed_skill_id"])
    options = tuple(row["skill_options"])
    if set(options) == {skill.id for skill in trainable_skill_definitions()}:
        return "Any skill"
    return ", ".join(_skill_display(skill_id) for skill_id in options)


def _claim_skill_tooltip(row: dict) -> str:
    skills = _lamp_skills(row)
    if row["fixed_skill_id"]:
        label = f"Pays {skills}"
    else:
        label = "Choose any skill" if skills == "Any skill" else f"Choose: {skills}"
    minimum_level = row["minimum_level"]
    if minimum_level > 1:
        return f"{label}. Minimum level: {minimum_level}."
    return f"{label}."


def _amount_text(row: dict) -> str:
    amount = float(row.get("xp_amount", 0) or 0)
    return f"{int(amount):,}" if amount.is_integer() else f"{amount:,.1f}"


def _lamp_metadata(row: dict) -> str:
    text = f"{_amount_text(row)} XP · {_lamp_skills(row)}"
    if row["minimum_level"] > 1 and not row["eligible_skill_ids"]:
        text += f" · Minimum level: {row['minimum_level']}"
    return text


def _skill_reward_metadata(row: dict) -> str:
    options = tuple(row.get("skill_options", ()) or ())
    skill_name = _skill_display(str(options[0])) if options else "Skill"
    return f"{_amount_text(row)} {skill_name} XP · {len(row['items'])} item rewards"


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


def _claim_bundle_tooltip(row: dict) -> str:
    items = tuple(row.get("items", ()) or ())
    lines = []
    for item in items:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            lines.append(f"{item[0]} x{item[1]}")
    return "\n".join(lines)


def _item_icon(row: dict) -> str:
    return str(row.get("item_name", row.get("display_name", "")))


def _bundle_icon(row: dict) -> str:
    items = tuple(row.get("items", ()) or ())
    first = items[0] if items else ()
    if isinstance(first, (tuple, list)) and first and isinstance(first[0], str):
        return first[0]
    return _item_icon(row)


def _display_name(row: dict) -> str:
    return str(row.get("display_name", _item_icon(row)))


def _lamp_title(row: dict) -> str:
    title = _display_name(row)
    if row["fixed_skill_id"]:
        title = title.replace("XP lamp", f"{_skill_display(row['fixed_skill_id'])} lamp")
    return title


_CLAIM_FORMATS = {
    "item": {
        "metadata": lambda row: "Ready to claim", "icon": _item_icon,
        "title": lambda row: f"{_display_name(row)} x{row.get('quantity', 1)}",
        "tooltip": _claim_bundle_tooltip, "choose_skill": False,
    },
    "xp_lamp": {
        "metadata": _lamp_metadata, "icon": _item_icon, "title": _lamp_title,
        "tooltip": _claim_skill_tooltip, "choose_skill": True,
    },
    "item_bundle": {
        "metadata": _bundle_metadata, "icon": _bundle_icon, "title": _display_name,
        "tooltip": _claim_bundle_tooltip, "choose_skill": False,
    },
    "skill_reward": {
        "metadata": _skill_reward_metadata, "icon": _bundle_icon, "title": _display_name,
        "tooltip": _claim_bundle_tooltip, "choose_skill": False,
    },
}


def claim_display_fields(row: dict) -> dict:
    format_rules = _CLAIM_FORMATS[row["claim_type"]]
    choose_skill = format_rules["choose_skill"] and not row["fixed_skill_id"]
    return {
        "title": format_rules["title"](row),
        "metadata": format_rules["metadata"](row),
        "action_label": "Choose skill" if choose_skill else "Claim",
        "tooltip": format_rules["tooltip"](row),
        "icon_name": format_rules["icon"](row),
        "choose_skill": choose_skill,
    }
