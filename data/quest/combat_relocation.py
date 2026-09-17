"""Apply the source-backed stage and drop corrections for quest encounters."""

from dataclasses import replace

from .. import rum_deal_data, zogre_flesh_eaters_data


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


def relocate_combat_encounters(quest_id, requirements):
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
