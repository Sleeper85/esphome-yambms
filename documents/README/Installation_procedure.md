# YamBMS - Installation procedure

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Installation procedure

### 1. Install ESPHome on your computer

Before you can flash your ESP32 you need to install the [ESPHome 2024.6.0 or higher](https://github.com/esphome/esphome/releases) command line application.<br>
[Follow these instructions for installation on Windows, Mac or Linux.](https://esphome.io/guides/installing_esphome)

> [!TIP]
> If you are using Windows install the `setuptools` package in addition to `wheel` and `esphome`.

```bash
pip3 install setuptools
pip3 install wheel
pip3 install esphome
```

### 2. Download all YAML files to your computer

You can do this from the command line or in your preferred method.

You need to gather the following three points in the same folder. If you are compiling from your HA server use the `Samba Share` add-on so that you can copy the `packages` folder to the `esphome` folder on the HA server.

  1) the `packages` folder
  2) your `secrets.yaml`
  3) your [custom](YamBMS_main_YAML_HowTo.md) `main.yaml`

```bash
# Clone this external component
git clone https://github.com/Sleeper85/esphome-yambms.git
cd esphome-yambms
```

### 3. Enter your WiFi credentials in the secrets.yaml files

```yaml
wifi_ssid: YourSSID
wifi_password: YourPassword
domain : .local
```

### 4. Install the YamBMS application into your ESP32

Choose the main YAML that best suits your needs like for example `multi-bms_JK-ALL_BLE.yaml`.<br>
Validate the configuration, create a binary, upload it, and start logs.<br>
**The only YAML that needs to be checked and configured is the main one like for example `multi-bms_JK-ALL_BLE.yaml` but you can modify other YAMLs if you want.<br>
The goal is that the main YAML which contains all your specific parameters can be preserved and reused each time the other YAMLs classified in the `packaged` folder are updated.**

```bash
# To install the multi-bms JK-ALL Bluetooth version
esphome run multi-bms_JK-ALL_BLE.yaml

# To install the multi-bms JK-B UART version
esphome run multi-bms_JK-B_UART.yaml

# To install the multi-bms JK-PB RS485 version
esphome run multi-bms_JK-PB_RS485_mode2.yaml

# upgrade via OTA by specifying the IP address of the ESP32
esphome run multi-bms_JK-ALL_BLE.yaml --device 192.168.x.x
```

### 5. Optional but recommended, add the ESP32 in your Home Assistant server

In Home Assistant under **" Settings > Devices and services > Add Intergration "** select ESPHome add device `yambms` if found or supply ip address of ESP32.

## Other ESPHome command-line

```bash
# clean files before compiling again
esphome clean multi-bms_JK-ALL_BLE.yaml

# test the config
esphome config multi-bms_JK-ALL_BLE.yaml

# install the config in ESP32
esphome run multi-bms_JK-ALL_BLE.yaml

# compile the firmware.bin
esphome compile multi-bms_JK-ALL_BLE.yaml

# check the logs (the --device option is not required)
esphome logs multi-bms_JK-ALL_BLE.yaml --device 192.168.x.x
```

## Debugging

If this component doesn't work out of the box for your device please update your configuration to enable the debug output of the UART component and increase the log level to the see outgoing and incoming serial traffic:

```
logger:
  level: DEBUG

uart:
  id: uart_0
  baud_rate: 115200
  rx_buffer_size: 384
  tx_pin: ${tx_pin}
  rx_pin: ${rx_pin}
  debug:
    direction: BOTH
```
