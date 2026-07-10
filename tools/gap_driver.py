#!/usr/bin/env python3
"""Autonomous gap-fill orchestrator for the AnkiScape /loop run.

Each item in memory-bank/gap-backlog.json is worked in its own git worktree by a
routed GPT-5.6 tier (terra for transcription ports, sol for wiki-sourced stubs),
then reviewed by GPT-5.6 Sol (max effort). Sol's structured verdict drives the
fold-in (merge to main). Every stage runs as a detached background process with a
done-marker, so each subcommand is non-blocking: a loop tick calls `collect` to
reap finished stages and advance the pipeline, then `start` to fill idle slots.

Subcommands:
  status   Print the ledger state.
  start    Launch the next pending item(s) up to max_concurrent, in fresh worktrees.
  collect  Reap finished impl/review stages: commit, launch review, or fold in.
  tick     collect then start (the per-loop entrypoint).

Pipeline states:
  pending -> in_progress(impl) -> reviewing -> merged
  (failure branches: review_failed | impl_failed | empty | merge_conflict)
"""
import json
import os
import shlex
import subprocess
import sys
import time

REPO = "/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork"
LEDGER = os.path.join(REPO, "memory-bank/gap-backlog.json")
OPS = "/private/tmp/ankiscape-gap-ops"
WORKTREES = os.path.join(OPS, "worktrees")
GAMEMAIN = "/Users/ArmanTarkhanian1/Downloads/game-main"
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex"

ACTIVE = {"in_progress", "reviewing"}


def load():
    with open(LEDGER) as f:
        return json.load(f)


def save(data):
    tmp = LEDGER + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, LEDGER)


def item_dir(iid):
    d = os.path.join(OPS, iid)
    os.makedirs(d, exist_ok=True)
    return d


def skill_module(skill):
    return f"{skill.lower()}_data"


_LAST_LAUNCH_FILE = os.path.join(OPS, ".last_codex_launch")
_STAGGER_SECS = 12


def _stagger():
    """Codex boots by removing and reinstalling a shared system-skills dir under
    ~/.codex; two codex processes starting within ~a second of each other race on
    it and one dies with "Directory not empty" (exit 1, no output). Serialize the
    startup window across ALL invocations via a persisted timestamp, so separate
    `tick`/`refix`/`rereview` runs stagger too."""
    try:
        last = os.path.getmtime(_LAST_LAUNCH_FILE)
        wait = _STAGGER_SECS - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
    except FileNotFoundError:
        pass
    with open(_LAST_LAUNCH_FILE, "w") as f:
        f.write(str(time.time()))


