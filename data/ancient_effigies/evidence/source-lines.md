# Literal supplying lines

These are source data, not instructions. Line numbers are from the saved original body; HTML markup is preserved. Full source metadata and SHA-256 are in source-register.json and evidence.md.

## DK — src/main/java/com/rs/game/content/AncientEffigies.java
`sources/darkan-AncientEffigies.java.txt` — SHA-256 `77efd801a8de0503ad516881738b128e25201d98ff3c1874459c480d98d88d2a`

```text
37: 	public static final int[] SELF_SKILLS = { Constants.AGILITY, Constants.THIEVING, Constants.FIREMAKING, Constants.FISHING, Constants.WOODCUTTING, Constants.HUNTER, Constants.MINING, Constants.SUMMONING };
38: 	public static final int[] ASSISTABLE_SKILLS = { Constants.CRAFTING, Constants.CONSTRUCTION, Constants.COOKING, Constants.FARMING, Constants.FLETCHING, Constants.HERBLORE, Constants.SMITHING, Constants.RUNECRAFTING };
39: 	public static final int STARVED_ANCIENT_EFFIGY = 18778, NOURISHED_ANCIENT_EFFIGY = 18779, SATED_ANCIENT_EFFIGY = 18780, GORGED_ANCIENT_EFFIGY = 18781, DRAGONKIN_LAMP = 18782, MINAS_LAMP = 18783;
40: 	private static final String TYPE_KEY = "effigyType";
46: 	public static ItemClickHandler handleEffigies = new ItemClickHandler(new Object[] { STARVED_ANCIENT_EFFIGY, NOURISHED_ANCIENT_EFFIGY, SATED_ANCIENT_EFFIGY, GORGED_ANCIENT_EFFIGY }, event -> {
49: 		int type = ensureType(player, item);
58: 						option(Constants.SKILL_NAME[selfSkill], dialogueFor(player, item, selfSkill, type));
59: 						option(Constants.SKILL_NAME[assistableSkill], dialogueFor(player, item, assistableSkill, type));
64: 	private static Dialogue dialogueFor(Player player, Item item, int skill, int type) {
65: 		int requiredLevel = getRequiredLevel(item.getId());
66: 		if (!canInvestigate(player, skill, requiredLevel))
67: 			return new Dialogue().addSimple("The images in your mind fade; the ancient effigy seems to desire knowledge of experiences you have not yet had.", () -> failLevelCheck(player, skill, requiredLevel));
74: 	private static void failLevelCheck(Player player, int skill, int requiredLevel) {
75: 		player.sendMessage("You require at least level " + requiredLevel + " " + Constants.SKILL_NAME[skill] + " to investigate the ancient effigy further.");
79: 	public static boolean canInvestigate(Player player, int skill, int requiredLevel) {
80: 		return player.getSkills().getLevel(skill) >= requiredLevel || AssistSystem.providerFor(player, skill, requiredLevel) != null;
83: 	public static InvestigationResult investigate(Player player, Item expectedItem, int skill, int type, long now) {
84: 		Item current = player.getInventory().getItem(expectedItem.getSlot());
85: 		if (current == null || current.getId() != expectedItem.getId() || readType(current) != type)
86: 			return InvestigationResult.STALE;
89: 		if (player.getSkills().getLevel(skill) >= requiredLevel) {
90: 			player.getSkills().addXpLamp(skill, xp);
91: 			player.sendMessage("You have gained " + xp + " " + Constants.SKILL_NAME[skill] + " experience!");
92: 			advance(player, current, type);
95: 		Player provider = AssistSystem.providerFor(player, skill, requiredLevel, now);
96: 		if (provider == null)
97: 			return InvestigationResult.INSUFFICIENT;
105: 	public static int ensureType(Player player, Item item) {
106: 		int type = readType(item);
107: 		if (type >= 0)
108: 			return type;
109: 		type = Utils.getRandomInclusive(7);
110: 		player.getInventory().replace(item, new Item(item.getId(), item.getAmount()).addMetaData(TYPE_KEY, type));
114: 	public static int readType(Item item) {
115: 		Object value = item.getMetaData(TYPE_KEY);
120: 		return raw == type && type >= 0 && type < SELF_SKILLS.length ? type : -1;
123: 	public static int nextType(int currentType, int roll) {
124: 		if (currentType < 0 || currentType >= SELF_SKILLS.length || roll < 0 || roll >= SELF_SKILLS.length - 1)
125: 			throw new IllegalArgumentException("Invalid effigy pair transition");
126: 		return roll >= currentType ? roll + 1 : roll;
131: 			case STARVED_ANCIENT_EFFIGY -> 91;
132: 			case NOURISHED_ANCIENT_EFFIGY -> 93;
133: 			case SATED_ANCIENT_EFFIGY -> 95;
134: 			case GORGED_ANCIENT_EFFIGY -> 97;
155: 			case STARVED_ANCIENT_EFFIGY -> 15000;
156: 			case NOURISHED_ANCIENT_EFFIGY -> 20000;
157: 			case SATED_ANCIENT_EFFIGY -> 25000;
158: 			case GORGED_ANCIENT_EFFIGY -> 30000;
163: 	public static void advance(Player player, Item item, int currentType) {
165: 		if (item.getId() == GORGED_ANCIENT_EFFIGY) {
167: 			inventory.replace(item, new Item(DRAGONKIN_LAMP, 1));
172: 		int nextItemId = item.getId() + 1;
173: 		int nextType = nextType(currentType, Utils.getRandomInclusive(6));
174: 		inventory.replace(item, new Item(nextItemId, 1).addMetaData(TYPE_KEY, nextType));
```

