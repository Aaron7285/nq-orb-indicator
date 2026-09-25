# Testing Guide

Claude can't run TradingView from its cloud session. Claude writes the code, the
automatic checks and the self-tests. **You run the TradingView steps** and report back
(a screenshot or the error text is enough).

---

## 1. Test levels

| Level | Test | Pass when | Who |
|---|---|---|---|
| L0 | Automatic checks | `build.py` and `lint.py` succeed; the GitHub check shows ✓ | Automatic |
| L1 | Compile | The module's test indicator **and** the full build add to the chart with no errors | You |
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
5. **Integrate:** the module is added to `dist/NQ_System.pine`, then L1, L7 and L8 are re-run.

## 3. Self-test catalogue

A self-test feeds a scripted sequence of candles (or, for the lifecycle engine, events)
into the module and compares the result with the expected answer written in the rulebook.
The IDs below are the minimum set. Each module's rulebook adds its own cases.

### 3.1 Core: level-interaction engine (LI)
- LI-01: price comes within the touch tolerance without penetrating → **TOUCH**, not a sweep.
- LI-02: wick through by ≥ the minimum penetration, closes back, meets the rejection filter → **SWEEP**.
- LI-03: wick through by less than the minimum penetration → **TOUCH**.
- LI-04: wick through, closes back, fails the rejection filter → **not a sweep**.
- LI-05: closes beyond → **BREAK**; then closes back within N → **FAILED BREAK**.
- LI-06: a level already swept (D5.9a) gets swept again → no second sweep event.

### 3.2 Opening range (OR)
- OR-01: high/low/midpoint match the scripted window exactly; locked at the window end.
- OR-02: no breakout event while the range is forming.
- OR-03: first close beyond → one breakout event; later closes beyond → none (D3.2a).
- OR-04: breakout then close back inside within N → one false-breakout event.
- OR-05: wick through, close inside, no breakout → an ORB sweep event (D4.3a).
- OR-06: the start time is correct across a daylight-saving change.

### 3.3 Structure (MS)
- MS-01: a swing is confirmed exactly N candles after it forms, never earlier.
- MS-02: close beyond the swing high in an uptrend → BOS; against the trend → CHoCH and the trend flips.
- MS-03: a wick beyond without a close (D6.3a) → no break.
- MS-04: each swing level is broken at most once.

### 3.4 FVG (FV), Liquidity (LQ), Supply & Demand (SD), Sessions (SE)
Cases are written into each module's rulebook at the start of its phase, following the
same pattern: one PASS/FAIL row per rulebook rule.

### 3.5 Confluence (CT)
- CT-01: ORB breakout + session + bullish bias, with no second core event → **no setup**.
- CT-02: Event 2 comes before Event 1 → **no setup**.
- CT-03: Event 2 later than N candles after Event 1 → **no setup**.
- CT-04: core gate passes, location missing (D9.4a) → **REJECTED** ("location").
- CT-05: a valid T1 sequence → exactly **one** QUALIFIED setup with the correct events attached.
- CT-06: a T2 sequence interrupted by a false breakout → **no setup**.

### 3.6 Setup lifecycle / anti-spam (LT)
These enforce the fixed requirements LC-1 … LC-7 in `rules/setup_lifecycle.md`.

| ID | Scripted scenario | Expected |
|---|---|---|
| LT-01 | A valid setup qualifies, and its conditions stay true for 20 more candles | Exactly **1** setup |
| LT-02 | A setup is stopped; the same sweep and shift are still within the lookback window | **No** new setup (events already used) |
| LT-03 | A long is active; price falls through the stop | Long **STOPPED**; **no short** on that candle or during cooldown |
| LT-04 | After LT-03, the bearish CHoCH that happened during the stop-out is the only bearish event | **No short** (D14.5a) |
| LT-05 | After cooldown, a **new** sweep and a **new** shift confirm | One new setup is allowed |
| LT-06 | A valid event combination confirms **during** cooldown | Ignored, and still ineligible after cooldown (D14.4a) |
| LT-07 | A candidate is rejected (R:R too low); on the next candle R:R would pass | **No setup** (D14.7a) |
| LT-08 | A Model B setup expires unfilled; the same events are still recent | **No** new setup |
| LT-09 | A long is live; a valid short sequence confirms | **No short** (one live setup, D14.1a) |
| LT-10 | The per-session cap is reached; another valid sequence confirms | **REJECTED** ("cap") |
| LT-11 | An opposite-direction setup that fails the D14.6 requirement | **No setup** |
| LT-12 | A same-direction setup after a stop, in the same session | Per D14.10 |
| LT-13 | Every state change on the scripted path | Exactly one alert per state change, never repeated |
| LT-14 | The whole scripted path run in Bar Replay | Identical to the historical result |

### 3.7 Entry models (EM)
| ID | Scripted scenario | Expected |
|---|---|---|
| EM-01 | Model A qualifies | Entry = trigger close; outcomes counted from the next candle |
| EM-02 | Model A: the trigger candle's own low is below the stop | **Not** stopped (it happened before entry) |
| EM-03 | Model B: price never reaches L within the expiry | **EXPIRED** |
| EM-04 | Model B: price touches L exactly (D10.6b) | **Not filled** |
| EM-05 | Model B: price trades 1 tick through L | Filled at **L** |
| EM-06 | Model B: TP1 reached before any fill | **MISSED** (D10.8a) |
| EM-07 | Model B: limit and stop both reachable in one candle | Filled, then **STOPPED**, *ambiguous* |
| EM-08 | Stop and TP both reachable in one candle | **STOPPED**, *ambiguous* |
| EM-09 | Model B: the retest level doesn't exist | **REJECTED** (D10.5a) |
| EM-10 | Model B: L isn't between the stop and the close | **REJECTED** ("retest level invalid") |
| EM-11 | R:R is calculated for TP1 and TP2 | Matches the hand calculation to 2 decimals |

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
- Every timeframe in D2.2

## 6. Setup counts: a spam detector, not a target

Setup counts per day are recorded during L3 and L5 **only** to catch lifecycle bugs (for
example, the same event producing two setups). They are never used to tune rules for
more or fewer setups. A day with zero setups is a valid result.

## 7. Results log

| Date | Phase / module | Level | Result | Notes / screenshot |
|---|---|---|---|---|
| — | — | — | — | No tests run yet (rules lock) |
