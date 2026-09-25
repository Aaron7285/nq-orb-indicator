# Rulebook — Opening Range (Phase 3)

**Status:** DRAFT, awaiting your approval. Built from approved decisions (D1.1–D1.6, D3, D4,
D5.9, R2, R9, C1–C8). **O1–O3** (§6) are details the decisions don't fully pin down; they need
your answer. All times are **Chicago**.

## 1. The range

- It runs **08:00 → 08:15** by default. The length can be set to 5, 15, 30 or 60 minutes;
  the end is the start plus the length (D1.1–D1.4).
- It's built from the candles inside the window (R1), which is 3 candles on 5m or 15 on 1m.
- It tracks the **high, low and midpoint**, and is **locked at the close of the last candle
  inside the window** (08:15). From the next candle on, the ORB high/low can be judged (C5).
- There's one ORB per trading day (D1.6), and it belongs to that day (C1).

## 2. Events (all judged on closed candles only)

| Event | Rule | Direction | Source |
|---|---|---|---|
| **ORB breakout** | The **first** candle that **closes above** the ORB high (or below the low) after the lock and no later than 11:00. At most one per side per day. | With the break | D3.1, D3.2, D1.5 |
| **ORB false breakout** | After a breakout, a candle **closes back inside** the range within **15 minutes** of the breakout candle's close. | Against the break (a failed up-breakout is bearish) | D4.1, D4.2 |
| **ORB sweep** | The core sweep test on the ORB high/low level (≥ 2 ticks through, same-candle close back, close in the half of the candle away from the level), with no confirmed breakout on that side. | Against the swept side | D4.3, C8 |

- **Extreme** (used later for T3 stops): for a sweep, the wick extreme. For a false
  breakout, the most extreme price between the breakout candle and the failure candle
  (R2).
- **Events from 08:15 to 08:30** are recorded normally. They can be Event 1 of a setup;
  setups themselves can only trigger inside NY AM (R9).
- After 11:00, no new ORB events are recorded (D1.5).
- The ORB high/low also become **liquidity levels**: they can be swept by T1 and used as
  targets (Phase 6). A breakout marks the level BROKEN (D5.9).

## 3. Display (DESIGN §6.1)

- A box from 08:00 to 08:15 with fill `accent` at 92 %, and an `accent` 60 % border that's
  dashed while forming and solid once locked.
- High and low lines extend to 11:00 (`accent` 25 %), with a dotted midline in `ink.secondary`.
- Tags: `ORB H` · `ORB L` · `ORB M`. The Standard preset shows today only.
- Events get a tiny tag on the event candle: `brk ▲` / `brk ▼`, `fail`, `sweep`.

## 4. Settings

Start time (HHMM, default 0800), length (5/15/30/60, default 15), and show/hide.

## 5. Self-tests (OR series, TESTING.md §3.2)

These cover: exact high/low/mid on 1m and 5m, the lock at 08:15, no events before the lock,
one breakout per side, the false breakout at 15 vs 16 minutes, ORB sweep vs touch, the 11:00
cutoff, the Event 1 window from 08:15 to 08:30, the DST change, and the O1–O3 cases.

## 6. Definitions that need your answer

| # | Question | Options |
|---|---|---|
| **O1** | For a false breakout, does a close **exactly at** the ORB high (or low) count as "back inside"? | a) ★ yes, which matches C2, where a close at a level isn't beyond it · b) no, it must close strictly inside |
| **O2** | If the ORB high is **swept** first (a wick through, close back inside), can a **later close above** it still be the ORB breakout? | a) ★ yes: the sweep uses up the ORB high as a *liquidity level* (D5.9), but the breakout is a separate ORB event (D3) · b) no: once swept, there's no breakout on that side that day |
| **O3** | What if the ORB window is **incomplete**, because of a holiday, a late open or chart history starting after 08:00? | a) ★ no ORB that day: no levels, no ORB events, no T2/T3 · b) use whatever candles exist |
