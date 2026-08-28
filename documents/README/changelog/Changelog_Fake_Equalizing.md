# YamBMS - Changelog about the new Fake Equalizing

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

`packages/bms/bms_options_fake_equalizing.yaml`

Original idea by [@haysdb](https://github.com/haysdb), who reported the problem and
proposed a first implementation. The package shipped here is a much smaller rewrite of
that idea — see [Why not the original pull request](#why-not-the-original-pull-request)
at the end.

---

## 1. The problem

Several BMS balance their cells but never expose a balancing flag over their protocol.
The YamBMS packages for those BMS had no choice but to declare the flag as a constant:

```yaml
  # equalizing
  - platform: template
    id: bms${bms_id}_bms_equalizing
    lambda: return false;
```

That constant is not a neutral placeholder, it is a wrong value. Those packs *do*
balance, and `equalizing` is not a cosmetic entity: in `yambms_core.yaml`, while it is
true the **Cut-Off timer is stopped** and the charge is allowed to continue up to the EOC
timer. Reporting `false` during a real balancing phase means the charge is terminated
while the pack is still equalizing, cycle after cycle, and the user has no indication
that anything is wrong.

## 2. What the package does

It infers the flag from the pack itself, and — this is the part that matters — **it
hardcodes neither of the two references it needs**. Both are already in your
configuration.

**The voltage reference** is the per-cell bulk setpoint:

```cpp
cell_bulk_v = bulk_voltage / cell_count
```

the exact derivation `yambms_core.yaml` already uses for its own end-of-charge
comparison. It follows `yambms_battery_chemistry`, the cell count and the bulk voltage you
configured, with no per-chemistry constant to maintain. LFP, Li-ion and LTO work out of
the box.

**The spread reference** is `bms_balance_trigger_voltage` — the very spread at which your
pack's own balancer engages. That number is not a matter of taste, and it is not the same
from one BMS to the next: **10 mV on a JK or a Seplos, 30 mV on an EG4 LL v2**. A fixed
constant would have fitted none of them — it would have reported balancing on a pack whose
balancer is idle, or stayed silent on one that is working. `bms_base_balancer.yaml`
already resolves this value to the external balancer's setting whenever one is online, and
to the BMS's own otherwise.

A pack that reports no trigger voltage at all never starts. There is no basis to claim it
is balancing, and no threshold worth inventing for it: the inference simply stays out of
the way and the behaviour is the one you have today.

```
  START when BOTH are true
    max cell >= cell_bulk_v                     the pack is at the setpoint
    AND (max - min) >= trigger voltage          its own balancing threshold

  STOP when EITHER is true
    max cell <  cell_bulk_v - hysteresis        the pack dropped off the setpoint
    OR (max - min) <  trigger - delta hyst.     the spread closed back below it
```

The **spread condition is what keeps this honest**. A pack that reaches the setpoint
already balanced has nothing to equalize: it reports `false` and the Cut-Off timer does
its job normally. A plain voltage comparison, with no spread condition, would report
balancing forever and push every single charge to the EOC timer ceiling.

The **two hysteresis margins** exist because both references are sat *on* at top of
charge: the max cell rests on the setpoint for a long time, and the spread hovers around
the trigger voltage. Without them the state would toggle on every tick.

The spread and its threshold are compared as whole millivolts, the resolution the cells
are reported at. This is not cosmetic: `3.450f - 3.445f` evaluates to `0.005000114`, so a
raw float comparison against `0.005` would hold the spread above the threshold forever and
never release the Cut-Off timer.

### Where it plugs in

The package extends `bms${bms_id}_bms_equalizing`, the **raw** BMS flag, and not the
combined `bms${bms_id}_equalizing` sensor. Consequence: `bms_base_balancer.yaml` is
neither modified nor duplicated, and it keeps giving an **external balancer priority**
whenever one is online. If you run a NEEY or a Modbus balancer on that `bms_id`, its
reading wins; the inference only applies when no balancer reports for this pack.

## 3. Which BMS are concerned

The four BMS below shipped a hardcoded `return false;`. The package is now **included by
default** for them — there is nothing to add to your YAML:

| BMS | Packages |
|---|---|
| EG4 LL V2 | `bms_combine_EG4_LLV2_RS485_bms_full.yaml`<br>`bms_modbus_EG4_LLV2_RS485_bms_full.yaml` |
| Seplos V1 V2 | `bms_combine_SEPLOS_V1_V2_RS485_bms_full.yaml`<br>`bms_modbus_SEPLOS_V1_V2_RS485_bms_full.yaml` |
| Seplos V3 | `bms_combine_SEPLOS_V3_RS485_bms_full.yaml`<br>`bms_modbus_SEPLOS_V3_RS485_bms_full.yaml` |
| JK RS485 DISPLAY | `bms_combine_JK_RS485_DISPLAY_full.yaml` |

The `bms_modbus_*` variants are the multi-node server packages, so a secondary node
relays the inferred flag to the client exactly like a real one.

The **Fake BMS** (`bms_combine_FAKE.yaml`, `_FAKE_extended.yaml`, `_DEMO.yaml`) also uses
it now. It previously carried an inline voltage comparison with no spread condition,
which the package replaces.

### BMS that are *not* concerned

- **JK** (BLE, RS485 Modbus, UART 4G-GPS), **JBD**, **Ecoworthy**, **PACE**, **Deye CAN**
  and the YamBMS Modbus client node all report a real balancing flag. Nothing changes.
- **BASEN** already infers the flag inline, from its own `balance_starting_voltage` and
  `balance_trigger_voltage` reported by the BMS. Those are a better source than a
  derived anchor, so it is left as is.
- **KS BLE** derives the flag from the balanced-cell bitmask, which is real information.

The package can be added manually to another BMS, once for each `bms_id`:

```yaml
      - path: packages/bms/bms_options_fake_equalizing.yaml
        vars:
          bms_id: '1' # must be a number
```

but only where `bms<id>_bms_equalizing` is declared as a plain `platform: template`
binary_sensor, which is what it replaces the lambda of. A BMS that exposes the flag
through its own component — `jk_bms_ble`, `jbd_bms`, `modbus_controller` and the like —
cannot be extended this way: those platforms take no `lambda:`, and the configuration
will not validate. That is not a real limitation, since those are precisely the BMS that
already report a genuine flag.

## 4. Tuning

### The one setting that matters: `bms_balance_trigger_voltage`

This is your BMS's own balancing threshold, and it is the spread the inference compares
against. Some BMS report it over their protocol; those that cannot expose it as a var to
declare at import — **Seplos V1/V2, Seplos V3, EG4 LL v2 and JK RS485 DISPLAY all work
that way**. It also feeds `Auto CVL`, so it was already worth getting right.

EG4 LL v2 and JK RS485 DISPLAY used a hard-coded value.
They now expose it like the others with the following default values:

| BMS | Default |
|---|---|
| EG4 LL V2 | 0.03 |
| SEPLOS V1 V2 | 0.01 |
| SEPLOS V3 | 0.01 |
| JK RS485 DISPLAY | 0.01 |

```yaml
      # BMS 1
      - path: 'packages/bms/bms_combine_your_BMS.yaml'
        vars:
          bms_id: '1'
          # ... other vars of your BMS ...
          bms_balance_trigger_voltage: '0.010'           # V. Your BMS's balancing threshold
          bms_fake_equalizing_enabled: 'true'            # Optional : true/fasle, true by default
          bms_fake_equalizing_hysteresis: '0.030'        # Optional : 0.030 by default
          bms_fake_equalizing_delta_hysteresis: '0.002'  # Optional : 0.002 by default
```

Set it to what your BMS is actually configured for. On a JK you can read and change it in
the BMS itself; on an EG4 it may not be adjustable, in which case leave the default.

### The rest

An on/off switch and two margins around the references. No threshold among them, and the
defaults are fine for any pack.

| Substitution | Default | Meaning |
|---|---|---|
| `bms_fake_equalizing_enabled` | `'true'` | set to `'false'` to turn the inference off for this BMS |
| `bms_fake_equalizing_hysteresis` | `0.030` | how far below the bulk setpoint the max cell may fall before balancing stops |
| `bms_fake_equalizing_delta_hysteresis` | `0.002` | how far below the trigger voltage the spread may fall before balancing stops |

All of them can be passed per BMS as above, or set once for every BMS in the root
`substitutions:` block. The spread values are resolved to whole millivolts, the resolution
the cells are reported at, so a value finer than `0.001` has no effect.

**To disable the inference** on a BMS without editing any package:

```yaml
          bms_fake_equalizing_enabled: 'false'
```

The flag then reports the constant `false` its package used to hardcode, which is the
behaviour you had before this release. Do *not* try to disable it by raising
`bms_balance_trigger_voltage` instead — that value also feeds `Auto CVL`, where it means
something else entirely: how far the highest cell may overshoot the per-cell setpoint
before the PI clamps.

## 5. What changes for you on upgrade

If you own one of the four BMS above, the `balancing` entity will now turn on at the top
of charge as soon as your cells are spread by as much as your BMS's own
`bms_balance_trigger_voltage` — 10 mV on a Seplos or a JK, 30 mV on an EG4 unless you
declared otherwise. The charge then runs until the spread closes back below that, or
until the EOC timer expires, instead of being cut short by the Cut-Off timer. That is the
intended fix, but it *is* a change in charge termination, so watch a couple of cycles
after updating.

The risk is bounded on the safe side. A false positive can only extend the charge up to
the EOC timer, which exists for exactly that purpose. A false negative simply restores
the previous behaviour.

## Why not the original pull request

[@haysdb](https://github.com/haysdb) opened
[PR #304](https://github.com/Sleeper85/esphome-yambms/pull/304) with a *Fake Balancer*
package. The diagnosis was right and the idea is his. The implementation was shaped
around his own setup — a NEEY balancer that does not run every day — and carried more
than YamBMS needs:

- **Absolute thresholds as entities.** Four `number` entities held the start / sleep /
  trigger / stop-diff voltages, hardcoded to LFP values (3.45 / 3.42 V). They lived
  alongside the bulk voltage the user had already configured, so the same physical
  setpoint existed twice and could drift apart. Taking the voltage reference from
  `bulk_voltage / cell_count` and the spread reference from
  `bms_balance_trigger_voltage` removes the duplication entirely, and makes the
  package track each BMS instead of a constant that fits none of them.
- **A companion stub package.** The lambda referenced `balancer${bms_id}_online_status`
  and `balancer${bms_id}_equalizing`, which only exist when a balancer package is
  included, so a second package had to declare two always-false sensors just to make it
  compile without one. Reading the raw BMS flag instead makes the stub unnecessary.
- **A duplicated core lambda.** It extended the *combined* `bms${bms_id}_equalizing` and
  recopied the branch from `bms_base_balancer.yaml` to add its OR. Extending the raw flag
  keeps a single copy of that logic.
- **A side effect on another entity.** The interval wrote
  `bms${bms_id}_var_ext_balancer_online = real_online || fake_eq`, which made
  `bms_base_balancer.yaml` report the external balancer's trigger voltage — `0.000 V`
  when no balancer had ever been online.
- **Eight entities and a sub-device per BMS**, for a function that needs none.

The `Force` switch and the `Max Run Time` number were dropped as well: they answer the
need to launch a weekly top-balance by hand when the hardware balancer is idle, which is
a balancer feature rather than a BMS one.

Thanks to @haysdb for finding the problem and for the threshold model — start and stop on
a spread with hysteresis is his, and it is the part that makes the inference trustworthy.
