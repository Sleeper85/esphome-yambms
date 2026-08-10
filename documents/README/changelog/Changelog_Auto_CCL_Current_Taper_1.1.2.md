# YamBMS - Changelog about new Auto CCL Current Taper (1.1.1 → 1.1.2)

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

`packages/yambms/yambms_auto_ccl_current_taper.yaml`

Changes applied after the code audit. None of them alter the taper curve itself or the
Cut-Off logic in `yambms_core.yaml`; they address pipeline contract, portability,
numerical robustness and configuration traps.

---

## 1. Pipeline contract — reset moved to the core

**Change:** the package no longer clears the pipeline variable in its early-exit branches.
`Gate #1` ("not our pipeline turn") is now a bare `return;` instead of a conditional
cleanup block.

**Why:** `yambms_core.yaml` now resets `var_auto_ccl_current_taper` at the start of every
Auto CCL cycle (before restarting the pipeline at step 1). Ownership of the variable
belongs to the core, which counts the functions, consumes the values and drives the step
counter. A contributor function has no reliable way to know whether it is the only writer
or whether the pipeline stalled — it can only clean up its own case.

**Resulting contract**, now documented in the file header: *a contributor function writes
its value on its own turn; staying silent (disabled, gated out, not its turn) is
equivalent to writing 0.* New contributed functions inherit the correct behavior without
defensive code.

> Note: the audit recommended the opposite — adding the variable write to Gates #2/#3.
> That was rejected in favour of the core-side reset.

**Core-side counterpart (`yambms_core.yaml`, block "Requested Charge Current (CCL)").** The
reset is placed after the sensor is published and before `var_charge_current_step = 1`, so
each cycle starts from a clean slate. All six variables of the `std::min` are reset
(`var_auto_temperature_ccl`, `var_auto_ccl`, `var_auto_ccl_current_taper`,
`var_auto_soc_limit`, `var_auto_eoc`, `var_auto_custom_ccl`): none of them is written by an
always-executed internal core block — the only write sites in the core are the reset lines
themselves, so they all originate from optional external packages. The globals are `float`,
`restore_value: no`, `initial_value: 0.0`, which is consistent with the reset at startup.

## 2. NaN guard on the inputs

**Change:** added before `Gate #3`:

```cpp
if (isnan(V_knee) || isnan(V_bulk) || isnan(V_pack)) { … }
```

**Why:** any comparison against NaN evaluates to false, so `Gate #3`
(`V_knee >= V_bulk - V_hyst`) does **not** block when `bulk_voltage` is still NaN — the
transient window before the `number` is restored at boot. Execution continued into the
`p = (V_pack - V_knee) / (V_bulk - V_knee)` division, and the only safety net was the
IEEE-754 behaviour of `fminf(0.0f, NaN)` returning `0.0f`. That is a fortunate C semantic,
not an explicit protection.

**Implementation note:** the guard does *not* simply `return` — it resets the session
latches, publishes a zero delta and **advances the pipeline step**. A bare `return` here
would have stalled the Auto CCL baton for the whole system on a transient NaN. This is a
deliberate improvement over the audit's proposed one-liner.

## 3. One-shot warning on a flat taper curve

**Change:** added a `flat_curve_warned` static flag, reset on each new session, guarding an
`ESP_LOGW` when `I_end >= I_anchor`.

**Why:** when `Bulk C-Rate >= Knee C-Rate` (or `>=` the effective CCL used as the left
anchor), the protective clamp `I_end = fminf(I_bulk, I_anchor)` makes the whole curve flat:
the function becomes a silent no-op — no error, no log, no visible effect. The clamp is
correct as a safety measure, but the configuration is a trap. The flag prevents the warning
from being emitted on every interval.

## 4. Release hysteresis scaled per cell

**Change:**

```diff
-constexpr float V_hyst = 0.2f;
+const float V_hyst = 0.0125f * ${yambms_cell_count};   // 0.2 V @ 16S
```

**Why:** `V_hyst` is a *pack* hysteresis. At 0.2 V it represents ~5 % of pack voltage on a
4S LTO pack (very wide release band) and ~0.26 % on a 24S LFP pack (very narrow, noise
sensitive despite the SMA). The per-cell form is portable and preserves the current
behaviour exactly on 16S — it is a reformulation of the existing constant, not a new
empirical value.

> `yambms_cell_hysteresis_v` from the core was deliberately **not** reused: it serves the
> discharge hysteresis of the Cut-Off logic and has a different purpose.

## 5. Balance Current bounds scaled with capacity

**Change:** the `Auto CCL CT Balance Current` maximum is now derived from the battery
capacity (0.1C ceiling, same order as `Bulk C-Rate`'s max) instead of a flat 0–50 A, with a
clamp of the stored value if it falls outside the window.

**Why:** unlike `knee_c_rate` / `bulk_c_rate`, this number was an absolute value. On a small
pack (e.g. 20 Ah) the UI allowed a 50 A "balance" current — 2.5C — physically meaningless
and not signalled to the user.

## 6. Balance Current vs the Cut-Off current deadband

**Change:** documentation comment added to the number.

**Why:** the Cut-Off logic in `yambms_core.yaml` ignores currents below
`yambms_current_deadband_crate × capacity` (0.005C, ≈1.4 A on a 280 Ah pack). Below that
threshold the compensated voltage criterion is no longer evaluated and charge termination
relies solely on the *fully charged at rest* signature. The default Balance Current of 2 A
is close to that limit on large packs.

This is the one real interaction between the taper and the Cut-Off logic, and it is a
configuration concern rather than a code defect.

## 7. Header contract updated

The `Contract with yambms_core.yaml` section now describes the actual behaviour: the
variable is written on the function's own turn only, and the core clears it every cycle.
