# YamBMS behavior

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

### Shunt/BMS combine status

![Image](../../images/YamBMS_Combine_Status.png "YamBMS_Combine_Status")

**Combined / Can be combined** : This status indicates whether the `BMS` or `Shunt` is currently combined.

In this example there are **3x BMS** and **1x BMS** is not combined (it is offline or is not sending correct data).

### Shunt

Combine condition :
1) the `Combine` switch is enabled
2) Shunt `Online Status` is `ON` (the shunt `Voltage` is `> 0`)

If one of these two conditions is not respected, the shunt is automatically uncombined.

> [!IMPORTANT]
> In RS485 modbus `multi-node`, if a server does not respond (cable or hardware failure) the `Online Status` of the shunt will be set to `OFF` and it will be uncombined.

As soon as you import a `Shunt` and it can be combined (see condition) the values ​​`Voltage`, `Current`, `Power` and `SoC` of the shunt(s) will take precedence over the BMS values.

> [!NOTE]
> If all BMS are `uncombined` the shunt data will no longer be published.

If one shunt is used for multiple batteries, it is possible to provide the BMS IDs the shunt code with the variable `bms_ids`, example: `bms_ids: '{1, 2, 3}'`.
When the BMS IDs are provided to the shunt and one or more of the BMS are offline, the shunt `Combine` switch will be turned `OFF`.
This is helpful when one BMS/battery shuts down for a longer time. The `SoC` of the shunt will then not be correct anymore and this avoids that the batteries are
discharged further then wanted.

> [!NOTE]
> You need to manually enable the `Combine` switch again if it was disabled automatically.
> If you do not want that behaviour, do not provide `bms_ids` to the shunt.

### BMS

Combine condition :
1) BMS `Online Status` is `ON / Connected` (to detect a loss of connection with the BMS e.g. cable, BMS OFF or dead)
2) The BMS `Battery Capacity` is `> 0` (to ensure that the data received is correct)

If one of these two conditions is not met, the BMS is automatically uncombined.

> [!IMPORTANT]
> In RS485 modbus `multi-node`, if a server does not respond (cable or hardware failure) the `Online Status` of the BMS will be set to `OFF` and it will be uncombined.

From YamBMS `1.5.1` :

The `binary_sensor` does not only represent the state of the `charge/discharge` switches but simply whether the `charge/discharge` is **allowed**. The value of `binary_sensor` is related to the status of the `switches/alarms`.

The `errors_bitmask` should not be a condition to combine a BMS anymore, let the BMS decide if the `charge/discharge` is allowed (its alarm system takes care of that).

The `errors_bitmask` continues to be analyzed to send `warnings/alarms` to the inverter.

The behavior of the `Charging Instruction` and `Discharging Instruction` sensors responsible for the instructions sent to the inverter will also be adapted. Alarm analysis will no longer be checked. If at least one BMS allows charging, charging can continue, if at least one BMS allows discharging, discharging can continue. This will also be based on the `binary_sensor` related to the state of `switchs/alarms` of the BMS.

If a BMS blocks charging or discharging, the permitted current is automatically reduced.

## External balancer

If an external balancer is used instead of the BMS internal one, it can be combined with the BMS.

Behaviour for `equalizing` and `balance trigger voltage`:

1) When no external balancer is present for a BMS or it is offline, the BMS values are used for `equalizing` and `balance trigger voltage`.
2) When an external balancer is present for a BMS and it is online, the BMS sensor data for `equalizing` and `balance trigger voltage` is overwritten by the external balancer sensor data.

## State of Charge

The `SoC` is slightly manipulated before reaching `0%` or `100%`.
SoC `100%` will be sent to your inverter only when the battery is `fully charged` (useful for some inverters stopping charging when the SoC reaches 100%).

SoC behavior:
1) If `SOC < 99%` real SoC is sent
2) Else if `the battery is fully charged` real SoC is sent
3) Else SoC `98%` is sent


## LED Status & Diagnostic Codes

The system uses Synchronized Diagnostic Blink Codes. 
This allows the device to communicate specific fault categories visually without requiring a network connection.

###  1. System Healthy
If no faults are present, the LED indicates the system is alive.

*   **Pattern:** 🟢 Green Pulse (1s) $\rightarrow$ ⚫ OFF (1s).
*   **Meaning:** All linked components operational.
*   **Cycle Time:** ~2.0 Seconds.

### 2. Component Fault
When a fault occurs, the cycle changes to a strict 3-part message structure.

| Phase | Color | Duration | Description |
| :--- | :--- | :--- | :--- |
| **1. Header** | 🔵 **Blue** | 1.0s | **"Attention."** Marks the start of a error report cycle. |
| **2. Gap** | ⚫ **OFF** | 0.5s | **"Wait."** A short pause to prepare for counting. |
| **3. Code** | 🔴 **Red** | Variable | **"Data."** A set count of short Red blinks. |

