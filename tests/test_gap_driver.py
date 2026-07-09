import unittest

from tools.gap_driver import _active_skills, pick_next


def _item(iid, skill, status, *, worktree=None, rank=1, depends_on=None):
    item = {
        "id": iid,
        "rank": rank,
        "skill": skill,
        "root_cause": "transcription",
        "status": status,
    }
    if worktree is not None:
        item["worktree"] = worktree
    if depends_on is not None:
        item["depends_on"] = depends_on
    return item


class GapDriverSchedulingTests(unittest.TestCase):
    def test_unresolved_worktree_locks_its_skill_after_failure(self):
        data = {
            "items": [
                _item("craft-a", "Crafting", "review_failed", worktree="/tmp/craft-a"),
                _item("craft-b", "Crafting", "pending", rank=2),
                _item("fish-a", "Fishing", "pending", rank=3),
            ]
        }

        self.assertEqual(_active_skills(data), {"Crafting"})
        self.assertEqual(pick_next(data)["id"], "fish-a")

    def test_independent_skills_can_overlap(self):
        data = {
            "items": [
                _item("craft-a", "Crafting", "reviewing", worktree="/tmp/craft-a"),
                _item("mine-a", "Mining", "pending", rank=2),
            ]
        }

        self.assertEqual(pick_next(data)["id"], "mine-a")

    def test_merged_worktree_path_does_not_keep_skill_locked(self):
        data = {
            "items": [
                _item("craft-a", "Crafting", "merged", worktree="/tmp/craft-a"),
                _item("craft-b", "Crafting", "pending", rank=2),
            ]
        }

        self.assertEqual(_active_skills(data), set())
        self.assertEqual(pick_next(data)["id"], "craft-b")

    def test_dependency_must_be_merged_before_launch(self):
        data = {
            "items": [
                _item("craft-a", "Crafting", "reviewing", worktree="/tmp/craft-a"),
                _item("fish-a", "Fishing", "pending", rank=2, depends_on=["craft-a"]),
                _item("mine-a", "Mining", "pending", rank=3),
            ]
        }

        self.assertEqual(pick_next(data)["id"], "mine-a")


if __name__ == "__main__":
    unittest.main()
