# Summoning familiar teleport source audit (2026-07-16)

Scope: establish which pre-EOC familiars teleported the player and constrain their
review-native translation. Cutoff is 2012-11-20. This audit does not create a global
player-location or transport system.

## Pinned period sources

1. **Summoning familiars**, oldid
   [6579789](https://runescape.wiki/w/Summoning_familiars?oldid=6579789),
   2012-11-19 04:08:58 UTC.
2. **Spirit graahk**, oldid
   [5919222](https://runescape.wiki/w/Spirit_graahk?oldid=5919222),
   2012-07-11 05:49:00 UTC.
3. **Spirit kyatt**, oldid
   [6469653](https://runescape.wiki/w/Spirit_kyatt?oldid=6469653),
   2012-10-25 14:41:30 UTC.
4. **Spirit larupia**, oldid
   [5925061](https://runescape.wiki/w/Spirit_larupia?oldid=5925061),
   2012-07-12 21:31:27 UTC.
5. **Arctic bear**, oldid
   [6333537](https://runescape.wiki/w/Arctic_bear?oldid=6333537),
   2012-10-02 13:09:02 UTC.
6. **Void shifter**, oldid
   [5919199](https://runescape.wiki/w/Void_shifter?oldid=5919199),
   2012-07-11 05:39:06 UTC.
7. **Void scroll (Call to Arms)**, oldid
   [5177862](https://runescape.wiki/w/Void_scroll_%28Call_to_Arms%29?oldid=5177862),
   2012-01-23 07:06:34 UTC.

Revision IDs and timestamps came from the RuneScape Wiki MediaWiki revisions API.
Claims were checked against literal revision wikitext.

## Closed source facts

- Spirit graahk had an Interact -> Teleport ability to the Horned Graahk area near
  the Nature altar. Oldid 5919222 says the remaining run took about 30 seconds and
  a complete Nature-rune circuit could take 60 seconds. Its stated 2,000-3,000
  essence/hour is consistent with roughly 60 circuits using period Runecrafting
  pouches.
- Spirit kyatt teleported to the Piscatoris Hunter area. Oldid 6469653 explicitly
  says there was no limit to the number of teleports and describes its use for
  Hunter, iron mining, and access to the nearby Summoning obelisk.
- Spirit larupia teleported to the Feldip Hunter area. Oldid 5925061 also explicitly
  says there was no limit to the number of teleports.
- Arctic bear teleported to the Rellekka Hunter area (called Trollweiss in the
  familiar summary row) and also supplied a Hunter boost and camouflage effect.
- All four Void familiars' Call to Arms scroll teleported the player to the Void
  Knight Outpost/Pest Control landers.
- Void shifter additionally behaved like a Ring of life: when damage left the player
  below 10% of maximum LP, it automatically teleported the player to the Void Knight
  Outpost. The source describes the familiar as a reusable substitute for the ring;
  it does not state a one-use or one-encounter cooldown.
- The 6-point graahk/kyatt/larupia and 4-point Void-shifter values are initial
  Summoning costs. The pinned pages do not say that each ordinary familiar teleport
  consumes another pouch, scroll, or those points. Call to Arms is separately a
  scroll special and therefore uses its harvested scroll and special-move-point row.

## Review-native consequence

The project-wide expansion contract forbids a standalone transport network and persistent
player location. Familiar teleports therefore select **target-local alternate route
profiles**. They do not become decorative buttons or a universal percentage discount.

The route profile owns the whole source-shaped circuit: teleport activation, remaining
approach, action site, Bank/return leg, and any other route stages. Where a period source
states a full circuit or rate, derive the route's travel reviews from that evidence. The
Spirit graahk's 60-second Nature circuit yields 60 circuits/hour; at AnkiScape's
1,000-review/hour cadence that is `1000 / 60 - 1 = 15 2/3` travel reviews plus the
conversion review. This replaces the separately sourced two-minute fairy-ring/glory route
at `32 1/3` travel reviews; it never stacks as a second reduction on either rate.

Every rate row must declare an `assumed_route_id`. A familiar route can replace a walking
or other route profile but cannot modify a rate that already assumes that familiar. Where
only the teleport destination is proven and no complete target circuit survives, the
remaining magnitude is `source_blocked` until a target-specific rate is found or the owner
approves the smallest labeled route abstraction.

An already-live familiar can use its unlimited ordinary teleport whenever its target route
calls for it. Summoning and maintaining that familiar still consume the settled pouch,
duration, and Summoning-point resources, and it occupies the one global familiar slot; the
teleport itself does not consume a fresh pouch. Casual may choose the strictly faster
eligible route when its target familiar policy permits the required familiar. Advanced
chooses the exact route and familiar. Again does not progress a foreground travel phase.

Void shifter uses existing Combat retreat semantics. If an enemy hit leaves the player
alive but below 10% maximum LP, it automatically ends the encounter and retreats instead
of waiting for another hit; a lethal hit still kills the player. Enemy progress resets and
the ordinary return route remains due. The familiar stays subject to its normal lifetime
and can trigger again after the player heals and re-enters; no invented block cooldown or
one-proc limit is added.

Call to Arms remains a sourced scroll special parked behind the future Pest Control
activity. It can only select that activity's entry route if Pest Control actually models a
non-zero route; it must not consume a scroll merely to reproduce an already-instant UI
selection.

## Consultation note

Fable independently recommended the same target-local route-hook shape, route-assumption
metadata, Casual best-route selection, and eventual convergence with Magic/jewellery
teleports. Its proposed universal one-review route and one-proc Void-shifter limit were
rejected because the graahk source proves substantial post-teleport circuit time and the
Void-shifter source states no such cooldown. Consultation informed design review; it is not
historical evidence.

## Open cross-system fork

Summoning can use target-local alternate routes without reopening Magic. The remaining
owner decision is whether the shared route-profile substrate should also revise Magic
teleports and teleport jewellery so their source costs can affect compatible targets in
addition to Magic's existing pure-training casts.
