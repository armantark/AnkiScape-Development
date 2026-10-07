# Exact source packets for native checks, 2026-10-07

Source `1bd9b9f9e10bdaca6a096b3369e159b542d6f842` adds only `tools/native/freeze_source.py` on baseline `b40f6c7af4f5adce580db1c1cc14efbc1e82f147`.
The 86-line file exactly matches the selected Git blob from `8d8888be054424ad68e1b156523b25edc1d32ed1`.
Source SHA-256 `96099993ebf0092e094787a717cc77b3692c235d355a1f6934a09a303f4e74e4`.
Astra and Kimi K3 approved the exact source. Root verified the committed bytes and imported helper compatibility.
The tool requires an exact clean revision and a new output directory. It writes source, archive and file hashes.
Its optional transfer uses the shipped retry helpers. It checks the remote commit and archive hash before it records success.
The tool does not open Anki or access a collection. It is independent of the parked menu and runtime acceptance.
Root remeasured `_transfer_bundle` at 2/1/1.7142857142857142 and `main` at 6/5/2.25 against unchanged 15/15/80 limits.
Compilation, help, all five audits and both local proofs exited 0.
Focused proof: 37 tests, 22.840s, no skips. Full local plain proof: 5220 tests, 1076.967s, 579 skips.
The clean packet passed. Wrong revision, dirty source, existing output and symlink cases each refused with exit 1.
Root verified the actual packet file hashes and archive contents.
The real MacBook transfer passed on two disposable files. Both bad transport-reply probes refused without a success receipt.
The initial probe failed before product import with `ModuleNotFoundError: No module named 'tools'`; the repaired probe passed. Both logs remain retained.
Root retained 162 raw files and their digests in [the proof manifest](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/1bd9b9f9e10bdaca6a096b3369e159b542d6f842/native-source-freezer-proof/retention-manifest.json>).
Manifest SHA-256 `32549bb35ea62b3a5d3a0c7d1cf08332c33bf8cd380e33d4ff49d3078cd87b8b`.
The exact merged full gate and official landing remain pending. This record does not accept any runtime or menu candidate.
