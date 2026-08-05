# YamBMS - Understanding ESPHome Modbus

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> **Work in progress.** The ESPHome Modbus stack is being reworked by
> [@exciton](https://github.com/exciton) through a long series of pull requests.
> The first of them landed in ESPHome 2026.7, and more are on the way — including
> a full overhaul of `modbus_controller`
> ([#11781](https://github.com/esphome/esphome/pull/11781)) that will change how
> commands are queued and how offline devices are handled. This page tracks that
> work and will be updated progressively as the PRs are merged.

Starting with **ESPHome 2026.7**, the Modbus client timing defaults have changed
(`send_wait_time` 250 ms → 2000 ms, `turnaround_time` 100 ms → 600 ms).
These new defaults are safe for slow third-party hardware, but they are far too
conservative for a YamBMS setup where many fast ESP32-based servers share one bus.

YamBMS therefore ships its own defaults:

```yaml
substitutions:
  # UART
  modbus_baud_rate: '19200'          # 9600 / 19200 / 115200
  # Modbus
  modbus_id: '1'
  modbus_send_wait_time: '200ms'     # Timeout: max time to wait for the FIRST byte of a response
  modbus_turnaround_time: '0ms'      # Pause after a completed response before the next command
  # Modbus Controller
  modbus_update_interval: '5s'       # Frequency with which BMS/Balancer/Shunt (modbus servers) are queried

modbus_controller:
  max_cmd_retries: 1                 # Retransmissions after a timeout (default is 4)
  offline_skip_updates: 5            # Server re-polled every 30s with an update_interval of 5s
```

> **The one idea to remember:** what costs time on the bus is the **number of
> Modbus commands per cycle**, not the number of servers. A BMS whose register
> map has gaps generates several commands instead of one. Reducing the command
> count is usually worth more than raising the baud rate.

---

## What each parameter does

### `send_wait_time` — response timeout

Maximum time the client waits for the **first byte** of a response. If nothing
has started arriving within this time, the command is treated as failed.

* It is a **latency** budget, not a transmission budget: it does not depend on
  the baud rate or on the response length. Once the first byte arrives, the
  client waits for the whole response however long it takes.
* It only costs time **when a server does not answer**. Lowering it has no effect
  on a healthy bus — it just bounds the price of a failure.

An ESPHome server on ESP32 answers within one pass of its main loop (16 ms by
default). `200ms` leaves ample margin for an occasional slow loop (WiFi burst,
API reconnect, flash write) without ever mistaking a busy server for a dead one.

### `turnaround_time` — inter-command pause

Pause inserted after a completed response, before the next command. It exists to
give slow devices time to get ready for the next frame.

**It is charged per command, not per server** — including between two commands
sent to the same BMS. With 24 BMS generating 4 commands each, a
`turnaround_time` of 100 ms would add 96 × 100 ms = **9.6 s** to every cycle.

`0ms` is the right value for an all-ESPHome bus. It never produces truly
back-to-back frames: the Modbus specification silence (3.5 characters) is always
enforced, and the ESPHome main loop adds its own scheduling delay on both sides.

### `update_interval` — polling frequency

How often each `modbus_controller` reads **all** its register ranges. All
controllers fire at roughly the same time and the resulting commands are
serialized on the bus, one conversation at a time.

### `max_cmd_retries` — retransmissions

Retransmissions of a timed-out command before giving up (not counting the initial
transmission). ESPHome defaults to `4`; YamBMS uses `1`. One retry absorbs a
transient glitch, and a genuinely dead server is handed to `offline_skip_updates`
quickly instead of blocking the bus.

### `offline_skip_updates` — offline back-off

Once a server has exhausted its retries it is marked **offline**, and this many
update cycles are skipped before it is probed again. With `5`, a silent server is
re-polled every `(5 + 1) × update_interval` = **30 s**. As soon as it answers a
probe it is marked online and normal polling resumes — no reboot or manual action
needed.

---

## Reducing the number of commands

ESPHome merges **consecutive** registers into a single range, and reads each
range with one Modbus command. A single unmapped register in the middle splits
the range in two — and every extra command costs a request frame, a response
frame, and a fixed scheduling overhead.

### Fill the gaps with `register_count`

`register_count` can span a gap. Set it on the sensor **before** the gap, sized
to reach the next register you actually want. The registers in between are read
and discarded.

Example — a PACE BMS map with gaps at register 8 and registers 13–14:

| Sensor to modify | Value | Effect |
|------------------|-------|--------|
| last sensor before the gap (address 7) | `register_count: 2` | absorbs register 8 |
| last sensor before the gap (address 12) | `register_count: 3` | absorbs registers 13–14 |

Ranges `0–7`, `9–12` and `15–36` then merge into a **single command covering
0–36**, taking that BMS from 4 commands per cycle down to 2 — roughly a third off
the total cycle time, for the cost of 3 useless registers read (6 bytes).

> Check first that the skipped registers are actually **readable** on your
> device. An invalid register anywhere inside a range makes the whole command
> fail with a Modbus exception.

### `force_new_range` — use sparingly

`force_new_range: true` (default `false`, available on every `modbus_controller`
platform) prevents a sensor from joining the previous range, forcing a separate
command. It works in the *opposite* direction to the optimisation above, so use
it only to isolate genuinely static registers that can then carry a high
`skip_updates`.

Two things to know:

* `skip_updates` applies to the **whole range**, and ESPHome keeps the lowest
  non-zero value among its sensors. One fast sensor inside a large block forces
  the entire block to the fast rate.
* Sensors marked `force_new_range` are sorted **before** all others, ahead of the
  address sort. Marking one sensor in the middle of a block does not split it in
  two — it pulls that sensor to the front and lets the rest merge. To split a
  block, mark the first sensor of each intended segment.

It is also set automatically for any sensor using `custom_command`.

### Sensors can share a range for free

Several sensors may read the same registers without any extra bus traffic — they
all decode the same response buffer. A `delta cell voltage` sensor declared at the
same address as `cell voltage 1`, with a lambda walking all 16 cells, costs
**zero** additional commands. Two declarations at the same address produce one
transaction, not two.

### YAML order: when it matters

Sensors are sorted internally (by register type, `force_new_range`, address, then
offset), so their order in the file is normally irrelevant.

**Except when two sensors share the same address and offset.** The final
tie-break is allocation order — that is, YAML order — and the sensor that comes
first defines the range's `register_count`.

With `cell voltage 1` (1 register) and `delta cell voltage`
(`register_count: 16`) both at address 15:

* `cell voltage 1` **first** → the range opens with count 1, cells 2–16 extend it
  normally → **one command**. ✅
* `delta` **first** → the range opens with count 16, cell 2 no longer fits the
  extension test → **a second range starts**, and registers 16–30 are read twice. ❌

Leave a comment in your YAML so nobody reorders these by accident.

---

## Tuning guide

* **`send_wait_time`**: set it to the slowest observed "time to first byte" of any
  server on the bus, with generous margin. `200ms` suits all-ESPHome/ESP32 buses.
  Raise it only if a device that is genuinely alive produces spurious timeouts.
  Do **not** raise it "to be safe": it is the unit price of every dead-server
  event.
* **`turnaround_time`**: keep `0ms` on an all-ESPHome bus. For a slow third-party
  device try `10–30ms` first; `100ms` (the old ESPHome default) is the safe
  fallback for unknown hardware, and `200–600ms` only for VFDs and gateways.
  Remember the cost is per command.
* **Mixed buses**: `turnaround_time` belongs to the *hub*, so one slow device
  imposes its value on all your BMS. Put slow third-party hardware on a **second
  UART** with its own `modbus:` hub rather than raising the global value.
* **`modbus_baud_rate`**: `19200` is a good default. Gains flatten out above it,
  because per-command scheduling overhead starts to dominate transmission time —
  merge ranges before reaching for a higher baud rate.
* **`update_interval`**: leave enough headroom that the full cycle still fits when
  a server is dead. If some entities stop refreshing while others keep updating,
  the cycle is overrunning the interval — reduce the command count, raise the
  interval, or split the bus.
* **`offline_skip_updates`**: `(value + 1) × update_interval` is the re-probe
  period. `5` → every 30 s at a 5 s interval. Lower it to `3` for faster recovery
  detection.

---

## Checking your configuration

Set the logger to `DEBUG` (or `VERBOSE` for the range details) and watch a few
cycles:

```yaml
logger:
  level: DEBUG
```

* Ranges are logged as they are built — the quickest way to confirm that a
  `register_count` gap fill actually merged what you expected.
* `Modbus command timed out` on a device that is alive means `send_wait_time` is
  too low, or the bus is saturated.
* `Modbus device=N set offline` / `back online` traces the offline back-off.
