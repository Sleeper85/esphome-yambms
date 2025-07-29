# YamBMS - How to create your YamBMS Remote Packages YAML

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

> [!TIP]
> Not sure which YAML to choose ? ... [YamBMS_Remote_Packages_example.yaml](../../YamBMS_Remote_Packages_example.yaml)
> is a good basis for creating your custom YAML.
> Examples of `BMS` and `Shunt` packages can be found in the [examples](../../examples/single-node/) folder.
> You don't have to import a shunt but you must import at least `one BMS`.
> You can mix different `BMS` models, the only condition is that the `bms_id` are numbered in order starting from `1` !

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

## Importing YamBMS Remote Packages

Package imports are done below this line:

```YAML
packages:
```

Each remote package starts with the 5 first lines below.
These lines will not be shown in the examples.
You can import multiple remote packages (3 in this example) without having to repeat the first 5 lines.

```YAML
  remote_packages:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 0s
    files:
      - path: 'your_remote_packages_1.yaml'
      - path: 'your_remote_packages_2.yaml'
      - path: 'your_remote_packages_3.yaml'
```

## Board

First you need to import the package that corresponds to the `board` you are going to use.

There are other `board.yaml` not mentioned here, see in the [board](../../packages/board/) folder.

So just one of the packages below :

### ESP32 Generic

```YAML
      - path: 'packages/board/board_ESP32_Generic.yaml'
```

### ESP32 DevKit-V1

```YAML
      - path: 'packages/board/board_ESP32_DevKit-V1.yaml'
```

### ESP32-S3 DevKitC-1

```YAML
      # RGB LED to GPIO 38
      - path: 'packages/board/board_ESP32-S3_DevKitC-1_LED-38.yaml'
```

```YAML
      # RGB LED to GPIO 48
      - path: 'packages/board/board_ESP32-S3_DevKitC-1_LED-48.yaml'
```

### ESP32-S3 LilyGo T-Connect

```YAML
      - path: 'packages/board/board_ESP32-S3_LilyGo-T-Connect.yaml'
```

### Atom S3 Lite

```YAML
      - path: 'packages/board/board_ESP32-S3_AtomS3-Lite.yaml'
```

### Atom S3 / S3R (display)

In this case you need to specify the `yambms` and `canbus` IDs to display the information on the screen.

```YAML
      - path: 'packages/board/board_ESP32-S3_AtomS3.yaml'
        vars:
          display_auto_next_page_interval: '5s'
          display_rotation: '0' # 0/90/180/270 rotation angle in degrees
```

```YAML
      - path: 'packages/board/board_ESP32-S3_AtomS3R.yaml'
        vars:
          display_auto_next_page_interval: '5s'
          display_rotation: '0' # 0/90/180/270 rotation angle in degrees
```

## YamBMS [single-node](../../examples/single-node/) example

```YAML
      # Shunt 1
      - path: 'packages/shunt/shunt_combine_Victron_SmartShunt_UART.yaml'
        vars:
          shunt_id: '1' # must be a number
          shunt_name: 'Shunt 1'
          shunt_uart_id: 'uart_esp_1'

      # BMS 1
      - path: 'packages/bms/bms_combine_JK_UART_4G-GPS_full.yaml'
        vars:
          bms_id: '1' # must be a number
          bms_name: 'BMS 1'
-         # other settings
          # ...

      # BMS 2
      - path: 'packages/bms/bms_combine_JBD_BLE_full.yaml'
        vars:
          bms_id: '2' # must be a number
          bms_name: 'BMS 2'
          # other settings
          # ...
```

## YamBMS [multi-node](../../examples/multi-node/) RS485 modbus example

> [!IMPORTANT]
> The BMS/Shunt IDs of the `modbus client` must match exactly with the BMS/Shunt IDs of the `modbus server` as in the example below.

### YamBMS modbus client `node1`

```YAML
      # Modbus client
      - path: 'packages/base/device_modbus.yaml'
        vars:
          modbus_role: 'client' # client / server
          modbus_uart_id: 'uart_esp_1' # RS485 board
      # Shunt 1
      - path: 'packages/shunt/shunt_combine_modbus_client.yaml'
        vars:
          shunt_id: '1' # must be a number
          shunt_name: 'Shunt 1'
      # BMS 1
      - path: 'packages/bms/bms_combine_modbus_client.yaml'
        vars:
          bms_id: '1' # must be a number
          bms_name: 'BMS 1'
      # BMS 2
      - path: 'packages/bms/bms_combine_modbus_client.yaml'
        vars:
          bms_id: '2' # must be a number
          bms_name: 'BMS 2'
      # BMS 3
      - path: 'packages/bms/bms_combine_modbus_client.yaml'
        vars:
          bms_id: '3' # must be a number
          bms_name: 'BMS 3'
```

### ESP32 modbus server `node2`

```YAML
      # Modbus server
      - path: 'packages/base/device_modbus.yaml'
        vars:
          modbus_role: 'server' # client / server
          modbus_uart_id: 'uart_esp_1' # RS485 board
      # Shunt 1
      - path: 'packages/shunt/shunt_modbus_Victron_SmartShunt_UART.yaml'
        vars:
          shunt_id: '1' # must be a number
          shunt_name: 'Shunt 1'
          # other settings
          # ..
      # BMS 1
      - path: 'packages/bms/bms_modbus_JK_UART_4G-GPS_full.yaml'
        vars:
          bms_id: '1' # must be a number
          bms_name: 'JK-BMS 1'
          # other settings
          # ..
```

