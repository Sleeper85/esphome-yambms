# YamBMS - Galvanic isolation

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Galvanic isolation of the `UART-TTL` connection

> [!CAUTION]
> `V1` and `V2` (3V3 or 5V) must be isolated and cannot come from the same source. `V1` can be powered by the device or the `3V3` of the ESP32 via a `DC-DC isolator` (**B0303S = 3V3-to-3V3**), `V2` (ESP32 side) is powered directly by the `3V3` of the ESP32.

```
┌─────────────┐             ┌──────────┐             ┌───────────┐
│             |  3V3/5V--V1>│          |<V2---3V3---<|           |
│   DEVICE    │<RX-------AO<│ UART-TTL │<AI-------TX<|   ESP32   |
│ BMS / Shunt │>TX-------AI>│ ISOLATOR │>BO-------RX>|           |
│             │<----GND---->│          │<----GND---->|           |
└─────────────┘             └──────────┘             └───────────┘
```

Here are some components available on the market allowing you to set up galvanic isolation. The `UART-TTL isolator 2` seems a little better isolated with more space below the chip.

* [UART-TTL isolator 1](https://a.aliexpress.com/_EuXszn7)
* [UART-TTL isolator 2](https://a.aliexpress.com/_EItDRvX)
* [DC-DC isolator](https://a.aliexpress.com/_EIsPAoh)

![Image](../../images/UART-TTL_isolator_1.png "UART-TTL isolator example")

| [UART-TTL isolator](https://a.aliexpress.com/_EItDRvX) | [DC-DC isolator](https://a.aliexpress.com/_EIsPAoh) |
| --- | --- |
| <img src="../../images/UART-TTL_isolator_2.png" width="400"> | <img src="../../images/DC-DC_3V3-to-3V3_isolator.png" width="400"> |

### Another solution would be the use of M5Stack's isolated RS485 unit.

| [M5Stack RS485 unit (isolated)](https://docs.m5stack.com/en/unit/iso485) |
| --- |
| <img src="../../images/RS485_Transceiver_M5stack_SKU-U094_RS485_Isolated_Unit.png" width="400"> |
