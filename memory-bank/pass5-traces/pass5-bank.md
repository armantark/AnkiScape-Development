# pass5-bank trace

## Round 12 — verifier test refix

- Hypothesis: The carried-inventory implementation is correct, but its offscreen Qt regression still expects the pre-scrollbar fixed height of 58 pixels.
- Change: `a00f0354` (`test: match carried inventory strip height`). Updated the stale assertion to the 72-pixel height produced by the 44-pixel cell, 8 pixels of layout margins, 18-pixel horizontal scrollbar extent, and 2 pixels of frame width.
- Test results:
  - Targeted offscreen Qt regression: 1 test passed.
  - Full plain lane: 3,708 tests passed, 438 skipped (`python3 run_tests.py`).
  - Full offscreen Qt lane: 3,708 tests passed, 2 skipped (`QT_QPA_PLATFORM=offscreen python run_tests.py` in `.venv-qt`).
- Verdict: keep. The verifier rejection was a stale test expectation against the intentional scrollbar-aware strip height; both required lanes are green.
- Open questions: none. Owner playtest remains the final closure gate.
