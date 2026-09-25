# Rulebook — Confluence Engine

**Status:** every input is decided (see `DECISIONS.md`). **Awaiting your final approval.**
Items marked *(derived)* are precise definitions needed to apply your decisions; they're
listed in `SUMMARY.md` §9 for approval.
**Built in:** Phase 8. **Depends on:** all detector modules.
All times are **Chicago time** (D1.2, D15.3).

## 1. Purpose

The confluence engine decides whether a combination of **market events** becomes a
setup. It is a **checklist, not a score**. There are no weights, percentages,
"probabilities" or AI ratings. Every item is a yes/no condition with a written rule.

## 2. Quality principle

The system is designed to produce **few, meaningful setups**. Setup count is never a
goal and is never tuned upward. A morning with no setups is a normal, valid result.

## 3. Factor classes

| Class | Items | Role |
|---|---|---|
| **Core events** | Liquidity sweep · ORB sweep · ORB breakout · ORB false breakout · internal BOS · internal CHoCH | Only these can complete a setup, and only in the sequences of §4 |
| **Location** | FVG from the setup's own move · supply/demand zone ✓ · different key level ✓ | At least one required (D9.4); the rest count toward M |
| **Context** | Session · bias · ORB position | Never creates a setup. Session is a hard filter; bias is flagged; ORB position is shown only. |

### 3.1 Core event definitions

| Event | Definition | Decisions |
|---|---|---|
| **Liquidity sweep** | On one closed candle, the wick goes ≥ **2 ticks** beyond an eligible level, the candle **closes back** on the original side, and the close is in the half of the candle's range **away from** the level. A close exactly at the midpoint counts *(derived)*. | D5.3–D5.5 |
| Eligible levels | Previous full futures day high/low (17:00–16:00) · most recent Asia high/low (19:00–23:00) · most recent London high/low (01:00–04:00) · EQH/EQL (swing-layer points within max(4 ticks, 0.1 × ATR(14))) · ORB high/low. A level is used up by its first sweep or break. | D5.1, D5.2, D5.8, D5.9, D5.11, D15.1, D15.4 |
| **ORB** | 08:00–08:15 (15 min; 5/15/30/60 selectable). High, low and midpoint are locked at 08:15. | D1.1–D1.4 |
| **ORB breakout** | The first candle **close** beyond the ORB high (or low) after 08:15 and before 11:00. One per side per day. | D3.1, D3.2, D1.5 |
| **ORB false breakout** | An ORB breakout, then a candle closes back inside the range within **15 minutes**. | D4.1, D4.2 |
| **ORB sweep** | A wick through the ORB high/low that closes inside the range, without a confirmed breakout. | D4.3 |
| **Internal BOS / CHoCH** | A candle **close** beyond the most recent confirmed internal swing (sensitivity **3**). BOS = in the direction of the internal trend; CHoCH = against it (the trend flips). The first break with no trend yet is a BOS. | D6.2, D6.3, D6.5, D6.6 |

Every internal break is either a BOS or a CHoCH, never both, so one break can complete a
T2 **or** a T1/T3 setup, never both.

## 4. Setup types (all three enabled, D9.1)

Every type needs **two core events in order**, with Event 2 confirmed **within 50
minutes** after Event 1 (D9.2). The **trigger candle** is the candle whose close
confirms Event 2.

| Type | Event 1 | Event 2 | Direction |
|---|---|---|---|
| **T1 Sweep → CHoCH** | A liquidity sweep (any eligible level) | An **internal CHoCH** against the swept side (D6.7) | Sweep of lows → long; sweep of highs → short |
| **T2 ORB Breakout → BOS** | An ORB breakout | An **internal BOS** in the breakout direction (D6.8), with no ORB false breakout in between | With the breakout |
| **T3 ORB Failure → CHoCH** | An ORB false breakout or ORB sweep | An **internal CHoCH** back toward the range | Against the failed side |

- **Several sweeps before one CHoCH:** all attach, all are used up, and the stop goes
  beyond the most extreme one (D9.3).
- **Overlap:** an ORB sweep followed by a CHoCH matches T1 and T3. One setup is created,
  labelled **T3** (D9.10).
