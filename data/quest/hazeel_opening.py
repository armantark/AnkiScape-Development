"""Source-bound Hazeel opening data; journal wording is authored paraphrase.

See hazeel_opening_sources.json for frozen passages, custody and consensus limits.
One eligible review groups one deed, not a historical duration.
"""

from dataclasses import dataclass
from types import MappingProxyType

from .choices import HAZEEL_CULT_ROUTE_CARNILLEAN, HAZEEL_CULT_ROUTE_HAZEEL

QUEST_ID = "hazeel_cult"
SOURCE = "https://runescape.wiki/w/Hazeel_Cult?oldid=6579784"
VALVE_KEY = "hazeel_cult_valve_states"
POISON = "Poison"
MARK = "Mark of Hazeel"
SHARED = ("ceril_commission", "clivet_briefing")
CARNILLEAN = "carnillean"
CULT = "hazeel"
BRANCH_ROUTES = MappingProxyType({CARNILLEAN: HAZEEL_CULT_ROUTE_CARNILLEAN, CULT: HAZEEL_CULT_ROUTE_HAZEEL})
BRANCH_DEEDS = MappingProxyType({
    CARNILLEAN: SHARED + ("carnillean_refusal",),
    CULT: SHARED + ("cult_acceptance", "poison_range", "family_confirmation", "clivet_mark"),
})
ENDPOINTS = MappingProxyType({CARNILLEAN: "carnillean_endpoint", CULT: "cult_endpoint"})
ENDPOINT_SENTENCES = MappingProxyType({
    CARNILLEAN: "Carnillean opening complete: all five valves are set correctly.",
    CULT: "Cult opening complete: all five valves are set correctly.",
})
POISON_RECEIPT = "Hazeel Cult: receive one Poison from Clivet"
POISON_OWNED = "Hazeel Cult: take Clivet's poison task with owned Poison"
MARK_RECEIPT = "Hazeel Cult: receive one Mark of Hazeel from Clivet"
MARK_OWNED = "Hazeel Cult: return to Clivet with an owned Mark"


@dataclass(frozen=True)
class Valve:
    number: int
    object_id: int
    varbit: int
    location: str
    correct: str
    opposite_option: str


VALVES = (
    Valve(1, 2844, 4846, "west of the Clock Tower", "right", "Turn-left"),
    Valve(2, 2845, 4847, "behind the Carnillean mansion", "right", "Turn-left"),
    Valve(3, 2846, 4848, "north of the cave", "left", "Turn-right"),
    Valve(4, 2847, 4849, "south of the zoo's penguin cage", "right", "Turn-left"),
    Valve(5, 2848, 4850, "southeast of valve 4 near Brother Cedric", "right", "Turn-left"),
)


@dataclass(frozen=True)
class OpeningAction:
    action_id: str
    proof: str
    pending: str
    completed: str
    target: int | None = None
    option: str | None = None
    direction: str | None = None


_DEEDS = (
    ("ceril_commission", "accept Ceril's armour commission", "Accept Ceril's commission to recover his family's stolen armour.", "Accepted Ceril's commission to recover his family's stolen armour."),
    ("clivet_briefing", "hear Clivet's revival offer", "Hear Clivet explain Hazeel's death and his plan to revive him.", "Heard Clivet explain Hazeel's death and ask for help reviving him."),
    ("carnillean_refusal", "refuse Clivet's revival offer", "Refuse Clivet's offer to revive Hazeel.", "Refused Clivet's offer to revive Hazeel."),
    ("cult_acceptance", "accept Clivet's poison task", "Accept Clivet's task and obtain Poison for the basement range.", "Accepted Clivet's task and received one Poison from him."),
    ("poison_range", "use Poison on the basement range", "Use one Poison on the Carnillean basement range.", "Used one Poison on the Carnillean basement range."),
    ("family_confirmation", "hear the Carnilleans confirm Scruffy's death", "Speak to the Carnilleans after using the Poison.", "Spoke to the Carnilleans and learned that Scruffy had died."),
    ("clivet_mark", "return to Clivet for the Mark", "Return to Clivet after speaking to the Carnilleans.", "Returned to Clivet after the family's report and received one Mark of Hazeel."),
)
_ACTIONS = {
    action_id: OpeningAction(action_id, f"Hazeel Cult: {proof}", pending, completed,
                             2859 if action_id == "poison_range" else None,
                             "use" if action_id == "poison_range" else None)
    for action_id, proof, pending, completed in _DEEDS
}
for _valve in VALVES:
    for _direction in ("left", "right"):
        _id = f"valve_{_valve.object_id}_{_direction}"
        _sentence = f"Set valve {_valve.number}, {_valve.location}, {_direction}."
        _ACTIONS[_id] = OpeningAction(_id, f"Hazeel Cult: set valve {_valve.number} {_direction}",
                                      _sentence, _sentence, _valve.object_id,
                                      f"Turn-{_direction}", _direction)
ACTIONS = MappingProxyType(_ACTIONS)
PROOFS = MappingProxyType({
    **{key: action.proof for key, action in ACTIONS.items()},
    "carnillean_endpoint": "Hazeel Cult: finish the Carnillean five-valve opening",
    "cult_endpoint": "Hazeel Cult: finish the cult five-valve opening",
})
CORRECT_VALVE_ACTIONS = tuple(f"valve_{valve.object_id}_{valve.correct}" for valve in VALVES)
REQUIRED_PROOFS = MappingProxyType({
    branch: tuple(PROOFS[key] for key in (*deeds, *CORRECT_VALVE_ACTIONS, ENDPOINTS[branch]))
    for branch, deeds in BRANCH_DEEDS.items()
})
OWNED_SENTENCES = MappingProxyType({
    "cult_acceptance": "Accepted Clivet's task; kept the Poison I already owned.",
    "clivet_mark": "Returned to Clivet after the family's report; kept the Mark of Hazeel I already owned.",
})
VALVE_CONTEXT = (
    "The valves redirect the currents.",
    "An opposite Turn option means the valve already faces the requested direction.",
)
NEUTRAL_JOURNAL = tuple(ACTIONS[key].pending for key in SHARED) + (
    "Carnillean route, if chosen", ACTIONS["carnillean_refusal"].pending,
    *tuple(ACTIONS[key].pending for key in CORRECT_VALVE_ACTIONS),
    "Hazeel's cult route, if chosen",
    *tuple(ACTIONS[key].pending for key in BRANCH_DEEDS[CULT][2:]),
    *tuple(ACTIONS[key].pending for key in CORRECT_VALVE_ACTIONS), *VALVE_CONTEXT,
)
HAZEEL_OPENING_ITEMS = {
    name: dict(category="material", item_id=item_id, model_id=model_id,
               stackable=False, tradeable=False,
               source=f"{SOURCE}; OpenRS2 cache 309 build 727 (2012-07-24), cache 544 build 742 (2012-11-07); {identity}")
    for name, item_id, model_id, identity in (
        (POISON, 273, 2714, "https://runescape.wiki/w/Poison_(item)?oldid=6150798"),
        (MARK, 2406, 40909, "https://runescape.wiki/w/Hazeel%27s_mark?oldid=5812161; https://runescape.wiki/w/Mark_of_Hazeel?oldid=526862"),
    )
}
