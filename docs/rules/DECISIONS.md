# Trading Rules — Decision Register

**Purpose:** every trading rule that could reasonably be defined in more than one way
is listed here as a question. Nothing in this project is coded until the decisions it
depends on are marked **DECIDED** with your answer.

**Ground rules**
- Claude may propose options and mark a suggestion with ★, with the reason. A ★ is
  **not** a decision. It becomes one only when you accept it.
- Questions marked **❗** have no suggestion. They need your answer.
- Answers can be given in chat by ID, e.g. `D1.1 = 08:00`, `D3.1 = a`, `D5 = accept all ★`.
- If a question is unclear, answer "explain" and it will be expanded before you decide.
- Once decided, the answer is copied into the relevant rulebook in `docs/rules/` and
  the decision is never silently changed. Later changes are logged at the bottom of this file.

Status key: `OPEN` · `DECIDED` · `CHANGED` (decided, then revised; see change log)

---

## D1 — Opening range (ORB)

| ID | Question | Options | Status |
|---|---|---|---|
| D1.1 ❗ | ORB **start time** | **08:00** (Chicago time, per D1.2) = 09:00 New York | DECIDED |
| D1.2 ❗ | **Timezone** for the ORB (and for sessions, unless D15.3 says otherwise) | **b) Chicago** (America/Chicago) | DECIDED |
| D1.3 | How the ORB **end** is defined | a) ★ start + length preset (5/15/30/60 min) · b) an explicit end time you type | OPEN |
| D1.4 | Default ORB **length** | 15 minutes (from your scope message); 5/15/30/60 selectable | DECIDED |
| D1.5 ❗ | **ORB trading window end**: time after which no ORB-based setup may form | **11:00 Chicago** (= 12:00 New York) | DECIDED |
| D1.6 | How many opening ranges | a) ★ one configurable ORB (simpler, cleaner chart) · b) two independent ORBs (e.g. 08:00 and 09:30) | OPEN |

## D2 — Chart timeframes and account

| ID | Question | Options | Status |
|---|---|---|---|
| D2.1 ❗ | Timeframe(s) **you trade** on | **5m primary**; 1m also used | DECIDED |
| D2.2 | Timeframes **officially supported and tested** | **1m and 5m** (from the D2.1 answer). Other timeframes are untested and show a notice. | DECIDED |
| D2.3 ❗ | Your **TradingView plan** | **Pro** | DECIDED |
| D2.4 | How **durations** are defined (Model B expiry, cooldown, max gap between core events, false-breakout window) | **In minutes**, so they behave the same on 1m and 5m. A duration ends on the first candle close at or after start + duration. Structure sensitivity (D6.1/D6.2) stays in candles, because it's a shape, not a duration. | DECIDED |

## D3 — Breakout confirmation (ORB)

| ID | Question | Options | Status |
|---|---|---|---|
| D3.1 | What counts as an ORB **breakout** | a) ★ one candle **closes** beyond the ORB level · b) close beyond by at least X ticks · c) two consecutive closes beyond · d) close beyond with a displacement body (≥ k × ATR) | OPEN |
| D3.2 | Breakouts per side per day | a) ★ first breakout only · b) a new breakout after price returns inside also counts | OPEN |

★ D3.1a: simplest objective rule, and it doesn't repaint. D3.2a: fewer repeated events.

## D4 — False breakout (ORB)

| ID | Question | Options | Status |
|---|---|---|---|
| D4.1 | Definition of an ORB **false breakout** | a) ★ a confirmed breakout (D3.1), then a candle **closes back inside** the range within N candles · b) same, but the close back must also be beyond the ORB **midpoint** | OPEN |
| D4.2 | Time allowed for the failure (minutes, per D2.4) | ★ 15 minutes (3 candles on 5m) | OPEN |
| D4.3 | A wick through the ORB level that **closes inside** with no confirmed breakout | a) ★ recorded as an **"ORB sweep"** (a liquidity event, kept separate from a false breakout) · b) treated as a false breakout · c) ignored | OPEN |

## D5 — Liquidity and sweeps