## A — Ancient effigies
`sources/ancient-effigies-6510644.txt` — SHA-256 `f76b81ecfc9d92c7caba649ff788cf9b90d6807b53fbca71ba6b8e786226edcf`

```text
3: [[File:Starved ancient effigy detail.png|left|100px]]'''Ancient effigies''' are a part of the [[Distractions and Diversions]] released on the [[15 June]] [[2010]]. They require nourishment which is supplied by knowledge in particular skills with a level range of '''91 to 97''', with there being four stages for each effigy. The reward from doing so is an amount of experience in the skill used to nourish that effigy, and after the fourth stage a [[dragonkin lamp]] appears, which grants experience in any skill relative to skill level.
7: Each effigy can be nourished in one of two skills. The effigies are interested in only a limited set of skills ([[Agility]], [[Crafting]], [[Construction]], [[Thieving]], [[Cooking]], [[Firemaking]], [[Fishing]], [[Farming]], [[Fletching]], [[Woodcutting]], [[Herblore]], [[Hunter]], [[Mining]], [[Smithing]], [[Runecrafting]], and [[Summoning]]).[[Dungeoneering]], [[Slayer]], and all combat skills other than Summoning are not associated with this Distraction and Diversion.
10: When an effigy is nourished, the skills its next level needs are reset. For example, an effigy that first wants nourishment in Hunter or Herblore will next want nourishment in two different skills (say, Thieving and Construction).
14: Players can possess multiple effigies. However, as of [[14 February]] [[2012]], it is no longer possible to gain effigies if you have 5 or more sitting in the bank. They do not stack in the bank, regardless of what stage they are at or what skills they require. Jagex also stated with this update that there will now be a permanent reduction in the drop rates of Ancient Effigies.
16: Since effigies can't be sorted by appearance, they can by sorted by placing them next to related materials in your bank. For example, an effigy which needs Construction assistance could be placed by some planks. Likewise, an effigy which requires Smithing assistance could be placed by ores and bars, and effigies which require Herblore assistance could be placed by potions or herbs, and so forth.
94: # [[Starved ancient effigy]] - This will require at least a level of 91 in one of the two skills to investigate; after investigation it becomes nourished, rewarding 15,000 experience in the skill used.
95: # [[Nourished ancient effigy]] - This will require at least a level of 93 in one of the two skills to investigate; after investigation it becomes sated, rewarding 20,000 experience in the skill used.
96: # [[Sated ancient effigy]] - This will require at least a level of 95 in one of the two skills to investigate; after investigation it becomes gorged, rewarding 25,000 experience in the skill used.
97: # [[Gorged ancient effigy]] - This will require at least a level of 97 in one of the two skills to investigate; after investigation it provides 30,000 experience in the skill used and, then crumbles to dust, leaving behind a [[dragonkin lamp]].
99: The formula for the lamp is <math>\frac{x^3-2x^2+100x}{20}</math>, in which <math>x</math> is the skill level. For example, at a skill level of 60, the experience gained would be <math>\frac{60^3-2*60^2+100*60}{20}=10,740</math>. A complete table can be found [[Dragonkin lamp|here]]. A rough estimate of the exp gained can be found by simply cubing the level and then dividing by 20.
101: After players have enlightened an entire ancient effigy - from its starved form to its gorged form - they will have received a total of 90,000 experience across the skills used and a [[Dragonkin lamp]] which has the same use as a regular experience lamp but with a larger amount of experience depending upon the level in the skill used.
111: [[Boost]]s will work, as well as for those assisting.
119: | {{Skill clickpic|crafting}} [[Crafting]]
120: | {{Skill clickpic|agility}} [[Agility]]
122: | {{Skill clickpic|construction}} [[Construction]]
123: | {{Skill clickpic|thieving}} [[Thieving]]
125: | {{Skill clickpic|cooking}} [[Cooking]]
126: | {{Skill clickpic|firemaking}} [[Firemaking]]
128: | {{Skill clickpic|farming}} [[Farming]]
129: | {{Skill clickpic|fishing}} [[Fishing]]
131: | {{Skill clickpic|fletching}} [[Fletching]]
132: | {{Skill clickpic|woodcutting}} [[Woodcutting]]
134: | {{Skill clickpic|herblore}} [[Herblore]]
135: | {{Skill clickpic|hunter}} [[Hunter]]
137: | {{Skill clickpic|smithing}} [[Smithing]]
138: | {{Skill clickpic|mining}} [[Mining]]
140: | {{Skill clickpic|runecrafting}} [[Runecrafting]]
141: | {{Skill clickpic|summoning}} [[Summoning]]
157: Note that only visible boosts can be used to open effigies.
```

