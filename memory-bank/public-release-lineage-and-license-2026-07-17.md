# Public Derivative Release Lineage and License Decision — 2026-07-17

Status: **product disposition settled; go-live gates not yet executed.**

This record governs any public AnkiWeb release of the current AnkiScape
checkout. It replaces the unresolved “personal fork versus public derivative”
question with a concrete release posture. It is not permission to upload before
the gates below are closed.

## Settled product disposition

AnkiScape may be prepared for a public derivative release. The honest product
description is:

> A radically expanded derivative fork of AnkiScape. Wilson Yeh's original
> implementation remains the recognizable foundation, while the present
> product, architecture, systems, content, tests, documentation, and asset
> breadth are overwhelmingly maintained by Arman Tarkhanian.

Do not describe the release as Wilson's current project, a minor update to his
add-on, or an independent rewrite. The public identity must preserve both parts
of the truth:

- Wilson Yeh (`wilson-taiwan`) is credited prominently as the original creator.
- Arman Tarkhanian is identified as the independent maintainer and author of
  the substantially expanded derivative.

The release should use a distinct name and a new AnkiWeb listing. “AnkiScape
Expanded” is the current working example, not a locked final title. Do not
replace, impersonate, or publish as an update to Wilson's existing AnkiWeb item
`1808450369` unless he explicitly transfers that listing.

## Lineage measurement snapshot

The 2026-07-17 audit compared Wilson's final public GitHub commit
`e65cae5e44e0658179f549c17ee29f2c3d05b6ce` with local commit
`709f9a9b8929f70d751fd9ebd992d2b254e4ca30`.

Two percentages answer different questions:

- **About 2.2% of the current production-code footprint** is surviving Wilson
  code when counting only normalized unchanged runs of at least three lines.
- **About 70.0% of Wilson's original production code still survives** under
  that same conservative rule. A more permissive exact-line comparison yields
  2.3% of the current footprint and 73.6% of the original.

The project is therefore overwhelmingly expanded but still plainly derivative.
The original architecture remains visible: 132 of 144 original same-path class
and function names survive.

Snapshot scale:

- production Python: 3,306 to 121,881 cloc code lines, about 36.9 times;
- all Python: 4,375 to 168,313 cloc code lines, about 38.5 times;
- tracked files: 159 to 3,962, about 24.9 times;
- PNG assets: 65 to 3,175, about 48.8 times; and
- production Python files: 13 to 63, about 4.8 times.

These are a dated provenance measurement, not hand-maintained live counters.
Regenerate them from Git and `cloc` for release copy or a future milestone.
They estimate surviving content; they do not allocate legal ownership.

## Repository and license posture

GitHub currently records `armantark/AnkiScape-Development` as a fork of
`wilson-taiwan/AnkiScape-Development`, but the local `main` history begins with
an Arman-authored root and does not preserve Wilson's 17 commits. The GitHub
fork badge is useful lineage evidence, but it disappears from an AnkiWeb
package and cannot substitute for package-level credit.

Neither GitHub repository currently contains a detected license file. Wilson's
existing AnkiWeb item is linked from his source and is item `1808450369`.
AnkiWeb's current terms say that add-ons without an explicitly stated license
are assumed to be AGPL-3.0. Treat that as the working derivative-license basis,
not as a reason to skip direct clarification.

Before public upload:

1. Contact Wilson and obtain a written acknowledgement or license
   clarification for the public derivative release.
2. Add an explicit AGPL-3.0-or-later compatible license to this repository.
3. Add durable `NOTICE` or `CREDITS` attribution naming Wilson, linking the
   original project, naming Arman as the independent maintainer, and describing
   the release as a substantially expanded fork.
4. Put the same lineage near the top of the GitHub README and AnkiWeb listing.

If Wilson objects or the license basis becomes materially disputed, stop the
release and resolve the rights question rather than relying on the size of
Arman's contribution.

## Public attribution copy

Use this as the default short attribution unless later wording is explicitly
approved:

