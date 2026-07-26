from __future__ import annotations

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.help_system import (
    HELP_HOME_ID,
    KNOWN_REGISTRY_BLOCK_IDS,
    PRIMARY_HELP_TOPIC_BY_TAB_LABEL,
    HelpRegistryTable,
    HELP_TOPICS_DIR,
    load_help_topics,
    parse_help_topic_text,
    render_help_topic_html,
    resolve_help_topic,
    search_help_topics,
    topics_by_id,
    validate_help_topics,
)


def _topic(
    help_id: str,
    *,
    title: str | None = None,
    surface: str | None = None,
    aliases: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    related: tuple[str, ...] = (),
    body: str = "",
):
    import json

    metadata = {
        "help_id": help_id,
        "title": title or help_id.replace("-", " ").title(),
        "surface": surface or help_id,
        "aliases": list(aliases),
        "tags": list(tags),
        "related": list(related),
    }
    return parse_help_topic_text(
        "---\n" + json.dumps(metadata) + "\n---\n" + body,
        source_name=f"{help_id}.md",
    )


class HelpCorpusTests(unittest.TestCase):
    def test_shipping_corpus_covers_every_primary_page_and_live_block(self) -> None:
        topics = load_help_topics()
        by_id = topics_by_id(topics)

        # Derived, not hardcoded: a new topic file must be loaded, and a
        # loader that silently drops one must fail here.
        self.assertEqual(
            len(topics), len(list(HELP_TOPICS_DIR.glob("*.md")))
        )
        self.assertEqual(
            set(PRIMARY_HELP_TOPIC_BY_TAB_LABEL.values()),
            {
                topic.help_id
                for topic in topics
                if topic.help_id in PRIMARY_HELP_TOPIC_BY_TAB_LABEL.values()
            },
        )
        self.assertEqual(by_id[HELP_HOME_ID].title, "Using AnkiScape")
        self.assertEqual(by_id["skills"].registry_blocks, ("implemented_skills",))

    def test_search_matches_alias_heading_and_body_with_and_tokens(self) -> None:
        topics = (
            _topic(
                "home",
                title="Home",
                aliases=("starter guide",),
                tags=("basics",),
                body="## First steps\nChoose a training target.",
            ),
            _topic(
                "bank",
                title="Bank",
                aliases=("inventory",),
                body="## Claims\nRecover items and Coins.",
            ),
        )

        self.assertEqual(
            [topic.help_id for topic in search_help_topics(topics, "starter")],
            ["home"],
        )
        self.assertEqual(
            [topic.help_id for topic in search_help_topics(topics, "claims coins")],
            ["bank"],
        )
        self.assertEqual(search_help_topics(topics, "training coins"), ())

    def test_validation_reports_links_anchors_relations_and_registry_blocks(self) -> None:
        home = _topic(
            "home",
            related=("missing-related",),
            body=(
                "## Existing {#existing}\n"
                "[Missing topic](help:missing-topic)\n"
                "[Missing anchor](help:page#absent)\n"
                "{{registry:not_a_registry}}"
            ),
        )
        page = _topic("page", body="## Present {#present}\nText.")

        issues = validate_help_topics(
            (home, page),
            known_registry_blocks=KNOWN_REGISTRY_BLOCK_IDS,
        )

        self.assertTrue(any("unknown related topic 'missing-related'" in issue for issue in issues))
        self.assertTrue(any("unknown help link 'missing-topic'" in issue for issue in issues))
        self.assertTrue(any("unknown anchor 'page'#absent" in issue for issue in issues))
        self.assertTrue(any("unknown registry block 'not_a_registry'" in issue for issue in issues))

    def test_missing_reference_is_visible_in_development_and_home_in_production(self) -> None:
        home = _topic("home", body="## Welcome {#welcome}\nText.")
        by_id = {"home": home}

        topic, anchor = resolve_help_topic(by_id, "help:missing#section")
        self.assertIs(topic, home)
        self.assertEqual(anchor, "")
        with self.assertRaisesRegex(KeyError, "Unknown help topic"):
            resolve_help_topic(by_id, "missing", developer_mode=True)
        with self.assertRaisesRegex(KeyError, "Unknown help anchor"):
            resolve_help_topic(by_id, "home#missing", developer_mode=True)

    def test_renderer_emits_safe_anchors_internal_links_and_registry_rows(self) -> None:
        topic = _topic(
            "home",
            body=(
                "## Live skills {#live-skills}\n"
                "Use **gear** and `Coins < 5` with [Bank](help:bank).\n\n"
                "{{registry:implemented_skills}}\n\n"
                "<script>not executable</script>"
            ),
        )
        html = render_help_topic_html(
            topic,
            registry_tables={
                "implemented_skills": HelpRegistryTable(
                    headers=("Skill", "Group"),
                    rows=(("Mining", "Gathering"),),
                )
            },
        )

        self.assertIn('<h2 id="live-skills">Live skills</h2>', html)
        self.assertIn('<a href="help:bank">Bank</a>', html)
        self.assertIn("<strong>gear</strong>", html)
        self.assertIn("<code>Coins &lt; 5</code>", html)
        self.assertIn("<td>Mining</td>", html)
        self.assertIn("&lt;script&gt;not executable&lt;/script&gt;", html)


if __name__ == "__main__":
    unittest.main()
