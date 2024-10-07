# YamBMS - ESP32 or ESP32-S3

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Number of BMS supported

**Warning:** BMS monitoring with `UART` or `RS485` is recommended, however, if you want to monitor your BMS with `Bluetooth`, please choose an `ESP32-S3`.

* 3x BMS with `Bluetooth` (BLE stack consumes significant amount of RAM on device and can cause crash and reboot)
* 3x `JK-B` BMS with `UART`
* several `JK-PB` BMS with `RS485` (already tested with 7 BMS)

Note: these are theoretical limits, not all combinations have been tested.

## UART/IO Expander

It would be possible to add one or more [WK2168 4x UART expander](https://esphome.io/components/weikai.html) to increase the number of BMS monitored with `UART`.

## Build your own PCB

This is an example of an ESP32 DevKit V1 30 pin board powered by the BMS.

![Image](../../images/PCB_ESP32_JK-BMS-CAN_powered_by_JK-BMS.png "PCB ESP32 JK-BMS-CAN powered by JK-BMS")

![Image](../../images/PCB_ESP32_JK-BMS-CAN_Prototype.jpg "PCB ESP32 JK-BMS-CAN powered by JK-BMS")
