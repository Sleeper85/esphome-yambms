# YamBMS - M5Stack Atom S3 (ESP32-S3FN8)

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> [!IMPORTANT]
> Atom S3 provides very few GPIOs without UART expander.
> BMS monitoring with `UART` or `RS485` is recommended.

## Number of BMS supported

* 2x BMS with `Bluetooth` (BLE stack consumes significant amount of RAM on device and can cause crash and reboot)
* 2x `JK-B` BMS with `UART/RS485` (the second UART must be soldered on the Atomic CAN base on GPIOs G7 and G8)
* several `JK-PB` BMS with `RS485` (already tested with 7 BMS)

Note: these are theoretical limits, not all combinations have been tested.

## UART/IO Expander

Theoretically, with the 4 GPIOs available, it would be possible to add one [WK2168 4x UART expander](https://esphome.io/components/weikai.html) for a total of 4x `JK-B` BMS monitored with `UART`.

## M5Stack Atom CAN Kit (the Plug & Play solution)

> [!IMPORTANT] 
> If you have JK-PB series BMS (inverter BMS) and want to monitor them via RS485, please read the [README](BMS_JK-PB_RS485_solution.md) dedicated to this topic.

If soldering or creating your own board seems complicated to you, know that it is possible to use the Atom CAN Kit from M5Stack.<br>

**Choose Atom S3 (display) or Atom S3 Lite + Atomic CAN base.**

- [Atom S3 - SKU:C123](https://docs.m5stack.com/en/core/AtomS3)
- [Atom S3 Lite - SKU:C124](https://docs.m5stack.com/en/core/AtomS3%20Lite)
- [Atomic CAN Base - SKU:A103](https://docs.m5stack.com/en/atom/Atomic%20CAN%20Base)

| Atomic S3 Lite | Atomic CAN Base |
| --- | --- |
| <img src="../../images/Atom_S3_Lite.png" width="450"> | <img src="../../images/CAN_Transceiver_M5Stack_Atomic_CAN_Base.png" width="450"> |

## Note regarding the sensors managing the display Backlight

* **Backlight control** : manual brightness control
* **Backlight max level** : limit the max brightness in general
* **Backlight Autodim level** : the desired brightness when dimmed down (set to 0 to switch off screen completely instead of dimming down)
* **Backlight Autodim time in min** :  time in minutes, after the screen will dim down (set to 0 to disable Auto dimming) 

Device will restore last screen brightness after boot, but the timer script does not get start automatically.
The auto dim timer gets initially started by pressing the screen button (which bumps up the brightness to 100% until the timer dims down then).

That seems to be the easiest and lightweight solution.
But i guess some user could be confused and expect from the device to react immediately after changing some parameters.