def launch(cmd_str, cwd, done, exit_file, log):
    """Fire a detached background stage that records its exit code and a done marker."""
    _stagger()
    for p in (done, exit_file):
        try:
            os.remove(p)
        except FileNotFoundError:
            pass
    wrapper = f"( {cmd_str} ); echo $? > {shlex.quote(exit_file)}; touch {shlex.quote(done)}"
    subprocess.Popen(
        ["bash", "-lc", wrapper],
        cwd=cwd,
        stdout=open(log, "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def git(args, cwd=REPO, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


# ---------------------------------------------------------------- prompts

def impl_prompt(item, wt):
    module = skill_module(item["skill"])
    common = f"""Repository (this git worktree, edit here): {wt}
Reference 2011Scape emulator source (READ-ONLY, never edit): {GAMEMAIN}

Goal: {item['title']}
Details: {item['detail']}
Skill data module to extend: {module}.py

Hard constraints:
- Match the module's existing conventions EXACTLY (same dataclass/tuple shape, field names, naming style, ordering, id registration). Additions must read as if written by the module's original author.
- Wire any new item ids into item_registry.py / constants.py the same way sibling rows are wired. Do NOT run network asset fetches.
- Do not invent numeric values. Do not add balance clamps. Do not touch unrelated skills, combat, or Prayer. Preserve every existing row.
- No new abstractions or refactors of existing code. Smallest correct diff.
- This is an automated gap-fill worker. Do NOT create, open, upload, or surface HTML status artifacts, and do not run Postplan. Keep intermediate communication entirely in the requested -o report, logs, tests, and source-audit/Memory Bank text when materially needed. The orchestrator owns one consolidated human-facing artifact at the terminal audited state.
- Do NOT commit, push, or edit git config. Just edit files.
- After editing, from {wt} run: python -c "import {module}" and fix any error until it imports cleanly.
"""
    if item["root_cause"] == "transcription":
        return f"""You are porting authentic pre-EOC RuneScape content into the AnkiScape Anki add-on, for Claude, in an isolated worktree. game-main HAS this data; transcribe it faithfully.

{common}
Method:
1. Read {module}.py to learn its exact conventions and how rows register.
2. Read the referenced game-main Kotlin source ({item['source']}). Transcribe EVERY authentic row AnkiScape is missing, using game-main's exact XP and level values (game-main wins all value conflicts).
3. Add the missing rows. If a game-main row references an item AnkiScape lacks, add the item id like its siblings.

Report (to the -o file): rows added, the game-main source lines each came from, rows deliberately omitted and why, and the `import {module}` result.
"""
    return f"""You are adding authentic pre-EOC RuneScape content that the 2011Scape emulator STUBBED (it is absent from game-main), into the AnkiScape add-on, for Claude, in an isolated worktree. Source it from the wiki pinned to the eve of EOC.

{common}
Wiki source hint: {item['source']}
Pre-EOC wiki tool (already in repo): tools/wiki_parity.py

Method:
1. Read {module}.py to learn its exact conventions.
2. Pin authentic values with: python tools/wiki_parity.py resolve "<Page>"  then  python tools/wiki_parity.py content "<Page>" --grep <regex>  (default cutoff is 2012-11-20). Record the oldid.
3. Transcribe authentic level requirements, XP, and outputs into the module's conventions. If the pinned revision lacks a specific value, mark it TODO — never guess.
4. If the content needs engine wiring beyond the data module, add the data rows plus a minimal clearly-marked stub hook and describe the remaining wiring in the report.

Report (to the -o file): every authentic value added WITH its wiki oldid citation, what engine wiring remains, and the `import {module}` result.
"""


def refix_prompt(item, wt):
    module = skill_module(item["skill"])
    blocking = item.get("verdict", {}).get("blocking", [])
    issues = "\n".join(f"  {i}. {b}" for i, b in enumerate(blocking, 1))
    src = ("game-main (exact values; game-main is authoritative and never invent a "
           "method/binding it does not define)" if item["root_cause"] == "transcription"
           else "the cited wiki oldid (pre-2012-11-20)")
    return f"""You previously attempted this AnkiScape gap-fill for Claude in this worktree. Your change is committed as HEAD on branch {item['branch']}. A senior reviewer (GPT-5.6 Sol) BLOCKED it from merging for these specific reasons:

{issues}

Repository (this git worktree, edit here): {wt}
Reference 2011Scape emulator source (READ-ONLY, never edit): {GAMEMAIN}
Skill data module: {module}.py
Original task: {item['title']} — {item['detail']}
Source of truth: {src}

Fix EXACTLY the blocking issues above, building on the existing committed work — keep everything the reviewer did not object to. If a blocking issue means content you added is NOT faithfully backed by the source (e.g. an invented method with no emulator tool binding), REMOVE it / restore it to its prior deferred state rather than inventing support for it. Do not add balance clamps or post-EOC content. Do not touch unrelated skills, combat, or Prayer. Smallest correct diff. Do NOT commit or push.

This is an automated gap-fill refix. Do NOT create, open, upload, or surface HTML status artifacts, and do not run Postplan. Keep the intermediate result in the requested -o report, tests, and source files only; the orchestrator owns the single terminal artifact.

After editing, from {wt} run: python -c "import {module}" and any tests the reviewer named, and fix until clean. Report (to the -o file) how you addressed each numbered blocking point.
"""


def review_prompt(item, wt, branch):
    module = skill_module(item["skill"])
    src = "game-main (exact values)" if item["root_cause"] == "transcription" else "the cited wiki oldid (pre-2012-11-20)"
    return f"""You are the senior reviewer (GPT-5.6 Sol) for an AnkiScape gap-fill change in an isolated worktree, working for Claude. Decide whether to fold it into main.

Worktree: {wt}
The change is committed as the HEAD commit on branch {branch}. Inspect it with:  git -C {wt} log -1 -p
Reference emulator (read-only): {GAMEMAIN}

Task the change was meant to accomplish: {item['title']} — {item['detail']}

This is an automated verifier pass. Do NOT create, open, upload, or surface HTML status artifacts, and do not run Postplan. Write only the requested verdict JSON and short -o review report.

Judge on:
- Parity: XP/level/output values faithful to {src}? No invented numbers, no post-EOC content, no invented balance clamps.
- Correctness: from {wt}, run  python -c "import {module}"  — must import cleanly.
- Convention fit: additions match the module's existing dataclass/naming/registration style; no unrelated edits; no refactors; combat/Prayer untouched.
- Completeness: did it actually add the missing content the task asked for?

Write your verdict as JSON to {wt}/.gap-review/verdict.json (create the dir) with EXACTLY this schema:
{{"approved": true or false, "blocking": ["issue", ...], "notes": "one paragraph"}}
Set approved=true only if you would fold this into main as-is. Any blocking parity/correctness issue => approved=false with the issue listed. Also write a short prose review to the -o file. Do not modify any source file other than creating the verdict JSON.
"""


# ---------------------------------------------------------------- stages

def running_count(data):
    # Only impl runs consume a concurrency slot; Sol reviews run on top so they
    # never stall the pipeline.
    return sum(1 for it in data["items"] if it.get("status") == "in_progress")


def _active_skills(data):
    # Any item still holding a worktree (impl or review) locks its skill's data
    # module, so we never run two same-skill ports in parallel — they would both
    # edit e.g. crafting_data.py and collide at merge.
    unlocked = {"pending", "merged", "needs_grill"}
    return {
        it["skill"]
        for it in data["items"]
        if it.get("worktree") and it.get("status") not in unlocked
    }


def pick_next(data):
    # Auto-fill ONLY transcription ports (game-main is authoritative — zero design
    # input). Stub items are new activity/mechanic systems that need the owner's
    # modeling decisions; they are parked as needs_grill and never auto-launched.
    merged = {it["id"] for it in data["items"] if it.get("status") == "merged"}
    busy_skills = _active_skills(data)
    cands = []
    for it in data["items"]:
        if it.get("status") != "pending":
            continue
        if it.get("root_cause") != "transcription":
            continue
        if it["skill"] in busy_skills:
            continue
        deps = it.get("depends_on", [])
        if not all(d in merged for d in deps):
            continue
        cands.append(it)
    cands.sort(key=lambda it: it["rank"])
    return cands[0] if cands else None


def start(data):
    policy = data["policy"]
    started = []
    while running_count(data) < policy["max_concurrent"]:
        item = pick_next(data)
        if item is None:
            break
        iid = item["id"]
        d = item_dir(iid)
        wt = os.path.join(WORKTREES, iid)
        branch = f"gap/{iid}"
        os.makedirs(WORKTREES, exist_ok=True)
        git(["worktree", "prune"], check=False)
        git(["worktree", "remove", "--force", wt], check=False)
        subprocess.run(["rm", "-rf", wt], check=False)
        git(["branch", "-D", branch], check=False)
        r = git(["worktree", "add", "-b", branch, wt, "main"], check=False)
        if r.returncode != 0:
            item["status"] = "impl_failed"
            item["note"] = "worktree add failed: " + r.stderr.strip()[:300]
            save(data)
            continue
        tier = policy["transcription_tier"] if item["root_cause"] == "transcription" else policy["stub_tier"]
        prompt_path = os.path.join(d, "impl_prompt.md")
        with open(prompt_path, "w") as f:
            f.write(impl_prompt(item, wt))
        report = os.path.join(d, "impl_report.md")
        log = os.path.join(d, "impl.log")
        done = os.path.join(d, "impl.done")
        exit_file = os.path.join(d, "impl.exit")
        cmd = (
            f"{shlex.quote(CODEX)} exec --yolo -C {shlex.quote(wt)} "
            f'-c model={shlex.quote(tier)} -c model_reasoning_effort=high '
            f"-o {shlex.quote(report)} - < {shlex.quote(prompt_path)} 2>&1"
        )
        launch(cmd, cwd=wt, done=done, exit_file=exit_file, log=log)
        item.update({
            "status": "in_progress", "worktree": wt, "branch": branch, "tier": tier,
            "impl_report": report, "impl_log": log, "impl_done": done, "impl_exit": exit_file,
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        save(data)
        started.append(iid)
    return started


def _launch_review(item, d, policy):
    """Launch (or relaunch) the Sol review for an already-committed branch and set
    the item to `reviewing`. Shared by collect and the `rereview` recovery path."""
    wt = item["worktree"]
    rp = os.path.join(d, "review_prompt.md")
    with open(rp, "w") as f:
        f.write(review_prompt(item, wt, item["branch"]))
    rreport = os.path.join(d, "review_report.md")
    rlog = os.path.join(d, "review.log")
    rdone = os.path.join(d, "review.done")
    rexit = os.path.join(d, "review.exit")
    cmd = (
        f"{shlex.quote(CODEX)} exec -s workspace-write -C {shlex.quote(wt)} "
        f'-c model={shlex.quote(policy["review_tier"])} '
        f'-c model_reasoning_effort={shlex.quote(policy["review_effort"])} '
        f"-o {shlex.quote(rreport)} - < {shlex.quote(rp)} 2>&1"
    )
    launch(cmd, cwd=wt, done=rdone, exit_file=rexit, log=rlog)
    item.update({
        "status": "reviewing", "review_report": rreport, "review_log": rlog,
        "review_done": rdone, "review_exit": rexit,
        "verdict_path": os.path.join(wt, ".gap-review/verdict.json"),
    })
    item.pop("verdict", None)


def refix(data, iid):
    """Relaunch the impl on a review_failed worktree with the reviewer's blocking
    points layered on the committed attempt. collect() then commits the follow-up
    and re-reviews it. Use for content rejections (invented values, omissions);
    use rereview for pure infra flakes."""
    item = next((it for it in data["items"] if it["id"] == iid), None)
    if item is None:
        return f"no such item: {iid}"
    wt = item.get("worktree")
    if not wt or not os.path.isdir(wt):
        return f"{iid}: worktree missing ({wt}); cannot refix"
    if not item.get("verdict", {}).get("blocking"):
        return f"{iid}: no blocking feedback recorded; nothing to refix"
    d = item_dir(iid)
    tier = data["policy"]["transcription_tier"] if item["root_cause"] == "transcription" else data["policy"]["stub_tier"]
    prompt_path = os.path.join(d, "refix_prompt.md")
    with open(prompt_path, "w") as f:
        f.write(refix_prompt(item, wt))
    report = os.path.join(d, "impl_report.md")
    log = os.path.join(d, "impl.log")
    done = os.path.join(d, "impl.done")
    exit_file = os.path.join(d, "impl.exit")
    cmd = (
        f"{shlex.quote(CODEX)} exec --yolo -C {shlex.quote(wt)} "
        f'-c model={shlex.quote(tier)} -c model_reasoning_effort=high '
        f"-o {shlex.quote(report)} - < {shlex.quote(prompt_path)} 2>&1"
    )
    launch(cmd, cwd=wt, done=done, exit_file=exit_file, log=log)
    item.update({"status": "in_progress", "tier": tier,
                 "impl_report": report, "impl_log": log, "impl_done": done, "impl_exit": exit_file})
    item.pop("verdict", None)
    save(data)
    return f"{iid}: refix impl relaunched ({tier}) with reviewer feedback"


def rereview(data, iid):
    """Relaunch a Sol review that failed for infrastructure reasons (codex startup
    race, killed process) rather than a content rejection. The branch is already
    committed in its worktree; this just re-runs the reviewer."""
    item = next((it for it in data["items"] if it["id"] == iid), None)
    if item is None:
        return f"no such item: {iid}"
    wt = item.get("worktree")
    if not wt or not os.path.isdir(wt):
        return f"{iid}: worktree missing ({wt}); cannot re-review"
    _launch_review(item, item_dir(iid), data["policy"])
    save(data)
    return f"{iid}: Sol review relaunched"


def _finished(path):
    return path and os.path.exists(path)


def collect(data):
    events = []
    policy = data["policy"]
    for item in data["items"]:
        st = item.get("status")
        iid = item["id"]
        wt = item.get("worktree")
        d = item_dir(iid)

        if st == "in_progress" and _finished(item.get("impl_done")):
            code = _read_exit(item.get("impl_exit"))
            if code != 0:
                item["status"] = "impl_failed"
                item["note"] = f"codex impl exit {code}; see {item.get('impl_log')}"
                events.append(f"{iid}: impl FAILED (exit {code})")
                save(data)
                continue
            git(["add", "-A"], cwd=wt, check=False)
            # The reviewer writes its verdict into <wt>/.gap-review; never let that
            # artifact contaminate the branch (and thus the eventual merge to main).
            git(["rm", "-r", "--cached", "--ignore-unmatch", "-q", ".gap-review"], cwd=wt, check=False)
            diff = git(["diff", "--cached", "--stat"], cwd=wt, check=False)
            if not diff.stdout.strip():
                item["status"] = "empty"
                item["note"] = "codex produced no changes"
                events.append(f"{iid}: EMPTY (no changes)")
                save(data)
                continue
            git(["commit", "-m", f"gap-fill: {item['title']} ({iid})"], cwd=wt, check=False)
            _launch_review(item, d, policy)
            events.append(f"{iid}: impl committed, Sol review launched")
            save(data)

        elif st == "reviewing" and _finished(item.get("review_done")):
            verdict = _read_verdict(item.get("verdict_path"))
            item["verdict"] = verdict
            if verdict.get("approved") is True:
                m = git(["merge", "--no-ff", item["branch"], "-m",
                         f"gap-fill: fold in {item['title']} ({iid}) [Sol-approved]"], check=False)
                if m.returncode != 0:
                    git(["merge", "--abort"], check=False)
                    item["status"] = "merge_conflict"
                    item["note"] = "auto-merge conflicted: " + m.stderr.strip()[:300]
                    events.append(f"{iid}: MERGE CONFLICT (left for manual)")
                else:
                    git(["worktree", "remove", "--force", wt], check=False)
                    item["status"] = "merged"
                    events.append(f"{iid}: MERGED (Sol approved)")
            else:
                item["status"] = "review_failed"
                item["note"] = "Sol blocking: " + "; ".join(verdict.get("blocking", []))[:400]
                events.append(f"{iid}: review FAILED — {item['note'][:120]}")
            save(data)
    return events


def _read_exit(path):
    try:
        with open(path) as f:
            return int(f.read().strip() or "1")
    except Exception:
        return 1


def _read_verdict(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return {"approved": False, "blocking": [f"verdict.json unreadable: {e}"], "notes": ""}


def status_report(data):
    from collections import Counter
    c = Counter(it.get("status", "pending") for it in data["items"])
    print("=== gap backlog ===")
    for k in ("pending", "in_progress", "reviewing", "merged", "review_failed",
              "impl_failed", "empty", "merge_conflict", "blocked"):
        if c.get(k):
            print(f"  {k:14s} {c[k]}")
    print("--- per item ---")
    for it in sorted(data["items"], key=lambda x: x["rank"]):
        line = f"  #{it['rank']:>2} {it['id']:<32} {it.get('status','pending'):<14} {it['root_cause']:<13} {it.get('tier','')}"
        note = it.get("note")
        if note:
            line += f"  :: {note[:80]}"
        print(line)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    os.makedirs(OPS, exist_ok=True)
    data = load()
    if cmd == "status":
        status_report(data)
    elif cmd == "start":
        print("started:", start(data) or "(none — at capacity or no eligible pending)")
    elif cmd == "collect":
        ev = collect(data)
        print("\n".join(ev) if ev else "(nothing to collect)")
    elif cmd == "rereview":
        if len(sys.argv) < 3:
            print("usage: gap_driver.py rereview <item-id>")
            sys.exit(2)
        print(rereview(data, sys.argv[2]))
    elif cmd == "refix":
        if len(sys.argv) < 3:
            print("usage: gap_driver.py refix <item-id>")
            sys.exit(2)
        print(refix(data, sys.argv[2]))
    elif cmd == "tick":
        ev = collect(data)
        st = start(data)
        print("collect:", "; ".join(ev) if ev else "(none)")
        print("started:", st or "(none)")
        status_report(load())
    else:
        print(f"unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
