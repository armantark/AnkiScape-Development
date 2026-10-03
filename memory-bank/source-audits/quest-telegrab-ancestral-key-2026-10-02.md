# Spirits of the Elid: ancestral-key Telegrab

The qualified evidence is section 3 of `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/quest-action-sources-2026-10-02.md`.

- [Spirits of the Elid, oldid 6326193](https://runescape.wiki/w/Spirits_of_the_Elid?oldid=6326193), `2012-09-30T18:25:54Z`: use Telekinetic Grab to acquire the ancestral key from the enclosed east side of Nardah's shrine. The route visits Awusah and Ghaslor for the ballad first. Searching cupboards and repairing robes are separate actions.
- [Telekinetic Grab, oldid 6587753](https://runescape.wiki/w/Telekinetic_Grab?oldid=6587753), `2012-11-19T14:24:13Z`: level 33, Normal spellbook, one Law rune and one Air rune per successful cast; expressly names this quest's ancestral key. The qualified cache extract binds `/items/ancestral_key` to `6792`.

The distinct `telegrab_ancestral_key` target reuses the existing non-combat Telegrab spell specification and its provenanced period icon. Its output is one Ancestral key. It does not consume Thread, robes or a needle. No quest-completion gate is added to an action required during that quest; no original numeric server-stage threshold is claimed. The exact existing stage-2 proof, `Cast Telegrab for the water channel puzzle`, is retained despite its misleading name: the cast acquires the key, while water channels use separate interactions.

`handle_magic_answer` calls the existing Magic reducer and successful shared recorder. Only this successful target event emits the proof. The ordinary wine target, possession of a key and refused casts do not emit it. Review Undo restores the inventory, XP and proof snapshot. The reachability adapter binds the same event to `Magic:telegrab_ancestral_key`.

Icon verification (2026-10-02): the wiki imageinfo lookup before `2012-11-19T23:59:59Z` returned the [Telekinetic Grab icon revision](https://runescape.wiki/images/archive/20130111000632%21Telekinetic_Grab_icon.png?fe052) dated `2011-11-29T14:12:02Z`, source SHA-1 `239bc51b9fba8be8f38c6e4f5460531186482294`, 225 bytes. Downloaded bytes match that SHA-1; decoded RGBA pixels match the new 359-byte icon exactly. Requests used `User-Agent: AnkiScape parity audit`. Raw revision, source PNG and pixel verification are in the slice evidence folder.
