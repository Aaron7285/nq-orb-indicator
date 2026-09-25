# Changelog

Versions follow the phases in [docs/PLAN.md](docs/PLAN.md): each completed phase raises
the version. The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.1] — 2026-09-25

### Changed
- The version line moved to the bottom-left (it sat behind a TradingView icon) and now warns when the chart is in RTH mode, which hides the overnight candles the system needs.

### Confirmed
- Sessions self-tests: SESSIONS 13/13 PASS in TradingView.

## [0.2.0] — 2026-09-25 — Phase 2: sessions

### Added
- `modules/sessions_core`: session tracker (R1 membership, high/low/open per instance, completion and known-at time, most recent completed range per D15.4), plus drawing per DESIGN §6.6.
- `modules/sessions`: settings for the five sessions (HHMM, Chicago), drawing switches, and the NY AM tradeable filter (D9.5, D15.2).
- `dist/test/sessions_test.pine`: 13 scripted self-tests (SE-01 … SE-13).
- `docs/rules/sessions.md`.

### Confirmed
- Phase 1 core: CORE 31/31 PASS in TradingView.

## [0.1.0] — 2026-09-25 — Phase 1: core

### Added
- Core modules in `src/core/`:
  - `base`: Candle record, Chicago timezone
  - `time`: trading day C1, session windows R1, minute durations, supported timeframes
  - `price`: tick math, C9 limit rounding, Wilder ATR(14)
  - `levels`: level record and the touch/sweep/break engine, C2–C5, C7
  - `events`: event IDs and the daily store
  - `budget`: per-module drawing budgets
  - `theme`: dark/light palette from `DESIGN.md`
  - `status`: version line and untested-timeframe notice
  - `selftest`: the PASS/FAIL table framework
- `dist/test/core_test.pine`: 31 scripted self-tests (TESTING.md §3.1).
- Core rulebook `docs/rules/core.md`, approved with definitions C1–C9.

### Removed
- The Phase 0 pipeline-check placeholder.

## [0.0.0] — 2026-09-25 — Phase 0: project setup

### Added
- **Rules lock:** 104 trading decisions (`docs/rules/DECISIONS.md`), the one-page rule
  summary with derived definitions R1–R13 (`docs/rules/SUMMARY.md`), and the confluence,
  setup-lifecycle and entry-model rulebooks. All approved on 2026-09-25.
- `tools/build.py`: joins module files into single TradingView scripts in `dist/`, with
  dependency ordering, a generated header and a `--check` mode.
- `tools/lint.py`: repaint and safety checks (`varip`, `lookahead_on`, negative offsets,
  `timenow`, `barstate.isrealtime`, `request.security`, module headers, tabs).
- 32 self-tests for both tools (`tools/tests/`).
- A GitHub Actions workflow running the tool tests, lint and the build check on every push.
- `docs/DESIGN.md`: a validated color palette for dark and light charts, visual tiers,
  label rules, dashboard layout, display presets and clutter budget.
- `dist/NQ_ORB.pine`: a pipeline-check indicator (a status line only, **no trading logic**).
