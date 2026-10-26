"""Shared real-plant, owned-supply and collection fixtures for Habitat tests."""

import copy
import json

import pkg_alias  # noqa: F401
from ankiscape.logic import farming_logic as farm

TARGET = "track_shadow_jadinko"
PATCH = "habitat_vine_flower"


def ready_shadow_habitat(target):
    if target != "track_shadow_jadinko":
        return {}
    record = farm.default_farming_state_pure()["farm_patches"]["habitat_vine_flower"]
    record.update(crop_id="red_blossom", last_crop_id="red_blossom")
    return {"habitat_feature": "abandoned_house", "farm_patches": {"habitat_vine_flower": record}}


def setup_state():
    return {
        **farm.default_farming_state_pure(),
        "inventory": {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Noose wand": 1, "Red blossom seed": 1, "Coins": 100000},
        "hunter_level": 71, "farming_level": 54, "construction_level": 57,
        "farming_exp": 0.0, "construction_exp": 0.0,
    }


def established_state(**record):
    data = setup_state()
    data.update(ready_shadow_habitat(TARGET))
    data["farm_patches"][PATCH].update(record)
    return data


class CollectionFacade:
    def __init__(self):
        self.values = {}

    def get_config(self, key, default=None):
        return copy.deepcopy(self.values.get(key, default))

    def set_config(self, key, value):
        self.values[key] = json.loads(json.dumps(value))

    def remove_config(self, key):
        self.values.pop(key, None)

