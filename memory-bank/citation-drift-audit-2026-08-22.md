# Citation drift audit — 2026-08-22

Status: implemented; existing drift is measured but deliberately not rewritten.

## Authority and method

Design-thread queue section 3.29 requires a mechanical check for Memory Bank
line citations. Repository-local citations are compared with the target text at
the commit that introduced the record line. Pinned external citations are read
from the named commit when its source checkout is available. Current external
source trees remain separately identified in the report when no usable commit
is named.

The audit reports the record location, cited target, prior text, current text,
and a unique relocated target when one exists. It never writes to a Memory Bank
record or source file.

## Measured baseline

The 2026-08-22 run scanned 552 Markdown files and found 1,381 citations. It
resolved 1,368: 466 repository-local, 326 pinned external, and 576 against
current external trees. It reported 416 stale citations and 13 citations whose
source checkout or identity is not available to the resolver.

The stale records were not edited in this slice. They are the remediation input
for later documentation-only work, not permission for automatic rewrites.
