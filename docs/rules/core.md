# Rulebook — Core (Phase 1)

**Status:** DRAFT, awaiting your approval. Definitions marked **C1–C9** make the approved
rules precise at the level of single candles; they need your approval (§10).
**Built in:** Phase 1. **Depends on:** nothing. Every other module depends on the core.
All times are **Chicago** (`America/Chicago`). 1 tick = 0.25 pt.

The core contains **no trading decisions of its own**. It gives every module the same
clock, the same price math, the same way of judging a candle against a level, and the
same event format, so the rules in `SUMMARY.md` are applied identically everywhere.

---

## 1. What the core provides

| Part | Purpose |
|---|---|
| Time | Trading day, session membership, minute-based durations, timeframe support |
| Price | Tick rounding, points ↔ ticks, ATR(14) |
| Levels | The level record and the **level-interaction engine**: touch / sweep / break |
| Events | The event record, unique event IDs, the daily event store, the used flag |
| Drawing | Per-module drawing budgets within TradingView's 500-object limits |
| Theme | Dark/light detection and the `DESIGN.md` color tokens |
| Self-tests | The framework that plays scripted candles and prints a PASS/FAIL table |

## 2. Time

| Item | Rule | Source |
|---|---|---|
| Timezone | Every clock time is interpreted in `America/Chicago`, independent of your chart's timezone setting | D1.2, D15.3 |
| **Trading day** | A candle belongs to the futures day that starts at 17:00. Formally: the Chicago calendar date of (candle open time + 7 hours). A candle opening at 16:55 on Monday belongs to Monday; one opening at 17:00 on Monday belongs to Tuesday. **(C1)** | D5.2, R5 |
| Daily reset | At the first candle of a new trading day: the event store is cleared, and the morning's setup count and "previous setup" are reset | D14.11, R5 |
| Session membership | A candle is **in** a window if it opens at or after the window's start **and** closes at or before its end | R1 |
| Durations | Measured in minutes. A duration that starts at time T ends on the **first candle close at or after T + duration** | D2.4, R8 |
| Timeframes | 1m and 5m are supported. Other timeframes still run, but show a small "untested timeframe" notice | D2.2 |

Candle open and close times come from TradingView's `time` and `time_close`. They're
known in advance for every candle, so using them isn't lookahead.

## 3. Price