| ID | Question | Options | Status |
|---|---|---|---|
| D5.1 | Which levels are **liquidity pools that can anchor a setup** (choose any) | PDH/PDL · previous-session H/L (which sessions?) · EQH/EQL · ORB H/L · swing-layer highs/lows · internal highs/lows. ★ PDH/PDL, Asia H/L, London H/L, EQH/EQL, ORB H/L. Raw swing points are excluded to keep setups meaningful. | OPEN |
| D5.2 ❗ | "Previous day" means | **a) full futures day**, 18:00–17:00 New York (= 17:00–16:00 Chicago) | DECIDED |
| D5.3 | **Minimum penetration** beyond a level for a sweep | a) 1 tick · b) ★ 2 ticks · c) fraction of ATR | OPEN |
| D5.4 | **Close-back** requirement | a) ★ the **same candle** must close back on the original side · b) within N candles (then it's also a "failed break") | OPEN |
| D5.5 | **Rejection-strength** filter | a) none (close-back only) · b) the wick beyond the level ≥ X % of the candle range · c) ★ the candle closes in the half of its range away from the level | OPEN |
| D5.6 | **Maximum penetration** (beyond this, it's a run rather than a sweep) | a) ★ no maximum · b) X points or k × ATR | OPEN |
| D5.7 | **Touch** tolerance: price gets this close without a sweep, and it's recorded as a touch | ★ 2 ticks | OPEN |
| D5.8 | **EQH/EQL** tolerance: how close two swing highs/lows must be to count as "equal" | a) X ticks · b) k × ATR · c) ★ whichever is larger (e.g. 4 ticks or 0.1 × ATR(14)) | OPEN |
| D5.9 | Can a pool be swept more than once? | a) ★ no: a pool is used up by its first sweep · b) yes | OPEN |

★ D5.4a/D5.5c: stricter definitions give fewer, clearer sweeps. The level-interaction
engine still records touches and breaks for display.

## D6 — Market structure (BOS / CHoCH)

| ID | Question | Options | Status |
|---|---|---|---|
| D6.1 | **Swing** sensitivity (candles on each side needed to confirm a swing) | ★ 10 (a starting point, to be tuned after seeing it on your timeframe) | OPEN |
| D6.2 | **Internal** sensitivity | ★ 3 | OPEN |
| D6.3 | What confirms a structure break | a) ★ candle **close** beyond the swing · b) wick beyond | OPEN |
| D6.4 ❗ | Which layer may **trigger setups** | **a) internal** | DECIDED |
| D6.5 | First break when the trend is still undefined | a) ★ labelled BOS; it cannot count as a CHoCH trigger · b) labelled CHoCH | OPEN |
| D6.6 | Which swing a CHoCH must break | a) ★ the most recent confirmed opposite swing · b) the "strong" swing that produced the latest high or low | OPEN |

**Delay note:** a swing is only confirmed after the D6.1/D6.2 number of candles closes
to its right. On a 1m chart with sensitivity 10, a swing is known 10 minutes after it forms.
This delay is shown honestly and is never hidden.

## D7 — Supply and demand

| ID | Question | Options | Status |
|---|---|---|---|
| D7.1 | Zone **base** | a) ★ the last opposite-colored candle before the displacement (most objective) · b) 1–3 small-bodied candles (body ≤ X × ATR) · c) either | OPEN |
| D7.2 | **Displacement** threshold: candle body ≥ k × ATR(14) | ★ k = 1.5 | OPEN |
| D7.3 ❗ | The displacement must **also** | **a) break structure**, on the **internal** layer | DECIDED |
| D7.4 | Zone **bounds** | a) ★ full base candle range (wick to wick) · b) near edge = body, far edge = wick | OPEN |
| D7.5 | Zone **invalidation** | a) ★ candle **closes** beyond the far edge · b) wick beyond the far edge | OPEN |
| D7.6 | **Retire** a zone after | ★ 2 tests (or specify a number of sessions) | OPEN |
| D7.7 | Maximum zones **shown per side** | ★ 2 | OPEN |

## D8 — Fair value gaps (FVG)

