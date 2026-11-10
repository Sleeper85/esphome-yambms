# Design decisions

Some parts of the codebase look more verbose or more redundant than they need to be. They are
deliberate. This page records why, so that a well-intentioned cleanup doesn't reintroduce a bug
that took a long time to find.

**Do not refactor anything listed here without discussing it first**, and read the rationale
before touching the code.

## Cut-Off / EOC logic

**File:** `packages/yambms/yambms_core.yaml`

The End Of Charge condition is deliberately compound. It has to distinguish a genuine EOC from a
charge current that is merely capped by low solar production. Collapsing it into a single
threshold or voltage comparison reintroduces false EOC on overcast days.

<!-- TODO maintainer: list the exact elements that must not be merged (timer, latched state,
compound conditions) — see v1.7.1. -->

## The combiner pipeline

**Files:** `packages/bms/bms_combine.yaml`, `packages/shunt/shunt_combine.yaml`,
`packages/yambms/yambms_core.yaml`

Every BMS and Shunt package instance runs the *same* interval lambda, and they coordinate through
a shared counter rather than through any central loop. Each instance only acts on the tick where
`var_to_combine_bms_number` equals its own `${bms_id}`, then increments the counter so the next
instance can run. `yambms_core.yaml` (STEP 2) waits until every device has been processed, then
resets the counters to `1` for the next round.

This is why `bms_id` **must start at 1 and be contiguous**. It is not a style rule and not only
about the bitmask index: with a gap in the numbering, the counter stops at the missing id, never
advances, and STEP 2 never fires. The whole pipeline deadlocks silently.

Include the BMS and Shunt packages in ascending id order. Out-of-order includes still converge,
but spread one round over several intervals instead of completing in one.

### `can_be_combined` is deliberately exhaustive

The condition in `bms_combine.yaml` checks every sensor the combiner will read. It is long on
purpose: a single missing or `NaN` value entering the totals corrupts the aggregate that drives
the inverter. Do not shorten it to a few representative checks.

Every entity in the condition is mandatory: a BMS with one value missing or `NaN` is not
combined.

The condition is evaluated in STEP 1, on the BMS's turn, and published to the `Can be combined`
binary sensor. Do not move it back into a template lambda: a template binary sensor with a lambda
runs it on every loop, about 60 times per second per BMS, for a value read once per round.

`shunt_combine.yaml` follows the same rules: its condition checks the `Combine enabled` switch,
`online_status` and the four values the combiner reads (`voltage > 0`, then `current`, `power`
and `soc` with `isnan()`), and it is evaluated in STEP 1 on the shunt's turn. A combined shunt
replaces the BMS values, so a `NaN` there would reach the inverter directly.

Note that the checks are not uniform, and the difference is deliberate:

- **Sensors use `!std::isnan()`, not `has_state()`.** ESPHome sets `has_state()` on every
  publication, a `NaN` included, so a sensor that has published `NaN` once passes it. A sensor's
  state starts at `NaN`, so `isnan()` also covers a sensor that never published.
- **Binary sensors use `has_state()`**, a `bool` cannot be `NaN`.

`total_voltage`, `battery_capacity`, `cell_ovp` and `cell_uvp` use `> 0` — a BMS reporting zero
for those is treated as not ready rather than as a valid reading. For `cell_ovp` and `cell_uvp` it
is also the only test that works: several packages (JK, KS, PACE) declare them as a `number`,
whose state starts at `0`, not `NaN`, so `isnan()` would combine the BMS before its protection
settings are read. `max_charge_current` and `max_discharge_current` use `>= 0`: `0 A` is a valid
limit that a BMS can announce, and it must not take that BMS out of the combination. A `NaN` still
fails the comparison, so a limit that was never received keeps the BMS uncombined.

### Combined by contribution, combined continuously, uncombined

Three distinct scopes in the same lambda, and they are not interchangeable:

- **By contribution** — `total_installed_battery_capacity` is a maintained total, not a per-round
  accumulator. Each BMS remembers the last capacity it contributed in
  `bms${bms_id}_installed_capacity` and applies only the *difference* to the total. So the
  installed capacity follows a capacity change made at runtime, without a reboot, while an
  offline BMS simply stops updating its contribution — which stays in the total. It represents
  the *installed* capacity and deliberately does not shrink when a BMS drops offline.
