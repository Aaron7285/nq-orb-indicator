# NQ.ORB — Development Plan

An NQ/MNQ intraday trading indicator for TradingView, built around an 08:00 Chicago opening range.

**Status:** Rules approved (2026-09-25; `docs/rules/SUMMARY.md`). Phases 0–2 complete (core 31/31, sessions 13/13 PASS in TradingView).
**Next: Phase 3 (opening range)**, rulebook `docs/rules/orb.md` awaiting approval.
**Architecture:** approved (modules + build tool), 2026-09-25.

---

## 1. What we're building

A professional TradingView indicator for NQ and MNQ intraday trading. The Opening Range
Breakout (ORB) is one component of a larger system:

| # | Component | What it does |
|---|---|---|
| 1 | Opening range | ORB high/low/midpoint, breakout and false-breakout detection |
| 2 | Market structure | Swing and internal structure, BOS, CHoCH, bullish/bearish state |
| 3 | Liquidity | PDH/PDL, previous session H/L, EQH/EQL, pools; touch vs sweep vs break |
| 4 | Supply & demand | A few meaningful, ranked zones that extend and get invalidated |
| 5 | Imbalance / FVG | Bullish/bearish FVGs, open vs filled, minimum-size filter |
| 6 | Sessions | Asia, London, New York, NY AM, NY PM, each switchable on/off |
| 7 | Confluence engine | A checklist of real, rule-based conditions: no scores |
| 8 | Setup lifecycle | Anti-spam state machine: one setup per event, cooldown, no flip-flopping |
| 9 | Trade plan | Two entry models, stop, TP1/TP2, R:R, invalidation, status |
| 10 | Risk calculator | Dollar risk, NQ and MNQ contract quantity (optional) |
| 11 | Dashboard | A compact real-time summary |
| 12 | Visual design | A dark, restrained, trading-terminal look |

## 2. Guiding principles

1. **No invented trading rules.** Every trading rule traces to an answered question in
   `DECISIONS.md`. If a rule isn't decided, Claude asks rather than assumes.
2. **Few, meaningful setups.** Defaults are strict. Signal count is never a goal.
3. **Events, not states.** Setups are triggered by things that happen once on a specific
   candle, never by conditions that stay true.
4. **Detectors report facts; only the setup engine creates setups.**
5. **No repainting and no lookahead** (§8).
6. **No claims.** No scores, probabilities, win rates or "high probability" wording.
7. **One subsystem at a time.** Each is defined, built, tested and reviewed on its own
   before it's integrated.

## 3. Architecture

### 3.1 Layers

```
          CORE: settings · shared types · time/tick/ATR math · event IDs
                level-interaction engine · drawing budget · self-test framework
                                         │
   Sessions · Opening Range · Structure · FVG · Liquidity · Supply & Demand
           (DETECTORS: report facts and events only; never decide trades)
                                         │
                    Bias + Confluence engine  (is there a qualifying setup?)
                                         │
                    Setup lifecycle engine    (may a setup form? what state is it in?)
                                         │
                    Trade plan  ──►  Risk calculator
                                         │
                Drawing · Dashboard · Alerts  (display only, no math)
```

### 3.2 Repository layout

```
nq-orb-indicator/
├── README.md, CHANGELOG.md
├── docs/
│   ├── PLAN.md                 this document
│   ├── TESTING.md              test levels, self-test catalogue, results log
│   ├── DESIGN.md               visual design system (Phase 0)
│   └── rules/
│       ├── DECISIONS.md        every trading decision, with a change log
│       ├── SUMMARY.md          the complete rule set on one page
│       ├── confluence.md       factor classes, setup types, qualification
│       ├── setup_lifecycle.md  states, anti-spam rules, cooldown
│       ├── entry_models.md     Model B (default), Model A, stops, targets, outcomes
│       └── <module>.md         one per detector, written at the start of its phase
├── src/
│   ├── core/                   shared types and helpers
│   └── modules/                one file per component
├── tests/                      self-test scripts (scripted candles/events → PASS/FAIL)
├── tools/
│   ├── build.py                joins src/ into single TradingView files
│   └── lint.py                 automatic repaint and safety checks
└── dist/                       ← the only folder you copy from into TradingView
    ├── NQ_ORB.pine             the full product (indicator name: NQ.ORB)
    └── test/                   one standalone test indicator per module
```

TradingView needs a single file and can't include other files. `build.py` joins the
module files in dependency order. The same tool builds **standalone test indicators**
(core + one module + its dependencies), so each subsystem can be tested on its own
without keeping duplicate copies of the code. A GitHub Actions check runs the build and
the lint on every push.

### 3.3 Module contract

- Each module file contains its own settings group, a **calculation** section and a
  **drawing** section.
