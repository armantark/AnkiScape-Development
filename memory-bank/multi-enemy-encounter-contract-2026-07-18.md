# Multi-enemy encounter contract

Date: `2026-07-18`

Status: **owner-settled general pattern; per-encounter values remain owned by
each activity's source audit.**

## The pattern: engaged target + pressure roster

Owner decision 2026-07-18 (made on the Fight Caves fork and generalized to all
multi-enemy encounters): a multi-enemy encounter spawns as a **visible
roster**. The player fights exactly one **engaged target** through the live
kernel's six-tick Combat slices; every unengaged roster member deals bounded
incoming pressure each review through the ordinary defense/protection-prayer
contract, so the styles remaining on the field keep mattering. A kill advances
engagement to the next target; the encounter resolves when the roster is
empty.

- Casual auto-picks the engaged target by source-shaped kill priority (for
  Fight Caves: prayer drainers first). Advanced picks freely from the roster.
- Homogeneous swarms may present the roster as one collapsed aggregate front —
  target choice among identical enemies is no decision. Troll Invasion's
  settled aggregate wave front and Pest Control's portal front (engaged
  target = portal, pests = pressure) remain valid instances of this contract,
  not exceptions to it.
- This unparks the general multi-enemy design: Bork's Ork-legion encounter,
  Barbarian Assault waves, and statless quest multi-encounters adopt this
  pattern as their runtime shape.

## First full consumer: Fight Caves

Darkan pins the complete structure
(`darkan-world-server`,
`src/main/java/com/rs/game/content/minigames/fightcaves/FightCavesController.java`):
the 63-wave roster table mixing up to six monsters of different attack styles
(Tz-Kih, Tz-Kek, Tok-Xil, Yt-MejKot, Ket-Zek) ending at TzTok-Jad, and
TokKul paid as `wave × 8032 / 63` on leaving. The packet's settled session
shape stands: live Combat slices inside persistent waves, explicit Leave, no
timeout, safe death, resumable across reviews.

Harvest work: corroborate the wave table, monster stats, healer/drain
mechanics, Jad's style-telegraph (its translation to the pressure model needs
its own design care), TokKul payouts, and the fire cape award against the
period record.
