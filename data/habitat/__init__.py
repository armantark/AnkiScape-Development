"""Shadow's maintained Habitat requirements, with period facts and open holds."""

# Jadinko/Combinations oldid 6436146 (2012-10-18T02:07:07Z), L2,
# L25–33 and L132: Red + Abandoned house, no potion, immature attraction,
# interrupted by disease. Independent Tip.It actual capture 20120817112352
# (2012-08-17T11:23:52Z), L883 corroborates immature/diseased behavior;
# L933–934, L946 and L959 leave a Banana tree present for Shadow.
SHADOW_TARGET = "track_shadow_jadinko"
SHADOW_FLOWER_PATCH = "habitat_vine_flower"
SHADOW_REQUIRED_CROP = "red_blossom"
SHADOW_FEATURE = "abandoned_house"

# Herblore Habitat/Construction oldid 5994924 (2012-07-26T17:28:40Z),
# L1, L13–16; independently official Knowledge Base actual capture
# 20111030050144 (2011-10-30T05:01:44Z), L630, L633, L653–655.
ABANDONED_HOUSE_LEVEL = 57
ABANDONED_HOUSE_FEE = 57_000
ABANDONED_HOUSE_MATERIALS = {}
ABANDONED_HOUSE_TOOLS = ()
ABANDONED_HOUSE_XP = 0

# Dated wiki says no preference. Darkan JadinkoType.kt L35, supplying commit
# 6af9ef3dd50b7fbf24ccfdf0ee712d3a78d27249, instead requires empty bush/tree.
# Retain the bush conflict; do not import its contradicted empty-tree rule or
# seed-only health predicate. No independent period dead-specific closure.
# PLACEHOLDER(habitat.shadow_empty_bush_requirement): independently corroborated
# cutoff instructions/routines distinguishing no preference from emptiness
# would settle the wiki/restoration conflict.
SHADOW_REQUIRES_EMPTY_BUSH = False
# PLACEHOLDER(habitat.shadow_dead_flower_attraction): owner's provisional
# rejection; independent cutoff dead-specific attraction evidence would settle it.
SHADOW_REJECTS_DEAD_FLOWER = True

# Herblore Habitat/Farming oldid 4397753 (2011-06-12T16:01:02Z), L14
# includes vine flowers in watering. The magnitude is an existing Farming
# abstraction, provisionally extended to Red, not a period disease-rate claim.
# PLACEHOLDER(farming.red_blossom_watering_factor): qualified period vine-flower
# watering/disease magnitude evidence would replace this provisional extension.
RED_BLOSSOM_WATERING_FACTOR = 0.9

# Red blossom seed oldid 5054589 (2011-12-15T12:55:02Z), L23 supplies
# level, XP and nominal growth. Live Farming keeps one seed and four five-minute
# stages; quantity lacks independent closure and Tip.It says about 15 minutes
# versus the seed page's about 20. Neither timing adds an attraction delay.
# Feature persistence is the owner's product requirement. Independently
# corroborated period logout semantics remain unstated; 6045371 is unrecovered.

# Saved originals: /Users/armantarkhanian/.local/state/sol-loop/ankiscape/active/
# 1130-shadow-jadinko-persistent-habitat/sources/ (SHA-256 custody):
# jadinko-combinations-6436146.txt
# f63bb17a0d853d04cc3b2207d617be8d0c6e1375cd1fca9c7d708eaa75a6669a
# herblore-habitat-construction-5994924.txt
# 60db056c78315b885d1cba295ce6469ce091b610442ff0be23bec7e2aa786de3
# official-kb-20111030050144.html
# 2859280ba69a99cc4c6d8d80232f036028e87197a30ac3c6ed9d07cadc7e93c0
# tipit-forum-main-20120817112352.html
# f88d971634557201fc4b55ca61e70ed109df90abe0b9bd04cf7a8bb8f3b27635
