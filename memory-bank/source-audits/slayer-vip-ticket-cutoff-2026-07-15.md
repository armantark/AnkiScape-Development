# Slayer VIP ticket cutoff audit — 2026-07-15

Status: **closed exclusion**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

Slayer VIP tickets did not exist at the AnkiScape cutoff. They were released on
`2014-04-14` with Cabbage Facepunch Bonanza and are therefore excluded from the
live Slayer design rather than represented as a reward, consumable, assignment
choice, or convenience abstraction.

## Evidence

1. The RuneScape Wiki's current Slayer VIP ticket record gives release date
   `14 April 2014` and identifies Cabbage Facepunch Bonanza as its original
   reward source:
   <https://runescape.fandom.com/wiki/Slayer_VIP_ticket>.
2. The Cabbage Facepunch Bonanza reward-shop record gives the same
   `14 April 2014` release and lists the ticket's two-assignment-choice effect:
   <https://runescape.wiki/w/Rewards_(Cabbage_Facepunch_Bonanza)>.
3. The earliest file-history row for the ticket-choice interface is
   `2014-04-14T19:52:00Z`, consistent with that release:
   <https://runescape.wiki/w/File:VIP_ticket_interface.png?oldid=36970185>.
4. Exact-name queries for `Slayer VIP ticket` returned no item definition from
   any of the six local period caches:

   - rev 727 — 2012-07-24;
   - rev 728 — 2012-08-01;
   - rev 729 — 2012-08-11;
   - rev 736 — 2012-10-09;
   - rev 741 — 2012-11-04; and
   - rev 742 — 2012-11-07.

5. Modern Darkan does contain item ID `31187` as `Slayer VIP ticket` in
   `darkan-world-server/developer-information/item_names.json:26172`. This is a
   useful later-content identity lead, not period evidence; the dated release
   and period-cache absence disqualify it from the frozen game.

## Design consequence

Assignment choice comes from period Slayer rules and owner-approved UI only.
AnkiScape must not recreate the post-cutoff ticket's choose-one-of-two mechanic
under another name or as an invented convenience setting.
