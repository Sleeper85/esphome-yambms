# MQTT and Prometheus with several BMS

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Problem

Since YamBMS 1.6.0 each BMS, shunt and balancer is an ESPHome
[sub-device](https://esphome.io/components/esphome/#sub-devices). Its entities are named
`Charging Power`, `Cell Voltage 1`, ... and the BMS name (`BMS 1`) is the device name.

Home Assistant (native API) keeps them apart with the device. MQTT and the Prometheus
exporter do not: ESPHome builds the MQTT topic and the Prometheus `id` label from the entity
name only. With several BMS, all of them publish to the same topic and nothing tells
which BMS a value comes from:

```
yambms/sensor/charging_power/state   536.49   <- BMS 1 ?
yambms/sensor/charging_power/state   0.00     <- BMS 2 ?
```

```
esphome_sensor_value{id="charging_power",name="Charging Power",...} 536.49
esphome_sensor_value{id="charging_power",name="Charging Power",...} 0.00
```

See [discussion #279](https://github.com/Sleeper85/esphome-yambms/discussions/279).

## Solution

Add the `device_base_sub_device_topics.yaml` package. At compile time it prefixes every entity
that belongs to a sub-device with that sub-device's name:

| Output | Before | After |
|---|---|---|
| MQTT state topic | `yambms/sensor/charging_power/state` | `yambms/sensor/bms_1_charging_power/state` |
| MQTT command topic | `yambms/switch/charging/command` | `yambms/switch/bms_1_charging/command` |
| Prometheus `id` label | `charging_power` | `bms_1_charging_power` |
| Prometheus `name` label | `Charging Power` | `BMS 1 Charging Power` |

The prefix is the device name in lower case, with spaces and special characters replaced by `_`
(`BMS 1` -> `bms_1`). The YamBMS, RS485, CAN, shunt and balancer sub-devices are prefixed in the
same way (e.g. `yambms_1_...`). Entities that are not on a sub-device keep their topic.

Remote packages:

```yaml
packages:
  remote_packages:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    files:
      - path: 'packages/base/device_base_sub_device_topics.yaml'
```

Local packages:

```yaml
packages:
  sub_device_topics: !include packages/base/device_base_sub_device_topics.yaml
```

The package only acts on what you configured: MQTT topics change only if `mqtt:` is in your
config, Prometheus labels only if `prometheus:` is. Either can be turned off:

```yaml
yambms_sub_device_topics:
  mqtt: true
  prometheus: false
```

An entity that sets its own `state_topic` / `command_topic`, or that has a Prometheus `relabel`
entry, is not changed.

## Limits

- **Home Assistant MQTT discovery** is not fixed. ESPHome builds the discovery topic
  (`homeassistant/sensor/<node>/<object_id>/config`) from the entity name and does not allow
  changing it, so entities with the same name on several BMS still overwrite each other in
  discovery. Use the native API with Home Assistant.
- Climate, cover, fan, light, valve and alarm panel entities are not changed (YamBMS does not use them).
- The package downloads the component from `github://Sleeper85/esphome-yambms@main`.
  With local packages you can build it from your local copy instead, by setting this in
  your main YAML (the path is relative to it):

  ```yaml
  substitutions:
    sub_device_topics_source: 'components'
  ```
