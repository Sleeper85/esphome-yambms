# YamBMS - Multi-node Modbus settings

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

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

This page explains what each parameter does, what actually happens on the bus
every `update_interval`, and how to tune the values for your hardware.

## What each parameter does

### `send_wait_time` — response timeout

Maximum time the client waits for the **first byte** of a response after sending
a command. If nothing has started arriving within this time, the command is
considered failed (timeout).

Two important properties:

* It is a **latency** budget, not a transmission budget. It does not depend on
  the baud rate or on the response length. Once the first byte arrives, the
  client waits for the complete response no matter how long it takes.
* It only costs time **when a server does not answer**. Lowering it has zero
  effect on a healthy bus — it only bounds the price of a failure.

An ESPHome server on ESP32 normally starts answering within 20–30 ms (one pass
of the main loop). `200ms` leaves ample margin for the occasional slow loop
(WiFi burst, API reconnect, flash write) without ever mistaking a busy server
for a dead one.

### `turnaround_time` — inter-command pause

Pause inserted after a **completed** response before the next command is sent.
Its purpose is to give slow devices time to get ready for the next frame.

With ESPHome firmware on ESP32 on both sides of the bus, this can safely be set
to `0ms`: the silent interval required by the Modbus specification (3.5
characters, ≈ 2 ms at 19200 baud) is still enforced automatically. Only raise
this value if you mix in third-party devices that need extra recovery time.

### `update_interval` — polling frequency

How often each `modbus_controller` schedules a read of its registers. All
controllers fire at (roughly) the same time; the commands are then serialized
on the bus one by one (see below).

### `max_cmd_retries` — retransmissions

How many times a timed-out command is retransmitted before giving up
(not counting the initial transmission). The ESPHome default is `4`, which
makes a dead server cost `(1 + 4) × send_wait_time` per cycle. YamBMS lowers
it to `1`: one retry is enough to ride out a transient glitch, and a truly
dead server is handed over to `offline_skip_updates` quickly.

### `offline_skip_updates` — offline back-off

When a server exhausts its retries, it is marked **offline** and this many
update cycles are skipped before it is probed again. With `5`, a silent server
is re-polled every `(5 + 1) × update_interval` = **30 s**. As soon as it
answers a probe, it is marked online again and normal polling resumes —
no reboot or manual action needed.

## How the bus is shared

There is exactly **one wire and one conversation at a time**. ESPHome enforces
this with a two-level design:

1. Each `modbus_controller` (one per BMS/Balancer/Shunt) keeps its own small
   command queue and submits **one command at a time** to the shared `modbus`
   hub, waiting for the response (or the final failure) before submitting the
   next one.
2. The `modbus` hub owns the bus: a single FIFO transmit queue and a single
   "waiting for response" slot. It sends one frame, waits for the response or
   the `send_wait_time` timeout, applies `turnaround_time`, then sends the
   next frame in the queue.

A read of 33 consecutive registers is a **single Modbus transaction**:
one request frame (8 bytes) and one response frame (71 bytes).

## What happens every 5 seconds — all 24 servers responding

At each `update_interval` tick, all 24 controllers queue their read command.
The hub then works through them strictly one at a time:

```
tick (t=0)                                                        idle until next tick
 │                                                                        │
 ▼                                                                        ▼
 ├─ Server 1 ──┬─ Server 2 ──┬─ Server 3 ── ... ──┬─ Server 24 ──────────┤
 │             │                                                          │
 │  request  (8 bytes  ≈  4.6 ms at 19200 baud)                           │
 │  latency  (first byte after ≈ 10–30 ms)                                │
 │  response (71 bytes ≈ 40.7 ms at 19200 baud)                           │
 │  turnaround_time = 0 → next command immediately (spec silence ≈ 2 ms)  │
 │                                                                        │
 │  ≈ 55–75 ms per server                                                 │
 └── 24 servers ≈ 1.4–1.8 s total ────────────────────────────────────────┘
```

The whole cycle completes in well under 2 seconds, then the bus sits idle for
about 3 seconds until the next tick. Every controller drains its queue long
before its next update — there is no backlog and no starvation.

Approximate full-cycle duration for 24 servers × 33 registers:

| Baud rate | Per transaction | Full cycle (24 servers) | Headroom in 5 s |
|-----------|----------------|-------------------------|-----------------|
| 9600      | ≈ 100–120 ms   | ≈ 2.4–2.9 s             | ≈ 2×            |
| **19200** | **≈ 55–75 ms** | **≈ 1.4–1.8 s**         | **≈ 3×**        |
| 115200    | ≈ 15–35 ms     | ≈ 0.4–0.8 s             | ≈ 6×            |

## What happens when one server does not respond

Say Server 7 is disconnected or has crashed:

**First cycle after the failure**

```
... ─ Server 6 ─┬────────── Server 7 ──────────┬─ Server 8 ─ ...
                │                              │
                │  request → silence           │
                │  wait send_wait_time (200 ms)│
                │  retry   → silence           │
                │  wait send_wait_time (200 ms)│
                │  → give up, mark OFFLINE     │
                │                              │
                └── cost: (1+1) × 200 ms = 400 ms, then move on
```

The other 23 servers are read normally. Total cycle:
23 × ~65 ms + 400 ms ≈ **1.9 s** — still far below the 5 s budget, so nothing
piles up and every other controller keeps refreshing on time.

**Subsequent cycles**

Server 7 is offline: the next 5 update cycles skip it entirely (zero cost on
the bus). Every 30 s it is probed once (400 ms worst case). When it answers
again, it is marked online and rejoins normal polling from the next cycle.

**Why this matters — the same scenario with ESPHome 2026.7 defaults**

With `send_wait_time: 2000ms` and `max_cmd_retries: 4`, a single dead server
would cost `(1 + 4) × 2000 ms = 10 s` per cycle — **twice the entire
update_interval on its own**. The command queues fill faster than they drain,
and since bus access is not fairly arbitrated, the controllers at the end of
the line may **never** get their turn (some entities stop refreshing
indefinitely). This starvation issue is a long-standing architectural
limitation, exposed (not caused) by the new defaults, and is queued to be
fixed in a future release. Until then, the YamBMS values above keep the
worst-case cycle short enough that the problem cannot occur.

## Tuning guide

* **`send_wait_time`**: set it to the slowest observed "time to first byte" of
  any server on your bus, with generous margin. `200ms` is right for
  all-ESPHome/ESP32 buses. Raise it only if you see spurious timeouts on a
  device that is actually alive (check the logs for `Modbus command timed
  out`). Do **not** raise it "to be safe" — every dead-server event costs
  `(1 + max_cmd_retries) × send_wait_time`.
* **`turnaround_time`**: keep `0ms` for all-ESPHome devices. If a third-party
  device occasionally misses requests, try `5–20ms` before anything larger.
* **`modbus_baud_rate`**: higher is better for cycle time; `19200` gives a
  comfortable 3× headroom with 24 servers. Use `9600` only if your wiring is
  long or noisy.
* **`update_interval`**: with the timings above you could go down to 2–3 s if
  you want faster refresh; make sure the full cycle (table above) stays well
  below the interval, dead-server penalty included.
* **`offline_skip_updates`**: `(value + 1) × update_interval` is the re-probe
  period. `5` → every 30 s at a 5 s interval. Since a failed probe only costs
  400 ms, you can lower it to `3` for faster recovery detection with no
  measurable impact on the bus.

**Rule of thumb:**

```
worst-case cycle ≈ (N_online × per-transaction time)
                 + N_offline_being_probed × (1 + max_cmd_retries) × send_wait_time

→ keep this comfortably below update_interval
```
