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
| D1.3 | How the ORB **end** is defined | **a) start + length preset** (5/15/30/60 min). Current range: 08:00–08:15 Chicago | DECIDED |
| D1.4 | Default ORB **length** | 15 minutes (from your scope message); 5/15/30/60 selectable | DECIDED |
| D1.5 ❗ | **ORB trading window end**: time after which no ORB-based setup may form | **11:00 Chicago** (= 12:00 New York) | DECIDED |
| D1.6 | How many opening ranges | **a) one configurable ORB** | DECIDED |

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
| D3.1 | What counts as an ORB **breakout** | **a) one candle close beyond the ORB level** | DECIDED |
| D3.2 | Breakouts per side per day | **a) first breakout per side only** | DECIDED |

★ D3.1a: simplest objective rule, and it doesn't repaint. D3.2a: fewer repeated events.

## D4 — False breakout (ORB)

| ID | Question | Options | Status |
|---|---|---|---|
| D4.1 | Definition of an ORB **false breakout** | **a) confirmed breakout, then a close back inside the range** within D4.2 | DECIDED |
| D4.2 | Time allowed for the failure (minutes, per D2.4) | **15 minutes** (3 candles on 5m) | DECIDED |
| D4.3 | A wick through the ORB level that **closes inside** with no confirmed breakout | **a) recorded as an "ORB sweep"** (liquidity event, separate from a false breakout) | DECIDED |

## D5 — Liquidity and sweeps

| ID | Question | Options | Status |
|---|---|---|---|
| D5.1 | Which levels are **liquidity pools that can anchor a setup** (choose any) | **PDH/PDL, Asia H/L, London H/L, EQH/EQL, ORB H/L** can be swept to trigger setups. Raw swing points are excluded. | DECIDED |
| D5.2 ❗ | "Previous day" means | **a) full futures day**, 18:00–17:00 New York (= 17:00–16:00 Chicago) | DECIDED |
| D5.3 | **Minimum penetration** beyond a level for a sweep | **2 ticks** minimum penetration | DECIDED |
| D5.4 | **Close-back** requirement | **a) same candle must close back** (on 5m and 1m alike) | DECIDED |
| D5.5 | **Rejection-strength** filter | **c) sweep candle closes in the half of its range away from the level** | DECIDED |
| D5.6 | **Maximum penetration** (beyond this, it's a run rather than a sweep) | **a) no maximum penetration** | DECIDED |
| D5.7 | **Touch** tolerance: price gets this close without a sweep, and it's recorded as a touch | **2 ticks** touch tolerance | DECIDED |
| D5.8 | **EQH/EQL** tolerance: how close two swing highs/lows must be to count as "equal" | **c) larger of 4 ticks (1 pt) and 0.1 × ATR(14)** | DECIDED |
| D5.9 | Can a pool be swept more than once? | **a) a level is used up by its first sweep** (and by a break) | DECIDED |
| D5.10 | Which levels can be **targets** (TP1/TP2, D12.1/D12.2) | **b) the D5.1 list plus untouched swing-layer highs/lows**, the latter as **targets only** | DECIDED |
| D5.11 | **EQH/EQL** are built from which swing points | **b) swing-layer points** | DECIDED |
| D5.12 | How long an untouched EQH/EQL (and a swing target, if D5.10 b) stays active | **b) active until swept or broken, whatever its age** (limited in practice by loaded chart history) | DECIDED |

★ D5.4a/D5.5c: stricter definitions give fewer, clearer sweeps. The level-interaction
engine still records touches and breaks for display.

## D6 — Market structure (BOS / CHoCH)

