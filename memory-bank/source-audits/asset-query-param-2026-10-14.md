# Supported image-history parameters: source audit — 2026-10-14

Source: `d59568900e6cdcd14ca52db151e977256ffa4a70`; base `2e7b6378871e0096515e1aaab7a64061c7aff7bc`.
Remove unsupported `iidir=older` from all four callers; each period fetcher validates the first revision against its existing cutoff and refuses a newer-first mixed response.
Retained contract: [S15](../audits/papercut-fix-slices-2026-10-03.md#s15--the-asset-audit-sends-an-unsupported-imageinfo-parameter).
Keep all configured cutoffs, iistart/iilimit, retries, classifications, aliases, checkpoints and provenance hashes.
Fetcher cutoff constants differ from the auditor's cutoff and remain unchanged; no art or provenance is requalified.
Primary API schema: https://www.mediawiki.org/wiki/API%3AImageinfo/en; no supported iidir parameter.

| Original proof | Result |
| --- | --- |
| Auditor request baseline / original module green | 1 red; then 8 green, no skips |
| S15 three-caller request/mixed-response baseline | 2 methods; 6 expected failing subcases |
| Final auditor/request/response coverage | 10 tests; exit 0; no skips |
| Broader plain and existing Qt neighbours | 27 each; exit 0; 2 existing Pillow skips; before equivalent timestamp-read reuse |
| Live read-only S15 canary, report in evidence | 2011-11-29T14:12:02Z Telegrab revision; no API warnings; no image/provenance write |
| Installed final metrics | All three fetchers CCN 15, cognitive 8; cap 15 preserved |

The initial strict protocol fixture is a canary, not a newly observed live API refusal. The correction models the original warning-plus-revision response and asserts outgoing parameter absence; no general API-warning handling is claimed.
Resolved audit-checkpoint reuse remains unchanged by inspection; no execution coverage of that branch is claimed.
The exact incident is preserved in the fixed archive. All 11 original manifest inputs still match their hashes.
Original manifest: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param/source-manifest.json`; SHA-256 `1c2c885bc13a6d456bf28404495204c6b847f2d22f0c57f79c1dbf5399caf97a`.
Correction manifest: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param/correction-s15/manifest.json`; SHA-256 `8e526c25bbac601c927f82b0efc5947b7620c77f9a1ad141bd200c668176358a`; exact raw paths/digests are inside.
Opus round 2 accepts F1/F2; no binding finding remains. Root resolved record notes O1/O2/O5/O6 and disposed of optional O3/O4.
Callers: `tools/audit_asset_cutoff.py`, `tools/fetch_navigation_icons.py`, `tools/fetch_agility_assets.py`, `tools/fetch_big_chinchompa_assets.py`.
Disposition: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param/opus-review-2/root-disposition.json`; SHA-256 `9716c97ea9ac50208948ee69b819405b853f50ede108dc620f1b18f48651e2a8`.
Exact merged `2fe9135819c85b04693f40ff5ed1a7ccd2973590` passed all nine remote-lane checks and officially landed; main was clean.
Original lanes: plain 5326 tests, 609.419s, skipped580; Qt 5326 tests, 842.283s, skipped5.
Retained original12 gate/lanes/land: `.git/ankiscape-promotion-evidence/2fe9135819c85b04693f40ff5ed1a7ccd2973590/merged-s15-gate/retention-manifest.json`; SHA-256 `b3ec9583681b8eb3c8e0a0f9b64b795afa547dd6332a9d805b11bea198ddab2b`.
No gameplay, existing UI, pinned baseline, audit limit or acceptance waiver change.
