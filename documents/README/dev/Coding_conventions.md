# Coding conventions

Conventions actually in use across the repository. Follow them when adding a package or editing
an existing one — the safest approach is always to copy a comparable existing file and adapt it.

## Language

Code comments and documentation are written in **English**.

## File naming

Files under `packages/<domain>/` follow this grammar:

```
<domain>_<layer>_<Brand>_<Interface>_<variant>.yaml
```

For example: `bms_combine_JK_RS485_Modbus_bms_full.yaml`.

The `_full` / `_standard` / `_minimal` / `_secondary` variants control **how many entities are
exposed**, not the logic itself.

## File header

Every package YAML starts with the same header block:

```yaml
# Updated : yyyy.mm.dd
# Version : x.y.z
# GitHub  : https://github.com/Sleeper85/esphome-yambms
```

followed by the GPLv3 notice. Reproduce it in any new package.

## Instance substitutions

`${xxx_id}` substitutions are numeric identifiers. For BMS units (`bms_id`) they **must start at
`1` and be contiguous**. This is a functional constraint, not a style rule, and the consequence of
getting it wrong is severe: the combiner pipeline advances a shared counter from one instance to
the next, so a gap in the numbering stalls that counter and the whole aggregation deadlocks
silently — no combined values, no setpoints sent to the inverter. The identifier is also used as
a bitmask index, for instance `1 << (${bms_id} - 1)` in `bms_combine.yaml`.

See [Design_decisions.md](Design_decisions.md) for how the pipeline works.

## Include order

Include the BMS and Shunt packages in ascending `${xxx_id}` order in your main YAML. The combiner
processes instances in the order their lambdas run, so ascending order completes one aggregation
round per interval; an out-of-order include still converges but spreads the round over several
intervals.

## Entity IDs

Entity IDs follow `<domain>${xxx_id}_<name>`:

```
bms${bms_id}_total_voltage
yambms${yambms_id}_var_bms_online_bitmask
```

Globals used by the YamBMS engine's internal logic are prefixed `yambms${yambms_id}_var_*`.

## Sub-devices

Every entity carries a `device_id:` that attaches it to the matching ESPHome `sub_device`, so that
each BMS, Shunt, Balancer and YamBMS instance appears as its own device in Home Assistant. Always
fill it in — copy an existing package to get it right.

## Section comments

Large files (`yambms_core.yaml`, `bms_combine.yaml`, the `YamBMS_LP_*` root YAML) are structured
with ASCII box comments:

```yaml
# +----------------------------------------+
# | Section title                          |
# +----------------------------------------+
```

## Boot sequencing

Startup ordering relies on `on_boot` priorities. For example, `priority: 600` initialises the BMS
combiner in `bms_combine.yaml`, and `priority: 550` is documented as running right after it in
`yambms_custom.yaml`. If you add an `on_boot` block, respect the existing ordering rather than
picking an arbitrary priority.

## Validating a change

There is no test suite. Validate a YAML with:

```bash
esphome config <file>.yaml    # validation only
esphome compile <file>.yaml   # full compilation
```

See [Installation_procedure.md](../Installation_procedure.md).
