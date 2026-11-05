# 03: Shop search, purchase quantity and Sawmill names

**What to build:** The Shop and Sawmill decisions in the spec.

**Blocked by:** None (can start immediately)

**Status:** built; native Shop and Utilities look waits for the orchestrator

- [x] Real widget flow: a new query returns both result lists to the top; a purchase keeps the position.
- [x] A new shop row resets quantity to 1, by tile and by search result; a refresh keeps a typed quantity.
- [x] "sawmill" and "plank" each find all four rows; a review still makes one plank at the same fee. Check saves, the queue and tests that store the old display names.
