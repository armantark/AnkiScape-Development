# Pre-EOC Wiki Parity Scraping

Mechanical procedure for pulling authentic pre-EOC numbers off `runescape.wiki`
when `game-main` (2011Scape rev 667) never implemented a mechanic. This is the
grunt-work half of Source Hierarchy #3 — hand it to GPT-5.6 (terra) with the
list of pages to pull; it needs no judgement, only the recipe below.

## Why this works

`runescape.wiki` (weirdgloop) imported the **full** Fandom edit history — every
article carries revisions back to ~2005 under the same `pageid`. So any page can
be read exactly as it stood on the eve of the Evolution of Combat
(**2012-11-20**), which is the last coherent pre-EOC snapshot. We resolve the
newest revision *before* that date and read its wikitext by `oldid`.

This does **not** replace `game-main`. The emulator stays primary for everything
it implements (exact XP, levels, tool tiers). The wiki fills gaps only where the
emulator stubbed content that authentically existed in the era — ancient curses,
the gilded/chaos altars, and similar. See the era-policy note in `SKILL.md`.

## The tool

Use `tools/wiki_parity.py` — do not re-derive the curl/JSON calls.

```bash
# Resolve the pre-EOC revision id + citation URL for a page
python3 tools/wiki_parity.py resolve "Ancient Curses"

# Dump the pre-EOC wikitext (auto-resolves the revid)
python3 tools/wiki_parity.py content "Ancient Curses"

# Filter to just the sections that mention a pattern (much smaller output)
python3 tools/wiki_parity.py content "Prayer" --grep "point every|drain"

# Read a specific revision directly (skips resolution)
python3 tools/wiki_parity.py content --revid 6535713

# Different cutoff — e.g. pin to the 2011Scape baseline instead of EOC
python3 tools/wiki_parity.py resolve "Gilded altar" --before 2011-10-04
```

Default cutoff is EOC (`2012-11-20T00:00:00Z`). Pass `--before 2011-10-04` to
pin to the emulator's own baseline when cross-checking a value the emulator
*does* implement.

## Procedure

1. **Resolve** each target page and record the `oldid` and timestamp. If the
   page is missing before the cutoff, the content did not exist pre-EOC — flag
   it, do not invent it.
2. **Pull** the wikitext, `--grep` to the relevant sections to keep output
   small. Wiki tables are `{|class="wikitable"` blocks; rows are `|-` and cells
   `|`. Effects/levels/drain-rates read straight out of the cells.
3. **Convert units.** The wiki quotes drain as "1 point every *x* seconds".
   game-main stores prayer points internally as `level × 10` and drains via
   `drainResistance = 60 + prayerBonus × 2` with a per-tick counter (Prayers.kt).
   The wiki's Prayer-bonus formula
   `modified interval = base interval × (1 + prayerBonus / 30)` is the same model
   (a bonus point = +2 on a base-60 resistance = 3⅓% slower). Reconcile to
   game-main's tick model; keep the wiki value only for effects the emulator
   lacks.
4. **Cross-check** every wiki number that overlaps `game-main` against the
   emulator; the emulator wins on conflict unless it is a known emulator bug.
5. **Cite.** Record `runescape.wiki/w/<Page>?oldid=<revid>` in the parity ledger
   next to each value, exactly as file-pins are recorded for emulator data.

## Gotchas

- **`{{beta}}` / update-flagged pages.** Some pre-EOC revisions are tagged beta
  or mid-update; confirm the value matches the stable release, not a test build.
- **OSRS wiki is not a pre-EOC source.** It is a 2007 baseline plus OSRS-only
  changes. Use only as a cross-check for 2007↔2012-unchanged content.
- **Art vs. data.** Icons changed across eras; for 2011-era art prefer the
  historical revision's `File:` links or a 2011Scape asset. Numbers are the job
  here; assets follow the normal `fetch_assets` path.
- **Rate-limit politely.** The tool sends a descriptive User-Agent; batch pages
  in one run rather than hammering the API in a tight loop.
