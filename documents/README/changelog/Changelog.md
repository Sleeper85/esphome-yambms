# YamBMS changelog

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

* YamBMS 1.8.2 :
  * Set esphome `min_version` to `2026.11.0`
  * Updated EG4 LL-V2 component to [v1.1.1](https://github.com/RAR/esphome-eg4-bms/releases/tag/v1.1.1) : it builds on ESPHome 2026.11, which removed `format_hex_pretty()` ; v1.1.0 fails to compile with `'format_hex_pretty' was not declared in this scope`
  * ESPHome 2026.11 requires a `relation` on every sub-device : the BMS, Shunt, Balancer, sniffer, Deye, board, YamBMS and inverter link devices are all declared as `via`, which is how Home Assistant already showed them, so your devices and entities stay as they are
  * Waveshare ESP32-S3 Touch-LCD 4.3, 4.3B and 7 : removed the `enable_pin` workaround added in 1.8.1 for `Pin 2 is used in multiple places`, ESPHome 2026.11 now resolves this conflict itself ; the display and the backlight behave as before
  * JK RS485 (JK-PB, and recent JK-B using the `JK BMS RS485 Modbus V1.0` protocol) : the sniffer packages temporarily load the [JK RS485 components](https://github.com/Sleeper85/esphome-components/tree/dev) 1.2 from the `dev` branch, until 1.2 is released on `main`. Full list in the [JK RS485 changelog](https://github.com/Sleeper85/esphome-components/blob/dev/documents/README/changelog/Changelog.md). Main fixes :
    * JK-B package : toggling the `heating`, `display always on`, `disable temperature sensors` or `smart sleep on` switch **crashed and rebooted the ESP**, which also cut the CAN link to the inverter ; these switches now work, and only the toggled one is written to the BMS
    * Numbers are rounded instead of truncated before being written : `3.350 V` was written `3.349 V`
    * A BMS that goes offline no longer turns its status and alarm binary sensors `on` (charging, discharging, balancing, heating...) : they become unknown until the BMS answers again
    * Broadcast mode no longer applies to the `charging` and `discharging` switches : turning one off on a BMS turned it off on the whole parallel bank
    * Mode 2 : a BMS that stops answering is removed from `network nodes available` and found again when it comes back
    * The components build with ESPHome 2026.11 at log level `DEBUG`
  * JK RS485 : removed the `precharging` switch and the `operation status` and `battery type` text sensors, which never received a value ; Home Assistant may keep them as unavailable entities, which you can delete
  * JK RS485 : the `sniffer_protocol` var is no longer used (JK RS485 1.2 removed `protocol_version`) ; you can remove it from your YAML, keeping it does no harm

* YamBMS 1.8.1 :
  * Set esphome `min_version` to `2026.10.0`
  * New documentation :
    * [Upgrade to YamBMS 1.8.1](documents/README/changelog/Changelog_upgrade_to_YamBMS_1.8.1.md)
    * [Telemetry.md](documents/README/Telemetry.md)
  * New documentation for contributors :
    * [Project_structure.md](documents/README/dev/Project_structure.md)
    * [Coding_conventions.md](documents/README/dev/Coding_conventions.md)
    * [Design_decisions.md](documents/README/dev/Design_decisions.md)
  * Updated HA dashboards `1.8.1` with a markdown card for the new inverter link diagnostics (`Inverter link protocol`, `Inverter battery mode`, `Note`) and a system fault card
  * **Breaking change** - New `Inverter brand` select and reworked `Protocol` select : selecting your inverter brand is enough, the protocol follows ; a protocol chosen explicitly still takes priority over the brand. Both selects are renamed, so their stored value is reset : **the inverter link stays inactive until you select your inverter brand**, see [release note](documents/README/changelog/Changelog_Inverter_brand_and_protocol.md)

  * Removed the `YamBMS name` select : the manufacturer name sent on CAN frame `0x35E` is now derived from the protocol in use, which is what the `Automatic` mode already did ; the `GOODWE`, `SHEnergy` and `BYD` names are no longer selectable

  * **Breaking change** - A package that uses a UART now declares it itself from its `*_uart_id` var : remove the `board_options_itf_uart_*.yaml` includes and the `UART flow control` block from your YAML, otherwise ESPHome reports `Expected integer, but cannot parse ${uart_baud_rate}`. Each UART can only be used by one package : two packages on the same UART report `ID uart_esp_1 redefined`
  * Baud rates are set in the `vars:` of the package and keep their names ; packages that had none get `bms_uart_baud_rate`, `sniffer_uart_baud_rate` and `shunt_uart_baud_rate`, with the speed of the device as default
  * New `uart_flow_control_pin` var on any package using a native ESP32 UART, which replaces the `board_options_itf_uart_flow_control.yaml` include ; the `_talk_pin` packages stay available for the rare setups that need them but are no longer shown in the examples
  * WK2168 channels are now declared the same way : `board_options_itf_wk2168_spi.yaml` or `board_options_itf_wk2168_i2c.yaml` replaces the PVbrain2 files in your YAML, the `uartN_baudrate` substitutions and `uart_hub_bus` are removed (write `uart_spi_3`), and `board_options_itf_modbus_expander.yaml` and `shunt_combine_Victron_SmartShunt_UART_expander.yaml` are removed

  * **Breaking change** - A package that uses a CAN bus now declares its node itself : remove the `board_options_itf_canbus_*.yaml` includes from your YAML, otherwise ESPHome fails on the unresolved `${canbus_bit_rate}`, and add `canbus_platform` (`esp32_can` or `mcp2515`) to the `yambms_canbus.yaml` package and to the Deye `top` package. A node declared by the board, or a second link on the same node, uses `canbus_platform: 'external'`
  * The CAN bit rate is set with the new `canbus_bitrate` var (default `500kbps`), which replaces `esp32_canbus_bitrate` and `mcp2515_canbus_bitrate`
  * RS485 packages reorganised for the additional protocols to come : the file you include changes from `yambms_rs485_pylon.yaml` to `yambms_rs485.yaml`, which now takes a `rs485_protocol` var (`pylon` or `voltronic`) and includes the matching protocol implementation for you ; a node with several RS485 links on different UARTs can run a different protocol on each, one var per link ; `yambms_rs485_pylon_web_server.yaml` becomes `yambms_rs485_web_server.yaml` and includes the entry point itself : use it instead of `yambms_rs485.yaml`, with the same `vars:`, see [release note](documents/README/changelog/Changelog_Inverter_brand_and_protocol.md)

  * New diagnostic entities per inverter link : `Inverter link protocol` (what the link is actually doing, e.g. `Solis - CAN SMA`), `Inverter battery mode` (how to configure the battery type on the inverter, keyed on brand *and* protocol so that forcing a protocol never displays a wrong instruction) and `Note` (what is specific to that brand and protocol)
  * Renamed CAN protocol `PYLON 1.2` to `PYLON V1` and RS485 protocol `Pylontech` to `PYLON`
  * Schneider XW Pro : the extended 29-bit ACK is now handled automatically and the `canbus_extended_ack` substitution is removed - both the 11-bit and the 29-bit ACK are listened to at the same time, which the CAN component supports natively
  * A link whose protocol is set to `Disabled` no longer lights the fault LED : it is unregistered from the fault registry (state that the master mask and the health report both ignore) instead of being reported as failing, since it is a deliberate choice and not a communication loss ; a link left unconfigured still faults, on purpose
  * Changing the inverter brand or protocol now restarts the CAN frames immediately instead of waiting for the next 30s retry tick, so the link comes up as soon as the selection is made
  * Fixed the RS485 link staying up with `Disabled` : the proxy sensors kept their last value, so the Pylontech component went on answering the inverter with stale data and kept reporting its status as ON ; the sensors it checks are now invalidated when the protocol is off, which makes it stop answering and report the link as down
  * Fixed the CAN bus not stopping when the protocol was set to `Disabled` at runtime : the frame index kept its previous value and the last frame was re-emitted every 100 ms
  * Fixed the reported communication bus and protocol being overwritten when a node declares several inverter links : each link now owns its slot, and the telemetry reports every link instead of the last one
  * Auto EOC : new `Auto EOC Start Hour` / `Auto EOC Start Minute` define the charging window, which may cross midnight, and the target hour can be set from `0` to `23` (night charging from the grid) ; outside the window the status is `Wait: Starts at hh:mm` instead of `Stop: Target time passed`, the default start `0:00` keeps the daylight behaviour
  * `Daily Charging Energy` / `Daily Discharging Energy` (YamBMS and BMS) rounded to 10 Wh (`0.01 kWh`) instead of 1 Wh, to reduce the number of state changes recorded by Home Assistant
  * Fixed YamBMS `Daily Charging Energy` / `Daily Discharging Energy` jumping after a long period in the opposite direction : the unused power sensor was published as unknown, which ESPHome skips without advancing its time base, so the next reading was multiplied by the whole gap ; `Battery Charging Power` / `Battery Discharging Power` now publish `0 W` on the unused side, as the shunt already did, and also when no BMS is combined

  * The `Update service` switch is removed : the version check and the telemetry are now enabled separately with the `yambms_update_service` and `yambms_telemetry_service` substitutions (both `'true'` by default), see [Telemetry](documents/README/Telemetry.md)
  * Telemetry no longer sends the MAC address but a salted SHA-256 hash of it, shown in the new `Node ID hash` diagnostic entity so that you can quote it for support ; the uptime is now sent in seconds
  * The update and telemetry requests now go to `script.yambms.org`
  * Fixed `Uptime` sometimes showing `24855d 3h 14m 7s` after boot, on the dashboard, the LVGL display and in the telemetry : the text sensor could format the uptime before it had a value, it is now published by its source
  * Fixed `charging cycles` and `total charging cycle capacity` published as `0` after a reboot until the first BMS frame, which also landed in the Home Assistant long-term statistics : both are now unavailable during that time

  * Auto CCL : the max cell voltage used by the curve is now smoothed with a time-based moving average (`auto_ccl_max_cell_v_tau`, default `30`s, `0` disables), which stops the requested CCL swinging between about 8 A and 45 A near the top of charge ; a reading more than `auto_ccl_max_cell_v_guard` (default `5` mV) above the average still cuts the current at once
  * Auto CCL : new `auto_ccl_min_current` (default `1` A), Auto CCL never requests less, including above the end of its curve ; other limits can still request 0 A
  * A BMS reporting a charge (CCL) or discharge (DCL) limit of `0 A` now stays combined : a full battery at 0 A CCL, or an empty one at 0 A DCL, no longer drops out of the capacity, SoC and totals ; this applies to all BMS models, a limit not received yet still keeps the BMS uncombined
  * Deye CAN : the battery power sensors now follow `bms_update_interval` instead of updating every 60s
  * Fixed sensors `device_class` / `state_class` that Home Assistant reported or handled wrongly : power sensors in W declared as `current` (BASEN RS485, DEYE CAN module), Ah sensors carrying a class that does not accept Ah (BASEN RS485, DEYE CAN, JK RS485 Display, Modbus client), DEYE battery capacity moved from `total_increasing` to `measurement`
  * Fixed PACE BMS compilation with ESPHome 2026.9 / 2026.10
  * Fixed the Waveshare ESP32-S3 Touch-LCD 4.3, 4.3B and 7 boards failing validation on ESPHome 2026.10 with `Pin 2 is used in multiple places` ; the backlight stays under control of the LVGL designs
  * New board `board_ESP32-P4_Elecrow-CrowPanel-Advanced-7-10.yaml` (CrowPanel Advanced ESP32-P4) and new Blue Navy 1024x600 HA display design
  * Fixed [issue 332](https://github.com/Sleeper85/esphome-yambms/issues/332) YamBMS_RP_BMS_PACE_RS485_Modbus.yaml no longer compiles under esphome 2026-9-1
  * Fixed [issue 335](https://github.com/Sleeper85/esphome-yambms/issues/335) PACE / DEYE packages: compile errors on ESPHome 2026.9–2026.10 + Deye power updated only every 60 s + full Deye excluded from combine
  * Merged [PR 322](https://github.com/Sleeper85/esphome-yambms/pull/322) Add CrowPanel Advanced (ESP32-P4) board and Blue Navy 1024x600 HA display
  * Merged [PR 329](https://github.com/Sleeper85/esphome-yambms/pull/329) Auto CCL smooths max cell voltage
  * Merged [PR 331](https://github.com/Sleeper85/esphome-yambms/pull/331) Fix sensor device_class and state_class
  * Merged [PR 336](https://github.com/Sleeper85/esphome-yambms/pull/336) Fix hub daily energy by publishing 0 W on the unused charge/discharge sign
  * Merged [PR 337](https://github.com/Sleeper85/esphome-yambms/pull/337) Improve Deye support
  * Merged [PR 338](https://github.com/Sleeper85/esphome-yambms/pull/338) Auto EOC 24h charging window
  * Merged [PR 339](https://github.com/Sleeper85/esphome-yambms/pull/339) Round daily energy sensors to 10 Wh

* YamBMS 1.8.0 :
  * Set esphome `min_version` to `2026.8.0`
  * New documentation :
    * [Charging_a_battery_with_CVL_and_CCL.md](documents/README/Charging_a_battery_with_CVL_and_CCL.md)
    * [Understanding_ESPHome_Modbus.md](documents/README/Understanding_ESPHome_Modbus.md)
    * [How_to_perform_a_PR_to_the_dev_branch.md](documents/README/How_to_perform_a_PR_to_the_dev_branch.md)
    * [HA_entities_cleanup.md](documents/README/HA_entities_cleanup.md)
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
  * Fixed a reboot every 6h on networks that filter the ESP32 outbound traffic (port 80 or DNS blocked) : the update and telemetry requests blocked the device long enough to trigger the watchdog ; requests now time out after 3s, the first one waits 5min after boot, and the services stop until the next reboot after 3 failed attempts
  * Added `KS BMS` BLE support, fixed [issue 151](https://github.com/Sleeper85/esphome-yambms/issues/151) [ADD] Requesting KS BMS support
  * JK BLE : BMS alarms are now taken into account through the new `errors_bitmask_hex` of the JK BLE component, instead of always reporting no alarm
  * Web server authentication switched to `digest`
  * Fixed the `brightness not supported` warning logged on every status LED change on boards with a single-colour LED ; `rgb_order` replaced by `channel_colors` in the board files (deprecated by ESPHome, removed in 2027.3.0), to report in your own board file if you have one
  * CAN frame logs moved from `INFO` to `DEBUG` level
  * Merged [PR 308](https://github.com/Sleeper85/esphome-yambms/pull/308) Check if Auto SoC Limit has reached its target
  * Merged [PR 303](https://github.com/Sleeper85/esphome-yambms/pull/303) Auto CCL Current Taper
  * Merged [PR 290](https://github.com/Sleeper85/esphome-yambms/pull/290) Add grace period to Auto EOC

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
