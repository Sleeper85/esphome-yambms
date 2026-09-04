# Inverter brand and protocol — breaking change

## What changes

The inverter link is now described by **two selects** instead of one:

| Select | Options | Default |
| --- | --- | --- |
| `Inverter brand` | `Not defined`, `Other`, then the supported brands | `Not defined` |
| `Protocol` | `Automatic`, `Disabled`, then the protocols of that bus | `Automatic` |

Selecting your inverter brand is enough: with `Protocol` on `Automatic`, YamBMS applies the
protocol that matches your brand. Choosing a protocol explicitly always takes priority over the
brand, so an inverter that does not follow the usual mapping can still be driven.

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

`yambms_rs485_pylon.yaml` **stays the file you include** — no change there. Its internals are
reorganised to make room for the additional RS485 protocols to come: the `Inverter brand`/
`Protocol` selects, diagnostics and telemetry move out to a new shared file, `yambms_rs485.yaml`,
which `yambms_rs485_pylon.yaml` includes itself. Each protocol file includes
`yambms_rs485.yaml` this way round, rather than the other way, so that a node with several RS485
links on different UARTs can run a different protocol on each.

`yambms_rs485_pylon_web_server.yaml` becomes `yambms_rs485_web_server.yaml`, and unlike before it
no longer includes the link itself: add it **alongside** `yambms_rs485_pylon.yaml` in your YAML,
with its own `vars: { rs485_id: '1' }` matching the link it decorates, instead of swapping one file
for the other.

`rs485_uart_baud_rate` keeps the same meaning but is now applied at runtime instead of extending
the `uart` component, and defaults to `9600`. Boards using a UART expander — the `wk2168` of the
PVbrain2 — no longer need a separate include: every board now uses the same entry point.
