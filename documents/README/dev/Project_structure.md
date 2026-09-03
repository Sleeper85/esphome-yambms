# Project structure

YamBMS is a set of **ESPHome YAML packages** — there is no compiled application code beyond a few
embedded C++ lambdas. It merges data from several BMS / Shunt / Balancer units and drives an
inverter over CAN or RS485 (PYLON / SMA / Victron / LuxPower). All the logic lives in YAML
(`substitutions`, `packages: !include`, `lambda:`) and is assembled by the ESPHome compiler.

## Entry points

- **`YamBMS_LP_*.yaml`** — *Local Packages*. Requires the `packages/` folder to be present
  locally.
- **`YamBMS_RP_*.yaml`** — *Remote Packages*. Pulls the packages from GitHub (`!include` on a
  `github://` URL). This is what most users run.

  Differences and structure are detailed in [YamBMS_LP_YAML.md](../YamBMS_LP_YAML.md) and
  [YamBMS_RP_YAML.md](../YamBMS_RP_YAML.md).

- **`YamBMS_Local_Packages_example.yaml`** / **`YamBMS_Remote_Packages_example.yaml`** — starting
  templates.
- **`yambms_config.yaml`** — Modbus substitutions shared between several nodes in a multi-node
  setup.
- **`yambms_custom.yaml`** — snippets meant to be copy-pasted into the main YAML (extra switches
  and services). Not included by default.
- **`examples/single-node/`** and **`examples/multi-node/`** — ready-to-copy `!include` blocks for
  a given BMS, Shunt or Balancer.

## The `packages/` tree

### `base/`

Generic device building block: ESPHome core, WiFi, Ethernet, `sub_device` declarations, the fault
registry (`device_base_fault_registry.yaml`), memory and PSRAM debug helpers.

### `board/`

One file per board (`board_ESP32-S3_*.yaml`) defining pins and GPIO. The `board_options_*.yaml`
files are optional building blocks — UART, CAN, PSRAM, LVGL display, WiFi AP — included
separately depending on the hardware.

### `bms/`, `shunt/`, `balancer/`

All three follow the same layered scheme, per brand and protocol:

| File pattern | Role |
|---|---|
| `*_combine_<Brand>_<Interface>_<variant>.yaml` | The file you include from your main YAML. Assembles the layers below. |
| `*_modbus_<Brand>_*.yaml` | Modbus register mapping (RS485/Modbus BMS only). |
| `*_sensors_<Brand>_*.yaml` | Declaration of the exposed ESPHome entities. |
| `*_errors_bitmask_<Brand>.yaml` | Alarm bit mapping. |
| `*_base*.yaml` | Brand-agnostic shared logic: combining engine, SoC/SoH, cycles, LED. |

### `yambms/`

The central engine. `yambms.yaml` aggregates `yambms_inverter_registry.yaml`,
`yambms_core.yaml`, the `yambms_auto_*.yaml` functions (CVL / CCL / DCL / Float / EOC /
temperature / SoC limit) and `yambms_service.yaml`, then `yambms_canbus*.yaml` or
`yambms_rs485*.yaml` for the link to the inverter.

`yambms_inverter_registry.yaml` holds the protocol dictionary (`YB_PROTO_*`), the brand to
protocol mapping and the per-couple battery mode and note. Both inverter buses read it.

On the RS485 side, `yambms_rs485.yaml` is the entry point — selects, diagnostics, telemetry
slot — and it includes the protocol implementation, currently `yambms_rs485_pylon.yaml`.

## Where the behaviour is documented

The structure above tells you where code lives, not what it does. For the charging logic and the
auto functions, read:

- [Charging_logic.md](../Charging_logic.md)
- [YamBMS_functions.md](../YamBMS_functions.md)
- [YamBMS_behavior.md](../YamBMS_behavior.md)
- [Supported_devices.md](../Supported_devices.md) — supported BMS, shunts and inverters.
