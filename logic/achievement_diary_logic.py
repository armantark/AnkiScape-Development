"""Pure achievement-diary progress, claiming, Taskmaster and cabinet view.

The rules live here. ``achievement_cabinet_view_pure`` is the single place that
decides what the Cabinet shows and what it lets the player press, so the panel
renders a view and never re-derives a gate.

Two contracts govern this module:

- ``memory-bank/achievement-diary-item-grants-design.md`` (the diary design).
- ``memory-bank/achievement-semantics-contract-2026-07-16.md``, whose Foundation
  section forbids diary gear from consuming a moving-denominator completion
  percentage. Nothing here reads one: every gate is a task predicate over
  durable state, and the only ratios computed are per-tier ``done/total`` counts
  whose denominator is the tier's own fixed task list.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG,
    BASE_CONDITION_KINDS,
    DiaryCondition,
    DiaryFamily,
    DiaryTask,
    DiaryTier,
    diary_lamp_claim_id,
)
from ..data.summoning_data import SUMMONING_ACTION_IDS_BY_FAMILY
from ..logic_pure.achievement_diary_events import sanitize_diary_event_maps_pure
from .achievement_diary_derived import (  # noqa: F401  (re-export)
    DIARY_DERIVED_VALUE_CEILINGS,
    DIARY_DERIVED_VALUES,
)
from .shop_logic import shop_diary_transaction_counter_key_pure


ACHIEVEMENT_DIARY_STATE_VERSION = 1

# The period achievement system unlocked "The Task at Hand" at 350 completed
# tasks; the design contract carries that figure into the Music Log.
MUSIC_UNLOCK_TASK_COUNT = 350


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _str_list(value: Any, *, limit: int = 4000) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    seen: dict[str, None] = {}
    for entry in value:
        if isinstance(entry, str) and entry:
            seen.setdefault(entry[:120], None)
        if len(seen) >= limit:
            break
    return list(seen)


# ---------------------------------------------------------------------------
# Persistent state
# ---------------------------------------------------------------------------


def default_achievement_diary_state_pure() -> dict[str, Any]:
    return {
        "achievement_diaries": {
            "version": ACHIEVEMENT_DIARY_STATE_VERSION,
            "completed_tasks": [],
            "claimed_tiers": [],
            "pinned_task": "",
            "event_counts": {},
            "event_stages": {},
            "taskmaster": False,
            # The period reward for all 534 tasks was an emote, which AnkiScape
            # has no system for. The design contract translates it into a
            # one-time presentation; this flag is what makes it one-time.
            "taskmaster_presented": False,
        }
    }


def sanitize_achievement_diary_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = _mapping(_mapping(player_data).get("achievement_diaries"))
    pinned_task = str(source.get("pinned_task", "") or "")[:120]
    if pinned_task and diary_task_by_id_pure(pinned_task) is None:
        pinned_task = ""
    event_counts, event_stages = sanitize_diary_event_maps_pure(source)
    return {
        "achievement_diaries": {
            "version": ACHIEVEMENT_DIARY_STATE_VERSION,
            "completed_tasks": _str_list(source.get("completed_tasks")),
            "claimed_tiers": _str_list(source.get("claimed_tiers")),
            "pinned_task": pinned_task,
            "event_counts": event_counts,
            "event_stages": event_stages,
            "taskmaster": bool(source.get("taskmaster", False)),
            "taskmaster_presented": bool(source.get("taskmaster_presented", False)),
        }
    }


def _state(player_data: Mapping[str, Any]) -> dict[str, Any]:
    return sanitize_achievement_diary_state_pure(player_data)["achievement_diaries"]


# ---------------------------------------------------------------------------
# Condition evaluation
# ---------------------------------------------------------------------------


def _ledger_bucket(
    player_data: Mapping[str, Any], skill_id: str, bucket: str
) -> Mapping[str, Any]:
    progress = _mapping(player_data.get("achievement_progress"))
    skills = _mapping(progress.get("skills"))
    return _mapping(_mapping(skills.get(skill_id)).get(bucket))


_MISSING = object()


def _value_at(player_data: Mapping[str, Any], path: str) -> Any:
    node: Any = player_data
    for part in path.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return _MISSING
        node = node[part]
    return node


def _counter_at(player_data: Mapping[str, Any], path: str) -> int:
    value = _value_at(player_data, path)
    return 0 if value is _MISSING else _int(value)


def _shop_transaction_count(player_data: Mapping[str, Any], key: str) -> int:
    transaction_type, separator, remainder = key.partition("|")
    shop_id, row_separator, row_id = remainder.partition("|")
    counter_key = (
        shop_diary_transaction_counter_key_pure(transaction_type, shop_id, row_id)
        if separator and row_separator
        else ""
    )
    return _int(_mapping(player_data.get("shop_transaction_counts")).get(counter_key))


def _ledger_action_family_count(
    player_data: Mapping[str, Any], skill_id: str, family_id: str
) -> int:
    if skill_id != "summoning":
        return 0
    action_ids = SUMMONING_ACTION_IDS_BY_FAMILY.get(family_id, ())
    actions = _ledger_bucket(player_data, skill_id, "actions")
    return sum(_int(actions.get(action_id)) for action_id in action_ids)


def _held_quantity(player_data: Mapping[str, Any], item_name: str) -> int:
    """Live Bank quantity plus anything of that name currently worn.

    Semantics contract: Hold/Own wording reads live state. Worn counts because
    equipping does not stop the player from owning the item.
    """

    held = _int(_mapping(player_data.get("inventory")).get(item_name))
    equipment = _mapping(player_data.get("equipment"))
    held += sum(1 for worn in equipment.values() if worn == item_name)
    return held


def condition_progress_pure(
    player_data: Mapping[str, Any], condition: DiaryCondition
) -> tuple[int, int]:
    """Return ``(have, need)`` for one condition."""

    need = max(1, _int(condition.amount, 1))
    kind = condition.kind
    if kind == "skill_level":
        return _int(player_data.get(f"{condition.key}_level", 1), 1), need
    if kind == "quest":
        state = _mapping(_mapping(player_data.get("quests")).get(condition.key))
        return (1 if state.get("completed") else 0), 1
    if kind in {"ledger_output", "ledger_action"}:
        skill_id, _, key = condition.key.partition(":")
        bucket = "outputs" if kind == "ledger_output" else "actions"
        return _int(_ledger_bucket(player_data, skill_id, bucket).get(key)), need
    if kind == "ledger_action_family":
        skill_id, _, family_id = condition.key.partition(":")
        return _ledger_action_family_count(player_data, skill_id, family_id), need
    if kind == "counter":
        return _counter_at(player_data, condition.key), need
    if kind == "combat_kill":
        return _counter_at(player_data, f"combat_kill_counts.{condition.key}"), need
    if kind == "shop_transaction":
        return _shop_transaction_count(player_data, condition.key), need
    if kind == "state_equals":
        actual = _value_at(player_data, condition.key)
        matches = (
            condition.expected is not None
            and actual is not _MISSING
            and type(actual) is type(condition.expected)
            and actual == condition.expected
        )
        return (1 if matches else 0), 1
    if kind == "hold_item":
        return _held_quantity(player_data, condition.key), need
    if kind == "equipped_item":
        slot, separator, item_name = condition.key.partition("|")
        worn = _mapping(player_data.get("equipment")).get(slot)
        return (1 if separator and worn == item_name else 0), 1
    if kind == "derived_value":
        # An unregistered name reads zero, never `need`: the import-time
        # assertion in the data module is what stands between a typo and an
        # impossible row, and this fallback must not hand out a free completion
        # if that assertion is ever removed.
        derivation = DIARY_DERIVED_VALUES.get(condition.key)
        return (0, need) if derivation is None else (_int(derivation(player_data)), need)
    if kind == "any_of":
        # The period wrote several tasks as "kill a giant rat" where AnkiScape
        # stores one counter per level variant. The task is done when any single
        # alternative is done, and the panel shows the closest alternative
        # rather than a sum of unlike units. An empty or unrecognised set of
        # alternatives is unsatisfiable, never satisfied by a vacuous any().
        pairs = [
            condition_progress_pure(player_data, alternative)
            for alternative in condition.alternatives
            if alternative.kind in BASE_CONDITION_KINDS
        ]
        if not pairs:
            return 0, 1
        best = max(pairs, key=lambda pair: (min(pair[0], pair[1]) / pair[1], pair[0]))
        return min(best[0], best[1]), best[1]
    return 0, need


def task_progress_pure(
    player_data: Mapping[str, Any], task: DiaryTask
) -> tuple[bool, int, int]:
    """Return ``(satisfied_now, have, need)`` for a whole task.

    Dormant rows intentionally have no predicate. They reserve an authentic cutoff
    task's place and can never complete until the generator emits a real condition.
    A multi-condition task reports its progress as the number of conditions met,
    because summing unrelated units would be meaningless. A single-condition
    task reports that condition's real figures, which is where staged progress
    is worth showing. Binary feats stay binary.
    """

    if task.dormant:
        return False, 0, 0
    if len(task.conditions) == 1:
        have, need = condition_progress_pure(player_data, task.conditions[0])
        return have >= need, min(have, need), need
    met = sum(
        1
        for condition in task.conditions
        if (lambda pair: pair[0] >= pair[1])(
            condition_progress_pure(player_data, condition)
        )
    )
    total = len(task.conditions)
    return met >= total, met, total


# ---------------------------------------------------------------------------
# Catalog helpers
# ---------------------------------------------------------------------------


_CATALOG_TIERS = tuple(
    (family, tier)
    for family in ACHIEVEMENT_DIARY_CATALOG
    for tier in family.tiers
)
_CATALOG_TASKS = tuple(
    (family, tier, task)
    for family, tier in _CATALOG_TIERS
    for task in tier.tasks
)
_TASKS_BY_ID = {task.id: (family, tier, task) for family, tier, task in _CATALOG_TASKS}
_TIERS_BY_ID = {tier.id: (family, tier) for family, tier in _CATALOG_TIERS}
_TASK_IDS = frozenset(_TASKS_BY_ID)
_ACTIVE_TASK_IDS = frozenset(
    task.id for _, _, task in _CATALOG_TASKS if not task.dormant
)
_DESIGNED_TASK_TOTAL = sum(tier.total_tasks for _, tier in _CATALOG_TIERS)


def _tiers():
    yield from _CATALOG_TIERS


def _tasks():
    yield from _CATALOG_TASKS


def diary_task_by_id_pure(task_id: str) -> "tuple[DiaryFamily, DiaryTier, DiaryTask] | None":
    return _TASKS_BY_ID.get(task_id)


def diary_tier_by_id_pure(tier_id: str) -> "tuple[DiaryFamily, DiaryTier] | None":
    return _TIERS_BY_ID.get(tier_id)


# ---------------------------------------------------------------------------
# Progress refresh
# ---------------------------------------------------------------------------


def refresh_achievement_diaries_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Credit every newly satisfied task and return the names that just landed.

    Completion is sticky, exactly as the semantics contract requires of
    completed achievement names: a task that was satisfied once stays satisfied
    after the proving item is spent.
    """

    data = dict(player_data)
    state = _state(data)
    completed = list(state["completed_tasks"])
    known = set(completed)
    newly: list[str] = []
    for _family, _tier, task in _tasks():
        if task.id in known:
            continue
        satisfied, _have, _need = task_progress_pure(data, task)
        if satisfied:
            completed.append(task.id)
            known.add(task.id)
            newly.append(task.id)
    state["completed_tasks"] = completed
    state["taskmaster"] = (
        len(_ACTIVE_TASK_IDS) == _DESIGNED_TASK_TOTAL
        and _ACTIVE_TASK_IDS.issubset(known)
    )
    data["achievement_diaries"] = state
    if newly:
        data = _award_task_coins(data, newly)
    return data, tuple(newly)


