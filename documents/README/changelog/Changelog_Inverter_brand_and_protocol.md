# Inverter brand and protocol — breaking change

## What changes

The inverter link is now described by **two selects** instead of one:

| Select | Options | Default |
| --- | --- | --- |
| `Inverter brand` | `Not defined`, `Other`, then the inverter brands | `Not defined` |
| `Protocol` | `Automatic`, `Disabled`, then the protocols of that bus | `Automatic` |

Selecting your inverter brand is enough: with `Protocol` on `Automatic`, YamBMS applies the
protocol that matches your brand. Choosing a protocol explicitly always takes priority over the
brand, so an inverter that does not follow the usual mapping can still be driven.

The brand list also covers manufacturers that are not validated yet. Those use `PYLON V2` on CAN
and the protocol compiled on the node on RS485, and the `Note` entity tells you the brand has not
been validated on that bus.

On RS485 the brand never changes the protocol, which is the `rs485_protocol` of your YAML. `LIB`
only works with `Voltronic` and `MPP Solar`: in `Automatic`, a node compiled for `LIB` stays silent
for any other brand. Rebranded Voltronic inverters must select `Voltronic`.

The old `YamBMS name` select is **removed**. The manufacturer name announced on CAN frame `0x35E`
is now derived from the protocol in use — exactly the names the `Automatic` mode already sent, and
which are known to work. The `GOODWE`, `SHEnergy` and `BYD` names are no longer selectable.

## What you must do after updating

> [!IMPORTANT]
> **The inverter link stays inactive until you select your inverter brand.** Both selects are
> renamed, so their stored value is reset and every node starts at `Not defined` + `Automatic`.
> Until you make a choice, nothing is sent on the CAN or RS485 bus and your inverter will report a
> BMS communication fault, stopping charge and discharge.

Open your YamBMS device in **Home Assistant** or **Web server** and set `Inverter brand`. That is all that is needed —
the protocol follows. If your inverter is not in the list, select `Other` and set `Protocol`
yourself.

Users running off-grid should plan the update accordingly: the inverter will stop using the
battery until the brand is selected.

Your Home Assistant automations and dashboards referring to the old entity ids must be updated:

| Before | After |
| --- | --- |
| `select.yambms_1_canbus_1_yambms_name` | removed |
| `select.yambms_1_canbus_1_yambms_protocol` | `select.yambms_1_canbus_1_protocol` |
| `select.yambms_1_rs485_1_yambms_protocol` | `select.yambms_1_rs485_1_protocol` |
| — | `select.yambms_1_canbus_1_inverter_brand` |
| — | `select.yambms_1_rs485_1_inverter_brand` |

The updated dashboards are provided in `HomeAssistant_Dashboards/`.

## New diagnostic entities

Three text sensors per inverter link report what is actually happening:

- **`Inverter link protocol`** — `Deye - CAN PYLON V1`, or `Inverter CAN bus not defined` when
  nothing is selected yet.
- **`Inverter battery mode`** — how to configure the battery type on the inverter itself, for
  instance `Lithium 00` for a Deye on CAN, `Lithium 12` for a Deye on RS485. It is keyed on the
  brand *and* the protocol, and reports `See inverter manual` for a couple that has never been
  confirmed rather than guessing.
- **`Note`** — what is specific to that brand and protocol, when there is anything to say.

## Protocol names

| Before | After |
| --- | --- |
| `PYLON 1.2` | `PYLON V1` |
| `Pylontech` (RS485) | `PYLON` |

`PYLON V1` leaves room for the 1.7 revision of the protocol.

## Schneider XW Pro

The `canbus_extended_ack` substitution is **removed**. Both the 11-bit and the 29-bit ACK are now
listened to at the same time, so the extended ACK works with no configuration at all. Remove the
line from your YAML if you had set it.

## RS485 package files

**The file you include changes**, from `yambms_rs485_pylon.yaml` to `yambms_rs485.yaml`. This
makes room for the additional RS485 protocols to come: `yambms_rs485.yaml` carries the `Inverter
brand`/`Protocol` selects, diagnostics and telemetry, and takes a new `rs485_protocol` var
(`pylon` or `voltronic`) that tells it which protocol implementation to include for you
(`yambms_rs485_pylon.yaml`, keeping the PYLON implementation only, or the new
`yambms_rs485_voltronic.yaml`). A node with several RS485 links on different UARTs can run a
different protocol on each, since each link's `vars:` names its own `rs485_protocol`.

> [!IMPORTANT]
> Point your `!include` to `yambms_rs485.yaml` and add `rs485_protocol: 'pylon'` to its `vars:`.
> This relies on substitutions in an `!include` filename, added in ESPHome 2026.4.0
> ([esphome#12213](https://github.com/esphome/esphome/pull/12213)) — already covered by this
> project's `min_version: 2026.10.0`, so no extra requirement for you.

`yambms_rs485_pylon_web_server.yaml` becomes `yambms_rs485_web_server.yaml`. It includes the link
itself, so use it **instead of** `yambms_rs485.yaml`, not alongside it, with the same `vars:`.

`rs485_uart_baud_rate` keeps the same meaning and defaults to `9600`. The link now declares its
UART itself from `rs485_uart_id`, so remove the `board_options_itf_uart_*.yaml` include of that UART
from your YAML. Boards using a UART expander — the `wk2168` of the PVbrain2 — no longer need a
separate include: every board now uses the same entry point.
