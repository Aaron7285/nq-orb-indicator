# NQ.ORB — Visual Design System

**Goal:** it should look like a premium trading terminal. Dark, restrained and precise,
where the most important thing on the chart is always the easiest to see.

**Status:** Phase 0 (approved plan §9). Every module follows this document. Visual
review is test level L6 in `TESTING.md`.

---

## 1. Principles

1. **Hierarchy over decoration.** Three visual tiers (§3). What you act on is strongest,
   and context is faint.
2. **Few colors, each with one job.** Three hues plus three grays. A hue never changes
   meaning within the same context (§2.4).
3. **Never color alone.** Direction is also shown by a glyph (▲ ▼) and a word; levels
   carry short text tags.
4. **Less is shown than is known.** Detectors track more than is drawn. Display limits
   and presets (§8, §9) keep the chart clean.
5. **Honest timing.** Objects appear on the candle where they were confirmed, never
   earlier (PLAN §8.7).

**Never:** neon or saturated colors, gradients, glass or blur effects, drop shadows,
large labels, speech-bubble labels, emoji, colored label backgrounds, full-chart
background painting, blinking, or decorative shapes.

## 2. Color tokens

### 2.1 Palette

The same hues are used in both themes. Light theme values are one step darker so they
keep contrast on a white chart.

| Token | Job | Dark theme | Light theme |
|---|---|---|---|
| `bull` | Bullish direction; the profit side of a trade plan | `#1BA995` | `#1B9786` |
| `bear` | Bearish direction; the loss side of a trade plan | `#B45C5E` | `#A05052` |
| `accent` | **Only** the ORB and the active setup's entry | `#B08E21` | `#B48630` |
| `ink.primary` | Main text, dashboard values | `#D1D4DC` | `#131722` |
| `ink.secondary` | Labels, dashboard row names, tier-2 lines | `#9598A1` | `#5D606B` |
| `ink.faint` | Tier-3 decoration only, **never text** | `#5D606B` | `#9598A1` |

Reference surfaces are TradingView's default backgrounds: dark `#131722`, light `#FFFFFF`.

### 2.2 Validation record

The hues were checked with the data-viz palette validator. The checks were run on all
pairs, because any two of these colors can appear next to each other on a chart.

| Theme | Lightness band | Chroma floor | Color-blind separation (worst pair) | Normal-vision separation (worst pair) | Contrast vs surface |
|---|---|---|---|---|---|
| Dark | pass | pass | pass, ΔE 9.0 (bull ↔ bear, deuteranopia) | pass, ΔE 16.0 (accent ↔ bear) | all ≥ 3:1 |
| Light | pass | pass | pass, ΔE 8.7 (bull ↔ bear, deuteranopia) | pass, ΔE 16.3 (accent ↔ bear) | all ≥ 3:1 |

**Ink contrast** (WCAG): primary 12.1 (dark) / 17.9 (light); secondary 6.2 / 6.3, which
passes 4.5:1 for text. Faint is 2.9 in both themes, so it's for decoration only.

**When colors change:** any change to §2.1 must be re-run through the validator and
recorded here.

### 2.3 Theme detection

The script picks the palette from the chart's own background, so no setting is needed:

```
dark theme  ⇔  0.299·R + 0.587·G + 0.114·B of chart.bg_color < 128
```

This is implemented once, in Phase 1 (core). Until then, the Phase 0 pipeline check
uses `chart.fg_color`, the chart's own text color, for its single line of text.

### 2.4 What each color means

- `bull` and `bear` mean **direction**: structure breaks, FVGs, zones, bias and setup
  direction.
- **Inside a trade plan** (§6.7), they mean profit and loss instead: target lines use
  `bull`, the stop line uses `bear`, whatever the trade's direction. This matches
  TradingView's own long/short position tool, which traders already know. The setup's
  direction is shown separately by its ▲/▼ marker and label.
