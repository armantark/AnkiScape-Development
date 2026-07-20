---
{
  "help_id": "bank",
  "title": "Bank and inventory actions",
  "surface": "bank",
  "aliases": ["inventory", "claims", "discard", "consume", "bank run"],
  "tags": ["bank", "items", "claims"],
  "related": ["carried-inventory", "equipment", "shop", "quests"]
}
---
The Bank is persistent item storage and the home for direct item actions, equipment access, recovery, and reward claims.

## Finding and using items

Search matches item names and categories without changing quantities or carried-pack order. Context actions expose only operations the selected item supports, such as consume, open, equip, teleport, or discard.

**Discard X** removes the confirmed quantity instantly. Its bounded command undo is separate from review undo.

## Claims and recovery

Bank Claims collect rewards that need an explicit choice. Grave and Death's Office panels expose recoverable Combat items and costs. Target-local carried packs remain separate from Bank ownership; see [Carried inventory](help:carried-inventory).