## S — Starved ancient effigy
`sources/starved-ancient-effigy-6564000.txt` — SHA-256 `5d73687aff752d32e2081d839b44dd00c79e7d78d275ee6c2c2574593e89c288`

```text
20: A '''Starved ancient effigy''' can be obtained as drops from many monsters around ''[[Runescape]]'', as part of the [[ancient effigies]] [[Distractions and Diversions]]. The more powerful the monster, the more likely the drop. It requires level 91 in the skill it craves knowledge in to nourish, but it can be banked until you can or choose to use it, or you may exchange it for a 5,000 experience Antique lamp (for any skill level 50 or more) by talking to [[Historian Minas]] at Varrock Museum. When given knowledge, it will become a [[nourished ancient effigy]] and will grant 15,000 experience in the skill that was used to nourish it. The nourished ancient effigy will need level 93 in a certain skill. This skill can be different from the ones needed for the starved ancient effigy. The [[Assist System]] can be used to nourish an effigy, however the assisting player will get all of the 15,000 experience points. No effigies of any type will stack in the bank.
```

## J — Jagex: Ancient Effigy
`sources/official-singular-20121009063538.html` — SHA-256 `2dd693577ad0ad6a0f656d4bbc12d4d12423a08387c3e31e54e4fd3252c64451`

