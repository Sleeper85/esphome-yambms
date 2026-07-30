# YamBMS - loop_task_stack_size

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

Reference for the `loop_task_stack_size` option. Read this before changing it.

This document covers **raising** the value. Lowering it below the ESPHome
default is not documented here and is not recommended: the gain is a few
kilobytes, and the failure mode is a rare crash on a code path you did not test.

## Stack and heap in one minute

An ESP32 stores data in two very different ways, and both come out of the same
pool of internal RAM.

| | Stack | Heap |
|---|---|---|
| What it is | Scratch space for the function currently running | A reserve the program borrows from on demand |
| Reserved when | At compile time, one fixed block per task | At runtime, piece by piece |
| Holds | Local variables, return addresses | Objects whose count is not known in advance |
| In YamBMS | The local variables of `setup()` | Every sensor object, every API connection, every network buffer |
| Runs out how | Silently overwrites neighbouring memory | `malloc()` returns null |

The **stack** is a fixed-size block. ESPHome runs `setup()` and the main loop
inside a FreeRTOS task called `loopTask`, whose stack defaults to 8192 bytes.
That block is reserved at compile time and never grows.

The **heap** is everything left over. When YamBMS creates 1,400 sensor objects
at boot, they come from the heap. On a board with PSRAM, most of them end up in
PSRAM rather than internal RAM.

Raising `loop_task_stack_size` enlarges the stack block, which takes internal
RAM away from the heap — byte for byte, nothing else changes.

## Why the default is sometimes not enough

ESPHome generates `setup()` as a single flat function. Every entity
registration adds local variables to the same stack frame, so the frame grows
in direct proportion to the number of entities.

Measured on YamBMS with **YamBMS RS485 BMS (bms_combine_modbus_client.yaml)** packages:

```
setup() frame = 784 + 400 x nb_BMS bytes

  12 BMS -> 5,584 B   ~2,350 B left for everything else   -> boots
  16 BMS -> 7,184 B     ~760 B left for everything else   -> boot loop
```

That frame stays alive while `App.setup()` initialises every component, so the
remaining bytes must also cover component init, NVS reads, log formatting and
CPU register spills. When they do not fit, the overflow writes past the end of
the stack and corrupts whatever sits next to it in memory.

### Symptoms

- Boot loops that start only after adding BMS or entities, with no hard
  threshold — it scales with config size.
- `Guru Meditation Error` whose **type changes between reboots**: sometimes
  `LoadProhibited`, sometimes an Interrupt WDT, sometimes a cache error.
- No stack overflow message. The FreeRTOS canary is often skipped entirely by
  a large stack frame, so nothing warns you.
- Adjusting PSRAM options changes nothing, because the stack is not in PSRAM.

If a boot loop produces **no ESPHome log output at all** and a constant
`abort()`, that is a different problem — the board ran out of internal RAM
before startup. Lower the value rather than raising it, and reduce the config.

## Recommended values

| BMS per node | `loop_task_stack_size` |
|---|---|
| up to 6 | `8192` (ESPHome default — leave unset) |
| 7 to 24 | `16384` |
| 25 to 64 | `32768` (maximum accepted value) |

Values include roughly 4 KB of reserve above the measured `setup()` frame.

**These values are for YamBMS RS485 BMS (bms_combine_modbus_client.yaml).** BLE BMS instantiate
`esp32_ble_tracker` and one `ble_client` per BMS, which gives a different fixed
cost and a different slope. The model above has not been calibrated for them.

**The 16384 and 32768 rows assume a board with PSRAM.** Not because the stack
needs PSRAM — it never lives there — but because a config large enough to need
them will run out of heap long before it runs out of stack. On a board without
PSRAM, keep `8192` unless you have a measured reason not to.

## How to apply it

The value belongs in your main configuration, not in a board or PSRAM package:
it depends on how many BMS you configured, not on your hardware.

```yaml
substitutions:
  loop_task_stack_size: "8192"   # see LOOP_TASK_STACK.md before changing

esp32:
  framework:
    advanced:
      loop_task_stack_size: ${loop_task_stack_size}
```

## Check the cost before flashing

Raising this value consumes internal RAM permanently. The size report at the end
of every compile tells you the cost, with no hardware required:

```
RAM:   [======    ]  59.2% (used 202299 bytes from 341760 bytes)
```

Recompile after changing the value and compare. Going from `8192` to `16384`
should increase the used figure by exactly 8,192 bytes; `8192` to `32768` by
24,576. Anything else means something unexpected happened.

Leave yourself comfortable margin on the free figure. If free internal RAM drops
low, you trade a boot-time crash for runtime symptoms instead: API
disconnections, WiFi failing to reconnect, entities failing to initialise.

To confirm the value actually reached the firmware:

```bash
NM=$(find ~/.cache/esphome/idf/tools -name '*-elf-nm' | head -1)
$NM -SC .esphome/build/<node>/build/<node>.elf | grep loop_task_stack
```

The second column is the size in hex: `00002000` = 8192, `00004000` = 16384,
`00008000` = 32768.

## Confirm on hardware

The size report proves the cost. Only a running device proves the value is
sufficient. Add this temporarily and read the log after boot:

```yaml
esphome:
  on_boot:
    priority: -100.0
    then:
      - lambda: 'ESP_LOGW("mem", "loopTask HWM=%u B", uxTaskGetStackHighWaterMark(nullptr));'
```

`HWM` is the smallest amount of stack that was still free — the remaining
margin, in bytes. Below about 2,000, go up one step in the table.

Note that `loopTask` also runs the main loop forever, not just `setup()`. Rare
paths such as an OTA update, an API reconnection or verbose logging can push
deeper than boot does, so keep margin rather than tuning to the exact boot
figure.

## Calibrating for a different node type

If your node is not a standard **YamBMS RS485 BMS (bms_combine_modbus_client.yaml)** setup, measure your own frame
size instead of using the table. Add this and compile twice with a different
number of BMS:

```yaml
esphome:
  build_flags:
    - "-Wframe-larger-than=4096"
```

The compiler prints the frame size directly:

```
warning: the frame size of 7184 bytes is larger than 4096 bytes
```

Two data points give you the fixed cost and the cost per BMS. Add about 4 KB of
reserve and round up to the next step.