| Item | Rule | Source |
|---|---|---|
| Tick | `syminfo.mintick` on the chart (0.25 for NQ/MNQ). Self-tests use a fixed 0.25. | — |
| Rounding | Levels, stops and targets are already on ticks. The only computed price is the Model B limit (an FVG's 50 % level). If it falls **exactly between two ticks**, the limit goes on the tick **closer to the current price**: the higher tick for a long, the lower for a short. **(C9)** | D10.4 |
| **ATR(14)** | Wilder's ATR over 14 candles, identical to TradingView's `ta.atr(14)`, calculated on **the chart's own candles**. The value used is the ATR **as of the close of the candle being judged**. **(C6)** | D5.8, D7.2, D8.1 |

**Consequence of C6:** ATR-based thresholds (the FVG minimum size, EQH/EQL tolerance, zone
displacement) are smaller on a 1m chart than on a 5m chart, because 1m candles are
smaller. That's consistent with structure being measured in candles (D2.4).

## 4. Levels

A **level** is a horizontal price the system watches: PDH/PDL, Asia and London high/low,
ORB high/low, EQH/EQL, and swing-layer highs/lows.

| Field | Meaning |
|---|---|
| kind | `PDH` `PDL` `ASH` `ASL` `LOH` `LOL` `ORBH` `ORBL` `EQH` `EQL` `SWH` `SWL` |
| side | **High-type** (price is below it; it gets swept upward) or **low-type** (the mirror) |
| price | Rounded to the tick |
| known from | The close of the candle on which the level became final (e.g. 08:15 for the ORB, 23:00 for Asia) |
| state | `ACTIVE` → `SWEPT` or `BROKEN` (final; D5.9) |
| sweepable | Yes for PDH/PDL, Asia/London, ORB, EQH/EQL. No for swing highs/lows (targets only; D5.10). |
| targetable | Yes for all kinds (D5.10) |

- A level is judged only from the **first candle that opens after it became known**. It
  never interacts on the candle that created it. **(C5)**
- Several levels at the same price are judged **independently**, so one candle can
  sweep several levels at once. D9.3 then attaches all of them. **(C7)**

## 5. Level-interaction engine

Run once per **closed** candle, for every `ACTIVE` level. It's written here for a
**high-type** level L; a low-type level is the exact mirror (low instead of high, below
instead of above).

| Result | Test (for a high-type level) | Source |
|---|---|---|
| **BREAK** | close > L | D5.9 |
| **SWEEP** | high − L ≥ 2 ticks **and** close ≤ L **and** close ≤ (high + low) ÷ 2 | D5.3–D5.5, R7 |
| **TOUCH** | Not a break or sweep, **and** high ≥ L − 2 ticks | D5.7 |
| none | Everything else | — |

- **Precedence:** BREAK before SWEEP before TOUCH. Each candle gives each level at most
  one result. **(C4)**
- **A close exactly at the level counts as closing back**, not as a break. **(C2)**
- **Touch includes near-sweeps.** A wick that goes through by only 1 tick, or a wick that
  goes 2+ ticks through and closes back but fails the half-of-range test, is a **TOUCH**.
  The level stays active. **(C3)**
- **SWEEP** and **BREAK** set the level's state for good (D5.9) and emit an event (§6).
  **TOUCH** emits nothing that setups use. It only goes to the display and the
  dashboard.
- **ORB sweeps use this same test** (2 ticks, same-candle close back, half-of-range).
  **(C8)**
- **Failed breaks** (D4.1, a breakout that closes back inside within 15 min) are judged
  by the ORB module, using BREAK from this engine plus a D2.4 duration.

## 6. Events

| Field | Meaning |
|---|---|
| kind | `SWEEP`, `ORB_BREAK`, `ORB_FALSE_BREAK`, `IBOS`, `ICHOCH`, `SBOS`, `SCHOCH`, `FVG`, `ZONE` |
| direction | +1 bullish / −1 bearish. A sweep of a high-type level is bearish, a sweep of a low-type level bullish. |
| level | The level involved (if any) and its price |
| extreme | For sweeps and failures: the wick extreme (used for stops, D11.1, R2) |
| confirmed at | The open time of the confirming candle |
| used | False until attached to a setup or rejected candidate; then true for good (L-2) |

- **Event ID** = kind : direction : level ID : confirming-candle time. For example,
  `SWEEP:+1:LOL-20260925:1790330700000`. Two events are the same only if all four parts
  match (lifecycle §3).
- **Level ID** = kind + trading day for daily levels (e.g. `PDH-20260925`), or kind +
  swing time for swing-based levels (e.g. `EQH-1790322600000`).
- **Store:** each trading day keeps its events in one list (at most 300), which is
  cleared at the daily reset. Setups never need older events: Event 1 must fall within 50
  minutes of Event 2, inside the same morning.

## 7. Drawing budget

TradingView allows at most 500 lines, 500 labels and 500 boxes per script. Each module
owns a fixed share. When a module needs a new object beyond its share, its **oldest**
object is deleted first. That affects older history only, never the live morning.

| Module | Lines | Labels | Boxes |
|---|---|---|---|
| ORB | 20 | 20 | 10 |
| Liquidity | 80 | 80 | 0 |
| Structure | 60 | 60 | 0 |
| FVG | 20 | 0 | 80 |
| Supply & demand | 0 | 0 | 40 |
| Sessions | 40 | 20 | 20 |
| Setups | 80 | 80 | 20 |
| Notices and self-tests | 20 | 20 | 0 |
| **Allocated / reserve** | **320 / 180** | **280 / 220** | **170 / 330** |

These are technical caps on stored history. What you actually **see** is set by the
display presets and the clutter budget in `DESIGN.md` §8–9.

## 8. Theme

- **Dark theme** when 0.299·R + 0.587·G + 0.114·B of `chart.bg_color` < 128; otherwise light.
- All modules take colors **only** from the core's tokens (`bull`, `bear`, `accent`,
  `ink.primary`, `ink.secondary`, `ink.faint`), with the dark and light values from
  `DESIGN.md` §2.1. No module may type its own hex color.

## 9. Self-test framework

- A test indicator (for example `dist/test/core_test.pine`) contains **scripted candles**
  (open, high, low, close, open time, close time) and the expected result of each case.
- It feeds those candles into the module functions one per chart bar, **ignoring the
  real chart data**. So it gives the same result on any symbol, timeframe or date.
- **Each scenario starts from a clean state.** The scripted times use real Chicago dates,
  including a daylight-saving change, so time rules are tested exactly.
- On the last bar it shows a table: **ID · what is tested · expected · got · PASS/FAIL**,
  and a summary row, e.g. **`CORE 24/24 PASS`**.
- The module code under test is **the same code** that goes into `dist/NQ_ORB.pine`. The
  build joins the same files into both.

## 10. Definitions that need your approval

| # | Definition |
|---|---|
| **C1** | The trading day for a candle is the Chicago date of its open time + 7 hours (the day runs 17:00 → 16:00). |
| **C2** | For a high-type level, a close **exactly at** the level counts as closing back (not a break). Mirror for low-type. |
| **C3** | Near-misses are **touches**: a wick through by only 1 tick, or a wick 2+ ticks through that closes back but fails the half-of-range test. The level stays active. |
| **C4** | Each candle gives each level at most one result, checked in the order break → sweep → touch. |
| **C5** | A level is only judged from the first candle that opens **after** it became known. |
| **C6** | ATR(14) = Wilder's ATR (as `ta.atr(14)`) on the chart's own candles, taken at the close of the candle being judged. So thresholds are smaller on 1m than on 5m. |
| **C7** | Levels at the same price are judged independently; one candle can sweep several at once. |
| **C8** | An ORB sweep uses exactly the same sweep test as every other level (2 ticks, same-candle close back, half-of-range). |
| **C9** | If an FVG's 50 % level falls exactly between two ticks, the limit goes on the tick closer to the current price (long: higher tick; short: lower tick). |

## 11. Self-tests for this phase

See `TESTING.md` §3.1: the LI (level interaction), TM (time), PX (price), EV (events),
DB (drawing budget) and TH (theme) series.