| ID | Question | Options | Status |
|---|---|---|---|
| D6.1 | **Swing** sensitivity (candles on each side needed to confirm a swing) | **10** candles each side (swing layer) | DECIDED |
| D6.2 | **Internal** sensitivity | **3** candles each side (internal layer) | DECIDED |
| D6.3 | What confirms a structure break | **a) candle close** beyond the swing | DECIDED |
| D6.4 ❗ | Which layer may **trigger setups** | **a) internal** | DECIDED |
| D6.5 | First break when the trend is still undefined | **a) labelled BOS**; cannot count as a CHoCH trigger | DECIDED |
| D6.6 | Which swing a CHoCH must break | **a) the most recent confirmed opposite swing** | DECIDED |
| D6.7 | What counts as the **shift** (Event 2) in T1/T3 | **a) internal CHoCH only** (the internal trend must flip) | DECIDED |
| D6.8 | What counts as the **BOS** (Event 2) in T2 | **a) internal BOS only** (the internal trend must already point in the breakout direction) | DECIDED |

**Delay note:** a swing is only confirmed after the D6.1/D6.2 number of candles closes
to its right. On a 1m chart with sensitivity 10, a swing is known 10 minutes after it forms.
This delay is shown honestly and is never hidden.

## D7 — Supply and demand

| ID | Question | Options | Status |
|---|---|---|---|
| D7.1 | Zone **base** | **a) the last opposite-colored candle before the displacement** | DECIDED |
| D7.2 | **Displacement** threshold: candle body ≥ k × ATR(14) | **k = 1.5** (body ≥ 1.5 × ATR(14)) | DECIDED |
| D7.3 ❗ | The displacement must **also** | **a) break structure**, on the **internal** layer | DECIDED |
| D7.4 | Zone **bounds** | **a) full base candle range (wick to wick)** | DECIDED |
| D7.5 | Zone **invalidation** | **a) candle closes beyond the far edge** | DECIDED |
| D7.6 | **Retire** a zone after | **2 tests**. A test = price trades into the zone, then a candle closes back outside it on the original side. | DECIDED |
| D7.7 | Maximum zones **shown per side** | **2** zones shown per side (display only) | DECIDED |
| D7.8 | When the optional item **"zone ✓"** counts for a setup | **c) either**: the stop-anchor point (setup origin) is inside an active zone of the setup direction, **or** the Model B limit entry is inside one | DECIDED |

## D8 — Fair value gaps (FVG)

| ID | Question | Options | Status |
|---|---|---|---|
| D8.1 | **Minimum size** | **c) larger of 2 points and 0.25 × ATR(14)** | DECIDED |
| D8.2 | When an FVG counts as **filled** | **a) price trades through the far edge** | DECIDED |
| D8.3 | Maximum open FVGs **shown per side** | **3** open FVGs shown per side (display only; the active setup FVG is always shown) | DECIDED |
| D8.4 | Which FVG counts for **confluence and the Model B entry** (D10.4) | **a) only an FVG created by the setup's own move** (for confluence and the Model B entry) | DECIDED |
| D8.5 | Definition of the setup's **own move** (for D8.4) | **The candles from the stop-anchor point (sweep extreme for T1/T3, BOS-origin swing for T2) up to and including the trigger candle** | DECIDED |
| D8.6 | A gap created by the **trigger candle itself** is only confirmed on the **next** candle (the third candle of the pattern) | **b) usable**: wait one more candle for the trigger candle's gap to confirm, then place the limit and run the stop/R:R checks (once). No gap and no earlier gap: rejected ("no FVG"). | DECIDED |

## D9 — Confluence: core requirements

See `rules/confluence.md` for the factor classes and setup types referenced here.
**Fixed rule (yours):** context factors (session, bias, ORB state) can never create a
setup, alone or together.

