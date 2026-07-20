---
{
  "help_id": "carried-inventory",
  "title": "Carried inventory and Bank runs",
  "surface": "concept",
  "aliases": ["pack", "backpack", "carried quantities", "bank run", "loadout"],
  "tags": ["inventory", "bank", "automation"],
  "related": ["bank", "automation", "combat", "equipment"]
}
---
Your Bank is persistent storage. A target's carried inventory is the active pack used by that target's review loop.

## Target-local packs

Casual mode builds a practical pack from owned resources. Advanced mode lets you set quantities and preserves the order in which entries were added. Stackable items consume one carried slot for the stack; non-stackable items consume one slot each.

## Bank boundaries

When a loop needs supplies or must deposit outputs, its Bank run follows that activity's review cost. Compatible restore or refill work can coalesce at the same boundary instead of charging duplicate reviews.

Changing pages does not silently rewrite a saved pack. See [Bank](help:bank) for direct inventory actions.
