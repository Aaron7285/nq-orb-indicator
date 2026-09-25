# Testing Guide

Claude can't run TradingView from its cloud session. Claude writes the code, the
automatic checks and the self-tests. **You run the TradingView steps** and report back
(a screenshot or the error text is enough).

---

## 1. Test levels

| Level | Test | Pass when | Who |
|---|---|---|---|
| L0 | Automatic checks | `build.py` and `lint.py` succeed; the GitHub check shows ✓ | Automatic |
| L1 | Compile | The module's test indicator **and** the full build (`dist/NQ_ORB.pine`) add to the chart with no errors | You |
| L2 | Self-tests | The test indicator's PASS/FAIL table shows every row as **PASS** | You |
| L3 | Real-chart checks | On the listed dates, Data Window values match a manual reading of the chart | You |
| L4 | Repaint checks | Bar Replay and the reload test show identical results (§4) | You |
| L5 | Edge cases | Every applicable item in §5 behaves as its rulebook says | You |
| L6 | Visual and clutter | Screenshots on 1m and 5m in each display preset stay within the clutter budget | You + Claude |
| L7 | Performance | No "script took too long" error on a 1m chart with maximum history | You |
| L8 | Regression | After integration, every earlier module's self-tests still pass | You |

## 2. Workflow per component

1. **Define:** the rulebook is approved (all its `DECISIONS.md` items are DECIDED).
2. **Implement:** the module plus its test indicator in `dist/test/`.
3. **Test:** L0 → L8, in order. A failure stops the phase until it's fixed.
4. **Review:** Claude checks the code against every rulebook line, you check the visuals,
   and findings are logged in §7.
5. **Integrate:** the module is added to `dist/NQ_ORB.pine`, then L1, L7 and L8 are re-run.

## 3. Self-test catalogue

A self-test feeds a scripted sequence of candles (or, for the lifecycle engine, events)
into the module and compares the result with the expected answer written in the rulebook.
The IDs below are the minimum set. Each module's rulebook adds its own cases.

### 3.1 Core (Phase 1; rulebook `rules/core.md`)
Test indicator: `dist/test/core_test.pine`. Scripted candles use tick 0.25.

**Level interaction (LI):** for a high-type level at 100.00 (low-type is mirrored in LI-10)

| ID | Scripted candle(s) | Expected |
|---|---|---|
| LI-01 | High 99.50, close 99.00 | **TOUCH** (within 2 ticks); the level stays active |
| LI-02 | High 100.50, low 99.00, close 99.50 (≤ midpoint 99.75) | **SWEEP**; the level becomes SWEPT |
| LI-03 | High 100.25 (1 tick through), close 99.50 | **TOUCH** (C3) |
| LI-04 | High 100.50, low 98.50, close 99.75 (above midpoint 99.50) | **TOUCH**, not a sweep (C3) |
| LI-05 | Close 100.25 | **BREAK**; the level becomes BROKEN |
| LI-06 | LI-02, then another sweep candle | **No** second event |
| LI-07 | High 100.50, low 99.00, close exactly 99.75 (the midpoint) | **SWEEP** (R7) |
| LI-08 | High 100.50, low 99.50, close exactly 100.00 (at the level, and also the midpoint) | Not a break (C2); close ≤ midpoint (R7) → **SWEEP** |
| LI-09 | A candle that would sweep, on the same candle the level became known | **Nothing** (C5); judged from the next candle |
| LI-10 | Low-type level at 100.00: low 99.50, high 101.00, close 100.50 (≥ midpoint 100.25) | **SWEEP**, bullish (mirror) |
| LI-11 | Two levels at 100.00 and 100.25; high 100.75, low 99.00, close 99.50 | **Both SWEPT** on one candle (C7) |
| LI-12 | High 103.00, close 100.25 | **BREAK**, not a sweep (C4) |
| LI-13 | High 99.25 (3 ticks below the level), close 99.00 | **none** |

**Time (TM)**

| ID | Scripted case | Expected |
|---|---|---|
| TM-01 | A candle opening Mon 16:55 / another opening Mon 17:00 | Trading day Mon / Tue (C1) |
| TM-02 | 5m candles 08:25, 08:30, 10:55, 11:00 (open times) | In NY AM: no, yes, yes, no (R1) |
| TM-03 | 1m candles, 30 min from the 09:02 close | Ends on the candle closing at 09:32 (D2.4) |
| TM-04 | 5m candles, 30 min from the 09:05 close | Ends on the candle closing at 09:35 |
| TM-05 | 08:00 Chicago on the Monday after the March and after the November clock change | Both correct |
| TM-06 | Timeframe 1m, 5m / 3m, 15m, 60m | Supported / notice shown |
| TM-07 | Same trading day / the first candle of a new trading day | Event store kept / cleared (the morning setup count is reset by the lifecycle module, Phase 9) |