- **Not continuously** — the combined counter is incremented on the transition into the combined
  state, not on every tick.
- **Continuously** — the totals, bitmasks and min/max values are recomputed every round.

`total_installed_battery_capacity` must never be turned into a per-round accumulator reset in the
`Global vars reset` block like the other totals. Its sensor is polled independently of STEP 2 and
its state is written straight into CAN frame `0x379` with no `has_state()` guard, so a transient
zero would announce 0 Ah of installed capacity to the inverter.

### `bms_seen_online_bitmask` is never cleared

It records that a BMS has been online at least once since boot. `shunt_combine.yaml` uses it to
tell "this BMS is offline" apart from "this BMS was never there" — a shunt must not be
uncombined because of a BMS the user never installed.

### Cell numbers are offset per pack

The combiner reports `cell number + (${bms_id} × 100)`, so cell 8 of BMS 1 is reported as `108`
and cell 3 of BMS 2 as `203`. This makes the pack immediately identifiable in the dashboard. It
caps a pack at 99 cells, which is well beyond any realistic configuration.

### A shunt uncombine turns the user switch off, and does not turn it back on

When a BMS mapped to a shunt goes offline, `shunt_combine.yaml` switches `Combine enabled` off
and records which BMS caused it, so the diagnostic `State` entity can say so. Re-enabling is
deliberately manual: coming back online does not automatically restore the combination, because
the SoC reference has to be trusted before it is used again.

### The `{0}` sentinel in `bms_ids`

`shunt${shunt_id}_bms_map` defaults to `'{0}'` because the vector needs a non-empty initialiser,
and the loop skips id `0` (`if (!bms_id) continue;`). Do not "clean up" the zero — it is what
makes an unmapped shunt valid.

## CAN frame catalogue

**File:** `packages/yambms/yambms_canbus.yaml`

Several `can_id` values are reused with different payloads depending on the protocol:

| CAN ID | Frame | Protocol |
|---|---|---|
| `0x359` | 5 | PYLON |
| `0x359` | 24 | Deye PCS |
| `0x371` | 11 | SEPLOS |
| `0x371` | 28 | Deye PCS |

**A frame's identity is its internal frame number, never its CAN ID.** Do not merge two blocks
because they share a CAN ID — that would break both protocols at once.

Byte order is not uniform either: `0x373` sends min cell voltage before max, `0x361` sends max
before min. Both match their respective specifications. Do not "harmonise" them.

## Frame sequencing

**File:** `packages/yambms/yambms_canbus.yaml`

Each protocol is defined as a sequence of frame numbers emitted on a fixed interval, so a full
cycle lasts `interval × sequence length` — from a few hundred milliseconds to over a second
depending on the protocol. Some inverters are sensitive to that cadence. Do not change the
interval to make protocols "consistent" with each other.

When adding a frame to a sequence, remember that the sequence length is tracked alongside the
array. Keep the two in sync, or the new frame will silently never be emitted.

## The update and telemetry services must never block the loop task

**File:** `packages/yambms/yambms_service.yaml`

`http_request` runs synchronously on the ESP32 loop task. ESPHome arms the IDF task watchdog at
5s with `CONFIG_ESP_TASK_WDT_PANIC=y`, and feeds it at most every 1 s, so any single blocking
call has a **4s budget** before the device panics and reboots.

Two paths exceed that budget on a network that filters outbound traffic. Both were reproduced on
an OPNsense firewall and measured on hardware:

| Path | Blocking time | Bounded by |
|---|---|---|
| Port 80 dropped silently | 4.5s | `timeout`, whose ESPHome default is 4.5s |
| Port 53 filtered (drop **or** reject) | 7.0 s, fixed | nothing — `timeout` does not cover DNS |

The 7s figure is the lwIP resolver retry ladder (`1 + 1 + 2 + 3`s over `DNS_MAX_RETRIES`), and
it is deterministic to a few milliseconds. A reject is not faster than a drop: lwIP's UDP API has
no error callback, so the ICMP unreachable is counted and discarded, and the query still runs its
full budget. Only an actual DNS *answer* — including `NXDOMAIN` from a local resolver — fails fast.

This is why three separate settings are needed, and none of them is redundant:

