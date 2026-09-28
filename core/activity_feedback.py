"""One popup line for the no-XP activity results a single review produced."""


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


def combine_activity_feedback(messages) -> str:
    """Sum repeated gains of one item, or repeated nest openings, into one line.

    Any other mix has no single honest total, so the review's last message
    stands for all of them.
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
        return f"+{amount} {item}"
    if opened_nests > 0 and not item_totals:
        return f"Opened {opened_nests} bird nest{'s' if opened_nests != 1 else ''}"
    return messages[-1] if messages else ""
