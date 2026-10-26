"""Lazim's opening: dated witnesses, disclosed reconstruction and canonical custody."""

from .contract import QuestStageRequirementCleanup

QUEST_ID = "enakhras_lament"
MASS_KEY = "enakhras_lament_sandstone_kg"
TARGET_KG = 32
SANDSTONE = {6971: ("Sandstone (1kg)", 1), 6973: ("Sandstone (2kg)", 2),
             6975: ("Sandstone (5kg)", 5), 6977: ("Sandstone (10kg)", 10)}
BLOCK_ID, BLOCK = 6986, "Sandstone (32kg)"
BASE_ID, BASE = 6988, "Sandstone base"
CHISEL_ID, CHISEL = 1755, "Chisel"
COAL_ID, FLAT_GROUND_ID = 453, 10954

# PLACEHOLDER(quests.enakhras_lament.split_10kg_outputs): independently qualified pre-cutoff outputs.
SPLIT_10KG_OUTPUTS = ((6975, 2),)
# PLACEHOLDER(quests.enakhras_lament.split_5kg_outputs): independently qualified pre-cutoff outputs.
SPLIT_5KG_OUTPUTS = ((6973, 2), (6971, 1))
# PLACEHOLDER(quests.enakhras_lament.split_2kg_outputs): independently qualified pre-cutoff outputs.
SPLIT_2KG_OUTPUTS = ((6971, 2),)
SPLIT_OUTPUTS = {6977: SPLIT_10KG_OUTPUTS, 6975: SPLIT_5KG_OUTPUTS, 6973: SPLIT_2KG_OUTPUTS}
# PLACEHOLDER(quests.enakhras_lament.split_xp): independently qualified action-specific experience.
SPLIT_ADDITIONAL_XP = 0.0
# PLACEHOLDER(quests.enakhras_lament.chisel_xp): independently qualified action-specific experience.
CHISEL_ADDITIONAL_XP = 0.0

PROOFS = {
    "offer_help": "Offer to help Lazim",
    "deliver_sandstone": "Supply sandstone to Lazim",
    "receive_32kg": "Receive Lazim's 32kg sandstone block",
    "chisel_base": "Chisel Lazim's sandstone block into a base",
    "talk_after_base": "Talk to Lazim after chiseling the base",
    "place_base": "Place the sandstone base beside Lazim",
    "split_10kg": "Split a 10kg sandstone block for Lazim",
    "split_5kg": "Split a 5kg sandstone block for Lazim",
    "split_2kg": "Split a 2kg sandstone block for Lazim",
}
EVENT_PREFIX = "enakhras_lament_"
NOTICES = {
    "offer_help": "I offered to help Lazim.",
    "deliver_sandstone": "Gave Lazim {mass} kg of sandstone ({total}/32 kg).",
    "receive_32kg": "Gave Lazim {mass} kg of sandstone ({total}/32 kg). Lazim joined the sandstone into one 32kg block.",
    "split_10kg": "Split one 10kg sandstone block.",
    "split_5kg": "Split one 5kg sandstone block.",
    "split_2kg": "Split one 2kg sandstone block.",
    "chisel_base": "Chiseled the 32kg block into a sandstone base.",
    "talk_after_base": "Spoke to Lazim again about the sandstone base.",
    "place_base": "Placed the sandstone base on the flat ground beside Lazim.",
}
OWNER_DECISIONS = (
    ("2026-10-24 08:55 PDT", "Use reconstructed split ratios as marked provisional values; preserve later saves without opening proofs."),
    ("2026-10-24 09:44 PDT", "Ship splitting and base chiseling with marked provisional zero additional experience."),
)
SOURCE_CUTOFF = "2012-11-20T00:00:00Z"

