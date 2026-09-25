# Rulebook — Sessions (Phase 2)

**Status:** implemented in v0.2.0. Built **only** from approved decisions (D15.1–D15.4, D9.5,
D5.2, R1, C1, C5, DESIGN §6.6). No new trading rules. The implementation choices in §5 don't
change trading behavior; they're listed so you can review them.
All times are **Chicago**.

## 1. Sessions

| Session | Default window | Role | Drawn by default |
|---|---|---|---|
| Asia | 19:00–23:00 | High/low become liquidity levels (Phase 6) | yes |
| London | 01:00–04:00 | High/low become liquidity levels (Phase 6) | yes |
| New York | 08:30–15:00 | Display and dashboard only | no |
| NY AM | 08:30–11:00 | **The only tradeable session** (D15.2, hard filter D9.5) | no |
| NY PM | 12:30–15:00 | Display and dashboard only | no |

All windows are editable in settings as HHMM in Chicago time (D15.1, D15.3).

## 2. Membership and instances

- A candle is **in** a session if it opens at or after the start and closes at or before the
  end (R1). Sessions may overlap: a 09:00 candle is in both New York and NY AM.
- An **instance** starts at the first candle inside the window. Its high, low and open are
  taken from candles inside the window only.
- It **completes** on the candle that closes exactly at the window end. If that candle
  doesn't exist (holiday, early close, data gap), it completes on the first candle after it.
- A completed range becomes **known at the close of its last candle inside the window** (for
  example 23:00 for Asia). From then on the core's C5 rule applies: the level can only be
  judged from the next candle.
- Each instance belongs to the trading day of its first candle (C1). So the 19:00 Asia
  session belongs to the next date.

## 3. Most recent range (D15.4)

Each session keeps **only the most recent completed** high/low/open, which is replaced when
the next instance completes. Phase 6 (Liquidity) turns the Asia and London ranges into levels.

## 4. Display (DESIGN §6.6)

- A faint dotted outline of each drawn session's high and low (tier 3, `ink.secondary` at
  60 %), plus a tiny tag at its start (`Asia`, `London`, …). An optional shade at 96 %.
- Updated only on closed candles, so there's no repainting.
- Drawings come from the `sessions` budget (40 lines, 20 labels, 20 boxes). The oldest days
  are deleted first.

## 5. Implementation choices (please review)

| # | Choice | Why |
|---|---|---|
| S1 | The on/off switches only affect **drawing**. Turning off a session never stops its range from being tracked, and never changes the NY AM trade filter. | Changing tracked levels or the filter would change trading rules, which were locked in the rules lock. |
| S2 | An instance first seen **after** its start time (the chart's history begins mid-session) is marked **partial**. Phase 6 will ask you whether partial ranges may become levels. | That's a trading decision, so it isn't made here. |
| S3 | The dashboard's "current session" wording is left to Phase 12. This module only reports each session's in/out state. | Display only. |

## 6. Self-tests

TESTING.md §3.4, SE-01 … SE-13, in `dist/test/sessions_test.pine`.
