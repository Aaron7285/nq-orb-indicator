# Rulebook — Setup Lifecycle & Anti-Signal-Spam

**Status:** approved 2026-09-25. Items marked *(derived)* were approved as R1–R13 in `SUMMARY.md` §9.
**Built in:** Phase 9 (its own module). **Depends on:** Core (event IDs), Confluence.
All times are **Chicago time**.

## 1. Purpose

The lifecycle engine controls when a setup may form, what state it is in, and when the
system may form another one. **One market event produces at most one setup.** The system
never spams signals and never flips direction just because price moved.

## 2. Fixed requirements (set by you)

| ID | Requirement |
|---|---|
| LC-1 | One setup per qualifying structure/liquidity event. |
| LC-2 | Repeated candles satisfying the same conditions can't create duplicate setups. |
| LC-3 | A setup can't flip long ↔ short just because price moves against it. |
| LC-4 | An opposite setup requires a genuinely new structure/liquidity event. |
| LC-5 | After invalidation or completion, the previous setup's triggering events can't be reused. |
| LC-6 | A configurable cooldown / new-context requirement exists. |
| LC-7 | All of the above are covered by self-tests (`TESTING.md`, LT-series). |

## 3. Definitions

- **Event:** something a detector reports once, on the candle that confirms it: a sweep,
  ORB sweep, ORB breakout, ORB false breakout, internal BOS or internal CHoCH. States such
  as "price is inside a zone" are not events.
- **Event ID:** type + direction + level + time of the confirming candle.
- **Used event:** an event attached to any setup or rejected candidate. It is used
  permanently, for both directions.
- **Re-arm time:** the end of the most recent cooldown. Only events confirmed **after** it
  are eligible (D14.4). At the start of each futures day (17:00) there is no previous setup,
  so every new event is eligible *(derived: daily reset point, D14.11)*.
- **Live setup:** a setup in state `CANDIDATE`, `PENDING` or `ACTIVE`. At most **one** at a
  time, either direction (D14.1).
- **Morning:** the NY AM session, 08:30–11:00.

## 4. States

```
              core gate passes                         (Model B default)
   ARMED ──────────────────► CANDIDATE ──checks pass──► PENDING ──fill──► ACTIVE ──TP1──► ACTIVE (stop at entry)
     ▲  ▲                      │  (0 or 1 candle,          │                │                 │
     │  │                      │   D8.6 wait)              ├─► EXPIRED     ├─► STOPPED        ├─► TP2_HIT
     │  └── REJECTED ◄─────────┘ checks fail               ├─► MISSED      └─► CLOSED_WINDOW  ├─► BREAKEVEN
     │     (logged, events used,                           ├─► INVALIDATED                    ├─► TP1_FINAL (no TP2)
     │      no cooldown)                                   └─► CLOSED_WINDOW (not filled)     └─► CLOSED_WINDOW
     │
     └──────────── COOLDOWN (30 min) ◄──────────── every terminal outcome
```

| State / outcome | Meaning | Decisions |
|---|---|---|
| `ARMED` | Ready: no live setup, no cooldown running | — |
| `CANDIDATE` | Core gate passed. Qualification checks run on this candle, or on the next one if waiting for the trigger candle's gap to confirm. | D8.6 |
| `REJECTED` | A check failed. The reason is logged, the events are used up, and the state returns to `ARMED` **without** a cooldown. | D14.7, D14.13 |
| `PENDING` | Model B limit placed; waiting for a fill | D10.2 |
| `ACTIVE` | Filled (or Model A: entered at the trigger close) | — |
| `EXPIRED` | No fill within **30 minutes** of the limit being placed | D10.7 |
| `MISSED` | TP1 reached before a fill | D10.8 |
| `INVALIDATED` | While pending, a candle closed beyond the stop level | D13.1 |
| `CLOSED_WINDOW` | Still pending or active at the close of the candle ending **11:00**. A pending setup is cancelled; an active one is closed at that candle's close. | D12.5, D13.1 |
| `STOPPED` | Stop hit before TP1: a full stop-out at a loss (the only outcome that counts as a stop-out) | D14.12 |
| `TP1` (not terminal) | TP1 hit; the stop moves to entry from the next candle | D12.4 |
| `BREAKEVEN` | Stopped at entry after TP1 | D12.4 |
| `TP2_HIT` | TP2 reached | D12.2 |
| `TP1_FINAL` | TP1 hit on a setup that has no TP2 | D12.2 |
| `COOLDOWN` | **30 minutes** after **every** terminal outcome, measured from the close of the candle where it happened. Then the state returns to `ARMED` and the re-arm time is set. | D14.2, D14.3 |

An **active** setup ends **only** by its stop, TP2, breakeven or the 11:00 close
(D13.2). A **pending** setup is not cancelled by structure breaks (D13.3). If the fill and
a cancellation happen on the same candle, the **fill counts first** (D13.4).

## 5. Rules that enforce LC-1 … LC-6

| Rule | Text | Enforces |
|---|---|---|
| L-1 | A setup can only start on the candle where a setup type's **final core event is confirmed**. Conditions that stay true on later candles trigger nothing. | LC-1, LC-2 |
| L-2 | Every event attached to a setup **or** a rejected candidate is marked **used**, permanently. | LC-1, LC-5 |
| L-3 | Only events confirmed **after the re-arm time** are eligible (D14.4). The event that stopped or cancelled a setup is therefore never eligible (D14.5). | LC-4, LC-5 |
| L-4 | At most **one live setup** at a time (D14.1). | LC-3 |
| L-5 | Price moving against a setup is **not** an event. It can only end the setup, which then enters cooldown. | LC-3 |
| L-6 | Opposite-direction setups need nothing beyond L-1 … L-5 (D14.6). | LC-4 |
| L-7 | Every terminal outcome is followed by a **30-minute cooldown** (D14.2, D14.3). | LC-6 |
| L-8 | At most **2 filled** setups per morning. Expired, missed and rejected setups don't count. Once 2 have filled, later candidates are REJECTED "cap". (D14.8, D14.9) | LC-6 |
| L-9 | A same-direction setup after a stop-out is allowed, built only from new events (D14.10). | LC-4 |
| L-10 | A rejected candidate is evaluated **once** and never re-checked (D14.7). | LC-2 |
| L-11 | "Previous setup" and the cap reset at the start of each futures day (D14.11). | — |

## 6. Where it is shown

- **Chart:**
  - A small marker on the trigger candle, labelled with the direction and the morning's
    setup number, e.g. `L1` or `S2`.
  - The limit, stop and target lines while the setup is live.
  - Finished setups fade to a faint reference style.
- **Dashboard:** the current state, the plan, and the last rejected candidate with its
  reason, e.g. `Rejected: R:R 0.8 < 1.0`.
- **Alerts:** one per state change (qualified/limit placed, filled, TP1, TP2, stopped,
  breakeven, expired, missed, invalidated, closed at 11:00). An alert is never repeated for
  the same setup and state.

## 7. Implementation notes (Phase 9; not trading rules)

- Built and tested **before** it's connected to real detectors, using scripted event
  sequences.
- Used events are tracked with a used flag on each event plus the re-arm time.
- All transitions are evaluated on closed candles only.
