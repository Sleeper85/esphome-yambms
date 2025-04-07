# YamBMS - Installation procedure

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## Installation procedure

### 1. Install ESPHome on your computer

Before you can flash your ESP32 you need to install the [ESPHome 2025.3.0 or higher](https://github.com/esphome/esphome/releases) command line application.<br>
[Follow these instructions for installation on Windows, Mac or Linux.](https://esphome.io/guides/installing_esphome)

> [!TIP]
> If you are using Windows install the `setuptools` package in addition to `wheel` and `esphome`.

```bash
pip3 install setuptools
pip3 install wheel
pip3 install esphome
```

### 2. Download all YAML files to your computer

> [!TIP]
> This step is not necessary if you are compiling the `Remote Packages` version of the YAML.

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

Create a copy of `YamBMS_Remote_Packages_example.yaml` and modify it to match your configuration.
Examples of BMS imports can be found in the [configuration_examples](configuration_examples/) folder.
You can mix different BMS models, the only condition is that they are numbered in order starting from `1`.

```bash
# install your YamBMS.yaml
# validate the configuration, create a binary, upload it, and start logs.
esphome run YamBMS.yaml

# upgrade via OTA by specifying the IP address of the ESP32
esphome run YamBMS.yaml --device 192.168.x.x
```

### 5. Optional but recommended, add the ESP32 in your Home Assistant server

In Home Assistant under **" Settings > Devices and services > Add Intergration "** select ESPHome add device `yambms` if found or supply ip address of ESP32.

## Other ESPHome command-line

```bash
# clean files before compiling again
esphome clean YamBMS.yaml

# test the config
esphome config YamBMS.yaml

# install the config in ESP32
esphome run YamBMS.yaml

# compile the firmware.bin
esphome compile YamBMS.yaml

# check the logs (the --device option is not required)
esphome logs YamBMS.yaml --device 192.168.x.x
```

## Debugging

If this component doesn't work out of the box for your device please update your configuration to increase the log level to `DEBUG`.

```YAML
logger:
  level: DEBUG
```
