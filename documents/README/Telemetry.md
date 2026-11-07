# Telemetry

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

This page describes YamBMS 1.8.1.

## Summary

Telemetry is **on by default**. Every 6 hours, each ESP32 sends its YamBMS setup :
versions, board, BMS and inverter types, uptime, date, and an identifier derived from its MAC
address. This shows which hardware to support first.
The server also sees your public IP address and sends a reduced form of it to ip-api.com to
find your country. Data has no expiry date. To stop all requests, see [How to disable](#how-to-disable).

## Why

These reports show how YamBMS is really used. They help to:

- decide which BMS, boards and inverters to support first;
- find bad default protocols: if many users of one inverter brand force another protocol, the
  default for that brand needs review;
- follow how fast new YamBMS and ESPHome versions are adopted.

## What is sent

The ESP32 sends one HTTP POST to `http://script.yambms.org/yambms.post.php`. This is the complete
list, from [yambms_service.yaml](../../packages/yambms/yambms_service.yaml):

| Field | Example | Meaning |
|---|---|---|
| `node_id_hash` | `0123456789abcdef0123456789abcdef` | Identifier derived from the MAC address, see [Identity](#identity) |
| `version` | `1.8.1` | YamBMS version |
| `board_chip` | `ESP32` | Chip of the board |
| `board_name` | `DevKit V1` | Name of the board |
| `bms_model` | `JK,JK,` | Model of each BMS |
| `bms_protocol` | `UART,UART,` | Protocol of each BMS |
| `bms_count` | `2` | Number of BMS |
| `inverter_brand` | `Deye,SRNE,` | Inverter brand of each link, `Not defined` if not set |
| `inverter_bus` | `CAN,RS485,` | Bus of each link |
| `inverter_protocol` | `PYLON V1,PYLON,` | Protocol of each link, also `None` (not configured) or `Disabled` |
| `inverter_protocol_source` | `auto,manual,` | `auto` if the protocol is set to `Automatic`, `manual` if you forced it |
| `uptime` | `93784` | Seconds since the last boot |
| `date_time_now` | `2026-09-02 12:37:37` | Date and local time of the ESP32 |
| `User-Agent` (HTTP header) | `ESPHome/2026.10.2 (https://esphome.io)` | ESPHome version. The server stores the version only |

`board_name`, `bms_model` and `bms_protocol` come from your YAML, so a value you edited there is
sent as you wrote it. The firmware does not send battery values (voltage, current, SoC), the WiFi
name or password, API or OTA keys, or the device name.

**When:** a first report 5 minutes after each boot, then every 6 hours. Nothing is sent without a
network connection.

**No internet access:** the update and telemetry services turn themselves off. After 3 failed
attempts in a row, about 12 hours after boot, the ESP32 stops trying. It tries again only after
the next reboot.

**Version check:** a separate request, sent at the same times, reads the latest version from
`http://script.yambms.org/yambms.get.php`. It has no data fields, but the server sees your IP
address and `User-Agent`, as with any web request. It writes nothing to the database.

**Plain HTTP:** the reports are not encrypted. Anyone on the network path, such as your internet
provider, can read them. HTTPS is not used because a TLS handshake needs 30 to 40 KB of internal
RAM, which does not fit next to BLE on boards without PSRAM.

## How it is processed

### Identity

- The ESP32 computes a SHA-256 hash of a public salt and its MAC address, and keeps the first 32
  characters. This is the **Node ID hash**. A reflash does not change it.
- The server hashes that value again with a secret key, and stores only the result.
- The MAC address and the Node ID hash are not stored in the database.
- The Node ID hash is **not anonymous**. The salt is public, so someone who captures your traffic
  can find your MAC address by trying candidates. A database leak alone does not reveal it,
  because the secret key is not in the database.
- **Firmware before 1.8.0 sends the MAC address itself**, in clear. The server derives the same
  identifier and does not store the MAC.

### IP address

The server reads your public IP address on each report. It does not store it in the database or
in its application logs. It derives two values:

- **Location ID:** a hash of the IP address made with a second secret key (the full IPv4 address,
  or the first 64 bits of an IPv6 address). It is stored and replaced at each report. It estimates
  how many installations exist when several nodes share one address. It changes when your address
  changes, and it does not prove that nodes are in the same home (CGNAT). Someone who has the
  secret key could find an address by trying candidates.
- **Country:** a two-letter code, or `XX` if unknown. The server cuts the address down to a network
  prefix (/24 for IPv4, /48 for IPv6) and holds it in the database, normally for up to 15 minutes.
  It then sends the prefix to [ip-api.com](https://ip-api.com), **a third party, over plain HTTP**
  (the free service has no HTTPS). The prefix is sent without any node identifier, and is deleted
  from the database once resolved. This happens for a new node, when the address changes, or
  while the country is unknown. YamBMS has no control over what ip-api.com does with the prefix.

### Retention

- The server keeps **one row per node**, overwritten at each report. There is no history of
  past reports. The row also keeps the date the node was first seen.
- **There is no expiry date.** A row stays forever, even if the node is off or telemetry is
  disabled. It is removed only [on request](#access-or-delete-your-data).
- The server also keeps the number of active nodes, once per week, with no per-node data.

Only [@Sleeper85](https://github.com/Sleeper85) can view the per-node data, on a password-protected
page. The hosting provider runs the server that holds it.

### Active nodes

A node is one ESP32 running YamBMS. It is **active** if its last report is less than 3 days old.
This count has limits:

- It counts ESP32 boards, not users. One user can have several nodes.
- A replaced ESP32 is a new node. The old row stays in the table.
- The date comes from the clock of the ESP32, not from the server. A node with a wrong clock can
  be counted wrongly.

## What is published

Public statistics are at [stats.yambms.org](https://stats.yambms.org). The page shows aggregated
counts of active nodes only, per version, board, BMS, inverter and country. Any value used by fewer
than 5 nodes is grouped into `Other`, except the number of BMS per node.

The page also shows the best and the average uptime of active nodes, in whole days. The best uptime
comes from a single node, with nothing else attached to it. No other per-node data is published.

## How to disable

Both services are set at compile time. Add this to the `substitutions:` block of your main YAML,
then compile and flash again:

```yaml
substitutions:
  yambms_update_service: 'false'     # Set to false to disable update checks
  yambms_telemetry_service: 'false'  # Set to false to disable the sending of telemetry data
```

| `yambms_telemetry_service` | `yambms_update_service` | Result |
|---|---|---|
| `'false'` | `'false'` | **No request is sent at all** |
| `'false'` | `'true'` | No report. The version check still runs |
| `'true'` | `'false'` | Reports are sent. The `Last version` entity no longer updates |

Disabling stops new reports. It does not delete your existing row. The precompiled demo firmware
cannot be changed: build your own firmware to disable telemetry.

## Access or delete your data

Use the form on the [Contact page](https://stats.yambms.org/contact/) of **stats.yambms.org** to ask a question,
get a copy of your data, or have it deleted. For configuration or hardware help, use
[GitHub](https://github.com/Sleeper85/esphome-yambms).

Access and deletion need your Node ID hash: 32 characters, digits and letters `a` to `f`. Find it
in the `Diagnostic` page of the YamBMS dashboard, card `YamBMS - Network`, line `Node ID hash`, or
in the `Node ID hash` diagnostic entity in Home Assistant. Each ESP32 has its own value.

Disable telemetry before asking for deletion. Otherwise, the next report creates a new row.
