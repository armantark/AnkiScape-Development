# Slayer Kuradal family-boundary supplement — 2026-07-19

Status: **period family membership closed; runtime unchanged**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

The two Kuradal-only ordinary-family boundaries that were not enumerated in
the original pool table are source-closed:

- **TzHaar** comprises the ordinary TzHaar-Ket, TzHaar-Xil, TzHaar-Mej, and
  TzHaar-Hur castes. Fight Cave `Tok-` creatures belong only to Kuradal's
  separate 280-kill challenge and are not ordinary-family variants.
- **Living rock creatures** comprise the Living rock patriarch, Living rock
  protector, and Living rock striker.

This supplement closes stable membership only. It does not certify missing
Combat targets or authorize the hidden Kuradal master while the registry schema
conflict in `audits/slayer-kuradal-registry-schema-conflict-2026-07-19.md`
remains unresolved.

## Period evidence

`Slayer assignment` oldid `6303852`, timestamp
`2012-09-27T13:49:08Z`, explicitly lists:

- `TzHaar-Ket`, `TzHaar-Xil`, `TzHaar-Mej`, and `TzHaar-Hur` as the TzHaar
  alternatives; and
- Living rock patriarch, protector, and striker as the Living rock creature
  alternatives.

Source:
<https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.

Kuradal oldid `6588106`, timestamp `2012-11-19T16:58:14Z`, independently
separates the ordinary TzHaar assignment from the optional 280-creature Fight
Cave challenge:
<https://runescape.wiki/w/Kuradal?oldid=6588106>.

## Emulator convergence and rejection

Darkan `TaskMonster.java` at pinned commit
`c343a917712649675989315009ce250639e0850f` defines:

- `LIVING_ROCK_CREATURES` through the `living rock` name prefix; and
- `VOLCANIC_CREATURES` through broad `tz` and `tok-` prefixes.

The Living-rock prefix converges with the period membership. The `tok-` prefix
does not preserve the period boundary because it can admit Fight Cave
creatures to the ordinary family. It remains emulator evidence for the
70–110 generator row only and is not adopted as stable membership.

## Implementation consequence

The stable registry must eventually use:

- `tzhaar_ket`, `tzhaar_xil`, `tzhaar_mej`, and `tzhaar_hur`; and
- `living_rock_patriarch`, `living_rock_protector`, and
  `living_rock_striker`.

The existing `tzhaar_ket` or `tzhaar_hur` Combat row may satisfy the ordinary
variant floor only after all four identities are present in the family ledger.
Neither row may redefine the family as a one-target category.
