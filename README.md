# NQ.ORB

A TradingView indicator for **NQ / MNQ intraday trading**, built around an **08:00
Chicago opening range**. It combines market structure, liquidity, supply & demand, fair
value gaps and sessions into a small number of rule-based setups, each with an entry,
stop, targets and status.

It shows **conditions that are present**. It never claims a setup is profitable or "high
probability", and it has no scores, win rates or AI ratings.

> **Status: Phase 0 (project setup) complete, version 0.0.0.** The indicator in `dist/`
> is currently only a *pipeline check*: it proves the build-to-TradingView workflow and
> contains no trading logic yet. See [the development plan](docs/PLAN.md) for the phases.

## Install in TradingView

1. Open [`dist/NQ_ORB.pine`](dist/NQ_ORB.pine) on GitHub, click **Raw**, and copy everything.
2. In TradingView, open an `NQ1!` or `MNQ1!` chart, then the **Pine Editor** tab at the bottom.
3. Replace the editor's contents with what you copied, click **Save** (name it `NQ.ORB`),
   then click **Add to chart**.
4. **To update later:** open the saved script, paste the new version over it and save.

Only ever copy from `dist/`. Those files are generated. Never edit them by hand.

## Documents

| Document | What it contains |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | Architecture, phases, anti-repainting rules |
| [docs/rules/SUMMARY.md](docs/rules/SUMMARY.md) | **The complete trading rules on one page** |
| [docs/rules/DECISIONS.md](docs/rules/DECISIONS.md) | Every trading decision and its change log |
| [docs/rules/](docs/rules/) | Detailed rulebooks (confluence, setup lifecycle, entry models) |
| [docs/TESTING.md](docs/TESTING.md) | Test levels, self-test catalogue, results log |
| [docs/DESIGN.md](docs/DESIGN.md) | Colors, visual hierarchy, labels, dashboard, clutter budget |
| [CHANGELOG.md](CHANGELOG.md) | What changed in each version |

## Repository layout

```
src/core/        shared building blocks (from Phase 1)
src/modules/     one file per component (sessions, ORB, structure, …)
tests/           self-test indicators (scripted candles → PASS/FAIL table)
tools/           build.py (joins modules), lint.py (repaint checks), their tests
dist/            generated TradingView scripts: the only files you copy
build.toml       which modules go into which script
VERSION          current version
```

TradingView needs one self-contained file per indicator, so the modules in `src/` are
joined by `tools/build.py` into files in `dist/`. Each module declares what it needs with
a header like `// @requires core/types`.

## Development commands

These need Python 3.11 or newer, with no extra packages.

```
python tools/build.py                          # regenerate dist/ from src/ and tests/
python tools/build.py --check                  # verify dist/ is up to date
python tools/lint.py                           # repaint and safety checks
python -m unittest discover -s tools/tests     # tests for the tools themselves
```

The same three checks run automatically on GitHub for every push (the ✓ / ✗ next to
each commit).

**Ground rules**
- Every trading rule must trace to an entry in `docs/rules/DECISIONS.md`. Undecided rules
  are asked about, never assumed.
- Never edit `dist/` by hand.
- A lint rule can only be waived on one line with a written reason:
  `// lint-allow: L00X reason`.

## Disclaimer

This is a charting tool, not financial advice. Futures trading involves substantial risk
of loss.
