# Rulebook — Confluence Engine (DRAFT)

**Status:** DRAFT. Parameters marked `Dx.y` are open in `DECISIONS.md`. This rulebook
can't be approved until they are decided.
**Built in:** Phase 8. **Depends on:** all detector modules.

## 1. Purpose

The confluence engine decides whether a combination of **market events** is strong
enough to become a setup. It is a **checklist, not a score**. There are no weights,
percentages, "probabilities" or AI ratings. Every item is a yes/no condition with a
written rule behind it.

## 2. Quality principle

The system is designed to produce **few, meaningful setups**. Defaults are strict.
Setup count is **never** a goal and is never tuned upward. A day with no setups is
a normal, valid result. Setup counts are recorded during testing **only** to catch
spam bugs (see `TESTING.md`).

## 3. Factor classes

Every factor belongs to exactly one class. The class decides what the factor is allowed
to do.

| Class | Factors | Can create a setup? |
|---|---|---|
| **Core events** | Liquidity sweep (of an eligible pool, D5.1) · Structure shift (BOS/CHoCH on the trigger layer, D6.4) · ORB breakout (D3) · ORB false breakout / ORB sweep (D4) | **Yes**, but only in the combinations defined by a setup type (§4) |
| **Location** | Active supply/demand zone · FVG (D8.4) · key level (PDH/PDL, session H/L, ORB level) | No. It can be required (D9.4). |
| **Context** | Session · Bias · ORB state (above / inside / below) | **Never** (fixed rule). It can only filter or inform. |

**Fixed rule C-1:** context factors can never create a setup, alone or in any
combination. *ORB state + session + bias* can never produce a setup.

**Fixed rule C-2:** a single core event is never enough. Every setup type needs **two
core events in a defined order** (§4).

**Fixed rule C-3:** setups are triggered by **events** (something that happens once, on a
specific candle), never by **states** (something that stays true, like "price is above
the ORB"). This is the main protection against signal spam; see `setup_lifecycle.md`.

## 4. Setup types: the explicit core requirements

Each type names its two required core events, their order and their time limit.
Which types are enabled is decision **D9.1**.

### T1 — Sweep → Shift (reversal)
1. **Event 1:** a liquidity sweep of an eligible pool (D5.1), by the sweep rules (D5.3–D5.6).
2. **Event 2:** a structure shift **in the opposite direction** to the swept side, on the
   trigger layer (D6.4), confirmed within N candles of Event 1 (D9.2).
   - A sweep of lows (sell-side) followed by a bullish shift gives a **long**.
   - A sweep of highs (buy-side) followed by a bearish shift gives a **short**.
3. **Trigger candle:** the candle whose close confirms Event 2.
4. Several sweeps before one shift: D9.3.

### T2 — ORB Breakout → BOS (continuation)
1. **Event 1:** an ORB breakout (D3.1) inside the ORB trading window (D1.5).
2. **Event 2:** a BOS **in the same direction** on the trigger layer, confirmed within N
   candles (D9.2), with no ORB false breakout (D4) in between.
3. **Trigger candle:** the candle whose close confirms Event 2.
4. The breakout alone is **never** enough (C-2).

### T3 — ORB Failure → Shift (reversal)
1. **Event 1:** an ORB false breakout (D4.1) or an ORB sweep (D4.3).
2. **Event 2:** a structure shift back toward the inside of the range, on the trigger
   layer, within N candles (D9.2).
3. **Trigger candle:** the candle whose close confirms Event 2.

### Overlap between types
If ORB H/L are liquidity pools (D5.1), an ORB sweep followed by a shift matches both T1
and T3. **Only one setup is created** (LC-1). Its label is decided by D9.10.

## 5. Qualification: exact order of checks

On each **closed** candle, while the lifecycle state is `ARMED` (see `setup_lifecycle.md`):

1. **Core gate:** did an enabled setup type's Event 2 confirm on this candle, with an
   eligible (unused, new enough, D14.4) Event 1 inside its time limit? If not, stop here.
   Nothing happens, and nothing is recorded.
2. **Location:** is the location requirement met (D9.4)?
3. **Context filters:** is the time inside a tradeable session (D9.5, D15.2), inside the ORB
   window for T2/T3 (D1.5), and does the bias allow it (D9.8)?
4. **Trade plan:** can a valid plan be built? That means a valid stop (D11), a valid
   retest level for Model B (D10.5), stop size within limits (D11.4/5) and minimum R:R (D12.3).
5. **Caps:** is it within the per-session and per-day limits (D14.8/9)?
6. **Optional factors:** are at least M optional factors true (D9.9)?

- If 1–6 all pass, the setup is **QUALIFIED** and the lifecycle takes over.
- If 1 passes but any of 2–6 fails, the result is **REJECTED**. The reason is recorded,
  and the events are handled per D14.7.

## 6. Checklist display

The checklist lists every factor with ✓ / ✗ and a short fact, for example:

```
LONG · T1 Sweep → Shift
✓ Sweep     PDL swept 08:47
✓ Shift     internal CHoCH ↑ 08:52
✓ Location  bullish FVG (own displacement)
✓ Session   NY AM
✗ Bias      neutral
Optional 1/3
```

It shows **only facts**. It never shows words like "strong", "high probability" or "A+".

## 7. Self-tests (summary; full list in TESTING.md)

- CT-01: ORB breakout + session + bullish bias, no second core event → **no setup**.
- CT-02: Event 2 comes before Event 1 → **no setup**.
- CT-03: Event 2 later than N candles after Event 1 → **no setup**.
- CT-04: core gate passes, location missing (D9.4a) → **REJECTED**, reason "location".
- CT-05: a valid T1 sequence → exactly **one** QUALIFIED setup, with the correct events attached.
- CT-06: a T2 sequence interrupted by a false breakout → **no setup**.