| ID | Question | Options | Status |
|---|---|---|---|
| D9.1 ❗ | Which **setup types** are enabled (choose any) | **All three: T1, T2 and T3** | DECIDED |
| D9.2 | Maximum time between the two core events (minutes, per D2.4; 0 = both on the same candle is allowed) | **50 minutes** maximum between the two core events | DECIDED |
| D9.3 | Several sweeps before one shift (e.g. Asia low, then PDL, then CHoCH) | **a) all attach and are used up; stop beyond the most extreme sweep** | DECIDED |
| D9.4 | **Location** requirement (zone, FVG, key level) | **a) at least one location item required** (zone, FVG or key level). With Model B the FVG always meets it, so M = 1 needs bias, zone or a different key level. | DECIDED |
| D9.5 | **Session** filter | **a) hard filter**: the trigger candle must close inside NY AM (08:30–11:00 Chicago) | DECIDED |
| D9.6 ❗ | **Bias** components (choose any) | **Swing-structure trend + price vs VWAP**, VWAP anchored at **08:30 Chicago** | DECIDED |
| D9.7 | Bias rule | **a) both components must agree**, otherwise bias = neutral | DECIDED |
| D9.8 ❗ | Setups **against the bias** | **b) allowed, flagged "counter-bias"** | DECIDED |
| D9.9 ❗ | Minimum number of **optional** checklist factors (M) | **M = 1**, counted from the optional items defined in D9.11/D9.12. Items that are already required don't count. | DECIDED |
| D9.10 | One event combination matches two setup types (e.g. an ORB sweep + shift fits both T1 and T3) | **a) labelled as the more specific type (T3)** | DECIDED |
| D9.11 | When "at a key level" counts as an optional item | **Only when the setup is at a different key level from the one used by its two core events** | DECIDED |
| D9.12 | ORB position (above / inside / below) on the checklist | **Shown on the checklist, not counted toward M.** It's fixed by setup type (always ✓ for T2, always ✗ for T3). | DECIDED |
| D9.13 | When a setup is **"at" a different key level** (D9.11) | **c) either the stop-anchor point or the limit entry** is within the D5.8 tolerance of another D5.1-list level; swept or broken levels **still count** | DECIDED |

## D10 — Entry models

Both models are defined in `rules/entry_models.md`. **Model A (Close Confirmation):**
enter at the close of the trigger candle. **Model B (Limit Retest):** place a limit at a
retest level and wait for a later candle to reach it.

