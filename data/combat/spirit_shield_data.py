"""Period wield requirements over the retained generated equipment block."""

from dataclasses import replace

from ..equipment_data import EQUIPMENT_DATA


SPIRIT_SHIELD_WIELD_SOURCE = (
    "https://runescape.wiki/w/index.php?title=Spirit_shield&oldid=5197774; "
    "https://web.archive.org/web/20120904064334id_/http://www.tip.it:80/runescape/?page=prayer_guide.htm"
)


def spirit_shield_equipment_data_as_dict():
    """Return a fresh overlay without modifying the generated record."""
    return {
        'Spirit shield': replace(
            EQUIPMENT_DATA['Spirit shield'],
            required_level=40,
            skill_requirements=(('defense', 40), ('prayer', 55)),
            source=f"{EQUIPMENT_DATA['Spirit shield'].source}; {SPIRIT_SHIELD_WIELD_SOURCE}",
        ),
    }
