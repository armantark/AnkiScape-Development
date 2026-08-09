"""Period-pinned compact data for Penguin Hide and Seek."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID = "penguin_hide_and_seek"
PENGUIN_WEEK_REVIEWS = 1_680
PENGUIN_POINT_CAP = 50
PENGUIN_COINS_PER_POINT = 6_500
PENGUIN_XP_PER_LEVEL_POINT = 25

PENGUIN_HIDE_AND_SEEK_SOURCE = (
    "RuneScape Wiki Penguin Hide and Seek oldid=6569778 "
    "(2012-11-17T23:47:37Z); Penguin Hide and Seek/Spawn locations "
    "oldid=6566231 (2012-11-17T15:09:05Z)"
)


@dataclass(frozen=True)
class PenguinSpawn:
    id: str
    location: str
    disguise: str
    point_tier: int
    detail: str


# The complete 67-spawn cutoff table. Five entries from each point tier rotate
# into the answered-card week; the settled locationless model exposes the
# source location and disguise without recreating travel or area gates.
PENGUIN_ONE_POINT_SPAWNS = (
    PenguinSpawn("al_kharid_cactus", "Al Kharid", "Cactus", 1, "Near cacti southwest of Ranael's Super Skirt Store; 1 step west of northwestern cactus."),
    PenguinSpawn("barbarian_outpost_bush", "Barbarian Outpost", "Bush", 1, "North of Barbarian Assault building; 2 steps north of the northmost tree."),
    PenguinSpawn("brimhaven_bush", "Brimhaven", "Bush", 1, "Northeast of goldmine; 1 step south of the southwestern post."),
    PenguinSpawn("burthorpe_rock", "Burthorpe", "Rock", 1, "On path along fence marked above ‘Death Plateau’ on world map; 1 step north of the fence, between the 3rd and 4th rock piles."),
    PenguinSpawn("castle_wars_bush", "Castle Wars", "Bush", 1, "On the island east outside Castle Wars; 3 steps northeast and 2 steps north of the bridge."),
    PenguinSpawn("central_karamja_bush", "Central Karamja", "Bush", 1, "Near the Nature altar, on the tropical-tree spot west of ‘Karamja’ on the world map."),
    PenguinSpawn("digsite_rock", "Digsite", "Rock", 1, "Next to the first crossroad southeast of the glider; 2 steps west of the northeastern fern."),
    PenguinSpawn("draynor_manor_crate", "Draynor Manor", "Crate", 1, "Inside Draynor Manor yard, northeast of the fence entrance; 5 steps north and 2 east of the south-east fence bend."),
    PenguinSpawn("dorgesh_kaan_barrel", "Dorgesh-Kaan", "Barrel", 1, "East of the large white fern north of the lamp stall; 3 steps east of the fern's northern side."),
    PenguinSpawn("eagles_peak_bush", "Eagles' Peak", "Bush", 1, "Northwest of Eagles' Peak by the tree southwest of the boulder trap; 8 steps east from the map edge."),
    PenguinSpawn("east_karamja_bush", "East Karamja", "Bush", 1, "West of the glider fence entrance; 1 step south of the tropical tree."),
    PenguinSpawn("entrana_barrel", "Entrana", "Barrel", 1, "In Entrana's north-western corner near the seaweed; 1 step east of the south-western tree."),
    PenguinSpawn("feldip_hills_rock", "Feldip Hills", "Rock", 1, "Northwest of the quest-start icon by the three coastline humps; 5 steps north and 1 east of the dead tree."),
    PenguinSpawn("gnome_maze_bush", "Gnome Maze", "Bush", 1, "In the south-western maze; 1 step west of the eastern bench inside the T-shaped dead end."),
    PenguinSpawn("gnome_stronghold_bush", "Gnome Stronghold", "Bush", 1, "Directly west of ‘Stronghold’ on the world map beside the river; 3 steps northeast and 2 north of the willow."),
    PenguinSpawn("goblin_village_bush", "Goblin Village", "Bush", 1, "West of the generals' house; 2 steps east of the standard."),
    PenguinSpawn("ice_mountain_rock", "Ice Mountain", "Rock", 1, "Southwest of the Oracle's tent; 1 step south of the western flagpole."),
    PenguinSpawn("lighthouse_rock", "Lighthouse", "Rock", 1, "Southeast of the lighthouse beyond the bridge, beside the round pool; 1 step southeast of the northern handrail."),
    PenguinSpawn("lumber_yard_crate", "Lumber Yard", "Crate", 1, "In the centre of the Lumber Yard; 3 steps west of the east building's entrance."),
    PenguinSpawn("lumbridge_swamp_toadstool", "Lumbridge Swamp", "Toadstool", 1, "North of the Water altar and northwest of the Zanaris shed; 13 steps northwest and 2 west from the door stones."),
    PenguinSpawn("mage_training_arena_bush", "Mage Training Arena", "Bush", 1, "West of the Mage Training Arena inside the rock wall; 1 step north of the tree."),
    PenguinSpawn("mcgrubors_wood_bush", "McGrubor's Wood", "Bush", 1, "West of fairy ring A-L-S; 1 step west of the tree northeast of the vine."),
    PenguinSpawn("mining_camp_cactus", "Mining Camp", "Cactus", 1, "Northwest of the Desert Mining Camp; 5 steps northwest of the red scarf."),
    PenguinSpawn("mudskipper_point_bush", "Mudskipper Point", "Bush", 1, "Northwest of fairy ring A-I-Q beyond the palms; 6 steps east of the rock in the water."),
    PenguinSpawn("musa_point_crate", "Musa Point", "Crate", 1, "Among the trees southeast of Karamja Volcano; 5 steps northwest and 6 north of the grapple shortcut."),
    PenguinSpawn("north_ardougne_bush", "North Ardougne", "Bush", 1, "West of Ardougne's Outpost in the level-1 gnome area; 3 steps northwest and 3 north of the broken cart."),
    PenguinSpawn("observatory_crate", "Observatory", "Crate", 1, "North of the Observatory near the hill giants; 1 step west of the westernmost tree."),
    PenguinSpawn("pollnivneach_cactus", "Pollnivneach", "Cactus", 1, "At the ‘h’ in ‘Kharidian Desert’ on the world map; 3 steps north of the western bush."),
    PenguinSpawn("port_khazard_barrel", "Port Khazard", "Barrel", 1, "East of the Port Khazard store near the dock, in the centre of the four pillars."),
    PenguinSpawn("rellekka_rock", "Rellekka", "Rock", 1, "Among the rock crabs inside Rellekka; 7 steps northeast and 2 north of the sandpit."),
    PenguinSpawn("white_wolf_mountain_rock", "White Wolf Mountain", "Rock", 1, "Northeast of the Sindarpos glider; 1 step southeast of the dead tree."),
    PenguinSpawn("witchaven_rock", "Witchaven", "Rock", 1, "East of Witchaven church; 1 step northwest of the floats."),
    PenguinSpawn("wizards_tower_bush", "Wizards' Tower", "Bush", 1, "Outside the tower west of the dungeon and northwest of fairy ring D-I-S; 2 steps south and 1 east of the standing torch."),
    PenguinSpawn("zanaris_toadstool", "Zanaris", "Toadstool", 1, "Near the wall northeast of the yew tree and windmill; 1 step northwest of the oak tree."),
)

PENGUIN_TWO_POINT_SPAWNS = (
    PenguinSpawn("ape_atoll_barrel", "Ape Atoll", "Barrel", 2, "Southwest of the dungeon; 3 steps south and 1 east of the round pool."),
    PenguinSpawn("ape_atoll_bush", "Ape Atoll", "Bush", 2, "Northeast of the temple; 1 step south and 2 west of the pineapple plant."),
    PenguinSpawn("arandar_rock", "Arandar", "Rock", 2, "In the rectangular rock cluster west of the limestone mine; 2 steps south and 4 east of the large rock."),
    PenguinSpawn("castle_wars_rock", "Castle Wars", "Rock", 2, "Southwest of Castle Wars between the two lakes; 1 step west of the north-eastern achey tree."),
    PenguinSpawn("south_kbd_rock", "South KBD", "Rock", 2, "Near the western border at Wilderness level 39; 4 steps north and 3 east of the rocks east of the altar."),
    PenguinSpawn("dragontooth_isle_crate", "Dragontooth Isle", "Crate", 2, "Near the north-eastern shore east of ‘Dragontooth’ on the world map; 1 step south and 3 east of the easternmost tree."),
    PenguinSpawn("elf_camp_toadstool", "Elf Camp", "Toadstool", 2, "Southeast of the log balance to Elf Camp; 1 step east of the northernmost tree."),
    PenguinSpawn("feldip_hills_bush", "Feldip Hills", "Bush", 2, "West of the hut north of the Oo'glog shortcut; 2 steps south and 1 west of the jungle flower by the rockslide."),
    PenguinSpawn("haunted_woods_bush", "Haunted Woods", "Bush", 2, "Southeast of fairy ring A-L-Q; 4 steps south of the brown mushroom."),
    PenguinSpawn("haunted_woods_crate", "Haunted Woods", "Crate", 2, "At the first lake west of Port Phasmatys' west entrance; 2 steps south and 1 east of the hollow tree."),
    PenguinSpawn("jatizso_bush", "Jatizso", "Bush", 2, "On the second island north of Neitiznot; 1 step north of the eastern bridge to Neitiznot."),
    PenguinSpawn("jatizso_rock", "Jatizso", "Rock", 2, "West of the bridge north of Jatizso; 1 step southeast and 1 south of the rocks."),
    PenguinSpawn("jiggig_rock", "Jiggig", "Rock", 2, "Southwest of the quest-start icon at Jiggig; 1 step north of the tree."),
    PenguinSpawn("keldagrim_rock", "Keldagrim", "Rock", 2, "Northwest of Blasidar the sculptor's house; 3 steps north of the small red fungus."),
    PenguinSpawn("north_kbd_rock", "North KBD", "Rock", 2, "North of the lesser-demon pen at Wilderness level 44; 1 step north and 3 east of the northernmost rock."),
    PenguinSpawn("lava_maze_rock", "Lava Maze", "Rock", 2, "In the south-eastern Lava Maze at Wilderness level 40; 4 steps south of the long north-south lava pool."),
    PenguinSpawn("lletya_toadstool", "Lletya", "Toadstool", 2, "Just west of Lletya's entrance; 1 step south of the gap between the two trees."),
    PenguinSpawn("lunar_isle_rock", "Lunar Isle", "Rock", 2, "Northeast of town by the north coast; 10 steps south and 2 west of the easternmost windswept tree."),
    PenguinSpawn("miscellania_bush", "Miscellania", "Bush", 2, "North of the musician and northwest of the path roundabout; 1 step south and 2 east of the tree."),
    PenguinSpawn("mort_myre_bush", "Mort Myre", "Bush", 2, "Southeast of the triangular lake south of fairy ring B-K-R; 2 steps north and 7 east of the huge mushroom."),
    PenguinSpawn("mort_myre_rock", "Mort Myre", "Rock", 2, "In the Hunter area west of the southern training icon; 3 steps south and 1 east of the fungus."),
    PenguinSpawn("mort_myre_toadstool", "Mort Myre", "Toadstool", 2, "On the south-eastern edge of the River Salve lake; 2 steps north and 1 east of the small bush."),
    PenguinSpawn("mos_le_harmless_barrel", "Mos Le'Harmless", "Barrel", 2, "East of the town's east wall near the first tropical tree; 5 steps east of the plant to its southeast."),
    PenguinSpawn("nardah_cactus", "Nardah", "Cactus", 2, "North of Nardah and southeast of fairy ring D-L-Q; 3 steps northwest of the first rockslide south of the cactus."),
    PenguinSpawn("neitiznot_bush", "Neitiznot", "Bush", 2, "On the green island north of Neitiznot; 4 steps north and 2 east of the eastern woodcutting stump."),
    PenguinSpawn("neitiznot_rock", "Neitiznot", "Rock", 2, "Near the south-eastern corner of town; 2 steps north and 5 east of the log pile outside the spinning wheel."),
    PenguinSpawn("piscatoris_crate", "Piscatoris", "Crate", 2, "Among dead trees south of the Piscatoris range building; 1 step northeast of the first dead tree south of the east wall."),
    PenguinSpawn("port_phasmatys_barrel", "Port Phasmatys", "Barrel", 2, "Southwest of the southernmost market stall; 2 steps south of the tree."),
    PenguinSpawn("scorpion_pit_rock", "Scorpion Pit", "Rock", 2, "South of Scorpion Pit at Wilderness level 51; 6 steps south and 2 west of the fourth rock."),
    PenguinSpawn("inner_sophanem_cactus", "Inner Sophanem", "Cactus", 2, "Southwest of the musician; 3 steps south and 2 east of the banana tree."),
    PenguinSpawn("outer_sophanem_cactus", "Outer Sophanem", "Cactus", 2, "Outside Sophanem beside the river west of the north entrance; 4 steps north and 1 east of the yellow fence."),
    PenguinSpawn("tyras_camp_toadstool", "Tyras Camp", "Toadstool", 2, "Southwest of the catapult; 2 steps north and 7 west of the passage to Tyras Camp."),
    PenguinSpawn("wilderness_volcano_rock", "Wilderness Volcano", "Rock", 2, "Northeast of the pond south of the volcano; 6 steps north of the second tree."),
)

PENGUIN_POLAR_BEAR_LOCATIONS = (
    "Ardougne well",
    "Falador well",
    "Musa Point well",
    "Rellekka well",
    "Rimmington well",
    "Varrock well",
)


def penguin_hide_and_seek_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID: {
            "display_name": "Penguin Hide and Seek",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": PENGUIN_HIDE_AND_SEEK_SOURCE,
        }
    }


def penguin_hide_and_seek_equipment_data_as_dict() -> "dict[str, Any]":
    """Register the Ring of visibility as wearable equipment.

    Desert Treasure already grants the ring (`quest_catalog_generated.py`, item
    reward of `desert_treasure`), and the settled loop gates the three-point
    invisible penguin on a "carried or equipped" ring. But the generated
    equipment table has no row for it, so the equipped half of that gate could
    never be satisfied and the three-point penguin was an inert row.

    The generated table comes from the 2011Scape items.yml equipment blocks and
    must not be hand-edited, so the ring joins through the same per-feature seam
    that Barrows, Fish Flingers, Trouble Brewing and Castle Wars already use.

    The ring carries no combat bonuses. Its whole function in the period is to
    reveal what is otherwise invisible, which is exactly what the penguin gate
    asks of it.
    """
    from .equipment_data import EquipmentBonuses, EquipmentItem

    return {
        "Ring of visibility": EquipmentItem(
            item_name="Ring of visibility",
            slot="ring",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="ring",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=4657,
            source=(
                "https://runescape.wiki/w/Desert_Treasure?oldid=6563639"
                "; Desert Treasure item reward, worn in the ring slot"
            ),
            source_status="quest reward equipment row",
            skill_requirements=(),
            weapon_type=-1,
        ),
    }
