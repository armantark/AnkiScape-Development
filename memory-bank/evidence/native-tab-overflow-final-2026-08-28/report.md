# Native tab-overflow and Cooking verification

Final verdict: **PARTIAL PASS**

- The tab-overflow slice passes all four native cases.
- Cooking remains blocked. This report does not claim a native Cooking pass.
- The normal Anki base remained unchanged.
- No process from this run remains.

## Evidence provenance and privacy

The native run produced the original report and manifest in a private remote artifact.

- `source_report.md` is the byte-for-byte final remote report. Its SHA-256 is `f7af19f50febf1081b91a06b539394a3b1ba0b81304bbcfe81cbc13d07a73313`.
- `source_manifest.txt` is the byte-for-byte final remote manifest. Its SHA-256 is `5b28910056a253b488cf5642abe08e78780fc15262b93270e45b385b63865d74`.
- The source manifest verifies 4,729 remote artifact files.
- The repository does not retain the four full-dialog screenshots.
- The repository does not retain the raw macOS `.ips` crash packet.
- The retained tab-strip images are lossless product-only crops. They exclude unrelated desktop windows.
- `manifest.txt` verifies every retained file except itself.

## Loaded product proof

The isolated Anki process loaded these product files:

- `ui/ui.py` SHA-256: `d55b987a308a82e13f8a9c9b1aa3fefa9472e60403609edf0c96fa1699185d8c`
- `__init__.py` SHA-256: `842df7cffa5b1ed49380ad24c8e757eaf0ce70e6d747e3e615f06135ed2e8137`

The disposable helper and all writable Anki paths stayed below `/private/tmp/ankiscape-native-tab-final.utu7VD`.

## Shared tab policy

Each case contained these 11 labels in this exact order:

```text
Skills | Stats | Bank | Equipment | Shop | Grand Exchange | Challenges | Quests | Achievements | Collections | Settings
```

Each case recorded these values:

- `QTabWidget.documentMode=true`
- `QTabBar.documentMode=true`
- `drawBase=true`
- `expanding=false`
- `usesScrollButtons=true`
- `elideMode=ElideNone`
- icon size `16x16`
- stylesheet `QTabBar::tab { min-width: 0px; padding-left: 1px; padding-right: 1px; }`
- no visible body horizontal scrollbar

All tab rectangles used at least their Python-owned size hint. The rectangles were contiguous and did not overlap.

## Case 1: normal font, wide dialog — PASS

- Application font: `.AppleSystemUIFont`, 13.0 pt.
- Observed dialog size: `1140x767`.
- Tab-bar width: `1108` pixels.
- Natural tab width: `905` pixels.
- Headroom: `203` pixels.
- Both scroll controls were hidden and disabled.
- Native pointer input selected `Bank` at index 2.
- The dialog stayed open.
- All labels were complete. No label had an ellipsis, clip, or overlap.

Retained evidence:

- `tab-case1-normal-wide-after-bank-retry.json`
- `case1_normal_wide_tabstrip.png`

## Case 2: 125% font, wide dialog — PASS

- Application font: `.AppleSystemUIFont`, 16.25 pt.
- Observed dialog size: `1145x769`.
- Tab-bar width: `1113` pixels.
- Natural tab width: `1070` pixels.
- Headroom: `43` pixels.
- Both scroll controls were hidden and disabled.
- Native pointer input selected `Bank` at index 2.
- The dialog stayed open.
- All labels were complete. No label had an ellipsis, clip, or overlap.

Retained evidence:

- `tab-case2-125-wide-after-bank.json`
- `tab-case2-125-wide-final.json`
- `case2_125_wide_tabstrip.png`

## Case 3: normal font, narrow dialog — PASS

