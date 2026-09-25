# Rulebook — Entry Models, Stops, Targets & Outcomes (DRAFT)

**Status:** DRAFT. Parameters marked `Dx.y` are open in `DECISIONS.md`.
**Built in:** Phase 10. **Depends on:** Setup lifecycle, Liquidity, Structure, FVG, Supply & Demand.

The system **does not choose an entry model for you**. Two separate models are defined
below. Which one is used (and whether both are shown) is decision D10.1/D10.2.

Both models share the same **trigger candle**: the closed candle on which the setup
becomes `QUALIFIED` (see `confluence.md` §5). They differ only in **how the entry
happens after that**.

## 1. Model A — Close Confirmation

| Item | Rule |
|---|---|
| Triggered when | The trigger candle **closes** and the setup qualifies. Optional extra candle requirement: D10.3. |
| Entry price | The **close** of the trigger candle. |
| State | `QUALIFIED` → `ACTIVE` on the trigger candle itself. There is no pending state. |
| Stop and targets | Calculated from the entry price on the trigger candle (§3). |
| Outcome tracking | Starts on the **next** candle. The trigger candle's own high/low happened before entry and is never counted. |
| Can it miss? | No. It's always "filled" at the close. |
| Strengths / costs | Never misses a move. The entry is usually further from the stop, so R:R is lower. |

## 2. Model B — Limit Retest

| Item | Rule |
|---|---|
| Triggered when | The same trigger candle closes and the setup qualifies. At that moment a **limit price L** is fixed at the retest level (D10.4). |
| If no retest level exists | Per D10.5 (★ rejected, no substitute). |
| Sanity rule | L must lie between the stop and the trigger-candle close. Otherwise the setup is rejected with reason "retest level invalid". |
| State | `QUALIFIED` → `PENDING` on the trigger candle. |
| Fill | On a **later** candle (never the trigger candle), when price reaches L by the fill rule (D10.6). |
| Entry price | **L** (never assumed to be better than the limit, even if price gaps through it). |
| Expiry | No fill within D10.7 candles → `EXPIRED`. |
| Missed | TP1 reached before a fill → `MISSED` (D10.8). |
| Invalidation before fill | D13.1 (close beyond stop, opposite shift, window end…). |
| Strengths / costs | Better price and R:R. It can miss moves that never retest. Touch fills are optimistic, which is why ★ D10.6 requires trading through by 1 tick. |

## 3. Stops, targets and R:R (shared by both models)

- **Stop:** per setup type: T1/T3 use D11.1, T2 uses D11.2, plus the buffer (D11.3).
  Setups whose stop is larger than D11.4 or smaller than D11.5 are rejected.
- **TP1 / TP2:** D12.1 / D12.2. If a target is based on a liquidity pool and no pool
  exists in that direction, the setup is rejected with reason "no target".
- **R:R** for each target = |target − entry| ÷ |entry − stop|, shown to 2 decimals.
- **Minimum R:R:** D12.3. It's checked once, on the trigger candle, and never re-checked
  later (D14.7).
- **After TP1:** D12.4. **Window/session end:** D12.5.

## 4. Conservative fill and outcome conventions (accept via D10.9)

Historical candles only show open, high, low and close, not the order in which prices
traded. To avoid flattering results, these conventions apply everywhere:

| # | Situation within one candle | Counted as |
|---|---|---|
| 4.1 | Both the stop and a target are reachable | **STOPPED**, marked *ambiguous* |
| 4.2 | Model B: both the limit and the stop are reachable | **Filled, then STOPPED**, marked *ambiguous* |
| 4.3 | Model B: both the limit and TP1 are reachable | **Filled only**. Targets are counted from the next candle. |
| 4.4 | Model B: both TP1 and the limit are reachable, while still pending | **Filled only** (4.3 applies). It's not counted as MISSED, because the order is unknown. |
| 4.5 | Stop moved to breakeven (if D12.4 b) and hit on the same candle as TP1 | Only TP1 is counted on that candle. The breakeven stop applies from the next candle. |

These conventions exist to keep the display honest. The indicator never presents
outcomes as a performance statistic.

## 5. What the indicator will never do

- Call a setup "high probability", "A+", "strong" or anything similar.
- Show win rates, expected value or any probability.
- Move a stop or target after the trigger candle, except the explicit D12.4 rule.
