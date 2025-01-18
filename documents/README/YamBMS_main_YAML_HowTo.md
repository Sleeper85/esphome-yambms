# YamBMS - How to create your YamBMS YAML

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> [!IMPORTANT]
> BMS monitoring with `Bluetooth` as well as the `Web server` are RAM-intensive components.
> Please note that enabling these components will take up a lot of memory and may decrease the stability of your ESP32.

## WiFi & Ethernet

> [!IMPORTANT]
> By default, if the ESP32 is disconnected from the WiFi network it will reboot `every 15 minutes` to try to resolve the problem.
> The `wifi` or `ethernet` components are found in the [YAML corresponding to the board](../../packages/board/).

Configuring a fixed IP address can be done in the main YAML like this:

### WiFi

> [!IMPORTANT]
> Don't forget to configure your WiFi credentials in the `secrets.yaml` file.

```YAML
wifi:
  manual_ip:
    static_ip: 192.168.0.85
    gateway: 192.168.0.1
    subnet: 255.255.255.0
    dns1: 8.8.8.8
    dns2: 8.8.4.4
```

### Ethernet

```YAML
ethernet:
  manual_ip:
    static_ip: 192.168.0.85
    gateway: 192.168.0.1
    subnet: 255.255.255.0
    dns1: 8.8.8.8
    dns2: 8.8.4.4
```

## Home Assistant API

> [!IMPORTANT]
> If your ESP32 is not connected with Home Assistant it will reboot every 15 minutes.
> This is the normal behavior of ESPHome, this is not a bug to be resolved but a mechanism put in place by the ESPHome team to correct a possible problem with the API connection.

The **"api:"** section is therefore configured by default not to reboot every 15 minutes if `Home Assistant` is not connected.

```YAML
api:
  reboot_timeout: 0s
```

## Web Server

> [!IMPORTANT]
> Please note that enabling this component will take up a lot of memory and may decrease stability and be the cause of reboot depending on the capabilities of the board used.

If you don't use `Home Assistant`, you can activate the `Web Server` and have access to YamBMS information and also interact with the application.

