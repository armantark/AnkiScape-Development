import unittest
from deck_injection_pure import DeckBrowserContent, inject_into_deck_browser_content

class DummyContent:
    def __init__(self, links=None, stats=None, tree=None):
        self.links = links
        self.stats = stats
        self.tree = tree

class TestDeckBrowserHookContract(unittest.TestCase):
    def test_pure_injection_contract_links_only(self):
        # Simulate Anki's content object with links present
        content = DummyContent(links="<div>links</div>")
        dbc = DeckBrowserContent(links=content.links, stats=content.stats, tree=content.tree)
        out = inject_into_deck_browser_content(dbc)
        # Apply back to simulated content (mirrors __init__ logic)
        if hasattr(content, 'links'):
            content.links = out.links
        # Button appears in links and not in stats/tree
        self.assertIn("ankiscape-btn", content.links)
        self.assertIsNone(content.stats)
        self.assertIsNone(content.tree)

if __name__ == "__main__":
    unittest.main()
