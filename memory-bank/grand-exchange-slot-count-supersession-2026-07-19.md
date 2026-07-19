# Grand Exchange slot-count supersession

Date: 2026-07-19

Status: **owner-settled; period parity wins.**

This record supersedes every earlier AnkiScape Grand Exchange clause that
specified eight player offer slots or ±20% quick-price controls, including:

- `fake-grand-exchange-design.md:25,258,278`;
- `ge-relitigation-2026-07-19.md:16-19`;
- the eight-slot implementation descriptions in the dated Grand Exchange
  source audits, `activeContext.md`, `progress.md`, and
  `future-work-kanban.md`.

The live Grand Exchange has **six** player offer slots and the period interface
controls: Guide, -5%, +5%, and custom price. The owner explicitly resolved the
conflict in favor of period accuracy after the interface harvest found the
cutoff-era values.

## Period evidence

RuneScape Wiki `Grand Exchange`, oldid `6367453`, timestamp
`2012-10-08T01:30:21Z`, states that members had six trading spaces and
free-to-play players had two. The same revision states that the post-2011
interface had guide prices, ±5% buttons, and custom offers; it does not attest
±20% controls:

<https://runescape.wiki/w/Grand_Exchange?oldid=6367453>

AnkiScape does not model membership tiers, so the normal player surface uses
the period member count of six. No eight-slot compatibility mode remains.