```text
608: <td align="center"><a href="/m=rswiki/en/Crafting" title="Crafting">Crafting</a></td>
610: <td align="center"><a href="/m=rswiki/en/Agility" title="Agility">Agility</a></td>
613: <td align="center"><a href="/m=rswiki/en/Construction" title="Construction">Construction</a></td>
615: <td align="center"><a href="/m=rswiki/en/Thieving" title="Thieving">Thieving</a></td>
618: <td align="center"><a href="/m=rswiki/en/Cooking" title="Cooking">Cooking</a></td>
620: <td align="center"><a href="/m=rswiki/en/Firemaking" title="Firemaking">Firemaking</a></td>
623: <td align="center"><a href="/m=rswiki/en/Farming" title="Farming">Farming</a></td>
625: <td align="center"><a href="/m=rswiki/en/Fishing" title="Fishing">Fishing</a></td>
628: <td align="center"><a href="/m=rswiki/en/Fletching" title="Fletching">Fletching</a></td>
630: <td align="center"><a href="/m=rswiki/en/Woodcutting" title="Woodcutting">Woodcutting</a></td>
633: <td align="center"><a href="/m=rswiki/en/Herblore" title="Herblore">Herblore</a></td>
635: <td align="center"><a href="/m=rswiki/en/Hunter" title="Hunter">Hunter</a></td>
638: <td align="center"><a href="/m=rswiki/en/Smithing" title="Smithing">Smithing</a></td>
640: <td align="center"><a href="/m=rswiki/en/Mining" title="Mining">Mining</a></td>
643: <td align="center"><a href="/m=rswiki/en/Runecrafting" title="Runecrafting">Runecrafting</a></td>
645: <td align="center"><a href="/m=rswiki/en/Summoning" title="Summoning">Summoning</a></td>
648: <p><br />
650: <p>The skills which can be used to successfully investigate an effigy will always be paired, though, so you at least have some choice of which to use; the pairings are listed at right.</p>
651: <p>It's not quite so simple, though, as you will need to be particularly knowledgeable in at least one of the pair of skills craved by the effigy to investigate it successfully.</p>
653: <li><a href="/m=rswiki/en/Starved_ancient_effigy" title="Starved ancient effigy">Starved ancient effigies</a> require a skill level of at least 91 to investigate, and become nourished.</li>
654: <li><a href="/m=rswiki/en/Nourished_ancient_effigy" title="Nourished ancient effigy">Nourished ancient effigies</a> require a skill level of at least 93 to investigate, and become sated.</li>
655: <li><a href="/m=rswiki/en/Sated_ancient_effigy" title="Sated ancient effigy">Sated ancient effigiesrequire</a> a skill level of at least 95 to investigate, and become gorged.</li>
656: <li><a href="/m=rswiki/en/Gorged_ancient_effigy" title="Gorged ancient effigy">Gorged ancient effigies</a> require a skill level of at least 97 to investigate, and will crumble to dust, producing a dragonkin lamp, their mysterious purpose fulfilled.</li>
657: <li><a href="/m=rswiki/en/Dragonkin_lamp" title="Dragonkin lamp">Dragonkin lamps</a> may be spent on a skill and provide approximately  one-twentieth of the skill level cubed in experience (see the item article for a complete accurate table of values for each level).</li>
661: <p>Each time you successfully investigate an ancient effigy, it will reward you with experience in the skill that you used to feed it. Starved effigies award 15,000XP; nourished effigies award 20,000XP; sated effigies award 25,000XP; and gorged effigies award 30,000XP.</p>
662: <p>For example: <i>A player receives a starved ancient effigy as a drop that craves knowledge of either Fishing or Farming. Their Farming level is only 65, so they cannot use that skill to investigate the effigy, but they do have 94 Fishing, which is above the level 91 minimum requirement. They use their Fishing skill to investigate the starved ancient effigy and receive 15,000 Fishing XP; the ancient effigy becomes nourished and now craves knowledge of either Herblore or Hunter.</i></p>
663: <p><i>The player now needs one of these two skills to be at least level 93 to investigate the effigy further. They do not have those levels, though, so will either need to train them up or find someone to aid them through the Assist System (you will always be able to get assistance with at least one of the skills an effigy craves).</i></p>
```

## TI — Tip.It: Ancient Effigy
`sources/tipit-old-20120419054059.html` — SHA-256 `785f5ce5949bd14f692179c31ebb46ba62a48ea58d6013b96f28a9f049726ba6`

```text
361: <p>Feeding an Effigy requires a certain pairing of skills, and each type of Effigy has a different skill level requirement. Having either one of the skills in the pairing at the required level is sufficient. For example, if an Effigy requires level 91 Mining or Smithing to investigate, having either skill at level 91 will allow you to do so. After feeding the Effigy, you will gain some experience, and it will either change into an Effigy of another type or crumble to dust and reveal a Dragonkin lamp. Note that if the Effigy changes type, the required skill pairing will change.</p>
373:   <td>91</td>
374:   <td><a href="?rs2item_id=10264">Nourished</a></td>
375:   <td>15,000 XP</td>
379:   <td>93</td>
380:   <td><a href="?rs2item_id=10265">Sated</a></td>
381:   <td>20,000 XP</td>
385:   <td>95</td>
386:   <td><a href="?rs2item_id=10266">Gorged</a></td>
387:   <td>25,000 XP</td>
391:   <td>97</td>
392:   <td><a href="?rs2item_id=10267">Dragonkin lamp</a></td>
393:   <td>30,000 XP</td>
407: <tr><td>Crafting</td><td>Agility</td></tr>
408: <tr><td>Construction</td><td>Thieving</td></tr>
409: <tr><td>Cooking</td><td>Firemaking</td></tr>
410: <tr><td>Farming</td><td>Fishing</td></tr>
411: <tr><td>Fletching</td><td>Woodcutting</td></tr>
412: <tr><td>Herblore</td><td>Hunter</td></tr>
413: <tr><td>Smithing</td><td>Mining</td></tr>
414: <tr><td>Runecrafting</td><td>Summoning</td></tr>
419: If a player feeds an Effigy until it crumbles to dust, they will receive a <a href="?rs2item_id=10267">Dragonkin lamp</a>. This lamp can be used to gain experience in a skill of your choice and cannot be banked. The exact amount of experience gained can be calculated with the formula <i>XP = (level^3 - 2 * level^2 + 100 * level) / 20</i>, where <i>level</i> is the level of the skill you wish to earn experience in.</p>
443:   var xp = Math.floor((Math.pow(level,3) - 2 * Math.pow(level,2) + 100 * level) / 20);
446:   printhtml = 'You will gain ' + outputComma(xp) + ' XP.';
```

