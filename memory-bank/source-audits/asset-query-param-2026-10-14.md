# Source audit: supported image-history parameters — 2026-10-14

Source: `11d4910b24a1d86a14118259fc9f078479e4e138`. Base: `2e7b6378871e0096515e1aaab7a64061c7aff7bc`.
Change: remove only unsupported `iidir=older` from `tools/audit_asset_cutoff.py`.
Keep the period cutoff, `iistart`, `iilimit=1`, retries, classifications, aliases and checkpoints.
Primary contract: https://www.mediawiki.org/wiki/API%3AImageinfo/en.
The retained actual warning is `Unrecognized parameter: iidir.`; the current primary module schema corroborates it.
This repair queries API documentation only. No image revision was fetched or replayed.

| Proof | Original result |
| --- | --- |
| Prepared disposable protocol canary, before repair | 1 test; exit 1; unsupported parameter refused after the existing four attempts |
| Complete module, after repair | 8 tests; exit 0; no skips |
| Papercut move | Exact incident moved; no-loss check against the base passed |

The protocol receiver is a test fixture; its refusal is not a fresh live wiki failure.
Existing post-cutoff, redirect and checkpoint cases passed; new persistent-error coverage preserves the four-attempt bound.
Raw evidence: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param.
Manifest: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param/source-manifest.json.
Manifest SHA-256: `1c2c885bc13a6d456bf28404495204c6b847f2d22f0c57f79c1dbf5399caf97a`; it gives the exact digest and path of every raw artifact.
Independent cross-lineage review, both full merged lanes and official landing remain pending.
No gameplay, art, existing UI, pinned baseline or audit acceptance criterion changes.