| ID | Question | Options | Status |
|---|---|---|---|
| D8.1 | **Minimum size** | a) X points · b) k × ATR · c) ★ whichever is larger (e.g. 2 points or 0.25 × ATR(14)) | OPEN |
| D8.2 | When an FVG counts as **filled** | a) ★ price trades through the far edge · b) price reaches the 50 % level | OPEN |
| D8.3 | Maximum open FVGs **shown per side** | ★ 3 | OPEN |
| D8.4 | Which FVG counts for **confluence** | a) ★ only an FVG created by the setup's own displacement · b) any open FVG price is currently retesting · c) either | OPEN |

## D9 — Confluence: core requirements

See `rules/confluence.md` for the factor classes and setup types referenced here.
**Fixed rule (yours):** context factors (session, bias, ORB state) can never create a
setup, alone or together.

| ID | Question | Options | Status |
|---|---|---|---|
| D9.1 ❗ | Which **setup types** are enabled (choose any) | **All three: T1, T2 and T3** | DECIDED |
| D9.2 | Maximum time between the two core events (minutes, per D2.4; 0 = both on the same candle is allowed) | ★ 50 minutes (10 candles on 5m) | OPEN |
| D9.3 | Several sweeps before one shift (e.g. Asia low, then PDL, then CHoCH) | a) ★ all attach to the setup and are used up; the stop goes beyond the most extreme one · b) only the most recent attaches | OPEN |
| D9.4 | **Location** requirement (zone, FVG, key level) | a) ★ at least one location factor required · b) location is shown on the checklist only · c) a specific one is required (say which) | OPEN |
| D9.5 | **Session** filter | a) ★ hard filter: setups form only inside sessions you mark as tradeable (D15.2) · b) checklist item only | OPEN |
| D9.6 ❗ | **Bias** components (choose any) | **Swing-structure trend + price vs VWAP**, VWAP anchored at **08:30 Chicago** | DECIDED |
| D9.7 | Bias rule | **a) both components must agree**, otherwise bias = neutral | DECIDED |
| D9.8 ❗ | Setups **against the bias** | **b) allowed, flagged "counter-bias"** | DECIDED |
| D9.9 ❗ | Minimum number of **optional** checklist factors (M) | **M = 1**, counted from the optional items defined in D9.11/D9.12. Items that are already required don't count. | DECIDED |
| D9.10 | One event combination matches two setup types (e.g. an ORB sweep + shift fits both T1 and T3) | Only one setup is ever created (LC-1). It's labelled a) ★ as the more specific type (T3 over T1) · b) as T1 | OPEN |
| D9.11 | When "at a key level" counts as an optional item | **Only when the setup is at a different key level from the one used by its two core events** | DECIDED |
| D9.12 | ORB position (above / inside / below) on the checklist | **Shown on the checklist, not counted toward M.** It's fixed by setup type (always ✓ for T2, always ✗ for T3). | DECIDED |

## D10 — Entry models

Both models are defined in `rules/entry_models.md`. **Model A (Close Confirmation):**
enter at the close of the trigger candle. **Model B (Limit Retest):** place a limit at a
retest level and wait for a later candle to reach it.

| ID | Question | Options | Status |
|---|---|---|---|
| D10.1 | How the models are offered | a) ★ one model chosen per chart in settings (one clear plan per setup) · b) both plans shown for every setup | OPEN |
| D10.2 ❗ | **Default** model | **B: Limit Retest** | DECIDED |
| D10.3 | Model A: extra requirement on the trigger candle | a) ★ none (the trigger event already requires a close) · b) close in the outer X % of its range · c) body ≥ k × ATR | OPEN |
| D10.4 ❗ | Model B: **retest level** | **b) FVG 50 %**. If several qualifying FVGs exist (which ones qualify: D8.4), use the **most recent one, closest to current price**. | DECIDED |
| D10.5 | Model B: the chosen level doesn't exist for this setup (e.g. no FVG formed) | a) ★ the setup is rejected (no substitute) · b) fall back to another level (say which) | OPEN |
| D10.6 | Model B: **fill** rule | a) price touches the limit · b) ★ price trades through the limit by ≥ 1 tick (more conservative) | OPEN |
| D10.7 ❗ | Model B: **expiry**, in candles without a fill | **30 minutes** (6 candles on 5m, 30 candles on 1m) | DECIDED |
| D10.8 | Model B: TP1 is reached before a fill | a) ★ setup ends as MISSED · b) keep waiting | OPEN |
| D10.9 | Accept the conservative fill/outcome conventions in `entry_models.md` §4 | ★ accept | OPEN |

