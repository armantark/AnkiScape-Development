"""Treasure Trails catalog, persistence and review regressions.

Shared literal search cases; importing this module loads no product code."""

SEARCH_ROWS = (
    ("simple_hemenster_crate", "Search for a crate in a building in Hemenster."),
    ("simple_seers_village_ground_floor_crate", "Search for a crate on the ground floor of a house in Seers' Village."),
    ("simple_varrock_south_entrance_boxes", "Search the boxes in the house near the South entrance of Varrock."),
    ("simple_east_ardougne_armour_shop_boxes", "Search the boxes just outside the Armour shop in east Ardougne."),
    ("simple_camelot_left_tower_chest", "Search the chest in the left-hand tower of Camelot castle."),
    ("simple_dwarven_mine_chests", "Search the chests in the Dwarven Mine."),
    ("simple_port_khazard_cart_crate", "Search the crate near a cart in Port Khazard."),
)


def finite_draws(values):
    """Unexpected generation/reward draws fail instead of silently repeating."""
    stream = iter(values)
    return lambda: next(stream)
