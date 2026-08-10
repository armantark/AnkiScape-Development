# Razor-backed kebbit tracking acquisition audit — 2026-08-09

Status: **implemented with one registered hidden-rate placeholder**.
Cutoff: `2012-11-20T00:00:00Z`.

This record supersedes only the Razor-backed-kebbit activation conclusion in
`hunter-tracking-pitfall-rabbit-restoration-2026-07-19.md`. The remaining
tracking, Penguin, pitfall, rabbit, and rabbit-foot source blockers in that
audit are unchanged.

## Period route

RuneScape Wiki `Hunter`, oldid `6484443`, timestamp
`2012-10-27T06:44:39Z`, pins the complete visible row:

- tracking requires a Noose wand;
- Razor-backed kebbit requires Hunter level 49;
- one successful catch awards 348 Hunter XP;
- a trail contains four or five successful searches before the final attack;
- successful kebbit catches produce Bones and Raw beast meat; and
- Razor-backed kebbit produces one Long kebbit spike.

Source: <https://runescape.wiki/w/Hunter?oldid=6484443>.

One answered review represents the complete trail and final attack. This is the
already-settled Hunter action model, not a claim that the period game resolved
tracking in one click.

## Executable corroboration and honest hidden value

Darkan commit `37957d17d62d6b14d326cd719a0ae0c239c76cf9` reconstructs
Razor-backed tracking with a reusable Noose wand and the same three outputs.
It is deterministic and records `348.5` XP, so it does not settle the hidden
catch curve and does not override the direct cutoff article's 348 XP.

The live row therefore registers
`hunter.razor_backed_kebbit_success_curve`: the shared Hunter fallback
`rate1=128`, `rate99=256`. At level 49, the authentic shared source-roll
adapter computes integer chance 191 and probability `192/255` before the
established review normalization. A period tracking routine or qualified
measured table would retire this value.

## Item identity and art

OpenRS2 rev-742 pins:

- item `10107`, Long kebbit spike: model `19401`, non-stackable,
  exchangeable, and `Craft` action; and
- item `9986`, Raw beast meat: model `11296`, non-stackable and exchangeable.

The live route reuses normalized pre-cutoff sprites already recorded in
`assets_provenance.json`:

- `fletcheditems/long_kebbit_spike.png`, 31×25, timestamp
  `2008-04-12T19:12:23Z`, SHA-1
  `3890fed08adae1c35e243285e4acf339c2809894`; and
- `shopitems/raw_beast_meat.png`, 29×18, timestamp
  `2011-11-27T14:04:36Z`, SHA-1
  `b0a4f2c59ca8c97edb6ebfa798510b4dda82d911`.

## Runtime boundary

The new target reuses Hunter's existing target lock, success/failure,
carried-pack Keep/Drop, cadence, telemetry, Shattered Heart, persistence, and
review-undo paths. Shattered Heart can replace up to two ordinary outputs with
Hunter strange rocks; because Long kebbit spike is the third sourced output,
the downstream Fletching and Leon service input remains retained.

No new UI pattern was added. The established grouped Hunter selector adds one
`Tracking` group and renders the target's existing item icon and actionable
Noose-wand lock.

## Verification boundary

Focused pure, runtime, registry, reachability, loaded-add-on review/undo, and
real offscreen Qt selector checks exercise the live row. The reachability graph
now routes Long kebbit spike through
`Hunter:track_razor_backed_kebbit`, which activates the existing six-bolt
Fletching target and Leon service without claiming the rest of the Hunter
tracking catalog.
