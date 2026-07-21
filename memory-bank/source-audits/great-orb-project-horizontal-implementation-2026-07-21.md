# Great Orb Project horizontal implementation

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

The implementation is anchored to the literal wikitext from RuneScape Wiki
`The Great Orb Project` oldid `6564759`, timestamp
`2012-11-17T03:12:07Z`:

<https://runescape.wiki/w/The_Great_Orb_Project?oldid=6564759>

That revision establishes:

- level 50 Runecrafting entry and team-versus-team altar rounds;
- the members' altar order Air, Mind, Water, Earth, Fire, Body, Chaos, Nature;
- attractor, repeller, and barrier equipment, plus an activity bar sustained by
  orb manipulation or barrier work;
- essence after each round based on both teams' scores, with overflow left on
  the ground and a player choice to craft now or carry it to a later altar;
- twice the ordinary Runecrafting XP for every essence crafted in the activity;
- member token payouts of 100 for an altar win, 10 for a loss, and 25 for a
  tie, plus a 200-token majority bonus or 100 each when the majority is tied;
- token participation requires attracting or repelling at least one orb;
  barrier work fills the activity bar but does not qualify that altar for
  tokens; and
- a manual Wizard Elriss reward shop. Free-to-play talismans cost 50 tokens,
  while essence supports an explicit Buy X action and members receive Pure
  essence.

The ordinary rune XP rows and deterministic multiple-rune thresholds reuse the
already-pinned Runecrafting table in `runecrafting_data.py`. Existing canonical
item definitions supply Pure essence item `7936` and Air talisman item `1438`.
OpenRS2 revision-742 config inspection independently identifies Runecrafting
guild tokens as `13650`-`13654`; the token remains an activity currency rather
than a carried inventory item.

## Disclosed AnkiScape translation

The settled competitive-activity contract in
`memory-bank/source-audits/competitive-tier-adaptations-2026-07-18.md` maps
each altar to one duty beat against a bounded, jittered opposing score. One
successful review therefore resolves one complete altar round. Eight reviews
complete one members' match; a review multiplier cannot begin a second match.

Casual uses a balanced orb doctrine and crafts after every round. Advanced may
save one of four doctrines and choose either round-by-round crafting or saving
essence for the Nature altar. Attract and repel are token-qualifying orb work.
Barrier control improves the team score but intentionally receives no
per-altar tokens, preserving the source's participation distinction.

The source does not expose exact per-player score rolls, opposing-team rolls,
or the score-to-essence formula. The shipped 7-13 score bands, doctrine offsets,
and `min(14, 4 + combined_score // 4)` essence award are disclosed bounded
abstractions under oldid `6564759`, not historical claims. The activity-local
essence capacity is 28; overflow is left behind. Saving carries only this
temporary essence between rounds and automatically crafts it at Nature.

Tokens stay pending until the eighth round. Leaving early forfeits pending
tokens and saved essence while preserving already-crafted runes and XP. The
shop is available only between matches. Pure essence exercises the authentic
Buy X path; Air talisman is the smallest representative one-at-a-time reward.
The complete robe, master-robe, talisman, staff, and teleport-tablet catalog is
vertical data depth, not a missing mechanic.

## Live product surface

- `great_orb_project_data.py`: period gate/order, ordinary XP inputs,
  representative shop rows, policy vocabulary, and activity registration.
- `great_orb_project_logic.py`: entry, persistent rounds, score/duty doctrine,
  participation, essence capacity/crafting, token settlement, leave, manual
  shop, sanitization, and view projection.
- `runtime_actions.py` and `__init__.py`: review dispatch, Runecrafting XP,
  telemetry, achievements, save, terminal stop, and review/direct-action undo.
- `storage_pure.py`: schema 66 defaults, migration, sanitization, and persistent
  activity arbitration.
- `ui.py`: compact paginated Activities card with a visible level gate,
  pre-match policy/shop controls, and an active round scoreboard.
- `activityicons/great_orb_project.png`: normalized pre-cutoff art recorded in
  `assets_provenance.json` and reproducible through
  `tools/fetch_great_orb_project_assets.py`.

## Explicit omissions

- No wall clock, movement map, lobby timer, other player actors, manual wand
  targeting, or extra review for portals or reward collection exists.
- Exact hidden score, opposing-team, and essence distributions are not claimed.
- The horizontal shop does not claim the full period reward catalog.
- Runecrafter hat asset provenance was not period-qualified by the source
  import available in this pass, so the hat was not shipped as a representative
  reward merely to make the catalog look larger.
- No new owner-design gap surfaced.

## Verification

Focused pure, migration, registry, integration/undo, asset, and real offscreen
Qt tests cover entry through match settlement, early leave, manual purchases,
save migration, cadence, and the compact card. Closure verification completed
on `2026-07-21`:

- the non-Qt suite ran 2,184 methods: 1,897 ordinary passes and 287 expected
  dependency skips;
- the real offscreen-Qt suite ran the same 2,184 methods: 2,183 ordinary passes
  and one intentional skip;
- documentation, hard test-quality, compilation, JSON, diff, asset
  normalization, and worktree-safety gates passed;
- reachability reported 1,440 actions, 2,132 reachable items, 166 known orphan
  inputs, and 187 unresolved actions; this slice added one action and no new
  orphan;
- a fully restarted native Anki process showed one launcher, one menu, the
  paginated Minigames page, the normalized Great Orb Project icon, and an
  unclipped locked card with the level-50 gate. The match was not entered and
  the owner save was not mutated; and
- Kimi K3 was unavailable at its fresh quota gate, so Opus performed the UI
  taste pass. Every reproduced finding was corrected. Fable was not called.

The two early read-only Codex Workflows reconnaissance leaves were canceled
after failing to converge; neither produced evidence used by the
implementation. The primary agent independently reproduced the source and
substrate work above.
