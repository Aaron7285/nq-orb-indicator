# Rulebook — Entry Models, Stops, Targets & Outcomes

**Status:** approved 2026-09-25. Items marked *(derived)* were approved as R1–R13 in `SUMMARY.md` §9.
**Built in:** Phase 10. **Depends on:** Setup lifecycle, Liquidity, Structure, FVG, Supply & Demand.
All times are **Chicago time**. 1 tick = 0.25 points.

One entry model is chosen per chart in settings (D10.1). The **default is Model B** (D10.2).
Both models start from the same qualification (`confluence.md` §5).

## 1. Model B — Limit Retest (default)

| Item | Rule | Decisions |
|---|---|---|
| Limit level L | The **50 % level** of the qualifying FVG from the setup's own move. With several, the **most recent, closest to price**. | D10.4, D8.4, D8.5 |
| When L is placed | At the close of the **plan candle**: the trigger candle, or the next candle if the trigger candle's own gap had to confirm | D8.6 |
| No qualifying FVG | REJECTED "no FVG", with no fallback | D10.5 |
| Sanity | L must lie between the stop and the plan-candle close; otherwise REJECTED "retest level invalid" | — |
| Fill | On a **later** candle, when price trades **through L by ≥ 1 tick**. An exact touch doesn't count. | D10.6 |
| Entry price | **L** (never better, even on a gap through) | — |
| Expiry | Not filled within **30 minutes** of the plan-candle close → EXPIRED *(derived: measured from the placement candle)* | D10.7, D2.4 |
| Missed | TP1 reached before a fill → MISSED | D10.8 |
| Other cancellations | A close beyond the stop level → INVALIDATED; the 11:00 candle close → CLOSED_WINDOW. **No** structure-based cancellation. | D13.1, D13.3 |
| Fill and cancellation on the same candle | The fill counts first; the setup is then ACTIVE | D13.4 |

## 2. Model A — Close Confirmation (optional setting)

| Item | Rule | Decisions |
|---|---|---|
| Entry | The close of the trigger candle. No extra candle requirement. | D10.3 |
| State | ACTIVE on the trigger candle; outcomes are tracked from the next candle | — |
| Checks | The same qualification. The entry FVG isn't needed for the entry, but the location requirement (D9.4) still applies. | — |

## 3. Stops

Buffer: **2 ticks** beyond the anchor (D11.3).

| Setup type | Stop anchor | Decisions |
|---|---|---|
| T1 | Beyond the **most extreme** attached sweep wick | D11.1, D9.3 |
| T3 | Beyond the most extreme price of the failure: the sweep wick, or for a false breakout the extreme between the breakout candle and the trigger candle *(derived)* | D11.1 |
| T2 | Beyond the **BOS-origin swing**: the most recent confirmed internal swing low (long) or high (short) at the moment of the BOS *(derived)* | D11.2 |

- **Stop distance** = |entry − stop|, buffer included.
- It must be **≥ 5 points** (else REJECTED "stop too tight") and **≤ 30 points** (else
  REJECTED "stop too wide"). (D11.4, D11.5)
- R = the stop distance.

## 4. Targets and R:R

| Item | Rule | Decisions |
|---|---|---|
| Target levels | Untouched levels (not yet swept or broken *(derived)*) from: previous-day high/low · most recent Asia and London high/low · EQH/EQL · ORB high/low · swing-layer highs/lows (targets only, any age) | D5.10, D5.12, D15.4 |
| **TP1** | The **nearest** untouched target level beyond the entry, placed **2 ticks before** it. None → REJECTED "no target". | D12.1, D12.6 |
| **TP2** | The **next** untouched target level beyond TP1, 2 ticks before it. If none exists or it isn't beyond TP1, the setup keeps **TP1 only** and is not rejected. | D12.2 |
| R:R | (TP − entry) ÷ (entry − stop), shown to 2 decimals for each target | — |
| Minimum | R:R to TP1 ≥ **1.0**, checked **once** at qualification | D12.3, D14.7 |

## 5. Trade management

| Event | Rule | Decisions |
|---|---|---|
| TP1 hit | The stop moves to **entry (breakeven)**, effective from the next candle | D12.4 |
| No TP2 | The setup ends at TP1 → TP1_FINAL | D12.2 |
| 11:00 | Anything still active is **closed at the close of the candle ending 11:00** → CLOSED_WINDOW | D12.5 |
| Anything else | Nothing else ends an active setup (no exit on structure breaks) | D13.2 |

## 6. Conservative same-candle conventions (D10.9)

| # | Within one candle | Counted as |
|---|---|---|
| 6.1 | Both the stop and a target reachable | **STOPPED** (or BREAKEVEN after TP1), marked *ambiguous* |
| 6.2 | Model B: the limit and the stop both reachable | **Filled, then STOPPED**, marked *ambiguous* |
| 6.3 | Model B: the limit and TP1 both reachable | **Filled only**; targets count from the next candle |
| 6.4 | Pending: TP1 and the limit both reachable | **Filled only** (6.3 applies), not MISSED |
| 6.5 | TP1 hit; the breakeven stop would also be touched | Only TP1 counts; breakeven applies from the next candle |
| 6.6 | Model A: the trigger candle's own high/low | Never counted (it happened before entry) |

## 7. What the indicator will never do

- Call a setup "high probability", "A+", "strong" or anything similar.
- Show win rates, expected value or probabilities.
- Move a stop or target after qualification, except the breakeven rule (D12.4).
