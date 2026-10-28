"""Witch's House identities and qualified route sources (facts versus adaptations)."""

QUEST_ID = "witchs_house"
DIARY = "Diary (Witch's House)"
DOOR_KEY = "Door key"
MAGNET = "Magnet"
BACKROOM_KEY = "Backroom key"
BALL = "Ball"
LEATHER_GLOVES = "Leather gloves"
CHEESE = "Cheese"
ITEM_IDS = {DOOR_KEY: 2409, MAGNET: 2410, BACKROOM_KEY: 2411,
            BALL: 2407, DIARY: 2408, LEATHER_GLOVES: 1059, CHEESE: 1985}

TAKE_DIARY = "Take the Witch's diary from the table"
READ_DIARY = "Read the Witch's diary"
ENTER_BASEMENT = "Enter the Witch's basement"
TAKE_GLOVES = "Find leather gloves in the Witch's basement boxes"
PASS_GATE = "Pass the Witch's electric gate wearing insulating gloves"
TAKE_MAGNET = "Take the magnet from the Witch's cupboard"
TAKE_KEY = "Search the Witch's fountain for the backroom key"
TAKE_BALL = "Pick up Harvey's ball from the shed"

INSULATING_GLOVES = {
    LEATHER_GLOVES: 1059, "Safety gloves": 12629, "Void knight gloves": 8842,
    "Ghostly gloves": 6110, "Penance gloves": 10553, "Flame gloves": 13660,
}
EXPERIMENTS = (
    ("witchs_house_witchs_experiment_first_form", "Witch's experiment (Skavid form)"),
    ("witchs_house_witchs_experiment_second_form", "Witch's experiment (Spider form)"),
    ("witchs_house_witchs_experiment_third_form", "Witch's experiment (Bear form)"),
    ("witchs_house_witchs_experiment_fourth_form", "Witch's experiment (Wolf form)"),
)
RESUME_KEY = "witchs_house_resume_stage"
LEGACY_COMPLETED_KEY = "witchs_house_legacy_completed"
RESUME_STAGES = {4: 8, 5: 9, 6: 10, 7: 10, 8: 11, 9: 12, 10: 13, 11: 14}

EVIDENCE = "data/quest/evidence/witchs_house"
ROUTE_SOURCE = (
    "https://runescape.wiki/w/Witch's_House?oldid=6474931 "
    "(2012-10-26T12:16:36Z), retained sources/witchs-house-6474931.txt:34-83; "
    f"{EVIDENCE}/source-index.json and sources/exact-source-lines.json; "
    "Tip.It 20120825005349:75,77,80; Sal's 20121018060604:49-56; "
    "RuneHQ 20121103135007:79-87 (continued custody conflicts; prior Read selected)"
)
DIARY_SOURCE = (
    "https://runescape.wiki/w/Diary_(Witch's_House)?oldid=5849371 "
    "(2012-06-27T19:24:38Z); retained sources/period-diary.txt; "
    "sources/cache-727-items.txt and sources/cache-742-items.txt "
    "(OpenRS2 caches 309/544, client identity/properties only); "
    f"{EVIDENCE}/source-index.json; upstairs wording conflicts, no floor gate"
)
HANDLER_SOURCE = (
    "Darkan WitchsHouse.java c73c79aae7d5fb45e7677376f70fb108447c8dd2; "
    f"{EVIDENCE}/sources/supplying-handler.txt:65,95-98,121-139,292-345 "
    "(reconstruction evidence, not independent period corroboration); "
    "retained-cache-identity.json:18-22 (alternate glove identities); "
    "Magnet retained per handler/product; period prose does not settle debit"
)
