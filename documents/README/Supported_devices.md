# YamBMS - Supported devices

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Supported BMS

* `JK` BMS (BLE / UART / RS485)
* `JBD` BMS (BLE / UART)
* `Seplos V1 V2 V3` BMS (RS485)
* `PACE` BMS (RS485)
* `BASEN` BMS (RS485)
* `DEYE` BMS (CAN)
* `Ecoworthy` BMS (RS485)

**Note: other BMS brands already integrated with ESPhome can be added easily.**

## Supported shunt

* `Victron Smartshunt` (UART)
* `Victron Smartshunt` (BLE)
* `Junctek KH-F` (UART / RS485)

**Note: other Shunt brands already integrated with ESPhome can be added easily.**

## Supported balancers

* `GW-24S4EB: NEEY/Heltec 4A Smart Active Balancer)` (BLE)
* `GW-24S4EB: NEEY 4A Smart Active Balancer 4th generation)` (BLE)
* `EK-24S15EB: (NEEY 15A Smart Active Balancer)` (BLE)
* `EK-24S10EB: (NEEY 10A Smart Active Balancer)` (BLE)

**Note: other Balancer brands already integrated with ESPhome can be added easily.**

## Supported MCU

This project works with various `ESP32` variants and also with the `Raspberry Pi Pico (RP2040)`.
Note that merging data from multiple BMS, balancers and shunts is resource-intensive, so I highly recommend a board based on the `ESP32-S3` with `PSRAM`.

| [AtomS3 Lite](Board_M5Stack_AtomS3.md) | [AtomS3](Board_M5Stack_AtomS3.md) | [AtomS3R (8MB PSRAM)](Board_M5Stack_AtomS3.md) |
| --- | --- | --- |
| <img src="../../images/MCU_AtomS3_Lite.png" width="300"> | <img src="../../images/MCU_AtomS3.png" width="300"> | <img src="../../images/MCU_AtomS3R.png" width="300"> |

