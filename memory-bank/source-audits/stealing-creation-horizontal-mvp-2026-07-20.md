# Stealing Creation horizontal-MVP harvest

Date: `2026-07-20`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **source-ready breadth slice implemented; exhaustive catalog deferred.**

## Authority and pinned revisions

- RuneScape Wiki `Stealing Creation`, oldid `6518618`,
  `2012-11-02T07:46:11Z`.
- RuneScape Wiki `Sacred clay`, oldid `5902636`,
  `2012-07-07T18:19:28Z`.
- RuneScape Wiki `Creation kiln`, oldid `5905778`,
  `2012-07-08T10:38:28Z`.
- RuneScape Wiki `Proto-tool`, oldid `6514505`,
  `2012-11-01T01:41:02Z`.
- RuneScape Wiki `Volatile clay tool`, oldid `6314239`,
  `2012-09-28T17:14:58Z`.
- RuneScape Wiki `Stealing Creation points`, oldid `5562700`,
  `2012-05-03T20:04:23Z`.
- RuneScape cache revision 742 item identities and options. The cache proves
  identity and interaction labels, not server mechanics.

## Period facts enabled in breadth one

- Stealing Creation is safe. Death removes accumulated temporary items; Protect
  Item keeps the highest-valued temporary item. No gravestone is created.
- Sacred clay has five classes with level gates `1/20/40/60/80`.
- Period gathering routes are ground fragments, Mining rocks, Fishing pools,
  Hunter swarms, and Woodcutting trees.
- Gathering, processing, and depositing each score `15 × clay class` per clay.
- One clay creates one same-class item at a creation kiln. Four barrier pieces
  complete a wall.
- The period combat game lasts 20 minutes. AnkiScape maps one source minute to
  one meaningful duty review, so the session lasts 20 review beats and never
  reads the wall clock.
- The winning team receives a 10% score bonus before reward conversion.
- Exact reward-point conversion:

| score | points |
|---:|---:|
| `0–19,999` | `floor(score / 1,000)` |
| `20,000–21,999` | `20` |
| `22,000–25,999` | `21` |
| `26,000–33,999` | `22` |
| `34,000–49,999` | `23` |
| `50,000–81,999` | `24` |
| `82,000–145,999` | `25` |
| `146,000+` | `26` |

- Combat XP had been removed by the cutoff. Session fights therefore use a
  closed temporary actor in the shared live six-tick combat reducer and merge
  back only session lifepoints and encounter state; ordinary XP and outside
  supplies never enter the session result.
- The proto-tool costs 20 points, lets the player choose among seven forms,
  gives 200% total XP, and consumes charge according to bonus XP rather than
  action count.
- The volatile tool costs 20 points, requires the matching skill at level 40 in
  the source game, gives 220% total XP, and randomly changes form after each
  10% charge segment.

## Reward-tool charge ledger

Charge is stored as a normalized fraction and consumed by `bonus XP / form
capacity`. Ranged or approximate source lifetimes use their conservative lower
endpoint.

| form | matching AnkiScape XP | bonus-XP capacity | status |
|---|---|---:|---|
| Hammer | Smithing | `32,062` | period explicit bonus XP |
| Hammer | Construction | `25,375` | period explicit bonus XP |
| Needle | Crafting | `21,948` | lower period total `43,896`, divided by two |
| Hatchet | Woodcutting | `15,000` | lower period total `30,000`, divided by two |
| Pickaxe | Mining | `7,000` | approximate period total `14,000`, divided by two |
| Harpoon | Fishing | `11,750` | period page explicitly states bonus XP |
| Fletching knife | Fletching | `38,500` | lower period total `77,000`, divided by two |
| Butterfly net | Hunter | `15,000` | `source_blocked` lifetime; labeled bounded fallback |

The morphic tool may change form without losing charge. The volatile tool rolls
among all seven period forms at each crossed 10% boundary. A depleted tool is
removed atomically from both the instance state and flat inventory.

## Cache identities enabled

- Sacred clay classes 1–5: item pairs `14182–14191`.
- Barriers classes 1–5: item pairs `14172–14181`.
- Class-1 hatchet: `14132/14133`.
- Class-1 scimitar: `14287/14288`.
- Class-1 platebody: `14347/14348`.
- Proto-tool: `14106`; its seven transformed identities are `14107–14113`.
- Volatile clay tool: `14098`; transformed identities are `14099–14105`.