**Price (PX)**

| ID | Scripted case | Expected |
|---|---|---|
| PX-01 | 50 % of an FVG 100.00–101.00 | 100.50 |
| PX-02 | 50 % of FVG 100.00–100.75 → 100.375: long / short | 100.50 / 100.25 (C9) |
| PX-03 | 20 points ↔ ticks | 80 ticks |
| PX-04 | Core ATR(14) vs TradingView `ta.atr(14)` on the real chart, last 500 candles | Equal to within 1e-9 (C6) |

**Events (EV)**

| ID | Scripted case | Expected |
|---|---|---|
| EV-01 | The same sweep judged twice (a re-run of the same candle) | The same event ID |
| EV-02 | Two sweeps of different levels on one candle | Two different IDs |
| EV-03 | Mark an event used | It stays used; it's never offered as eligible again |
| EV-04 | More than 300 events in a day | The oldest are dropped; no error |

**Drawing budget (DB) and theme (TH)**

| ID | Scripted case | Expected |
|---|---|---|
| DB-01 | A module with budget 20 lines creates 25 | 20 exist; the 5 oldest were deleted |
| DB-02 | All modules at full budget | Totals stay ≤ 500 per object type |
| TH-01 | Background #131722 / #FFFFFF | Dark / light tokens |

### 3.2 Opening range (OR)
Values: 08:00–08:15 Chicago, breakouts until 11:00.
- OR-01: high/low/midpoint match the scripted 08:00–08:15 candles exactly on 1m and 5m; locked at 08:15.
- OR-02: no breakout, false-breakout or ORB-sweep event before 08:15.
- OR-03: the first close above the ORB high → one breakout event; later closes above → none.
- OR-04: a breakout, then a close back inside within 15 minutes → one false-breakout event; after 16+ minutes → none.
- OR-05: a wick through the ORB high that closes inside, with no breakout → one ORB-sweep event.
- OR-06: the ORB starts at 08:00 Chicago in both summer and winter time.

### 3.3 Structure (MS)
Values: swing 10, internal 3, close-confirmed, CHoCH breaks the most recent opposite swing.
- MS-01: an internal swing is confirmed exactly 3 candles after it forms (a swing-layer one after 10), never earlier.
- MS-02: a close beyond an internal swing high in an internal uptrend → internal **BOS**; against the trend → internal **CHoCH**, and the trend flips.
- MS-03: a wick beyond without a close → no break.
- MS-04: each swing level is broken at most once.
- MS-05: the first break with no trend yet → labelled BOS, never CHoCH.

### 3.4 FVG (FV), Liquidity (LQ), Supply & Demand (SD), Sessions (SE)
These are completed in each module's rulebook at the start of its phase: one PASS/FAIL row
per rule. Required minimum cases:
- FV: minimum size max(2 pts, 0.25 × ATR); filled only through the far edge; the trigger candle's own gap is confirmed one candle later.
- LQ: EQH/EQL from swing-layer points within max(4 ticks, 0.1 × ATR); Asia/London/previous-day levels replaced daily; EQH/EQL and swing targets kept until swept or broken.
- SD: a zone requires a body ≥ 1.5 × ATR **and** an internal structure break; invalidated by a close beyond its far edge; retired after 2 tests.
- SE: every session boundary is correct in Chicago time in both summer and winter.

**Sessions (SE)**, in `dist/test/sessions_test.pine` (rulebook `rules/sessions.md`)

| ID | Scripted case | Expected |
|---|---|---|
| SE-01 | Asia 5m candles 19:00–23:00 (high 105 at 20:00, low 96 at 21:30) | 105 / 96 / open 99.5 / known at 23:00 |
| SE-02 | Extreme candles at 18:55 and 23:00 | Excluded (R1) |
| SE-03 | The candle closing at 23:00 | Completes the session |
| SE-04 | Trading day of the Mon 19:00 Asia session | Tuesday's date (C1) |
| SE-05 | The same Asia session on 1m | Same range, known at 23:00 |
| SE-06 | The next day's Asia (high 110) | Replaces the most recent (D15.4) |
| SE-07 | London 1m 01:00–04:00 | 104 / 97 / known at 04:00 |
| SE-08 | London candles stop at 03:35; the next candle is at 05:00 | Completes on the 05:00 candle, known at 03:35 |
| SE-09 | First seen at 20:30 / from 19:00 | Partial yes / no (S2) |
| SE-10 | NY AM 08:25/08:30/10:55/11:00 | no, yes, yes, no (tradeable filter) |
| SE-11 | 09:00 and 12:30 candles | In NY and NY AM; in NY and NY PM |
| SE-12 | 19:00 Chicago in January | In Asia; 01:00 UTC (winter) |
| SE-13 | HHMM settings 1900 / 130 / 2300 | 1140 / 90 / 1380 minutes |