| [LilyGo T-CAN485 (ESP32)](https://github.com/Xinyuan-LilyGO/T-CAN485) | [LilyGo T-Connect (ESP32-S3)](Board_LilyGo_T-Connect.md) | [Waveshare ESP32-S3-RS485-CAN](Board_Waveshare_ESP32-S3-RS485-CAN.md) |
| --- | --- | --- |
| <img src="../../images/MCU_ESP32_LilyGo-T-CAN485.jpg" width="300"> | <img src="../../images/MCU_ESP32-S3_LilyGo-T-Connect_1.jpg" width="300"> | <img src="../../images/MCU_ESP32-S3_WS-RS485-CAN_1.png" width="300"> |

| [ESP32 DevKit-V1](Board_Build_your_own_PCB.md) | [ESP32-S3 DevKitC-1](Board_Build_your_own_PCB.md) | [ESP32-C3 ETH01-EVO](https://a.aliexpress.com/_Ey29fog) |
| --- | --- | --- |
| <img src="../../images/MCU_ESP32-DevKit-V1.jpg" width="300"> | <img src="../../images/MCU_ESP32-S3-DevKitC-1.png" width="300"> | <img src="../../images/MCU_ESP32-C3_ETH01-EVO.png" width="300"> |

| [Olimex ESP32-EVB](https://github.com/OLIMEX/ESP32-EVB) | [espBerry + Waveshare 2-CH CAN HAT](https://copperhilltech.com/esp32-development-board-with-dual-isolated-can-bus-hat/) |
| --- | --- |
| <img src="../../images/MCU_ESP32-EVB.jpg" width="300">| <img src="../../images/MCU_ESP32-DevKitC_espBerry_2-CH-CAN.png" width="300"> |

## Supported CAN bus transceiver

**Note: some inverters only accept a CAN bus at 3.3V in this case please choose the SN65HVD230 chip.**

| TJA1050 (5V) | [TJA1051T (5V)](https://a.aliexpress.com/_EIdl3b5) | [SN65HVD230 (3V3)](https://a.aliexpress.com/_Evq9Ra7) |
| --- | --- | --- |
| <img src="../../images/CAN_Transceiver_TJA1050.png" width="300"> | <img src="../../images/CAN_Transceiver_TJA1051.jpg" width="300"> | <img src="../../images/CAN_Transceiver_SN65HVD230.jpg" width="300"> |

| [M5Stack Atomic CAN Base (isolated)](https://docs.m5stack.com/en/atom/Atomic%20CAN%20Base) | [M5Stack CAN Unit (isolated)](https://docs.m5stack.com/en/unit/can) | [MCP2515 (5V)](https://a.aliexpress.com/_EGPcjhZ) |
| --- | --- | --- |
| <img src="../../images/CAN_Transceiver_M5Stack_Atomic_CAN_Base.png" width="300"> | <img src="../../images/CAN_Transceiver_M5Stack_CAN_Unit.png" width="300"> | <img src="../../images/CAN_Transceiver_MCP2515.png" width="300"> |

## Supported RS485 transceiver

| [M5Stack RS485 Unit (isolated)](https://docs.m5stack.com/en/unit/iso485) | [RS485 isolated board (high speed dual)](https://a.aliexpress.com/_EueIZT5) | [RS485 Two-way Converter](https://electronics.stackexchange.com/questions/244425/how-is-this-rs485-module-working) |
| --- | --- | --- |
| <img src="../../images/RS485_Transceiver_M5stack_SKU-U094_RS485_Isolated_Unit.png" width="300"> | <img src="../../images/RS485_Transceiver_isolated_high_speed_dual_board.png" width="300"> | <img src="../../images/RS485_Transceiver_Two-way_Converter.jpg" width="300"> |


## Supported inverters

Inverters supporting CAN PYLON/Goodwe/SMA/Victron Low Voltage protocol should work, check your inverter manual to confirm.

The following are confirmed and known to work:

| Brand | Model | Inverter bat. mode | CAN/RS485 protocol | Remarks | Reported by |
| --- | --- | --- | --- | --- | --- |
| Deye | SUN-3.6K-SG03LP1-EU | Lithium 00 | CAN : PYLON 1.2 | --- | [@Der_Hannes](https://diysolarforum.com/members/der_hannes.16949/) |
| Deye | SUN-5K-SG03LP1-EU | Lithium 00 | CAN : PYLON 1.2 | --- | [@vdiex](https://github.com/vdiex), [@arzaman](https://github.com/arzaman), [@widget4145](https://diysolarforum.com/members/widget4145.110784/) |
| Deye | SUN-6K-SG03LP1-EU | Lithium 00 | CAN : PYLON 1.2 | --- | [@Sleeper85](https://github.com/Sleeper85), [@Imanol82](https://diysolarforum.com/members/imanol82.122457/) |
| Deye | SUN-12K-SG04LP3-EU | Lithium 00 | CAN : PYLON 1.2 | --- | [@lucize](https://github.com/lucize), [@luckylinux](https://github.com/luckylinux), [@virus100b](https://github.com/virus100b), [@b1ggi](https://diysolarforum.com/members/b1ggi.120910/) |
| Goodwe | GW5048-ES | --- | CAN : PYLON V2 | --- | [@jirdol](https://github.com/jirdol) |
| Goodwe | GW5000S-BP | Goodwe LX U5.4-L | CAN : PYLON V2 | --- | [@Uksa007](https://github.com/Uksa007), [@OselDusan7](https://github.com/OselDusan7) |
| Goodwe | GW3600S-BP | --- | CAN : PYLON V2 | --- | [@OselDusan7](https://github.com/OselDusan7) |
| Sofar | ME 3000-SP | --- | --- | --- | [@starman](https://diysolarforum.com/members/starman.65151/) |
| Sofar | HYD 3600-ES | Automatic | CAN : PYLON 1.2 | A 120 Ohm resistor had to be added on the Sofar side. | [@chaosnature](https://diysolarforum.com/members/chaosnature.64395/) |
| Sofar | HYD 5000-ES | --- | --- | --- | [@Paulfrench35](https://diysolarforum.com/members/paulfrench35.78523/) |
| Sofar | HYD 5000-EP | --- | --- | --- | [@tonystrullu](https://diysolarforum.com/members/tonystrullu.91283/) |
| Growatt | SPF 5000ES | CAN L52 | CAN : PYLON 1.2 | --- | [@Paulfrench35](https://diysolarforum.com/members/paulfrench35.78523/), [@cjdell](https://github.com/cjdell), [@cinusik](https://diysolarforum.com/members/cinusik.109738/) |
| Solis | RHI-3.6K-48ES-5G | Pylon LV / AoBo | CAN : PYLON V2 / SMA | CAN transceiver 3V3 required (SN65HVD230) for Pylon LV mode. | [@cjdell](https://github.com/cjdell), [@MrPabloUK](https://github.com/MrPabloUK) |
| Solis | S5-EH1P4.6K-L | Pylon LV | CAN : PYLON V2 | CAN transceiver 3V3 required (SN65HVD230). | [@Baker0052](https://github.com/Baker0052) |
| Solis | S5-EH1P6K-L | AoBo | CAN : SMA | --- | [@MrPabloUK](https://github.com/MrPabloUK) |
| Solis | RHI-3K-48ES | AoBo | CAN : SMA | --- | [@chaosnature](https://diysolarforum.com/members/chaosnature.64395/) |
| LuxPower | LXP SNA 5K | Lithium 6 | CAN : LuxPower | --- | [@shvmm](https://github.com/shvmm), [@yur43](https://diysolarforum.com/members/yur43.121157/) |
| LuxPower | LXP-LB-US 10K | Lithium 6 | CAN : LuxPower | --- | [@Henny101](https://diysolarforum.com/members/henny101.67026/) |
| EG4 | 6000XP | Lithium 2 / Lithium 6 | CAN : PYLON 1.2 / LuxPower | --- | [@ChrisG](https://diysolarforum.com/members/chrisg.483/), [@SGB](https://diysolarforum.com/members/scrotpusgobblebottom.100804/) |
| EG4 | 12000XP | Lithium 6 | CAN : LuxPower | --- | [@andrewfraley](https://github.com/andrewfraley) |
| EG4 | 18kPV | Lithium 6 | CAN : LuxPower | --- | [@Maintman](https://diysolarforum.com/members/maintman.19007/) |
| Victron | Multiplus 24/1200/25-16 | CAN-bus BMS LV (500 kbit/s) | CAN : Victron | Plugged into Cerbo CAN port (must use supplied Victron terminator in the other port). | [@dmsims](https://diysolarforum.com/members/dmsims.23417/) |
| Victron | MultiPlus-II 48/10000/140 | CAN-bus BMS LV (500 kbit/s) | CAN : Victron | --- | [@cali-clim](https://diysolarforum.com/members/cali-clim.54284/), [@20after4](https://github.com/20after4) |
| MidNite Solar | MN15-12KW-AIO | PYLON | CAN : PYLON 1.2 | --- | [@goldserve](https://diysolarforum.com/members/goldserve.52541/), [@jahyde](https://diysolarforum.com/members/jahyde.7475/) |
| SRNE | HESP48120U200-H | UZE | CAN : PYLON V2 | Most PYLON-based protocols show same results. Inverter does not work in PYLON mode, UZE works. Incorrect temp reported. | [@ogremustcrush](https://diysolarforum.com/members/ogremustcrush.116979/) |
| Studer | XTM-4000 | Pylontech | CAN : PYLON V2 | DIP Switch in Xcom-CAN: 11000110 (1 to 8, ON==1). | [@kolins-cz](https://github.com/kolins-cz) |
| Schneider | XW Pro 6848 NA | Voltage Control Li-Ion | CAN : PYLON V2 | Requires enabling the CAN bus option `canbus_extended_ack:` to `true`. | [@AGDorsum](https://diysolarforum.com/members/agdorsum.29403/), [@ngustas](https://diysolarforum.com/members/ngustas.126045/) |
| SMA | Sunny Island | --- | --- | --- | --- |