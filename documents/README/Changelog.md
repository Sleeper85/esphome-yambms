# YamBMS - Changelog

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

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