| ID | Question | Options | Status |
|---|---|---|---|
| D10.1 | How the models are offered | **a) one model per chart, chosen in settings** (default B) | DECIDED |
| D10.2 ❗ | **Default** model | **B: Limit Retest** | DECIDED |
| D10.3 | Model A: extra requirement on the trigger candle | **a) no extra requirement** on the Model A trigger candle | DECIDED |
| D10.4 ❗ | Model B: **retest level** | **b) FVG 50 %**. If several qualifying FVGs exist (which ones qualify: D8.4), use the **most recent one, closest to current price**. | DECIDED |
| D10.5 | Model B: the chosen level doesn't exist for this setup (e.g. no FVG formed) | **a) setup rejected** ("no FVG"), no fallback level | DECIDED |
| D10.6 | Model B: **fill** rule | **b) trade through the limit by ≥ 1 tick** | DECIDED |
| D10.7 ❗ | Model B: **expiry**, in candles without a fill | **30 minutes** (6 candles on 5m, 30 candles on 1m) | DECIDED |
| D10.8 | Model B: TP1 is reached before a fill | **a) setup ends as MISSED** when TP1 is reached before a fill | DECIDED |
| D10.9 | Accept the conservative fill/outcome conventions in `entry_models.md` §4 | **Accepted**: conservative same-candle conventions in entry_models.md §4 | DECIDED |

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
| D12.1 ❗ | **TP1** | **b) nearest untouched opposing liquidity level** (level list per D5.1), placed **a set number of ticks before** the level (D12.6). No level beyond entry means the setup is rejected ("no target"). | DECIDED |
| D12.2 ❗ | **TP2** | **b) next untouched liquidity level beyond TP1** (same 2-tick offset). If none exists, or it isn't beyond TP1: **keep the setup with TP1 only** (never rejected for lack of a TP2) | DECIDED |
| D12.3 ❗ | **Minimum R:R** to TP1 for a setup to be created | **b) 1.0** minimum R:R to TP1 (measured from the limit entry, stop buffer and target offset included); below it, the setup is rejected | DECIDED |
| D12.4 ❗ | After TP1 is hit | **b) stop moves to entry (breakeven)** after TP1, effective from the next candle (entry_models.md §4.5) | DECIDED |
| D12.5 ❗ | Setup still active when the trading window/session ends | **a) closed at the close of the candle ending 11:00 Chicago** (outcome CLOSED_WINDOW) | DECIDED |
| D12.6 ❗ | Target offset: **how many ticks before** the liquidity level the target sits (1 tick = 0.25 pt) | **2 ticks** (0.5 pt) before the level, for TP1 and TP2 | DECIDED |

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
| D14.3 ❗ | Cooldown length (minutes, per D2.4) | **30 minutes**, the same after every outcome, measured from the close of the candle where the outcome happened | DECIDED |
| D14.4 | Which events may build the next setup | a) ★ only events confirmed **after** the previous setup ended **and** its cooldown finished (strict) · b) only the final trigger event must be new; earlier unused events may be reused | OPEN |
| D14.5 | Can the event that stopped or invalidated a setup be used for an opposite setup? | a) ★ no: it's used up · b) yes, after cooldown | OPEN |
| D14.6 ❗ | Extra requirement for an **opposite-direction** setup after a setup ends | **a) nothing extra**: an opposite setup is treated like any other (still needs new events after cooldown) | DECIDED |
| D14.7 | A candidate **rejected** by a filter (stop too large, R:R too low, outside session, cap) | a) ★ never re-evaluated: each event combination is checked exactly once, on the candle its final event confirms · b) may be re-checked for N candles | OPEN |
| D14.8 ❗ | Maximum setups **per session** | **2 per morning**, counting **filled setups only** (expired, missed and rejected ones don't count). Once 2 have filled, later candidates are rejected ("cap"). | DECIDED |
| D14.9 ❗ | Maximum setups **per day** | **Same limit as D14.8**: one cap of 2 filled setups per morning (NY AM is the only tradeable session) | DECIDED |
| D14.10 ❗ | After a STOPPED setup, can a **same-direction** setup form later in the same session? | **a) yes**, only if built from completely new events after the cooldown | DECIDED |
| D14.11 | Does "previous setup" reset each morning? | **Yes.** The previous setup only affects setups within the **same morning**; yesterday's setups never affect today's. | DECIDED |
| D14.12 | What counts as a **stop-out** | **Only a full stop-out at a loss** (STOPPED). Breakeven after TP1, EXPIRED, MISSED and CLOSED_WINDOW don't count. | DECIDED |

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
| 2026-09-25 | D12.1 | Decided: b) nearest untouched opposing liquidity level, placed before the level | Your answer |
| 2026-09-25 | D12.6 | Added: exact tick offset for targets ("a few ticks" needs a number) | Follow-up to D12.1 |
| 2026-09-25 | D12.6 | Decided: targets sit 2 ticks before the level | Your answer |
| 2026-09-25 | D12.2 | Decided: b) next level beyond TP1; fallback = TP1 only, no rejection | Your answer |
| 2026-09-25 | D12.3 | Decided: minimum R:R 1.0 to TP1 | Your answer |
| 2026-09-25 | D12.4 | Decided: b) breakeven stop after TP1 | Your answer |
| 2026-09-25 | D12.5 | Decided: a) close open setups at the 11:00 Chicago candle close | Your answer |
| 2026-09-25 | D14.3 | Decided: 30-minute cooldown after every outcome | Your answer |
| 2026-09-25 | D14.6 | Decided: a) nothing extra for opposite-direction setups | Your answer |
| 2026-09-25 | D14.11 | Added and decided: previous-setup rules reset each morning | Your answer |
| 2026-09-25 | D14.8 | Decided: max 2 filled setups per morning | Your answer |
| 2026-09-25 | D14.9 | Decided: same limit as D14.8 (one cap per morning) | Your answer |
| 2026-09-25 | D14.10 | Decided: a) same-direction setup after a stop allowed, from new events only | Your answer |
| 2026-09-25 | D14.12 | Added and decided: stop-out = full stop at a loss only | Your answer |
| 2026-09-25 | D1.3 | Decided: a) start + length preset (5/15/30/60 min). Current range: 08:00–08:15 Chicago | ★ accepted (Group 1) |
| 2026-09-25 | D1.6 | Decided: a) one configurable ORB | ★ accepted (Group 1) |
| 2026-09-25 | D3.1 | Decided: a) one candle close beyond the ORB level | ★ accepted (Group 1) |
| 2026-09-25 | D3.2 | Decided: a) first breakout per side only | ★ accepted (Group 1) |
| 2026-09-25 | D4.1 | Decided: a) confirmed breakout, then a close back inside the range within D4.2 | ★ accepted (Group 1) |
| 2026-09-25 | D4.2 | Decided: 15 minutes (3 candles on 5m) | ★ accepted (Group 1) |
| 2026-09-25 | D4.3 | Decided: a) recorded as an "ORB sweep" (liquidity event, separate from a false breakout) | ★ accepted (Group 1) |
| 2026-09-25 | D5.10–D5.12 | Added: target level list, EQH/EQL source layer, EQH/EQL lifetime | Gaps found while reviewing Group 2 |
| 2026-09-25 | D5.1 | Decided: PDH/PDL, Asia H/L, London H/L, EQH/EQL, ORB H/L can be swept to trigger setups. Raw swing points are excluded. | Group 2 answer |
| 2026-09-25 | D5.3 | Decided: 2 ticks minimum penetration | Group 2 answer |
| 2026-09-25 | D5.4 | Decided: a) same candle must close back (on 5m and 1m alike) | Group 2 answer |
| 2026-09-25 | D5.5 | Decided: c) sweep candle closes in the half of its range away from the level | Group 2 answer |
| 2026-09-25 | D5.6 | Decided: a) no maximum penetration | Group 2 answer |
| 2026-09-25 | D5.7 | Decided: 2 ticks touch tolerance | Group 2 answer |
| 2026-09-25 | D5.8 | Decided: c) larger of 4 ticks (1 pt) and 0.1 × ATR(14) | Group 2 answer |
| 2026-09-25 | D5.9 | Decided: a) a level is used up by its first sweep (and by a break) | Group 2 answer |
| 2026-09-25 | D5.10 | Decided: b) the D5.1 list plus untouched swing-layer highs/lows, the latter as targets only | Group 2 answer |
| 2026-09-25 | D5.11 | Decided: b) swing-layer points | Group 2 answer |
| 2026-09-25 | D5.12 | Decided: b) active until swept or broken, whatever its age (limited in practice by loaded chart history) | Group 2 answer |
| 2026-09-25 | D6.7–D6.8 | Added: which break types count as Event 2 for T1/T3 and T2 | Gap found while reviewing Group 3 |
| 2026-09-25 | D6.1 | Decided: 10 candles each side (swing layer) | Group 3 answer |
| 2026-09-25 | D6.2 | Decided: 3 candles each side (internal layer) | Group 3 answer |
| 2026-09-25 | D6.3 | Decided: a) candle close beyond the swing | Group 3 answer |
| 2026-09-25 | D6.5 | Decided: a) labelled BOS; cannot count as a CHoCH trigger | Group 3 answer |
| 2026-09-25 | D6.6 | Decided: a) the most recent confirmed opposite swing | Group 3 answer |
| 2026-09-25 | D6.7 | Decided: a) internal CHoCH only (the internal trend must flip) | Group 3 answer |
| 2026-09-25 | D6.8 | Decided: a) internal BOS only (the internal trend must already point in the breakout direction) | Group 3 answer |
| 2026-09-25 | D7.8, D8.5, D8.6 | Added: zone ✓ definition, own-move definition, trigger-candle gap timing; clarified D7.6, D8.3, D8.4 wording | Gaps found while reviewing Group 4 |
| 2026-09-25 | D7.1 | Decided: a) the last opposite-colored candle before the displacement | Group 4 answer |
| 2026-09-25 | D7.2 | Decided: k = 1.5 (body ≥ 1.5 × ATR(14)) | Group 4 answer |
| 2026-09-25 | D7.4 | Decided: a) full base candle range (wick to wick) | Group 4 answer |
| 2026-09-25 | D7.5 | Decided: a) candle closes beyond the far edge | Group 4 answer |
| 2026-09-25 | D7.6 | Decided: 2 tests. A test = price trades into the zone, then a candle closes back outside it on the original side. | Group 4 answer |
| 2026-09-25 | D7.7 | Decided: 2 zones shown per side (display only) | Group 4 answer |
| 2026-09-25 | D7.8 | Decided: c) either: the stop-anchor point (setup origin) is inside an active zone of the setup direction, or the Model B limit entry is inside one | Group 4 answer |
| 2026-09-25 | D8.1 | Decided: c) larger of 2 points and 0.25 × ATR(14) | Group 4 answer |
| 2026-09-25 | D8.2 | Decided: a) price trades through the far edge | Group 4 answer |
| 2026-09-25 | D8.3 | Decided: 3 open FVGs shown per side (display only; the active setup FVG is always shown) | Group 4 answer |
| 2026-09-25 | D8.4 | Decided: a) only an FVG created by the setup's own move (for confluence and the Model B entry) | Group 4 answer |
| 2026-09-25 | D8.5 | Decided: The candles from the stop-anchor point (sweep extreme for T1/T3, BOS-origin swing for T2) up to and including the trigger candle | Group 4 answer |
| 2026-09-25 | D8.6 | Decided: b) usable: wait one more candle for the trigger candle's gap to confirm, then place the limit and run the stop/R:R checks (once). No gap and no earlier gap: rejected ("no FVG"). | Group 4 answer |
| 2026-09-25 | D9.13 | Added: definition of "at a different key level" | Gap found while reviewing Group 5 |
| 2026-09-25 | D9.2 | Decided: 50 minutes maximum between the two core events | Group 5 answer |
| 2026-09-25 | D9.3 | Decided: a) all attach and are used up; stop beyond the most extreme sweep | Group 5 answer |
| 2026-09-25 | D9.4 | Decided: a) at least one location item required (zone, FVG or key level). With Model B the FVG always meets it, so M = 1 needs bias, zone or a different key level. | Group 5 answer |
| 2026-09-25 | D9.5 | Decided: a) hard filter: the trigger candle must close inside NY AM (08:30–11:00 Chicago) | Group 5 answer |
| 2026-09-25 | D9.10 | Decided: a) labelled as the more specific type (T3) | Group 5 answer |
| 2026-09-25 | D10.1 | Decided: a) one model per chart, chosen in settings (default B) | Group 5 answer |
| 2026-09-25 | D10.3 | Decided: a) no extra requirement on the Model A trigger candle | Group 5 answer |
| 2026-09-25 | D10.5 | Decided: a) setup rejected ("no FVG"), no fallback level | Group 5 answer |
| 2026-09-25 | D10.6 | Decided: b) trade through the limit by ≥ 1 tick | Group 5 answer |
| 2026-09-25 | D10.8 | Decided: a) setup ends as MISSED when TP1 is reached before a fill | Group 5 answer |
| 2026-09-25 | D10.9 | Decided: Accepted: conservative same-candle conventions in entry_models.md §4 | Group 5 answer |
| 2026-09-25 | D9.13 | Decided: c) either the stop-anchor point or the limit entry is within the D5.8 tolerance of another D5.1-list level; swept or broken levels still count | Group 5 answer |
