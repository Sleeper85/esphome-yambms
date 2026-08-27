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

Two problems with that shape:

- **The formula was hardcoded per phase.** Each new correction had to be wired into the right
  branch by hand, and a phase that had never needed one had no slot to receive it.
- **`Stop` requested `Rebulk V.` itself**, which left the pack sitting on the very threshold that
  decides when to rebulk.

The controller itself matched that Bulk-only scope: its reference (`CVL`, `CVL_orig`) and deadband
reference (`cell_bulk_v`) were anchored to `bulk_voltage`, its ceiling to `bulk_voltage + boost`,
its floor to `float_voltage`.

## Design decisions

Each was validated against one hard invariant: **Bulk's observable behavior must not change**
unless explicitly stated otherwise.

1. **The core formula becomes a base plus offsets.** `yambms_core.yaml` now picks a per-phase base
   target and adds a common set of offsets to it, instead of carrying a separate formula per
   branch. Every phase now has a slot for every correction; an offset is simply `0` when its
   function is idle or disabled.

2. **`Stop` is anchored to nominal voltage** (`cell_count × var_cell_nominal_v`) instead of
   `Rebulk V.`, giving it a target that is independent of the rebulk decision instead of one that
   sits exactly on it.

3. **`Auto CVL` is rewritten from a per-second template sensor into an interval lambda.** The
   1.7.0 version was a `lambda:` returning a value inside a single `internal: true` sensor, so the
   correction and the published value were necessarily the same thing. Separating them is what
   allows the two user-visible diagnostic sensors below, and gives the file room for the per-phase
   branching.

4. **Phase source of truth**: read the existing `yambms${id}_charging_instruction` text sensor
   (already published by `yambms_core.yaml`, values `"Bulk"` / `"Float"` / `"Stop"`) instead of
   duplicating the `charge_status` → phase classification logic in this file.

5. **Bulk** (kept close to identical): still tracks `max_cell_v` against `bulk_voltage`, still
   uses the BMS `Balance Trig. Volt.` as deadband. One deliberate change: the floor moved from
   `float_voltage` (a user-configurable entity, not guaranteed to sit below `bulk_voltage`) to
   `cell_count × var_cell_min_charge_v` (the chemistry's fixed cv_min — "fully charged at rest"
   voltage). In practice this floor is rarely reached (the loop normally self-limits once
   `max_cell_v` drops back under `cell_bulk_v`, well before hitting either floor), so the
   observable difference is confined to edge cases where the correction saturates.

6. **PI state is reset when crossing the Bulk ↔ Float/Stop boundary.** Bulk uses `integral_bulk`;
   a second state, `integral_avg`, is reserved for the Float/Stop correction and is currently only
   ever zeroed. Carrying state across the Bulk boundary is not meaningful: the measured quantity
   itself changes nature at that transition, so an accumulated integral from one phase does not
   represent a valid correction for the other. Without the reset, a stale integral from before a
   Float cycle would be re-injected on the next rebulk. Turning the `Automatic Charge Voltage`
   switch off also clears both PI states entirely.

7. **NaN / availability guards are branch-specific**: only `cell_count`, `bulk_voltage` and the
   `charging_instruction` state are required upfront (common to all phases). `balance_delta` and
   `max_cell_v` are only required to enter the Bulk branch. This keeps a sensor hiccup on one
   branch's inputs from silently disabling another phase's correction — which would have broken
   the Bulk invariant in that edge case.

## Auto CVL outside Bulk : implemented, then suspended

Some inverters hold their output voltage a bit above (~0.1–0.3 V) the requested `CVL`, and they do
so in every phase, not just Bulk. That was the case for extending `Auto CVL` to `Float` and
`Stop`, and a full PI branch for them was written and tested. **It is suspended in the shipped
version**, and the reason is worth recording, because the failure is not obvious from the idea.

Outside Bulk, a real inverter overshoot, a pack relaxing after charge, and a pack discharging into
house load all present the **same signature**: pack average above target at near-zero current. No
function of pack current tells them apart — a fixed overshoot settles at ~0 A just like a resting
pack does. Left active, the PI integrates against an error it has no authority over and pins `CVL`
to its floor, burning the safety margin above `Rebulk V.` for no benefit.

`Stop` is a separate case: it means "let the pack discharge down to rebulk", which the low base
target now set by `yambms_core.yaml` (decision 2 above) achieves on its own. A PI loop has nothing
to add there, and `Stop` is not expected to come back even if `Float` does.

`Bulk` — the `OVP` protection path, and the reason `Auto CVL` exists — is untouched by this. The
`Float`/`Stop` slot of the new core formula stays free for a future implementation, and the
`integral_avg` PI state and the `auto_cvl_rebulk_margin_v` substitution are kept in place for it.

> [!NOTE]
> `auto_cvl_rebulk_margin_v` (default `0.5`) is declared but **has no effect** in the current
> version. It was the Float branch's safety margin above `Rebulk V.`: any fixed floor can sit at
> or below the rebulk threshold depending on the user's settings, which would let `Auto CVL`
> trigger a rebulk it caused itself and loop `Float → Bulk → Float`. Deriving the floor from the
> live `Rebulk V.` entity is what keeps that margin correct whatever the configuration.

## Result

| Phase | Base target (`yambms_core.yaml`) | Auto CVL correction |
|---|---|---|
| Bulk | `bulk_voltage` | `max_cell_v` vs `bulk_voltage`, deadband `balance_trigger_voltage`, floor `cell_count × var_cell_min_charge_v`, ceiling `bulk_voltage + boost` |
| Float | `float_voltage` | none (`var_auto_cvl` = `0`) |
| Stop | `cell_count × var_cell_nominal_v` | none (`var_auto_cvl` = `0`) |

`yambms_core.yaml` builds the requested voltage from that per-phase base plus a common set of
offsets, instead of a separate formula per branch:

```
base   : Bulk -> bulk_voltage | Float -> float_voltage | Stop -> cell_count × nominal_v
result : base + charger_offset + var_auto_cvl + var_auto_float + var_auto_custom_cvl
```

Each offset is `0` when its function is idle or disabled.

### New entities

Two diagnostic sensors expose the two halves of the charge voltage setpoint, so a misbehaving
correction can be read directly from the dashboard instead of being inferred:

- **`Auto CVL Delta`** — the correction `Auto CVL` is currently applying. Negative when it is
  reducing the charge voltage, `0` when idle — which includes the whole of `Float` and `Stop`.
- **`Auto Float Voltage Delta`** — the remaining offset of the `Auto Float` glide above the
  target float voltage. Reaches `0` once the ramp is complete.

Alongside them, `Auto CVL` and `Auto Float Voltage` publish the absolute value each function is
requesting. Outside `Bulk`, `Auto CVL` sits at `Bulk Voltage` with a delta of `0`.

Together the two deltas reconstruct the setpoint published by `yambms_core.yaml`:

```
Requested Charge Voltage = base target + Charger Offset V. + Auto Float Delta + Auto CVL Delta
```

Documentation updated in the same change: `documents/README/YamBMS_functions.md`, `Auto CVL`
section.
