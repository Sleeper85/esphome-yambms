# YamBMS behavior

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Shunt and BMS combination

![Image](../../images/YamBMS_Combine_switch.png "YamBMS_Combine_switch")

The various counters above allow you to see what state your system is in.

### Shunt/BMS combine status

![Image](../../images/YamBMS_Combine_Status.png "YamBMS_Combine_Status")

* **Combine Availability** : This status indicates whether the `BMS` or `Shunt` meets the conditions to be combined.
* **Can be combined** : This status indicates whether the `BMS` or `Shunt` is currently combined.

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

### BMS

Combine condition :
1) BMS `Online Status` is `ON / Connected` (to detect a loss of connection with the BMS e.g. cable, BMS OFF or dead)
2) The BMS `Battery Capacity` is `> 0` (to ensure that the data received is correct)

If one of these three conditions is not met, the BMS is automatically uncombined.

> [!IMPORTANT]
> In RS485 modbus `multi-node`, if a server does not respond (cable or hardware failure) the `Online Status` of the BMS will be set to `OFF` and it will be uncombined.

From YamBMS `1.5.1` :

The `binary_sensor` does not only represent the state of the `charge/discharge` switches but simply whether the `charge/discharge` is **allowed**. The value of `binary_sensor` is related to the status of the `switches/alarms`.

The `errors_bitmask` should not be a condition to combine a BMS anymore, let the BMS decide if the `charge/discharge` is allowed (its alarm system takes care of that).

The `errors_bitmask` continues to be analyzed to send `warnings/alarms` on the CAN bus.

The behavior of the `Charging Instruction` and `Discharging Instruction` sensors responsible for the instructions sent to the inverter will also be adapted. Alarm analysis will no longer be checked. If at least one BMS allows charging, charging can continue, if at least one BMS allows discharging, discharging can continue. This will also be based on the `binary_sensor` related to the state of `switchs/alarms` of the BMS.

If a BMS blocks charging or discharging, the permitted current is automatically reduced.

## State of Charge

The `SoC` is slightly manipulated before reaching `0%` or `100%`.
SoC `100%` will be sent to your inverter only when the battery is `fully charged` (useful for some inverters stopping charging when the SoC reaches 100%).

SoC behavior:
1) If `SOC < 99%` real SoC is sent
2) Else if `the battery is fully charged` real SoC is sent
3) Else SoC `98%` is sent

## RGB LED status

This only applies to boards with an `RGB LED`.

| Color | Status |
| --- | --- |
| $${\color{red}Red}$$ | HA or MQTT KO + CANBUS KO |
| $${\color{green}Green}$$ | HA or MQTT OK + CANBUS KO |
| $${\color{blue}Flashing-Blue}$$ | HA or MQTT KO + CANBUS OK |
| $${\color{cyan}Flashing-Cyan}$$ | HA or MQTT OK + CANBUS OK |

## CAN bus link

For the CAN bus link to be established with your inverter, the two conditions below must be met:
1) At least one BMS is in service (the number of combined BMS must be `> 0`)
2) Your inverter sends an `ACK 0x305` every `1s` (the link will be faulty if no ACK is received for 5s)

If these conditions are not met, the application waits `60s` before trying to connect again.

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