SOURCES = ({'id': 'W1',
  'title': "Enakhra's Lament",
  'revision': 6548386,
  'timestamp_utc': '2012-11-11T21:18:24Z',
  'file': 'sources/enakhra-s-lament-6548386.txt',
  'sha256': '8e38947f97cd8d94b2446d3280f6438fa7a355d6aa05d6a921867d925328d2af',
  'url': 'https://runescape.wiki/w/Enakhra%27s_Lament?oldid=6548386',
  'rung': 'H4 dated wiki',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/enakhra-s-lament-6548386.txt',
  'historical_witness': True,
  'excerpts': ((30, '{{Skillreq|Crafting|50}} Cannot be boosted.'),
               (31, '{{Skillreq|Firemaking|45}}'),
               (32, '{{Skillreq|Prayer|43}} (43 if on standard prayers, 71 if on [[Ancient curses]].)'),
               (33, '{{Skillreq|Magic|39}}'),
               (34, '{{Skillreq|Mining|45}} (Not required, but would be helpful!)'),
               (35, '|items='),
               (36, '*A [[pickaxe]] (can be obtained in quest, the toolbelt will work) or [[Dwarven Army Axe]]'),
               (37, '*Two 5Kg [[Granite rock|granite block]] (can be obtained in quest with 45 mining)'),
               (38,
                '*52Kg of [[sandstone]] (Bring 5 10kg and one 2kg, or mine with 45 mining. 32kg is for the base, 20kg for the '
                'body)'),
               (39, '*1 loaf of [[bread]] (or [[Cake]])'),
               (40,
                '*Enough [[runes]] to cast [[Fire Bolt]] (or better), [[Wind Bolt]] (or better), and [[Crumble Undead]] '
                'successfully (it is possible to splash)'),
               (41, '*A [[candle]] (a [[Black candle]] will not work)'),
               (42, '*1 of each: [[logs]], [[oak logs]], [[willow logs]], [[maple logs]]'),
               (43, '*[[Soft clay]] (bring two if you want to have a [[camel mask]])'),
               (44, '*1 [[coal]] (obtainable during quest)'),
               (45, '*Some [[Waterskin]]s or an [[Enchanted water tiara]].'),
               (46, '*[[Chisel]] (the toolbelt will work)'),
               (57,
                'Speak to [[Lazim]] just outside the [[Granite and sandstone quarry|desert quarry]]. He will tell you about how '
                'he wishes to sculpt but had an accident and cannot do it himself. Offer to help him, and get 32 kilograms of '
                '[[sandstone]] by mining it in the quarry (if you forgot your pickaxe take one from the rock nearby). Lazim will '
                'not take more than 32 kg, so if necessary, break up your blocks with your chisel. Players will find it much '
                'simpler to deal with Lazim if they bring him their sandstone after each piece they mine. Also, mine 1 [[coal]] '
                "if you didn't start with one."),
               (59, '===Building a statue==='),
               (60,
                "After you've given Lazim exactly 32 kg, he will attach them with magic to make a [[sandstone (32kg)|32kg "
                'sandstone block]]. Use your chisel on the block that he gives you to make a [[sandstone base]]. Talk to him '
                'again, then use the base on the flat ground next to him.'),
               (62,
                "You now need 20 kg of sandstone for the body. After you've given him the required amount and he gives you the "
                '[[sandstone (20kg)|20kg sandstone block]], use your chisel on it to make a [[sandstone body]] and then attach '
                'it to the base. Once attached to the base, chisel the body once more to get more intricate details on the '
                'statue.'),
               (64,
                'Lazim will tell you to create a head next. You must then choose a head to sculpt. For players who have '
                'completed [[The Giant Dwarf]], this choice may seem familiar. Your options include [[Lazim]], [[Icthlarin]], '
                '[[Zamorak]], [[Akthanakos]], or a camel, choose the head of Lazim. You also have the choice of using your own '
                "head, but Lazim will refuse. To create the head mine a 5 kg block of '''granite (make sure it's GRANITE, not "
                "sandstone!''') then chisel it. You will need to create another head later, so mine a second 5 kg block of "
                'granite as well but do not chisel it. You will need later on in the quest.'))},
 {'id': 'A1',
  'title': 'Enakhra’s Lament – RuneScape Guide – RuneHQ',
  'revision': 'Wayback 20121107054626',
  'timestamp_utc': '2012-11-07T05:46:26Z',
  'file': 'sources/runehq-enakhras-lament-20121107054626.html',
  'sha256': 'b1993f2098788a804d423aaec1791dfc0a037e3e3958f87f609451194bd961f0',
  'url': 'https://web.archive.org/web/20121107054626id_/http://www.runehq.com:80/quest/enakhras-lament',
  'rung': 'H4 independent contemporary article',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/runehq-enakhras-lament-20121107054626.html',
  'historical_witness': True,
  'excerpts': ((248,
                '<div class="undersubheader">Difficulty:</div><div class="guide">Experienced</div><div '
                'class="undersubheader">Length:</div><div class="guide">Medium</div><div class="undersubheader">Quest '
                'Requirements:<br /></div><div class="guide">None</div><div class="undersubheader">Skill/Other Requirements:<br '
                '/></div><div class="guide">39 <a href="/guide.php?type=skill&amp;id=389">Magic</a><br />'),
               (249, '43 <a href="/guide.php?type=skill&amp;id=295">Prayer</a><br />'),
               (250, '45 <a href="/guide.php?type=skill&amp;id=368">Firemaking</a><br />'),
               (251, '50 <a href="/guide.php?type=skill&amp;id=386">Crafting</a>'),
               (264,
                'Offer to help <a href="/database.php?type=person&amp;id=2656">Lazim</a> and he will first ask you to acquire '
                '32kg of sandstone for him. Head over to the stone quarry to the southwest and start mining the sandstone rocks. '
                'Large blocks of sandstone weigh 10kg, medium-sized blocks 5K, small blocks 2kg and tiny blocks 1kg.'),
               (265, '<br /><br />'),
               (266,
                '<span class="smallbold">Note: </span>Blocks can be broken up into smaller ones by using a <a '
                'href="/database.php?type=item&amp;id=278">Chisel</a> on them. If you forgot to bring a pickaxe, or don\'t have '
                'one in your toolbelt, then pull the <a href="/database.php?type=item&amp;id=181">Bronze pickaxe</a> out of the '
                'rock in the center of the quarry.'),
               (267, '<br /><br />'),
               (268, '<img src="/image/quests/p2p/enakhraslament/quarry.png" alt="Quarry" />'),
               (269, '<br /><br />'),
               (270, '</li>'),
               (272, '<li>'),
               (273,
                'Hand the sandstone blocks over to <a href="/database.php?type=person&amp;id=2656">Lazim</a> and he will give '
                'you some <a href="/database.php?type=item&amp;id=20909">Sandstone (32kg)</a>. Use a <a '
                'href="/database.php?type=item&amp;id=278">Chisel</a> on it to create a <a '
                'href="/database.php?type=item&amp;id=20910">Sandstone base</a> and place the it on the flat ground near <a '
                'href="/database.php?type=person&amp;id=2656">Lazim</a>.'),
               (280,
                '<a href="/database.php?type=person&amp;id=2656">Lazim</a> say that the statue is missing something and will ask '
                'for 20Kg of sandstone. Repeat what you did earlier but get 20kg instead of 32kg. Hand the sandstone blocks over '
                'to <a href="/database.php?type=person&amp;id=2656">Lazim</a> and he will give you block of <a '
                'href="/database.php?type=item&amp;id=20913">Sandstone (20kg</a>. Use a <a '
                'href="/database.php?type=item&amp;id=278">Chisel</a> on it to create a <a '
                'href="/database.php?type=item&amp;id=20912">Sandstone body</a> and add it to the statue\'s base.'),
               (281, '<br /><br />'),
               (282, '<img src="/image/quests/p2p/enakhraslament/body.png" alt="Body" />'),
               (283, '<br /><br />'),
               (284, '</li>'),
               (286, '<li>'),
               (287,
                'Talk to <a href="/database.php?type=person&amp;id=2656">Lazim</a> again and he will ask to chisel the statue a '
                'bit more. Do as requested and he will ask for a head made of granite. Choose what kind of head you want to '
                'make. Return to the quarry and mine 2 <a href="/database.php?type=item&amp;id=2578">Granite (5kg)</a> blocks, '
                'one of which you will need later on in the quest. Use a <a href="/database.php?type=item&amp;id=278">Chisel</a> '
                'on one of the blocks and select the kind of head you have chosen earlier to create a <a '
                'href="/database.php?type=item&amp;id=20914">Stone head (Statue)</a>. Now, place the head on the statue. '))},
 {'id': 'W2',
  'title': 'Sandstone (32kg)',
  'revision': 6049281,
  'timestamp_utc': '2012-08-05T19:45:39Z',
  'file': 'sources/sandstone-32kg-6049281.txt',
  'sha256': 'd06babba0f7e7fa9386fae5363c94a27788dada2500c04a4cb381f41db9cc7c0',
  'url': 'https://runescape.wiki/w/Sandstone_(32kg)?oldid=6049281',
  'rung': 'H4 dated wiki',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/sandstone-32kg-6049281.txt',
  'historical_witness': True,
  'excerpts': ((8, '|tradeable = No'),
               (9, '|equipable = No'),
               (10, '|stackable = No'),
               (11, '|value = 1'),
               (12, '|destroy = You can make another 32 kg sandstone block by giving enough stone to Lazim.'),
               (17, '|weight = 32'),
               (18, '}}'),
               (19,
                "'''Sandstone (32 kg)''' is a quest item used during the [[Enakhra's Lament]] quest. It is obtained by speaking "
                'to [[Lazim]] in the desert south of the [[Bandit Camp (Kharidian Desert)|Bandit Camp]] and then giving exactly '
                '32 kg of individual sandstone blocks. The blocks can be mined from the quarry immediately south west of Lazim. '
                'After giving the blocks to Lazim he will magically join them to create the 32 kg block. The player can then use '
                'a [[chisel]] on this to make the [[sandstone base]] for the statue needed in the quest.'))},
 {'id': 'W3',
  'title': 'Sandstone base',
  'revision': 4831227,
  'timestamp_utc': '2011-10-10T16:38:25Z',
  'file': 'sources/sandstone-base-4831227.txt',
  'sha256': '8f0443ceb6a765d121c648871cface311af7d8b7d76ae3785a8887e2c64744f0',
  'url': 'https://runescape.wiki/w/Sandstone_base?oldid=4831227',
  'rung': 'H4 dated wiki',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/sandstone-base-4831227.txt',
  'historical_witness': True,
  'excerpts': ((8, '|tradeable = No'),
               (9, '|equipable = No'),
               (10, '|stackable = No'),
               (11, '|value = 1'),
               (12, '|destroy = You can make another statue base by giving Lazim 32 kg of stone and then crafting it.'),
               (17, '|weight = 32'),
               (18, '}}'),
               (20,
                "The '''Sandstone base''' is a [[quests|quest]] [[items|item]] used during the [[Enakhra's Lament]] quest. It is "
                'obtained by using a [[chisel]] to carve the [[sandstone (32kg)|32kg block of sandstone]] given to the player by '
                '[[Lazim]] in the desert south of the [[Bandit Camp (Kharidian Desert)|Bandit Camp]].'),
               (22, 'The base can then be positioned on the floor near Lazim ready to put the [[sandstone body]] on top.'))},
 {'id': 'W4',
  'title': 'Sandstone',
  'revision': 6298095,
  'timestamp_utc': '2012-09-26T03:09:24Z',
  'file': 'sources/sandstone-6298095.txt',
  'sha256': 'e50a402fa71b141975db5f2c90721d1ddfa526e90d60622dcc562cb8924c28bc',
  'url': 'https://runescape.wiki/w/Sandstone?oldid=6298095',
  'rung': 'H4 dated wiki',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/sandstone-6298095.txt',
  'historical_witness': True,
  'excerpts': ((9, '|tradeable = Yes'),
               (24,
                'Sandstone is tradeable and can be sold on the [[Grand Exchange]], but it is in very low demand because it '
                "currently has no known use in ''RuneScape'' other than in the quest ''[[Enakhra's Lament]]'' to make part of "
                "[[Lazim]]'s statue and can be power-mined for fast XP."),
               (26,
                'A player must have a [[Mining]] level of 35 or greater to mine sandstone, which yields the following experience '
                'depending on the size the sandstone block mined:'),
               (35, '|[[File:Sandstone (1kg).png|Sandstone (1kg)]]'),
               (36, '|1 kg'),
               (37, '|30'),
               (38, '|A tiny chunk of sandstone.'),
               (39, '|{{GEPriceUpdate|Sandstone (1kg)}}'),
               (40, '|-'),
               (41, '|[[File:Sandstone (2kg).png|Sandstone (2kg)]]'),
               (42, '|2 kg'),
               (43, '|40'),
               (44, '|A small chunk of sandstone.'),
               (45, '|{{GEPriceUpdate|Sandstone (2kg)}}'),
               (46, '|-'),
               (47, '|[[File:Sandstone (5kg).png|Sandstone (5kg)]]'),
               (48, '|5 kg'),
               (49, '|50'),
               (50, '|A medium-sized chunk of sandstone.'),
               (51, '|{{GEPriceUpdate|Sandstone (5kg)}}'),
               (52, '|-'),
               (53, '|[[File:Sandstone (10kg).png|Sandstone (10kg)]]'),
               (54, '|10 kg'),
               (55, '|60'))},
 {'id': 'W5',
  'title': 'Sandstone rock',
  'revision': 6298093,
  'timestamp_utc': '2012-09-26T03:09:22Z',
  'file': 'sources/sandstone-rock-6298093.txt',
  'sha256': '340b0e30355790d0b1bee40787034ff63ec1d5954bdeb7bf7729bfd5418eccbe',
  'url': 'https://runescape.wiki/w/Sandstone_rock?oldid=6298093',
  'rung': 'H4 dated wiki, same lineage as W4',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/sandstone-rock-6298093.txt',
  'historical_witness': True,
  'excerpts': ((7,
                'A player must have a [[Mining]] level of 35 or greater to mine sandstone, which yields the following experience '
                'depending on the size the sandstone block mined:'),
               (15, '|[[File:Sandstone (1kg).png]]'),
               (16, '|1&nbsp;kg'),
               (17, '|30'),
               (18, '|A tiny chunk of sandstone.'),
               (19, '|4 coins'),
               (20, '|-'),
               (21, '|[[File:Sandstone (2kg).png]]'),
               (22, '|2&nbsp;kg'),
               (23, '|40'),
               (24, '|A small chunk of sandstone.'),
               (25, '|13 coins'),
               (26, '|-'),
               (27, '|[[File:Sandstone (5kg).png]]'),
               (28, '|5&nbsp;kg'),
               (29, '|50'),
               (30, '|A medium-sized chunk of sandstone.'),
               (31, '|25 coins'),
               (32, '|-'),
               (33, '|[[File:Sandstone (10kg).png]]'),
               (34, '|10&nbsp;kg'),
               (35, '|60'))},
 {'id': 'D1',
  'title': 'EnakhrasLament.kt',
  'revision': 'a706bb783e95f9be0705dd37da85322e5737045c',
  'timestamp_utc': '2026-07-15T11:09:31Z',
  'file': 'sources/EnakhrasLament.kt',
  'sha256': '77a3bc5489edbff215bf74856e5ebddc73edb475c9e6562fd0996ecd0996103c',
  'url': 'local canonical Darkan checkout; src/main/java/com/rs/game/content/quests/enakhraslament/EnakhrasLament.kt',
  'rung': 'D primary restoration, not independent period witness',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/EnakhrasLament.kt',
  'historical_witness': False,
  'excerpts': ((58, '    private val sandstoneWeights = mapOf('),
               (59, '        EnakhrasLamentIds.SANDSTONE_1KG to 1,'),
               (60, '        EnakhrasLamentIds.SANDSTONE_2KG to 2,'),
               (61, '        EnakhrasLamentIds.SANDSTONE_5KG to 5,'),
               (62, '        EnakhrasLamentIds.SANDSTONE_10KG to 10,'),
               (63, '    )'),
               (105,
                '    private fun exchange(player: Player, inputs: List<Pair<Int, Int>>, outputId: Int? = null, outputAmount: Int '
                '= 1): Boolean {'),
               (106,
                '        if (inputs.any { (id, amount) -> !player.inventory.containsItem(id, amount) || '
                '!player.controllerManager.canDeleteInventoryItem(id, amount) }) return false'),
               (107, '        inputs.forEach { (id, amount) -> player.inventory.deleteItem(id, amount) }'),
               (108, '        if (outputId == null || player.inventory.addItem(outputId, outputAmount)) return true'),
               (109, '        inputs.forEach { (id, amount) -> player.inventory.addItem(id, amount) }'),
               (110, '        return false'),
               (111, '    }'),
               (113, '    private fun hasChisel(player: Player): Boolean = player.containsTool(EnakhrasLamentIds.CHISEL)'),
               (146, '    @JvmStatic fun deliverSandstone(player: Player, itemId: Int): Boolean {'),
               (147, '        if (EnakhrasLamentState.stage(player) != EnakhrasLamentState.STARTED) return false'),
               (148, '        val weight = sandstoneWeights[itemId] ?: return false'),
               (149, '        val attrs = EnakhrasLamentState.attrs(player)'),
               (150, '        val target = if (attrs.getB(EnakhrasLamentState.BASE_PLACED)) 20 else 32'),
               (151, '        if (attrs.getB(EnakhrasLamentState.BODY_ATTACHED)) return false'),
               (152, '        val given = attrs.getI(EnakhrasLamentState.SANDSTONE_GIVEN)'),
               (153, '        if (given + weight > target) return false'),
               (154, '        val output = if (given + weight == target) {'),
               (155, '            if (target == 32) EnakhrasLamentIds.SANDSTONE_32KG else EnakhrasLamentIds.SANDSTONE_20KG'),
               (156, '        } else null'),
               (157, '        if (!exchange(player, listOf(itemId to 1), output)) return false'),
               (158, '        attrs.setI(EnakhrasLamentState.SANDSTONE_GIVEN, given + weight)'),
               (159, '        return true'),
               (160, '    }'),
               (162, '    @JvmStatic fun craftQuestBlock(player: Player, itemId: Int): Boolean {'),
               (163,
                '        if (EnakhrasLamentState.stage(player) != EnakhrasLamentState.STARTED || !hasChisel(player)) return '
                'false'),
               (164, '        val output = when (itemId) {'),
               (165, '            EnakhrasLamentIds.SANDSTONE_32KG -> EnakhrasLamentIds.SANDSTONE_BASE'),
               (166, '            EnakhrasLamentIds.SANDSTONE_20KG -> EnakhrasLamentIds.SANDSTONE_BODY'),
               (167, '            else -> return false'),
               (168, '        }'),
               (169, '        return exchange(player, listOf(itemId to 1), output)'),
               (170, '    }'),
               (172, '    @JvmStatic fun placeBase(player: Player): Boolean {'),
               (173, '        val attrs = EnakhrasLamentState.attrs(player)'),
               (174,
                '        if (EnakhrasLamentState.stage(player) != EnakhrasLamentState.STARTED || '
                'attrs.getB(EnakhrasLamentState.BASE_PLACED) ||'),
               (175, '            !exchange(player, listOf(EnakhrasLamentIds.SANDSTONE_BASE to 1))) return false'),
               (176, '        attrs.setB(EnakhrasLamentState.BASE_PLACED, true)'),
               (177, '        attrs.setI(EnakhrasLamentState.SANDSTONE_GIVEN, 0)'),
               (178, '        return true')),
  'canonical_path': '/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/quests/enakhraslament/EnakhrasLament.kt'},
 {'id': 'D2',
  'title': 'EnakhrasLamentState.kt',
  'revision': 'a706bb783e95f9be0705dd37da85322e5737045c',
  'timestamp_utc': '2026-07-15T11:09:31Z',
  'file': 'sources/EnakhrasLamentState.kt',
  'sha256': 'e44bfb1ec2da2c7a2286fda08180baee815d9148f56e74e614c11694b802a38f',
  'url': 'same canonical checkout; src/main/java/com/rs/game/content/quests/enakhraslament/EnakhrasLamentState.kt',
  'rung': 'D primary restoration',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/EnakhrasLamentState.kt',
  'historical_witness': False,
  'excerpts': ((8, '    const val CHISEL = 1755'),
               (14, '    const val SANDSTONE_1KG = 6971'),
               (15, '    const val SANDSTONE_2KG = 6973'),
               (16, '    const val SANDSTONE_5KG = 6975'),
               (17, '    const val SANDSTONE_10KG = 6977'),
               (18, '    const val CAMULET = 6707'),
               (19, '    const val UGTHANKI_DUNG = 4601'),
               (20, '    const val SANDSTONE_20KG = 6985'),
               (21, '    const val SANDSTONE_32KG = 6986'),
               (22, '    const val SANDSTONE_BODY = 6987'),
               (23, '    const val SANDSTONE_BASE = 6988'),
               (49, '    const val COAL = 453'),
               (51, '    val LAZIM = intArrayOf(3143, 3144, 3145, 3146, 3147)'),
               (52, '    const val PENTYN = 3126'),
               (53, '    const val FIRST_BONEGUARD = 3129'),
               (54, '    val AKTHANAKOS = intArrayOf(3140, 3141, 3142)'),
               (56, '    const val FLAT_GROUND = 10954')),
  'canonical_path': '/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/quests/enakhraslament/EnakhrasLamentState.kt'},
 {'id': 'D3',
  'title': 'Desert.kt splitting lines 263–289',
  'revision': 'd606d1177e1a8f0adb528f253f7064e1644b3f31',
  'timestamp_utc': '2024-08-31T15:42:29Z',
  'file': 'sources/Desert.kt',
  'sha256': 'ee961adb7d51f3a5105ebe62b852f319f191433cfd9bc7b89bce1d8c36b975ad',
  'url': 'same canonical checkout; src/main/java/com/rs/game/content/world/areas/desert/Desert.kt',
  'rung': 'D pre-existing reconstruction, not recovered 2012 server code',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/Desert.kt',
  'historical_witness': False,
  'excerpts': ((263, '    onItemClick(6973, 6975, 6977, options = arrayOf("Craft")) { (player, item)->'),
               (264, '        if (!player.inventory.containsItem(1755, 1, true)) {'),
               (265, '            player.sendMessage("You must have a chisel in order to craft sandstone.")'),
               (266, '            return@onItemClick'),
               (267, '        }'),
               (268, '        if (player.inventory.freeSlots < (if (item.id == 6975) 2 else 1)) {'),
               (269, '            player.sendMessage("You do not have enough room in your inventory to split the sandstone.")'),
               (270, '            return@onItemClick'),
               (271, '        }'),
               (272, '        player.lock(2)'),
               (273, '        when (item.id) {'),
               (274, '            6977 -> { // 10kg - splits into 2x 5kg'),
               (275, '                player.inventory.deleteItem(6977, 1)'),
               (276, '                player.inventory.addItem(6975, 2)'),
               (277, '            }'),
               (278, '            6975 -> { // 5kg - splits into 2x 2kg and 1x 1kg'),
               (279, '                player.inventory.deleteItem(6975, 1)'),
               (280, '                player.inventory.addItem(6973, 2)'),
               (281, '                player.inventory.addItem(6971, 1)'),
               (282, '            }'),
               (283, '            6973 -> { // 2kg - splits into 2x 1kg'),
               (284, '                player.inventory.deleteItem(6973, 1)'),
               (285, '                player.inventory.addItem(6971, 2)'),
               (286, '            }'),
               (287, '        }'),
               (288, '        player.anim(11146)'),
               (289, '    }')),
  'canonical_path': '/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/world/areas/desert/Desert.kt'},
 {'id': 'D4',
  'title': 'Ore.java sandstone lines 55–58',
  'revision': 'c6fbe036b1743f4dd6067ec178332c69c3708856',
  'timestamp_utc': '2021-06-16T18:24:32Z',
  'file': 'sources/Ore.java',
  'sha256': 'a346b7cd9c6d4c80d6dcc9d5d4996ccdca3ffa59849f74d3da5cba5c2b9aa9ea',
  'url': 'same canonical checkout; src/main/java/com/rs/game/content/skills/mining/Ore.java',
  'rung': 'D initial-checkout implementation, not contemporary article',
  'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/Ore.java',
  'historical_witness': False,
  'excerpts': ((55, '\tSANDSTONE_1KG(6971, 35, 30, 16, 100, 0),'),
               (56, '\tSANDSTONE_2KG(6973, 35, 40, 8, 75, 0),'),
               (57, '\tSANDSTONE_5KG(6975, 35, 50, 6, 64, 0),'),
               (58, '\tSANDSTONE_10KG(6977, 35, 60, 3, 30, 0),')),
  'canonical_path': '/Users/armantarkhanian/Documents/CodexWorktrees/.treehouse/darkan-world-server-0e01c4/2/darkan-world-server/src/main/java/com/rs/game/content/skills/mining/Ore.java'})

