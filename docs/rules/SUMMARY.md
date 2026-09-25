# NQ.ORB — Trading Rules at a Glance

**Status:** approved 2026-09-25, including R1–R13. Every line traces to `DECISIONS.md`
(IDs in brackets). Changes need your approval and are logged in `DECISIONS.md`.
All times are **Chicago**. 1 tick = 0.25 pt. NQ = $20/pt, MNQ = $2/pt.

## 1. Chart and time
- **5m primary**, 1m also supported. Other timeframes show an "untested" notice. [D2.1, D2.2]
- Durations are in **minutes**, so they behave the same on 1m and 5m. Structure
  sensitivity is in candles. [D2.4]
- **Setups form only in NY AM, 08:30–11:00.** [D15.2, D9.5]
- Sessions (all fixed Chicago times): Asia 19:00–23:00 · London 01:00–04:00 · New York
  08:30–15:00 · NY AM 08:30–11:00 · NY PM 12:30–15:00. [D15.1, D15.3]

## 2. Opening range
- **08:00–08:15** (15 min default; 5/15/30/60 selectable). High, low and midpoint are
  locked at 08:15. One ORB. [D1.1–D1.4, D1.6]
- **Breakout:** the first candle close beyond the high or low (one per side per day).
  [D3.1, D3.2]
- **False breakout:** a breakout, then a close back inside within 15 min. [D4.1, D4.2]
- **ORB sweep:** a wick through the level that closes inside, without a breakout. [D4.3]
- ORB-based setups end at 11:00. [D1.5]

## 3. Levels and liquidity
- **Levels that can be swept:**
  - previous futures-day high/low (17:00–16:00)
  - most recent Asia high/low
  - most recent London high/low
  - EQH/EQL (swing-layer points within max(4 ticks, 0.1 × ATR))
  - ORB high/low

  [D5.1, D5.2, D5.8, D5.11, D15.4]
- **Sweep:** the wick goes ≥ 2 ticks through, the **same candle** closes back, in the half
  of its range away from the level. Within 2 ticks, or 1 tick through, is a **touch**.
  A close beyond is a **break**. [D5.3–D5.7]
- A level is used up by its first sweep or break. [D5.9]
- **Targets:** the same list plus untouched swing-layer highs/lows. EQH/EQL and swing
  targets stay active until swept or broken; the daily levels are replaced each day.
  [D5.10, D5.12, D15.4]

## 4. Structure
- **Internal** sensitivity 3 (triggers setups and zones); **swing** sensitivity 10 (bias,
  EQH/EQL, targets). [D6.1, D6.2, D6.4]
- A break needs a candle **close**. A CHoCH breaks the most recent opposite swing. The
  first break with no trend yet is a BOS. [D6.3, D6.5, D6.6]

## 5. Zones and FVGs
- **Zone:**
  - the last opposite-colored candle before a displacement (body ≥ 1.5 × ATR) that breaks
    **internal** structure
  - covers that candle wick to wick
  - invalidated by a close beyond its far edge; retired after 2 tests
  - 2 shown per side

  [D7.1–D7.7]
- **FVG:**
  - minimum size max(2 pts, 0.25 × ATR)
  - filled when price trades through the far edge
  - 3 shown per side
  - only a gap from the setup's **own move** counts: from the stop anchor to the trigger
    candle
  - the trigger candle's own gap is usable after one more candle

  [D8.1–D8.6]

## 6. Setups
Two core events, in order, with the second within **50 min** of the first. [D9.2]

| Type | Event 1 | Event 2 |
|---|---|---|
| **T1** | A liquidity sweep | An internal **CHoCH** the other way [D6.7] |
| **T2** | An ORB breakout | An internal **BOS** the same way, with no false breakout in between [D6.8] |
| **T3** | An ORB false breakout or ORB sweep | An internal **CHoCH** back toward the range (the label used when it overlaps T1) [D9.10] |

