# Victron SmartShunt How To

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## UART : Schematic

> [!CAUTION]
> [Please read this page about setting up galvanic isolation of the `UART-TTL` connection.](Galvanic_isolation.md)

> [!TIP]
> If you are unsure about to pin order please measure the voltage between GND and VCC (5V). If you measure a positive voltage you know the position of VCC and GND!

```
┌─────────────────┐             ┌──────────┐             ┌───────────┐
│             5V o│<----5V---V1>│          |<V2---3V3--->|           |
│ Victron     RX o│<---------AO<│ UART-TTL │<AI-------TX<|   ESP32   |
│ SmartShunt  TX o│>---------AI>│ ISOLATOR │>BO-------RX>|           |
│            GND o│<----GND---->│          │<----GND---->|           |
└─────────────────┘             └──────────┘             └───────────┘

# UART-TTL VE.Direct port (JST-PH 2.0mm pinch)
┌─── ─────── ────┐
│                │
│ O   O   O   O  │
│GND  RX  TX VCC │ 
└────────────────┘
  │   │   │   └ 5V
  │   │   └──── TX  to TTL-isolator AI (input)
  │   └──────── RX  to TTL-isolator AO (output)
  └──────────── GND to TTL-isolator GND

```

## Bluetooth : How to retrieve MAC address and encryption key

To connect to your Victron device with BLE component you must have two information :

- `mac_address` -  Bluetooth mac address of device.
- `encryption_key` - AES encryption key.

Use [VictronConnect App v5.93](https://www.victronenergy.com/live/victronconnect:beta) (or later) released on 2023-08-25.

![VictronConnect App Settings page](../../images/Victron_SmartShunt_App_01_Settings.png)
![VictronConnect App Product info page](../../images/Victron_SmartShunt_App_02_ProductInfo.png)
![VictronConnect App Instant readout encryption data](../../images/Victron_SmartShunt_App_03_EncryptionData.png)

1. Open `Settings` of Device.
2. Open `Product Info` page.
3. Ensure `Instant readout via Bluetooth` is enabled.
4. Bottom of page press `SHOW` for Instant readout details Encryption data.

When connected to the device via VictronConnect App no Instant readout (Bluetooth advertising) data is generated.