TRANSACTION_SOURCES = {
    "offer_help": ("W1:57",),
    "deliver_sandstone": ("W1:57", "A1:264–266", "D1:58–63,146–159", "D2:14–17"),
    "receive_32kg": ("W1:60", "A1:273", "W2:19", "D1:154–158", "D2:21"),
    "chisel_base": ("W1:60", "A1:273", "W2:19", "W3:20", "D1:105–113,162–169", "D2:8,23"),
    "talk_after_base": ("W1:60",),
    "place_base": ("W1:60", "A1:273", "W3:20–22", "D1:172–178", "D2:49,56"),
    "split_10kg": ("W1:57", "A1:266", "D3:263–285"),
    "split_5kg": ("W1:57", "A1:266", "D3:263–285"),
    "split_2kg": ("W1:57", "A1:266", "D3:263–285"),
}
QUALIFICATION_NOTES = (
    "D1/D2 and D3 are modern restorations, not independent historical witnesses. Exact per-call granularity and split ratios lack independent period corroboration.",
    "D3's two free slots for 5kg and one for 2/10kg are disclosed reconstruction only; abstract quest inventory has no slot admission check.",
    "D1 and D3 contain no experience awards in these handlers. Neither source silence nor the limited modern comparison establishes historical zero experience; zero additional XP is the owner's provisional answer.",
    "W1:38 says 'mine with 45 mining'; specialized W4/W5 and D4 give Mining 35. Mining remains optional at entry and existing Mining values/probabilities are preserved.",
    "W1 further talk is enforced despite D1 omitting its gate. W2/W3 remake descriptions disagree with D2's free replacement shortcut; destruction/loss recovery remains unresolved and excluded.",
    "W2/W3 item weight is not a total-player-weight admission gate. Additional checks, action XP, exact dialogue, timing and animation are not stated in the checked period bodies.",
)

