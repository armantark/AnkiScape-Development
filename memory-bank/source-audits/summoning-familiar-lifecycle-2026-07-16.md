# Summoning familiar lifecycle source audit (2026-07-16)

Scope: evidence needed to frame the first Summoning owner-grill decision. Cutoff is
2012-11-20. This is not yet the exhaustive familiar/pouch/scroll table harvest.

## Pinned period sources

1. **Summoning**, oldid
   [6582606](https://runescape.wiki/w/Summoning?oldid=6582606),
   2012-11-19 08:49:35 UTC.
2. **Summoning familiars**, oldid
   [6579789](https://runescape.wiki/w/Summoning_familiars?oldid=6579789),
   2012-11-19 04:08:58 UTC.
3. **Summoning points**, oldid
   [6542597](https://runescape.wiki/w/Summoning_points?oldid=6542597),
   2012-11-08 06:20:13 UTC.
4. **Summoning pouches**, oldid
   [6438719](https://runescape.wiki/w/Summoning_pouches?oldid=6438719),
   2012-10-18 21:44:17 UTC.
5. **Follower details**, oldid
   [6093772](https://runescape.wiki/w/Follower_details?oldid=6093772),
   2012-08-15 03:51:25 UTC.
6. **Beasts of Burden**, oldid
   [6288415](https://runescape.wiki/w/Beasts_of_Burden?oldid=6288415),
   2012-09-24 05:14:06 UTC.

The revision IDs and timestamps were retrieved directly through the RuneScape Wiki
MediaWiki revisions API with `rvstart=2012-11-20T23:59:59Z` and `rvdir=older`; claims
below were checked against the literal revision wikitext rather than the modern page.

## Findings

| Claim | Period evidence | Confidence |
|---|---|---|
| Familiar lifetime was per-familiar, not a universal duration. | The oldid 6579789 table has a `Time (minutes)` column on every familiar row; early rows already differ (Spirit wolf 6, Dreadfowl 4, Meerkats 40, Spirit spider 15). | High |
| A pouch summons one familiar and is consumed. | Oldid 6582606, `Pouches`, says the pouch is used up on summon and is not restored on dismissal. | High |
| Only one familiar may be active. | Oldid 6582606, `Familiars`, requires dismissal before summoning another. | High |
| Summoning points and familiar duration were distinct state. | Oldid 6542597 explains an initial summon cost plus continuing drain over the familiar's life; reaching zero does not dismiss the familiar. | High |
| Zero points disabled right-click abilities but not the familiar's other ordinary behavior. | Oldids 6542597 and 6582606 agree on the zero-point behavior. | High |
| Scroll specials did not spend ordinary Summoning points. | Oldid 6542597 explicitly distinguishes scrolls from point-draining right-click abilities. | High |
| Points restored at obelisks/small obelisks or with Summoning/super-restore potions. | Oldids 6542597 and 6582606 agree. | High |
| Familiar roles were heterogeneous. | Oldid 6582606 classifies fighters, skill boosters, beasts of burden, healers, foragers, teleporters, and other abilities; oldid 6579789 provides per-row specifics. | High |
| Renewal deliberately consumed another pouch of the same familiar near expiry. | Oldid 6093772 says Renew required an unnoted matching pouch and was available only at 2:30 or less; renewal also healed the familiar. | High |
| A BoB had a separate inventory with direct whole-inventory bank deposit. | Oldid 6288415 describes its inventory UI and the familiar icon in the bank interface. | High |
| BoB items fell to the ground when the familiar expired or died. | Oldid 6288415 describes expiry/death drops and a five-minute owner retrieval window after expiry. | High |
| BoB inventory could not be accessed during combat. | Oldid 6288415 says players needed to find safety before withdrawing carried items. | High |

## Design boundary

The source proves real-time duration and relative per-familiar lifetimes. It cannot tell
AnkiScape which discrete study event should replace elapsed minutes. Any conversion from
minutes to answered cards/actions is therefore a **labeled AnkiScape abstraction**.
Preserving duration ratios is source-respecting; the global conversion magnitude is a
product decision.

Do not collapse duration and Summoning points into one charge pool. The period game let
a familiar remain active at zero points, so those states supported different decisions.

## Remaining harvest

- Extract every familiar row and reconcile its duration, summon cost, role, combat
  statistics, capacity, passive, active ability, and scroll special.
- Extract every pouch and scroll recipe, output quantity, XP award, shard count, charm,
  tertiary, and quest/activity gate.
- Pin special-move-point recovery and scroll costs separately from Summoning points.
- Source logout/context, forbidden-area, and familiar-combat behavior from period
  revisions and reconciled server code. Renewal and the basic BoB expiry/storage surface
  are pinned above; exact implementation still needs the owner automation and no-ground
  inventory decisions.
