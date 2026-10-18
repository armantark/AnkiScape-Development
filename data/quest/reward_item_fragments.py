from __future__ import annotations

from .dependencies import *
from .sources import *

_BAR_CRAWL_FRAGMENT = {
        "Barcrawl card": {
            "category": "tool",
            "item_id": 455,
            "model_id": 2430,
            "client_options": ("Read", "Drop"),
            "source": BAR_CRAWL_HARVEST_SOURCE,
        },
}

_COINS_FRAGMENT = {
        "Coins": {"category": "material", "source": "RuneScape currency"},
}

_LET_THEM_EAT_PIE_FRAGMENT = {
        "Expensive spices": {
            "category": "material",
            "item_id": 23081,
            "stackable": False,
            "tradeable": False,
            "source": LET_THEM_EAT_PIE_SPICES_SOURCE,
        },
}

_EAGLES_PEAK_FRAGMENT = {
        # A real holdable, non-stackable, tradeable item (rev-742 item 10132)
        # obtained later by hunting rabbits; Eagles' Peak itself puts the ferret
        # in the zoo rather than awarding this, so it stays defined but
        # ungranted by any quest.
        "Strung rabbit foot": {
            "category": "material",
            "item_id": 10132,
            "stackable": False,
            "tradeable": True,
            "source": (
                "https://runescape.wiki/w/Eagles%27_Peak?oldid=6579761 "
                "(reward text: string a rabbit's foot with ball of wool); "
                "OpenRS2 rev-742 item definition 10132"
            ),
        },
}

_RATCATCHERS_FRAGMENT = {
    "Rat pole": {
        "category": "equipment",
        "item_id": 6773,
        "stackable": False,
        "tradeable": False,
        "source": "https://runescape.wiki/w/Rat_pole?oldid=5671031",
    },
}

__all__: tuple[str, ...] = ()