RETAINED_BINDINGS = ({'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/cache-opening-raw.json',
  'sha256': 'adffc25eff2b150de6c366f997d985be063e4eb3b5d18c995d93a9d662354126',
  'use': 'Identity corroboration only; no recovered quest behavior.',
  'lineage': None},
 {'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/game-main-667-opening-bindings.json',
  'sha256': '4d00762a5e7adf1edaee57b067605ae0c4c9cbe49d56fb52c4e7967062407358',
  'use': 'Identity corroboration only; no recovered quest behavior.',
  'lineage': None},
 {'body_path': '/Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/1360-enakhras-lament-sandstone-base-opening/sources/enakhra-contract.json',
  'sha256': '9c7bd4680c0f8d694ba4308b25dc5a589583f6f9a122c0f6276dcf933f3d66ba',
  'use': 'Retained lineage and limits; no recovered dialogue or original intermediate stages.',
  'lineage': {'schema_version': 1,
              'iteration': 136,
              'unit_id': 'quests-enakhras-lament',
              'target': 'November 2012 pre-EOC',
              'verdict_ceiling': 'PARTIAL[source_blocked]',
              'baseline_world_commit': 'f48cfc6b67af91ae4af175e6f672da28aa4f371b',
              'baseline_world_tree': 'f99493b0a947170a542716faf233d500eedcb38a',
              'cache_commit': '3947b57bba01516ab126906042ec96ca0c555739',
              'cache_tree': 'c7e124976375c851f398a64089de12781e7a9911',
              'evidence_boundaries': {'dated_primary': [{'file': 'enakhras-lament-build727-oldid-5972414.json',
                                                         'timestamp': '2012-07-22T03:13:33Z',
                                                         'sha256': 'af3cc49c9fb0a5f815ca3bf0a1d66c4f16a24577e849de06d4c4a60e5f5d0c20'},
                                                        {'file': 'enakhras-lament-final-preeoc-oldid-6548386.json',
                                                         'timestamp': '2012-11-11T21:18:24Z',
                                                         'sha256': 'ca723f90e744487a5c9ced20050bd823ba57b31aa79687add2fe787ab08f77f5'}],
                                      'focused_sources': [{'file': 'enakhras-lament-camulet-oldid-6590797.json',
                                                           'sha256': 'f48e6d22fc79062eb633e6dd1490e64d736896229016857cb957694226f087f3'},
                                                          {'file': 'enakhras-lament-camel-mask-oldid-6590793.json',
                                                           'sha256': 'cd95f918531cf1ef4d5e042c03b42c8a2f4d9e1e98503a429af08ad09f87976d'},
                                                          {'file': 'enakhras-lament-lazim-oldid-6224209.json',
                                                           'sha256': '5d51270479a7f3ad568b251145251f4f41842b5bea189f8e78c24d25a90f7da6'},
                                                          {'file': 'enakhras-lament-temple-oldid-5906344.json',
                                                           'sha256': 'a5152ff161216f548edcb6743e176f357e99977fa1ce1f0094c7c8fb4644f4a4'},
                                                          {'file': 'enakhras-lament-akthanakos-oldid-6593600.json',
                                                           'sha256': 'e2a075b8baac655912e8f5575a3e61d67e2574dd337443098c3efbf83d8cb694'},
                                                          {'file': 'enakhras-lament-pentyn-oldid-6225062.json',
                                                           'sha256': '83180bb6030f9f6e6a2808a48708d82b10345e64138af59ba88816716dffb16a'},
                                                          {'file': 'enakhras-lament-boneguard-oldid-6352071.json',
                                                           'sha256': 'e4bf192ce7d032c7addd1841beef97b0ea57735272a0cb89cb29954f1032b45e'},
                                                          {'file': 'enakhras-lament-stone-head-oldid-5503900.json',
                                                           'sha256': '6bf61992515aef2efe61e86a865aff496bf4b8fed71f78ef3e0d3e0cf697f897'},
                                                          {'file': 'enakhras-lament-ugthanki-dung-oldid-6288566.json',
                                                           'sha256': '44c1021fc5527d38da282e4519ebc14f2ce60f9844c459a38dcac33008ab6065'}],
                                      'transcript_history': {'file': 'enakhras-lament-transcript-history.json',
                                                             'sha256': '7942c0c6a8874a983cdb83e4c634ef1b0ffbb12e256b71ab3d99118051326e03',
                                                             'finding': 'Neither transcript title has a pre-cutoff revision; the '
                                                                        'earliest colon-title revision is 2013-10-23 and the '
                                                                        'slash title begins in 2016.'},
                                      'cache': 'openrs2-cache-727-742-enakhras-lament.json',
                                      'game_main_revision_667': 'The local revision-667 emulator supplies identities, varbit '
                                                                '1560, and a surface Lazim continuity spawn only; no quest '
                                                                'behavior was recovered.'},
              'requirements': {'quest_points': 0,
                               'completed_quests': [],
                               'skills': [{'skill': 'Crafting', 'level': 50, 'boostable': False},
                                          {'skill': 'Firemaking', 'level': 45, 'boostable': True},
                                          {'skill': 'Prayer',
                                           'level': 43,
                                           'boostable': True,
                                           'qualification': '71 when using Ancient curses for Deflect Melee'},
                                          {'skill': 'Magic', 'level': 39, 'boostable': True}],
                               'optional_skill': {'skill': 'Mining',
                                                  'level': 45,
                                                  'purpose': 'obtain granite, sandstone, and coal during the quest'},
                               'start_npc': {'id': 3147, 'name': 'Lazim', 'wrapper_ids': [3143, 3144, 3145, 3146]}},
              'client_state_contract': {'main_progress_varbit': 1560,
                                        'started': 10,
                                        'completed': 70,
                                        'intermediate_stages': {'statue_build': 10,
                                                                'temple_entry': 20,
                                                                'outer_doors': 30,
                                                                'pedestal': 40,
                                                                'globes': 50,
                                                                'boneguards_and_wall': 60},
                                        'intermediate_stage_standing': 'Correctness checkpoints inferred between the '
                                                                       'cache-proven 10 and 70 endpoints; no claim is made that '
                                                                       'the original server used these exact intermediate '
                                                                       'values.',
                                        'npc_wrapper_varbits': [{'id': 1604, 'purpose': 'Lazim surface transform'},
                                                                {'id': 1605, 'purpose': 'Enakhra transform'},
                                                                {'id': 1606, 'purpose': 'Boneguard/Akthanakos transform'}]},
              'quest_route': ['Lazim starts only when base Crafting is at least 50 and current Firemaking, Prayer, and Magic '
                              'satisfy the dated requirements. Mining 45 is helpful but not a start gate.',
                              'Lazim accepts exactly 32 kg of sandstone before returning item 6986. A chisel or toolbelt '
                              'converts it to base 6988; the flat-ground placement then opens a separate exact 20 kg collection '
                              'and body 6987 path.',
                              'A 5 kg granite block and chisel produce the accepted Lazim head. The own-head choice is refused. '
                              'Placing the accepted head collapses the statue and enters the temple.',
                              'The M sigil and four statue limbs are unique recoverable custody items. Each outer door consumes '
                              'or marks its matching limb; the three remaining sigils are collected in the dated route before '
                              'Lazim returns the head and the four inner sigil doors are opened.',
                              'The undersized head is placed on the central pedestal. Soft clay makes camel mould 7001; a second '
                              '5 kg granite block and chisel make camel-cavity head 7002, which unlocks the globe puzzle. '
                              'Postquest soft clay on the middle pedestal produces unlimited camel masks.',
                              "Pentyn's blood globe consumes bread or cake and requires all three questions. Fire Bolt or better "
                              'thaws the fountain, six exact fuel items light the six braziers, and Wind Bolt or better clears '
                              'the furnace. The barrier opens only after all four globes and the dated Lazim/Pentyn gates.',
                              'Crumble Undead changes the first Boneguard to a pile of bones. The second Boneguard requires '
                              'Protect from Melee or Deflect Melee; three rubble blocks are then placed and chiseled as three '
                              'ordered wall segments before Akthanakos is revealed.',
                              'Completion grants two quest points, 7,000 XP each in Crafting, Mining, Firemaking, and Magic, and '
                              'one Camulet exactly once. The five big bones are loot from the first guard rather than a '
                              'completion reward; Squeal of Fortune spins are excluded.'],
              'completion': {'quest_points': 2,
                             'xp': [{'skill': 'Crafting', 'amount': 7000},
                                    {'skill': 'Mining', 'amount': 7000},
                                    {'skill': 'Firemaking', 'amount': 7000},
                                    {'skill': 'Magic', 'amount': 7000}],
                             'items': [{'id': 6707, 'name': 'Camulet', 'amount': 1}],
                             'services': [{'provider': 'Lazim',
                                           'service': 'Recover a lost Camulet',
                                           'multiples_via_drop_trick': True},
                                          {'provider': 'middle pedestal',
                                           'service': 'Create a Camel mask from soft clay',
                                           'limit': 'unlimited'},
                                          {'item': 6707,
                                           'service': 'Check shared charge count and teleport to the quarry surface',
                                           'maximum_charges': 4,
                                           'charge_scope': 'shared across all copies'},
                                          {'item': 4601, 'service': 'Recharge all Camulet copies to four charges'}],
                             'downstream': ['Camulet camel dialogue', 'The Temple at Senntisten', 'Ritual of the Mahjarrat'],
                             'excluded': ['Squeal of Fortune spins', 'five big bones as completion-window grant']},
              'runtime_acceptance': {'rows': ['registration_requirements_client_endpoints_and_wrapper_vars_are_exact',
                                              'sandstone_weights_chisel_base_body_head_and_surface_entry_are_transactional',
                                              'fall_limb_custody_outer_doors_sigils_and_recovery_are_ordered',
                                              'pedestal_mould_camel_head_inner_doors_and_mask_service_are_stage_scoped',
                                              'pentyn_blood_fire_fountain_six_braziers_wind_furnace_and_barrier_are_exact',
                                              'crumble_boneguard_pile_prayer_gate_rubble_and_three_wall_segments_are_ordered',
                                              'completion_rewards_downstream_and_replay_are_idempotent',
                                              'camulet_shared_charges_recharge_recovery_teleport_and_camel_dialogue_unlock_are_durable'],
                                     'headless_world_only': True,
                                     'live_runescape_or_rs3_client_forbidden': True,
                                     'custom_darkan_client_last_resort': True},
              'source_blocked': ['Exact pre-cutoff dialogue, choices, camera, animation, sound, and cutscene presentation.',
                                 'Exact original intermediate stage values between cache-proven varbit 1560 endpoints 10 and 70, '
                                 'plus exact thresholds and meanings of wrapper varbits 1604, 1605, and 1606.',
                                 'Exact surface start, collapse, re-entry, and Camulet teleport tiles; the implementation may '
                                 'use the revision-667 Lazim continuity area and cache-proven temple placements with disclosure.',
                                 'Exact damage, prayer-guard attack cadence, spell projectile timing, rune consumption edge '
                                 'presentation, and brazier insect timing.',
                                 'Exact full-inventory, item-loss, replay, relog, and recovery dialogue and presentation.',
                                 'Exact NPC movement bounds, historic spawn ownership, and the Enakhra/Akthanakos departure '
                                 'choreography.']}})