- **`watchdog_timeout: 60s`** is the only thing that covers the DNS wait. It is never reached in
  normal operation, where a full request takes under 400 ms.
- **`timeout: 3s`** brings the socket phase back under the 4s budget. It does **not** help the
  DNS case.
- **The failure counter** (`yambms${yambms_id}_var_service_failures`) is what stops the loop from
  freezing for 7s every 6h, forever, on a device that will never reach the internet.

`my_network.is_connected()` is not a reachability test — it only proves the device holds an IP.
It is kept as a cheap first filter, but the counter is the real guard. Do not remove it on the
grounds that the connectivity check above it "already handles this".

The counter is incremented from `on_error`, which fires only when no connection could be made.
An HTTP error status still fires `on_response` and resets the counter, which is correct: the
network worked, so there is no freeze to protect against.

The POST is guarded by an `if` on the counter rather than nested inside the GET's `on_response`.
Nesting would stack one blocking request inside another on a loop task whose stack is 8192 B by
default — see [LOOP_TASK_STACK.md](../LOOP_TASK_STACK.md). It also avoids a second 7s freeze on
a filtered network, halving the worst case.

Reaching 3 failures disables both requests until reboot.

### Two services, one counter

The two requests are gated independently, by substitution and therefore at compile time:

| Substitution | Request | What it does |
|---|---|---|
| `yambms_update_service` | GET | checks the latest published version |
| `yambms_telemetry_service` | POST | sends the node's configuration |

They share **one** counter, and that is deliberate: the counter measures whether the network is
reachable, not whether a given endpoint answered. Both requests block the loop task the same way,
so either one is a valid source of that signal.

This is why the POST carries its own `on_error` / `on_response`, which looks redundant next to
the GET's. It is not. With `yambms_update_service: 'false'` there is no GET, and without those
triggers nothing would ever increment the counter — the POST would freeze the loop for 7s every
6h forever, which is exactly the bug the counter exists to prevent.

The one thing the two services share besides the counter is
`yambms${yambms_id}_var_service_round_failed`: cleared at the start of every round, raised by any
request that could not connect. The POST is skipped when it is set, so a round that has already
frozen the loop once does not freeze it a second time for nothing.

Keep that flag separate from the counter. The counter is cumulative and spans rounds; the
question the POST needs answered is "did a request fail *in this round*", which is not the same
question. Expressing it as `failures == 0` happens to work while the GET runs immediately before
the POST and always writes the counter, but it silently breaks with `yambms_update_service:
'false'`: nothing resets the counter before the guard, so the POST would stop for good after its
first failed round, and the counter would sit at 1 without ever reaching the threshold that
disables the service.

### The interval carries a `startup_delay`

An `interval:` does **not** wait a full period before its first run. The scheduler sets the first
execution at `now + random(0, min(period / 2, 5s))`, capped by `MAX_INTERVAL_DELAY = 5000` — see
the `first execution happens immediately after a random smallish offset` comment in
`core/scheduler.cpp`. A 6h interval therefore fires within 5 seconds of `setup()`.

Without `startup_delay`, that first request lands in the middle of boot: combiner init at
priority 600, the first CAN frames to the inverter, RS485 polling starting up. Whether it runs at
all comes down to a race with the WiFi association, since `is_connected()` is usually still false
that early. That race is also why the reported symptom was a reboot every 6h rather than a boot
loop — but it is a race, not a design, and a fast reconnect after OTA can win it.

`startup_delay: 5min` puts the request outside the boot window and makes the sequence
deterministic on a network that filters outbound traffic:

| t | What happens | `failures` |
|---|---|---|
| 5min | GET fails after 7s, POST skipped | 1 |
| 6h05 | same | 2 |
| 12h05 | same | 3 |
| 18h05 and later | condition is false, no request is made | 3 |

So a device that will never reach the internet freezes for 7s three times over 12 hours, then
never again. The counter is `restore_value: no`, so a reboot replays that sequence — acceptable
for a node meant to run for months, and the reason the threshold is not lower: a single transient
outage must not disable version checking for good.

A version check has no urgency, so the 5min delay costs nothing.

## A derived sensor is published by its source, not polled

**File:** `packages/base/device_base.yaml`

