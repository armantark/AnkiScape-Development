"""Shared Hunter image ownership used by the registry and asset fetcher."""

import os

from .paths import FARMING_ITEMS_FOLDER, FLETCHED_ITEMS_FOLDER, SHOP_ITEMS_FOLDER


HUNTER_SHARED_ITEM_IMAGES = {
    "Marasamaw plant": os.path.join(SHOP_ITEMS_FOLDER, "marasamaw_plant.png"),
    "Wimpy feather": os.path.join(SHOP_ITEMS_FOLDER, "wimpy_feather.png"),
    "Raw beast meat": os.path.join(SHOP_ITEMS_FOLDER, "raw_beast_meat.png"),
    "Polar kebbit fur": os.path.join(SHOP_ITEMS_FOLDER, "polar_kebbit_fur.png"),
    "Long kebbit spike": os.path.join(
        FLETCHED_ITEMS_FOLDER, "long_kebbit_spike.png"
    ),
    "Erzille seed": os.path.join(FARMING_ITEMS_FOLDER, "erzille_seed.png"),
    "Argway seed": os.path.join(FARMING_ITEMS_FOLDER, "argway_seed.png"),
    "Ugune seed": os.path.join(FARMING_ITEMS_FOLDER, "ugune_seed.png"),
    "Shengo seed": os.path.join(FARMING_ITEMS_FOLDER, "shengo_seed.png"),
    "Samaden seed": os.path.join(FARMING_ITEMS_FOLDER, "samaden_seed.png"),
}
