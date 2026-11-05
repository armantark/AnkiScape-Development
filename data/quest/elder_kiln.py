"""The Elder Kiln's egg-hatching opening, played as an owner-approved review exercise.

The period sources establish the request, the offer, fire and water spells that
move a heat gauge between moving markers, Mej assistance, the restart at 0% and
the Ga’al outcome at 100%. They do not state server initialization, increments,
inclusivity, cadence, helper latency, marker narrowing, reset or reconnect
behavior. Every number below that only Darkan's modern reconstruction supplies
is a marked placeholder; none of them is a verified period mechanic.

The exercise runs in attempt-relative logical steps, never seconds. Checked and
failed-retrieval source lists remain distinct in the evidence packet; a source
that was unavailable or unchecked is not negative evidence.
"""

from .contract import QuestStage, QuestStageRequirementCleanup
from ..quest_action_proof_data import ELDER_KILN_HATCH_PROOF
from ...generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG as _CATALOG

__all__ = ()

QUEST_ID = "the_elder_kiln"
STATE_KEY = "elder_kiln_hatching"
HATCH_EVENT = ("quest_activity", "elder_kiln_first_egg")
# Local feedback identities; only the hatch is a completed deed.
ATTEMPT_EVENT_ID = "elder_kiln_first_egg_attempt"
FAILURE_EVENT_ID = "elder_kiln_first_egg_failure"
HATCH_EVENT_ID = "elder_kiln_first_egg_hatch"

# Provenance. Bodies are retained in the 1440 evidence packet beside
# source-index.json; they are evidence references, not runtime dependencies.
# Historical cutoff: strictly before 2012-11-20T00:00:00Z.
SOURCE_W = {
    "title": "The Elder Kiln", "oldid": 6579162, "timestamp": "2012-11-18T16:32:05Z",
    "url": "https://runescape.wiki/w/index.php?title=The_Elder_Kiln&oldid=6579162",
    "body": "sources/the-elder-kiln-6579162.txt",
    "sha256": "edfc7a09036a7e3b48c395bb1926b6df0dbedab29d201af614822f3d6394da8a",
    # 21–23 entry skills; 48 opening resources and suggested quests; 52 request;
    # 56–58 hatching and restart; 62 outcome; 64–68 subsequent request.
    "lines": {"skills": (21, 23), "resources": 48, "request": 52, "hatching": (56, 58),
              "outcome": 62, "next_request": (64, 68)},
}
SOURCE_Q = {
    "title": "The Elder Kiln/Quick guide", "oldid": 5706348, "timestamp": "2012-06-03T04:51:41Z",
    "url": "https://runescape.wiki/w/index.php?title=The_Elder_Kiln%2FQuick_guide&oldid=5706348",
    "body": "sources/the-elder-kiln-quick-guide-5706348.txt",
    "sha256": "e763201d3fd9ba7b62260c7596deac2ca7a48b1bf1c4e3114a3303c99570eef5",
    # 9–11 skills; 34–38 briefing, offer and hatching. Same wiki lineage as W.
    "lines": {"skills": (9, 11), "opening": (34, 38)},
}
SOURCE_R = {
    "title": "The Elder Kiln — RuneHQ", "capture": "20120218052431", "timestamp": "2012-02-18T05:24:31Z",
    "url": "https://web.archive.org/web/20120218052431id_/http://www.runehq.com:80/quest/the-elder-kiln",
    "body": "sources/runehq-elder-kiln-20120218052431.html",
    "sha256": "e195afbf2da16711fbc3bb61cbb4d43dde63cfecc8eea547721fe3d71d432251",
    # 401–403 skills, no quest prerequisites, no starting items; 406 agreement;
    # 413/418 the explicit 100% endpoint.
    "lines": {"requirements": (401, 403), "agreement": 406, "endpoint": (413, 418)},
}
SOURCE_T = {
    "title": "Elder Kiln, The — Tip.It", "capture": "20121117012923", "timestamp": "2012-11-17T01:29:23Z",
    "url": "https://web.archive.org/web/20121117012923id_/http://www.tip.it:80/runescape/index.php?rs2quest_id=238",
    "body": "sources/tipit-20121117012923.html",
    "sha256": "baff250e99834d3e12a964d2a200a045390691244db80cf7c343d9058a9ba87b",
    # 250–260 offer, supplied runes, stronger-spell ordering, restart and the
    # memoryless Ga’al outcome.
    "lines": {"opening": (250, 260)},
}
SOURCE_D = {
    "title": "Darkan HatchEggCutscene.kt", "revision": "517bdeaaf16dbe3cbfe80ee74a91f7fbe944aaed",
    "body": "sources/darkan-HatchEggCutscene.kt.txt",
    "sha256": "4fde07c225cdac045cdec23fa6a6b5386fd2ec832cf14e0de583b7c726bf0851",
    # Modern reconstruction dates, not period evidence.
    "algorithm_commit": "b1e16caf5ceadc5780d6222b80bc561ac60daf01",
    "algorithm_date": "2024-04-18T23:19:43Z",
    "success_wait_commit": "aec071d34c8bd52f9ddbdeb36e8c8b01cfdbffa5",
    "success_wait_date": "2024-04-19T02:45:11Z",
}
SOURCE_CLIENT = {
    # Spell labels only; neither build establishes server progression or timing.
    "build_727": "2012-07-24", "build_742": "2012-11-07", "interface": 1247,
    "body": "sources/cache727-interface1247.txt",
    "sha256": "87e79878d40769f860f75811e4dc273e4abcd08dc736df7438bdd6ecf08091f6",
}
LOCAL_AUTHORITY = (
    "memory-bank/design-thread-queue.md:3199–3207",
    "sources/design-rulings.md:17–18 (R1, R2)",
    "decisions.md:1–4 (owner answer 2026-10-24)",
    "memory-bank/source-audits/elder-kiln-and-wanted-opening-boundaries-2026-10-15.md:5–7",
)
OPENING_SOURCE = f"{SOURCE_W['url']}; {SOURCE_Q['url']}"