### 3.5 Confluence (CT)
| ID | Scripted scenario | Expected |
|---|---|---|
| CT-01 | ORB breakout + NY AM + bullish bias, with no internal BOS | **No setup** (context never creates setups) |
| CT-02 | An internal CHoCH, then a sweep | **No setup** (wrong order) |
| CT-03 | A sweep, then an internal CHoCH **55 min** later | **No setup** (> 50 min) |
| CT-04 | A sweep, then an internal **BOS** (not a CHoCH) in the setup direction | **No T1** (D6.7) |
| CT-05 | An ORB breakout, then an internal **CHoCH** in the breakout direction | **No T2** (D6.8) |
| CT-06 | A T2 sequence with an ORB false breakout in between | **No setup** |
| CT-07 | A valid T1 sequence with a qualifying FVG and a zone ✓ | Exactly **one** QUALIFIED setup, correct events attached |
| CT-08 | A valid T1 sequence whose only extra ✓ is the FVG (no zone, no other level, bias not agreeing) | **REJECTED** "optional 0/1" (the FVG is used up by the location requirement) |
| CT-09 | A valid sequence against the bias with a zone ✓ | QUALIFIED and flagged **counter-bias** |
| CT-10 | An ORB sweep, then an internal CHoCH | One setup, labelled **T3** |
| CT-11 | Two sweeps (Asia low, then the previous-day low), then a CHoCH | One setup, both sweeps attached, stop beyond the lower wick |
| CT-12 | A valid sequence whose trigger candle closes at 11:05 | **No setup** (outside NY AM) |
| CT-13 | The trigger candle's own gap is the only FVG | The plan is made on the next candle; the limit is at that gap's 50 % |
| CT-14 | Same as CT-13, but the next candle doesn't confirm the gap | **REJECTED** "no FVG" |

### 3.6 Setup lifecycle / anti-spam (LT)
These enforce LC-1 … LC-7 in `rules/setup_lifecycle.md`.

