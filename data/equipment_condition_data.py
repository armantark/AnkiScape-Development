"""Shared condition families for every degradable equipment subsystem."""

try:
    from .barrows_data import BARROWS_CONDITION_DATA
    from .fist_of_guthix_data import FIST_OF_GUTHIX_CONDITION_DATA
except ImportError:  # pragma: no cover - flat test imports
    from barrows_data import BARROWS_CONDITION_DATA  # type: ignore
    from fist_of_guthix_data import FIST_OF_GUTHIX_CONDITION_DATA  # type: ignore


EQUIPMENT_CONDITION_DATA = {
    **FIST_OF_GUTHIX_CONDITION_DATA,
    **{f"barrows_{key}": value for key, value in BARROWS_CONDITION_DATA.items()},
}