# Entry gates (W21–23, Q9–11, R401–403) already match the structured catalog
# row; quest prerequisites stay empty (R401, round-19 qualification). Temple at
# Senntisten and TokTz-Ket-Dill are suggestions in W48, never gates.
REQUIREMENT_READOUT = ("Agility 60 (boosts do not work)", "Magic 75 (boosts do not work)", "Mining 41")

# Controls: interface 1247 labels in builds 727/742 and D142–147. Runes are
# supplied virtually (W48/W56, T252): nothing enters or leaves the inventory,
# no spellbook is checked and no Magic XP is given (W56).
SPELL_IDS = ("fire_bolt", "fire_blast", "fire_wave", "water_bolt", "water_blast", "water_wave")
SPELL_LABELS = ("Fire Bolt", "Fire Blast", "Fire Wave", "Water Bolt", "Water Blast", "Water Wave")
# PLACEHOLDER(quests.elder_kiln.spell_deltas): independent pre-cutoff evidence of each spell's heat change
SPELL_DELTAS = (5, 10, 25, -5, -10, -25)

# PLACEHOLDER(quests.elder_kiln.initial_heat): independent pre-cutoff evidence of the starting heat
INITIAL_HEAT = 0
# PLACEHOLDER(quests.elder_kiln.initial_progress): independent pre-cutoff evidence of the starting hatching percentage
INITIAL_PROGRESS = 0
# PLACEHOLDER(quests.elder_kiln.initial_band): independent pre-cutoff evidence of the starting marker position
INITIAL_BAND = 1
# Heat is a unitless gauge, not degrees.
# PLACEHOLDER(quests.elder_kiln.heat_bounds): independent pre-cutoff evidence of the gauge's limits
HEAT_BOUNDS = (0, 100)
# Inclusive on both ends; period prose says only "between" the markers.
# PLACEHOLDER(quests.elder_kiln.bands): independent pre-cutoff evidence of marker positions and inclusivity
BANDS = ((20, 40), (55, 70), (80, 90))
# Unresolved conflict: W58 says the marker gap narrows as hatching progresses,
# while D draws among fixed bands with no progress-dependent narrowing. The
# owner approved varying widths; no narrowing curve is added and the conflict
# is not historically resolved.
# PLACEHOLDER(quests.elder_kiln.progress_step): independent pre-cutoff evidence of the per-step percentage change
PROGRESS_STEP = 1
# The 100% endpoint is sourced (R413/418); it is not a placeholder.
PROGRESS_COMPLETE = 100
# PLACEHOLDER(quests.elder_kiln.cooling_step): independent pre-cutoff evidence of natural cooling per step
COOLING_STEP = 1
# Attempt-relative steps and the add-on RNG are the approved review adapter,
# not server-time parity. A draw may repeat the current band.
# PLACEHOLDER(quests.elder_kiln.marker_interval): independent pre-cutoff evidence of marker movement cadence
MARKER_INTERVAL = 20

