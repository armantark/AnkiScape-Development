"""Add only missing period Elite lamps after retiring legacy original payments."""

from ...data.achievement_diary_data import DIARY_ALL_LAMP_CLAIM_IDS_BY_TIER


def migrate_missing_diary_lamps_pure(data: dict, loaded_config_version: int) -> None:
    """Update sanitized load data once, keeping spent and forfeited claims intact."""
    if loaded_config_version >= 125:
        return
    claimed_tiers = data.get("achievement_diaries", {}).get("claimed_tiers", ())
    claims = dict(data.get("claims", {}))
    for tier_id in claimed_tiers:
        for claim_id in DIARY_ALL_LAMP_CLAIM_IDS_BY_TIER.get(tier_id, ())[1:]:
            claims.setdefault(claim_id, {"claimed": False})
    data["claims"] = claims
