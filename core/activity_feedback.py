"""The feedback lines of one card: one popup line for its no-XP results, and
the reason a danger stop ended it early (plan 2.1, owner Q8).
"""

# The reason rides on the card's last line rather than a line of its own: with
# no XP the popup keeps one line, so a separate line would hide the result it
# explains. The Thieving stun already says so on its own line, and a kill, wave
# or round ends an activity card by design, so neither gets a text.
_DANGER_STOP_TEXTS = {
    "died": "Ended early: you died",
    "fled": "Ended early: you fled",
    "low_lp_no_food": "Ended early: low LP, no food",
    "poison_started": "Ended early: new poison",
    "prayer_empty": "Ended early: prayer ran out",
    "familiar_ended": "Ended early: familiar ran out",
    "void_shifter": "Ended early: Void shifter",
    "out_of_ammo": "Ended early: out of ammo",
    "out_of_runes": "Ended early: out of runes",
    "bank_trip": "Ended early: bank trip",
    "slayer_task_complete": "Ended early: Slayer task done",
}


def _whole_number(text: str):
    try:
        return int(text)
    except ValueError:
        return None


def _item_gain(text: str):
    """Return ``(item, amount)`` for a positive ``+N Item`` line."""
    if not text.startswith("+"):
        return None
    parts = text[1:].split(" ", 1)
    if len(parts) != 2:
        return None
    amount = _whole_number(parts[0])
    if amount is None or amount <= 0:
        return None
    return parts[1], amount


def _opened_bird_nests(text: str) -> int:
    if not text.startswith("Opened ") or " bird nest" not in text:
        return 0
    return _whole_number(text.split(" ", 2)[1]) or 0


def _with_stop_reason(line, stop_reason: str) -> str:
    text = _DANGER_STOP_TEXTS.get(stop_reason)
    return f"{line} · {text}" if line and text else line


def lines_with_stop_reason(messages, stop_reason: str) -> list:
    """The card's lines, the last one ending with why a danger stop ended the card.

    A card without a line gets no reason: the existing lines are the only
    feedback surface.
    """
    return [*messages[:-1], _with_stop_reason(messages[-1], stop_reason)] if messages else []


def combine_activity_feedback(messages, stop_reason: str = "") -> str:
    """Sum repeated gains of one item, or repeated nest openings, into one line.

    Any other mix has no single honest total, so the review's last message
    stands for all of them. A danger stop's reason ends the line after the sum,
    so it never breaks a total.
    """
    item_totals = {}
    opened_nests = 0
    for message in messages:
        text = str(message)
        gain = _item_gain(text)
        if gain is not None:
            item, amount = gain
            item_totals[item] = item_totals.get(item, 0) + amount
        opened_nests += _opened_bird_nests(text)

    if len(item_totals) == 1 and opened_nests == 0:
        [(item, amount)] = item_totals.items()
        line = f"+{amount} {item}"
    elif opened_nests > 0 and not item_totals:
        line = f"Opened {opened_nests} bird nest{'s' if opened_nests != 1 else ''}"
    else:
        line = messages[-1] if messages else ""
    return _with_stop_reason(line, stop_reason)