`esp32_uptime` formats the value of `esp32_uptime_sec` for humans. It used to do so from its own
`update_interval: 10s` lambda, reading `id(esp32_uptime_sec).state`.

Two independent pollers reading one another is a race. Each starts with its own random offset in
`[0, 5s)` — see the `startup_delay` note above — so on roughly half of boots the text sensor ran
first and formatted a state that had never been published. That state is `NaN`, and the
`float`→`int` conversion saturates to `INT32_MAX` on Xtensa, which the formatter prints as
`24855d 3h 14m 7s`. It reached the dashboard, the LVGL label, and the telemetry POST, where it
was stored server-side as a real record.

The source's `on_value` now publishes the text sensor, and the lambda formats `x` — the value
that was just published. The failure mode is not guarded against, it cannot occur.

Do not convert it back to a polled lambda with a `has_state()` guard. The guard would work, but
it leaves two pollers where one is enough, and it puts the ordering question back in front of
whoever edits the file next.

`esp32_date_time_now` keeps its own poller, because it has no source sensor to hang a trigger on.
There the guard is `now().is_valid()`, and it is the right tool: the problem is an NTP sync that
may not have happened yet, not a scheduling order.

## The inverter protocol is resolved once, never in the loop

**Files:** `packages/yambms/yambms_brand_registry.yaml`, `packages/yambms/yambms_canbus.yaml`,
`packages/yambms/yambms_rs485.yaml`

The protocol actually applied on a link is not readable from a single select. It is the result of
a resolution with two inputs: the `Protocol` select, and — when that one is on `Automatic` — the
`Inverter brand` select passed through the registry's mapping.

That resolution runs in a script, triggered at boot and on `on_value` of either select, and its
result is stored in `canbus${canbus_id}_active_protocol` / `rs485${rs485_id}_active_protocol`.
Everything else only reads that integer.

Do not inline the resolution back into the consumers. The 100 ms sequencing interval, the five
protocol branches and the four LuxPower payload tweaks would each redo a table lookup and a
series of `std::string` comparisons ten times a second, for a value that only changes when a user
touches a select.

Do not dispatch on `active_index()` either. That is what the code did before: `active_index() == 5`
meant LuxPower purely by convention of the option order, so reordering the select silently broke
four payload branches in different frames. The `YB_PROTO_*` constants are named, and the
conversion from option string to constant exists in exactly one place — the resolution script.

`on_value` is used and **not** `set_action`: `TemplateSelectWithSetAction::control()` fires the
set trigger *before* `publish_state()`, so a script called from `set_action` would read the
previous option.

### The resolution must not run during setup

`on_value` also fires when the select restores its value, at `setup_priority::HARDWARE` (800).
The telemetry slot, on the other hand, is reserved in `on_boot` at `priority: -100`. Between the
two, the vectors in `yambms_core.yaml` are still empty, so the script would index element `0` of
an empty `std::vector` and the device would crash on every boot. The registry's `std::function`
globals are at `HARDWARE` too, so calling them that early is a race of its own.

`canbus${canbus_id}_link_ready` / `rs485${rs485_id}_link_ready` is what closes both holes: the
script returns immediately until the slot has been reserved, and the reservation raises the flag
then runs the script explicitly. Do not drop that guard on the grounds that the `has_state()`
check above it already protects the script — it does not, it only proves the selects have a value.

### The `YB_PROTO_*` values are internal

They are never persisted, never published to Home Assistant and never sent to the telemetry
service — the label from `global_inverter_protocol_label()` is what leaves the device. So the
ranges can be renumbered or extended at any time with no impact on existing nodes.

The two invariants that do bind are elsewhere: the **order of the select options**, because
`restore_value` stores an index (append new brands and protocols at the end, never insert), and
the **labels**, because they carry the continuity of the collected telemetry.

### Turning the RS485 link off means invalidating its proxies

**File:** `packages/yambms/yambms_rs485_pylon.yaml`

`pylontech_rs485` is passive: it answers the inverter from the proxy sensors YamBMS feeds. Stopping
the 100 ms interval therefore does **not** stop the link — the proxies keep their last value,
`update_state_from_sensors_()` still returns true, and the component keeps answering with stale
data while refreshing `rs485_status`, which is why the status stayed ON.