def _award_task_coins(data: dict[str, Any], task_ids: Sequence[str]) -> dict[str, Any]:
    """Pay Miscellaneous rewards on the cache-proven completion-count curve."""

    payout = 0
    completed_total = len(_ACTIVE_TASK_IDS & set(_state(data)["completed_tasks"]))
    starting_ordinal = max(0, completed_total - len(task_ids))
    for offset, task_id in enumerate(task_ids, start=1):
        found = diary_task_by_id_pure(task_id)
        if found is not None and found[2].coin_reward:
            payout += int(found[2].coin_reward) * (starting_ordinal + offset)
    if not payout:
        return data
    inventory = dict(_mapping(data.get("inventory")))
    inventory["Coins"] = _int(inventory.get("Coins")) + payout
    data["inventory"] = inventory
    return data


# ---------------------------------------------------------------------------
# Claiming
# ---------------------------------------------------------------------------


def tier_claim_state_pure(
    player_data: Mapping[str, Any],
    family: DiaryFamily,
    tier: DiaryTier,
) -> dict[str, Any]:
    state = _state(player_data)
    completed = set(state["completed_tasks"])
    claimed = set(state["claimed_tiers"])
    done = sum(1 for task in tier.tasks if not task.dormant and task.id in completed)
    total = tier.total_tasks
    predecessor = None
    for index, candidate in enumerate(family.tiers):
        if candidate.id == tier.id and index:
            predecessor = family.tiers[index - 1]
            break
    blocked_by = (
        predecessor.name
        if predecessor is not None and predecessor.id not in claimed
        else ""
    )
    if not total:
        # Defensive migration guard: an empty tier is never a finished one and
        # must not fall through to "Ready to Claim".
        status = "Roster pending harvest"
    elif tier.id in claimed:
        status = "Claimed"
    elif done < total:
        status = "In progress"
    elif blocked_by:
        status = f"Claim {blocked_by} first"
    else:
        status = "Ready to Claim"
    return {
        "tier_id": tier.id,
        "done": done,
        "total": total,
        "latent": sum(1 for task in tier.tasks if task.dormant),
        "source_gap": total - len(tier.tasks),
        "claimed": tier.id in claimed,
        "ready": bool(total) and done >= total and not blocked_by and tier.id not in claimed,
        "blocked_by": blocked_by,
        "status": status,
    }


