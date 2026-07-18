"""Source-pinned Warriors' Guild activity, token, and defender data."""

from __future__ import annotations


WARRIORS_GUILD_SOURCE = "RuneScape Wiki Warriors' Guild oldid=6565080"
ANIMATED_ARMOUR_SOURCE = "RuneScape Wiki Animated Armour oldid=6538652"
DEFENDER_SOURCE = "RuneScape Wiki Defenders oldid=6513277"
CYCLOSSUS_SOURCE = "RuneScape Wiki Cyclossus oldid=6510357"
DARKAN_WARRIORS_GUILD_SOURCE = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
    "darkan-world-server/src/main/java/com/rs/game/content/minigames/"
    "warriors_guild/WarriorsGuild.kt"
)

WARRIORS_GUILD_TOKEN_KEYS = (
    "combat",
    "attack",
    "defense",
    "strength",
    "balance",
)

WARRIORS_GUILD_ACTIVITY_IDS = (
    "warriors_guild_animated_armour",
    "warriors_guild_attack_dummy",
    "warriors_guild_catapult",
    "warriors_guild_shot_put",
    "warriors_guild_keg_balance",
)

WARRIORS_GUILD_ACTIVITIES = {
    "warriors_guild_animated_armour": {
        "display_name": "Animated armour",
        "group": "warriors_guild",
        "requirements": {},
        "batch_size": 1,
        "warriors_guild_activity": True,
        "token_key": "combat",
        "summary": "Animate and defeat the strongest complete metal armour set in your bank.",
        "source": f"{ANIMATED_ARMOUR_SOURCE}; {DARKAN_WARRIORS_GUILD_SOURCE}:392-423",
    },
    "warriors_guild_attack_dummy": {
        "display_name": "Attack dummies",
        "group": "warriors_guild",
        "requirements": {},
        "batch_size": 1,
        "warriors_guild_activity": True,
        "token_key": "attack",
        "summary": "Read the raised dummy and answer with its matching attack style.",
        "source": f"{WARRIORS_GUILD_SOURCE}; {DARKAN_WARRIORS_GUILD_SOURCE}:494-524",
    },
    "warriors_guild_catapult": {
        "display_name": "Catapult defence",
        "group": "warriors_guild",
        "requirements": {},
        "batch_size": 1,
        "warriors_guild_activity": True,
        "token_key": "defense",
        "summary": "Use Gamfred's defensive shield to deflect one incoming projectile.",
        "source": f"{WARRIORS_GUILD_SOURCE}; {DARKAN_WARRIORS_GUILD_SOURCE}:530-548",
    },
    "warriors_guild_shot_put": {
        "display_name": "Shot put",
        "group": "warriors_guild",
        "requirements": {},
        "batch_size": 1,
        "warriors_guild_activity": True,
        "token_key": "strength",
        "summary": "Throw the 22 lb shot; distance and success scale with Strength.",
        "source": f"{WARRIORS_GUILD_SOURCE}; {DARKAN_WARRIORS_GUILD_SOURCE}:567-623",
    },
    "warriors_guild_keg_balance": {
        "display_name": "Keg balance",
        "group": "warriors_guild",
        "requirements": {},
        "batch_size": 1,
        "warriors_guild_activity": True,
        "token_key": "balance",
        "summary": "Balance five kegs for one scoring interval.",
        "source": f"{WARRIORS_GUILD_SOURCE}; {DARKAN_WARRIORS_GUILD_SOURCE}:429-466",
    },
}

