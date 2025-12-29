# YamBMS - Waveshare ESP32-S3-RS485-CAN

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> [!IMPORTANT]  
> This board uses a `flow_control_pin`, also called a `talk_pin` in the YamBMS documentation and used to manage the direction of data transmission for RS485 transceiver that do not handle this automatically. This `talk_pin` must be specified in your YAML.

## Overview

The Waveshare ESP32-S3-RS485-CAN is an industrial-grade WiFi wireless communicator based on the ESP32-S3 microcontroller. This board is designed for professional IoT applications with built-in isolation and protection circuits, making it particularly well-suited for the YamBMS project thanks to its robust RS485 and CAN bus interfaces.

**Key Features:**
- Industrial-grade design with multiple protection circuits
- Isolated RS485 and CAN interfaces
- Built-in 120Ω termination resistors (jumper-selectable)
- Digital isolation to prevent signal interference
- Power supply isolation for stable operation
- Wide voltage input range (7-36V DC)
- DIN rail mountable protective enclosure

<img src="../..//images/MCU_ESP32-S3_WS-RS485-CAN_1.png" width="500"> <img src="../..//images/MCU_ESP32-S3_WS-RS485-CAN_2.png" width="500">

## Board Specifications

| Specification | Details |
|-----|-----|
| Microcontroller | ESP32-S3-WROOM-1 |
| Processor | Xtensa 32-bit LX7 dual-core @ up to 240MHz |
| FLASH | 16MB |
| PSRAM | 8MB |
| Wireless | Wi-Fi 802.11 b/g/n (2.4GHz) / Bluetooth 5.0 (LE) |
| RS485 | 1× Isolated RS485 interface |
| CAN Bus | 1× Isolated CAN interface |
| UART | 1x SH1.0 interface (not isolated) |
| Power Input (DC Terminal) | 7-36V DC (wide range) |
| Power Input (USB) | 5V via USB Type-C |
| Isolation | Power isolation + Optocoupler isolation |
| Termination | 120Ω resistors (jumper-selectable for RS485 & CAN) |
| LED Indicators | PWR, RS485 TX/RX, CAN |
| Enclosure | Rail-mounted ABS protective case |
| Programming | USB Type-C (firmware download & debugging) |

## Interfaces Support Capacity

Based on hardware limitations and testing, this board supports:

| Interface | Maximum | Notes |
|-----------|---------|-------|
| **CAN** | 1x bus | CAN bus to BMS or Inverter |
| **RS485** | 1x bus | Best option for monitoring many BMS of the same brand |
| **UART** | 3× devices¹ | Can be connected to the **SH1.0 interface** or **GPIOs header** (**shared with RS485**) |
| **Bluetooth (BLE)** | 3× devices¹ | BLE stack consumes significant RAM, may cause crashes/reboots |

¹ BMS / Balancer / Shunt

**Note:** These are theoretical limits. Not all combinations have been tested.

## UART/IO Expander

