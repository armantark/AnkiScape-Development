"""Pinned pre-EOC Court Cases representative catalog."""

from __future__ import annotations

from typing import Any


COURT_CASES_ACTIVITY_ID = "court_cases"
COURT_CASES_BATCH2_COOLDOWN_DAYS = 14
COURT_CASES_SOURCE = (
    "RuneScape Wiki Court Cases oldid=6202025 (2012-09-06T03:11:19Z); "
    "Mugger v. Roger Murray oldid=6130755 (2012-08-23T17:59:01Z); "
    "River troll v. The People oldid=6134988 (2012-08-24T09:50:53Z); "
    "Party Pete v. His Neighbours oldid=6447758 (2012-10-20T23:34:14Z); "
    "Court summons oldid=6476690 (2012-10-26T16:05:53Z)"
)

COURT_ROLE_LABELS = {
    "prosecution": "Prosecute",
    "defence": "Defend",
}


def _step(
    kind: str,
    subject: str,
    prosecution: str,
    defence: str,
) -> dict[str, str]:
    return {
        "kind": kind,
        "subject": subject,
        "prosecution": prosecution,
        "defence": defence,
    }


# This two-case horizontal catalog is deliberately complete enough to exercise
# the family: the free starter, summons entry, fingerprint/no-fingerprint
# preparation, both legal roles, evidence, witnesses, jury appeal, retry, XP,
# and an item reward. The other fourteen cases are catalog depth, not mechanics.
COURT_CASES: dict[str, dict[str, Any]] = {
    "mugger": {
        "display_name": "Mugger v. Roger Murray",
        "summary": "The Mugger is accused of beating Roger Murray and stealing his winnings.",
        "starter": True,
        "batch": 1,
        "case_reports": 3,
        "fingerprint": True,
        "xp": 2000.0,
        "rewards": {},
        "trial_steps": (
            _step(
                "Evidence",
                "Fingerprint",
                "Present the matched fingerprint.",
                "Present the matched fingerprint.",
            ),
            _step(
                "Evidence",
                "Nightstick",
                "The nightstick was found on the accused.",
                "This nightstick was found on my client.",
            ),
            _step(
                "Evidence",
                "Facemask",
                "The accused was wearing this mask when he was arrested.",
                "It isn't a crime to wear a facemask.",
            ),
            _step(
                "Witness",
                "First witness",
                "Call the arresting officer about the Nightstick.",
                "Call the victim about the Attack.",
            ),
            _step(
                "Witness",
                "Second witness",
                "Call the victim about the Nightstick.",
                "Call the arresting officer about the Victim.",
            ),
            _step(
                "Closing",
                "Jury appeal",
                "Address the elderly gentleman.",
                "Address the shady gentleman.",
            ),
        ),
    },
    "river_troll": {
        "display_name": "River troll v. The People",
        "summary": "The River troll is accused of littering on Catherby's beach.",
        "starter": False,
        "batch": 1,
        "case_reports": 2,
        "fingerprint": False,
        "xp": 3500.0,
        "rewards": {"Shark": 20},
        "trial_steps": (
            _step(
                "Evidence",
                "Raw fish",
                "This was one of several fish found at the scene of the crime.",
                "The accused was found eating this fish.",
            ),
            _step(
                "Evidence",
                "Spinach roll",
                "These were found next to the suspect.",
                "This is not a common food for trolls.",
            ),
            _step(
                "Evidence",
                "Half-key",
                "This is yet more junk dropped on the beach.",
                "This was found next to the river troll.",
            ),
            _step(
                "Witness",
                "First witness",
                "Call the river troll about Littering.",
                "Call the arresting officer about the Arrest.",
            ),
            _step(
                "Witness",
                "Second witness",
                "Call the arresting officer about Catherby.",
                "Call the river troll about Catherby.",
            ),
            _step(
                "Closing",
                "Jury appeal",
                "Address the young woman.",
                "Address the barbarian.",
            ),
        ),
    },
    "party_pete": {
        "display_name": "Party Pete v. His Neighbours",
        "summary": "Party Pete is accused of making noise above the legal limit.",
        "starter": False,
        "batch": 2,
        "case_reports": 2,
        "fingerprint": True,
        "preparation_steps": (
            "Read case report 1",
            "Read case report 2",
            "Interview Ikis Krum",
            "Interview Party Pete",
            "Interview Megan",
            "Inspect the Party Room crime scene",
            {
                "prosecution": "Measure the Party Room noise with the Bat-in-a-box",
                "defence": "Measure the noise beside Ikis Krum with the Bat-in-a-box",
            },
            "Inspect the magical amplifier",
            "Match Ikis Krum's fingerprint",
        ),
        "xp": 9000.0,
        "rewards": {"Rainbow afro": 1},
        "trial_steps_by_role": {
            "prosecution": (
                _step(
                    "Evidence",
                    "Magical amplifier",
                    "The volume was turned up to maximum.",
                    "The volume was turned up to maximum.",
                ),
                _step(
                    "Evidence",
                    "Bat-in-a-box",
                    "This tool showed sound levels to be too high.",
                    "This tool showed sound levels to be too high.",
                ),
                _step("Witness", "Ikis Krum", "Ask about the noise.", "Ask about the noise."),
                _step("Witness", "Party Pete", "Ask about the noise.", "Ask about the noise."),
                _step("Witness", "Megan", "Ask about the noise.", "Ask about the noise."),
                _step(
                    "Closing",
                    "Jury appeal",
                    "Address the elderly citizen.",
                    "Address the elderly citizen.",
                ),
            ),
            "defence": (
                _step(
                    "Evidence",
                    "Fingerprint",
                    "Present Ikis Krum's matched fingerprint.",
                    "Present Ikis Krum's matched fingerprint.",
                ),
                _step(
                    "Evidence",
                    "Bat-in-a-box",
                    "This shows the sound levels to be at normal level.",
                    "This shows the sound levels to be at normal level.",
                ),
                _step(
                    "Evidence",
                    "Magical amplifier",
                    "Ikis Krum's fingerprint was on it.",
                    "Ikis Krum's fingerprint was on it.",
                ),
                _step(
                    "Witness",
                    "Party Pete",
                    "Ask about your neighbour.",
                    "Ask about your neighbour.",
                ),
                _step(
                    "Closing",
                    "Jury appeal",
                    "Address the young man.",
                    "Address the young man.",
                ),
            ),
        },
    },
}

COURT_CASE_ORDER = tuple(COURT_CASES)


def court_cases_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        COURT_CASES_ACTIVITY_ID: {
            "display_name": "Court Cases",
            "requirements": {},
            "outputs": ("Shark", "Rainbow afro"),
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": COURT_CASES_SOURCE,
        }
    }


def court_cases_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        "Court summons": {
            "category": "material",
            "source_item_id": 18757,
            "stackable": False,
            "tradeable": False,
            "source": COURT_CASES_SOURCE,
        },
        "Rainbow afro": {
            "category": "equipment",
            "source_item_id": 19747,
            "stackable": False,
            "tradeable": True,
            "equipment_slot": "head",
            "source": (
                f"{COURT_CASES_SOURCE}; data/cfg/items.yml item 19747"
            ),
        },
    }