# Mej-Ak and Mej-Jeh cast fire only, and only when the egg is below the current
# lower marker (W56–58). D's helpers fire unconditionally; that policy is
# rejected here. Projectile travel is omitted, as approved.
HELPER_IDS = ("ak", "jeh")
HELPER_NAMES = ("Mej-Ak", "Mej-Jeh")
HELPER_CALL = "Firing now!"
# PLACEHOLDER(quests.elder_kiln.helper_initial_delay): independent pre-cutoff evidence of each Mej's first-cast delay
HELPER_INITIAL_DELAY = (0, 25)
# PLACEHOLDER(quests.elder_kiln.helper_warning): independent pre-cutoff evidence of the warning-to-cast interval
HELPER_WARNING = 5
# PLACEHOLDER(quests.elder_kiln.helper_cooldown): independent pre-cutoff evidence of the interval between Mej casts
HELPER_COOLDOWN = 50
# PLACEHOLDER(quests.elder_kiln.helper_heat): independent pre-cutoff evidence of a Mej cast's heat change
HELPER_HEAT = 25

# Restart (W58, T252): once progress has become positive, falling to 0 ends
# the attempt and Retry restores the contracted defaults above; D's recoverable
# zero loop is rejected. Holding at 0 before progress first becomes positive is
# the owner-approved resolution of the initial-zero gap, not a recovered grace
# period. Closing pauses the whole attempt; nothing progresses offline.

# Copy paraphrases the identified sources; it is not a dialogue transcript.
REQUEST_COPY = (
    "TzHaar-Mej-Jeh’s egg is dying because it is too cold. The other Mejs think it is beyond help, "
    "but he believes it can survive. He asks me to help hatch it."
)
BEFORE_OFFER_COPY = (
    "Speak to TzHaar-Mej-Jeh at the Birthing Pool in north-east TzHaar City and offer to help hatch his egg."
)
AFTER_OFFER_COPY = "I have agreed to help Mej-Jeh and Mej-Ak hatch the egg."
INSTRUCTIONS_COPY = (
    "Use fire spells to warm the egg and water spells to cool it. Keep the temperature between the moving "
    "markers so the hatching percentage rises. The Mejs help with fire when it is too cold, so watch for "
    "overheating. Reach 100% to hatch the egg. If progress falls back to 0%, start again. No items or player "
    "runes are needed, and this activity gives no Magic experience."
)
EXERCISE_COPY = "The egg changes when you cast or choose to wait. Closing this window pauses your attempt."
SUCCESS_COPY = (
    "The egg has hatched as a Ga’al, without its parent’s inherited memories. "
    "Mej-Ak has taken him away toward the Fight Pits."
)
LEGACY_COPY = "This journal has no recorded hatching deed for the opening."
FAILURE_COPY = "The hatching progress fell to 0%. Start again."
STAGE_2_COPY = "Mej-Jeh wants me to retrieve Ga’al-Jeh from the Main Plaza, west of the Birthing Pool."
# Generated stage 3 opens with the hatching instruction that stage 1 now owns.
GENERATED_HATCHING_LINE = (
    "Keep the gauge within the two arrows using fire spells to heat it and water spells to cool it until it hatches."
)


def _journal_stage(row):
    if row["stage"] == 1:
        return QuestStage(1, (BEFORE_OFFER_COPY,))
    if row["stage"] == 2:
        return QuestStage(2, (STAGE_2_COPY,))
    return QuestStage(row["stage"], tuple(line for line in row["journal"] if line != GENERATED_HATCHING_LINE))


ELDER_KILN_JOURNAL_STAGES = tuple(
    _journal_stage(row)
    for quest in _CATALOG if quest["id"] == QUEST_ID
    for row in quest["journal_stages"]
)
ELDER_KILN_STAGE_CLEANUPS = (QuestStageRequirementCleanup(
    stage=1,
    remove_required_actions=("Complete The Elder Kiln stage 1 objective",),
    add_required_actions=(ELDER_KILN_HATCH_PROOF,),
    source=OPENING_SOURCE,
),)
