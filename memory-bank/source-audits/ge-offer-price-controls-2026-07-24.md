# Grand Exchange offer-screen controls — SOURCED from cache client scripts

Date: `2026-07-24`, corrected `2026-07-25` twice

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **sourced from primary Jagex data.** The arithmetic was recovered by
disassembling the period client script out of the game cache. This supersedes
both earlier versions of this record: the first wrongly called Darkan's
reconstruction sourced, and the second wrongly concluded the behaviour was
unknowable and fell back to owner preference. Neither is true — the answer was
in the cache the whole time, in a client script, which is why no server source
and no wiki revision documents it.

## The recovered behaviour

Interface `105` components `179` (+5%) and `181` (−5%) both invoke **client
script 4112**, passing the percentage as an argument (`105` and `95`). The script
computes the new price and writes it to a **client** variable. It sends nothing
to the server.

The editable price is **varc 85**, not varp 1111. Varp 1111 is the server-owned
committed price; varc 85 is the scratch value the buttons edit, seeded from varp
1114 (the guide price) by script 607 on the guide-price button.

```
percent = arg0                        # 105 from component 179, 95 from component 181
price   = varc 85                     # the price currently displayed

if varp 1109 (selected item) == -1:            return          # nothing selected
if percent > 100 and price > 2045222520:       new = 2147483647 # +5% overflow clamp
elif percent < 100 and price <= 1:             new = 1          # -5% floor
else:
    new = (int)((long) price * percent / 100)                   # truncates toward zero
    if new == price:                                            # truncation stalled
        new += (percent >= 100) ? +1 : -1                       # forced 1-coin step
varc 85 = new
```

Three properties matter and none were guessable:

1. **It compounds off the displayed price** (`LOAD_VARC 85`), not off the guide
   price. Repeated clicks multiply.
2. **Rounding is truncation toward zero**, through the `SCALE` opcode, whose
   deobfuscated implementation is `(int)((long) c * a / b)`
   (`darkan-client/src/main/java/com/rs/jagex/CS2Interpreter.java:10789-10795`) —
   a 64-bit intermediate and a truncating integer divide.
3. **There is a forced one-coin minimum step.** When truncation would leave the
   price unchanged, the client nudges it by ±1 anyway, so the button is never a
   no-op on cheap items.

Each button also ends with `CALL_CS2 609`, the hold-to-repeat timer built on varc
83 (starts at 100, then +10 per tick) — press-and-hold acceleration, available if
we ever want it.

## Provenance

- **Index 12** holds client scripts (archive = script id, file 0); **index 3**
  holds interfaces (archive = interface id, file = component id). Established two
  independent ways: the deobfuscated client's loader table
  (`darkan-client/.../IndexLoaders.java:169`,
  `CS2_SCRIPTS_INDEX = loadIndex(IndexReference.INDEX_12)`) and Darkan core's
  `IndexType.CS2_SCRIPTS`.
- Component hook bytes, interface archive 105:
  `comp_179` → `[script 4112, arg 105]`; `comp_181` → `[script 4112, arg 95]`.
- Disassembly is from the **727 (2012-07-24)** build, 62 ops.
- **Stable across the whole pre-EOC window.** In 652 (2011-06-08), 727, 728, 736,
  741 (2012-11-04) and 742 (2012-11-07), components 179/181 carry the identical
  hook and script 4112 is **371 bytes in every build with every constant at the
  identical offset** (`2045222520` @72, `2147483647` @90, `6881433` @336, `100`
  @48/114/180/231). The finding is not a 727 artifact.
- **Why the cross-check is structural rather than six disassemblies:** Jagex
  renumbered the CS2 opcode table in every build after 727 (script 100's first
  three opcodes are 500/902/184 in 727, 394/318/626 in 728, 644/773/2 in 741).
  Both Darkan core and the deobfuscated client carry only the 727 table, so 727
  is the only build on disk that decodes symbolically. Worth remembering before
  anyone tries to disassemble 741 directly.

Tooling: `tools/OpenRs2Cs2Disassembler.java`, written for this question and
reusable. Modes `count`, `dump <ids>`, `scan <opNameSubstr|*> [operand|lo-hi]`,
`grepstr <needle>`. Run it with the classpath idiom from
`tools/query_openrs2_cache.sh`. `scan PUSH_INT 6881280-6881900` enumerates every
script touching interface 105; `scan VARC 85` finds every writer of the price
field. That range-scan is what located everything here.

## Verdict on the two competing accounts

**Darkan** (`GE.java:170,174`, `(int)(price * 1.05)` server-side) is *mostly*
right and wrong in three specific ways:

- correct that it compounds off the displayed price, and correct that it
  truncates;
- **missing the forced one-coin step.** For +5% this diverges at every price from
  0 to 19: the real client takes 19 → 20, Darkan leaves 19 → 19, stuck forever.
  An exhaustive check of prices 0–200,000 found those twenty low prices to be the
  *only* +5% divergences;
- **missing the −5% floor of 1** (Darkan returns 0 at price 1), and missing the
  explicit `> 2045222520 → MAX_INT` clamp, which is not observably different in
  Java but is worth copying because the constant is exactly the +5% overflow
  boundary — it hard-proves 105 is the only percentage that button ever passes.

**The owner's remembered "additive, 5% of base on all clicks" is contradicted.**
The real game compounds. This matters because the owner's instruction was
explicitly "whatever it is in the real game", and that condition is now satisfied
by primary data rather than a fan reconstruction.

## Implementation consequence

Ship the recovered behaviour: compounding off the displayed price, a 64-bit
intermediate with truncation toward zero, the forced ±1 step, the −5% floor of 1,
and the overflow clamp. The pass-2 agent's one-coin minimum step turns out to be
**authentic** and must stay; only its round-to-nearest is wrong and becomes
truncation. Note plainly for the owner that up-then-down does not return to the
starting price and that the guide-price button is the exact reset — that is
period behaviour, and script 607 exists precisely to provide it.

## Corrections to neighbouring claims

- **Darkan's "component 166 = quantity all/+1000" is not supported.** No
  component in interface archive 105 hooks such a script. Do not cite it, and do
  not cite the earlier claim in this record that the period "all" button reads the
  carried inventory — that came from Darkan and is now unsupported.
- **There is therefore no period basis for a sell-all button.** The owner asked
  for one as a quality-of-life feature; ship it as an acknowledged addition, not
  as parity.
- **Quantity buttons are asymmetric by offer side** (scripts 598/599/600 read
  varp 1113): on a buy offer the 1/10/100 buttons *add* to the running quantity;
  on a sell offer they *set* it outright. Components are quantity −1 = 155,
  +1 = 157, then 160/162/164.
- **Price ±1 coin buttons carry their own clamps**: script 604 does
  `max(price - 1, 1)`, script 605 refuses to increment at `Integer.MAX_VALUE`.
- **Guide-price reset** (script 607, component 175) sets varc 85 to varp 1114, or
  to 1 when the guide price is negative or no item is selected.
- **Buy limits are not client-side in this era.** Nothing in these scripts
  mentions a per-item limit, so they were enforced server-side and remain
  unrecoverable from the cache. Any buy-limit value stays sourced elsewhere.
- **Total-cost display** (script 621, ops 157-185) prints `"Too high!"` when
  `quantity > Integer.MAX_VALUE / price`, otherwise `price * quantity` with a
  `" gp"` suffix; script 397 recolours it red when the player's coins fall below
  the total.

One thing left unverified: how varc 85 reaches the server on confirm. No script
reads it at confirm time, which points at the automatic transmitted-varc sync
rather than an explicit packet, but that was not chased down.
