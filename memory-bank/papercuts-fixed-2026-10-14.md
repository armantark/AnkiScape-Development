# Papercuts fixed — 2026-10-14

## Image-history requests use supported parameters

Disposition: fixed.

Evidence: Source 11d4910b24a1d86a14118259fc9f078479e4e138 removes only unsupported iidir from tools/audit_asset_cutoff.py. The pinned iistart, iilimit=1, four-attempt retry, post-cutoff refusal, alias and checkpoint behavior remain. Disposable protocol canary was red before repair; all 8 module tests then passed. Primary MediaWiki imageinfo parameter schema and raw receipts: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param. S15 correction source `d59568900e6cdcd14ca52db151e977256ffa4a70` also repairs the original icon getter and both equivalent fetchers, refuses mixed newer-first results, and retains a successful live canary/report outside the checkout. Final focused10 has no skips; unchanged-checkpoint behavior is inspection-only. Independent re-review and exact merged promotion remain pending.

- 2026-10-02T18:54:44-07:00 — Telegrab icon provenance lookup: the wiki imageinfo API returned `Unrecognized parameter: iidir.`; `iistart=2012-11-19T23:59:59Z` still returned the required `2011-11-29T14:12:02Z` revision. `tools/audit_asset_cutoff.py::_request_batch` also supplies this unsupported parameter.