It would be possible to add one or more [WK2168 4x UART expander](https://esphome.io/components/weikai.html) to increase the number of `UART` port.

## Power Supply

The Waveshare ESP32-S3-RS485-CAN can be powered using two methods:

### Option 1: USB Type-C Port
- Connect a USB Type-C cable to the USB port
- Provides **5V** power
- Recommended for programming, debugging, and testing
- Convenient for development and troubleshooting

### Option 2: External DC Power Supply (Screw Terminal)
- Voltage range: **7V to 36V DC** (wide range)
- Connect to the dedicated power screw terminal
- Recommended for permanent installations and industrial environments
- Provides stable power with built-in voltage regulator
- **Built-in power supply isolation** provides stable isolated voltage
- No extra power supply required for the isolated terminal

**Important:** 
- The board features integrated power isolation for enhanced safety and reliability
- Suitable for harsh industrial environments with voltage fluctuations
- Do not exceed the 36V maximum input voltage

## Port Identification and Pinout

### RS485 Port

The RS485 interface is **isolated** and clearly labeled on the board.

**RS485 GPIO Pins (Internal):**
- **TX (GPIO17)**: RS485 transmit data
- **RX (GPIO18)**: RS485 receive data  
- **EN (GPIO21)**: RS485 transceiver enable (automatic switching) `talk_in`

**RS485 Terminal Block Pinout:**
The RS485 port typically has a **2-pin screw terminal block**:
- **A (or +)**: RS485 A / Data+ (non-inverting)
- **B (or -)**: RS485 B / Data- (inverting)

**RS485 Features:**
- **Isolated interface** to avoid external signal interference
- **Automatic transceiver mode switching** (no manual DE/RE control needed)
- Supports RS485 Modbus and other industrial protocols
- **LED indicators**: 
  - Green LED: Lights up when RS485 transmits data
  - Blue LED: Lights up when RS485 receives data

### CAN Port

The CAN interface is **isolated** and clearly labeled on the board.

**CAN GPIO Pins (Internal):**
- **TX (GPIO15)**: CAN transmit (TWAI TX)
- **RX (GPIO16)**: CAN receive (TWAI RX)

**CAN Terminal Block Pinout:**
The CAN port typically has a **2-pin screw terminal block**:
- **H (or CANH)**: CAN High
- **L (or CANL)**: CAN Low

**CAN Features:**
- **Isolated CAN interface** for easy access to various CAN devices
- Uses ESP32-S3 TWAI (Two-Wire Automotive Interface) controller
- **LED indicator**: Blinks during CAN data transmission

## Wiring Instructions

### Connecting RS485 Devices

To connect an RS485 device to the RS485 port:

| RS485 | Terminal Block |
|-------|----------------|
| A + | RS485 A+ (Data+ non-inverting) |
| B - | RS485 B- (Data- inverting) |

**Wiring Steps:**
1. Identify the A and B wires from your RS485 device (may be labeled as D+/D-, A/B, or +/-)
2. Connect the **A wire (D+ / Data+)** to the **A+ terminal**
3. Connect the **B wire (D- / Data-)** to the **B- terminal**
4. Connect the **ground wire** to the **GND terminal** for common reference

**RS485 Best Practices:**
- **Always connect the ground (GND)** to provide a common reference between devices
- The board features **automatic transceiver mode switching**, no manual control needed
- RS485 polarity matters: if communication fails, try swapping A and B connections
- Use twisted pair cable (recommended) to reduce noise and interference
- The **isolation protects** the ESP32-S3 from high-voltage interference on the RS485 bus
- Monitor communication using the **green (TX) and blue (RX) LED indicators**

### Connecting CAN Bus Devices

To connect a CAN device to the CAN port:

| CAN bus | Terminal Block |
|---------|----------------|
| CAN H | CAN H (CAN High) |
| CAN L | CAN L (CAN Low) |

**Wiring Steps:**
1. Identify the CAN H and CAN L wires from your CAN device
2. Connect the **CAN H wire** to the **H (CANH) terminal**
3. Connect the **CAN L wire** to the **L (CANL) terminal**
4. Connect the **ground wire** to the **GND terminal** for common reference (optional)

**CAN Bus Best Practices:**
- **Always connect the ground (GND)** for proper common mode voltage reference
- The board uses the ESP32-S3 **TWAI (Two-Wire Automotive Interface)** controller
- CAN bus requires proper termination (see Termination Resistors section below)
- Use twisted pair cable specifically designed for CAN bus (120Ω impedance)
- The **isolation protects** the ESP32-S3 from electrical noise on the CAN bus
- Monitor CAN communication using the **CAN LED indicator** (blinks during transmission)
- Typical CAN bus speeds: 125 kbps, 250 kbps, 500 kbps, or 1 Mbps

## Termination Resistors

One of the **key advantages** of the Waveshare ESP32-S3-RS485-CAN is its **built-in 120Ω termination resistors** that can be enabled or disabled via **jumpers**.

### RS485 Termination

The board includes an **onboard 120Ω RS485 termination resistor**.

**How to Enable RS485 Termination:**
1. Locate the **RS485 termination jumper** on the board (typically labeled "RS485 120R" or similar)
2. **Move the jumper cap to the "120R" position** to enable the termination resistor
3. **Move the jumper cap to the "NC" (No Connection) position** to disable termination

**When to Enable RS485 Termination:**
- Enable termination if the board is at **one of the two endpoints** of the RS485 bus
- RS485 networks require **120Ω termination at both ends** of the bus
- If the board is in the **middle** of the network, keep termination disabled (NC position)
- For short cable runs (<10 meters), termination may be optional but is still recommended

**FAQ Note:** If RS485 communication is not working, the Waveshare wiki recommends: *"Please move the jumper cap to 120R and try again. Some RS485 devices require a 120R resistor to be connected in series."*

### CAN Bus Termination

The board includes an **onboard 120Ω CAN termination resistor**.

**How to Enable CAN Termination:**
1. Locate the **CAN termination jumper** on the board (typically labeled "CAN 120R" or similar)
2. **Move the jumper cap to the "120R" position** to enable the termination resistor
3. **Move the jumper cap to the "NC" (No Connection) position** to disable termination

**When to Enable CAN Termination:**
- Enable termination if the board is at **one of the two endpoints** of the CAN bus
- CAN bus requires **exactly two 120Ω termination resistors** on the entire bus (one at each end)
- If the board is in the **middle** of the network, keep termination disabled (NC position)
- With proper termination, you should measure ~60Ω between CAN H and CAN L

**Termination Tips:**
- Always check termination settings before troubleshooting communication issues
- Many CAN devices (like inverters) have built-in termination - verify before adding more
- Incorrect termination is a common cause of CAN communication failures

## LED Indicators

The board includes several LED indicators for monitoring system status:

| LED | Color | Function |
|-----|-------|----------|
| **PWR** | Red/Green | Power indicator - lights up when board is powered |
| **RS485 TX** | Green | Lights up when RS485 port **sends** data |
| **RS485 RX** | Blue | Lights up when RS485 port **receives** data |
| **CAN** | Yellow/Green | Blinks during CAN bus **data transmission** |

These indicators are extremely useful for troubleshooting communication issues in real-time.

## Typical YamBMS Configuration

For a typical YamBMS setup with the Waveshare ESP32-S3-RS485-CAN:

1. **Power Supply:** 
   - For bench testing: Connect USB Type-C cable (5V)
   - For permanent installation: Connect 12V or 24V DC to screw terminal (recommended)

2. **BMS Communication (RS485):** 
   - Connect your BMS (e.g., JK, JBD, SEPLOS, PACE, BASEN) to the RS485 port
   - Wire according to: **A=RS485 A (Data+)**, **B=RS485 B (Data-)**, **GND=Ground**
   - **Enable RS485 termination (120R jumper)** if the board is at the end of the RS485 bus
   - If the BMS is the only RS485 device, enable termination

3. **Inverter Communication (CAN):** 
   - Connect your inverter (e.g., Deye, Sofar, Growatt, Victron) to the CAN port
   - Wire according to: **H=CAN H**, **L=CAN L**, **GND=Ground**
   - **Enable CAN termination (120R jumper)** if the inverter is at the end of the CAN bus
   - For point-to-point (board ↔ inverter), typically both ends need termination
   - Check if your inverter has built-in termination before enabling

4. **Verification:**
   - Power on the board - the **PWR LED** should light up
   - Monitor RS485 communication using **green (TX) and blue (RX) LEDs**
   - Monitor CAN communication using the **CAN LED** (should blink during transmission)

5. **GPIO Pin Configuration:**
   - RS485: TX=GPIO17, RX=GPIO18, EN=GPIO21
   - CAN: TX=GPIO15, RX=GPIO16

## Protective Enclosure

The Waveshare ESP32-S3-RS485-CAN comes with a **rail-mounted ABS protective enclosure**:

**Enclosure Features:**
- Industrial-grade ABS plastic case
- **DIN rail mountable** for easy installation in electrical cabinets
- Protects the board from dust, moisture, and physical damage
- Provides professional appearance for industrial installations
- Easy to install and safe to use

**Installation:**
- The case clips onto standard 35mm DIN rails
- Suitable for use in control panels, switchboards, and industrial enclosures

## Programming and Development

### Entering Download Mode

If you have trouble uploading firmware:

1. **Long press the BOOT button**
2. While holding BOOT, **press the RESET button**
3. **Release RESET**, then release BOOT
4. The module will enter download mode
5. Now you can upload your firmware

This solves most download/flashing issues.

### Web Interface Demo

Waveshare provides demo firmware with a web interface:
- Default WiFi AP name: **ESP32-S3-RS485-CAN**
- Default password: **waveshare**
- The web interface allows control of RS485 and CAN ports
- You can get the device IP via Bluetooth debugging assistant

## Additional Resources

### Official Waveshare Documentation
- [Waveshare ESP32-S3-RS485-CAN Product Page](https://www.waveshare.com/esp32-s3-rs485-can.htm)
- [Waveshare ESP32-S3-RS485-CAN Wiki](https://www.waveshare.com/wiki/ESP32-S3-RS485-CAN)
- [Schematic Diagram](https://www.waveshare.com/wiki/ESP32-S3-RS485-CAN#Schematic) (available on wiki)

### Datasheets
- [ESP32-S3 Datasheet](https://files.waveshare.com/upload/f/f7/Esp32-s3_datasheet_en_(1).pdf)
- [ESP32-S3 Technical Reference Manual](https://files.waveshare.com/wiki/common/Esp32-s3_technical_reference_manual_en.pdf)

## Troubleshooting

### RS485 Communication Issues
- **Check termination jumper** - move to "120R" position if board is at bus endpoint
- Verify correct A/B wiring - try swapping if needed
- Check that **ground (GND) is connected** between devices
- Monitor **green (TX) and blue (RX) LEDs** to verify data transmission
- Ensure baud rate matches between all RS485 devices
- Test cable continuity and check for damaged twisted pair cable

### CAN Bus Communication Issues
- **Check termination jumper** - move to "120R" position if board is at bus endpoint
- Verify exactly **two 120Ω termination resistors** are present on entire CAN bus
- Check correct CAN H and CAN L wiring
- Verify **ground (GND) is connected** for common mode voltage reference
- Measure resistance between CAN H and CAN L (should be ~60Ω with proper termination)
- Monitor **CAN LED** - it should blink during transmission
- Verify CAN bus speed matches all devices (typically 125k, 250k, 500k, or 1Mbps)

### Upload/Programming Issues
- **Enter download mode** using BOOT + RESET button sequence (see Programming section)
- Verify USB cable supports data transfer (not charge-only)
- Check correct COM port is selected in IDE
- Try different USB cable or USB port on computer
- Ensure USB drivers are installed (CH343P chip)

### Power Issues
- Verify power supply voltage is within **7-36V DC** range (or 5V via USB)
- Check **PWR LED** lights up when powered
- Verify polarity of DC power connection
- Do not exceed 36V maximum input voltage
- The board's power isolation should prevent most power-related issues

### Isolation Issues
- The board has **built-in isolation** for both power and communication interfaces
- If experiencing interference issues, verify:
  - Ground connections are properly made
  - Shielded cables are used in noisy environments
  - Isolation jumpers are correctly configured

## Comparison with Other Boards

### Waveshare ESP32-S3-RS485-CAN vs LilyGo T-Connect

| Feature | Waveshare | LilyGo T-Connect |
|---------|-----------|------------------|
| RS485 Ports | 1 (isolated) | Up to 3 (isolated) |
| CAN Ports | 1 (isolated) | 1 (isolated) |
| Built-in Termination | ✅ Yes (120Ω jumper-selectable) | ❌ No (external resistors required) |
| Power Isolation | ✅ Yes | ❌ No |
| Signal Isolation | ✅ Yes (RS485 & CAN) | ✅ Yes (RS485 & CAN up to 2500V) |
| Enclosure | ✅ DIN rail ABS case included | ❌ No enclosure |
| Power Input | 7-36V DC or USB-C | 7-12V DC or USB-C |
| LED Indicators | PWR, RS485 TX/RX, CAN | PWR, APA102 support |
| Price | Moderate | Moderate |
| Best For | Single RS485 + CAN with isolation | Multiple RS485 + CAN with isolation |

**Summary:** The Waveshare board excels in **industrial-grade protection and built-in termination**, while the LilyGo offers **more RS485 ports and configuration flexibility**. Choose based on your specific needs:
- **Waveshare**: Best for harsh environments, built-in termination, ease of installation
- **LilyGo**: Best for multiple RS485 devices, flexible configuration, compact size

---

**License:** This documentation is part of the YamBMS project and follows the same GPLv3 license.

**Disclaimer:** Always verify specifications and wiring with the official Waveshare documentation before deployment. This guide is community-created and may not reflect the latest product revisions.