The component's own fail-safe is a `NaN` on any of the eight sensors it checks. The `else` branch
of the interval publishes those `NaN` once per transition, guarded by
`rs485${rs485_id}_proxies_valid` so it does not run ten times a second.

Only those eight sensors matter — the ones read by `update_state_from_sensors_()`. Invalidating the
others would be harmless but pointless, and would hide which ones the contract actually depends on.

### On RS485 the protocol is compiled, the brand only gates it

**Files:** `packages/yambms/yambms_rs485.yaml`, `packages/yambms/yambms_rs485_pylon.yaml`,
`packages/yambms/yambms_rs485_voltronic.yaml`

`rs485_protocol` picks the implementation at compile time, and each implementation declares what
it is in `rs485${rs485_id}_compiled_protocol`. In `Automatic` the resolution script applies that
value and never derives a protocol from the brand: a node can only speak what was compiled into
it, and resolving anything else made the diagnostics describe a protocol that was not running.

Voltronic and MPP Solar are the reason this cannot be a brand mapping. On recent firmwares,
parameter `05` offers both `PYL` and `LIB` on RS485, so either implementation is a valid choice
for the same inverter and the brand says nothing about which one was compiled.

`LIB` is the one exception. It is a Voltronic protocol and no other brand can use it, so in
`Automatic` a node compiled for `LIB` stays silent for any other brand, and `Note` says why.
Forcing `LIB` is still possible, because an explicit protocol always takes priority over the
brand. Rebranded inverters are expected to select `Voltronic`. MPP Solar is not a rebrand, which
is why it has its own entry.

### Turning the LIB link off means moving its Modbus address

**File:** `packages/yambms/yambms_rs485_voltronic.yaml`

`modbus_server` has no off switch, and returning nothing from a `read_lambda` only turns the reply
into an exception frame, so the inverter still gets an answer on a link that should be silent.
`ModbusServerHub::find_device_()` matches the address on every request, so moving the server to
address `248` makes the hub drop the request instead. The 100 ms interval moves it back to `1`
only while `rs485${rs485_id}_active_protocol` is `LIB` **and** YamBMS is initialized
(`var_initialized` and at least one BMS combined).

The second condition is the gate the CAN and PYLON links already apply: no frame on CAN, `NaN`
proxies on PYLON. Without it, the LIB link answered during a boot or a BMS dropout, and its
`read_lambda`s converted the `NaN` values to integers, which is undefined. The status mirroring
still follows `active` only: an active link left silent serves no request, its `Status` goes
false and raises the fault, exactly like the other links during a dropout.

Do not replace this with reported charge and discharge limits of zero: the inverter would still
see a battery, on a link the user believes is off.

### `Disabled` unregisters the link instead of faulting it

**File:** `packages/base/device_base_fault_registry.yaml`

Turning a link off stops the frames, so the inverter stops acknowledging, the link timer expires
and the status binary sensor goes false. Fed straight into `global_update_fault()` that lights the
fault LED for something the user asked for.

The registry already had the right answer: state `2`, which both the master mask and the health
report ignore. `global_update_fault()` only takes a `bool`, so it can write `0` or `1` and nothing
else — hence `global_unregister_fault()`, added alongside it.

Do not use `Healthy` for a disabled link. It would clear the LED just as well, but the health
report would print `[ OK ]` for a link that sends nothing, which is worse than the bug it fixes.

The guard exists in **two** places and both are needed: the resolution script applies it when the
protocol changes, and the status sensor's `on_state` applies it on every subsequent state change.
Without the second one the link timer would re-raise the fault a few seconds later.

A link left at `Automatic` with no brand selected is deliberately **not** unregistered — it faults.
That is the signal telling the user the node was never configured, which is the whole point of the
1.8.0 breaking change.

### Both ACK triggers are registered

`canbus.cpp` matches a trigger on `can_id` **and** `use_extended_id`, so declaring `0x305` twice —
once standard, once extended — is not a conflict: only the one matching the received frame fires.
This is why the Schneider XW Pro extended ACK needs no configuration, and why the
`canbus_extended_ack` substitution was removed. Both triggers call the same script so the handler
is not duplicated.

## The CCL/DCL divider counts declared links, not active ones

