# YamBMS - Changelog about new YamBMS 1.8.0 Auto CVL function

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Problem

`Auto CVL` is a PI controller that reduces the `Requested Charge Voltage (CVL)` sent to the
inverter when a cell voltage rises above target, to avoid tripping the BMS `OVP` alarm. Its
computation was hardcoded around `Bulk Voltage`:

- the PI's starting point / reference (`CVL`, `CVL_orig`) was always `bulk_voltage`;
- the deadband reference (`cell_bulk_v`) was always `bulk_voltage / cell_count`;
- the lower clamp (`min_CVL`) was always `float_voltage`;
- the upper clamp (`max_CVL`) was always `bulk_voltage + boost`.

However, `yambms_core.yaml` already adds the resulting offset (`var_auto_cvl`) to
`requested_charge_voltage` **unconditionally**, regardless of the charging phase (`Bulk`,
`Float`, or `Stop`). So the function was never actually gated to Bulk — it just computed a
Bulk-anchored correction that got silently applied during Float/Stop too, where the reference
values no longer made sense. Concretely: in `Stop` (target = nominal voltage, the lowest value
on the whole voltage scale), the old `min_CVL = float_voltage` floor sat *above* the actual
target, so any correction would have pulled the requested voltage *up* toward float voltage
instead of down — silently defeating the purpose of `Stop`.

Real-world motivation for fixing this: some inverters hold their output voltage a bit above
(~0.1–0.3 V) the requested `CVL`, in every phase, not just Bulk. `Auto CVL` needed to become a
general "help the pack respect whatever `requested_charge_voltage` currently is" function,
regardless of which phase produced that target.

## Design decisions

Reached iteratively, each validated against one hard invariant: **Bulk's observable behavior
must not change** unless explicitly agreed otherwise.

1. **Phase source of truth**: read the existing `yambms${id}_charging_instruction` text sensor
   (already published by `yambms_core.yaml`, values `"Bulk"`/`"Float"`/`"Stop"`) instead of
   duplicating the `charge_status` → phase classification logic in this file.

2. **Bulk** (kept close to identical): still tracks `max_cell_v` against `bulk_voltage`, still
   uses the BMS `Balance Trig. Volt.` as deadband. One deliberate change: the floor moved from
   `float_voltage` (a user-configurable entity, not guaranteed to sit below `bulk_voltage`) to
   `cell_count × var_cell_min_charge_v` (the chemistry's fixed cv_min — "fully charged at rest"
   voltage). In practice this floor is rarely reached (the loop normally self-limits once
   `max_cell_v` drops back under `cell_bulk_v`, well before hitting either floor), so the
   observable difference is confined to edge cases where the correction saturates.

3. **Float / Stop use a different metric**: `average_cell_v = total_voltage / cell_count`
   instead of `max_cell_v`. Rationale: the goal here is compensating a roughly-constant inverter
   overshoot (not protecting against a single runner cell), and the average is naturally
   smoother than a single-cell reading — so no deadband is needed; the correction reacts as soon
   as `average_cell_v` exceeds the target.

4. **Float / Stop are unidirectional**: the correction only ever pulls `CVL` down, never above
   target. Implemented by setting `max_CVL = target_v` — combined with the existing
   clamp-and-freeze anti-windup pattern (only commit the integral when not clamped), this
   naturally prevents any upward correction without needing a separate code path.

5. **Float's target tracks the live `Auto Float` glide, not the final `Float Voltage`**:
   `target_v = float_voltage + var_auto_float`. `yambms_auto_float.yaml` already ramps the
   effective CVL down from `bulk_voltage` to `float_voltage` over time on entering Float. If
   `Auto CVL` targeted the final `float_voltage` directly, it would see the pack still near bulk
   level during the ramp and start pulling `CVL` down aggressively — fighting the (deliberately
   paced) Auto Float ramp. Tracking the live glide value means `Auto CVL` only reacts to a real
   overshoot *beyond* whatever Auto Float currently requests.

6. **Per-phase floors, chained down the voltage ladder**:
   - Float floor = `cell_count × var_cell_nominal_v` (Stop's own target — never pull Float below
     what Stop would ask for anyway).
   - Stop floor = `cell_count × var_cell_max_discharge_v` — a chemistry constant that existed in
     `yambms_core.yaml` but was previously unused (commented `// Not used`). This gives `Stop` a
     real correction range below nominal voltage, comfortably above actual discharge cut-off, so
     a poorly-behaved inverter can't keep trickling current in even after charging has stopped.

7. **Two independent PI loops, not one shared state**: Bulk uses `integral_bulk` /
   `prev_integral_bulk`; Float and Stop share `integral_avg` / `prev_integral_avg` (they track
   the same metric — `average_cell_v` — so carrying state between them is meaningful). Carrying
   state from Bulk into Float/Stop would not be: the measured quantity itself changes nature
   (`max_cell_v` vs `average_cell_v`) at that transition, so an accumulated integral from one
   would not represent a valid correction for the other.

8. **NaN/availability guards are branch-specific**: only `cell_count`, `bulk_voltage`, and the
   `charging_instruction` state are required upfront (common to all phases). `balance_delta` /
   `max_cell_v` are only required to enter the Bulk branch; `float_voltage` / `total_voltage`
   are only required to enter the Float/Stop branch. This avoids a sensor hiccup on one branch's
   inputs (e.g. `total_voltage`, an aggregated BMS value more likely to be transiently
   unavailable than a restored config entity) silently disabling the other phase's correction —
   which would have broken the Bulk invariant in that edge case.

## Result

| Phase | Metric | Target (`target_v`) | Floor | Ceiling | Deadband |
|---|---|---|---|---|---|
| Bulk | `max_cell_v` | `bulk_voltage` | `cell_count × var_cell_min_charge_v` | `bulk_voltage + boost` | `balance_trigger_voltage` |
| Float | `average_cell_v` | `float_voltage + var_auto_float` | `cell_count × var_cell_nominal_v` | `target_v` | none |
| Stop | `average_cell_v` | `cell_count × var_cell_nominal_v` | `cell_count × var_cell_max_discharge_v` | `target_v` | none |

Documentation updated in the same change: `documents/README/YamBMS_functions.md`, `Auto CVL`
section.
