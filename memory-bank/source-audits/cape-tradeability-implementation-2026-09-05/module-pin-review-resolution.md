# Module pin review and authorization

The retained raw Opus evidence review accepted all five proposed digest replacements. The parent driver then explicitly authorized only those five literals in `tests/test_module_surface.py`: constants, shop logic, carried actions, activity actions, and the root Qt digest. The frozen proposal remains unchanged as the reviewed input. No other pins, tools, thresholds, product fields, or test behavior may change under this authorization.

At edit time, the author verified the complete prior pin-file SHA-256 against the tested source binding, checked that each old literal appeared exactly once, and verified the complete file against the source baseline. Reversal of the five applied literals restored every baseline byte. `module-pin-application.json` records both file hashes and the exact replacements. The module-surface tool and all authored product/regression files remain unchanged.

The review is a bounded packet review. The driver’s complete-body footer validation and reversal supply the underlying comparison evidence. Matching hashes alone do not establish that a capture is complete. The raw bodies remain in the named immutable MacBook report directories; the local packet binds the complete compact proof.

The reviewer’s observation about `required_level: 1` is outside this pin change. It is existing equipment metadata protected by the identity regression and owner proof; it was not changed. The review does not authorize a product adjustment.

The parent authorized a new atomic implementation commit with normal hooks. Full-branch execution of the new pins and native acceptance remain pending with the driver. The author ran static checks only and did not execute runtime tests or access the MacBook.