# The dedicated period monster table is more specific than the rounded summary
# table on the Guild page (notably Adamant's 990 LP).
ANIMATED_ARMOUR_TIERS = (
    {
        "name": "Bronze",
        "items": ("Bronze full helm", "Bronze platebody", "Bronze platelegs"),
        "level": 11,
        "lifepoints": 100,
        "tokens": 5,
    },
    {
        "name": "Iron",
        "items": ("Iron full helm", "Iron platebody", "Iron platelegs"),
        "level": 23,
        "lifepoints": 200,
        "tokens": 10,
    },
    {
        "name": "Steel",
        "items": ("Steel full helm", "Steel platebody", "Steel platelegs"),
        "level": 46,
        "lifepoints": 400,
        "tokens": 15,
    },
    {
        "name": "Black",
        "items": ("Black full helm", "Black platebody", "Black platelegs"),
        "level": 69,
        "lifepoints": 600,
        "tokens": 40,
    },
    {
        "name": "Mithril",
        "items": ("Mithril full helm", "Mithril platebody", "Mithril platelegs"),
        "level": 92,
        "lifepoints": 800,
        "tokens": 50,
    },
    {
        "name": "Adamant",
        "items": ("Adamant full helm", "Adamant platebody", "Adamant platelegs"),
        "level": 113,
        "lifepoints": 990,
        "tokens": 60,
    },
    {
        "name": "Rune",
        "items": ("Rune full helm", "Rune platebody", "Rune platelegs"),
        "level": 138,
        "lifepoints": 1200,
        "tokens": 80,
    },
)

DEFENDER_TIERS = (
    {
        "name": "Bronze defender",
        "item_id": 8844,
        "level": 1,
        "attack": (3, 2, 1),
        "defense": (3, 2, 1),
        "strength": 0,
        "summoning": 1,
    },
    {
        "name": "Iron defender",
        "item_id": 8845,
        "level": 1,
        "attack": (5, 4, 3),
        "defense": (5, 4, 3),
        "strength": 0,
        "summoning": 2,
    },
    {
        "name": "Steel defender",
        "item_id": 8846,
        "level": 5,
        "attack": (7, 6, 5),
        "defense": (7, 6, 5),
        "strength": 1,
        "summoning": 3,
    },
    {
        "name": "Black defender",
        "item_id": 8847,
        "level": 10,
        "attack": (9, 8, 7),
        "defense": (9, 8, 7),
        "strength": 2,
        "summoning": 4,
    },
    {
        "name": "Mithril defender",
        "item_id": 8848,
        "level": 20,
        "attack": (10, 9, 8),
        "defense": (10, 9, 8),
        "strength": 3,
        "summoning": 5,
    },
    {
        "name": "Adamant defender",
        "item_id": 8849,
        "level": 30,
        "attack": (13, 12, 11),
        "defense": (13, 12, 11),
        "strength": 4,
        "summoning": 6,
    },
    {
        "name": "Rune defender",
        "item_id": 8850,
        "level": 40,
        "attack": (20, 19, 18),
        "defense": (20, 19, 18),
        "strength": 5,
        "summoning": 8,
    },
    {
        "name": "Dragon defender",
        "item_id": 20072,
        "level": 60,
        "attack": (25, 24, 23),
        "defense": (25, 24, 23),
        "strength": 6,
        "summoning": 10,
    },
)

SINGLE_TOKEN_ENTRY_COST = 200
SINGLE_TOKEN_DRAIN_PER_100_TICKS = 20
MULTI_TOKEN_ENTRY_COST = 30
MULTI_TOKEN_DRAIN_PER_100_TICKS = 3

# The period pages say multi-token payment improves both values but do not
# preserve magnitudes. These bounded, visible abstractions keep the distinction.
SINGLE_DEFENDER_CHANCE = 1.0 / 50.0
MULTI_DEFENDER_CHANCE = 1.0 / 25.0
MULTI_DAMAGE_MULTIPLIER = 1.05

# The period pages preserve only "a chance" and an increased multi-token
# chance. Reuse the visible defender odds as a bounded spawn abstraction.
SINGLE_CYCLOSSUS_CHANCE = 1.0 / 50.0
MULTI_CYCLOSSUS_CHANCE = 1.0 / 25.0
ANIMATED_ARMOUR_LOSS_CHANCE = 0.05
KEG_REVIEW_SUCCESS_CHANCE = 0.80