- `accent` is reserved for the ORB and the active setup's entry line. Nothing else uses it.
- **All text uses ink tokens**, never `bull`/`bear`/`accent`. Direction in text is a
  colored glyph (▲ `bull` / ▼ `bear`) next to ink-colored words.

## 3. Visual hierarchy

| Tier | Purpose | Elements | Lines | Fills | Text |
|---|---|---|---|---|---|
| **1: act on it** | What a trader acts on now | Active setup (entry, stop, TP1, TP2, marker), dashboard | width 2, 0 % transparency | trade-plan bands 90 % | `size.small`, ink.primary |
| **2: key levels** | The morning's reference frame | ORB box and lines, PDH/PDL, Asia/London H/L, top-ranked zones | width 1, 25 % | ORB 92 %, zones 88 % | `size.small`, ink.secondary |
| **3: context** | Background structure | Structure breaks, FVGs, EQH/EQL, swing targets, sessions, finished setups | width 1, 60 % | FVG 90 %, sessions 96 % | `size.tiny`, ink.secondary |

Transparency is Pine's 0–100 scale: 0 = solid, 100 = invisible.

## 4. Line language

| Style | Meaning |
|---|---|
| **Solid** | Active and confirmed: a live level, a filled setup's lines |
| **Dashed** | Forming or pending: the ORB before 08:15, a pending Model B limit |
| **Dotted** | Reference or historical: the midpoint, swept or broken levels (briefly), finished setups |

Lines end at the current candle. They never extend infinitely unless the element is a
tier-1 line.

## 5. Labels and typography

- Labels are **text only** (`label.style_label_left` with a transparent background, or
  `label.style_none`), placed at the **right end** of their line.
- Sizes: `size.tiny` (tier 3) or `size.small` (tiers 1–2 and the dashboard). Nothing larger.
- Dashboard values and prices use `font.family_monospace` for a terminal look, with
  aligned digits.
- Prices use `format.mintick` (NQ ticks: .00 / .25 / .50 / .75).
- **Tags** (a maximum of about 12 characters):

