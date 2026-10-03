# Source image query repair — 2026-10-03

Status: branch implementation and isolated HTTP proof complete; root acceptance pending.
Base: `0a6281292401f62a59804044ff195091559f2623`.
Branch: `goal/source-url-query-2026-10-03`.

Named URL query bytes are retained when the downloader requests original art.
Repeated parameters, blank values, encoded separators and existing source markers keep their values and encoding.
A missing source marker receives `source=original`; a lone wiki optimization token keeps its existing source-marker behavior.
SHA-1 refusal and the three-attempt boundary are unchanged.
Ordinary optimized downloads retain their original request and image normalization.

The local proof imports only downloader tooling and the focused test module.
It uses disposable localhost HTTP responses and temporary output directories.
Six behavior tests passed with zero skips after failing against the base implementation.
Four existing adjacent source/normalization tests also passed with zero skips.

The exact retained Crumble Undead source was served read-only through the same local downloader canary.
Its original path and query were retained while the host was replaced with localhost.
The unchanged source bytes measure 297 bytes, SHA-1 `263b75038c03b742bdfa93843623f38a656896b7`, SHA-256 `d994cf8e9c5cd33c40a613c4cb6152cd9c1305d75a381550021527adce256996`.
The base implementation refused these bytes because it corrupted `cb=20111119160524&format=original`.
The repair accepted the bytes; the mismatch scenario still refused after three attempts.
No source harvest, bundled asset, provenance hash or cutoff audit changed.

Raw commands, request paths, response byte counts, hashes and before/after results are retained outside the tracked tree:
`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/source-url-evidence/`.

Root must collect and run both `tests.test_fetch_assets` and `tests.historical_assets.test_fetch_assets_source_urls` explicitly.
`run_tests.py` whole-name precedence means the original `test_fetch_assets` selector does not include the new module.
The MacBook focused run, full plain branch proof, reachability audit and both merged promotion lanes remain pending.
Branch-side Qt is exempt under the standing contract's explicit promotion-gate exception.
The original S03 papercut stays open until root accepts the proof and promotion.