| ID | Scripted scenario | Expected |
|---|---|---|
| LT-01 | A valid setup qualifies; its conditions stay true for 20 more candles | Exactly **1** setup |
| LT-02 | A setup is stopped; the same sweep and CHoCH are still within 50 min | **No** new setup (events used) |
| LT-03 | A long is active; price falls through the stop | **STOPPED**; **no short** on that candle or during the 30-min cooldown |
| LT-04 | After LT-03, the bearish CHoCH from the stop-out candle is the only bearish event | **No short** (event before re-arm) |
| LT-05 | 30 min after LT-03, a **new** sweep and a **new** CHoCH confirm | One new setup (either direction) |
| LT-06 | A valid sequence confirms **during** the cooldown | Ignored, and still ineligible after the cooldown |
| LT-07 | A candidate is rejected (R:R 0.8); on the next candle R:R would be 1.2 | **No setup**, and **no cooldown** starts |
| LT-08 | A Model B setup expires unfilled; the same events are still recent | **No** new setup; a 30-min cooldown runs |
| LT-09 | A long is live (pending or active); a valid short sequence confirms | **No short** |
| LT-10 | 2 setups have **filled** this morning; another valid sequence confirms | **REJECTED** "cap" |
| LT-11 | 1 filled + 1 expired this morning; another valid sequence confirms | Allowed (expired doesn't count toward the cap) |
| LT-12 | A long is stopped; 30+ min later a new long sequence from new events | Allowed |
| LT-13 | Yesterday's last setup was a long; today's first sequence is a short | Allowed, with no cooldown carried over (daily reset) |
| LT-14 | Every state change on the scripted path | Exactly one alert per state change, never repeated |
| LT-15 | The whole scripted path run in Bar Replay | Identical to the historical result |

### 3.7 Entry models, stops and targets (EM)
| ID | Scripted scenario | Expected |
|---|---|---|
| EM-01 | Model B qualifies | Limit at the chosen FVG's 50 %; state PENDING |
| EM-02 | Price reaches L exactly, but not 1 tick through | **Not filled** |
| EM-03 | Price trades 1 tick through L | Filled at **L** |
| EM-04 | No fill within 30 min of placement | **EXPIRED** |
| EM-05 | TP1 (2 ticks before its level) reached before any fill | **MISSED** |
| EM-06 | Pending; a bearish internal CHoCH (against a long) closes before the fill | **Still pending** (no structure-based cancellation) |
| EM-07 | The fill and a close beyond the stop in one candle | Filled, then **STOPPED**, *ambiguous* |
| EM-08 | The fill and TP1 in one candle | **Filled only**; TP1 counts from the next candle |
| EM-09 | Stop and TP1 both reachable in one candle | **STOPPED**, *ambiguous* |
| EM-10 | Stop distance 4.75 pts / 30.25 pts | **REJECTED** "stop too tight" / "stop too wide" |
| EM-11 | R:R to TP1 = 0.95 | **REJECTED** "R:R" |
| EM-12 | No untouched level beyond entry | **REJECTED** "no target" |
| EM-13 | No level beyond TP1 | Setup kept with **TP1 only**; ends as TP1_FINAL |
| EM-14 | TP1 hit, then price returns to entry | Stop at entry from the next candle → **BREAKEVEN** |
| EM-15 | Setup active at the candle ending 11:00 | **CLOSED_WINDOW** at that candle's close |
| EM-16 | Setup pending at the candle ending 11:00 | Cancelled, CLOSED_WINDOW (not filled) |
| EM-17 | T3 after a false breakout | Stop 2 ticks beyond the extreme between the breakout and trigger candles |
| EM-18 | T2 long | Stop 2 ticks below the most recent confirmed internal swing low at the BOS |
| EM-19 | R:R shown for TP1 and TP2 | Matches the hand calculation to 2 decimals |
| EM-20 | Model A (setting) qualifies | Entry = trigger close; the trigger candle's own low is never counted as a stop hit |

### 3.8 Risk (RK)
- RK-01: account $50,000, 1 %, stop 20 pts → $500 risk; NQ risk per contract = $400 → 1 NQ; MNQ = $40 → 12 MNQ.
- RK-02: the NQ quantity rounds down to 0 → only MNQ is shown.
- RK-03: an optional commission reduces the quantity correctly.

## 4. Repaint checks (L4)

**Bar Replay test**
1. Open a 1m chart, click **Replay**, and choose a start about 2 hours before a known setup.
2. Step forward one candle at a time through the setup.
3. Pass when every event, setup marker and state change appears on the same candle it
   appears on the normal (historical) chart, and nothing appears then disappears.

**Reload test**
1. Keep the indicator on a live chart during a session and screenshot each new setup.
2. Reload the page later.
3. Pass when the historical chart shows exactly the same setups, on the same candles, at the same prices.

## 5. Edge cases (L5)

- Daylight-saving change weeks (US and Europe change on different dates)
- Exchange holidays and early-close days
- The Sunday evening open, and the first candles of available history
- Contract roll weeks (`NQ1!` / `MNQ1!`)
- Large gap opens
- Days with no breakout, days with breakouts on both sides, days with no setup at all
- An ORB length that doesn't divide evenly by the chart timeframe → a warning is shown
- 1m and 5m charts (D2.2); other timeframes show the "untested timeframe" notice
- US/UK daylight-saving mismatch weeks: London window stays 01:00–04:00 Chicago (D15.3)

## 6. Setup counts: a spam detector, not a target

Setup counts per day are recorded during L3 and L5 **only** to catch lifecycle bugs (for
example, the same event producing two setups). They are never used to tune rules for
more or fewer setups. A day with zero setups is a valid result.

## 7. Results log

| Date | Phase / module | Level | Result | Notes / screenshot |
|---|---|---|---|---|
| 2026-09-25 | Phase 0 / tooling | L0 | PASS | 32 tool self-tests, lint (0 problems), build check: all pass locally |
| 2026-09-25 | Phase 0 / pipeline check | L1 | PASS | Compiled and added to an NQ1! 5m chart in TradingView with no errors (reported by you) |
| 2026-09-25 | Phase 1 / core | L0 | PASS | Build, lint (10 files, 0 problems) and 32 tool tests pass |
| 2026-09-25 | Phase 1 / core | L1 + L2 | PASS | CORE 31/31 PASS in TradingView; PX-04: diff 0 over 5554 candles, 0 start mismatches (screenshot from you) |
| 2026-09-25 | Phase 2 / sessions | L0 | PASS | Build, lint (13 files, 0 problems), 32 tool tests |
| 2026-09-25 | Phase 2 / sessions | L1 + L2 | PASS | SESSIONS 13/13 PASS in TradingView (screenshot from you) |
| 2026-09-25 | Phase 2 / sessions | L6 (visual) | PASS | MNQ1! 1m ETH, 3 days: Asia 19:00–23:00 and London 01:00–04:00 outlines correct, faint, uncluttered. Note: the chart must be in ETH mode (RTH hides overnight candles; warning added in v0.2.1) |