**Files:** `packages/yambms/yambms_core.yaml`, `packages/yambms/yambms_canbus.yaml`,
`packages/yambms/yambms_rs485.yaml`

Each inverter link increments `yambms${yambms_id}_var_comm_interfaces_count` once, in its
`on_boot` at priority `-100`, and the requested CCL and DCL are divided by that counter. The
counter never goes down. A link whose `Protocol` is `Disabled`, a link left on `Automatic` with no
brand, and a link whose inverter stopped answering all keep dividing.

Do not make it count only the active links. In every case where a declared link is not active, the
inverter behind it may still be drawing from the bank:

- `Disabled` is meant to cut a link temporarily. The inverter is usually still connected to the
  bank and running on its own settings, and the share the others are not given is the margin it
  uses.
- `Automatic` with no brand is an unfinished configuration, and every link starts there after the
  1.8.0 breaking change. Excluding it would hand the full current to the first link configured.
- A lost link must never raise the current, or a transient communication loss would double the
  limit sent to the remaining inverters.

A link that is not wired to anything has no business in the YAML, so the divider is changed by
changing what is declared. This is why `YamBMS_Local_Packages_example.yaml` ships its RS485 link
commented out, like the Remote Packages template.

If this is ever revisited, count the excluded links and subtract them, never count the active ones.
A mask of active links is empty until the resolution script has run, which gives a divider of `1`
and the full current; a mask of excluded links defaults to the declared count.

## A UART is declared by the package that consumes it

**Files:** `packages/board/board_options_itf_uart_*.yaml`, every package taking a `*_uart_id`

The main YAML names a UART once, in the `vars:` of the package that uses it, and that package
imports the matching `board_options_itf_${xxx_uart_id}.yaml`. It replaces a two-step declaration,
an `uart_esp_N` include followed by a `!extend` of the baud rate, which could not reach a WK2168
channel: those live under `wk2168_spi[].uart[]`, so every consumer needed an `_expander` twin
without the `uart:` block.

### One importer per UART

Two imports of the same UART fail with `ID uart_esp_1 redefined`, on an expander channel too. Keep
it that way. Sharing a UART at two speeds has no valid meaning, and with the old `!extend` it did
not fail: the extended value simply won, so an inverter link declared at 115200 silently ran at
the 9600 of a BMS package on the same UART.

This is why bus-level packages import the UART, not the per-BMS ones: a bus package is included
once, the BMS packages on that bus several times.

### Each package keeps its key, `uart_baud_rate` stays internal

Every package exposes its own key (`rs485_uart_baud_rate`, `pace_modbus_baud_rate`,
`shunt_uart_baud_rate`...) and maps it to `uart_baud_rate` in the `vars:` of the import. Do not
expose `uart_baud_rate` itself: with `${uart_baud_rate | default(...)}` in every package, one value
in a root `substitutions:` block would override all the consumers of the node, defaults included.

The defaults live in that `| default()` and nowhere else:

- **Not in `substitutions:`.** Package substitutions are merged into one global block, so
  `bms_uart_baud_rate` would get the same value for JBD (9600), JK UART (115200) and JK Display
  (2400), with no error.
- **Not in the UART file.** It does not know who imports it, and a wrong speed is valid
  configuration that fails silently on the wire. This is what the old fixed `115200` hid: the JK
  UART, JK sniffer and Junctek packages only worked because that value happened to suit them.
- **Not as a fixed value.** A value written in the `vars:` of the import takes priority over the
  one passed by the user, who is ignored without a message.

Leave `| default()` out when the speed depends on the installation (PACE, EG4, Seplos, BASEN): a
missing key then fails validation instead of picking a speed.

`modbus_baud_rate` is the exception that keeps its place in `substitutions:`: `yambms_config.yaml`
shares it between the nodes of a multi-node setup from the root.

### `flow_control` is enabled by a var, so `min_version` is at least 2026.10.0

`uart_flow_control_pin` is passed like any other var of the import and reaches the UART file,
which includes `board_options_itf_uart_flow_control.yaml` only when it is defined. So no consumer
has to know about it.

`flow_control_pin: ${uart_flow_control_pin}` with an empty default is not an option, the UART
schema refuses a null pin. The `condition:` key of `!include` is what makes the pin optional, and
ESPHome 2026.8.0 ignores it: the file is included anyway and the configuration fails. Do not lower
`min_version` without replacing it.