[ESPHome Web Server Component](https://esphome.io/components/web_server.html)

## Importing YamBMS packages

Package imports are done below this line:

```YAML
packages:
```

## Board

First you need to import the package that corresponds to the `board` you are going to use.

There are other `board.yaml` not mentioned here, see in the [board](../../packages/board/) folder.

So just one of the packages below :

### ESP32 Generic

```YAML
  device_board: !include packages/board/board_ESP32_Generic.yaml
```

### ESP32 DevKit-V1

```YAML
  device_board: !include packages/board/board_ESP32_DevKit-V1.yaml
```

### ESP32-S3 DevKitC-1

```YAML
  device_board: !include packages/board/board_ESP32-S3_DevKitC-1.yaml
```

### Atom S3 Lite

```YAML
  device_board: !include packages/board/board_ESP32-S3_AtomS3-Lite.yaml
```

### Atom S3 / S3R (display)

In this case you need to specify the `yambms` and `canbus` IDs to display the information on the screen.

```YAML
  device_board: !include
    file: packages/board/board_ESP32-S3_AtomS3.yaml
    vars:
      display_auto_next_page_interval: '5s'
```

```YAML
  device_board: !include
    file: packages/board/board_ESP32-S3_AtomS3R.yaml
    vars:
      display_auto_next_page_interval: '5s'
```

### ESP32-C3 DevKitM-1

```YAML
  device_board: !include packages/board_ESP32-C3_DevKitM-1.yaml
```

### ESP32-C3 ETH01-EVO

This board has an `Ethernet` port and can be powered from `POE` (optional).

```YAML
  device_board: !include packages/board/board_ESP32-C3_ETH01-EVO.yaml
```

### ESP32 LilyGo T-CAN485

```YAML
  device_board: !include packages/board/board_ESP32_LilyGo-T-CAN485.yaml
```

### ESP32-S3 LilyGo T-Connect

```YAML
  device_board: !include packages/board/board_ESP32-S3_LilyGo-T-Connect.yaml
```

## YamBMS single-node example

```YAML
  # Config : this YAML contains the settings shared between all ESP32s
  config_yambms: !include packages/config/config_yambms.yaml

  shunt1: !include
    file: packages/shunt/shunt_combine_Victron_SmartShunt_UART.yaml
    vars:
      shunt_id: '1' # must be a number
      shunt_name: 'Shunt 1'
      # other settings
      # ...

  bms1: !include
    file: packages/bms/bms_combine_JK-B_UART_full.yaml
    vars:
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      # other settings
      # ...

  bms2: !include
    file: packages/bms/bms_combine_JBD_UART_full.yaml
    vars:
      bms_id: '2' # must be a number
      bms_name: 'BMS 2'
      # other settings
      # ...
```

## YamBMS multi-node RS485 modbus example

> [!IMPORTANT]
> The BMS/Shunt IDs of the `modbus client` must match exactly with the BMS/Shunt IDs of the `modbus server` as in the example below.

### YamBMS modbus client `node1`

```YAML
  # Config : this YAMLs contains the settings shared between all ESP32s
  config_yambms: !include packages/config/config_yambms.yaml
  config_multinode_modbus: !include packages/config/config_multi-node_modbus.yaml

  modbus: !include
    file: packages/base/device_modbus.yaml
    vars:
      modbus_role: 'client' # client / server
      modbus_uart_id: 'uart_esp_1' # RS485 board

  shunt1: !include
    file: packages/shunt/shunt_combine_modbus_client.yaml # a Shunt connected to a node of the RS485 bus
    vars:
      shunt_id: '1' # must be a number, also represents the modbus server number (200 + shunt_id) !
      shunt_name: 'Shunt 1'

  bms1: !include
    file: packages/bms/bms_combine_modbus_client.yaml # a BMS connected to a node of the RS485 bus
    vars:
      bms_id: '1' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 1'

  bms2: !include
    file: packages/bms/bms_combine_modbus_client.yaml # a BMS connected to a node of the RS485 bus
    vars:
      bms_id: '2' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 2'

  bms3: !include
    file: packages/bms/bms_combine_modbus_client.yaml # a BMS connected to a node of the RS485 bus
    vars:
      bms_id: '3' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 3'
```

### ESP32 modbus server `node2`

```YAML
  # Config : this YAMLs contains the settings shared between all ESP32s
  config_yambms: !include packages/config/config_yambms.yaml
  config_multinode_modbus: !include packages/config/config_multi-node_modbus.yaml

  modbus: !include
    file: packages/base/device_modbus.yaml
    vars:
      modbus_role: 'server' # client / server
      modbus_uart_id: 'uart_esp_1' # RS485 board

  shunt1: !include
    file: packages/shunt/shunt_modbus_Victron_SmartShunt_UART.yaml
    vars:
      shunt_id: '1' # must be a number, also represents the modbus server number (200 + shunt_id) !
      shunt_name: 'Shunt 1'
      # other settings
      # ...

  bms1: !include
    file: packages/bms/bms_modbus_JK-B_UART_full.yaml
    vars:
      bms_id: '1' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 1'
      # other settings
      # ...
```

### ESP32 modbus server `node3`

```YAML
  # Config : this YAMLs contains the settings shared between all ESP32s
  config_yambms: !include packages/config/config_yambms.yaml
  config_multinode_modbus: !include packages/config/config_multi-node_modbus.yaml

  modbus: !include
    file: packages/base/device_modbus.yaml
    vars:
      modbus_role: 'server' # client / server
      modbus_uart_id: 'uart_esp_1' # RS485 board

  bms2: !include
    file: packages/bms/bms_modbus_JK-ALL_BLE_standard.yaml
    vars:
      bms_id: '2' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 2'
      # other settings
      # ...

  bms3: !include
    file: packages/bms/bms_modbus_JK-ALL_BLE_standard.yaml
    vars:
      bms_id: '3' # must be a number, also represents the modbus server number !
      bms_name: 'BMS 3'
      # other settings
      # ...
```

## BMS

> [!IMPORTANT]
> You must number your `BMS` in order starting with the number `1`.

> [!TIP]
> YAML files whose name starts with `bms_combine` are to be used on the main `YamBMS` node connected to your inverter, those whose name starts with `bms_modbus` are to be used on the other nodes connected to the `RS485` bus.

The example YAMLs are just examples, you can mix different BMS models without problems.

There are other `bms.yaml` not mentioned here, see in the [bms](../../packages/bms/) folder.

The `full` / `standard` versions contain all available sensors while the `minimal` version contains the basic sensors without the voltages of each cell and other superfluous sensors.

### [JK-ALL (BLE)](https://github.com/syssi/esphome-jk-bms)

> [!IMPORTANT]
> The BLE software stack on the ESP32 consumes a significant amount of RAM on the device.
> Crashes are likely to occur if you include too many additional components in your device’s configuration.
> I recommend using `UART` or `RS485` if possible.

```YAML
  bms1: !include
    file: packages/bms/bms_combine_JK-ALL_BLE_standard.yaml # bms_modbus_JK-ALL_BLE_standard.yaml
    vars:
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      bms_ble_protocol_version: 'JK02_32S' # JK02_24S < hardware version 11.0 >= JK02_32S
      bms_ble_mac_address: 'C8:47:8C:10:7E:AA' # Your MAC address
```

### [JK-B (UART)](https://github.com/syssi/esphome-jk-bms)

[How to make the UART connection with the ESP32.](BMS_JK-B_UART_solution.md)

```YAML
  bms1: !include
    file: packages/bms/bms_combine_JK-B_UART_full.yaml # bms_modbus_JK-B_UART_full.yaml
    vars:
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      bms_uart_id: 'uart_esp_1'
```

### [JK-B (RS485 DISPLAY)](https://github.com/syssi/esphome-jk-bms)

> [!CAUTION]
> The `jk_bms_display` component does not provide all the information needed for an optimal operation of `YamBMS`.
> The missing information has been added in the code by fixed values.
> e.g. it's not possible to know if the BMS is `online` or if the BMS is `equalizing` the cells.

[How to make the RS485 connection with the ESP32.](BMS_JK-B_RS485_DISPLAY_solution.md)

```YAML
  bms1: !include
    file: packages/bms/bms_combine_JK-B_RS485_DISPLAY_full.yaml
    vars:
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      bms_uart_id: 'uart_esp_1'
      # Required settings cannot be retrieved from BMS
      # These values ​​must match your BMS settings
      # LFP values example
      bms_battery_capacity: '280' # Ah
      bms_max_charge_current: '100' # A. Used to calculate maximum charge current
      bms_max_discharge_current: '100' # A. Used to calculate maximum discharge current
      bms_cell_ovp: '3.650' # V. Used by 'Auto CCL' functions
      bms_cell_uvp: '2.800' # V. Used by 'Auto DCL' functions and to calculate maximum discharge voltage
```

### [JK-PB (RS485)](https://github.com/txubelaxu/esphome-jk-bms/)

A single `RS485 bus` allows you to monitor up to `16` BMS.

[How to make the RS485 connection with the ESP32.](BMS_JK-PB_RS485_solution.md)

#### JK-PB sniffer

> [!IMPORTANT]
> You need to import only one `sniffer` package of your choice.
> Depending on which `RS485` board you have, you should use the version of the `sniffer` with or without `talk_pin`.

The sniffer represents the ESP node connected to the JK-PB RS485 bus
If address `0x00` is not detected on the RS485 bus, the sniffer will act directly as a master BMS (mode 2, max 15 BMS).

Sniffer without `talk_pin` :

```YAML
  sniffer1: !include
    file: packages/bms/bms_combine_JK-PB_RS485_sniffer.yaml
    vars:
      sniffer_id: 'sniffer1'
      sniffer_protocol: 'JK02_32S'
      sniffer_uart_id: 'uart_esp_1'
```

If your `RS485` board requires a `talk_pin` you must specify which `GPIO` will be used :

```YAML
  sniffer1: !include
    file: packages/bms/bms_combine_JK-PB_RS485_sniffer_talk_pin.yaml
    vars:
      sniffer_id: 'sniffer1'
      sniffer_protocol: 'JK02_32S'
      sniffer_uart_id: 'uart_esp_1'
      sniffer_talk_pin: 8 # ESP32: 4, ESP32-S3: 8, ESP32-C3: 10
```

#### JK-PB BMS

```YAML
  # Mode2 : configure the DIP switches of your BMS from 0x01 to 0x0F (don't use the 0x00 address, maximum 15 BMS)
  bms1: !include
    file: packages/bms/bms_combine_JK-PB_RS485_bms_full.yaml
    vars:
      # Sniffer ID
      sniffer_id: 'sniffer1'
      # BMS vars
      bms_id: '1' # must be a number
      bms_name: 'JK-BMS 1'
      bms_address: '0x01' # BMS 1 DIP switch
```

### [JBD (UART)](https://github.com/syssi/esphome-jbd-bms)

```YAML
  bms1: !include
    file: packages/bms/bms_combine_JBD_UART_full.yaml # bms_modbus_JBD_UART_full.yaml
    vars:
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      bms_uart_id: 'uart_esp_1'
      bms_rx_timeout: '150ms'
      # Required settings cannot be retrieved from BMS
      # These values ​​must match your BMS settings
      # LFP values example
      bms_max_charge_current: '100' # A. Used to calculate maximum charge current
      bms_max_discharge_current: '100' # A. Used to calculate maximum discharge current
      bms_cell_ovp: '3.650' # V. Used by 'Auto CCL' functions
      bms_cell_uvp: '2.800' # V. Used by 'Auto DCL' functions and to calculate maximum discharge voltage
      bms_balance_trigger_voltage: '0.010' # V. Used by 'Auto CVL' functions
```

### [Seplos V1/V2 (RS485)](https://github.com/syssi/esphome-seplos-bms)

A single `RS485 bus` allows you to monitor up to `16` BMS.

> [!CAUTION]
> The `seplos_bms` component does not provide all the information needed for an optimal operation of `YamBMS`.
> The missing information has been added in the code by fixed values.
> e.g. it's not possible to know if the BMS **blocks** the `charge` or the `discharge` or if the BMS is `equalizing` the cells.
> The `online` status has not been tested.

> [!IMPORTANT]
> You need to import only one `seplos_modbus`.

#### Seplos modbus

```YAML
  seplos_modbus1: !include
    file: packages/bms/bms_combine_SEPLOS_V1_V2_RS485_modbus.yaml
    vars:
      seplos_modbus_id: 'seplos_modbus1'
      seplos_modbus_uart_id: 'uart_esp_1'
      seplos_modbus_baud_rate: '9600' # 9600 / 19200 ; please set the baudrate of your Seplos BMS model here
      seplos_modbus_rx_timeout: '150ms'
```

#### Seplos V1/V2 BMS

```YAML
  bms1: !include
    file: packages/bms/bms_combine_SEPLOS_V1_V2_RS485_bms_full.yaml
    vars:
      # Seplos modbus ID
      seplos_modbus_id: 'seplos_modbus1'
      # BMS vars
      bms_id: '1' # must be a number
      bms_name: 'BMS 1'
      bms_address: '0x01' # BMS 1 DIP switch
      bms_protocol_version: '0x20' # Known protocol versions: 0x20 (Seplos), 0x26 (Boqiang)
      # Required settings cannot be retrieved from BMS
      # These values ​​must match your BMS settings
      # LFP values example
      bms_max_charge_current: '100' # A. Used to calculate maximum charge current
      bms_max_discharge_current: '100' # A. Used to calculate maximum discharge current
      bms_cell_ovp: '3.650' # V. Used by 'Auto CCL' functions
      bms_cell_uvp: '2.800' # V. Used by 'Auto DCL' functions and to calculate maximum discharge voltage
      bms_balance_trigger_voltage: '0.010' # V. Used by 'Auto CVL' functions
```

## Shunt

> [!IMPORTANT]
> You must number your `Shunt` in order starting with the number `1`.

> [!TIP]
> YAML files whose name starts with `shunt_combine` are to be used on the main `YamBMS` node connected to your inverter, those whose name starts with `shunt_modbus` are to be used on the other nodes connected to the `RS485` bus.

As soon as you import a `Shunt` and it can be combined ([see condition](YamBMS_behavior.md#shunt)) the values ​​`Voltage`, `Current`, `Power` and `SoC` of the shunt(s) will take precedence over the BMS values.


### [Victron Smartshunt (UART)](https://github.com/KinDR007/VictronMPPT-ESPHOME)

[How to make the UART connection with the ESP32.](Shunt_Victron_SmartShunt_HowTo.md)

```YAML
  shunt1: !include
    file: packages/shunt/shunt_combine_Victron_SmartShunt_UART.yaml # shunt_modbus_Victron_SmartShunt_UART.yaml
    vars:
      shunt_id: '1' # must be a number
      shunt_name: 'Shunt 1'
      shunt_uart_id: 'uart_esp_1'
```

### [Victron Smartshunt (BLE)](https://github.com/Fabian-Schmidt/esphome-victron_ble)

> [!IMPORTANT]
> The BLE software stack on the ESP32 consumes a significant amount of RAM on the device.
> Crashes are likely to occur if you include too many additional components in your device’s configuration.
> I recommend using `UART` or `RS485` if possible.

[How to make the BLE connection with the ESP32.](Shunt_Victron_SmartShunt_HowTo.md)

```YAML
  shunt1: !include
    file: packages/shunt/shunt_combine_Victron_SmartShunt_BLE.yaml # shunt_modbus_Victron_SmartShunt_BLE.yaml
    vars:
      shunt_id: '1' # must be a number
      shunt_name: 'Shunt 1'
      shunt_mac_address: '60:A4:23:91:8F:55' # Your MAC address
      shunt_encryption_key: '0df4d0395b7d1a876c0c33ecb9e70dcd' # Your encryption key
```

### [Junctek KH-F (UART/RS485)](https://github.com/Sleeper85/esphome-junctek_khf)

```YAML
  shunt1: !include
    file: packages/shunt/shunt_combine_Junctek_KHF_UART.yaml # shunt_modbus_Junctek_KHF_UART.yaml
    vars:
      shunt_id: '1' # must be a number
      shunt_name: 'Shunt 1'
      shunt_uart_id: 'uart_esp_1'
```

## YamBMS

> [!TIP]
> This package is only used with the `YamBMS` main node.

> [!CAUTION]
> By default, `YamBMS` is configured with the values ​​for a 16S LFP battery !

Take the time to configure `YamBMS` correctly according to your battery chemistry type `LFP/Li-ion/LTO` and `cell count`. Charging voltages can be changed in the app.

```YAML
  yambms1: !include
    file: packages/yambms/yambms.yaml
    vars:
      # Please read the cut-off charging logic README to understand how the YamBMS works
      yambms_update_interval: '1s'
      # Input numbers can be displayed as a slider or an input box, options are 'slider' or 'box'.
      yambms_input_number_mode: 'slider'
      # Please check and fill in the options below correctly according to your battery chemistry and number of cells in series.
      # These parameters are important and used for charging logic.
      # Battery Chemistry
      yambms_battery_chemistry: '1' # 1-LFP | 2-Li-ion | 3-LTO
      # Number of cells in series
      yambms_cell_count: '16'
      # Bulk / Absorption Voltage : corresponds to the Bulk voltage that will be used to charge the battery. (LFP : 55.2V = 3.45V/Cell for 16S battery)
      yambms_bulk_v: '55.2'
      # Float Voltage : corresponds to the voltage at which the battery would be maintained at the end of charge. (LFP : 53.6V = 3.35V/Cell for 16S battery)
      yambms_float_v: '53.6'
      # Rebulk voltage, voltage from which a new Bulk charge can start. (LFP : 52.8V = 3.3V/Cell for 16S battery)
      yambms_rebulk_v: '52.8'
      # Maximum time in minutes that the cut-off step can last before charging is complete
      # If your cells are properly balanced this step ends at the fastest after the `cut-off timer`
      # This timer can be deactivated with a switch
      yambms_eoc_timer: '30'
      # Time in seconds during which the end of charge conditions must be respected (cut-off + cells not equalizing)
      yambms_cutoff_timer: '60'
      # Maximum charging cycles is used to calculate the battey SOH, LF280K v3 =8000.0, LF280K v2 =6000.0, LF280=3000.0 (decimal is required)
      yambms_max_cycles: '6000.0'
```

## CAN bus

> [!TIP]
> This package is only used with the `YamBMS` main node.
> It's possible to use this package multiple times in order to send information on two different CAN bus.

The CAN bus connected to your inverter via the CAN transceiver `canbus_node1`.

You can keep the default configuration.

```YAML
  canbus1: !include
    file: packages/yambms/yambms_canbus.yaml
    vars:
      # CANBUS vars
      canbus_id: 'canbus1'
      canbus_name: 'CANBUS 1'
      canbus_node_id: 'canbus_node1'
      canbus_light_id: 'esp_light'
      # The CANBUS link will be considered down if no response from the inverter (ID 0x305) for 5s
      # The Deye inverter sends the ACK (can_id 0x305) only when it receives the can_id 0x356
      canbus_link_timer: '5s'
```

## Debug

The `debug` package will add useful information to refer to if problems occur.

### ESP32 and AtomS3

```YAML
  device_debug: !include
    file: packages/base/device_debug_ESP32.yaml
    vars:
      debug_name: 'Debug'
      debug_update_interval: '5s'
```

### ESP32 with PSRAM memory like ESP32-S3 / AtomS3R

```YAML
  device_debug: !include
    file: packages/base/device_debug_ESP32-S3.yaml
    vars:
      debug_name: 'Debug'
      debug_update_interval: '5s'
      # Size of your PSRAM in bits
      # 8Mb='8388608' | 6Mb='6291456' | 4Mb='4194304' | 2Mb='2097152' | NoPSRAM='0'
      debug_psram_size: '8388608'
```