#### Reading the Blink Code
The number of Red blinks corresponds to the Fault Category (see table below).
To make counting easier, long codes are broken into groups of 4:
*   **5 Pips:** `* * * *` ... `*`
*   **9 Pips:** `* * * *` ... `* * * *` ... `*`

#### Category Reference Table

| Blinks | Category | Description |
| :--: | :--- | :--- |
| **1** | **API / MQTT** | API or MQTT communication failure. |
| **2** | **BMS** | Battery Management System communication failure. |
| **3** | **INV CAN** | Inverter CAN-BUS communication failure. |
| **4** | **INV RS485** | Inverter Modbus/RS485 communication failure. |
| **5** | **SHUNT** | Shunt communication failure. |
| **6** | **BALANCER** | Balancer communication failure. |
| **7** | **NETWORK** | No wifi or ethernet connection. |
| **8-16** | **AUX 1-9** | Reserved for future expansion. |

### Advanced Behaviors

#### Spotlight Mode
When a fault is active anywhere in the system:
1.  Fault LEDs: Display the Red error code.
2.  Healthy LEDs: Turn OFF during the "Code" phase
This reduces visual noise, highlighting exactly which components requires attention.

#### Multi-Fault Rotation
If a single LED monitors multiple components (e.g., a LED monitoring both the BMS and the Shunt) and both fail simultaneously:
*   **Cycle 1:** Displays BMS Code (2 Pips).
*   **Cycle 2:** Displays Shunt Code (5 Pips).
*   **Repeat:** The LED rotates through active faults one by one.

#### Monochromatic LEDs
For boards without RGB LEDs:
*   **Header:** Solid on.
*   **Code:** Blinking.
*   **Gap/Healthy:** off.

#### Multi-LED Boards
For boards with multiple LEDs, it's possible to assign a specific led to a specific component.
For example, led_1 for BMS 1, led_2 for canbus. See the section below for more details.

### Configuration & LED Assignment

The system links specific hardware LEDs to software components using Substitutions in your YAML package configuration.

Each component package (BMS, canbus, etc.) includes a specific variable to define which LED should report its status.

#### Example Configuration
In your main YAML file, under `packages`, you assign the Light ID to the `*_status_led_id` variable.
In most cases, the default values can be used but some boards such as the [LilyGo T-Connect](documents/README/Board_LilyGo_T-Connect.md) have multi-LED functionality.

```yaml
packages:
  bms:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 60min
    files:
      - path: 'packages/bms/bms_combine_JK_RS485_Modbus_bms_standard.yaml'
        vars:
          # Unique ID for this specific instance
          bms_id: '1' # must be a number
          bms_name: 'JK-BMS 1'
          bms_address: '0x01' # BMS 1 DIP switch
          
          # 1. LINKING THE LED
          # Set this to the ID of the light component defined in your ESPHome config.
          # Example: 'esp_light', 'led_1', etc. The board config will show further details
          bms_status_led_id: 'esp_light' # led used to show status. Default = esp_light, comment out to disable
```

## CAN bus link

For the CAN bus link to be established with your inverter, the three conditions below must be met:
1) At least `one` BMS is `combined`
2) The YamBMS status must be `initialized`
3) Your inverter sends an `ACK 0x305` every `1s` (the link will be faulty if no ACK is received for 5s)

If these conditions are not met, the application waits `30s` before trying to connect again.

During boot or when switching from `0 to 1` combined BMS, the CAN bus link is established after `30s`.

### Extra infos

Sending CAN frames continues without an inverter connected is problematic and will lead to ESP32 crash.

During boot the CAN bus links are activated directly if at least one BMS is combined and the inverter responds to the sending of CAN frames within a `5s` delay.
This `5s` delay represents the time during which the link is valid, this timer is reset each time an `ACK 0x305` is received from the inverter.
This `5s` delay can be modified in the configuration when importing the canbus package.

```YAML
  canbus1: !include
    file: packages/yambms/yambms_canbus.yaml
    vars:
      canbus_id: 'canbus1'
      canbus_name: 'CANBUS 1'
      canbus_node_id: 'canbus_node1'
      canbus_light_id: 'esp_light'
      # The CANBUS link will be considered down if no response from the inverter (ID 0x305) for 5s
      canbus_link_timer: '5s'
```

If the inverter does not respond with an `ACK 0x305` within this `5s` delay the sending of CAN frames is paused for `60s` this delay cannot be modified when importing the canbus package but you can modify it in the code if you need to.

## BMS alarms

![Image](../../images/YamBMS_BMS_alarms.png "YamBMS_BMS_alarms")

If all BMS have alarms, the alarms are sent to the **CAN bus** as `Protection Alarms`.

If at least one BMS has no alarms, the alarms are sent to the CAN bus as `Warning`.

Both **text_sensor** `Alarm` and `Warning` show the alarms/warnings currently transmitted to the inverter.
