"""The Elder Kiln's first journal row, chosen from the recorded hatch and the saved attempt."""

from ...data.quest.elder_kiln import (
    AFTER_OFFER_COPY, BEFORE_OFFER_COPY, FAILURE_COPY, INSTRUCTIONS_COPY, LEGACY_COPY, QUEST_ID,
    STATE_KEY, SUCCESS_COPY,
)
from ...data.quest_action_proof_data import ELDER_KILN_HATCH_PROOF
from ..quest_action_proofs import quest_action_proof_completed_pure
from .elder_kiln_state import sanitize_elder_kiln_state_pure

_OPENING_LINES = {
    "request": (BEFORE_OFFER_COPY,),
    "preparing": (AFTER_OFFER_COPY, INSTRUCTIONS_COPY),
    "active": (AFTER_OFFER_COPY, INSTRUCTIONS_COPY),
    "failed": (AFTER_OFFER_COPY, INSTRUCTIONS_COPY, FAILURE_COPY),
}


def elder_kiln_journal_row_pure(player_data, quest_id, row):
    if quest_id != QUEST_ID or row["stage"] != 1:
        return row
    if quest_action_proof_completed_pure(player_data, ELDER_KILN_HATCH_PROOF):
        return dict(row, lines=(SUCCESS_COPY,))
    if not row["current"]:
        # Advanced saves keep their progress; only the missing deed is honest here.
        return dict(row, lines=(LEGACY_COPY,), completed=False, current=False)
    phase = sanitize_elder_kiln_state_pure(player_data.get(STATE_KEY), False)["phase"]
    return dict(row, lines=_OPENING_LINES[phase])
