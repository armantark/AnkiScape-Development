"""One ranked, token-based search rule for the game's catalogs."""

import re


def _one_edit(left: str, right: str) -> bool:
    if abs(len(left) - len(right)) > 1:
        return False
    if len(left) == len(right):
        return sum(a != b for a, b in zip(left, right)) <= 1
    short, long = (left, right) if len(left) < len(right) else (right, left)
    for index, char in enumerate(short):
        if char != long[index]:
            return short[index:] == long[index + 1:]
    return True


def _fuzzy_token(token: str, word: str) -> bool:
    letters = iter(word)
    return all(char in letters for char in token) or _one_edit(token, word)


def match_rank(query: str, primary: object, *metadata: object) -> int | None:
    """Return exact, prefix, name tokens, metadata tokens, fuzzy, or no match.

    Short tokens require substrings. Longer tokens can skip letters in one
    word or differ from that word by one insertion, deletion or substitution.
    """
    query = " ".join(query.casefold().split())
    name = " ".join(str(primary).casefold().split())
    if not query or query == name:
        return 0
    if name.startswith(query):
        return 1
    tokens = query.split()
    if all(token in name for token in tokens):
        return 2
    text = " ".join((name, *(str(value).casefold() for value in metadata if value is not None)))
    if all(token in text for token in tokens):
        return 3
    words = re.findall(r"[^\W_]+", text)
    if all(token in text or (len(token) >= 4 and any(_fuzzy_token(token, word) for word in words)) for token in tokens):
        return 4
    return None
