# Native acceptance verification

Overall: FAIL. The corrected Skippy title, menu opening, quest filters, and Crayfish guide price pass. Alfred's journal stages were not visible, and the known navigation truncation remains.

Date: 2026-09-17 (America/Los_Angeles).
Repository mirror: /Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork
Isolated session: /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk
Artifact directory: /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts

## Isolation and steps performed

1. Read the prepared session receipt and guard source. No direct owner-collection access was performed; the explicitly requested verify command performed its own integrity measurement.
2. Ran exactly the supplied session_guard.py launch command through the terminal tool. Anki was not running beforehand. After launch, the inventory showed Anki running. Attached with its bundle ID, net.ankiweb.anki, to that running instance. Never selected /Applications/Anki.app, constructed an Anki launch command, or used another launch route.
3. Accepted English (United States) in the isolated first-run profile and declined the optional Anki update. No account sign-in or Sync.
4. Opened AnkiScape > Menu. Inspected Skills and Quests at the default window size. Scrolled the quest list to Miniquests.
5. Searched Skippy, then Alfred; expanded Alfred's card. Selected Special difficulty and Medium length; changed difficulty to Novice, then restored Special.
6. Started Alfred in the disposable profile. Inspected the immediate card state, visited Stats, and returned to Quests once to test the recorded refresh behavior. Did not investigate or fix the defect.
7. Opened Grand Exchange. Chose No in the Ironman prompt so this disposable profile could use the regular exchange. Searched Crayfish and selected its row. Did not click Place buy offer or submit any offer.
8. Closed AnkiScape, opened Anki's own application menu, and selected Quit Anki. The guard launch process exited 0. A subsequent app inventory confirmed isRunning: false.
9. Ran exactly the supplied verify command. Exit status: 0. Saved its full output below and in verify-output.txt.

## Numbered acceptance results

| Item | Result | Native UI observation |
|---|---|---|
| 1 | PASS | AnkiScape > Menu opened without an error dialog. |
| 2 | PASS | Miniquests listed both Alfred Grimhand's Barcrawl and Skippy and the Mogres together. Searching Skippy returned Skippy and the Mogres, with Showing 1/198. The obsolete standalone title Mogre was not used for this card. |
| 3 | FAIL | Alfred's complete title, enabled Start quest action, description, and unlock text were readable without truncation or ellipsis. However, no journal stages appeared in the expanded body. Starting changed the header to Stage 0/3 and the button to Currently active, while the body retained the old description. Returning from Stats did not make the journal stages appear. |
| 4 | PASS | Search Alfred plus Special difficulty and Medium length showed Alfred (Showing 1/198). Novice difficulty with Medium hid the card and displayed Showing 0/198 and No quests match the current filters. |
| 5 | PASS | Crayfish appeared in exchangeable items and was selectable. Its detail panel showed Guide: 45 Coins and a buy limit of 10,000 per 40 cards. All offer slots remained empty. No offer was submitted. These values are the captured UI values for this run. |
| 6 | FAIL | The six known navigation labels were ellipsised and Settings had no visible text. No other static text truncation, clipped control, or overlapping element was seen in the inspected AnkiScape surfaces. Scroll-viewport clipping and intentional ellipses are listed separately below. |

## Known defects

- Alfred stale expanded body: REPRODUCES. After Start quest, the header reads Stage 0/3 and the button Currently active, but the body still reads: "Talk to a Barbarian guard at the Barbarian Outpost. Short if the Grand Tree quest is completed and the Lodestone Network is unlocked." The unlock line also stays. DIFFERENCE FROM RECORDED WORKAROUND: leaving for Stats and returning to Quests did not refresh the body in this run. No further investigation was performed.
- Navigation truncation: REPRODUCES. Equipment appears as Equi..., Grand Exchange as Gra..., Challenges as Cha..., Quests as Que..., Achievements as Ach..., Collections as Coll..., and Settings as a wrench only. This remains visible throughout the inspected AnkiScape tabs.

## Other visible clipping and ellipses

- The unfiltered Quests scroll viewport shows partial rows at its top or bottom depending on scroll position. Examples captured: Pirate's Treasure at the lower edge of the initial list and upper edge after scrolling; Temple of Ikov at the lower edge of the intermediate list; The Elder Kiln at the upper edge of the bottom-list screenshot. These are scroll-boundary crops, not shortened card text. Alfred and Skippy are fully visible at the bottom-list position.
- The first-run language selector shows a partial next language row at its lower scroll boundary. This is outside AnkiScape.
- The empty exchange search placeholder visibly ends in an intentional ellipsis: Search exchangeable items.... This is placeholder punctuation; the phrase fits within its field.
- Native application-menu command labels contain conventional dialog ellipses: Preferences..., About Anki..., and Services Settings…. These are not width truncation.
- No overlap or additional clipped controls were observed. This is limited to the surfaces visited for these acceptance steps; every tab and every catalog row was not exhaustively inspected.

## Verification command

```text
/Applications/Xcode.app/Contents/Developer/usr/bin/python3 /Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork/tools/native/session_guard.py verify /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk
```

Full output (stdout; no stderr returned):

```json
{"path": "/private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk", "collection": "/Users/armantarkhanian/Library/Application Support/Anki2/User 1/collection.anki2", "unchanged": true, "changes": {}}
```

Exit status: 0.
The guard reports unchanged: true and changes: {} for the owner's collection. No source edits, repository changes, commits, or pushes were made. Only the disposable session's normal app state and these artifacts were written.

## Screenshot inventory

- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/01-language.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/02-ankiscape-open.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/03-quests.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/04-miniquests-list.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/05-miniquests-bottom.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/06-skippy-search.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/07-alfred-journal-before-start.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/08-difficulty-options.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/09-alfred-special.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/10-alfred-special-medium.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/11-alfred-novice-hidden.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/12-alfred-start-stale-body.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/13-stats-transition.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/14-alfred-journal-after-return.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/15-grand-exchange.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/16-grand-exchange-regular.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/17-crayfish-search.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/18-crayfish-guide-price.png
- /private/var/folders/g8/swv_4sld1_zg_r_w52b6xg7c0000gn/T/ankiscape-native-6vhhxrsk/artifacts/19-anki-before-quit.png

## Tool friction

An initial Quests click used an invalid accessibility ID after a full tree refresh: "Computer Use server error -10005: 124 is an invalid element ID". The click failed without changing the UI. Continued with screenshot-grounded coordinates. The unfiltered quest list initially omitted its content from the accessibility tree, so screenshots were used. The first scroll stopped partway through the list; the visible scrollbar was then dragged to the bottom. No source changes or defect investigation followed.