ENAKHRA_OPENING_ITEMS = {
    BLOCK: dict(category="material", item_id=BLOCK_ID, stackable=False, tradeable=False,
                source="https://runescape.wiki/w/index.php?title=Sandstone_(32kg)&oldid=6049281"),
    BASE: dict(category="material", item_id=BASE_ID, stackable=False, tradeable=False,
               source="https://runescape.wiki/w/index.php?title=Sandstone_base&oldid=4831227"),
}
ENAKHRA_OPENING_CLEANUPS = (
    QuestStageRequirementCleanup(
        stage=1, remove_required_inventory=("Sandstone", "Runes", "Logs", "Oak logs", "Willow logs", "Maple logs", "Coal"),
        remove_required_inventory_options=("Waterskin", "Enchanted water tiara"), remove_required_tools=(CHISEL,),
        remove_required_actions=("Complete Enakhra's Lament stage 1 objective",), add_required_actions=(PROOFS["place_base"],),
    ),
    QuestStageRequirementCleanup(stage=4, remove_required_inventory=("Fire Bolt",)),
    QuestStageRequirementCleanup(
        stage=5, remove_required_inventory=("Crumble Undead", "Wind Bolt"),
        remove_required_actions=("Complete Enakhra's Lament stage 5 objective",),
        add_required_actions=("Cast Crumble Undead during the boneguard fight",),
        add_required_inventory=(("Logs", 1), ("Oak logs", 1), ("Willow logs", 1), ("Maple logs", 1), ("Coal", 1)),
    ),
)
