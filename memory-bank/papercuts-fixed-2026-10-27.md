# Papercuts fixed — 2026-10-27

## Bounded generated-catalog discovery

Disposition: fixed.

Evidence: already fixed: tools/repo_search.py DEFAULT_EXCLUDES omits shop_data.py/construction_data.py/combat_data.py; search_text uses --max-columns-preview and refuses incomplete result sets. python3 tools/repo_search.py Bucket data --max-results 2 --max-columns 120 returned two bounded results and exit 2 with Search stopped at 2 results. General packet/output truncation remains open.

- 2026-10-15T14:44:37.517135+00:00 — Warning: truncated output (original token count: 612614) rg matched generated single-line data/shop_data.py, defeating line-count bounds (1401878 bytes omitted). Switched to AST shape and filtered literals, never imported shops; no omitted output used as absence or values.
- 2026-10-15T15:03:49.254636+00:00 — A line search included the generated one-line data/shop_data.py. The result reported original token count583797 and1286609 bytes omitted. The Bucket producer was then read by AST at the exact shop/key. Omitted output supplied no evidence.
- 2026-10-15T15:48:58.426136+00:00 — Read-only source qualification round27 reported inspection friction (original event timestamp was not captured; this is Root receipt time): 2026-10-15: A Construction grep emitted a giant single-line literal; output original_token_count56964 truncated. No raw generated shop line was dumped. Later supply reads used AST projections.
- 2026-10-15T15:48:58.426136+00:00 — Read-only source qualification round28 reported inspection friction (original event timestamp was not captured; this is Root receipt time): {"at":"2026-10-15","what":"A git grep included the generated one-line shop literal despite the explicit prohibition.","path":"/Users/armantarkhanian/ankiscape_worktrees/pool/.treehouse/AnkiScape-091389/2/AnkiScape/data/shop_data.py","exact_tool_summary":"Warning: truncated output (original token count: 612260); ... 1400464 bytes omitted ...","effect":"Read-only output failure. The report records it for Root. Later inspection used AST-selected shop rows; raw literal is not embedded in this packet.","class_correction":"Select fields before printing; never grep a generated literal file directly.","recorded_at":"2026-10-15T15:43:28.040762+00:00","event_timestamp_status":"Exact event timestamp was not captured; recorded_at is the report timestamp."}
