import json
import tempfile
import unittest
from pathlib import Path

from tools.memory_bank_queue_packet import MIN_MAX_BYTES, PacketError, build_packet


class MemoryBankQueuePacketTest(unittest.TestCase):
    def _root(self, parent: Path, name: str, marker: str = "alpha") -> Path:
        root = parent / name
        memory_bank = root / "memory-bank"
        memory_bank.mkdir(parents=True)
        (memory_bank / "activeContext.md").write_text(
            "# Active Context\n\n"
            f"## Newest {marker}\n"
            f"Current {marker} state.\n\n"
            "## Previous state\n"
            "Older state.\n\n"
            "## Historical state\n"
            "Oldest state.\n",
            encoding="utf-8",
        )
        (memory_bank / "progress.md").write_text(
            "# Progress\n\n"
            f"## Latest {marker}\n"
            "Latest ledger entry.\n\n"
            "## Prior ledger entry\n"
            "Prior entry.\n",
            encoding="utf-8",
        )
        (memory_bank / "loop-queue.md").write_text(
            "# Queue\n\n"
            "Status: live queue.\n\n"
            "1. [x] Finished.\n"
            f"2. [ ] Select {marker}.\n"
            "   First context line.\n"
            "   Second context line.\n"
            "3. [ ] Wait for source.\n",
            encoding="utf-8",
        )
        (memory_bank / "future-work-kanban.md").write_text(
            "# Kanban\n\n"
            "Status: live board.\n\n"
            "## Now\n\n"
            "Labels: `IMPLEMENT`.\n",
            encoding="utf-8",
        )
        (memory_bank / "design-thread-queue.md").write_text(
            "# Design queue\n\nStatus: live queue.\n- Blocks: owner choice.\n",
            encoding="utf-8",
        )
        (memory_bank / "gpt-deferred-queue.md").write_text(
            "# Deferred queue\n\nStatus: live queue.\n",
            encoding="utf-8",
        )
        (memory_bank / "gap-backlog.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "id": f"{marker}-blocked",
                            "skill": "Runecrafting",
                            "title": f"Source {marker}",
                            "status": "design_settled_waiting_source",
                            "note": "Exact blocker remains.",
                        },
                        {
                            "id": f"{marker}-done",
                            "skill": "Crafting",
                            "title": "Done",
                            "status": "merged",
                            "note": "Closed.",
                        },
                    ]
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (memory_bank / "papercuts.md").write_text(
            "# Papercuts\n\n"
            + "\n".join(
                f"- 2026-08-{20 - index:02d}T00:00:00-07:00 — papercut {marker} {index}"
                for index in range(10)
            )
            + "\n",
            encoding="utf-8",
        )
        return root

    def test_output_is_deterministic_and_line_numbered(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")
            memory_bank = root / "memory-bank"
            before = {
                path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                for path in memory_bank.iterdir()
            }

            first = build_packet([root])
            second = build_packet([root])
            after = {
                path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                for path in memory_bank.iterdir()
            }

        self.assertEqual(first, second)
        self.assertEqual(before, after)
        self.assertIn("root[1]/memory-bank/activeContext.md:3: ## Newest alpha", first)
        self.assertIn("root[1]/memory-bank/loop-queue.md:6: 2. [ ] Select alpha.", first)
        self.assertIn("root[1]/memory-bank/future-work-kanban.md:7: Labels: `IMPLEMENT`.", first)
        self.assertIn("root[1]/memory-bank/design-thread-queue.md:4: - Blocks: owner choice.", first)
        self.assertIn('root[1]/memory-bank/gap-backlog.json:4:       "id": "alpha-blocked",', first)
        self.assertNotIn("alpha-done", first)

    def test_empty_match_sources_are_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")
            memory_bank = root / "memory-bank"
            queue_names = (
                "future-work-kanban.md",
                "design-thread-queue.md",
                "gpt-deferred-queue.md",
                "loop-queue.md",
                "newly-discovered-queue.md",
            )
            for name in queue_names:
                (memory_bank / name).write_text("# Queue\n\nNo selected entries.\n", encoding="utf-8")
            (memory_bank / "gap-backlog.json").write_text(
                json.dumps({"items": [{"id": "done", "status": "merged"}]}, indent=2) + "\n",
                encoding="utf-8",
            )
            (memory_bank / "papercuts.md").write_text(
                "# Papercuts\n\nNo matching entries.\n",
                encoding="utf-8",
            )

            packet = build_packet([root])

        queue_notice = (
            "no unchecked entries or blocker/class labels matched the queue packet vocabulary"
        )
        for name in queue_names:
            self.assertIn(f"root[1]/memory-bank/{name} — {queue_notice}", packet)
        self.assertIn(
            "root[1]/memory-bank/gap-backlog.json — "
            "no non-closed backlog items matched the queue packet vocabulary",
            packet,
        )
        self.assertIn(
            "root[1]/memory-bank/papercuts.md — "
            "no papercut entries matched the queue packet vocabulary",
            packet,
        )
        self.assertNotIn("\n- none\n", packet)

    def test_backlog_item_boundaries_do_not_depend_on_id_key_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")
            path = root / "memory-bank" / "gap-backlog.json"
            path.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "title": "Active title before id",
                                "status": "waiting_on_source",
                                "id": "active-late-id",
                                "note": "Active note.",
                            },
                            {
                                "title": "Closed title before id",
                                "status": "merged",
                                "id": "closed-late-id",
                                "note": "Closed note.",
                            },
                        ]
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            packet = build_packet([root])

        self.assertIn(
            'root[1]/memory-bank/gap-backlog.json:4:       "title": "Active title before id",',
            packet,
        )
        self.assertIn(
            'root[1]/memory-bank/gap-backlog.json:6:       "id": "active-late-id",',
            packet,
        )
        self.assertNotIn("Closed title before id", packet)
        self.assertNotIn("closed-late-id", packet)

    def test_minified_backlog_line_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")
            path = root / "memory-bank" / "gap-backlog.json"
            path.write_text(
                json.dumps({"items": [{"id": f"item-{index}", "status": "open"} for index in range(3)]})
                + "\n",
                encoding="utf-8",
            )

            packet = build_packet([root])

        self.assertEqual(packet.count("root[1]/memory-bank/gap-backlog.json:1:"), 1)

    def test_multiple_roots_keep_separate_references(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            first_root = self._root(parent, "one", "alpha")
            second_root = self._root(parent, "two", "beta")

            packet = build_packet([first_root, second_root])

        self.assertIn("root[1]/memory-bank/activeContext.md:3: ## Newest alpha", packet)
        self.assertIn("root[2]/memory-bank/activeContext.md:3: ## Newest beta", packet)
        self.assertIn(f"- root[1]: {first_root.resolve()}", packet)
        self.assertIn(f"- root[2]: {second_root.resolve()}", packet)

    def test_byte_cap_reports_each_omitted_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")
            long_line = "x" * 1500
            path = root / "memory-bank" / "papercuts.md"
            path.write_text(
                "# Papercuts\n\n"
                + "\n".join(f"- 2026-08-20T00:00:00-07:00 — {long_line}" for _ in range(8))
                + "\n",
                encoding="utf-8",
            )

            packet = build_packet([root], max_bytes=2200)

        self.assertLessEqual(len(packet.encode("utf-8")), 2200)
        self.assertIn("## Omissions and truncations", packet)
        self.assertIn("root[1]/memory-bank/papercuts.md — omitted because the 2200-byte cap was reached", packet)

    def test_intrinsic_limits_report_truncated_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._root(Path(temp_dir), "one")

            packet = build_packet([root])

        self.assertIn(
            "root[1]/memory-bank/activeContext.md — kept first 2 of 3 top-level sections",
            packet,
        )
        self.assertIn(
            "root[1]/memory-bank/papercuts.md — kept first 8 of 10 papercuts",
            packet,
        )

    def test_invalid_inputs_fail_loudly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            root = self._root(parent, "one")
            missing = parent / "missing"
            incomplete = parent / "incomplete"
            (incomplete / "memory-bank").mkdir(parents=True)

            with self.subTest("missing root"), self.assertRaisesRegex(PacketError, "invalid root"):
                build_packet([missing])
            with self.subTest("missing sources"), self.assertRaisesRegex(PacketError, "missing required"):
                build_packet([incomplete])
            with self.subTest("duplicate root"), self.assertRaisesRegex(PacketError, "duplicate root"):
                build_packet([root, root])
            with self.subTest("undersized cap"), self.assertRaisesRegex(PacketError, "at least"):
                build_packet([root], max_bytes=MIN_MAX_BYTES - 1)
            memory_bank = root / "memory-bank"
            for index in range(12):
                (memory_bank / f"{index:02d}-{'q' * 100}-queue.md").write_text(
                    "# Queue\n\nStatus: open.\n",
                    encoding="utf-8",
                )
            with self.subTest("truthful packet cannot fit"), self.assertRaisesRegex(
                PacketError,
                "cannot fit the packet header and omission report",
            ):
                build_packet([root], max_bytes=MIN_MAX_BYTES)

    def test_malformed_backlog_shapes_fail_closed(self):
        cases = (
            ("invalid JSON", "not json\n", "invalid JSON"),
            ("missing items list", json.dumps({}) + "\n", "must contain an 'items' list"),
            (
                "non-object item",
                json.dumps({"items": ["not an object"]}) + "\n",
                "non-object backlog item",
            ),
            (
                "missing required field",
                json.dumps({"items": [{"id": "missing-status"}]}) + "\n",
                "require non-empty string 'id' and 'status'",
            ),
            (
                "duplicate ids",
                json.dumps(
                    {
                        "items": [
                            {"id": "repeated", "status": "open"},
                            {"id": "repeated", "status": "blocked"},
                        ]
                    }
                )
                + "\n",
                "duplicate backlog id 'repeated'",
            ),
            (
                "ambiguous active field",
                '{"items": [{"id": "first", "id": "second", "status": "open"}]}\n',
                "duplicate 'id' field",
            ),
        )
        for name, backlog, error in cases:
            with self.subTest(name), tempfile.TemporaryDirectory() as temp_dir:
                root = self._root(Path(temp_dir), "one")
                (root / "memory-bank" / "gap-backlog.json").write_text(
                    backlog,
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(PacketError, error):
                    build_packet([root])


if __name__ == "__main__":
    unittest.main()
