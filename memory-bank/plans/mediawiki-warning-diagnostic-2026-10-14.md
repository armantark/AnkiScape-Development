# MediaWiki warnings must reach the operator — 2026-10-14

The shared asset client and cutoff auditor currently accept valid warning-bearing responses without a diagnostic.
Root selects a nonfatal stderr diagnostic. The retained S2/O6 review permits this policy.

## Scope

Change only the shared JSON boundary and meaningful behavior tests after C1 lands.
For each nonempty warnings value, print one diagnostic with the complete warning content to stderr.
Return the original payload unchanged. Empty or absent warnings produce no diagnostic.
Preserve stdout, valid results, request parameters, transport and API retries, cutoffs, classifications and provenance behavior.
Do not add a warning-specific retry, another logger, a wrapper, a parser framework or a live harvest.
No existing UI or artwork change is authorized.

## Failure domains and proof

Before production code changes, add behavior checks that exercise the real JSON boundary through fixture transport bytes.
Cover the shared image lookup and the real cutoff batch caller. Capture the missing diagnostic as the baseline failure.
Prove the full warning survives, the valid period result remains exact, stdout stays empty and one response yields one diagnostic.
Prove empty/absent warnings remain silent. Preserve the existing retry and refusal suite without weaker assertions.
Obtain fresh supported focused inventory and a zero-skip execution. Keep both full lanes serialized.
Resolve independent cross-lineage findings. Run the exact merged full remote gate, then its official land command.

[Baseline observation](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/c2-warning-contract/baseline-observation.json): main fdb1ac49, actual0; both real boundaries accepted the2011 revision with empty stdout/stderr. Only transport returned fixture bytes; no network request occurred. This observation is not a red acceptance-test run or implementation acceptance.