## D11 — Stop placement

| ID | Question | Options | Status |
|---|---|---|---|
| D11.1 | Stop for **T1/T3** (reversals) | a) ★ beyond the sweep extreme (if price goes past it, the sweep has failed) · b) beyond the swing the shift started from · c) the farther of a and b · d) ATR multiple | OPEN |
| D11.2 ❗ | Stop for **T2** (breakout continuation), if T2 is enabled | **a) beyond the internal swing where the BOS move started** (plus the D11.3 buffer) | DECIDED |
| D11.3 | Stop **buffer** | ★ 2 ticks | OPEN |
| D11.4 ❗ | **Maximum** stop: larger stops mean no setup | **b) 30 points** maximum (entry to stop, including the buffer); wider stops mean the setup is rejected | DECIDED |
| D11.5 ❗ | **Minimum** stop | **b) 5 points** minimum; tighter stops mean the setup is rejected ("stop too tight") | DECIDED |

## D12 — Take-profit logic

| ID | Question | Options | Status |
|---|---|---|---|
| D12.1 ❗ | **TP1** | a) fixed R multiple (value?) · b) nearest opposing liquidity pool · c) nearest opposing pool at least X R away | OPEN |
| D12.2 ❗ | **TP2** | a) fixed R multiple · b) second opposing pool · c) day or session high/low | OPEN |
| D12.3 ❗ | **Minimum R:R** to TP1 for a setup to be created | a) none · b) X R | OPEN |
| D12.4 ❗ | After TP1 is hit | a) stop unchanged · b) stop moves to entry (breakeven) · c) setup ends at TP1 | OPEN |
| D12.5 ❗ | Setup still active when the trading window/session ends | a) closed at that candle's close · b) stays open until stop or target | OPEN |

## D13 — Setup invalidation

| ID | Question | Options | Status |
|---|---|---|---|
| D13.1 | A **pending** (not yet entered) setup is invalidated by (choose any) | a) candle closes beyond the stop level · b) opposite structure shift (on the D6.4 layer) · c) expiry (D10.7) · d) trading window ends · e) TP1 reached first (D10.8). ★ all five | OPEN |
| D13.2 | Can an **active** (entered) setup end early for any reason other than stop, targets or window end? | a) ★ no (prevents flip-flopping) · b) yes: an opposite swing-layer CHoCH closes it | OPEN |

## D14 — Lifecycle, cooldown and re-arm

The fixed requirements you set (one setup per event, no duplicates, no instant flip,
opposite needs a new event, used events never reused) are in `rules/setup_lifecycle.md`.
These questions set the remaining details.

| ID | Question | Options | Status |
|---|---|---|---|
| D14.1 | Live setups at the same time | a) ★ **one** in total, either direction · b) one per direction | OPEN |
| D14.2 | **Cooldown** type after a setup ends | a) N candles · b) until the next session starts · c) ★ N candles, **and** then a new core event is required | OPEN |
| D14.3 ❗ | Cooldown length (minutes, per D2.4) | a number of minutes | OPEN |
| D14.4 | Which events may build the next setup | a) ★ only events confirmed **after** the previous setup ended **and** its cooldown finished (strict) · b) only the final trigger event must be new; earlier unused events may be reused | OPEN |
| D14.5 | Can the event that stopped or invalidated a setup be used for an opposite setup? | a) ★ no: it's used up · b) yes, after cooldown | OPEN |
| D14.6 ❗ | Extra requirement for an **opposite-direction** setup after a setup ends | a) nothing beyond D14.4 · b) the shift must be on the swing layer · c) needs a new sweep **and** a new shift | OPEN |
| D14.7 | A candidate **rejected** by a filter (stop too large, R:R too low, outside session, cap) | a) ★ never re-evaluated: each event combination is checked exactly once, on the candle its final event confirms · b) may be re-checked for N candles | OPEN |
| D14.8 ❗ | Maximum setups **per session** | a) no cap · b) X | OPEN |
| D14.9 ❗ | Maximum setups **per day** | a) no cap · b) X | OPEN |
| D14.10 ❗ | After a STOPPED setup, can a **same-direction** setup form later in the same session? | a) yes, with new events (D14.4) · b) no | OPEN |

