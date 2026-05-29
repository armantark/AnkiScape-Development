"""Pure helpers to prepare Deck Browser injection content and test idempotency.
These do not import Anki modules and can be unit-tested.
"""
from dataclasses import dataclass
from typing import Optional
import os
import base64

_ICON_DATA_URI = None

def _get_icon_data_uri() -> Optional[str]:
    global _ICON_DATA_URI
    if _ICON_DATA_URI is not None:
        return _ICON_DATA_URI
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon", "stats_icon.png")
        with open(icon_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
            _ICON_DATA_URI = f"data:image/png;base64,{b64}"
            return _ICON_DATA_URI
    except Exception:
        _ICON_DATA_URI = None
        return None

@dataclass
class DeckBrowserContent:
    # Likely present where Anki places the bottom action links (Get Shared, Create Deck, Import)
    links: Optional[str] = None
    # We avoid stats/tree to not overlap Heatmap or deck tree visually
    stats: Optional[str] = None
    tree: Optional[str] = None


def ankiscape_button_html() -> str:
    icon = _get_icon_data_uri()
    if icon:
        return (
            '<span id="ankiscape-btn-wrap" style="margin-left:8px">'
            '<a id="ankiscape-btn" href="#" title="AnkiScape" aria-label="AnkiScape" '
            'style="display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:6px; text-decoration:none; background:transparent; border:none;">'
            f'<img src="{icon}" alt="AnkiScape" style="width:24px; height:24px; display:block; filter: drop-shadow(0 1px 1px rgba(0,0,0,0.25));" />'
            '</a>'
            '</span>'
        )
    else:
        return (
            '<span id="ankiscape-btn-wrap" style="margin-left:8px">'
            '<a id="ankiscape-btn" href="#" style="padding:6px; text-decoration:none; background:transparent; border:none;" '
            'title="AnkiScape" aria-label="AnkiScape">AnkiScape</a>'
            '</span>'
        )


def inject_into_deck_browser_content(content: DeckBrowserContent) -> DeckBrowserContent:
    """Append ankiscape button HTML to the bottom links area only (idempotent).
    We intentionally avoid stats/tree to prevent overlap with Heatmap or deck list.
    """
    if content.links is not None and "ankiscape-btn" not in content.links:
        content.links = (content.links or "") + ankiscape_button_html()
        return content
    return content
