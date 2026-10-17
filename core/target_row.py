"""Shared target row contract and its player-facing details projection."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TargetRowMetadata:
    """Shared contract for one selectable flat target-list row."""

    target_id: str
    label: str
    tooltip: str
    enabled: bool = True
    navigation_enabled: bool = False
    current: bool = False
    icon_path: Optional[str] = None
    group: str = ""
    locked_reasons: tuple[str, ...] = ()
    sort_key: tuple[object, ...] = ()
    requires_confirmation: bool = False
    confirmation_title: str = ""
    confirmation_message: str = ""


@dataclass(frozen=True)
class TargetDetails:
    """Player-facing mechanics copied from one live target row."""

    target_id: str
    title: str
    lines: tuple[str, ...]
    enabled: bool


def target_details_from_row_pure(row: TargetRowMetadata) -> TargetDetails:
    """Build optional details without exposing provenance or inventing values."""

    lines = tuple(
        line.rstrip()
        for line in row.tooltip.splitlines()
        if line.strip() and not line.strip().startswith("Source:")
    )
    if not lines:
        lines = ("No extra mechanics to show for this target.",)
    return TargetDetails(
        target_id=row.target_id,
        title=row.label,
        lines=lines,
        enabled=row.enabled,
    )
