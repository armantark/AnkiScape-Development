# Navigation and activity icon audit — 2026-07-20

## Scope

This audit covers the icon vocabulary and activity categorization used by the
main menu, the Stats skill selector, Combat XP rows, Magic target rows, and the
Activities tree.
It does not claim that modern OSRS interface art is pre-EOC RuneScape art.
Where the owner selected modern interface art for clarity, that choice is
recorded as a visual-language exception rather than period evidence.

## Period anchors

- RuneScape Wiki `Shop` oldid `6460792`, timestamp
  `2012-10-23T17:07:12Z`, explicitly lists the general-store marker and the
  period shop-map icon family. The literal revision was retrieved through the
  MediaWiki API; its response had SHA-256
  `0f87af9dbff17342429ff6eebafe681483a6f748f6c7fd5d02fc3e8989e13f53`.
- `Activity icon.png` is pinned to the RuneScape Wiki file revision from
  `2011-11-17T04:09:26Z` and is used for the Activities hub.
- `Coins.png` is pinned to the RuneScape Wiki file revision from
  `2012-05-09T11:33:58Z` and is used for the Shop tab. This replaced the
  OSRS Store orb after a native-Anki check showed that it reads as a Bond icon.

## Owner-selected visual vocabulary

- Achievement Diaries alone use the green compass.
- D&D group headings use the yellow compass; Minigame group headings use the
  red compass. These compact OSRS interface files are clarity-oriented
  vocabulary selected by the owner, not period-mechanics evidence.
- Combat uses the owner-selected intertwined combat icon, Stats uses the
  familiar bar graph, Equipment uses the worn-equipment figure, Shop uses
  period coin art, and Skills uses the period Max cape. Each global tab has a
  unique icon.
- Every skill-facing surface now uses one coherent period highscores family:
  all 25 skill glyphs, including the Combat components, Summoning, and
  Dungeoneering, are pinned to RuneScape Wiki file revisions from
  `2012-01-21`. This supersedes the mixed large/detail/modern icon treatment.
  The exact revision timestamp, source URL, hash, and normalized path for each
  glyph live in `assets_provenance.json`; the reproducible manifest is
  `PERIOD_SKILL_ASSETS` in `tools/fetch_navigation_icons.py`.
- The canonical source files are tight-cropped transparent sprites no larger
  than 32 pixels on either axis after normalization. Qt explicitly scales them
  with aspect ratio preserved and fast pixel-art transformation: 24 pixels in
  the Stats grid and 32 pixels in Training. The same canonical file therefore
  cannot drift between Stats, Training, or the Combat XP rows.
- Stats follows the period three-column scan order from Attack through
  Dungeoneering in a fixed 344-pixel left selector. It shows live
  `current / base` levels in every cell and in the selected detail block.
  Temporary Combat boosts/drains come from `combat_current_levels`; Agility's
  existing action-bounded boost is projected while it remains active.
  Dungeoneering is deliberately display-only here until its settled gameplay
  contract is implemented. The total-level footer uses all 25 base levels.
- Every live Magic target has a dedicated spellbook icon rather than borrowing
  its output item's art. Shared spells intentionally reuse their real family
  glyph: one icon covers all output variants of Make Leather, Superheat Item,
  Plank Make, each jewellery enchantment level, and Enchant Crossbow Bolt.
  Of 114 targets, 105 use cutoff-pinned RuneScape Wiki or legacy RuneScape
  Wiki revisions. Nine exact sprites whose cutoff file revision did not
  survive are explicitly labeled visual fallbacks in provenance: Mobilising
  Armies Teleport, Tan Leather, Magic Imbue, Cure Plant, Fertile Soil, and the
  four Borrowed Power wrappers. These files are UI vocabulary, not mechanics
  evidence.
- Qt renders transparent source art directly. It does not synthesize white or
  neutral backing circles behind dark Combat targets, Combat XP glyphs,
  Shooting Stars, or activity rows. A ring that remains is part of the actual
  spellbook sprite.
- Fixed-size skill, Utility, and Activity target rows use one DPR-aware
  nearest-neighbor scaler with a 28-pixel slot and 32-pixel minimum row height.
  This normalizes small native sprites without blurring them or compositing a
  background. Hand-injected Landmark rows use the same path.

All downloaded files and exact source URLs, timestamps, hashes, and normalized
paths are recorded in `assets_provenance.json`. Reproducible manifests live in
`tools/fetch_navigation_icons.py` and `tools/fetch_magic_spell_assets.py`.

## Activity categorization

- `Big Chinchompa`, `Shooting Stars`, and `Familiarisation` are under
  `Distractions and Diversions`.
- `Livid Farm` remains under `Minigames`.
- Familiarisation is no longer shown in Equipment/Follower controls. It has a
  dedicated Activities card that starts its four-successful-review session and
  presents its two completion rewards.
- Utilities and Activities remain distinct navigation surfaces.

## Verification boundary

Offscreen Qt renders covered dark and light Stats at 900×560, dark Stats at
1400×900, the Training selector, the full top tab strip, Combat XP rows,
Shooting Stars, and Familiarisation. A fully quit and relaunched native Anki
process then verified the three-column Stats grid, live current/base values,
unified Training icons, and all six Combat XP icons in the actual macOS/Anki
runtime. A second full quit/relaunch after removing synthetic backings verified
that the native Combat XP and enemy rows render transparent source pixels
directly. The offscreen Magic render verifies the final spellbook icons and
normalized row rhythm. That native pass also preserved the earlier tree
branch-cell selection correction: branch and selected-row cells use the same
opaque blended green instead of inheriting macOS blue.

The Shop oldid proves the period shop-marker family and terminology. The final
Shop tab uses period coin art rather than a post-cutoff Store/Bond orb.

Kimi K3 returned `SHIP` for both the final Stats/Training delta and the
spell-icon/direct-transparency delta after checking hierarchy, density, period
scan order, current/base legibility, narrow/wide balance, icon coherence, and
selected-state treatment. A later fresh Claude quota probe succeeded, and
Fable independently returned `SHIP` for the same spell and Combat surfaces.
Both reviewers treated source-faithful spell-size variation as non-blocking
and confirmed that the remaining circular forms belong to the source glyphs.
Their final normalization review prompted the shared target-tree scaler and
Landmark-row cleanup; Kimi's post-change verdict remained `SHIP`.
