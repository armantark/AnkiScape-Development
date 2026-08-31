import unittest
from collections import defaultdict

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data import vinesweeper_data
from tools.audit_item_reachability import _add_vinesweeper_actions


class TestVinesweeperReachabilityAudit(unittest.TestCase):
    def test_actions_match_runtime_point_and_purchase_requirements(self):
        actions = []
        consumers = defaultdict(set)
        producers = defaultdict(set)

        _add_vinesweeper_actions(actions, consumers, producers)
        actions_by_id = {action["id"]: action for action in actions}

        operation = actions_by_id["Activity:vinesweeper:operation"]
        self.assertEqual(operation["required"], {"Spade"})
        self.assertEqual(operation["outputs"], {"Vinesweeper point"})

        inventory_rewards = {
            reward.id: reward
            for reward in vinesweeper_data.VINESWEEPER_REWARDS
            if reward.id != "flag"
        }
        buy_actions = {
            action_id.removeprefix("Activity:vinesweeper:buy:"): action
            for action_id, action in actions_by_id.items()
            if action_id.startswith("Activity:vinesweeper:buy:")
        }
        self.assertEqual(set(buy_actions), set(inventory_rewards))
        for reward_id, reward in inventory_rewards.items():
            self.assertEqual(buy_actions[reward_id]["required"], {"Vinesweeper point"})
            self.assertEqual(buy_actions[reward_id]["outputs"], {reward.item_name})

        remainders = vinesweeper_data.COMPOST_POTION_DOSES[1:] + ("Vial",)
        for current, remainder in zip(vinesweeper_data.COMPOST_POTION_DOSES, remainders):
            action = actions_by_id[f"Utility:use_compost_potion:{current}"]
            self.assertEqual(action["required"], {current, "Compost"})
            self.assertEqual(action["outputs"], {remainder, "Supercompost"})


if __name__ == "__main__":
    unittest.main()