- Application font: `.AppleSystemUIFont`, 13.0 pt.
- Observed dialog size: `720x768`.
- Tab-bar width: `688` pixels.
- Natural tab width: `972` pixels.
- Headroom: `-284` pixels, so scroll controls were required.
- Both controls were visible and distinct.
- Native right-control input exposed the complete `Settings` tab.
- Native pointer input selected `Settings` at index 10.
- One native left-control action moved the strip back by 31 pixels.
- The right control became enabled again after the left action.
- The dialog stayed open.
- Visible labels had no ellipsis or overlap.

Retained evidence:

- `tab-case3-normal-narrow-final.json`
- `tab-case3-normal-narrow-after-settings.json`
- `tab-case3-normal-narrow-after-left-once.json`
- `case3_normal_narrow_pre_scroll_tabstrip.png`
- `case3_normal_narrow_tabstrip.png`

## Case 4: 125% font, narrow dialog — PASS

- Application font: `.AppleSystemUIFont`, 16.25 pt.
- Observed dialog size: `720x768`.
- Tab-bar width: `688` pixels.
- Natural tab width: `1070` pixels.
- Headroom: `-382` pixels, so scroll controls were required.
- Both controls were visible and distinct.
- Native right-control input exposed the complete `Settings` tab.
- Native pointer input selected `Settings` at index 10.
- One native left-control action moved the strip back by 32 pixels.
- The right control became enabled again after the left action.
- The dialog stayed open.
- Visible labels had no ellipsis or overlap.

Retained evidence:

- `tab-case4-125-narrow-final.json`
- `tab-case4-125-narrow-after-settings.json`
- `tab-case4-125-narrow-after-left-once.json`
- `case4_125_narrow_pre_scroll_tabstrip.png`
- `case4_125_narrow_tabstrip.png`

## Visual limits

The narrow screenshots show the correct scroll viewport behavior. Tabs outside the viewport appear after the user scrolls.

The cursor covers part of one label in some crops. Geometry data and the other screenshots prove the full label width.

The final JSON names for cases 3 and 4 describe initial post-resize states. Their timestamps place them before the scroll sequence.

## Cooking — BLOCKED

The disposable save had Cooking level 94 and the required Cooking state. Native input opened the Skills tab and the Artisan group.

Pointer activation of the visible Cooking row returned:

```text
Accessibility error: AXError.notImplemented
```

Keyboard input then moved the selected Artisan skill from Smithing to Crafting. The next `Down` action caused this Computer Use error:

```text
Computer Use server error -10005: App quit
```

The crash occurred at `2026-08-28 18:57:01 -0700` in Anki 26.5, PID `48896`.

Crash facts:

- Exception: `EXC_BAD_ACCESS`
- Signal: `SIGSEGV`
- Subtype: `KERN_INVALID_ADDRESS`
- Faulting thread: `CrBrowserMain`
- Top frame: `QAccessibleCache::deleteInterface(unsigned int, QObject*)`
- Later frames: `QAccessible::updateAccessibility(QAccessibleEvent*)`, `QAbstractItemView::event(QEvent*)`, `sipQTreeWidget::event(QEvent*)`, and `QDialog::exec()`

The least-specific supported class is a native Qt accessibility-bridge crash during a posted accessibility update for the Skills `QTreeWidget`.

The evidence does not prove an AnkiScape product defect. No AnkiScape Python frame appears in the faulting stack.

The evidence also does not prove a Qt-only defect. No control run exists without an accessibility client.

The process exited before the Cooking target page opened. These checks remain incomplete:

- the visible Casual value
- the native change to Advanced
- close and reopen persistence
- the persisted Cooking state

Retained evidence:

- `cooking_blocked_reason.txt`
- `cooking_blocked_crash_summary.txt`
- `cooking_skill_after_first_down.tree.txt`
- `action_log.jsonl`

## Cleanup

`cleanup_proof.txt` records these final facts:

- product PID `48896` exited
- no product child remained
- no `Anki`, `mpv`, or `QtWebEngineProcess` remained
- normal-base metadata remained unchanged
- no graphical application query occurred after product exit
