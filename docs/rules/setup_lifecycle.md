# Rulebook — Setup Lifecycle & Anti-Signal-Spam (DRAFT)

**Status:** DRAFT. Parameters marked `Dx.y` are open in `DECISIONS.md`.
**Built in:** Phase 9 (its own module). **Depends on:** Core (event types), Confluence.

## 1. Purpose

The lifecycle engine controls when a setup may form, what state it is in, and when the
system may form another one. Its job is to make sure **one market event produces at most
one setup**, and that the indicator doesn't spam BUY/SELL signals or flip direction just
because price moved.

## 2. Fixed requirements (set by you; not open for change without your approval)

| ID | Requirement |
|---|---|
| LC-1 | One setup per qualifying structure/liquidity event. |
| LC-2 | Repeated candles that satisfy the same conditions can't create duplicate setups. |
| LC-3 | A setup can't flip from long to short (or short to long) just because price moves against it. |
| LC-4 | An opposite setup requires a **genuinely new** structure/liquidity event. |
| LC-5 | After invalidation or completion, the previous setup's triggering events can't be reused. |
| LC-6 | A configurable cooldown / new-context requirement exists. |
| LC-7 | All of the above are covered by self-tests (see `TESTING.md`, LT-series). |

## 3. Definitions

- **Event:** something a detector reports **once**, on the candle that confirms it
  (a sweep, a BOS, a CHoCH, an ORB breakout, an ORB false breakout). States such as
  "price is inside a zone" are **not** events.
- **Event ID:** a unique identity made of the event's type, direction, the level involved,
  and the time of the confirming candle. Two events are the same only if all four match.
- **Used event:** an event attached to any setup or rejected candidate. It can never
  qualify another setup, in either direction.
- **Re-arm time:** the moment after which new events become eligible (D14.4).
- **Live setup:** a setup in state `PENDING` or `ACTIVE`.

## 4. States

```
              core gate + all filters pass            Model A
   ARMED ────────────────────────────► QUALIFIED ────────────────► ACTIVE ──► TP1_HIT ──► TP2_HIT
     ▲  │                                  │                          ▲  ├──► STOPPED
     │  │ core gate passes,                │ Model B                  │  └──► CLOSED_WINDOW
     │  │ a filter fails                   ▼                          │
     │  └──► REJECTED (logged,          PENDING ────── fill ──────────┘
     │       events used, stays ARMED)     ├──► INVALIDATED
     │                                     ├──► EXPIRED
     │                                     └──► MISSED
     │
     └────────── COOLDOWN ◄────────── every terminal state
```

| State | Meaning | Leaves when |
|---|---|---|
| `ARMED` | Ready. No live setup, cooldown finished. | A core gate passes (§5) |
| `QUALIFIED` | Momentary: this candle qualified; the trade plan is fixed | Same candle: goes to `ACTIVE` (Model A) or `PENDING` (Model B) |
| `PENDING` | Model B only: waiting for the limit fill | Fill → `ACTIVE`; or `INVALIDATED` / `EXPIRED` / `MISSED` (D13.1, D10.7, D10.8) |
| `ACTIVE` | Entered | `STOPPED`, `TP1_HIT` (then per D12.4), `TP2_HIT`, `CLOSED_WINDOW` (D12.5). Nothing else, if D13.2 = a. |
| Terminal states | `TP2_HIT`, `STOPPED`, `INVALIDATED`, `EXPIRED`, `MISSED`, `CLOSED_WINDOW` (and TP1 or breakeven outcomes per D12.4) | Immediately → `COOLDOWN` |
| `COOLDOWN` | No new setups may form | When the cooldown finishes (D14.2/D14.3) → `ARMED`, with the re-arm time set |

`REJECTED` isn't a state the system stays in. It's a logged outcome: the candidate is
recorded with its reason, its events are used, and the state stays `ARMED`.

## 5. Rules that enforce LC-1 … LC-6

| Rule | Text | Enforces |
|---|---|---|
| L-1 | Setups are triggered only on the candle where a setup type's **final core event is confirmed**. Conditions that stay true on later candles trigger nothing. | LC-1, LC-2 |
| L-2 | Every event attached to a setup **or** a rejected candidate is marked **used**, permanently. | LC-1, LC-5 |
| L-3 | Only events confirmed after the **re-arm time** are eligible (D14.4). | LC-4, LC-5 |
| L-4 | At most **one live setup** at a time (D14.1). While a setup is live, no other setup can qualify in either direction. | LC-3 |
| L-5 | Price moving against a setup is **not** an event. It can only stop or invalidate the setup, which then enters cooldown. It can never create the opposite setup. | LC-3 |
| L-6 | The event that stopped or invalidated a setup is marked used (D14.5). | LC-4 |
| L-7 | An opposite-direction setup must also meet D14.6. | LC-4 |
| L-8 | Every terminal state is followed by `COOLDOWN` (D14.2/D14.3). | LC-6 |
| L-9 | Caps per session and per day (D14.8/D14.9). Same-direction setups after a stop: D14.10. | LC-6 |
| L-10 | A rejected candidate is evaluated **once** (D14.7). | LC-2 |

## 6. Where it is shown

- **Chart:** one small marker on the trigger candle (e.g. `L1` / `S1`, the setup number
  for the day) plus the entry, stop and target lines while the setup is live. Terminal
  setups fade to a faint reference style.
- **Dashboard:** the current state and plan, and (optionally) the last rejected candidate
  with its reason, e.g. `Rejected: R:R 0.8 < 1.0`.
- **Alerts:** one alert per state change (QUALIFIED, filled, TP1, TP2, STOPPED,
  INVALIDATED, EXPIRED, MISSED). Never repeated for the same setup and state.

## 7. Implementation notes (for Phase 9; not trading rules)

- The lifecycle engine is built and tested **before** it is connected to the real
  detectors. Its self-tests feed it scripted event sequences directly.
- Used events are tracked with a used flag on each event, plus the re-arm time.
- All transitions are evaluated on closed candles only (`barstate.isconfirmed`), so
  history, Bar Replay and live trading behave the same.
