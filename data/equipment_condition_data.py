"""Shared condition families for every degradable equipment subsystem."""

from .barrows_data import BARROWS_CONDITION_DATA
from .brawling_gloves_data import brawling_gloves_condition_data_as_dict
from .fist_of_guthix_data import FIST_OF_GUTHIX_CONDITION_DATA


EQUIPMENT_CONDITION_DATA = {
    **FIST_OF_GUTHIX_CONDITION_DATA,
    **{f"barrows_{key}": value for key, value in BARROWS_CONDITION_DATA.items()},
    **brawling_gloves_condition_data_as_dict(),
}
