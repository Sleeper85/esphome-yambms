# YamBMS - Changelog about new YamBMS 1.8.0 Auto CVL function

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Problem

`Auto CVL` is a PI controller that reduces the `Requested Charge Voltage (CVL)` sent to the
inverter when cell voltage rises above target, to avoid tripping the BMS `OVP` alarm.

In 1.7.0 it was strictly a Bulk-phase function. `yambms_core.yaml` built the requested voltage
one branch per phase, and only the Bulk branch added the correction:

```
Bulk   : bulk_voltage   + charger_offset + var_auto_cvl
Float  : float_voltage  + charger_offset + var_auto_float
Stop   : rebulk_voltage + charger_offset
```

The controller itself matched that scope: its reference (`CVL`, `CVL_orig`) and deadband
reference (`cell_bulk_v`) were anchored to `bulk_voltage`, its ceiling to `bulk_voltage + boost`,
its floor to `float_voltage`.

The gap: **`Float` and `Stop` had no correction at all.** Some inverters hold their output
voltage a bit above (~0.1–0.3 V) the requested `CVL`, and they do so in every phase, not just
Bulk. Once charging is meant to taper or stop, an uncompensated overshoot keeps pushing current
into a pack that is already full — exactly when it is least wanted. `Auto CVL` therefore needed
to become a general "help the pack respect whatever `requested_charge_voltage` currently is"
function, regardless of which phase produced that target.

Extending it was not a matter of removing a phase check. Every reference the controller used was
a Bulk constant, and the metric that makes sense in Bulk (`max_cell_v`, protecting against a
single runner cell) is not the one that makes sense once the pack is full.

## Design decisions

Each was validated against one hard invariant: **Bulk's observable behavior must not change**
unless explicitly stated otherwise.

1. **Phase source of truth**: read the existing `yambms${id}_charging_instruction` text sensor
   (already published by `yambms_core.yaml`, values `"Bulk"` / `"Float"` / `"Stop"`) instead of
   duplicating the `charge_status` → phase classification logic in this file.

2. **Bulk** (kept close to identical): still tracks `max_cell_v` against `bulk_voltage`, still
   uses the BMS `Balance Trig. Volt.` as deadband. One deliberate change: the floor moved from
   `float_voltage` (a user-configurable entity, not guaranteed to sit below `bulk_voltage`) to
   `cell_count × var_cell_min_charge_v` (the chemistry's fixed cv_min — "fully charged at rest"
   voltage). In practice this floor is rarely reached (the loop normally self-limits once
   `max_cell_v` drops back under `cell_bulk_v`, well before hitting either floor), so the
   observable difference is confined to edge cases where the correction saturates.

3. **Float / Stop use a different metric**: `average_cell_v = total_voltage / cell_count`
   instead of `max_cell_v`. Rationale: the goal here is compensating a roughly constant inverter
   overshoot, not protecting against a single runner cell, and the average is naturally smoother
   than a single-cell reading — so no deadband is needed; the correction reacts as soon as
   `average_cell_v` exceeds the target.

4. **Float / Stop are unidirectional**: the correction only ever pulls `CVL` down, never above
   target. Implemented by setting `max_CVL = target_v`, and by clamping the integral term at `0`
   so it can never wind up positive — an upward correction is blocked by the ceiling anyway, and
   a lingering positive integral would only delay the reaction to the next real overshoot.

5. **Float's target tracks the live `Auto Float` glide, not the final `Float Voltage`**:
   `target_v = float_voltage + var_auto_float`. `yambms_auto_float.yaml` already ramps the
   effective CVL down from `bulk_voltage` to `float_voltage` over time on entering Float. If
   `Auto CVL` targeted the final `float_voltage` directly, it would see the pack still near bulk
   level during the ramp and start pulling `CVL` down aggressively — fighting the (deliberately
   paced) Auto Float ramp. Tracking the live glide value means `Auto CVL` only reacts to a real
   overshoot *beyond* whatever Auto Float currently requests.

6. **Float's floor is derived from `Rebulk V.`, not from a fixed voltage**:
   `min_CVL = Rebulk V. + ${auto_cvl_rebulk_margin_v}` (default margin 0.5 V).
   This is the single most important safety property of the Float branch. Any fixed floor —
   including `cell_count × var_cell_nominal_v`, which is exactly the lower bound of the
   `Rebulk V.` range — can sit *at or below* the rebulk threshold, depending on the user's
   settings. `Auto CVL` would then be able to pull the pack down far enough to satisfy
   `max_cell_v ≤ Rebulk V. / cell_count`, triggering a rebulk it caused itself and looping
   Float → Bulk → Float indefinitely. Deriving the floor from the actual `Rebulk V.` entity
   keeps that margin correct whatever the configuration. If `Rebulk V.` is unavailable, the
   floor falls back to `cell_count × var_cell_nominal_v`; if the Float target is already at or
   below the floor, the floor is clamped to the target so `Auto CVL` stays neutral rather than
   pushing the voltage back up.

