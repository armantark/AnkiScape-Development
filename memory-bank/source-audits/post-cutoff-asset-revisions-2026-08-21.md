# Post-cutoff asset revision audit — 2026-08-21

The machine-readable record is
`memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json`.
`tools/audit_asset_cutoff.py` enumerated `assets_provenance.json` from source,
selected every record later than `2012-11-30T23:59:59Z`, and compared its
recorded SHA-1 with the newest source-wiki revision at or before that cutoff.
The report checkpoints each batch and reuses resolved rows on later runs.

## Measured result

| Classification | Assets |
| --- | ---: |
| No revision at or before the cutoff | 436 |
| Earlier revision byte-identical to the recorded revision | 0 |
| Earlier revision differs from the recorded revision | 143 |
| Unresolved | 38 |
| Pending | 0 |
| Total post-cutoff provenance records | 617 |

All 38 unresolved rows carry the exact reason `The recorded file page is now
missing from its source wiki.` A post-cutoff timestamp is therefore a warning,
not a verdict: it found 143 byte-different candidates, while 436 had no earlier
wiki revision to substitute and 38 could not be resolved.

Every `different` row keeps the compared revisions' timestamp, SHA-1, byte
count, and URL. The earlier side uses its archive URL, so a reviewer can identify
both inputs without repeating the history query.

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
claim that every one of the 143 differing rows has been inspected pixel by
pixel.

No asset was replaced by this audit.
