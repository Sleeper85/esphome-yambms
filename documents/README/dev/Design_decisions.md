# Design decisions

Some parts of the codebase look more verbose or more redundant than they need to be. They are
deliberate. This page records why, so that a well-intentioned cleanup doesn't reintroduce a bug
that took a long time to find.

**Do not refactor anything listed here without discussing it first**, and read the rationale
before touching the code.

## Cut-Off / EOC logic

**File:** `packages/yambms/yambms_core.yaml`

The End Of Charge condition is deliberately compound. It has to distinguish a genuine EOC from a
charge current that is merely capped by low solar production. Collapsing it into a single
threshold or voltage comparison reintroduces false EOC on overcast days.

<!-- TODO maintainer: list the exact elements that must not be merged (timer, latched state,
compound conditions) — see v1.7.1. -->

## The combiner pipeline

**Files:** `packages/bms/bms_combine.yaml`, `packages/shunt/shunt_combine.yaml`,
`packages/yambms/yambms_core.yaml`

Every BMS and Shunt package instance runs the *same* interval lambda, and they coordinate through
a shared counter rather than through any central loop. Each instance only acts on the tick where
`var_to_combine_bms_number` equals its own `${bms_id}`, then increments the counter so the next
instance can run. `yambms_core.yaml` (STEP 2) waits until every device has been processed, then
resets the counters to `1` for the next round.

This is why `bms_id` **must start at 1 and be contiguous**. It is not a style rule and not only
about the bitmask index: with a gap in the numbering, the counter stops at the missing id, never
advances, and STEP 2 never fires. The whole pipeline deadlocks silently.

Include the BMS and Shunt packages in ascending id order. Out-of-order includes still converge,
but spread one round over several intervals instead of completing in one.

### `can_be_combined` is deliberately exhaustive

The condition in `bms_combine.yaml` checks every sensor the combiner will read. It is long on
purpose: a single missing or `NaN` value entering the totals corrupts the aggregate that drives
the inverter. Do not shorten it to a few representative checks.

Note that the checks are not uniform. Most use `has_state()`, but `total_voltage`,
`battery_capacity`, `max_charge_current` and `max_discharge_current` use `> 0` — a BMS reporting
zero for those is treated as not ready rather than as a valid reading.

### Combined once, combined continuously, uncombined

Three distinct scopes in the same lambda, and they are not interchangeable:

- **Once** — `total_installed_battery_capacity` accumulates a single time per BMS, for the
  lifetime of the boot. It represents the *installed* capacity and deliberately does not shrink
  when a BMS drops offline.
- **Not continuously** — the combined counter is incremented on the transition into the combined
  state, not on every tick.
- **Continuously** — the totals, bitmasks and min/max values are recomputed every round.

### `bms_seen_online_bitmask` is never cleared

It records that a BMS has been online at least once since boot. `shunt_combine.yaml` uses it to
tell "this BMS is offline" apart from "this BMS was never there" — a shunt must not be
uncombined because of a BMS the user never installed.

### Cell numbers are offset per pack

The combiner reports `cell number + (${bms_id} × 100)`, so cell 8 of BMS 1 is reported as `108`
and cell 3 of BMS 2 as `203`. This makes the pack immediately identifiable in the dashboard. It
caps a pack at 99 cells, which is well beyond any realistic configuration.

### A shunt uncombine turns the user switch off, and does not turn it back on

When a BMS mapped to a shunt goes offline, `shunt_combine.yaml` switches `Combine enabled` off
and records which BMS caused it, so the diagnostic `State` entity can say so. Re-enabling is
deliberately manual: coming back online does not automatically restore the combination, because
the SoC reference has to be trusted before it is used again.

### The `{0}` sentinel in `bms_ids`

`shunt${shunt_id}_bms_map` defaults to `'{0}'` because the vector needs a non-empty initialiser,
and the loop skips id `0` (`if (!bms_id) continue;`). Do not "clean up" the zero — it is what
makes an unmapped shunt valid.

