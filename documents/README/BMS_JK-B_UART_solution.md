# YamBMS - JK-B BMS UART Solution

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## External component

[esphome-jk-bms](https://github.com/syssi/esphome-jk-bms) by [@syssi](https://github.com/syssi)

## Schematic and setup instructions

> [!CAUTION]
> The `GND` of the `JK-B GPS port` is directly connected with the `B-` of your battery. Even if your BMS is in protection or stopped you can measure the `full voltage` between this `GND` and `B+`. This therefore presents a risk of `bypass` of the BMS `P-` and can be dangerous if the GND of your ESP32 is connected to the GND of your inverter or a measurement shunt for example.
> I therefore strongly advise you to achieve galvanic isolation between your ESP32 and the `UART-TTL` of the `JK-B GPS port`.

## Galvanic isolation of the `UART-TTL` connection

> [!CAUTION]
> `V1` and `V2` must be isolated and cannot come from the same source. `V1` (JK GPS port side) can be powered by the `3V3` of the ESP32 via a `DC-DC isolator` (**B0303S = 3V3-to-3V3**), `V2` (ESP32 side) is powered directly by the `3V3` of the ESP32.

```
┌────────────┐   |         ┌──────────┐             ┌───────────┐
│            |   └─3V3--V1>│          |<V2---3V3---<|           |
│   DEVICE   │<RX-------AO<│ UART-TTL │<AI-------TX<|   ESP32   |
│   JK BMS   │>TX-------AI>│ ISOLATOR │>BO-------RX>|           |
│            │<----GND---->│          │<----GND---->|           |
└────────────┘             └──────────┘             └───────────┘
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

### Atom S3 (ESP32-S3)

> [!CAUTION]
> The diagram below does not show the galvanic isolation of the `UART-TTL` connection !

The GPIOs are preconfigured in the `packages/board/board_atom-s3-lite.yaml` file.<br>
You need to import this YAML into the main YAML.

```
              UART-TTL               RS232-TTL                   CAN BUS
┌──────────┐            ┌──────────┐             ┌────────────┐              ┌──────────┐
│          │<TX------RX>│2        5│<TX-------TX>|            |              |          |
│  JK-BMS  │<RX------TX>│1        6│<RX-------RX>| CA-IS3050G |<---CAN H --->| Inverter |
│          │<----GND--->│   ESP32  │             |    CAN     |<---CAN L --->|          |
│          │     5V---->│5V     3V3|             |            |              |          |
└──────────┘            └──────────┘             └────────────┘              └──────────┘

```

### Atom Lite (ESP32-PICO)

> [!CAUTION]
> The diagram below does not show the galvanic isolation of the `UART-TTL` connection !

The GPIOs are preconfigured in the `packages/board/board_atom-lite.yaml` file.<br>
You need to import this YAML into the main YAML.

```
              UART-TTL               RS232-TTL                   CAN BUS
┌──────────┐            ┌──────────┐             ┌────────────┐              ┌──────────┐
│          │<TX------RX>│26      22│<TX-------TX>|            |              |          |
│  JK-BMS  │<RX------TX>│32      19│<RX-------RX>| CA-IS3050G |<---CAN H --->| Inverter |
│          │<----GND--->│   ESP32  │             |    CAN     |<---CAN L --->|          |
│          │     5V---->│5V     3V3|             |            |              |          |
└──────────┘            └──────────┘             └────────────┘              └──────────┘

```

### Generic ESP32 DevKit V1 30 pin

> [!CAUTION]
> The diagram below does not show the galvanic isolation of the `UART-TTL` connection !

The GPIOs are preconfigured in the `packages/board/board_esp32-devkit-v1.yaml` file.<br>
You need to import this YAML into the main YAML.

```
3V3 CAN bus

              UART-TTL               RS232-TTL                 CAN BUS (3V3)
┌──────────┐            ┌──────────┐             ┌────────────┐              ┌──────────┐
│          │<TX------RX>│16      23│<TX-------TX>|            |              |          |
│  JK-BMS  │<RX------TX>│17      22│<RX-------RX>| SN65HVD230 |<---CAN H --->| Inverter |
│          │<----GND--->│   ESP32  │<----GND---->|    CAN     |<---CAN L --->|          |
│          │     5V---->│VIN    3V3│<----3V3---->|            |              |          |
└──────────┘            └──────────┘             └────────────┘              └──────────┘


5V CAN bus

              UART-TTL               RS232-TTL                 CAN BUS (5V)
┌──────────┐            ┌──────────┐             ┌────────────┐              ┌──────────┐
│          │<TX------RX>│16      23│<TX-------TX>|            |              |          |
│  JK-BMS  │<RX------TX>│17      22│<RX--4K7--RX>|  TJA1050   |<---CAN H --->| Inverter |
│          │<----GND--->│   ESP32  │<----GND---->|    CAN     |<---CAN L --->|          |
│          │     5V---->│VIN    VIN│<----5V----->|            |              |          |
└──────────┘            └──────────┘             └────────────┘              └──────────┘

```

### Schematic with addition of the UART-TTL to RS485 adapter sold by Jikong

```

              UART-TTL                  RS485              RS485-TTL              RS232-TTL                CAN BUS
┌──────────┐            ┌───────────┐           ┌────────┐           ┌─────────┐             ┌─────────┐              ┌──────────┐
│          │<----TX---->│Y    JK   Y│<A------A+>│        │<TX-----RX>│16     23│<TX-------TX>|         |              |          |
│  JK-BMS  │<----RX---->│W  RS485  W│<B------B->│ RS485  │<RX-----TX>│17     22│<RX--4K7--RX>| TJA1050 |<---CAN H --->| Inverter |
│          │<----GND--->│B Adaptor B│<---GND--->│To 3.3V │<---GND--->|         |<----GND---->|   CAN   |<---CAN L --->|          |
│          │<----VBAT-->│R          │           │        │<---3V3--->|  ESP32  |<----5V----->|         |              |          |
└──────────┘            └───────────┘           └────────┘           └─────────┘             └─────────┘              └──────────┘

```

### JK-B BMS UART-TTL GPS port

The `GPS` port sometimes called `RS485` is not an `RS485` port but `3V3 UART-TTL`.

```
# UART-TTL GPS port on JK-BMS (4 pin, JST 1.25mm pitch)
┌─── ─────── ────┐
│                │
│ O   O   O   O  │
│GND  RX  TX VBAT│ 
└────────────────┘
  │   │   │   | VBAT is full battery volatge eg 51.2V (possible to use it via an isolated DC-DC converter)
  │   │   └──── to TTL-isolator AI (input)
  │   └──────── to TTL-isolator AO (output)
  └──────────── to TTL-isolator GND
```

The UART-TTL (labeled as `GPS`) socket of the BMS can be attached to any UART pins of the ESP.<br>
A hardware UART should be preferred because of the high baudrate (115200 baud).<br>
The connector is called 4 pin JST with 1.25mm pitch.

![Image](../../images/JK-BMS_24S_GPS_port.png "JK-B BMS GPS port")