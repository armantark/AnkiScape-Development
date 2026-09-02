# Reading the OpenRS2 cache archives without damaging them — 2026-09-02

Found while harvesting Bar Crawl. This is a live-state hazard, so it belongs in
the memory bank rather than in a harvest record.

## The hazard

`com.rs.cache.Store` in the prebuilt Darkan reader
(`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/build/libs/world-server-2.0.11-all.jar`,
SHA-256 `2acc58e4eb35212146c2bac1a99208163b626dee0984e20df0d8f247c78ea861`)
opens `main_file_cache.dat2` and every index with
`RandomAccessFile(..., "rw")`. So the obvious way to read a definition out of
the owner's cache archives opens them for writing. Verified with:

```sh
JAR='/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/build/libs/world-server-2.0.11-all.jar'
javap -classpath "$JAR" -c -p com.rs.cache.Cache com.rs.cache.Store
```

The bundled dumpers are worse: they delete and recreate their output files
through `FileWriter`.

```
darkan-world-server/src/main/java/com/rs/tools/ItemListDumper.java:45-67
darkan-world-server/src/main/java/com/rs/tools/NPCListDumper.java:29-53
darkan-world-server/src/main/java/com/rs/tools/ObjectListDumper.java:30-55
```

That project's Gradle tasks also default to a different, mutable cache path
(`darkan-world-server/build.gradle.kts:186-193`). Never repoint them at the
archive set for a read-only lookup.

## The safe route

An in-memory Python decoder using only standard-library `gzip` and `bz2`, with
every cache file opened `"rb"`, validating JS5 sector headers before it
decompresses a container. Indexes: objects `16`, NPCs `18`, items `19`. The
file shift is 8 bits for objects and items and 7 bits for NPCs, so an item id
is `archive * 256 + file`. A production reader must take valid file ids from
the index reference table instead of assuming every final container is full.

Six candidate tools are not installed here: `openrs2`, `cachetool`,
`cache-tool`, `rs2cache`, `rs-cache`, `cache-util`.

## What it found, as an example of the route working

Positive controls first, in revision 742: item 1205 `Bronze dagger` (`Wield`),
object 5276 `Bank booth` (`Bank`, `Collect`), NPC 731 `Bartender` (`Talk-to`),
NPC 849 `Barman` (`Talk-to`, `Trade`). Only then was absence interpreted.

`Barcrawl card` is item `455`, option `Read`, present in revisions 727, 728,
729, 736, 741 and 742. In revision 652 the same id carries the German
localization `Tavernenmarathonkarte` (`Lesen`). The addressing in 742 is item
index 19, archive 1, file 199, and `1 * 256 + 199 = 455`.

No `barcrawl` or `bar crawl` literal appears in the object or NPC definitions of
any scanned revision. That is a lexical result only: dialogue and quest logic
can live in client scripts outside definition records, so it is not evidence
that no Bar Crawl NPC or object exists.

## Cache set on this machine

Under `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/`:
`652-2011-06-08`, `727-2012-07-24`, `728-2012-08-01`, `729-2012-08-11`,
`736-2012-10-09`, `741-2012-11-04`, `742-2012-11-07`. There is no manifest or
supplied checksum record, so the date in each directory name is the usable
source-date metadata; filesystem mtimes are extraction dates and mean nothing.

Written under `memory-bank/pending/` because a landing window was open
(ruling 38.2). It folds into the memory bank after the window.