## CAN frame catalogue

**File:** `packages/yambms/yambms_canbus.yaml`

Several `can_id` values are reused with different payloads depending on the protocol:

| CAN ID | Frame | Protocol |
|---|---|---|
| `0x359` | 5 | PYLON |
| `0x359` | 24 | Deye PCS |
| `0x371` | 11 | SEPLOS |
| `0x371` | 28 | Deye PCS |

**A frame's identity is its internal frame number, never its CAN ID.** Do not merge two blocks
because they share a CAN ID — that would break both protocols at once.

Byte order is not uniform either: `0x373` sends min cell voltage before max, `0x361` sends max
before min. Both match their respective specifications. Do not "harmonise" them.

## Frame sequencing

**File:** `packages/yambms/yambms_canbus.yaml`

Each protocol is defined as a sequence of frame numbers emitted on a fixed interval, so a full
cycle lasts `interval × sequence length` — from a few hundred milliseconds to over a second
depending on the protocol. Some inverters are sensitive to that cadence. Do not change the
interval to make protocols "consistent" with each other.

When adding a frame to a sequence, remember that the sequence length is tracked alongside the
array. Keep the two in sync, or the new frame will silently never be emitted.

## The update service must never block the loop task

**File:** `packages/yambms/yambms_service.yaml`

`http_request` runs synchronously on the ESP32 loop task. ESPHome arms the IDF task watchdog at
5s with `CONFIG_ESP_TASK_WDT_PANIC=y`, and feeds it at most every 1 s, so any single blocking
call has a **4s budget** before the device panics and reboots.

Two paths exceed that budget on a network that filters outbound traffic. Both were reproduced on
an OPNsense firewall and measured on hardware:

| Path | Blocking time | Bounded by |
|---|---|---|
| Port 80 dropped silently | 4.5s | `timeout`, whose ESPHome default is 4.5s |
| Port 53 filtered (drop **or** reject) | 7.0 s, fixed | nothing — `timeout` does not cover DNS |

The 7s figure is the lwIP resolver retry ladder (`1 + 1 + 2 + 3`s over `DNS_MAX_RETRIES`), and
it is deterministic to a few milliseconds. A reject is not faster than a drop: lwIP's UDP API has
no error callback, so the ICMP unreachable is counted and discarded, and the query still runs its
full budget. Only an actual DNS *answer* — including `NXDOMAIN` from a local resolver — fails fast.

This is why three separate settings are needed, and none of them is redundant:

- **`watchdog_timeout: 60s`** is the only thing that covers the DNS wait. It is never reached in
  normal operation, where a full request takes under 400 ms.
- **`timeout: 3s`** brings the socket phase back under the 4s budget. It does **not** help the
  DNS case.
- **The failure counter** (`yambms${yambms_id}_var_service_failures`) is what stops the loop from
  freezing for 7s every 6h, forever, on a device that will never reach the internet.

`my_network.is_connected()` is not a reachability test — it only proves the device holds an IP.
It is kept as a cheap first filter, but the counter is the real guard. Do not remove it on the
grounds that the connectivity check above it "already handles this".

The counter is incremented from `on_error`, which fires only when no connection could be made.
An HTTP error status still fires `on_response` and resets the counter, which is correct: the
network worked, so there is no freeze to protect against.

The POST is guarded by an `if` on the counter rather than nested inside the GET's `on_response`.
Nesting would stack one blocking request inside another on a loop task whose stack is 8192 B by
default — see [LOOP_TASK_STACK.md](../LOOP_TASK_STACK.md). It also avoids a second 7s freeze on
a filtered network, halving the worst case.

Reaching 3 failures disables the service until reboot, or until the user toggles the
`Update service` switch off and on, which rearms the counter.

## Empirical constants

Some constants were found by trial on real hardware and must not be rounded or harmonised.

<!-- TODO maintainer: list them here, in the form "do not lower <value> below <threshold>, or
<symptom>" — at minimum loop_task_stack_size, update intervals, RS485 timings. -->
