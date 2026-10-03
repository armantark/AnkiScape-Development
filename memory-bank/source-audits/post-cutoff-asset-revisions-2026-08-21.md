# Post-cutoff asset revision audit — 2026-08-21

The machine-readable record is
`memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json`.
`tools/audit_asset_cutoff.py` selected every `assets_provenance.json` record
later than the shared asset-fetch cutoff `2012-11-20T23:59:59Z`. It queried the
recorded source wiki first. When an OSRS lookup had no pre-cutoff revision, it
also queried the RS3 wiki for the same file title. Each affected row records
both wikis' answers explicitly.

## Recheck — 2026-10-02

Commit `075e90a9` tightened the shared cutoff to `2012-11-19T23:59:59Z`,
but did not regenerate the report. The unchanged audit was rerun against
current provenance at that stricter cutoff, first into a disposable report,
then at its normal path. The audit code and consistency test are unchanged.

The report now covers 516 post-cutoff records: 137 `different`,
35 `needs_inspection`, 222 `no_earlier_revision`, 122 `unresolved`,
0 `byte_identical`, and 0 `pending`. All earlier revision timestamps are
at or before the new cutoff. All 179 OSRS lookups have explicit RS3 results.

The previous committed report held 616 records. The 100 removed rows each
have current provenance at or before the stricter cutoff; no questioned
current record was excluded. Two retained rows changed: `shopitems/rune_crossbow.png`
now selects `2012-10-08T17:06:29Z` instead of release-day
`2012-11-20T21:58:46Z`; `constructionitems/spike_trap.png` is now `unresolved`
because its source page is missing. No asset or provenance was changed.

## Original measured result — 2026-08-21

| Lookup result | Assets |
| --- | ---: |
| RS3 source history: earlier revision differs | 138 |
| RS3 source history: no revision at or before the cutoff | 162 |
| RS3 source history: unresolved missing page | 38 |
| OSRS has no pre-cutoff revision; RS3 same-title revision differs and needs identity inspection | 135 |
| OSRS and RS3 have no same-title revision at or before the cutoff | 61 |
| OSRS has no pre-cutoff revision; RS3 same-title page is unresolved | 83 |
| Byte-identical earlier revisions, source or cross-wiki | 0 |
| Pending | 0 |
| Total post-cutoff provenance records | 617 |

An OSRS-only `no_earlier_revision` does not clear an asset. The Old School wiki
starts after this cutoff, so that result means only that the queried wiki cannot
answer the period-art question. All 279 such rows received the RS3 same-title
lookup shown above.

A same title across wikis is not proof of the same asset identity. The audit
therefore marks all 135 cross-wiki revision candidates as `needs_inspection`
rather than asserting that they are the recorded item's period art. Their
nested `cross_wiki_lookup` still records the mechanical SHA-1 classification,
revision timestamp, byte count, archive URL, and answering wiki.

Tightening the cutoff from `2012-11-30T23:59:59Z` did not change the questioned
set: it remains 617 paths. It did move five RS3 source rows from `different` to
`no_earlier_revision`, because their old candidate revisions were dated 22 or
25 November 2012: `herbloreitems/weapon_poison.png`,
`magicspells/borrowed_bones_to_peaches.png`,
`magicspells/borrowed_high_alchemy.png`,
`magicspells/borrowed_telegrab_wine_of_zamorak.png`, and
`magicspells/borrowed_teleport_to_house.png`.

## Five end-to-end checks

The ten original PNGs below were downloaded through the shared source-byte
path, which bypasses CDN PNG optimization. Every download matched the report's
SHA-1 and byte count before its dimensions and pixels were inspected.

| Asset | Recorded revision | Earlier revision | Visual verdict |
| --- | --- | --- | --- |
| `hunteritems/withered_vine.png` | 463 bytes, 29×26, `f945f32a2b70ea3ddcea4687e9a335a4ac1ce199` | 366 bytes, 28×25, `bf1eeb11c854f0f465ce384a966a468064eec81e` | Real art change: the blade silhouette, base, outline, and highlights differ. |
| `constructionitems/blue_charm.png` | 935 bytes, 32×29, `de54652c916604c24e8eb14fd5ba13e980086dc5` | 1,187 bytes, 31×27, `8e1b6b6f0f1d9ad5962c6ee68a15a011c360afd5` | Real art change: the central mark, rim shape, outline, and shading differ. |
| `magicitems/air_rune.png` | 1,302 bytes, 30×30, `93b8775e683fd3b48efc25608d359d227767601f` | 775 bytes, 28×29, `ea86af5ac02c3ec620a08522bfa17866636af37c` | Real art change: the rune silhouette, glyph placement, outline, and shading differ. |
| `constructionitems/gold_charm.png` | 1,363 bytes, 32×29, `ca48db1bee5bb3177fc88420988b6c25491e957a` | 1,166 bytes, 31×27, `bde30f49f6b5dcca7cb50b21cef30c5a9edf962b` | Real art change: the center glyph, rim geometry, outline, and highlights differ. |
| `constructionitems/steel_nails.png` | 418 bytes, 32×25, `39a2bb424ccd8907148e029066c85f629bdbbe9b` | 1,423 bytes, 30×23, `b08338fcae267bb23c3d51b71adf63a25970a528` | Real art change: the nail silhouettes, spacing, outline, and shading differ. |

None of these five cases is only cosmetic re-encoding. This visual check
validates the tool's `different` classification for the sample; it does not
claim that every one of the 138 source-wiki differing rows has been inspected
pixel by pixel.

No asset was replaced by this audit.
