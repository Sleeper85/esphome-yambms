# YamBMS behavior

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Shunt and BMS combination

![Image](../../images/YamBMS_Combine_switch.png "YamBMS_Combine_switch")

### Combine status

![Image](../../images/YamBMS_Combine_Status.png "YamBMS_Combine_Status")

**Combine Availability** : This status indicates whether the BMS or Shunt meets the conditions to be combined.

**Can be combined** : This status indicates whether the BMS or Shunt is currently combined.

## Shunt

Combine condition :
1) the `Combine` switch is enabled
2) the `Voltage` supplied by the shunt `is > 0V`

If one of these two conditions is not respected, the shunt is automatically decombined.

As soon as you import a `shunt` and it can be combined (see condition) the values ​​(Voltage, Current, Power and SoC) of the shunt(s) will take precedence over the BMS values.

## BMS

Combine condition :
1) the `Combine` switch is enabled
2) BMS `Charging` or `Discharging` switch is enabled
3) BMS is not in `alarm`

If one of these three conditions is not met, the BMS is automatically decombined.

## BMS alarms

> [!IMPORTANT]  
> This is the current behavior, it may not be perfect, feel free to communicate your ideas to improve it.

![Image](../../images/YamBMS_BMS_alarms.png "YamBMS_BMS_alarms")

The `errors_bitmask` values ​​are merged and then analyzed continuously **even if the BMS is uncombined**.

As long as at least one BMS is working normally the system will continue to work.
YamBMS will display BMS alarms as `Warning`.

If all BMS are in alarm, they are all uncombined and in this case the sending of instructions on the `CAN bus` is also stopped.
YamBMS will display BMS alarms as `Alarm`.