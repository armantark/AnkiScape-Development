"""Apply the source-backed stage and drop corrections for quest encounters."""

from dataclasses import replace

from .. import rum_deal_data, zogre_flesh_eaters_data
from .stage_overrides.free.the_blood_pact import THE_BLOOD_PACT_COMBAT_PREREQUISITES


_RELOCATIONS_BY_QUEST_ID = {
    rum_deal_data.QUEST_ID: (
        rum_deal_data.RUM_DEAL_COMBAT_ENCOUNTER_STAGES,
        rum_deal_data.RUM_DEAL_COMBAT_GUARANTEED_DROPS,
        "Rum Deal combat encounter catalog changed",
    ),
    zogre_flesh_eaters_data.QUEST_ID: (
        zogre_flesh_eaters_data.ZOGRE_FLESH_EATERS_COMBAT_ENCOUNTER_STAGES,
        zogre_flesh_eaters_data.ZOGRE_FLESH_EATERS_COMBAT_GUARANTEED_DROPS,
        "Zogre Flesh Eaters combat encounter catalog changed",
    ),
}


def _bind_combat_prerequisites(requirements, prerequisites, catalog_error):
    encounter_ids = {
        encounter.encounter_id
        for requirement in requirements
        for encounter in requirement.combat_encounters
    }
    required_ids = set(prerequisites) | {
        encounter_id for ids in prerequisites.values() for encounter_id in ids
    }
    if not required_ids <= encounter_ids:
        raise ValueError(catalog_error)
    return tuple(
        replace(requirement, combat_encounters=tuple(
            replace(encounter, required_encounters=prerequisites[encounter.encounter_id])
            if encounter.encounter_id in prerequisites else encounter
            for encounter in requirement.combat_encounters
        ))
        for requirement in requirements
    )


def relocate_combat_encounters(quest_id, requirements):
    if quest_id == "the_blood_pact":
        return _bind_combat_prerequisites(
            requirements, THE_BLOOD_PACT_COMBAT_PREREQUISITES,
            "The Blood Pact combat encounter catalog changed",
        )
    relocation = _RELOCATIONS_BY_QUEST_ID.get(quest_id)
    if relocation is None:
        return requirements
    encounter_stages, guaranteed_drops, catalog_error = relocation
    moved_ids = frozenset(encounter_stages)
    encounters = {
        encounter.encounter_id: encounter
        for requirement in requirements
        for encounter in requirement.combat_encounters
        if encounter.encounter_id in moved_ids
    }
    if encounters.keys() != moved_ids:
        raise ValueError(catalog_error)
    encounters = {
        encounter_id: replace(
            encounter,
            guaranteed_drops=guaranteed_drops[encounter_id],
        )
        for encounter_id, encounter in encounters.items()
    }
    return tuple(
        replace(
            requirement,
            combat_encounters=tuple(
                encounter
                for encounter in requirement.combat_encounters
                if encounter.encounter_id not in moved_ids
            )
            + tuple(
                encounters[encounter_id]
                for encounter_id, stage in encounter_stages.items()
                if stage == requirement.stage
            ),
        )
        for requirement in requirements
    )