## N — Nourished ancient effigy
`sources/nourished-ancient-effigy-5821163.txt` — SHA-256 `5609cfeba696f1e3e3eafe3094b7be72c728c06d736334e532d5fcf4bf11aa19`

```text
20: A '''Nourished ancient effigy''' is obtained by imbuing knowledge into a [[starved ancient effigy]]. If a player nourishes this effigy it will grant 20,000 experience in the skill which you give it knowledge in. A player may only put knowledge in for one of the two skills the effigy allows at the time, and will only allow players to nourish it if they have a level 93 or above in the skill that the effigy craves knowledge in. It can be banked until you can or choose to use it. Once it has been further nourished, this effigy will become [[sated ancient effigy]].
```

## T — Sated ancient effigy
`sources/sated-ancient-effigy-5783477.txt` — SHA-256 `d756f0a6c17624af70cdbcf273112c18d2cad5965ddee64ae88726e8f9617e2e`

```text
19: A '''Sated ancient effigy''' is one of the [[Ancient effigies]]. It can be obtained by imbuing knowledge into a [[Nourished ancient effigy]], which requires level 93 in the skill in which the nourished effigy craves knowledge. It requires a level of '''95''' in one of the two skills you can choose from to investigate. It then becomes a [[Gorged ancient effigy]], and reward 25,000 [[experience]] in the chosen skill. If the player does not have the required level, or for some other reason wishes to wait, it can be banked for later investigation.
```

## G — Gorged ancient effigy
`sources/gorged-ancient-effigy-6201896.txt` — SHA-256 `9f6d1def4f3a9a699c8846564f833cbc28e8364a3587682fb5b428d5e74d2a83`

```text
19: A '''Gorged ancient effigy''' is the fourth and final stage of an ancient effigy, requiring the highest [[skills|skill levels]] to complete. It can be obtained by imbuing knowledge into a [[Sated ancient effigy]], which requires at least level 95 in the skill in which it craves knowledge. A Gorged Ancient Effigy requires one of the two skills in which it requests knowledge to be at level 97 or greater; however, it can be banked until the player either has a sufficient skill level or can receive an assist via the [[assist system]]. Receiving an assist to investigate an effigy does not grant the owner of the effigy any experience; the full experience will be granted to the person giving the assist. Gorged Ancient Effigies do not stack, either in the inventory or in a bank. It will disappear upon investigating, granting 30,000 [[experience]] and a [[Dragonkin lamp]], which can be used for additional experience.
21: '''Note''': Dragonkin lamps may not be banked, thus some players may choose to keep their Gorged Ancient Effigies in the bank until they are ready to use their Dragonkin Lamps.
```

## U — Update:Ancient Effigies
`sources/update-ancient-effigies-3346081.txt` — SHA-256 `c19b082673a7abba31c7321a5b601ef1c22722aa45b33c140050d2b5611dc7fc`

```text
6: These ancient effigies seemingly possess a will of their own and desire knowledge from the adventurers who hold them. Initially, an effigy will require you to have level 91 in one of two skills (chosen randomly) to investigate it, from which you will receive healthy amounts of experience in the skill you choose. As effigies absorb more and more of your knowledge, they will require ever higher levels in other skills – level 93, then level 95, and, finally, level 97. If you can supply the ancient effigy with all the knowledge it seeks, you may discover something of the secrets it holds...
```

## RH — RuneHQ: Ancient Effigies
`sources/runehq-20120702024058.html` — SHA-256 `b77046a243d90002bd0bf03079a370fc9f5753dfa3d6dc0055be0404919cd4fc`

```text
210: To start, you will need to receive a <a href="/database.php?type=item&amp;id=20421">Starved ancient effigy</a> as a drop from a monster. The higher the monster's level, the more likely it is to drop one. Once you receive one, you can investigate it to figure out what skills as needed to feed the effigy to make it grow into the next stage.
216: An ancient effigy has 4 possible stages. To grow it into the next stage you will have to have the required levels to advance it. The lowest stage, the <a href="/database.php?type=item&amp;id=20421">Starved ancient effigy</a>, will require a level of 91 in either of the 2 levels it requires. You can use items to boost your level to reach that level, or  you can have someone assist you to reach it. After you feed the <a href="/database.php?type=item&amp;id=20424">Gorged ancient effigy</a>, it will crumble to dust and you will receive a Dragonkin lamp.
247: <p>
269: <li><a href="/database.php?type=item&amp;id=20424">Gorged ancient effigy</a> - 30k experience in the skill you choose to feed it as well as a Dragonkin lamp, which gives experience (Level^3/20).</li>
```

