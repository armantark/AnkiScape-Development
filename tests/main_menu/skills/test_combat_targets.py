from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_line_edit,
    _find_tree_with_user_role,
    _make_player_data,
    _tree_items,
    _tree_row,
    patch,
    re,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QAbstractItemView, QApplication, QColor, QEvent, QListWidget, QPoint, QTreeWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_combat_is_selectable_and_shows_simple_enemy_targets(self) -> None:
        from ankiscape.data.combat_data import COMBAT_ENEMY_DATA

        pd = _make_player_data()
        pd["combat_examined_monsters"] = list(COMBAT_ENEMY_DATA)
        pd["inventory"]["Waterskin (4)"] = 1
        pd["current_combat_target"] = "seagull"
        pd["slayer_level"] = 65
        pd["equipment"]["head"] = "Face mask"
        pd["equipment"]["shield"] = "Lit bug lantern"
        pd["equipment"]["feet"] = "Insulated boots"
        pd["quests"]["ernest_the_chicken"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["royal_trouble"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["olafs_quest"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["inventory"]["Spade"] = 1
        pd["quests"]["death_to_the_dorgeshuun"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["inventory"]["Slayer bell"] = 1
        pd["inventory"]["Lit torch"] = 1
        pd["equipment"]["weapon"] = "Leaf-bladed spear"
        pd["quests"]["priest_in_peril"] = {
            "started": True,
            "progress": 9,
            "completed": True,
        }
        pd["quests"]["lost_city"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["cabin_fever"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["legends_quest"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        pd["quests"]["regicide"] = {
            "started": True,
            "progress": 1,
            "completed": True,
        }
        dialog = self._open(pd, current_skill="Combat")

        tree = _find_tree_with_user_role(dialog, "seagull")
        cow_calf = _tree_row(tree, "cow_calf")
        ram = _tree_row(tree, "ram")
        spider = _tree_row(tree, "spider")
        giant_spider = _tree_row(tree, "giant_spider")
        goblin_unarmed = _tree_row(tree, "goblin_level_2_unarmed")
        goblin_armed = _tree_row(tree, "goblin_level_2_armed")
        goblin_level_11 = _tree_row(tree, "goblin_level_11")
        farmer = _tree_row(tree, "farmer")
        highwayman = _tree_row(tree, "highwayman")
        barbarian_level_10 = _tree_row(tree, "barbarian_level_10")
        ogre = _tree_row(tree, "ogre")
        jackal = _tree_row(tree, "jackal")
        goat = _tree_row(tree, "goat")
        icefiend = _tree_row(tree, "icefiend")
        pyrefiend = _tree_row(tree, "pyrefiend")
        jelly = _tree_row(tree, "jelly")
        bloodveld = _tree_row(tree, "bloodveld")
        infernal_mage = _tree_row(tree, "infernal_mage")
        dust_devil = _tree_row(tree, "dust_devil")
        green_dragon = _tree_row(tree, "green_dragon")
        harpie_bug_swarm = _tree_row(tree, "harpie_bug_swarm")
        killerwatt = _tree_row(tree, "killerwatt")
        sea_snake_hatchling = _tree_row(tree, "sea_snake_hatchling")
        sea_snake_young = _tree_row(tree, "sea_snake_young")
        brine_rat = _tree_row(tree, "brine_rat")
        molanisk = _tree_row(tree, "molanisk")
        turoth = _tree_row(tree, "turoth")
        fire_giant = _tree_row(tree, "fire_giant")
        blue_dragon = _tree_row(tree, "blue_dragon")
        baby_blue_dragon = _tree_row(tree, "baby_blue_dragon")
        bronze_dragon = _tree_row(tree, "bronze_dragon")
        iron_dragon = _tree_row(tree, "iron_dragon")
        steel_dragon = _tree_row(tree, "steel_dragon")
        red_dragon = _tree_row(tree, "red_dragon")
        black_dragon = _tree_row(tree, "black_dragon")
        baby_red_dragon = _tree_row(tree, "baby_red_dragon")
        cave_horror = _tree_row(tree, "cave_horror")
        dagannoth = _tree_row(tree, "dagannoth")
        dagannoth_melee = _tree_row(tree, "dagannoth_level_92")
        elf_warrior = _tree_row(tree, "elf_warrior")
        elf_warrior_melee = _tree_row(tree, "elf_warrior_level_108")
        aberrant_spectre = _tree_row(tree, "aberrant_spectre")
        basilisk = _tree_row(tree, "basilisk")
        crocodile = _tree_row(tree, "crocodile")
        otherworldly_being = _tree_row(tree, "otherworldly_being")
        jungle_horror = _tree_row(tree, "jungle_horror")
        shadow_warrior = _tree_row(tree, "shadow_warrior")
        kalphite_soldier = _tree_row(tree, "kalphite_soldier")
        wall_beast = _tree_row(tree, "wall_beast")
        vampyre = _tree_row(tree, "vampyre")
        banshee = _tree_row(tree, "banshee")
        seagull = _tree_row(tree, "seagull")

        self.assertEqual(cow_calf.text(0), "Cow calf (Lvl\xa02)")
        self.assertIn("Cowhide", cow_calf.toolTip(0))
        self.assertEqual(ram.text(0), "Ram (Lvl\xa02)")
        self.assertEqual(spider.text(0), "Spider (Lvl\xa01)")
        self.assertIn("Gold charm x1 (5/200)", spider.toolTip(0))
        self.assertEqual(giant_spider.text(0), "Giant spider (Lvl\xa02)")
        self.assertIn("Air rune x4-6 (7/48)", giant_spider.toolTip(0))
        self.assertIn("Staff of air", giant_spider.toolTip(0))
        self.assertEqual(goblin_unarmed.text(0), "Goblin (unarmed) (Lvl\xa02)")
        self.assertIn("Bronze spear x1 (32/1024)", goblin_unarmed.toolTip(0))
        self.assertEqual(goblin_armed.text(0), "Goblin (armed) (Lvl\xa02)")
        self.assertIn("armed id", goblin_armed.toolTip(0))
        self.assertEqual(goblin_level_11.text(0), "Goblin (Lvl\xa011)")
        self.assertIn("Bronze javelin x5 (2/128)", goblin_level_11.toolTip(0))
        self.assertIn("Minor herb table (2/128)", goblin_level_11.toolTip(0))
        self.assertEqual(farmer.text(0), "Farmer (Lvl\xa07)")
        self.assertIn("Allotment seed table (27/128)", farmer.toolTip(0))
        self.assertEqual(highwayman.text(0), "Highwayman (Lvl\xa05)")
        self.assertIn("Cape x1", highwayman.toolTip(0))
        self.assertEqual(goat.text(0), "Goat (Lvl\xa023)")
        self.assertIn("Enemy max hit: 47 LP", goat.toolTip(0))
        self.assertIn("Desert goat horn x1", goat.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            goat.toolTip(0),
        )
        self.assertFalse(goat.icon(0).isNull())
        self.assertIn("Iron bolts x2-12 (1/20)", highwayman.toolTip(0))
        self.assertEqual(barbarian_level_10.text(0), "Barbarian (Lvl\xa010)")
        self.assertIn("Enemy LP: 180/180", barbarian_level_10.toolTip(0))
        self.assertIn("Law rune x2 (8/1024)", barbarian_level_10.toolTip(0))
        self.assertIn("barbarian_2hsword_lvl_10.plugin.kts", barbarian_level_10.toolTip(0))
        self.assertEqual(ogre.text(0), "Ogre (Lvl\xa053)")
        self.assertIn("Ogre common seed table (19/128)", ogre.toolTip(0))
        self.assertIn("Big bones x1", ogre.toolTip(0))
        self.assertFalse(ogre.icon(0).isNull())
        self.assertEqual(jackal.text(0), "Jackal (Lvl\xa021)")
        self.assertIn("Enemy LP: 270/270", jackal.toolTip(0))
        self.assertIn("Enemy max hit: 80 LP", jackal.toolTip(0))
        self.assertFalse(jackal.icon(0).isNull())
        self.assertEqual(icefiend.text(0), "Icefiend (Lvl\xa013)")
        self.assertIn("Impious ashes x1", icefiend.toolTip(0))
        self.assertIn("Enemy max hit: 20 LP", icefiend.toolTip(0))
        self.assertFalse(icefiend.icon(0).isNull())
        self.assertEqual(pyrefiend.text(0), "Pyrefiend (Lvl\xa043)")
        self.assertIn("Enemy attack: Magic-based melee", pyrefiend.toolTip(0))
        self.assertIn("Enemy max hit: 44 LP", pyrefiend.toolTip(0))
        self.assertIn("Steel boots x1 (1/128)", pyrefiend.toolTip(0))
        self.assertFalse(pyrefiend.icon(0).isNull())
        self.assertEqual(jelly.text(0), "Jelly (Lvl\xa078)")
        self.assertIn("Enemy attack: Magic-based melee", jelly.toolTip(0))
        self.assertIn("Enemy max hit: 60 LP", jelly.toolTip(0))
        self.assertIn("Mithril boots x1 (1/128)", jelly.toolTip(0))
        self.assertFalse(jelly.icon(0).isNull())
        self.assertEqual(bloodveld.text(0), "Bloodveld (Lvl\xa076)")
        self.assertIn("Enemy attack: Magic-based melee", bloodveld.toolTip(0))
        self.assertIn("Enemy max hit: 59 LP", bloodveld.toolTip(0))
        self.assertIn("Black boots x1 (1/128)", bloodveld.toolTip(0))
        self.assertFalse(bloodveld.icon(0).isNull())
        self.assertEqual(infernal_mage.text(0), "Infernal Mage (Lvl\xa066)")
        self.assertIn("Enemy attack: Magic", infernal_mage.toolTip(0))
        self.assertIn("Enemy max hit: 89 LP", infernal_mage.toolTip(0))
        self.assertIn(
            "Mystic boots (dark) x1 (125/64000)", infernal_mage.toolTip(0)
        )
        self.assertIn(
            "Lava battlestaff x1 (64/64000)", infernal_mage.toolTip(0)
        )
        self.assertFalse(infernal_mage.icon(0).isNull())
        self.assertEqual(dust_devil.text(0), "Dust devil (Lvl\xa093)")
        self.assertIn("Enemy max hit: 90 LP", dust_devil.toolTip(0))
        self.assertIn("Dragon chainbody x1 (1/32768)", dust_devil.toolTip(0))
        self.assertIn("Crimson charm x1 (115/606)", dust_devil.toolTip(0))
        self.assertFalse(dust_devil.icon(0).isNull())
        self.assertEqual(green_dragon.text(0), "Green dragon (Lvl\xa079)")
        self.assertIn("Dragonfire: None protection", green_dragon.toolTip(0))
        self.assertIn("Dragon bones x1", green_dragon.toolTip(0))
        self.assertFalse(green_dragon.icon(0).isNull())
        self.assertEqual(
            harpie_bug_swarm.text(0), "Harpie Bug Swarm (Lvl\xa046)"
        )
        self.assertIn(
            "Gold ore x1 (10514/100000)", harpie_bug_swarm.toolTip(0)
        )
        self.assertIn(
            "Green charm x1 (11/202)", harpie_bug_swarm.toolTip(0)
        )
        self.assertFalse(harpie_bug_swarm.icon(0).isNull())
        self.assertEqual(killerwatt.text(0), "Killerwatt (Lvl\xa071)")
        self.assertIn("Impious ashes x1", killerwatt.toolTip(0))
        self.assertIn("Gold charm x1 (41/303)", killerwatt.toolTip(0))
        self.assertFalse(killerwatt.icon(0).isNull())
        self.assertEqual(
            sea_snake_hatchling.text(0), "Sea Snake Hatchling (Lvl\xa062)"
        )
        self.assertIn("Casket x1 (11700/13000)", sea_snake_hatchling.toolTip(0))
        self.assertFalse(sea_snake_hatchling.icon(0).isNull())
        self.assertEqual(sea_snake_young.text(0), "Sea Snake Young (Lvl\xa090)")
        self.assertIn("Coins x44 (60/128)", sea_snake_young.toolTip(0))
        self.assertFalse(sea_snake_young.icon(0).isNull())
        self.assertEqual(brine_rat.text(0), "Brine rat (Lvl\xa070)")
        self.assertIn("Brine sabre x1 (1/512)", brine_rat.toolTip(0))
        self.assertIn("Gold charm x1 (133/606)", brine_rat.toolTip(0))
        self.assertFalse(brine_rat.icon(0).isNull())
        self.assertEqual(molanisk.text(0), "Molanisk (Lvl\xa051)")
        self.assertIn("Mole claw x1 (207/100000)", molanisk.toolTip(0))
        self.assertIn("Clue scroll (easy) x1 (1/128)", molanisk.toolTip(0))
        self.assertFalse(molanisk.icon(0).isNull())
        self.assertEqual(turoth.text(0), "Turoth (Lvl\xa083)")
        self.assertIn(
            "Leaf-bladed sword x1 (169/100000)",
            turoth.toolTip(0),
        )
        self.assertIn("Green charm x1 (214/1212)", turoth.toolTip(0))
        self.assertFalse(turoth.icon(0).isNull())
        self.assertEqual(fire_giant.text(0), "Fire giant (Lvl\xa086)")
        self.assertIn("Enemy max hit: 116 LP", fire_giant.toolTip(0))
        self.assertIn("Big bones x1", fire_giant.toolTip(0))
        self.assertIn("Gold charm x1 (207/404)", fire_giant.toolTip(0))
        self.assertFalse(fire_giant.icon(0).isNull())
        self.assertEqual(blue_dragon.text(0), "Blue dragon (Lvl\xa0111)")
        self.assertIn("Enemy max hit: 500 LP", blue_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", blue_dragon.toolTip(0))
        self.assertIn("Blue dragon egg x1 (1/2000)", blue_dragon.toolTip(0))
        self.assertIn("Gold charm x1 (15/404)", blue_dragon.toolTip(0))
        self.assertFalse(blue_dragon.icon(0).isNull())
        self.assertEqual(baby_blue_dragon.text(0), "Baby blue dragon (Lvl\xa048)")
        self.assertIn("Baby dragon bones x1", baby_blue_dragon.toolTip(0))
        self.assertNotIn("Dragonfire:", baby_blue_dragon.toolTip(0))
        self.assertFalse(baby_blue_dragon.icon(0).isNull())
        self.assertEqual(bronze_dragon.text(0), "Bronze dragon (Lvl\xa0131)")
        self.assertIn("Enemy max hit: 500 LP", bronze_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", bronze_dragon.toolTip(0))
        self.assertIn("Bronze bar x5", bronze_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/2048)", bronze_dragon.toolTip(0))
        self.assertIn("Clue scroll (elite) x1 (1/500)", bronze_dragon.toolTip(0))
        self.assertFalse(bronze_dragon.icon(0).isNull())
        self.assertEqual(iron_dragon.text(0), "Iron dragon (Lvl\xa0189)")
        self.assertIn("Enemy max hit: 500 LP", iron_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", iron_dragon.toolTip(0))
        self.assertIn("Iron bar x5", iron_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/1024)", iron_dragon.toolTip(0))
        self.assertIn("Draconic visage x1 (1/10000)", iron_dragon.toolTip(0))
        self.assertIn("Green charm x2 (282/1212)", iron_dragon.toolTip(0))
        self.assertFalse(iron_dragon.icon(0).isNull())
        self.assertEqual(steel_dragon.text(0), "Steel dragon (Lvl\xa0246)")
        self.assertIn("Enemy max hit: 500 LP", steel_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", steel_dragon.toolTip(0))
        self.assertIn("Steel bar x5", steel_dragon.toolTip(0))
        self.assertIn("Coins x650 (5/128)", steel_dragon.toolTip(0))
        self.assertIn("Dragon plateskirt x1 (1/512)", steel_dragon.toolTip(0))
        self.assertIn("Green charm x3 (308/1212)", steel_dragon.toolTip(0))
        self.assertFalse(steel_dragon.icon(0).isNull())
        self.assertEqual(red_dragon.text(0), "Red dragon (Lvl\xa0152)")
        self.assertIn("Enemy max hit: 500 LP", red_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", red_dragon.toolTip(0))
        self.assertIn("Red dragonhide x1", red_dragon.toolTip(0))
        self.assertIn("Red dragon egg x1 (1/2000)", red_dragon.toolTip(0))
        self.assertIn("Green charm x1 (385/1212)", red_dragon.toolTip(0))
        self.assertFalse(red_dragon.icon(0).isNull())
        self.assertEqual(black_dragon.text(0), "Black dragon (Lvl\xa0227)")
        self.assertIn("Enemy max hit: 500 LP", black_dragon.toolTip(0))
        self.assertIn("Dragonfire: None", black_dragon.toolTip(0))
        self.assertIn("Black dragonhide x1", black_dragon.toolTip(0))
        self.assertIn("Black dragon egg x1 (1/2000)", black_dragon.toolTip(0))
        self.assertIn("Draconic visage x1 (1/10000)", black_dragon.toolTip(0))
        self.assertIn("Gold charm x3 (42/1212)", black_dragon.toolTip(0))
        self.assertFalse(black_dragon.icon(0).isNull())
        self.assertEqual(baby_red_dragon.text(0), "Baby red dragon (Lvl\xa048)")
        self.assertIn("Enemy max hit: 54 LP", baby_red_dragon.toolTip(0))
        self.assertIn("Baby dragon bones x1", baby_red_dragon.toolTip(0))
        self.assertNotIn("Dragonfire:", baby_red_dragon.toolTip(0))
        self.assertFalse(baby_red_dragon.icon(0).isNull())
        self.assertEqual(cave_horror.text(0), "Cave horror (Lvl\xa080)")
        self.assertIn("Enemy attack: Magic-based melee", cave_horror.toolTip(0))
        self.assertIn("Enemy max hit: 87 LP", cave_horror.toolTip(0))
        self.assertIn("Missing a Witchwood icon", cave_horror.toolTip(0))
        self.assertIn("Black mask (10) x1 (1/512)", cave_horror.toolTip(0))
        self.assertIn("Crimson charm x1 (136/1212)", cave_horror.toolTip(0))
        self.assertFalse(cave_horror.icon(0).isNull())
        self.assertEqual(dagannoth.text(0), "Dagannoth (ranged) (Lvl\xa074)")
        self.assertIn("Enemy attack: Ranged", dagannoth.toolTip(0))
        self.assertIn("Pearl bolt tips x12 (25/1100)", dagannoth.toolTip(0))
        self.assertIn("Crimson charm x1 (212/1212)", dagannoth.toolTip(0))
        self.assertFalse(dagannoth.icon(0).isNull())
        self.assertEqual(
            dagannoth_melee.text(0), "Dagannoth (melee) (Lvl\xa092)"
        )
        self.assertIn("Enemy attack: Melee", dagannoth_melee.toolTip(0))
        self.assertIn("Clue scroll (medium) x1 (1/128)", dagannoth_melee.toolTip(0))
        self.assertFalse(dagannoth_melee.icon(0).isNull())
        self.assertEqual(
            elf_warrior.text(0), "Elf warrior (ranged) (Lvl\xa090)"
        )
        self.assertIn(
            "Crystal teleport seed x1 (25/128)", elf_warrior.toolTip(0)
        )
        self.assertIn("Green charm x1 (227/1212)", elf_warrior.toolTip(0))
        self.assertFalse(elf_warrior.icon(0).isNull())
        self.assertEqual(
            elf_warrior_melee.text(0), "Elf warrior (melee) (Lvl\xa0108)"
        )
        self.assertIn("Enemy attack: Melee", elf_warrior_melee.toolTip(0))
        self.assertIn(
            "Clue scroll (hard) x1 (1/128)", elf_warrior_melee.toolTip(0)
        )
        self.assertFalse(elf_warrior_melee.icon(0).isNull())
        self.assertEqual(
            aberrant_spectre.text(0), "Aberrant spectre (Lvl\xa096)"
        )
        self.assertIn("Enemy max hit: 10 LP", aberrant_spectre.toolTip(0))
        self.assertIn("Missing Nose peg", aberrant_spectre.toolTip(0))
        self.assertIn(
            "Mystic robe bottom (dark) x1 (1/512)",
            aberrant_spectre.toolTip(0),
        )
        self.assertIn("Gold charm x1 (97/1212)", aberrant_spectre.toolTip(0))
        self.assertFalse(aberrant_spectre.icon(0).isNull())
        self.assertEqual(basilisk.text(0), "Basilisk (Lvl\xa061)")
        self.assertIn("Enemy max hit: 10 LP", basilisk.toolTip(0))
        self.assertIn("Missing Mirror shield", basilisk.toolTip(0))
        self.assertIn(
            "Mystic hat (light) x1 (125/64000)", basilisk.toolTip(0)
        )
        self.assertIn("Basilisk head x1 (32/64000)", basilisk.toolTip(0))
        self.assertFalse(basilisk.icon(0).isNull())
        self.assertEqual(crocodile.text(0), "Crocodile (Lvl\xa063)")
        self.assertIn("Enemy max hit: 67 LP", crocodile.toolTip(0))
        self.assertIn("Bones x1", crocodile.toolTip(0))
        self.assertIn(
            "Desert heat: 1 Waterskin dose per Combat review",
            crocodile.toolTip(0),
        )
        self.assertFalse(crocodile.icon(0).isNull())
        self.assertEqual(
            otherworldly_being.text(0), "Otherworldly being (Lvl\xa064)"
        )
        self.assertIn("Enemy max hit: 70 LP", otherworldly_being.toolTip(0))
        self.assertIn("Minor herb table (10/128)", otherworldly_being.toolTip(0))
        self.assertIn("Rune mace x1 (1/128)", otherworldly_being.toolTip(0))
        self.assertFalse(otherworldly_being.icon(0).isNull())
        self.assertEqual(jungle_horror.text(0), "Jungle horror (Lvl\xa070)")
        self.assertIn("Enemy max hit: 84 LP", jungle_horror.toolTip(0))
        self.assertIn(
            "Iron warhammer x1 (8395/100000)", jungle_horror.toolTip(0)
        )
        self.assertFalse(jungle_horror.icon(0).isNull())
        self.assertEqual(shadow_warrior.text(0), "Shadow warrior (Lvl\xa048)")
        self.assertIn("Enemy max hit: 65 LP", shadow_warrior.toolTip(0))
        self.assertIn("Adamant spear x1 (1/128)", shadow_warrior.toolTip(0))
        self.assertIn("Crimson charm x1 (44/606)", shadow_warrior.toolTip(0))
        self.assertFalse(shadow_warrior.icon(0).isNull())
        self.assertEqual(kalphite_soldier.text(0), "Kalphite Soldier (Lvl\xa085)")
        self.assertIn("Enemy max hit: 80 LP", kalphite_soldier.toolTip(0))
        self.assertIn(
            "Poison: 50 LP initial · 40% attack chance",
            kalphite_soldier.toolTip(0),
        )
        self.assertIn("Rune chainbody x1 (1/128)", kalphite_soldier.toolTip(0))
        self.assertFalse(kalphite_soldier.icon(0).isNull())
        self.assertEqual(wall_beast.text(0), "Wall beast (Lvl\xa049)")
        self.assertIn(
            "Equip a Spiny helmet to start fighting Wall beasts",
            wall_beast.toolTip(0),
        )
        self.assertFalse(wall_beast.icon(0).isNull())
        self.assertEqual(vampyre.text(0), "Vampyre (Lvl\xa061)")
        self.assertIn("Vampyre dust x1", vampyre.toolTip(0))
        self.assertIn(
            "Weakness: Holy symbol not equipped · enemy accuracy -20% · max hit -20%",
            vampyre.toolTip(0),
        )
        self.assertFalse(vampyre.icon(0).isNull())
        self.assertEqual(banshee.text(0), "Banshee (Lvl\xa023)")
        self.assertIn("Missing Earmuffs", banshee.toolTip(0))
        self.assertIn("Enemy max hit: 10 LP", banshee.toolTip(0))
        self.assertEqual(seagull.text(0), "✓ Seagull (Lvl\xa02)")
        self.assertIn("seagull_level_2.plugin.kts", seagull.toolTip(0))
        self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "seagull")

    def test_bush_snake_row_is_selectable_and_uses_its_icon(self) -> None:
        pd = _make_player_data()
        pd["current_combat_target"] = "bush_snake"
        pd["combat_examined_monsters"] = ["bush_snake"]
        pd["woodcutting_level"] = 10
        pd["inventory"]["Machete"] = 1
        pd["quests"]["jungle_potion"] = {
            "started": True,
            "progress": 5,
            "completed": True,
        }
        dialog = self._open(pd, current_skill="Combat")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()

        tree = _find_tree_with_user_role(dialog, "bush_snake")
        snake = _tree_row(tree, "bush_snake")
        self.assertFalse(snake.isDisabled())
        self.assertEqual(snake.text(0), "✓ Bush snake (Lvl\xa035)")
        self.assertIn("Enemy LP: 250/250", snake.toolTip(0))
        self.assertIn("Enemy max hit: 38 LP", snake.toolTip(0))
        self.assertIn("Snake hide x1-5", snake.toolTip(0))
        self.assertFalse(snake.icon(0).isNull())
        self.assertTrue(snake.parent().isExpanded())
        self.assertTrue(tree.viewport().rect().intersects(tree.visualItemRect(snake)))
        dialog.deleteLater()

    def test_combat_search_filters_without_changing_or_activating_the_saved_target(self) -> None:
        from aqt.qt import QEvent, QKeyEvent

        pd = _make_player_data()
        pd["current_combat_target"] = "seagull"
        dialog = self._open(pd, current_skill="Combat")
        search = _find_named_line_edit(dialog, "combatTargetSearchInput")

        search.setText("cockatrice")
        QApplication.processEvents()
        tree = dialog.findChild(QListWidget, "combatTargetTree")
        self.assertIsNotNone(tree)
        visible_roles = {
            tree.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(tree.count())
        }
        self.assertEqual(visible_roles, {"cockatrice"})
        self.assertEqual(pd["current_combat_target"], "seagull")
        self.assertEqual(self._combat_calls, [])
        self.assertIsNone(tree.currentItem())

        search.setText("wall beast")
        QApplication.processEvents()
        tree = dialog.findChild(QListWidget, "combatTargetTree")
        wall_beast = tree.item(0)
        self.assertEqual(
            wall_beast.data(Qt.ItemDataRole.UserRole),
            "wall_beast",
        )
        self.assertFalse(wall_beast.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Locked due to:", wall_beast.toolTip())

        search.setText("seagull")
        QApplication.processEvents()
        tree = dialog.findChild(QListWidget, "combatTargetTree")
        seagull = tree.currentItem()
        self.assertEqual(seagull.data(Qt.ItemDataRole.UserRole), "seagull")
        self.assertEqual(seagull.background().color(), QColor(76, 175, 80, 120))
        self.assertEqual(seagull.text(), "✓ Seagull (Lvl\xa02)")
        self.assertTrue(seagull.font().bold())
        self.assertTrue(tree.viewport().rect().intersects(tree.visualItemRect(seagull)))

        search.setText("definitely-not-a-target")
        QApplication.processEvents()
        tree = dialog.findChild(QListWidget, "combatTargetTree")
        empty = tree.item(0)
        self.assertEqual(empty.text(), "No combat targets match this search.")
        self.assertFalse(empty.flags() & Qt.ItemFlag.ItemIsEnabled)
        tree.itemActivated.emit(empty)
        QApplication.processEvents()
        self.assertEqual(self._combat_calls, [])

        escape = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(search, escape)
        QApplication.processEvents()
        self.assertEqual(search.text(), "")
        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        self.assertEqual(
            tree.currentItem().data(0, Qt.ItemDataRole.UserRole),
            "seagull",
        )
        self.assertEqual(pd["current_combat_target"], "seagull")
        dialog.deleteLater()

    def test_combat_selector_hybridizes_at_twenty_five_filtered_rows(self) -> None:
        from ankiscape.core.target_metadata import TargetRowMetadata

        def _rows(count: int) -> tuple[TargetRowMetadata, ...]:
            return tuple(
                TargetRowMetadata(
                    target_id=f"combat_hybrid_{index}",
                    label=f"Combat hybrid {index}",
                    tooltip=f"Target {index}",
                    current=index == 0,
                    group="Other",
                    sort_key=(index,),
                )
                for index in range(count)
            )

        dialogs = []
        try:
            with patch.object(self._ui, "combat_target_rows", return_value=_rows(24)):
                flat_dialog = self._open(_make_player_data(), current_skill="Combat")
            dialogs.append(flat_dialog)
            with patch.object(self._ui, "combat_target_rows", return_value=_rows(25)):
                tree_dialog = self._open(_make_player_data(), current_skill="Combat")
            dialogs.append(tree_dialog)

            flat = flat_dialog.findChild(QListWidget, "combatTargetTree")
            tree = tree_dialog.findChild(QTreeWidget, "combatTargetTree")
            self.assertIsNotNone(flat)
            self.assertIsNotNone(tree)
            self.assertEqual(flat.count(), 24)
            self.assertEqual(tree.topLevelItem(0).childCount(), 25)
        finally:
            for dialog in dialogs:
                dialog.deleteLater()

    def test_combat_selector_scrolls_the_saved_target_into_view(self) -> None:
        pd = _make_player_data()
        pd["current_combat_target"] = "seagull"
        dialog = self._open(pd, current_skill="Combat")
        dialog.resize(900, 560)
        dialog.show()
        for _ in range(4):
            QApplication.processEvents()

        tree = dialog.findChild(QTreeWidget, "combatTargetTree")
        self.assertIsNotNone(tree)
        seagull = _tree_row(tree, "seagull")
        wall_beast = _tree_row(tree, "wall_beast")

        self.assertTrue(tree.alternatingRowColors())
        self.assertEqual(
            tree.selectionMode(), QAbstractItemView.SelectionMode.SingleSelection
        )
        self.assertEqual(tree.visualItemRect(seagull).height(), 30)
        self.assertIs(tree.currentItem(), seagull)
        self.assertTrue(seagull.parent().isExpanded())
        self.assertEqual(seagull.background(0).color(), QColor(76, 175, 80, 120))
        self.assertEqual(seagull.text(0), "✓ Seagull (Lvl\xa02)")
        self.assertTrue(seagull.font(0).bold())
        self.assertFalse(seagull.isSelected())
        self.assertTrue(tree.viewport().rect().intersects(tree.visualItemRect(seagull)))

        self.assertTrue(wall_beast.isDisabled())
        self.assertIn("Locked due to:", wall_beast.toolTip(0))
        self.assertIn("Slayer level 35", wall_beast.toolTip(0))

        # The role-based brush assertion above is not enough: QSS item border
        # rules can make Qt ignore BackgroundRole during native painting.
        def _sample_row(item, image):
            rect = tree.visualItemRect(item)
            viewport_point = QPoint(tree.viewport().width() - 12, rect.center().y())
            return image.pixelColor(tree.viewport().mapTo(tree, viewport_point))

        saved_pixel = _sample_row(seagull, tree.grab().toImage())
        candidate_rows = [
            item
            for item in _tree_items(tree)
            if item.parent() is not None
            and item is not seagull
            and not item.isDisabled()
        ]
        self.assertTrue(candidate_rows, "a non-saved combat row must exist")
        non_saved = candidate_rows[0]
        non_saved.parent().setExpanded(True)
        tree.scrollToItem(non_saved)
        for _ in range(3):
            QApplication.processEvents()
        non_saved_pixel = _sample_row(non_saved, tree.grab().toImage())
        self.assertGreater(saved_pixel.green(), saved_pixel.red())
        self.assertGreater(saved_pixel.green(), saved_pixel.blue())
        self.assertFalse(
            non_saved_pixel.green() > non_saved_pixel.red()
            and non_saved_pixel.green() > non_saved_pixel.blue()
        )

        tree.setCurrentItem(non_saved)
        for _ in range(3):
            QApplication.processEvents()
        selected_pixel = _sample_row(non_saved, tree.grab().toImage())
        self.assertGreater(selected_pixel.blue(), selected_pixel.green())
        self.assertNotEqual(selected_pixel.rgba(), saved_pixel.rgba())

        for group_index in range(tree.topLevelItemCount()):
            group = tree.topLevelItem(group_index)
            levels = []
            for child_index in range(group.childCount()):
                match = re.search(r"\(Lvl\xa0(\d+)\)", group.child(child_index).text(0))
                self.assertIsNotNone(match)
                levels.append(int(match.group(1)))
            self.assertEqual(levels, sorted(levels), group.text(0))

        dialog.deleteLater()
