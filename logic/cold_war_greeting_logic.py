"""Assignment and read-only journal formatting for Cold War greetings."""

import random
from collections.abc import Mapping

from ..data.cold_war_greeting_data import COLD_WAR_GREETING_EMOTES, COLD_WAR_GREETING_LENGTH


def sanitize_cold_war_greeting_pure(raw):
    if not isinstance(raw, (list, tuple)) or len(raw) != COLD_WAR_GREETING_LENGTH:
        return []
    if not all(isinstance(move, str) and move in COLD_WAR_GREETING_EMOTES for move in raw):
        return []
    return list(raw) if len(set(raw)) == COLD_WAR_GREETING_LENGTH else []


def _cold_war_active(player_data):
    quests = player_data.get("quests", {})
    state = quests.get("cold_war", {}) if isinstance(quests, Mapping) else {}
    return isinstance(state, Mapping) and bool(state.get("started") or state.get("completed"))


def ensure_cold_war_greeting_pure(player_data):
    if not _cold_war_active(player_data):
        return []
    greeting = sanitize_cold_war_greeting_pure(player_data.get("cold_war_greeting"))
    return greeting or random.sample(COLD_WAR_GREETING_EMOTES, COLD_WAR_GREETING_LENGTH)


def cold_war_journal_lines_pure(player_data, quest_id, stage, lines):
    result = tuple(lines)
    if quest_id == "cold_war" and stage == 1 and _cold_war_active(player_data):
        greeting = sanitize_cold_war_greeting_pure(player_data.get("cold_war_greeting"))
        if greeting:
            result += ("Penguin greeting: " + " → ".join(greeting) + " (automatic).",)
    return result