## RNG — Darkan core Utils.getRandomInclusive bytecode
`sources/darkan-core-2.0.5-Utils.javap.txt` — SHA-256 `a075ad68cbafab4fe3b701b1bb040783707a49bfc0e5ed413847eea76568ea80`

```text
3052:   public static final int getRandomInclusive(int);
3054:          0: invokestatic  #27                 // Method java/lang/Math.random:()D
3055:          3: iload_0
3056:          4: iconst_1
3057:          5: iadd
3058:          6: i2d
3059:          7: dmul
3060:          8: d2i
3061:          9: ireturn
```

## DS — src/main/java/com/rs/game/model/entity/player/Skills.java
`sources/darkan-Skills.java.txt` — SHA-256 `6dcc260df69a90462b0bc54c5fec42e83d373c672cb16242b8bd2dfc561eeda0`

```text
569: 	public int getLevel(int skill) {
570: 		return level[skill];
649: 	public int getLevelForXp(int skill) {
653: 		for (int lvl = 1; lvl <= (skill == Constants.DUNGEONEERING ? 120 : 99); lvl++) {
660: 	}
833: 	public double addXpLamp(int skill, double exp) {
841: 		if (Settings.getConfig().getXpRate() > 1)
842: 			exp *= Settings.getConfig().getXpRate();
844: 		xp[skill] += exp;
855: 		if (xp[skill] > MAXIMUM_EXP)
856: 			xp[skill] = MAXIMUM_EXP;
```

## DI — src/main/java/com/rs/game/model/entity/player/Inventory.java
`sources/darkan-Inventory.java.txt` — SHA-256 `20c0c8de13557f17d750c22a15c71dde68dfbabfa3834e762e97388ad6f817c8`

```text
202: 	public void replace(Item item, Item newItem) {
203: 		if (items.get(item.getSlot()) == null)
205: 		if (item.getId() != items.get(item.getSlot()).getId())
207: 		items.set(item.getSlot(), newItem);
```

## L — Dragonkin lamp
`sources/dragonkin-lamp-6350210.txt` — SHA-256 `19be1abf94d1cc11fe2484835bc2f3901594d3aacc4553ad44a24148a7d7ce88`

```text
2: |name = Dragonkin lamp
8: |tradeable = No
10: |stackable = No
14: |destroy = Rub this lamp to claim your reward - it will be destroyed in the process. If you choose to destroy it now, you cannot replace it.
22: A '''Dragonkin lamp''' is the final reward from the [[Ancient Effigies]] [[Distraction and Diversion]]. Its name references the [[Dragonkin]], though their connection to this artefact is currently unknown. It is an easy way for players who only use combat to level non-combat skills. It is received after investigating a [[gorged ancient effigy]] and receiving experience from it. This will require a level of at least 97 in one of the two skills that the effigy craves knowledge in, or using an assist from a player who already has the required levels if you do not. The fastest way to get assistance is by posting in the dedicated thread on the official Runescape forums and asking for it. Like most xp lamps, the dragonkin lamp may '''not''' be banked.
29: The dragonkin lamp can be used to gain experience in any skill. The amount of experience gained depends on the player's level in that skill (see calculator and chart below). After using a Dragonkin Lamp the player receives the message: "As you focus on your chosen memories, you feel a burning malevolence in the back of your mind. You have gained new insight into ''[skill]''... but at what cost?". The significance of this message is unknown and could hint at a sinister aspect of the lamp's powers.     
36: The '''exact''' experience gained is shown in the following table based on the following equation, where the floor function, <math>\lfloor x \rfloor</math>, means to round down to the nearest integer:
38: <math>\text{experience} = \left \lfloor \frac{\text{level}^3 - 2 \times \text{level}^2 + 100 \times \text{level}}{20}\right \rfloor</math>
46:  param = 1|Level||int|1-120
72: | 120|| 85,560 ||||90|| 36,090 ||||60|| 10,740 ||||30|| 1,410
114: | 99|| 48,029 ||||69|| 16,294 ||||39|| 3,008 ||||9|| 73
130: | 91|| 37,305 ||||61|| 11,281 ||||31|| 1,548 ||||1||4
```

