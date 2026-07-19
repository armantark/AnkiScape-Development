#!/bin/zsh
# Overnight exhaustive pre-EOC content recon (Sol/Codex, network-enabled).
# Diffs the RuneScape Wiki's own period content indices against the AnkiScape
# design ledger. Read-intent: the prompt forbids repo edits; network is only
# for wiki reads. Run it before bed:
#
#   caffeinate -i tools/overnight_content_recon.sh
#
# Report lands in memory-bank/audits/overnight-content-recon-$(date).md
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y-%m-%d)"
OUT="$REPO/memory-bank/audits/overnight-content-recon-$STAMP.md"
P="$(mktemp)"
cat > "$P" <<'EOF'
# Overnight recon: exhaustive pre-EOC content diff (wiki-grounded)

You have network access for READING the RuneScape Wiki only. Do not edit any
repo file; your only output is the final markdown report.

Repo: current working directory (AnkiScape). Its design ledger is
`memory-bank/**/*.md` + `memory-bank/gap-backlog.json`. The prior recon and
its settled dispositions are in
`memory-bank/source-audits/recon-coverage-closure-2026-07-18.md` — do NOT
re-report anything already settled, pattern-determined, parked, or excluded
anywhere in the ledger.

Goal: enumerate, as exhaustively as the wiki allows, every gameplay surface
that existed in RuneScape on 2012-11-19 (the day before EOC), and report only
the ones the ledger does not own. Sources to walk (prefer pinned pre-cutoff
oldids; current pages are acceptable for enumeration but flag anything whose
period existence is uncertain):
- the Minigames, Distractions and Diversions, Miniquests, and Bosses lists;
- the 2010/2011/2012 game-update year pages (every content update after the
  last ledger-known item);
- Treasure Trails, task-set/diary, skill, and activity category indices;
- members/f2p activity lists and the pay-to-play content index.

Be polite to the wiki: sequential fetches, no parallel hammering.

For each candidate: grep the ledger (case-insensitive, all files). Report only
true absences or named-but-unowned items. Classify each: (a) needs an owner
design fork, (b) pattern-determined (name the owning contract), (c) needs an
explicit exclusion entry. Exclude post-2012-11-19 and OSRS-only content, and
purely social/cosmetic surfaces already covered by the blanket exclusions.

Output: a ranked markdown report — sections "Owner forks", "Pattern-determined
additions", "Exclusion candidates", "Uncertain period existence (needs oldid
check)" — every item with its wiki URL and the grep evidence of absence.
EOF
/Applications/ChatGPT.app/Contents/Resources/codex exec \
  -s workspace-write -c sandbox_workspace_write.network_access=true \
  -C "$REPO" -c model_reasoning_effort="xhigh" \
  -o "$OUT" - < "$P" 2>/dev/null
rm -f "$P"
echo "Report: $OUT"
