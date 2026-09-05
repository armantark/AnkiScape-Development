# Goal queue maintenance papercuts

- 2026-09-05: While checking asset coverage, the driver guessed `tools/verify/*.py` and received `zsh:1: no matches found: tools/verify/*.py`. The actual full-lane entry points are `run_tests.py` and unittest discovery under `tests`. Asset normalization and provenance checks are in the full suite; these slices contain no asset edits. Do not run a broad asset network audit for this check.