## D15 — Sessions

| ID | Question | Options | Status |
|---|---|---|---|
| D15.1 | Session times (each can be switched on/off) | Proposed (New York time): Asia 20:00–00:00 · London 02:00–05:00 · New York 09:30–16:00 · NY AM 09:30–12:00 · NY PM 13:30–16:00. Confirm or edit. | OPEN |
| D15.2 ❗ | Which sessions are **tradeable** (setups may form) | **NY AM only** | DECIDED |
| D15.3 | Define each session in its **own local time** (London in London time, Asia in Tokyo time) | a) ★ yes: stays correct during the weeks when US and European clocks change on different dates · b) no: all sessions use the D1.2 timezone | OPEN |

## D16 — Other

| ID | Question | Options | Status |
|---|---|---|---|
| D16.1 ❗ | Indicator **name** shown in TradingView | **NQ.ORB** | DECIDED |

---

## Change log

| Date | ID | Change | Reason |
|---|---|---|---|
| 2026-09-25 | D1.4 | Recorded 15 min default | From scope message |
| 2026-09-25 | D1.1 | 9:30 default withdrawn; start time is now an open question | You may use an 8:00 ORB |
| 2026-09-25 | D1.1 | Decided: 08:00 (Chicago time, per D1.2) = 09:00 New York | Your answer |
| 2026-09-25 | D1.2 | Decided: b) Chicago (America/Chicago) | Your answer |
| 2026-09-25 | D1.5 | Decided: 11:00 Chicago (= 12:00 New York) | Your answer |
| 2026-09-25 | D2.1 | Decided: 5m primary; 1m also used | Your answer |
| 2026-09-25 | D2.2 | Decided: 1m and 5m (from the D2.1 answer). Other timeframes are untested and show a notice. | Your answer |
| 2026-09-25 | D2.3 | Decided: Pro | Your answer |
| 2026-09-25 | D5.2 | Decided: a) full futures day, 18:00–17:00 New York (= 17:00–16:00 Chicago) | Your answer |
| 2026-09-25 | D15.2 | Decided: NY AM only | Your answer |
| 2026-09-25 | D16.1 | Decided: NQ.ORB | Your answer |
| 2026-09-25 | D1.1 | Reconfirmed: 08:00 Chicago (09:00 New York) is intended | Your answer |
| 2026-09-25 | D6.4 | Decided: a) internal | Your answer |
| 2026-09-25 | D7.3 | Decided: a) break structure (internal layer) | Your answer |
| 2026-09-25 | D9.1 | Decided: T1, T2 and T3 enabled | Your answer |
| 2026-09-25 | D9.6 | Decided: swing-structure trend + price vs VWAP (anchor 08:30 Chicago) | Your answer |
| 2026-09-25 | D9.7 | Decided: both bias components must agree, otherwise neutral | Your answer |
| 2026-09-25 | D9.8 | Decided: b) counter-bias setups allowed and flagged | Your answer |
| 2026-09-25 | D9.9 | Decided: M = 1 | Your answer |
| 2026-09-25 | D9.11 | Added and decided: key level counts only if different from the core events' level | Your answer |
| 2026-09-25 | D9.12 | Added and decided: ORB position shown, not counted toward M | Your answer |
| 2026-09-25 | D10.2 | Decided: default entry model B (Limit Retest) | Your answer |
| 2026-09-25 | D10.4 | Decided: b) FVG 50 %; with several FVGs, use the most recent one closest to price | Your answer |
| 2026-09-25 | D10.7 | Decided: 30 minutes | Your answer |
| 2026-09-25 | D2.4 | Added and decided: durations in minutes; D4.2, D9.2 and D14.3 restated in minutes | Your answer (with D10.7) |
| 2026-09-25 | D11.2 | Decided: a) T2 stop beyond the internal swing the BOS move started from | Your answer |
| 2026-09-25 | D11.4 | Decided: maximum stop 30 points | Your answer |
| 2026-09-25 | D11.5 | Decided: minimum stop 5 points (reject below) | Your answer |
