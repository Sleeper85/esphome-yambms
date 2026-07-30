# YamBMS - PSRAM options

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

Reference for `board_options_PSRAM_options.yaml`, the shared `sdkconfig_options`
included by every `board_options_PSRAM_*.yaml` board file.


## Which boards have PSRAM

PSRAM is a **property of the board or module, not of the chip family**. Two
boards built on the same chip may or may not have it.

| Chip | PSRAM | Modes | Notes |
|---|---|---|---|
| ESP32 | On some modules (WROVER and similar; WROOM has none) | Quad only | 8 MB chips expose only 4 MB through the cache window at a time |
| ESP32-S2 | On some modules | Quad only | |
| ESP32-S3 | On some modules (N8R2, N16R8 …) | Quad or octal | The `R` suffix in the module reference indicates PSRAM |
| ESP32-C3 / C6 / H2 | None | — | These options are inert |

**Check your module before choosing a mode.** Declaring `octal` on a board with
quad PSRAM — or on a chip that has no octal support at all — makes PSRAM
initialisation fail. It does not produce a clear error message; it shows up
later as random cache errors and unstable behaviour. The ESP-IDF boot log
reports what was actually detected.

On the original ESP32, 80 MHz PSRAM has additional constraints tied to the flash
clock, and early chip revisions require a cache workaround that ESP-IDF enables
automatically. If a board misbehaves at 80 MHz, 40 MHz is the safe fallback.

A board file declares the mode and includes this shared options file:

```yaml
psram:
  mode: octal
  speed: 80MHz

packages:
  psram_options: !include board_options_PSRAM_options.yaml
```

If a board has no PSRAM, every option below is silently ignored. They are
harmless, but they do nothing.

## Why these options exist

An ESP32 with PSRAM has two separate pools of RAM:

| Pool | Size | Speed | Used for |
|---|---|---|---|
| Internal RAM | A few hundred KB, fixed by the chip | Fast | Everything by default; the only pool usable for DMA |
| PSRAM | 2–16 MB depending on the module | Slower | Optional overflow, must be explicitly enabled |

Internal RAM is the scarce resource. A YamBMS master with 16 BMS creates roughly
1,400 entity objects on top of WiFi, the native API and several peripherals, and
internal RAM runs out long before PSRAM does.

Every option below does one thing: **move something out of internal RAM and into
PSRAM.**

> **Reference build.** The figures quoted in this document come from a 16-BMS
> master: ESP32-S3, octal PSRAM at 80 MHz, ESPHome 2026.7.3, ESP-IDF 5.5.5.
>
> ```
> DIRAM   202,299 / 341,760   (59.2 %)   ->   139,461 B free for the heap
> ```
>
> They are orders of magnitude, not universal constants. The original ESP32 in
> particular splits its internal RAM into separate instruction and data regions
> instead of the unified DIRAM pool the S3 uses, so its size report looks
> different. Compare against your own baseline rather than against these numbers.

## The options

### Moving the network stack to PSRAM

```yaml
CONFIG_SPIRAM_ALLOW_BSS_SEG_EXTERNAL_MEMORY: y
CONFIG_SPIRAM_TRY_ALLOCATE_WIFI_LWIP: y
```

**These two must be kept together.** The first turns `EXT_RAM_BSS_ATTR` in
ESP-IDF's `esp_attr.h` into a real section directive — without it the macro
expands to nothing. The second makes the network stack actually use it.
Removing either one cancels the benefit of both.

**Measured gain on the reference build: 12,308 bytes of internal RAM.** The
symbols moved are the socket table, `dns_table`, `dns_requests`, the `tcpip_*`
and `sntp_*` globals, and `select_cb_list`. Without these options internal
`.bss` would be 133,612 instead of 121,304, pushing DIRAM usage from 59.2 % to
62.8 %.

**Why this is safe.** Data in PSRAM is unreachable while the flash cache is
disabled, which is why PSRAM placement is normally risky. That only affects
interrupt handlers flagged to run from IRAM. LWIP has none — these globals are
touched exclusively from the `tcpip` task, in task context, where the cache is
always available.

**Cost:** marginally slower socket and DNS access. Irrelevant at ESPHome traffic
levels.

> **Reading the size report:** this segment is reported by `esp_idf_size` under
> *Flash Data / .bss*, not under internal RAM. That is a tooling artefact —
> flash `.rodata` and PSRAM share the same address window. The data really is in
> PSRAM.

