# Combat magic full-source gate diagnosis

Read-only diagnosis at 2026-09-18T12:03:07-07:00. Candidate `a8137bab2566b45e52585c580794a84563241b7e`, tree `19d384a1ff98edef40c208db2e74ff09bc00aa08`. P8 is clean. No source, pin, instrument, Git, or runtime changes were made. Only this report was written. Root owns the gate and MacBook.

## Measured failure

Root's full source gate session `16559` failed its plain lane: `Ran 5693 tests in 615.277s`; `FAILED (failures=2, skipped=1366)`. This diagnosis read the complete retained plain log `/tmp/ankiscape-magic-source-plain-failure-2026-09-18.log.gz`: 8572 decoded bytes, SHA-256 `1f97e11f941a4fe677783551007b7873f6a102c0bf7723364e2083cf2fe5ef1a` (verified here). The gate file `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/gate-a8137bab.log` contains only a tail of that lane.

| Failed assertion | Expected digest | Observed digest |
| --- | --- | --- |
| `test_first_wave_digests`, `tests/test_module_surface.py:73`, combat engine | `886cde5a31bb852ed696e8018c8954e707fff86c56dc0fc65633fd1b2f76f8c6` | `ce360383f420a4bd22595f8e7ee8af3ad4cb9c7c069a86ad355a1f82dc074d79` |
| `test_root_initializer_digest_under_qt`, `tests/test_module_surface.py:202`, root initializer | `c81943a0fc224bafcefc85a0fa3bd1a1c6bc242b73c2c9949d65efa8e1bcf030` | `2040bdd3887ef471b0aa1fcfbb4031180bccbfb458e4b46161a42eed7781b366` |

The plain suite explicitly launches the Qt interpreter for its root-initializer assertion. Its name does not establish the separate full Qt lane's outcome. That lane remains root-owned; no outcome is inferred here. The first-wave test stops at its first unequal line, so the failure does not establish that later surfaces or its later interpreter iteration passed.

## Supported static explanation

`tools/module_surface.py:38` includes a function's `__module__` and `__qualname__`; `_normalize_function` at line 82 includes that qualified name plus its signature. `dump_module` at line 300 serializes every public binding. Re-exporting a function preserves the object; it does not restore the object's old defining-module metadata.

AST and Git reads establish these exact moved public bindings:

| Surface | Binding | Original definition | Candidate definition |
| --- | --- | --- | --- |
| Engine | `combat_magic_preset_locked_reasons_pure` | `logic_pure_combat_model.py:413` | `logic_pure_combat_magic.py:32` |
| Engine | `combat_staff_covered_runes_pure` | `logic_pure_combat_model.py:2288` | `logic_pure_combat_magic.py:107` |
| Root, through the pure facade | `combat_dream_thrift_locked_reasons_pure` | `logic_pure_combat_model.py:403` | `logic_pure_combat_magic.py:22` |

Engine imports the first two through model at lines 117 and 383. The facade imports all three through model at line 438; root imports Dream through the facade at line 44. The model re-exports them from magic at line 9. The magic module assigns no replacement `__module__` or `__qualname__`. All three argument ASTs, absent return annotations, and undecorated status are unchanged. Dream and staff whole-function ASTs are identical; the preset validator's already-reviewed two-helper refactor is not whole-function-identical, and the surface instrument does not serialize its body.

The instrument, pinned test, engine, facade, and root initializer are each byte-identical to Git base `0d606cfd3e79fa660223a5b0a00974c9098a9447`. Thus a changed instrument or changed pinned expectation is ruled out for this candidate. The narrow supported cause is exposed defining-module metadata from the extraction. It predicts two engine qualified-name changes and one root qualified-name change. **This is a source-supported prediction, not proof that these are the only differences in the complete runtime dumps.** Neither full before/after dump was generated during this diagnosis.

## Proposed bounded repair for tomorrow

First, root should capture complete baseline/candidate engine and Qt-root surface dumps with the unchanged instrument on the same MacBook environment and package name. Confirm the exact changed records above, including any unexpected extra records; do not infer whole-dump equivalence from digest values.

If the dump delta is exactly that prediction, preserve the historical model-module metadata for these three public function objects at their new owner, using the existing package-relative metadata convention. Keep their implementation, globals, imports, signatures, and function identity at the magic owner. No wrappers, function reconstruction, root-globals rebinding, instrument change, threshold change, or digest repin is proposed.

This convention already exists for functions in `runtime/runtime_actions_activities_shared.py:28` and other activity parts (`__module__` set with the package-relative owner path). Ruling 42.2 item 3 records preservation of the old published module path; ruling 53 forbids rebuilding functions against another module's globals, which the proposed metadata-only repair does not do. No repair is authorized or applied by this report.

Proof still required: unchanged expected digests and full surface dumps in both supported interpreters; old/new export identity and magic-owned globals; unchanged behavior/comparison proofs on refreshed source and harness pins; independent review; normal source commit; complete source and exact merged-tree gates. Preserve the failed gate as failed. Current bounded comparison/focused acceptance is insufficient to claim full-source acceptance or landing.

## Diagnosis friction

- 2026-09-18T12:03:07-07:00: broad initial `git ls-files 'memory-bank/*'` returned 4597 paths / 109472 tokens and was truncated to the requested output budget; the combined tool result was also truncated (11953 tokens). Reads were narrowed to known files. No complete-bank-read claim is made.
- 2026-09-18T12:03:07-07:00: guessed tool path failed exactly: `rg: tools/module_surface_digest.py: IO error for operation on tools/module_surface_digest.py: No such file or directory (os error 2)`. Used the actual test-declared `tools/module_surface.py` afterward.
- 2026-09-18T12:03:07-07:00: guessed ruling path failed exactly: `rg: memory-bank/design-to-impl-rulings-2026-08-13.md: No such file or directory (os error 2)`. Filename discovery found `memory-bank/handoffs/design-to-impl-rulings-2026-08-13.md`.
- 2026-09-18T12:03:07-07:00: discovery included an absent directory and returned `rg: docs: No such file or directory (os error 2)`; its chained reads did not run and were retried against known paths.
- 2026-09-18T12:03:07-07:00: a 4255-token combined source read and an 8424-token broad ruling-context read exceeded their output budgets. Exact relevant sections and a compact AST binding audit were reread. A no-match `__module__` search exited 1 and skipped a chained history read; this was normal search behavior, not a product failure.

No local product import, test run, remote call, native action, branch edit, or Git mutation occurred. Diagnosis used existing failure logs, source text, Git objects, and stdlib AST/hash inspection only.