### ESP32 modbus server `node3`

```YAML
      # Modbus server
      - path: 'packages/base/device_modbus.yaml'
        vars:
          modbus_role: 'server' # client / server
          modbus_uart_id: 'uart_esp_1' # RS485 board
      # BMS 2
      - path: 'packages/bms/bms_modbus_JK_BLE_standard.yaml'
        vars:
          bms_id: '2' # must be a number, also represents the modbus server number !
          bms_name: 'JK-BMS 2'
          # other settings
          # ..
      # BMS 3
      - path: 'packages/bms/bms_modbus_JK_BLE_standard.yaml'
        vars:
          bms_id: '3' # must be a number, also represents the modbus server number !
          bms_name: 'JK-BMS 3'
          # other settings
          # ..
```

## BMS

> [!IMPORTANT]
> You must number your `BMS` in order starting with the number `1`.

> [!TIP]
> YAML files whose name starts with `bms_combine` are to be used on the main `YamBMS` node connected to your inverter, those whose name starts with `bms_modbus` are to be used on the other nodes connected to the `RS485` bus.

The example YAMLs are just examples, you can mix different BMS models without problems.

There are other `bms.yaml` not mentioned here, see in the [bms](../../packages/bms/) folder.

The `full` / `standard` versions contain all available sensors while the `minimal` version contains the basic sensors without the voltages of each cell and other superfluous sensors.

You can find `BMS` import `RP` examples in the [examples/single-node](../../examples/single-node/) folder.

## Shunt

> [!IMPORTANT]
> You must number your `Shunt` in order starting with the number `1`.

> [!TIP]
> YAML files whose name starts with `shunt_combine` are to be used on the main `YamBMS` node connected to your inverter, those whose name starts with `shunt_modbus` are to be used on the other nodes connected to the `RS485` bus.

As soon as you import a `Shunt` and it can be combined ([see condition](YamBMS_behavior.md#shunt)) the values ​​`Voltage`, `Current`, `Power` and `SoC` of the shunt(s) will take precedence over the BMS values.

You can find `Shunt` import `RP` examples in the [examples/single-node](../../examples/single-node/) folder.


## YamBMS

> [!TIP]
> This package is only used with the `YamBMS` main node.

> [!CAUTION]
> By default, `YamBMS` is configured with the values ​​for a 16S LFP battery !

Take the time to configure `YamBMS` correctly according to your battery chemistry type `LFP/Li-ion/LTO` and `cell count`. Charging voltages can be changed in the app.

```YAML
  yambms:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 0s
    files:
      - path: 'packages/yambms/yambms.yaml'
        vars:
          # Please read the cut-off charging logic README to understand how the YamBMS works
          yambms_id: 'yambms1'
          yambms_name: 'YamBMS 1'
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
          # Max. charge current : corresponds to the maximum charge current which may be requested by YamBMS.
          # The current requested will be proportional to the BMS count without ever exceeding this value.
          yambms_max_requested_charge_current: '300' # in Ampere
          # Max. discharge current : corresponds to the maximum discharge current which may be requested by YamBMS.
          # The current requested will be proportional to the BMS count without ever exceeding this value.
          yambms_max_requested_discharge_current: '300' # in Ampere
```

## CAN bus to Inverter

> [!TIP]
> This package is only used with the `YamBMS` main node.
> It's possible to use this package multiple times in order to send information on two different `CAN` bus.

The CAN bus connected to your inverter via the CAN transceiver `canbus_inverter_1`.

You can keep the default configuration and adapt the `canbus` node on which the component must connect.

```YAML
  canbus:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 0s
    files:
      - path: 'packages/yambms/yambms_canbus.yaml'
        vars:
          canbus_id: 'canbus1'
          canbus_name: 'CANBUS 1'
          canbus_node_id: 'canbus_inverter_1'
          canbus_light_id: 'esp_light'
          # The CANBUS link will be considered down if no response from the inverter (0x305 frame) for 5s
          # The Deye inverter sends the ACK 0x305 only when it receives the 0x356 frame.
          canbus_link_timer: '5s'
```

# RS485 bus to Inverter

> [!TIP]
> This package is only used with the `YamBMS` main node.
> It's possible to use this package multiple times in order to send information on two different `RS485` bus.

The RS485 bus connected to your inverter via the RS485 transceiver `uart_esp_3`.

You can keep the default configuration and adapt the `uart` port on which the component must connect.

```YAML
  rs485_pylon:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 0s
    files:
      - path: 'packages/yambms/yambms_rs485_pylon.yaml'
        vars:
          rs485_id: 'rs485_1'
          rs485_name: 'RS485 1'
          rs485_uart_id: 'uart_esp_3' # UART interface to which your inverter is connected
          rs485_uart_baud_rate: '9600'
          rs485_update_timeout: '5s'
```

## Debug

The `debug` package will add useful information to refer to if problems occur.

```YAML
  debug:
    url: https://github.com/Sleeper85/esphome-yambms
    ref: main
    refresh: 0s
    files:
      - path: packages/base/device_debug_ESP32.yaml
      # - path: packages/base/device_debug_ESP32_PSRAM.yaml # for ESP32 with PSRAM
        vars:
          debug_name: 'Debug'
          debug_update_interval: '5s'
          # Size of your PSRAM in bits
          # 8Mb='8388608' | 6Mb='6291456' | 4Mb='4194304' | 2Mb='2097152' | NoPSRAM='0'
          debug_psram_size: '8388608'
```