def _create_tier_lamp_claim(data: dict[str, Any], tier: DiaryTier) -> str:
    if tier.lamp is None:
        return ""
    claim_id = diary_lamp_claim_id(tier.id)
    claims = dict(_mapping(data.get("claims")))
    claims.setdefault(claim_id, {"claimed": False})
    data["claims"] = claims
    return claim_id


def claim_diary_tier_pure(
    player_data: Mapping[str, Any],
    tier_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Grant or upgrade equipment and place the sourced lamp in Bank Claims."""

    found = diary_tier_by_id_pure(tier_id)
    if found is None:
        return dict(player_data), False, {"reason": "Unknown diary tier."}
    family, tier = found
    data = dict(player_data)
    claim_state = tier_claim_state_pure(data, family, tier)
    if claim_state["claimed"]:
        return data, False, {"reason": f"{tier.name} is already claimed."}
    if not claim_state["ready"] and not claim_state["blocked_by"]:
        return data, False, {"reason": f"{tier.name} still has tasks outstanding."}
    if claim_state["blocked_by"]:
        return (
            data,
            False,
            {"reason": f"Claim {claim_state['blocked_by']} before {tier.name}."},
        )

    data = _grant_tier_item(data, family, tier)
    lamp_claim_id = _create_tier_lamp_claim(data, tier)

    state = _state(data)
    state["claimed_tiers"] = list(state["claimed_tiers"]) + [tier.id]
    data["achievement_diaries"] = state
    granted = tier_reward_names_pure(tier)
    message = (
        f"{family.name}: {tier.name} claimed. {_join(granted)} is yours."
        if granted
        else f"{family.name}: {tier.name} claimed."
    )
    if tier.lamp is not None:
        message += f" A {tier.lamp.experience:,} XP reward lamp is waiting in Bank Claims."
    return (
        data,
        True,
        {
            "message": message,
            "item": tier.reward_item,
            "items": granted,
            "lamp_claim_id": lamp_claim_id,
            "lamp_experience": tier.lamp.experience if tier.lamp else 0,
        },
    )


def tier_reward_names_pure(tier: DiaryTier) -> tuple[str, ...]:
    """Every item this tier's claim hands over, in the order it is presented."""

    if tier.reward_item:
        return (tier.reward_item,)
    return tuple(f"{count}x {name}" if count > 1 else name for name, count in tier.reward_bundle)


def _join(names: Sequence[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" and {names[-1]}"


def _grant_tier_item(
    data: dict[str, Any], family: DiaryFamily, tier: DiaryTier
) -> dict[str, Any]:
    """Grant the tier item, replacing its predecessor wherever that one sits."""

    if not tier.reward_item:
        # A tier with no upgradeable worn item pays its set bundle whole. The
        # bundle never replaces anything, so it skips the upgrade sweep below.
        if tier.reward_bundle:
            inventory = dict(_mapping(data.get("inventory")))
            for name, count in tier.reward_bundle:
                inventory[name] = _int(inventory.get(name)) + count
            data["inventory"] = inventory
        return data
    inventory = dict(_mapping(data.get("inventory")))
    equipment = dict(_mapping(data.get("equipment")))
    predecessor = ""
    for index, candidate in enumerate(family.tiers):
        if candidate.id == tier.id and index:
            predecessor = family.tiers[index - 1].reward_item
            break

    worn_slot = ""
    if predecessor:
        for slot, worn in list(equipment.items()):
            if worn == predecessor:
                worn_slot = str(slot)
                del equipment[slot]
                break
        if not worn_slot and _int(inventory.get(predecessor)):
            remaining = _int(inventory.get(predecessor)) - 1
            if remaining > 0:
                inventory[predecessor] = remaining
            else:
                inventory.pop(predecessor, None)

    if worn_slot:
        equipment[worn_slot] = tier.reward_item
    else:
        inventory[tier.reward_item] = _int(inventory.get(tier.reward_item)) + 1
    data["inventory"] = inventory
    data["equipment"] = equipment
    return data


# ---------------------------------------------------------------------------
# Taskmaster
# ---------------------------------------------------------------------------


TASKMASTER_TITLE = "Taskmaster"
TASKMASTER_BODY = (
    "Every regional, Burthorpe/Taverley and Miscellaneous task is complete."
    " The gold Taskmaster seal is yours, and the Completionist cape's"
    " Taskmaster requirement is satisfied."
)


def taskmaster_presentation_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The one-time completion presentation, and whether it is still owed.

    It grants nothing: the design contract is explicit that Taskmaster adds no
    cape, no stat and no mechanical perk. The seal and the Completionist
    requirement are already carried by the durable ``taskmaster`` flag; this is
    the moment the player is told.
    """

    state = _state(player_data)
    return {
        "earned": bool(state["taskmaster"]),
        "show": bool(state["taskmaster"]) and not state["taskmaster_presented"],
        "title": TASKMASTER_TITLE,
        "body": TASKMASTER_BODY,
    }


def acknowledge_taskmaster_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = _state(data)
    if not state["taskmaster"]:
        return data, False, {"reason": "Taskmaster is not complete."}
    if state["taskmaster_presented"]:
        return data, False, {"reason": "Taskmaster has already been presented."}
    state["taskmaster_presented"] = True
    data["achievement_diaries"] = state
    return data, True, {"message": f"{TASKMASTER_TITLE}. {TASKMASTER_BODY}"}


# ---------------------------------------------------------------------------
# Pinning
# ---------------------------------------------------------------------------


def pin_diary_task_pure(
    player_data: Mapping[str, Any], task_id: str
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """The 2012 interface's one-task pin, surviving only inside the Cabinet."""

    data = dict(player_data)
    state = _state(data)
    if not task_id:
        state["pinned_task"] = ""
        data["achievement_diaries"] = state
        return data, True, {"message": "Pin cleared."}
    if diary_task_by_id_pure(task_id) is None:
        return data, False, {"reason": "Unknown task."}
    state["pinned_task"] = "" if state["pinned_task"] == task_id else task_id
    data["achievement_diaries"] = state
    return (
        data,
        True,
        {"message": "Task pinned." if state["pinned_task"] else "Pin cleared."},
    )


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------


def diary_totals_pure(
    player_data: Mapping[str, Any]
) -> dict[str, int]:
    state = _state(player_data)
    completed = set(state["completed_tasks"])
    return {
        "completed": len(_ACTIVE_TASK_IDS.intersection(completed)),
        "total": _DESIGNED_TASK_TOTAL,
    }


def achievement_cabinet_view_pure(
    player_data: Mapping[str, Any],
    *,
    family_filter: str = "",
    tier_filter: str = "",
    completion_filter: str = "",
    search: str = "",
) -> dict[str, Any]:
    """Everything the Cabinet renders, including every enable decision."""

    # Late imports: both modules read the diary ledger, so binding them at
    # module scope would close a cycle.
    from .cape_logic import cape_view_pure
    from .music_log_logic import music_log_totals_pure

    state = _state(player_data)
    completed = set(state["completed_tasks"]) & _ACTIVE_TASK_IDS
    pinned = state["pinned_task"]
    needle = search.strip().lower()
    families: list[dict[str, Any]] = []
    for family in ACHIEVEMENT_DIARY_CATALOG:
        if family_filter and family.id != family_filter:
            continue
        tiers: list[dict[str, Any]] = []
        for tier in family.tiers:
            if tier_filter and tier.name != tier_filter:
                continue
            rows: list[dict[str, Any]] = []
            for task in tier.tasks:
                done = task.id in completed
                if completion_filter == "complete" and not done:
                    continue
                if completion_filter == "incomplete" and done:
                    continue
                _satisfied, have, need = task_progress_pure(player_data, task)
                if needle and needle not in f"{task.name} {task.description}".lower():
                    continue
                rows.append(
                    {
                        "task_id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "requirements": tuple(
                            condition.label or condition.key
                            for condition in task.conditions
                        )
                        + tuple(
                            f"Access gate — {condition.label or condition.key}"
                            for condition in task.access_gates
                        ),
                        "completed": done,
                        "latent": task.dormant,
                        "curation_anchor": task.curation_anchor,
                        "have": need if done else have,
                        "need": need,
                        "staged": need > 1,
                        "pinned": task.id == pinned,
                        "coin_reward": task.coin_reward,
                        "source": task.source,
                    }
                )
            rows.sort(key=lambda row: (not row["pinned"],))
            claim = tier_claim_state_pure(player_data, family, tier)
            tiers.append(
                {
                    **claim,
                    "name": tier.name,
                    "index": tier.index,
                    "effort_multiplier": tier.effort_multiplier,
                    "reward_item": tier.reward_item,
                    "reward_items": tier_reward_names_pure(tier),
                    "reward_summary": tier.reward_summary,
                    "lamp": (
                        {
                            "claim_id": diary_lamp_claim_id(tier.id),
                            "experience": tier.lamp.experience,
                            "minimum_level": tier.lamp.minimum_level,
                            "description": (
                                f"A {tier.lamp.experience:,} XP reward lamp for an"
                                f" eligible level {tier.lamp.minimum_level}+ skill will"
                                " be placed in Bank Claims."
                            ),
                        }
                        if tier.lamp is not None
                        else None
                    ),
                    "tasks": tuple(rows),
                    "source": tier.source,
                }
            )
        families.append(
            {
                "family_id": family.id,
                "name": family.name,
                "kind": family.kind,
                "taskmaster": {
                    "show": bool(family.taskmaster),
                    "name": family.taskmaster,
                    "chathead_asset_path": family.taskmaster_chathead_asset_path,
                },
                "tiers": tuple(tiers),
            }
        )

    totals = diary_totals_pure(player_data)
    return {
        "families": tuple(families),
        "completed": totals["completed"],
        "total": totals["total"],
        "taskmaster": bool(state["taskmaster"]),
        "taskmaster_presentation": taskmaster_presentation_pure(player_data),
        "capes": cape_view_pure(player_data),
        "music": music_log_totals_pure(player_data),
        "pinned_task": pinned,
        "filters": {
            "families": tuple((family.id, family.name) for family in ACHIEVEMENT_DIARY_CATALOG),
            "tiers": tuple(
                dict.fromkeys(tier.name for _family, tier in _tiers())
            ),
        },
    }


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------


def apply_achievement_diary_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Every Cabinet mutation, routed through one undoable seam in __init__."""

    body = _mapping(payload)
    if action_id == "claim_tier":
        return claim_diary_tier_pure(player_data, str(body.get("tier_id", "")))
    if action_id == "pin_task":
        return pin_diary_task_pure(player_data, str(body.get("task_id", "")))
    if action_id == "purchase_cape":
        from .cape_logic import purchase_cape_pure

        return purchase_cape_pure(player_data, str(body.get("cape_id", "")))
    if action_id == "acknowledge_taskmaster":
        return acknowledge_taskmaster_pure(player_data)
    return dict(player_data), False, {"reason": "Unknown Cabinet command."}
