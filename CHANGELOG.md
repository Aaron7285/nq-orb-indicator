# Changelog

Versions follow the phases in [docs/PLAN.md](docs/PLAN.md): each completed phase raises
the version. The format is based on [Keep a Changelog](https://keepachangelog.com/).

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