| Element | Tag |
|---|---|
| ORB | `ORB H` · `ORB L` · `ORB M` |
| Previous day | `PDH` · `PDL` |
| Sessions | `AS H` · `AS L` (Asia) · `LO H` · `LO L` (London) |
| Equal highs/lows | `EQH` · `EQL` |
| Swing target | `SW H` · `SW L` |
| Structure | `iBOS` · `iCHoCH` (internal) · `BOS` · `CHoCH` (swing) |
| Liquidity events | `sweep` (tiny, on the swept level) |
| Setup marker | `▲ L1` · `▼ S2` (direction and the morning's setup number) |
| Trade plan | `LMT 21,432.50` · `SL …` · `TP1 …` · `TP2 …` |

FVGs and zones have no labels by default; their color and position say enough.

## 6. Element specifications

| # | Element | Specification |
|---|---|---|
| 6.1 | **ORB** | A box from 08:00 to 08:15, fill `accent` 92 %, border `accent` 60 % width 1 (dashed while forming, solid once locked). High and low lines extend to 11:00 (tier 2, `accent` 25 %); the midline is dotted `ink.secondary`. |
| 6.2 | **Liquidity levels** | Tier 2 for PDH/PDL and Asia/London H/L; tier 3 for EQH/EQL and swing targets. `ink.secondary` lines with a tag. When swept or broken: dotted for 30 minutes, then removed. |
| 6.3 | **Structure** | A dotted `bull`/`bear` connector (60 %) from the broken swing to the breaking candle, with the tag in `ink.secondary`. Internal breaks are tier 3, `size.tiny`. |
| 6.4 | **FVG** | A box with fill `bull`/`bear` at 90 % and no border. It extends right while open, and is removed when filled. The active setup's FVG gets a thin dotted 50 % line. |
| 6.5 | **Supply/demand zone** | A box with fill `bull` (demand) or `bear` (supply) at 88 %, and a border in the same color at 70 %. It extends right while active and is removed when invalidated or retired. |
| 6.6 | **Sessions** | By default, a faint dotted outline of each session's high/low range (tier 3) with a tiny tag at its start. An optional shade at 96 %. Never a full-height background. |
| 6.7 | **Active setup** | Entry (limit) line `accent` width 2 (dashed while pending, solid once filled); stop `bear` width 2; TP1/TP2 `bull` width 2; optional profit/loss bands at 90 %. The marker `▲ L1` / `▼ S1` sits on the trigger candle. |
| 6.8 | **Finished setups** | Everything fades to tier 3 dotted, and is removed after the morning in the Standard preset. |
| 6.9 | **Rejected candidates** | Not drawn on the chart. The dashboard only shows the most recent one and its reason. |

## 7. Dashboard

A compact two-column table (`label | value`). The position is a setting, top-right by
default.

```
 NQ.ORB                 ● ARMED
 Bias        ▲ bull   swing ▲ · VWAP ▲
 Session     NY AM    09:12
 ORB         15.25 pt · above
 Structure   int ▲ · swing ▼
 Liquidity   swept LO L 08:47 · next ▲ PDH
 Zone        demand 21,398–21,404
 FVG         ▲ open 21,431–21,434
 Setup       ▲ L1 · T1 · PENDING
 Entry       21,432.50
 Stop        21,418.25   14.25 pt
 TP1 / TP2   21,461.00 / 21,488.75
 R:R         2.00 / 3.95
 Risk        $500 · 1 NQ · 17 MNQ
 Rejected    09:02 R:R 0.8 < 1.0
```

- Row names use `ink.secondary`; values use `ink.primary` in monospace. The glyphs ▲ ▼
  are colored `bull` or `bear`.
- **Background:** a flat panel, `ink.primary` at 94 % over the chart, with no cell borders
  and a 1 px `ink.faint` frame. No gradients, no transparency effects.
- **Size:** `size.small`. The Risk and Rejected rows are optional settings.
- The table is updated **only on the last candle** (performance).

## 8. Display presets

| Element | Minimal | Standard (default) | Full |
|---|---|---|---|
| Active setup + dashboard | ✓ | ✓ | ✓ |
| ORB (today) | ✓ | ✓ | ✓ plus 2 previous days |
| PDH/PDL, Asia/London H/L | — | ✓ | ✓ |
| EQH/EQL, swing targets | — | nearest 1 per side | all within display range |
| Zones | — | ✓ (≤ 2/side) | ✓ (≤ 2/side) |
| FVGs | active setup's only | ✓ (≤ 3/side) | ✓ (≤ 3/side) |
| Structure labels | — | last 3 | last 8 |
| Sessions | — | outline | outline + shade |
| Finished setups today | — | faded | faded |

Every element also has its own on/off setting, which overrides the preset.

## 9. Clutter budget (checked in L6)

These are the maximum objects visible at once in the **Standard** preset on a 1m or 5m
chart:

| Element | Limit |
|---|---|
| ORB | 1 box + 3 lines + 3 tags |
| Reference levels | 8 lines + 8 tags |
| EQH/EQL + swing targets | 2 lines + 2 tags |
| Zones | 4 boxes |
| FVGs | 6 boxes |
| Structure | 3 connectors + 3 tags |
| Sessions | 4 lines + 2 tags |
| Active setup | 4 lines + 4 tags + 1 marker (+ 2 bands) |
| Finished setups | 2 markers |
| Dashboard | 1 table |
| **Total** | **≈ 60 objects**, most of them faint |

If an L6 screenshot shows more, or two tags overlapping, that's a failed visual test.

## 10. Accessibility

- The hues pass color-blind (protanopia/deuteranopia) separation in both themes (§2.2).
- Direction is always shown by a glyph and a word as well as color.
- Text contrast is ≥ 4.5:1 (ink.primary and ink.secondary). ink.faint is never used for text.