> AnkiScape Expanded is a substantially expanded fork of AnkiScape, originally
> created by Wilson Yeh (`wilson-taiwan`). This fork is independently maintained
> by Arman Tarkhanian and has diverged extensively in scope, systems,
> architecture, content, and testing.

Follow it with both complete links:

- Original source:
  `https://github.com/wilson-taiwan/AnkiScape-Development`
- Expanded fork:
  `https://github.com/armantark/AnkiScape-Development`

Do not bury this at the bottom of a long listing or rely only on GitHub's
“forked from” banner.

## Wilson outreach copy

Use this as the default concise outreach:

> Hi Wilson — I wanted to give you a heads-up before publishing anything. I
> started from your AnkiScape add-on and have expanded it very substantially
> into a much larger pre-EOC progression system. I plan to publish it as a
> separate, clearly labeled fork, credit you prominently as the original
> creator, link your repository, and release my derivative under
> AGPL-3.0-or-later. I will not replace or present it as an update to your
> existing AnkiWeb listing. Are you comfortable with that attribution and
> licensing description, or is there anything specific you would like me to
> preserve?

Preserve the response with the release records. Do not overstate silence as
approval.

## Ordered go-live gates

### 1. Lineage and licensing

- Obtain and retain Wilson's written acknowledgement or clarification.
- Add the explicit compatible license.
- Add `NOTICE` or `CREDITS`.
- Add the approved lineage wording to the README and release description.

### 2. Public repository truth

- Synchronize the public fork with the exact release candidate before linking
  users to it. At the audit snapshot, public `origin/main` was hundreds of
  commits behind local `main`.
- Tag the exact release source and keep the source available as required by the
  chosen license.
- Do not rewrite history merely to manufacture contributor percentages; the
  explicit lineage record is the durable correction for the disconnected
  local root.

### 3. AnkiWeb identity

- Create a new listing rather than reusing `1808450369`.
- Use a distinct expanded-fork name and author/maintainer wording.
- Remove the current hard-coded review link to
  `https://ankiweb.net/shared/review/1808450369`; after the new listing exists,
  point it to the new item or omit it from the first package.
- Declare the original package as a conflict where Anki packaging supports it,
  so both live add-ons cannot register duplicate hooks, menus, and state paths.

### 4. Asset and content provenance

- Complete the packaging/license audit already required by the Roadmap.
- Resolve every shipped asset still carrying
  `private-fork asset; provenance not audited`.
- Treat the tracked PNGs, RuneScape-derived art/content, trademarks, and source
  datasets as a separate release-rights problem. Wilson attribution does not
  settle Jagex or third-party rights.
- Exclude or replace material whose redistribution basis cannot be defended.

### 5. Release engineering

- Freeze a clean release candidate.
- Run migration fixtures, complete pure and offscreen Qt suites, documentation
  and asset audits, performance/accessibility checks, export/recovery checks,
  and real-profile manual Anki QA.
- Build a package that excludes development-only files and contains all
  required license, credit, source, and conflict metadata.
- Install the exact package into a clean profile and verify that the displayed
  name, version, links, upgrade path, and review link all refer to the new
  derivative listing.

### 6. Publication and post-upload verification

- Upload the new listing only after the preceding gates pass.
- Verify the public AnkiWeb page, downloadable package, source link, license,
  attribution, compatibility range, conflict behavior, and clean-profile
  install.
- Preserve the final checklist, Wilson correspondence, exact Git tag, package
  hash, and release description in the release records.

## Release blockers at decision time

- Wilson acknowledgement or explicit license clarification is not recorded.
- The repository has no explicit license or durable original-creator credit.
- The public fork does not yet represent the complete local product.
- The in-product review link still points to Wilson's AnkiWeb item.
- Asset redistribution provenance is explicitly incomplete.
- The ordinary packaging, migration, real-profile, performance,
  accessibility, export/recovery, and documentation release gates remain open.

Until these are closed, the settled decision is **prepare a public derivative
release**, not **upload now**.