**Qualification checks, in order:**
1. The trigger candle is inside NY AM.
2. A qualifying FVG exists (Model B).
3. A location item is present.
4. The stop is 5–30 pts.
5. A target exists and R:R to TP1 is ≥ 1.0.
6. Fewer than 2 filled setups this morning.
7. At least 1 optional ✓ (bias, zone, different key level) beyond the required location.

Any failure → **REJECTED**, and it's never re-checked. Bias = swing trend + VWAP (from
08:30), both agreeing. Counter-bias setups are **allowed and flagged**. Context alone
never creates a setup. [D9.3–D9.13, D11.4, D11.5, D12.3, D14.8]

## 7. Entry, stop, targets, management
- **Entry: Model B (default).**
  - A limit at the **50 % level** of the most recent qualifying FVG.
  - It fills only when price trades 1 tick through. Entry price = the limit.
  - It **expires after 30 min**, ends as **MISSED** if TP1 comes first, and is cancelled
    by a close beyond the stop or at 11:00.
  - No structure-based cancellation. If the fill and a cancellation happen on the same
    candle, the fill counts first.
  - Model A (enter at the trigger close) is available in settings.

  [D10.1–D10.9, D13.1, D13.3, D13.4]
- **Stop (plus 2 ticks):** T1/T3 beyond the most extreme sweep; T2 beyond the BOS-origin
  internal swing. [D11.1–D11.3, D9.3]
- **TP1:** the nearest untouched level, 2 ticks before it. **TP2:** the next level beyond,
  2 ticks before it. With no TP2, the setup keeps TP1 only. [D12.1, D12.2, D12.6]
- After TP1, the stop moves to **breakeven**. Anything still open is **closed at 11:00**.
  Nothing else ends a trade. [D12.4, D12.5, D13.2]
- Same-candle ambiguity is resolved **conservatively**: stop beats target. [D10.9]

## 8. Lifecycle and anti-spam
- **One live setup at a time.** Events are used once, forever. **30-min cooldown** after
  every outcome. Only events after the cooldown count. [D14.1–D14.5, D14.7]
- **At most 2 filled setups per morning** (expired and missed don't count). A rejection
  doesn't start a cooldown. The next setup, same or opposite direction, just needs
  completely new events. Everything resets daily.
  [D14.6, D14.8–D14.11, D14.13]
- "Stop-out" = a full stop at a loss only. [D14.12]

## 9. Derived definitions (approved)
These make your decisions precise enough to code and test. They don't add new trading ideas.

| # | Definition |
|---|---|
| R1 | A candle is **in NY AM** if it opens at or after 08:30 and closes at or before 11:00. If the plan would be made after 11:00 (because of the one-candle FVG wait), the setup is rejected "window ended". |
| R2 | **T3 stop anchor** for a false breakout = the most extreme price between the breakout candle and the trigger candle. |
| R3 | **T2 "BOS-origin swing"** = the most recent confirmed internal swing low (long) or high (short) at the moment of the BOS. |
| R4 | The **location requirement** uses up one location item; every **other** ✓ counts toward M. |
| R5 | The **daily reset** happens at the futures-day start, 17:00. |
| R6 | An **untouched** level = one not yet swept or broken. Touches don't count. |
| R7 | A sweep candle closing **exactly at its midpoint** counts as "the half away from the level". |
| R8 | The **30-min expiry** is measured from the close of the candle on which the limit is placed. |
| R9 | ORB events can happen from 08:15 to 11:00. Events between 08:15 and 08:30 can be Event 1. |
| R10 | A setup without TP2 ends at TP1 (outcome **TP1_FINAL**). |
| R11 | A setup still **pending** at 11:00 is cancelled (outcome CLOSED_WINDOW, not filled). |
| R12 | The limit must lie between the stop and the plan-candle close, otherwise rejected "retest level invalid". |
| R13 | During the one-candle FVG wait, the candidate counts as the live setup. |

## 10. What it will never do
- No scores, probabilities, win rates or "high probability" wording.
- No automated trading.
- No data from other timeframes.
- No repainting.