- **Event 1 before 08:30:** an event between 08:15 and 08:30 (e.g. an ORB breakout) can
  serve as Event 1. The trigger candle must still be inside NY AM (§5 step 2).

## 5. Qualification: exact order of checks

On each **closed** candle, while the lifecycle state is `ARMED`:

1. **Core gate:** Event 2 of an enabled type confirmed on this candle, with an eligible
   Event 1 that is unused, confirmed **after the re-arm time** (D14.4) and no more than 50
   minutes earlier. If not, nothing happens and nothing is recorded.
2. **Session:** the trigger candle opens at or after 08:30 and closes at or before 11:00
   (NY AM, a hard filter; D9.5, D15.2) *(derived: session membership)*.
3. **Entry FVG (Model B):** a qualifying FVG exists:
   - It's in the setup's **own move**: from the stop-anchor point up to and including the
     trigger candle (D8.4, D8.5).
   - Its size is ≥ max(2 points, 0.25 × ATR(14)) (D8.1), and it isn't filled (D8.2).
   - If several qualify, the **most recent one, closest to price** is used (D10.4).
   - If the only candidate is the gap created by the trigger candle itself, the check
     waits **one more candle** for that gap to confirm (D8.6). Steps 3–7 then run on that
     **plan candle**, still exactly once.
   - No qualifying FVG → REJECTED "no FVG" (D10.5).
   - If the plan candle would close after 11:00 → REJECTED "window ended" *(derived)*.
4. **Location:** at least one location item ✓ (D9.4). With Model B, the entry FVG always
   meets this.
5. **Trade plan** (`entry_models.md`):
   - The stop distance is 5–30 points, buffer included (D11.4, D11.5).
   - TP1 exists (D12.1).
   - R:R to TP1 is ≥ 1.0 (D12.3).
   - The limit lies between the stop and the plan-candle close.
6. **Cap:** fewer than **2 filled** setups so far this morning (D14.8, D14.9).
7. **Optional items:** at least **M = 1** ✓ beyond the required location (§6).

- If every step passes, the setup is **QUALIFIED**.
- If any step 2–7 fails, it's **REJECTED** with the reason. Its events are used up, it is
  never re-evaluated (D14.7), and no cooldown starts (D14.13).

**Counter-bias setups are not blocked.** They're flagged **"counter-bias"** (D9.8).

## 6. Checklist items and counting M

**Counting rule** *(derived)*: the location requirement is met by **one** location item;
every **other** ✓ item below counts toward M.

| Item | ✓ when | Decisions |
|---|---|---|
| FVG | A qualifying FVG from the setup's own move exists (always true for a Model B setup that passed step 3) | D8.4, D8.5 |
| Zone | The stop-anchor point **or** the limit entry lies inside an active supply/demand zone of the setup's direction | D7.8 |
| Different key level | The stop-anchor point **or** the limit entry is within max(4 ticks, 0.1 × ATR(14)) of an eligible level **other than** the one used by the core events. Swept or broken levels still count. | D9.11, D9.13 |
| Bias agrees | Swing trend and price-vs-VWAP (anchored 08:30) **both** point in the setup's direction | D9.6, D9.7 |
| ORB position | Shown only; **never counted** | D9.12 |

In practice, with Model B the FVG meets the location requirement, so M = 1 means **at
least one of: zone, different key level, bias agrees.**

**Supply/demand zone definition** (D7.1–D7.7):
- A zone is the last opposite-colored candle before a displacement candle with a
  body ≥ 1.5 × ATR(14), and the displacement must break internal structure.
- It covers that candle wick to wick.
- It's invalidated by a close beyond its far edge, and retired after 2 tests.
- At most 2 zones are shown per side.

Example checklist:
```
LONG · T1 Sweep → CHoCH                         counter-bias
✓ Sweep     London low swept 08:47
✓ CHoCH     internal ↑ 08:55
✓ FVG       08:50–08:55 gap (entry at 50 %)       ← location
✓ Zone      entry inside demand zone             ← counts: 1/1
✗ Level     —
✗ Bias      bearish (swing ↓, below VWAP)
· ORB       inside range (not counted)
```

## 7. Self-tests (full list in TESTING.md §3.5)

CT-01 … CT-14.
