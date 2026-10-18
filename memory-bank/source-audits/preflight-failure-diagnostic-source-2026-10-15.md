# Preserve preflight failure context

Source `02e61b51ab7f7346fe2d491152731ca03e9bf734` adds the discovered gate path and child status to stderr after a nonzero exit. Child output, exit status, silent success and disposable-index staging stay unchanged. No gameplay or existing UI changes.

Three real disposable-child regression cases failed twice before implementation. The focused suite then passed seven tests without skips. The first fixture-path mismatch and unsupported raw full-plain failure remain retained; neither is a pass.

The configured local MacBook plain run `plain-1792077844-1434070d` passed 5379 tests in603.515s with580 expected skips and outer exit0. Root verified the original host log and report. No SSH, dependency install, source-pin change or measuring-instrument change was used.

The original2026-10-02T21:09:33-0700 silent-child cause remains unexplained and its incident stays open. The new diagnostic closes only the missing wrapper context. Source verification does not grant merged-gate or landing acceptance.

Astra and K3 Standards/Spec reviews closed all findings. Exact candidate `c74a1c8a5ba639f7cb19133283496c4788d0ad31` passed all nine `--remote-lanes` checks and official `land` exit0. Gate plain5379/603.730s/580 skips and Qt5379/833.913s/5 skips passed with original outer reports0. Canonical main was clean after landing. No gameplay or native acceptance is claimed.

External evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/preflight-failure-diagnostic-source/`. Original files stay unchanged. `source-evidence-digests.json` binds the raw records:

- `committed-source.patch`: `4b8407d649d0dbf96cd2327a8ec379b13faf6c2bf68a4c1dc46818be9f2d8794`.
- `red-execution.final.json`: `656b6b69dc8b3e5763549553a41b5119d7f6a117155a0c2f1f3cbebb6d8c7c6c`.
- `red-execution-suv2wzhc.log`: `634f8e6523d697cd400752aa0ee57a30b28a05be56a7267d7dac4c362c1dd298`.
- `focused-canonical-execution.final.json`: `8d27ca1a284680399a3b6714ca85bf99d1aaa1be75dfd082106d5bf507048f6e`.
- `focused-canonical-execution-vsb8t2u3.log`: `a77b24a3574f4c50c821b736a11f28d4a558309cbf067029a929395f2f5f4a6e`.
- `full-plain-failures-hk6onp1y.log`: `dfb41c8db995aa71abaca43577b4035d691b6f3a490b68143c910f2bb1eec104`.
- `configured-full-plain-execution.pending.json`: `6f0878641ce585788b13817fdbead758bba6c945723cda2a8d35a115960295a7`.
- `configured-full-plain-execution.final.json`: `1dfa22a5f068ad16310b5943701f6111c523aa4df31b6b789f7d7d3748558e5c`.
- `configured-host-plain-1792077844-1434070d.log`: `459049ad85f5122bfd126e76ac91c5838efa1c797c0f9e0133d913a48ffb072d`.
- `configured-host-plain-1792077844-1434070d.report`: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`.
- `root-configured-source-plain-verification.json`: `c7bef52be16dc46c0ee325a6cba50f3f3456d951d613271bb770c14c15458bff`.
- `handback-configured.json`: `0c06ee2b17f8a2d05ae525ba673adee07a4a525b44d1d4713383b2bd66b62141`.
- `friction.txt`: `4ec278bc70d57322efd15ea1dec07ea06c8f53d6c02005c3ff4cf488d40e39e8`.

Exact gate and land evidence is retained in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/preflight-diagnostic-exact-merged-verification/`: `official-certificate.json` SHA256`d51b69ec78ef5508a65719089390bd01d9b4d781a1ffa911aae165710009e178`; `original-gate-full.log` SHA256`f6ea90cc9c62375a6c21150e5bdc39b040c4e98e28d95b2647bc8ce15df88141`; `plain-original-outer.log` SHA256`0b6642cce0314aad501da0b3b29bacc7306dfb3fa97907459f2198c995cbf290`; `qt-original-outer.log` SHA256`5d2902bdc8c7e35c9f4f76e35707e9e075fe65be308d601d1c6be54490ee56b7`; `official-land.json` SHA256`842835aae21b7496d21d40fa52c83ca10a63fd6db53191aa6c2880cfd7a5c2d4`; `preflight-diagnostic-official-land-7rqd3qub.log` SHA256`f11f84e1eb9fce7455c37873c9162162c4bbf87294a5ea70dd114a8ac888e5fa`.
The independent112-file retained packet is `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/retained-preflight-diagnostic-landed-c74a1c8a/retention-manifest.json`, SHA256`392caa31631819c0d523b18fdf3eacf503425b8b2e26c17cf399a69f07a98a57`. Root rehashed every retained file successfully. The manifest binds each original raw artifact; original failed receipts remain.