This `!extend` is the last one on a UART. It is not exposed to the user, and it works whatever the
order of the packages.

### Expander channels

`uart_spi_N` and `uart_i2c_N` are numbered like the PVbrain2 connectors: `0` to `3` on bridge 0,
`4` to `7` on bridge 1. Do not shift them to start at 1, every existing wiring would move by one
channel.

Each channel adds itself with `!extend uart_bridgeN`, and the bridges are declared with an empty
`uart:` by `board_options_itf_wk2168_spi.yaml` or `board_options_itf_wk2168_i2c.yaml`.

A WK2168 channel has no `flow_control_pin`, so `uart_flow_control_pin` is ignored there, without a
message. Its RS485 transceivers must handle the direction automatically. The `_talk_pin` packages
are kept for that one case: they drive a plain GPIO from the component, which works on any UART.
Everywhere else `uart_flow_control_pin` replaces them, and the examples no longer show them.

The UART id must be readable when the `!include` filename is resolved. A value built from a
substitution declared in a package, such as `uart_${uart_hub_bus}_3`, is not, so write `uart_spi_3`.

## A CAN node is declared by the package that consumes it

**Files:** `packages/board/board_options_itf_canbus_*.yaml`, `packages/yambms/yambms_canbus.yaml`,
`packages/bms/bms_sensors_DEYE_CAN_top_*.yaml`

Same principle as the UART: the main YAML describes a link once, in the `vars:` of the package that
uses it. The mechanism is not the same, and the differences are deliberate.

### The file is picked by platform, not by id

`uart_esp_1` is bound to pins and says nothing about what is connected. A CAN node is the reverse:
its id is a role (`canbus_inverter_1`, `canbus_bms_1`) that users read and reuse, and the hardware
behind it is either of two controllers. Naming the file after the id would have replaced those
roles with `canbus_esp_1`-style names for no gain.

So the id stays free in `canbus_node_id` and `canbus_platform` picks the file, the way
`rs485_protocol` picks the RS485 implementation.

### `canbus_platform` has no default

A wrong default is valid configuration on the wrong pins, and it fails silently on the wire. A
missing key fails validation instead, with `Cannot load include with unresolved substitutions`.

### `external` declares nothing

The import is unconditional, so a node that already exists needs a file that adds nothing:

- the espBerry board declares its two nodes in its own board file ;
- a second link on the same node would otherwise fail with `ID canbus_inverter_1 redefined`.

`board_options_itf_canbus_external.yaml` is that file. `canbus_bitrate` has no effect there, the
bit rate is the one of the package or board that declares the node.

### One importer per node

As with a UART, two imports of the same node fail, and that should stay so. This is why only the
Deye `top` packages import the node: the `module` packages are included several times on one bus
and only add `on_frame` triggers with `!extend`.

In the Deye packages `canbus_id` holds a node id, while in `yambms_canbus.yaml` it is a number. The
`top` packages map it with `canbus_node_id: ${canbus_id}` so that the examples keep their key.

`board_options_itf_canbus_mcp2515.yaml` declares its own `spi:` bus, so importing it twice fails
with `ID mcp2515_spi_bus redefined`. A board with two MCP2515 declares them itself and uses
`external`, as the espBerry does.

### `canbus_bit_rate` stays internal

The reasoning is the UART one: the default lives in the `| default()` of the consumer, not in the
CAN file nor in `substitutions:`. `esp32_canbus_bitrate` and `mcp2515_canbus_bitrate` were removed,
the bit rate is not a property of the controller but of the bus.

### The bit rate is set at compile time, the protocol is not

`canbus_bitrate` is compiled in, and nothing in YamBMS changes it at runtime, while the `Protocol`
select does change at runtime. So a protocol that does not run at 500 kbps cannot work from the
select alone: the user must also set `canbus_bitrate`. Any such protocol needs a `Note` in
`yambms_brand_registry.yaml` that says so.

## Empirical constants

Some constants were found by trial on real hardware and must not be rounded or harmonised.

<!-- TODO maintainer: list them here, in the form "do not lower <value> below <threshold>, or
<symptom>" — at minimum loop_task_stack_size, update intervals, RS485 timings. -->