## DL — src/main/java/com/rs/game/content/items/Lamps.java
`sources/darkan-Lamps.java.txt` — SHA-256 `3edbbcc3feaebc9781dff1b044422ef9a324e221bb1eebe67524e425386962a4`

```text
45: 	public static final int[] SELECTABLE_XP_LAMPS = { 23713, 23714, 23715, 23716, 12628, 18782, 20935, 20936, 20960 };
78: 	private static final int[] DIALOGUE_INTERFACE_CS2 = { Skills.ATTACK, Skills.MAGIC, Skills.MINING, Skills.WOODCUTTING, Skills.AGILITY, Skills.FLETCHING, Skills.THIEVING, Skills.STRENGTH, Skills.RANGE, Skills.SMITHING, Skills.FIREMAKING, Skills.HERBLORE, Skills.SLAYER, Skills.CONSTRUCTION, Skills.DEFENSE, Skills.PRAYER, Skills.FISHING, Skills.CRAFTING, Skills.FARMING, Skills.HUNTER, Skills.SUMMONING, Skills.HITPOINTS, Skills.DUNGEONEERING, Skills.COOKING, Skills.RUNECRAFTING };
126: 			default -> 1;
136: 	public static void openSelectableInterface(Player player, int slot, int id) {
140: 			Item selectedLamp = player.getInventory().getItem(slot);
141: 			if (selectedLamp == null || selectedLamp.getId() != lamp.getId()) {
142: 				player.getTempAttribs().removeO("lampInstance");
143: 				player.closeInterfaces();
144: 				return;
146: 			int lvl = player.getSkills().getLevelForXp(lamp.getSelectedSkill());
147: 			if (lvl < lamp.getReq())// makes unmet req skill xp unclickable
159: 			int lampsBefore = player.getInventory().getAmountOf(lamp.getId());
160: 			player.getInventory().deleteItem(slot, new Item(lamp.getId(), 1));
161: 			if (player.getInventory().getAmountOf(lamp.getId()) != lampsBefore - 1)
162: 				return;
164: 			if (lamp.getId() == 18782)
165: 				xpAmt = dragonkinLampXp(lvl);
195: 			double exp = player.getSkills().addXpLamp(lamp.getSelectedSkill(), xpAmt);
197: 			player.getTempAttribs().removeO("lampInstance");
199: 		lampD.addNext(() -> player.getTempAttribs().removeO("lampInstance"));
201: 		player.setCloseInterfacesEvent(() -> player.getTempAttribs().removeO("lampInstance"));
204: 	public static int dragonkinLampXp(int level) {
205: 		return (int) Math.floor((Math.pow(level, 3) - 2 * Math.pow(level, 2) + 100 * level) / 20.0);
```

## DG — Dungeoneering
`sources/dungeoneering-6579699.txt` — SHA-256 `e7a3b744db3d2d14c7e2c2e306e8f5e8c70d6c4a005d71ded6c7859861b30c64`

```text
23: Players can train Dungeoneering past [[level 99]] up to [[level 120]], at which point players will have over 104 million experience. This new maximum level, which is only applied to Dungeoneering, is called "[[True Skill Mastery]]".
776: *It has a maximum level of 120, whereas all other skills are capped at level 99.
```

## AV — logic/inventory_pure.py
`sources/ankiscape-logic__inventory_pure.py.txt` — SHA-256 `d69db3d436ede3f917098f035b0dd1d107ce6f95be39e468f27e1cb44c414527`

```text
1: """Pure carried-inventory helpers for AnkiScape.
3: The flat inventory remains the bank. This module models the 28-slot carried
4: overlay and the pouch-only coin balance without importing Anki or UI code.
```

## AE — logic/equipment_instance_logic.py
`sources/ankiscape-logic__equipment_instance_logic.py.txt` — SHA-256 `d1733c40b78ed678d38854972f725195176a55207e8ae771609b2303bcdfdfaa`

```text
125: def sanitize_equipment_instance_state_pure(
129:     # Shallow on purpose: the ledger below is rebuilt as fresh records, and
132:     raw_instances = data.get("equipment_instances", {})
145:                 max_seen_id = max(max_seen_id, _clean_int(raw_id.removeprefix("equipment-"), 0))
146:             if family_id not in condition_data:
149:                 # another feature's rows through rather than discard them. Rows
151:                 if family_id in EQUIPMENT_CONDITION_DATA:
152:                     foreign[raw_id] = dict(raw_record)
248: def add_equipment_instance_pure(
255:     item_name = condition_name_pure(family_id, maximum, condition_data)
256:     instance_id = f"equipment-{data['equipment_instance_next_id']}"
258:     data["equipment_instances"][instance_id] = {
259:         "family_id": family_id,
260:         "item_name": item_name,
261:         "condition": maximum,
262:         "location": "bank",
264:     inventory = dict(data.get("inventory", {}) or {})
265:     inventory[item_name] = _clean_int(inventory.get(item_name), 0) + 1
266:     data["inventory"] = inventory
```