- It keeps its results in one named container (e.g. `orb.high`, `structure.trend`).
- It reads only from modules above it, and never changes another module's results.
- Its logic is written as functions that receive candle data as inputs, which is what
  makes self-tests possible.
- It gets a **drawing budget**. TradingView allows at most 500 lines, 500 boxes and 500
  labels per script, and all modules share that limit.

### 3.4 Level-interaction engine (shared)

Every horizontal level (ORB high/low, PDH/PDL, session H/L, swing levels, EQH/EQL, zone
edges) is classified on each closed candle by the same rules. For a level above price
(the mirror applies below):

| Result | Rule |
|---|---|
| Touch | Price comes within the touch tolerance (D5.7) without the minimum penetration |
| Sweep / rejection | The wick goes through by ≥ the minimum penetration (D5.3) and closes back (D5.4), meeting the rejection filter (D5.5) |
| Break | The candle closes beyond the level |
| Failed break | A break, then a close back within N candles (D4, D5.4b) |

### 3.5 Events

Every detector reports **events** (sweep, BOS, CHoCH, ORB breakout, ORB false breakout,
FVG created, zone created). Each has a unique **event ID**: type + direction + level +
the time of the confirming candle. The confluence engine and the lifecycle engine work
only with events and their IDs. That's how "one setup per event" is enforced.

### 3.6 Self-tests

Each module has a test indicator that plays hand-made candle or event sequences with
known correct answers, and shows a **PASS/FAIL table** on any chart. This is the closest
TradingView gets to automatic testing. Claude can't run TradingView, so you run it and
send a screenshot.

## 4. Component rules

Each detector gets its own rulebook (`docs/rules/<module>.md`) at the start of its phase.
It's built only from decided answers:

| Component | Decisions |
|---|---|
| Opening range | D1, D3, D4 |
| Timeframes / account | D2 |
| Liquidity | D5 |
| Market structure | D6 |
| Supply & demand | D7 |
| FVG | D8 |
| Sessions | D15 |
| Confluence & bias | D9, see `rules/confluence.md` |
| Entry models, stops, targets | D10, D11, D12, see `rules/entry_models.md` |
| Invalidation, lifecycle | D13, D14, see `rules/setup_lifecycle.md` |

## 5. Confluence: core requirements (summary of `rules/confluence.md`)

- Factors belong to three classes: **Core events** (liquidity sweep, ORB sweep, ORB
  breakout, ORB false breakout, internal BOS, internal CHoCH), **Location** (FVG, zone,
  key level) and **Context** (session, bias, ORB position).
- **Context can never create a setup**, alone or together.
- Every setup needs **two core events in order**, the second within 50 minutes:
  - **T1 Sweep → internal CHoCH**
  - **T2 ORB Breakout → internal BOS**
  - **T3 ORB Failure → internal CHoCH**
- Setups form only in **NY AM (08:30–11:00 Chicago)**. At least one location item is
  required, plus **M = 1** further ✓ (bias, zone or a different key level).
- Counter-bias setups are allowed and **flagged**. The display is a ✓/✗ checklist of
  facts, never a score.

## 6. Setup lifecycle (summary of `rules/setup_lifecycle.md`)

- States: `ARMED → CANDIDATE → PENDING → ACTIVE → outcome → COOLDOWN → ARMED`; a failed
  check is `REJECTED` (logged, events used up, no cooldown).
- One live setup at a time. Events are used once, forever.
- A **30-minute cooldown** follows every outcome. Only events after it count.
- At most **2 filled setups per morning**. Everything resets daily.
- Price moving against a setup can only end it, never create the opposite setup.
- Every rule is covered by self-tests (LT-series in `TESTING.md`).

## 7. Entry models (summary of `rules/entry_models.md`)

- **Model B: Limit Retest (default).**
  - A limit at the 50 % level of the setup's own FVG, filled on a 1-tick trade-through.
  - It expires after 30 minutes, and ends as MISSED if TP1 comes first.
- **Model A: Close Confirmation** (setting). Entry at the trigger candle's close.
- **Stop:** 5–30 points. **TP1 / TP2:** the nearest and the next untouched liquidity
  levels, 2 ticks before each. Minimum R:R to TP1 is 1.0.
- After TP1, the stop moves to **breakeven**. Anything still open is closed at **11:00
  Chicago**.
- Conservative conventions apply to same-candle ambiguity (e.g. stop and target both hit
  is counted as stopped).

## 8. Anti-repainting and lookahead rules

1. Signals, events and state changes are evaluated on **closed candles only**.
2. Breakouts are based on the **close**, not a touch (D3.1).
3. The ORB is locked only when its window ends. No signals while it's forming.
4. No `lookahead_on`. v1 uses no data from other timeframes; all levels are built from
   the chart's own candles.
