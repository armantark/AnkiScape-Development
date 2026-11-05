# 17: Review tests preserve the process RNG

**Status:** done

- [x] Reproduce the Relicym failure with eight workers at `1844cae18`.
- [x] Identify and repair shared-state cleanup without weakening ownership assertions.
- [x] Check full-pack Herblore output, strange-rock replacement, reload and undo through real reviews.
- [x] Supply Pillow outside Homebrew Python and pass the three affected plain-lane selectors.

The Bittercap review-undo test seeded the process RNG with `5` and left that state behind. The failing worker reached the Relicym review at seed 5 draw index `48`: `0.003383119374356758`. The ordinary Shattered Heart hook therefore replaced the new potion with `Strange rock (Herblore 1)`. A minimal replay runs the Bittercap test, consumes the intervening 48 draws, then runs the unchanged Relicym assertion. The cleanup now restores the caller's RNG state, and the Relicym persistence fixture explicitly rolls no rock. Product behavior is unchanged.

Synthetic real-review checks cover ordinary output, loose-rock replacement and bagged rocks with the full pack, including exact reload and undo. Evidence, diagnostic scripts, full-lane job records and logs: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/17/`. Final commands and results: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/reports/17.md`.