## AI — __init__.py
`sources/ankiscape-__init__.py.txt` — SHA-256 `6e475caba39fd28c432d0faf63ed4f7ff713eb51cdb4bbf71fce02f83063bb44`

```text
799: ):
801: 
802:     `apply_change` receives the live save and returns `(updated, ok)`. Returning
803:     `ok=False` refuses the action: nothing is written and the random state is put
804:     back, so a refusal the player never saw cannot advance the sequence. Optional
805:     `after_apply` work runs after the undo entry exists but before the save commit;
806:     a raise there or in the save restores the snapshot, and that entry's Undo is a no-op.
819: 
820:     before = _capture_player_data_snapshot()
821:     updated, ok = apply_change(_state.player_data)
822:     if not ok:
823:         random.setstate(before["random_state"])
824:         return False
838:     updated = runtime_actions.drop_superseded_bank_run_requests_pure(before["player_data"], updated)
839:     try:
840:         mw.col.add_custom_undo_entry(_DIRECT_ACTION_UNDO_OPERATION)
841:     except (AttributeError, RuntimeError):
850:         if switch_to_bankstanding:
851:             _switch_to_bankstanding(
852:                 bankstanding_reason,
859:         save_player_data()
1147: def _capture_player_data_snapshot(*, review_answer=False):
1157:         before_player_data = copy.deepcopy(_state.player_data)
1159:         "player_data": before_player_data,
1161:         "random_state": random.getstate(),
1256: def _restore_direct_action_snapshot(snapshot) -> None:
1258:     _state.player_data.update(copy.deepcopy(snapshot["player_data"]))
1261:     if random_state is not None:
1262:         random.setstate(random_state)
1263:     save_player_data()
```

## AS — core/storage.py
`sources/ankiscape-core__storage.py.txt` — SHA-256 `5ef2a7786484909f135b048db4779d1c6fa3d2b1446d39a3ecebb953d0b1744c`

```text
25: def _save_player_data_config(player_data: dict) -> None:
28:         mw.col.set_config(_PLAYER_DATA_KEY, player_data)
69: def load_player_data():
73:         player_data = migrate_loaded_data(deepcopy(loaded), ORE_DATA, ITEM_DEFINITIONS)
81: def save_player_data(player_data: dict, current_skill: str) -> None:
83:     if carried := player_data.get("carried_inventory"):
87:             if (clamped := clamp_carried_view_to_bank(view, player_data.get("inventory")))
90:     mw.col.set_config("ankiscape_current_skill", current_skill)
```

## AB — data/bork_data.py
`sources/ankiscape-data__bork_data.py.txt` — SHA-256 `6efa48b726823e7d5748c383d8acd952df7e96dcc6de9b2815519cc09185c70a`

```text
17: BORK_EFFIGY_ITEM = "Starved ancient effigy"
83:     (BORK_EFFIGY_ITEM, 1.0 / 64.0),
```

## AG — data/farming_skill_guide_data.py
`sources/ankiscape-data__farming_skill_guide_data.py.txt` — SHA-256 `e9359c414408c341f769e0e4671c3d206ca42f140e9fb7e00f29cd1fe0e35a57`

```text
171:         (3516, "Starved ancient effigy", 91, 18778, 21, 5, None),
172:         (3517, "Nourished ancient effigy", 93, 18779, 21, 5, None),
173:         (3518, "Sated ancient effigy", 95, 18780, 21, 5, None),
174:         (3519, "Gorged ancient effigy", 97, 18781, 21, 5, None),
```

## AC — memory-bank/source-audits/recon-coverage-closure-2026-07-18.md
`sources/ankiscape-closure.md` — SHA-256 `06807db8e4e4f6df596bacbbc8e44c72d8f3105551f8bbddd36dbfef3fc8d40d`

```text
60: - **Existing item-stage/effect systems:** Ancient Effigies (own-levels only;
61:   the source assist system stays under the multiplayer exclusion), Oo'glog
62:   spa buffs as sourced timed effects on the world clock.
```