7. **Stop's target moves from `Rebulk V.` to `cell_count × var_cell_nominal_v`**, and its floor
   becomes `cell_count × var_cell_max_discharge_v` — a chemistry constant that existed in
   `yambms_core.yaml` but was previously unused (commented `// Not used`).
   In 1.7.0, `Stop` requested `Rebulk V.` itself, which left the pack sitting on the very
   threshold that decides when to rebulk. Anchoring `Stop` to nominal voltage instead gives it a
   target that is independent of the rebulk decision, and a real correction range below it,
   comfortably above actual discharge cut-off — so a poorly-behaved inverter can't keep
   trickling current in after charging has stopped.

8. **Bounded anti-windup on the Float/Stop integral**: the integral is capped at
   `-(target_v - min_CVL) / ki`, i.e. at the correction the floor can actually deliver. Without
   this bound, a pack that stays above target while the CVL has no effect — an inverter
   substituting its own voltage target, for instance a Deye in ToU mode — winds the integral
   down without limit, and the CVL stays pinned to the floor long after the cause is gone.

9. **PI state is reset when crossing the Bulk ↔ Float/Stop boundary**. Bulk uses
   `integral_bulk`; Float and Stop share `integral_avg` (they track the same metric —
   `average_cell_v` — so carrying state between them is meaningful). Carrying state across the
   Bulk boundary is not: the measured quantity itself changes nature (`max_cell_v` vs
   `average_cell_v`) at that transition, so an accumulated integral from one phase does not
   represent a valid correction for the other. Without the reset, a stale integral from before a
   Float cycle would be re-injected on the next rebulk. Turning the `Automatic Charge Voltage`
   switch off also clears both PI states entirely.

10. **NaN / availability guards are branch-specific**: only `cell_count`, `bulk_voltage` and the
    `charging_instruction` state are required upfront (common to all phases). `balance_delta` and
    `max_cell_v` are only required to enter the Bulk branch; `float_voltage` and `total_voltage`
    only to enter the Float/Stop branch. This avoids a sensor hiccup on one branch's inputs (e.g.
    `total_voltage`, an aggregated BMS value more likely to be transiently unavailable than a
    restored config entity) silently disabling the other phase's correction — which would have
    broken the Bulk invariant in that edge case.

## Result

| Phase | Metric | Target (`target_v`) | Floor | Ceiling | Deadband |
|---|---|---|---|---|---|
| Bulk | `max_cell_v` | `bulk_voltage` | `cell_count × var_cell_min_charge_v` | `bulk_voltage + boost` | `balance_trigger_voltage` |
| Float | `average_cell_v` | `float_voltage + var_auto_float` | `Rebulk V. + rebulk margin` | `target_v` | none |
| Stop | `average_cell_v` | `cell_count × var_cell_nominal_v` | `cell_count × var_cell_max_discharge_v` | `target_v` | none |

`yambms_core.yaml` now builds the requested voltage from a per-phase base plus a common set of
offsets, instead of a separate formula per branch:

```
base   : Bulk -> bulk_voltage | Float -> float_voltage | Stop -> cell_count × nominal_v
result : base + charger_offset + var_auto_cvl + var_auto_float + var_auto_custom_cvl
```

Each offset is `0` when its function is idle or disabled, so the phases that used to receive no
correction now receive one only when it is actually enabled.

### New entities

Two diagnostic sensors expose the two halves of the charge voltage setpoint, so a misbehaving
correction can be read directly from the dashboard instead of being inferred:

- **`Auto CVL Delta`** — the correction `Auto CVL` is currently applying. Negative when it is
  reducing the charge voltage, `0` when idle.
- **`Auto Float Voltage Delta`** — the remaining offset of the `Auto Float` glide above the
  target float voltage. Reaches `0` once the ramp is complete.

Together they reconstruct the setpoint published by `yambms_core.yaml`:

```
Requested Charge Voltage = base target + Auto Float Delta + Auto CVL Delta
```

### New substitution

`auto_cvl_rebulk_margin_v` (default `0.5`) — safety margin kept above `Rebulk V.` by the Float
floor. It must exceed the spread between pack average and highest cell, otherwise `max_cell_v`
can reach the rebulk threshold while the average is still above the floor. Increase it on a
poorly balanced pack.

## Known limitations

- On entering `Float`, `Auto CVL` runs every second while `Auto Float` runs every 60 s. During
  that window `var_auto_float` is still `0`, so `Auto CVL` briefly targets `float_voltage`
  instead of the start of the glide. The requested voltage can dip for up to a minute before the
  glide takes over. To be addressed in `yambms_auto_float.yaml`.

Documentation updated in the same change: `documents/README/YamBMS_functions.md`, `Auto CVL`
section.
