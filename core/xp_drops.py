"""Whole-number XP changes for review feedback; awards keep their precision."""

from math import floor

from .action_products import product_gains_pure
from .activity_feedback import item_changes_text
from .last_action import last_action_record_pure
from .skill_registry import trainable_skill_definitions
from ..logic.inventory_pure import review_item_changes_pure


def whole_number_xp_breakdown(before, after):
    breakdown = []
    for skill in trainable_skill_definitions():
        gained = floor(float(after.get(skill.exp_key, 0) or 0)) - floor(
            float(before.get(skill.exp_key, 0) or 0)
        )
        if gained > 0:
            breakdown.append((skill.display_name, gained))
    return breakdown


def review_product_text(before, after, current_skill) -> str:
    """The popup's item text: the review's gain of its action's product, never loot or what it used."""
    action = last_action_record_pure(before, current_skill)
    return item_changes_text(product_gains_pure(action, review_item_changes_pure(before, after)))


class NamedExperience(float):
    """A numeric XP result that carries the skills which earned it.

    A finished review also carries its item changes, which its drop names after
    the XP.
    """

    def __new__(cls, amount, skill_names=(), breakdown=(), item_text=""):
        value = super().__new__(cls, float(amount))
        value.skill_names = tuple(
            dict.fromkeys(str(name) for name in skill_names if name)
        )
        totals = {}
        for name, skill_amount in breakdown:
            amount_value = float(skill_amount)
            if name and amount_value > 0:
                key = str(name)
                totals[key] = totals.get(key, 0.0) + amount_value
        if not totals and len(value.skill_names) == 1:
            totals[value.skill_names[0]] = float(value)
        value.breakdown = tuple(totals.items())
        value.item_text = str(item_text)
        return value

    @property
    def display_text(self) -> str:
        def amount_text(amount) -> str:
            value = float(amount)
            return f"{value:.1f}" if 0 < value < 1 else str(int(value))

        if len(self.breakdown) > 1:
            message = " · ".join(
                f"{name} +{amount_text(amount)} XP"
                for name, amount in self.breakdown
            )
        else:
            amount = self.breakdown[0][1] if self.breakdown else self
            message = f"+{amount_text(amount)} XP"
            if self.skill_names:
                message += f" · {', '.join(self.skill_names)}"
        return f"{message} · {self.item_text}" if self.item_text else message

    def __add__(self, other):
        return NamedExperience(
            float(self) + float(other),
            (*self.skill_names, *getattr(other, "skill_names", ())),
            (*self.breakdown, *getattr(other, "breakdown", ())),
        )

    def __radd__(self, other):
        return NamedExperience(
            float(other) + float(self),
            (*getattr(other, "skill_names", ()), *self.skill_names),
            (*getattr(other, "breakdown", ()), *self.breakdown),
        )