5. No `varip` in logic.
6. Fixed timezones (D1.2, D15.3), independent of your chart settings.
7. **Delayed confirmation is handled honestly.** Swings, zones and FVGs may be drawn at
   the candle where they formed, but the logic only uses them from their confirmation
   candle onward.
8. Conservative same-candle outcome rules (`entry_models.md` §4).
9. `lint.py` rejects: `varip`, `lookahead_on` outside one approved helper, negative plot
   offsets, `timenow` in logic, and logic that branches on `barstate.isrealtime`.

## 9. Visual design (full system in `DESIGN.md`)

- **Six colors:** teal (bullish), muted red (bearish), muted gold (the single accent, for
  the ORB and the active setup) and three grays. They're validated for contrast and
  color-blind separation on dark and light charts (`DESIGN.md` §2).
- **Tiers:**
  - Tier 1, act on it: the active setup's lines and the dashboard.
  - Tier 2, key levels: the ORB, PDH/PDL and top-ranked zones.
  - Tier 3, context: structure labels, FVGs, sessions, EQH/EQL. These are faint.
- **Line styles:** solid = active, dashed = pending or forming, dotted = reference.
- **Labels:** short tags, tiny text, no speech bubbles.
- Display presets (Minimal / Standard / Full), a hard clutter budget, and readable on
  light charts too.
- **Avoid:** neon, heavy gradients, glassmorphism, large labels, decorative elements.

## 10. Workflow for every component

1. **Define:** Claude drafts the module's rulebook from decided answers, and **you approve it**.
2. **Implement:** the module plus its standalone test indicator.
3. **Test:** levels L0–L8 in `TESTING.md`. **You run the TradingView steps.**
4. **Review:** Claude checks the code against the rulebook, you check the visuals, and
   findings are logged.
5. **Integrate:** the module is added to `dist/NQ_ORB.pine`, and the regression tests
   are re-run.

## 11. Phases

| Phase | Deliverable | Depends on | Gate |
|---|---|---|---|
| **R** | Rules lock: `DECISIONS.md`, `SUMMARY.md` and the rulebooks ✓ **done** | — | Approved 2026-09-25 |
| 0 | Tooling: build.py, lint.py, GitHub check, DESIGN.md, README ✓ **done (v0.0.0)** | R | Build + lint pass ✓ |
| 1 | Core: types, event IDs, time/tick/ATR helpers, level-interaction engine, drawing budget, self-test framework ✓ **done (v0.1.0)** | 0 | Core 31/31 PASS ✓ |
| 2 | Sessions ✓ **done (v0.2.x)** | 1 | SE 13/13 PASS ✓, visual ✓ |
| 3 | Opening range (breakout, false breakout, ORB sweep) | 2 | §10 |
| 4 | Market structure (swing + internal, BOS, CHoCH) | 1 | §10 |
| 5 | FVG | 1 | §10 |
| 6 | Liquidity (pools, touch / sweep / break) | 2, 4 | §10 |
| 7 | Supply & demand | 4, 5 | §10 |
| 8 | Bias + confluence engine (core gate, checklist) | 2–7 | §10 |
| 9 | **Setup lifecycle engine** (states, used events, cooldown, caps). Tested first with scripted events, then connected. | 8 | §10 + all LT tests pass |
| 10 | Trade plan: entry Models A and B, stops, targets, invalidation, outcomes | 9 | §10 + all EM tests pass |
| 11 | Risk calculator | 10 | §10 |
| 12 | Dashboard | all | §10 |
| 13 | Visual polish and display presets | all | Clutter budget met |
| 14 | Hardening: full edge-case, performance and regression pass; user guide | all | All levels pass |
| 15 | **v1.0 release**: merge to `main`, install in TradingView | 14 | You sign off |

Each phase ends with a version tag (v0.1, v0.2 …).

## 12. Out of scope for v1

- Scores, probabilities, win rates, "AI" ratings.
- Automated trading and backtesting (a separate strategy script could reuse the modules later).
- Data from higher timeframes (could be added later using the one linted safe pattern).

## 13. Risks

| Risk | Mitigation |
|---|---|
| TradingView script size and speed limits | Drawing budgets, capped object lists, dashboard updates only on the last candle, a performance test every phase. The build can split the system into two indicators if needed. |
| Drawing limit (500 each) shared by all modules | A per-module budget, enforced in the core |
| Limited 1-minute history on some plans | Checked against your plan (D2.3); previous-day levels need ≥ 2 days loaded |
| Your testing time | Self-tests reduce most checks to reading a PASS/FAIL table |

## 14. Getting it into TradingView

1. On GitHub, open `dist/NQ_ORB.pine` (or a file in `dist/test/`), click **Raw**, and copy everything.
2. In TradingView, open the **Pine Editor** at the bottom of the chart.
3. Paste over the default code, click **Save**, then **Add to chart**.
4. For updates, open the saved script, paste the new version and save again.
