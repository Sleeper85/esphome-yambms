# YamBMS changelog

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

* YamBMS 1.8.0 :
  * Set esphome `min_version` to `2026.8.0`
  * Updated HA dashboards `1.8.0` for the new Cut-Off Cell Voltage, Charger Offset V., C-Rate and Auto CCL Current Taper entities
  * Rewritten Cut-Off / EOC charging logic : adds a current deadband (rejects sensor noise / low-solar current limiting) and a minimum SoC gate before Cut-Off can be declared, extends the cut-off confirmation delay from 60s to 180s to reject transient voltage readings, see [release note](documents/README/changelog/Changelog_YamBMS_1.8.0_Cut-Off_charging_logic.md)
  * New select `Cut-Off Cell Voltage` : choose between `Max Cell Voltage` (default, conservative) and `Average Cell Voltage` (consistent charge termination voltage for packs with a runner cell, requires Auto CVL and/or Auto CCL for cell protection)
  * New sliders `Max charge C-Rate` / `Max discharge C-Rate` : the max charge/discharge current is now the lowest of the user slider, the BMS OCP safety margin, and battery capacity × C-Rate
  * Renamed `Inverter Offset V.` to `Charger Offset V.` and allowed negative values (-1V to +1V)
  * `Requested Charge Voltage (CVL)` calculation reworked : it is now built as a per-phase base target (`Bulk` → bulk voltage, `Float` → float voltage, `Stop` → nominal voltage) plus a common set of offsets (`Charger Offset V.`, `Auto CVL`, `Auto Float` and the new `Auto Custom CVL`, each `0` when its function is idle or disabled), instead of one hardcoded formula per phase ; `Stop` charging voltage target changed from `Rebulk V.` to nominal voltage, so the pack no longer sits on the very threshold that decides when to rebulk.
  * Auto CVL : rewritten from a per-second template sensor to an interval lambda, now exposed as two sensors (`Auto CVL` value + `Auto CVL Delta`) instead of one internal-only sensor ; it remains a `Bulk`-only correction, the `Float`/`Stop` slot of the new formula being left free for a future implementation
  * Auto Float : rewritten from a per-minute template sensor to an interval lambda, now exposed as two sensors (`Auto Float Voltage` value + `Auto Float Voltage Delta`) ; no behavior change
  * Auto EOC : new 1-hour grace period holding the last computed current after target time passes (instead of releasing to maximum current), smoothed remaining-capacity estimate between BMS 1% SoC steps to remove current sawtoothing, `Stop SoC` slider capped at 98% (100% could never trigger because SoC is clamped to 98% until end-of-charge)
  * New `Auto CCL Current Taper` function : tapers CCL from a configurable knee voltage/C-Rate down to a bulk C-Rate, then holds a configurable balance current while at bulk or after EOC ; release hysteresis and Balance Current max are now scaled to cell count/battery capacity instead of flat constants, and a NaN guard prevents a spurious taper during the boot transient, see [changelog](documents/README/changelog/Changelog_Auto_CCL_Current_Taper_1.1.2.md)
  * Fixed HA dashboards : `Auto CCL Current Taper` card's switch pointed to a non-existent entity id and never toggled
  * New substitutions `custom_ccl_derating_reason` / `custom_dcl_derating_reason` allowing a custom current-limiting source (e.g. added via `yambms_custom.yaml`) to report itself in the CCL/DCL derating reason sensor, and a similar `Auto Custom CVL` slot for voltage
  * Reworked Modbus timing options : `send_wait_time` is now a response timeout (default lowered from 2000ms to 200ms) and a new `turnaround_time` option was added; shared multi-node settings (`yambms_config.yaml`) updated accordingly
  * Improved PACE BMS Modbus : power is now computed from current × voltage instead of a raw register (fixes incorrect readings), improved offline detection
  * Sensors (Total Voltage, Current, Power, SoC, Requested CVL/DVL/CCL/DCL, etc.) now publish as unavailable (`NaN`) instead of `0` when no BMS is combined
  * Fixed `Installed Battery Capacity` frozen until reboot : the value was summed once per BMS at boot, so a BMS whose capacity was reconfigured at runtime kept contributing its old value ; each BMS now applies only the difference to the total, which still never shrinks when a BMS goes offline
  * Multi-inverter / multi-charger support : the requested CCL/DCL is now divided by the number of declared CAN/RS485 inverter interfaces, so several identical inverters/chargers sharing the same battery bank each receive their share of the limit instead of every unit requesting the full value, see [documentation](documents/README/YamBMS_functions.md#multi-inverter--multi-charger)
  * New `Combiner Stall` diagnostic sensor : reports which BMS or Shunt id the combiner pipeline is stuck on when `bms_id`/`shunt_id` numbering has a gap, instead of stalling silently with no combined values; added the new `Combiner Stall` diagnostic row in dashboard
  * New `Fake Equalizing` : BMS that balance their cells but never report a balancing flag had it hardcoded to `false`, so the Cut-Off timer ended the charge while the pack was still equalizing ; YamBMS now infers it, with no constant of its own - the voltage reference is the per-cell bulk setpoint (`bulk voltage / cell count`, so it follows the chemistry) and the spread reference is `bms_balance_trigger_voltage`, the threshold at which the pack's own balancer engages, which is 10 mV on a JK or a Seplos and 30 mV on an EG4, a pack reporting none at all simply never starting ; an external balancer keeps priority whenever one is online ; enabled by default for Seplos V3, Seplos V1/V2, EG4 LL v2 and JK RS485 DISPLAY, available for any other BMS, idea by [@haysdb](https://github.com/haysdb), see [changelog](documents/README/changelog/Changelog_Fake_Equalizing.md)
  * `bms_balance_trigger_voltage` is now a var on EG4 LL v2 and JK RS485 DISPLAY, which hardcoded it : declare your unit's actual balancing threshold at import, as Seplos already required. EG4 keeps `0.030` as its default, JK RS485 DISPLAY moves from `0.005` to `0.010` to match the JK factory default - note that this value also feeds 'Auto CVL'
  * Updated EG4 LL-V2 component to [v1.1.0](https://github.com/RAR/esphome-eg4-bms/releases/tag/v1.1.0) : fixes [issue 7](https://github.com/RAR/esphome-eg4-bms/issues/7), some EG4 LL-V2 units intermittently answer with a CRC-valid response whose register data is entirely zero, which was published as a real reading and collapsed SoC / voltage / capacity for one poll cycle ; those blocks are now rejected and no longer refresh the online tracker
  * PVbrain2 board split into two DevKitC-1 variants to follow the RGB LED / CAN TX pin swap between board revisions : `board_ESP32-S3_DevKitC-1_PVbrain2_LED-48.yaml` (DevKitC-1 V1.0, LED on GPIO 48 and CAN TX on 38) and `board_ESP32-S3_DevKitC-1_PVbrain2_LED-38.yaml` (V1.1, LED on GPIO 38 and CAN TX on 48), both including the common `board_ESP32-S3_DevKitC-1_PVbrain2.yaml` : include the one matching your board revision
  * New `loop_task_stack_size` option (8192/16384/32768) available on every board, to prevent stack overflow with a large number of BMS/entities, see [documentation](documents/README/LOOP_TASK_STACK.md)
  * Updated default PSRAM options for ESP-IDF 5.5+, see [documentation](documents/README/PSRAM_options.md)
  * Fixed incorrect Max/Min Cell Voltage scaling (×100 instead of ×1000) sent on the CAN bus for the Deye PCS protocol
  * `secrets.yaml` template renamed to `secrets_example.yaml` (copy it to your own gitignored `secrets.yaml`, as documented in Installation_procedure.md)
  * Merged [PR 308](https://github.com/Sleeper85/esphome-yambms/pull/308) Check if Auto SoC Limit has reached its target
  * Merged [PR 303](https://github.com/Sleeper85/esphome-yambms/pull/303) Auto CCL Current Taper
  * Merged [PR 290](https://github.com/Sleeper85/esphome-yambms/pull/290) Add grace period to Auto EOC
  * New documentation :
    * [Charging_a_battery_with_CVL_and_CCL.md](documents/README/Charging_a_battery_with_CVL_and_CCL.md)
    * [Understanding_ESPHome_Modbus.md](documents/README/Understanding_ESPHome_Modbus.md)
    * [How_to_perform_a_PR_to_the_dev_branch.md](documents/README/How_to_perform_a_PR_to_the_dev_branch.md)
    * [HA_entities_cleanup.md](documents/README/HA_entities_cleanup.md)

* YamBMS 1.7.0 :
  * Partial rewrite of `yambms_core` and merging of C++ code into a single lambda in several stages with increased datas control.
  * Added LVGL display dashboard for Waveshare Touch-LCD 4.3" and 7" (Blue Navy 800x480 design)
  * Fixed [issue 10](https://github.com/Sleeper85/esphome-yambms/issues/10) Sending CAN bus data before the end of the combination process
  * Fixed [issue 154](https://github.com/Sleeper85/esphome-yambms/issues/154) Add `Enerkey Balancers` balance stop diff voltage setting (register 0x1A)
  * Fixed [issue 160](https://github.com/Sleeper85/esphome-yambms/issues/160) The SOH sensor is interpreted as a battery percentage
  * Fixed [issue 182](https://github.com/Sleeper85/esphome-yambms/issues/182) Compliance of Auto functions for YamBMS 1.7.0
  * Fixed [issue 268](https://github.com/Sleeper85/esphome-yambms/issues/268) [Add an option] The inverter is not sending ACK CAN ID 0x305
  * Fixed [issue 282](https://github.com/Sleeper85/esphome-yambms/issues/282) JK errors_bitmask has been removed
  * Merged [PR 281](https://github.com/Sleeper85/esphome-yambms/pull/281) Add WS Touch-LCD-4.3B board 
  * Merged [PR 261](https://github.com/Sleeper85/esphome-yambms/pull/261) Add LilyGo T-Connect Pro Lite board (without screen)
  * Merged [PR 259](https://github.com/Sleeper85/esphome-yambms/pull/259) Add support for Rebulk Days
  * Merged [PR 258](https://github.com/Sleeper85/esphome-yambms/pull/258) Auto EOC: Factor in Auto SoC Limit for battery capacity calculation
  * Merged [PR 255](https://github.com/Sleeper85/esphome-yambms/pull/255) Add support for Auto SoC Limit
  * Merged [PR 236](https://github.com/Sleeper85/esphome-yambms/pull/236) Switch to VictronMPPT-ESPHOME fork
  * Merged [PR 235](https://github.com/Sleeper85/esphome-yambms/pull/235) Basen: Add "Enable communication" switch
  * Merged [PR 200](https://github.com/Sleeper85/esphome-yambms/pull/200) Add M5Stack Tab5 with LVGL display
  * Merged [PR 199](https://github.com/Sleeper85/esphome-yambms/pull/199) Add Ecoworthy BMS integration for YamBMS
  * Merged [PR 194](https://github.com/Sleeper85/esphome-yambms/pull/194) Component Fault Registry & Advanced LED Control
  * Merged [PR 178](https://github.com/Sleeper85/esphome-yambms/pull/178) Basen BMS: Add heating control
  * Merged [PR 170](https://github.com/Sleeper85/esphome-yambms/pull/170) Add Freenove S3 board
  * Merged [PR 162](https://github.com/Sleeper85/esphome-yambms/pull/162) PACE Sensor Fixes
  * Merged [PR 158](https://github.com/Sleeper85/esphome-yambms/pull/158) Automatically disable shunt when connected BMSs are going offline

* YamBMS 1.6.0 :
  * New dashboards `1.6.0`
  * Added `iBMS V3.3` board
  * Updated `JK-PB` readme with **V19** warning and SoC 100% reset solution 1 and 2
  * Added board option `UART flow control` allows you to activate a `talk_pin` for the UART of your choice (e.g. WS-RS485-CAN)
  * Added AtomS3 GPIOs for `Atomic RS485 base` (uart_esp_3)
  * Disabled the `reboot_timeout` after 15 minutes in case of WiFi unavailability
  * New `Hardware highlighted` documentation (LilyGo / Waveshare / M5Stack)
  * New readme for **LilyGo T-Connect, WS RS485-CAN and M5Stack AtomS3** boards
  * Improved documentation.
  * Fixed [issue 83](https://github.com/Sleeper85/esphome-yambms/issues/83) Add esphome-pace-bms
  * Fixed [issue 94](https://github.com/Sleeper85/esphome-yambms/issues/94) Multi-BMS Seplos V3 don't work
  * Fixed [issue 96](https://github.com/Sleeper85/esphome-yambms/issues/96) Improve the SoC returned at the end of discharge
  * Fixed [issue 100](https://github.com/Sleeper85/esphome-yambms/issues/100) Improve the BMS Seplos V1 V2 examples
  * Fixed [issue 102](https://github.com/Sleeper85/esphome-yambms/issues/102) Improve Remaining Capacity when using a shunt
  * Added [issue 106](https://github.com/Sleeper85/esphome-yambms/issues/106) [FEATURE REQUEST] Temperature-based current limiting
  * Fixed [issue 108](https://github.com/Sleeper85/esphome-yambms/issues/108) [WARNING] esphome::select::Select::state` is deprecated
  * Fixed [issue 122](https://github.com/Sleeper85/esphome-yambms/issues/122) Adjust `bms_name` in all example YAML to something unique
  * Fixed [issue 128](https://github.com/Sleeper85/esphome-yambms/issues/128) Align the names of the shunt entities
  * Fixed [issue 142](https://github.com/Sleeper85/esphome-yambms/issues/142) Maximum capacity needs to be increased for `JK_RS485` BMS
  * Merged [PR 76](https://github.com/Sleeper85/esphome-yambms/pull/76) Add `Auto EOC` function
  * Merged [PR 82](https://github.com/Sleeper85/esphome-yambms/pull/82) Add support for external balancer
  * Merged [PR 85](https://github.com/Sleeper85/esphome-yambms/pull/85) Adding `EG4 LLV2` BMS
  * Merged [PR 97](https://github.com/Sleeper85/esphome-yambms/pull/97) Add `Basen controller` version with talk/flow control pin
  * Merged [PR 99](https://github.com/Sleeper85/esphome-yambms/pull/99) Basen: Use new binary sensors for charging/discharging
  * Merged [PR 112](https://github.com/Sleeper85/esphome-yambms/pull/112) Adding `FLIP_C3` board
  * Merged [PR 117](https://github.com/Sleeper85/esphome-yambms/pull/117) Round requested charge/discharge current to nearest integer
  * Change [PR 119](https://github.com/Sleeper85/esphome-yambms/pull/119) Updated `Power` gauge (-10kW to 10kW)
  * Merged [PR 133](https://github.com/Sleeper85/esphome-yambms/pull/133) Add `Studer XTM-4000` to supported inverters
  * Merged [PR 142](https://github.com/Sleeper85/esphome-yambms/pull/142) Sub device support
  * Merged [PR 143](https://github.com/Sleeper85/esphome-yambms/pull/143) Improved `Cut-Off charging` logic equation and documentation
  * Merged [PR 147](https://github.com/Sleeper85/esphome-yambms/pull/147) Improved `CCL`, `DCL` and `Temp-based` current control
  * Merged [PR 155](https://github.com/Sleeper85/esphome-yambms/pull/155) Update temperature sensor filters to reduce noise

* YamBMS 1.5.8 :
  * New Dashboards `1.5.8` compatible with `CANBUS` and `RS485` inverter communication protocol
  * Added BMS `SEPLOS V3` (beta)
  * Added YamBMS `Web Server v3`
  * Added `WiFi AP`
  * `WiFi AP` and `Web Server` credentials centralized in `secrets.yaml`
  * Added `WT32-ETH01` board
  * Fixed [issue 8](https://github.com/Sleeper85/esphome-yambms/issues/8) ETH01-EVO board - Davicom DM9051 SPI Ethernet Controller is now integrated in esphome `2025.7`
  * Fixed [issue 24](https://github.com/Sleeper85/esphome-yambms/issues/24) [JK-PB] SoC never reaches 100%
  * Fixed [issue 63](https://github.com/Sleeper85/esphome-yambms/issues/63) [JK RS485 component] Fix *.*_SCHEMA deprecations
  * Merged [PR 67](https://github.com/Sleeper85/esphome-yambms/pull/67) Add options to restrict max. charge and discharge current
  * Merged [PR 72](https://github.com/Sleeper85/esphome-yambms/pull/72) Add Pylontech RS485 inverter protocol
  * Merged [PR 74](https://github.com/Sleeper85/esphome-yambms/pull/74) `PYLON RS485` link status, Heartbeat and Requested Force Charge
  * Merged [PR 75](https://github.com/Sleeper85/esphome-yambms/pull/75) Round `Auto CCL` / `Auto DCL` values
  * Merged [PR 77](https://github.com/Sleeper85/esphome-yambms/pull/77) `PYLON RS485` prevent stale data on BMS disconnect
  * Merged [PR 80](https://github.com/Sleeper85/esphome-yambms/pull/80) BMS Modbus client: Return 0 when not online
  * Merged [PR 81](https://github.com/Sleeper85/esphome-yambms/pull/81) Fix balance trigger voltage for Basen and Deye

* YamBMS 1.5.7 :
  * Adapted the default `min/max` values ​​for the `Float` slider
  * Merged [PR 53](https://github.com/Sleeper85/esphome-yambms/pull/53) Add feature `Auto Float Voltage`
  * New dashboard for `Auto Float Voltage` function
  * Defining `state_class` for all YamBMS sensors
  * Set esphome `min_version` to `2025.6.0`
  * Fixed: change `Charge Status` to `Bulk` when `Force Charge` is requested
  * Merged [PR 70](https://github.com/Sleeper85/esphome-yambms/pull/70) Dashboards compatible with `HA 2025.7`
  * Merged [PR 70](https://github.com/Sleeper85/esphome-yambms/pull/71) Dashboard `max/min` cell voltage in color using macro
  * Removed all special characters in entities name + dashboards correction

* YamBMS 1.5.6 :
  * Fixed [issue 58](https://github.com/Sleeper85/esphome-yambms/issues/58) Compilation problem with `esphome 2025.5.0`
  * Fixed [issue 55](https://github.com/Sleeper85/esphome-yambms/issues/55) New CPU frequency option
  * Fixed [issue 65](https://github.com/Sleeper85/esphome-yambms/issues/65) JBD Circular dependency error 
  * Fixed [issue 35](https://github.com/Sleeper85/esphome-yambms/issues/35) BMS Charging Cycles Offset
  * Merged [PR 51](https://github.com/Sleeper85/esphome-yambms/pull/51) Support for RP2040 RPi Pico
  * Merged [PR 56](https://github.com/Sleeper85/esphome-yambms/pull/56) Add support for Basengreen BMS
  * Merged [PR 60](https://github.com/Sleeper85/esphome-yambms/pull/60) Fixes for new ESPHome and add of BMS Cycle Count offset
  * Merged [PR 61](https://github.com/Sleeper85/esphome-yambms/pull/61) Set Modbus BMS values to 0 when BMS goes offline
  * New `board_ESP32-S3_Touch-LCD-4.3.yaml` board
  * New `board_ESP32-S3_Touch-LCD-7.yaml` board
  * New `board_ESP32-S3_YBoard_DJK.yaml` board
  * New `board_RP2040_RPi_Pico.yaml` board

* YamBMS 1.5.5 :
  * New `main.yaml` with LP (local packages) and RP (remote packages) versions
  * New `board.yaml` with modular UART/CAN interfaces
  * The name of the JK `bms.yaml` is no longer linked to a specific model
  * SoC calculation is now based on remaining capacity for more accuracy (BMS only) [issues #39](https://github.com/Sleeper85/esphome-yambms/issues/39)
  * SoH calculation is moved to BMS level (for those who do not provide this information)
  * Improvement of the Victron SmartShunt doc [issues #38](https://github.com/Sleeper85/esphome-yambms/issues/38)

* YamBMS 1.5.4 :
  * New low SoC corrected at each BMS level (the corrected SoC is the one transmitted to YamBMS)
  * New BMS dashboard
  * New end of charge logic at each BMS level, the charge switch turns off when the cells are equalized (disabled by default)
  * Fixed `errors_bitamsk` for JK-PB RS485, test OK with YamBMS (forked component)

* YamBMS 1.5.3 :
  * Broadcasting JK-PB settings to all BMS set to OFF by default
  * Reorganizing the `board` folder and YAMLs (device_base.yaml moved to board.yaml)
  * `device_base.yaml` should no longer be part of `YamBMS_main.yaml`
  * New `RGB LED status` light effects (red, green, blue, cyan) as an `options` packages for `board.yaml`
  * Increased CPU frequency to `240Mhz` as an `options` packages for `board.yaml`
  * Added `ESP32 Generic`, `LilyGo T-CAN485`, `LilyGo T-Connect` and `XIAO` boards
  * Fixed SoC logic (low SoC will be detected at BMS level and no longer at YamBMS level)
  * Simplified combination logic (removal of the combine switch) + dashboard update
  * Check `Battery Capacity` is `> 0` before combining info (see [issue #14](https://github.com/Sleeper85/esphome-yambms/issues/14))
  * Improved alarm logic with a common `YamBMS errors bitmask` for all BMS models (see OTP vs UTP bug reported by @ChrisG)
  * Added [PR #7547](https://github.com/esphome/esphome/pull/7547) regarding publishing entities via the API
  * Removed `captive_portal` because it increases the `loop time` too much
  * `PSRAM` will no longer be enabled by default as this has a bad impact on `BLE BMS`

* YamBMS 1.5.2 :
  * Added shunt `Online Status` binary_sensor
  * Shunt combine condition based on the new binary_sensor `Online Status`
  * Logger `baud_rate: 0` by default (frees the 3rd UART and avoids some bugs like "WK2168 with canbus" or "BLE client with RS485 modbus")
  * Changed names of `bms` and `shunt` YAMLs for modbus `multi-node` solution
  * Added shared configuration file to simplify main YAML (centralization of parameters)
  * Simplification (fewer options) when importing `BMS / Shunt` YAMLs
  * New `multi-node` solution using `RS485 modbus` to communicate information to YamBMS
  * New board `espBerry` with `2-CH-CAN HAT`

* YamBMS 1.5.1 :
  * The conditions for `combining` BMS and the `charging` and `discharging` instructions no longer have any relation with the `errors_bitmask` sensor, the new system relies on the three **binary_sensor** `online status`, `charging allowed` and `discharging allowed` being linked to the status of alarms and switches.
  * The BMS combination procedure has been completely rewritten.
  * Improved structure and ID names of `bms.yaml`.
  * The `yambms.yaml` and `yambms_combine.yaml` global variable names have been changed for better code reading.
  * Improved code regarding the CAN bus `esp_light` status for boards without integrated LED.
  * New `Atom S3R` board and `Smartshunt BLE` shunt.
  * New `JBD`, `Seplos V1 V2`, `JK-B RS485` (display port) and `FAKE` BMS.
  * New `YamBMS DEMO` YAML and firmware offered to test and discover how `YamBMS` works.
  * New management of temperature sensors (no longer limited to two sensors).
  * **@Der_Hannes** fixed the AtomS3 `black screen` issue (with **esphome > 2024.7.3**) and developed new code for display management based on the [ili9xxx](https://esphome.io/components/display/ili9xxx.html) platform.
  * `Auto CCL/DCL` functions have been fixed to work with `JK-PB` and `new JK-B` BMS, [see this issue](https://github.com/Sleeper85/esphome-yambms/issues/11).
  * The `UVPR` and `OVPR` sensors are no longer used and replaced by `UVP` and `OVP` to ensure operation with all BMS.
  * **@txubelaxu** fixed a bug in the `JK-PB RS485` component that could cause a false battery voltage value to be sent, [see this issue](https://github.com/Sleeper85/esphome-yambms/issues/10).
  * Improved documentation, added a `HowTo` to create its main YAML, warning about galvanic isolation.

* CANBUS 2.3.7 : If there is no response from the inverter, the time before a new communication test has been reduced from `120s` to `60s`, added Victron `0x372` nbr. of modules `blocking charge/discharge`.

* YamBMS 1.4.5 : Changed the way to configure WiFi/Ethernet network, added `ESP32-C3 ETH01-EVO` ethernet board, reduction of the number of YAML bms files, UART `rx_buffer_size` is set to `512` by default for JK-B and JK-PB, new JK-BMS BLE sensors (last commits of @syssi) and new BLE `standard` version

* CANBUS 2.3.6 : Sending CAN frames stops immediately if there are no combined BMS

* YamBMS 1.4.4 : Multi-shunt support, Simplified and new YamBMS option `battery chemistry`, slider `min/max` values ​​are automatically configured based on the battery chemistry and cell count, added `YamBMS Fallback Hotspot`, added YamBMS `Update service`, added PVbrain2 and Atom Matrix board, added PSRAM settings YAML (not enabled by default), new MIN/MAX temperature sensor, added DC current icon, fixed dual sensor `Cell UVPR (MAX)` bug, Improved `combine` code, Breaking change : Atom S3 `GPIOs 1 and 2` reversed

* CANBUS 2.3.5 : New MIN/MAX temperature / sensor ID, Improved Victron protocol (online/offline battery modules, installed/available battery capacity)

* CANBUS 2.3.4 : Fixed bug of canbus link validation without inverter connected

* YamBMS 1.4.3 : Added Victron and Junctek KH-F `Shunt` support and `Requested Force Charge` function based on `SoC start/stop`, new `Total Daily Energy` sensors

* CANBUS 2.3.3 : Added `Automatic` BMS name selection and `Requested Force Charge` Bit 3/4/5 (PYLON 0x35C)

* CANBUS 2.3.2 : Added `LuxPower` protocol with updated `can_id` 0x355, 0x356, 0x359 and 0x35C

* CANBUS 2.3.1 : Improved the procedure for sending canbus frames with reduced loop time, rewritten of the canbus link validation code and added `Inverter Heartbeat Monitoring` function

* YamBMS 1.4.2 : Added new `Auto CVL Boost V.` and `Rebulk SoC` functions, new debug.yaml for ESP32 and ESP32-S3, improved code and comments

* YamBMS 1.4.1 : Rewriting of the alarm system, bug fixes and improvement of the charging logic (new status `Cut-Off`), icon allocation for each sensor, UART and CANBUS `!extend ${vars}`, New sensor `YamBMS Delta Cell V.`, Improved `Battery SOC` logic

* YamBMS 1.3.2 : New var `yambms_cell_count`, the BMS charge or discharge switches can be activated separately without causing the decombination of the BMS, new `minimal` version of the BMS YAML in order to reduce the loop time

* YamBMS 1.3.1 : First multi-BMS version named `YamBMS`