### Internal RAM reservation

```yaml
CONFIG_SPIRAM_MALLOC_RESERVE_INTERNAL: "65536"
```

Bytes kept exclusively for allocations that cannot live in PSRAM — DMA buffers
and internal-only requests. Once free internal RAM drops to this level, generic
allocations fall back to PSRAM instead of starving the reserve.

ESP-IDF's default is 32,768. It is raised here because a YamBMS master runs
WiFi, the native API and several UART / SPI / CAN peripherals concurrently, all
of which need DMA-capable memory.

On a chip with less internal RAM than an S3, 65,536 is a large share of the
total. If free heap gets tight, this is one of the first values to reconsider.

### Allocation size threshold

```yaml
CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL: "4096"
```

Allocations up to this size go to internal RAM first; larger ones go straight to
PSRAM. ESP-IDF's default is 16,384.

**Tuning note.** Entity objects are typically 100–400 bytes, so at 4096 they all
still land in internal RAM. On a node short on internal memory, lowering this to
`"512"` pushes them into PSRAM and gives internal RAM back, at the cost of
slower access to every entity. Measure the free heap before and after — this is
a trade-off, not a free win.

DMA buffers request `MALLOC_CAP_DMA` explicitly and stay internal regardless of
this value.

### Bluetooth (BLE BMS only)

```yaml
CONFIG_BT_ALLOCATION_FROM_SPIRAM_FIRST: y
CONFIG_BT_BLE_DYNAMIC_ENV_MEMORY: y
```

**These two must also be kept together**, for the same reason as the pair above.
`BT_BLE_DYNAMIC_ENV_MEMORY` moves the Bluedroid host environment from static
`.bss` to dynamic allocation; `BT_ALLOCATION_FROM_SPIRAM_FIRST` sends those
allocations to PSRAM first. Alone, the first only shifts the cost from `.bss` to
the internal heap, and the second has nothing to redirect.

**Inert on RS485 / CAN-only builds.** Both are children of `CONFIG_BT_ENABLED`
in ESP-IDF's Kconfig tree, so they are dropped entirely when the Bluetooth
component is not compiled. Verified on a 16-BMS RS485 build: zero `CONFIG_BT_`
lines in the generated `sdkconfig`, zero Bluedroid symbols in the ELF, zero
bytes consumed.

**Caveat.** `BT_BLE_DYNAMIC_ENV_MEMORY` has a history of reliability reports
upstream. If BLE users hit crashes, remove this one first when bisecting;
`BT_ALLOCATION_FROM_SPIRAM_FIRST` alone is far less controversial.

**Note for BLE nodes.** The BLE controller needs internal RAM that PSRAM cannot
replace — buffers accessed during radio windows. A BLE node therefore has less
free internal RAM than the reference figures above.

## Verifying what actually applied

The generated `sdkconfig` is the only source of truth. ESPHome manages some
symbols itself, and those cannot be overridden from `sdkconfig_options`.

```bash
grep -E "SPIRAM|COMPILER_OPTIMIZATION" .esphome/build/<node>/sdkconfig.<node>
```

To confirm that data really landed in PSRAM, look for the external RAM section
in the linker map. This works on any chip:

```bash
grep -n '\.ext_ram\.bss' .esphome/build/<node>/build/<node>.map | head
```

If you prefer to inspect symbols directly, the address tells you where a symbol
lives — but the windows are chip-specific:

| Chip | Internal RAM | PSRAM |
|---|---|---|
| ESP32 | `0x3FF…` | `0x3F8…` – `0x3FB…` |
| ESP32-S3 | `0x3FC…` | `0x3C…` – `0x3D…` |

```bash
NM=$(find ~/.cache/esphome/idf/tools -name '*-elf-nm' | head -1)
$NM -nSC .esphome/build/<node>/build/<node>.elf | awk 'tolower($3)=="b"'
```

The compile size report is the quickest regression check. On the reference
build, internal RAM usage was 202,299 bytes (59.19 %). Any unexpected change
after editing these options means something behaved differently than documented
here — investigate before shipping.

## Note on `loop_task_stack_size`

This option is **not** part of this file, and is documented separately.

It is unrelated to PSRAM: it sizes the stack of the FreeRTOS task that runs
`setup()` and the main loop, and the required value depends on entity count, not
on available memory. It applies on every ESP32, with or without PSRAM, and
raising it consumes internal RAM that a board without PSRAM cannot recover
elsewhere.
