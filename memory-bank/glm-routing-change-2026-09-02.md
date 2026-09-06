# GLM 5.3 Flash routing changed at 14:38 — 2026-09-02

Relayed by `claude-code-7f` as owner-approved, and verified here: fleet commits
`18bacd0`, `b2e5252` and `d2d7983` all exist in `~/fleet`, with subjects that
match the relayed rules.

1. GLM gets one bounded pass per brief and never orchestrates: no child agents,
   no review pipelines, no driving the code-review skill, no waiting on other
   work. Review orchestration belongs to the main orchestrator. A GLM driver of
   `/code-review` spent 333M tokens, 49 percent of all GLM tokens in 48 hours,
   running `date` in a loop while it waited on children, and reviewed the wrong
   range for its first half.
2. `glm-5.3-flash` stays pinned to fast providers at double price, for work
   somebody is waiting on. The Workflow-only twin `glm-5.3-flash-cheap` takes
   OpenRouter's cheapest route at half price and is the pick for background
   fan-out when nobody waits.
3. Any agent that must wait on a background task lets the harness re-invoke it
   on the task notification. It never polls with `date`, `ps` or `sleep`.

This seat's own GLM dispatch today (the preserved-ref guard) was a single
bounded pass with no children, so it already complied. The rules apply to every
dispatch from here on.