Temporary clay and equipment remain session state and never enter the global
Bank, inventory, or equipment substrate. Only the two persistent reward-tool
base identities are registered as ordinary items.

## Explicit bounded abstractions

- The source 20-minute game becomes 20 duty reviews. Reviews are the only
  progression clock.
- A gathering duty summarizes ten clay harvests; a crafted session hatchet
  doubles that batch to twenty. The opposing team summarizes five clay per
  duty. These event-scaled batches keep the source `15 × class × clay` score
  intact while making the period reward-point table reachable on review scale.
- Opposing production draws one class 1–5 duty per review and applies the exact
  source `15 × class` score. This exposes the approximation instead of hiding a
  continuous invented rate.
- Raiders reuse the Fist of Guthix bounded opponent population. A raid arrives
  after a jittered 4–6 duty reviews and resolves through the shared six-tick
  combat reducer. Raider lifepoints use three times the sampled Constitution
  stat (minimum 75) so a raid is a bounded interruption rather than consuming
  the whole 20-review economy.
- Cache-backed temporary scimitar and platebody identities use monotonic
  class-scaled combat bonuses because an exact cutoff stat table was not
  recovered. The values are session-only and cannot contaminate ordinary gear.
- Protect Item ranks temporary possessions by clay class, with a stable slot
  tie-break, because the complete period withdrawal-value table is not yet
  pinned. All unprotected clay and crafted gear are still removed atomically.
- A completed barrier has `class × 2` raid exchanges of durability and reduces
  incoming pressure by 10% per class, reaching 50% of baseline at class 5.
- The butterfly-net lifetime remains `source_blocked`; `15,000` bonus XP is the
  explicit horizontal fallback until stronger period evidence is found.
- Reward tools apply only while the matching skill family is the selected
  review action. This prevents unrelated lamps, quests, or minigame side XP
  from consuming tool charge; within that family, exact per-recipe tool-use
  distinctions remain depth work.

## Deferred depth, not missing mechanics

- The exhaustive kiln catalog, rune/scroll output quantities, every equipment
  stat row, clay familiar creation, pickpocketing, and the complete reward shop
  remain depth work.
- Exact raid arrival distribution, opposing population mix, and every tool
  lifetime are still precision harvest work.
- The five-player-per-team real entry gate is retired by the owner-settled solo
  opponent simulation. It is not an unimplemented lock.

## Asset provenance

`tools/fetch_stealing_creation_assets.py` pins period revisions before the
cutoff and records immutable metadata in `assets_provenance.json` for:

- `activityicons/stealing_creation.png` from `Sacred clay (class 5).png`;
- `activityitems/proto_tool.png` from `Proto-tool.png`;
- `activityitems/volatile_clay_tool.png` from `Volatile clay tool.png`.

All three PNGs are alpha-cropped by the shared normalizer. UI code scales them
into the shared 28-pixel activity or item surface without stretching.

## Verification and review closure

- `2,057` non-Qt tests pass with `268` expected environment skips.
- `2,057` real offscreen-Qt tests pass with one intentional skip.
- The hard test-quality audit reports zero issues. Documentation, Python
  compilation, JSON, diff, normalized assets and worktree safety pass.
- Reachability reports `1,436` actions, `2,102` reachable items, `168` orphan
  inputs and `189` blocked actions. The nonzero exit is the repository's known
  unresolved acquisition debt, not a Stealing Creation regression.
- A fully restarted native Anki process shows one launcher, one menu, the
  Minigames row and the unclipped dark-mode READY card. The native pass found
  and fixed Casual mode displaying stale disabled Advanced choices.
- Opus independently reviewed the implementation and UI. Every reproduced
  actor-isolation, encounter-terminal, Casual-planning, XP-charge, sanitation
  and hierarchy finding is regression-covered. Fable was deliberately reserved
  at the owner's request. A single Kimi K3 taste request returned no response
  headers for roughly 25 minutes and was stopped without retry; no Kimi approval
  is claimed.

The attempted three-leaf Codex Workflows review, run
`bc4c6eee-c56a-4143-b066-b600f9d0f799`, produced no task session or review
output. One worker eventually reported `failed to refresh available models:
timeout waiting for child process to exit`; the run was canceled and no claim
depends on it. Root verification reproduced every accepted finding directly.
