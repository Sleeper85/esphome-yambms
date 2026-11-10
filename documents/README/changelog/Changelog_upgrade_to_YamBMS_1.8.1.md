# Upgrade to YamBMS 1.8.1

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

YamBMS 1.8.1 changes the way the inverter, UART and CAN are configured, so a 1.7.0 or 1.8.0 YAML
no longer validates as it is. If you use Remote Packages, your next compile will fail until you
have made the changes below.

## Biggest changes

- **Inverter brand:** a new `Inverter brand` select sets the protocol for you, and you can still
  force one with `Protocol`. Your old protocol selection is not kept: **the CAN or RS485 link does
  not work until you select your inverter brand, or `Other` for a manual setup**. Your choice is
  then remembered.
- **UART:** each package now declares its own UART from its `*_uart_id` var. Two packages can no
  longer share a UART.
- **CAN:** each package now declares its own CAN node, which needs the new `canbus_platform` var.
- **RS485:** you now include `yambms_rs485.yaml` and choose the protocol with `rs485_protocol`.
- **Current limits:** the `Max charge C-Rate` and `Max discharge C-Rate`
  sliders added in 1.8.0 default to 0.5C. A 280 Ah bank is limited to 140 A in both directions
  until you raise them (1C maximum).
- **Several inverter links:** CCL and DCL are divided by the number of CAN and RS485 links declared
  in your YAML, including a link set to `Disabled`. Only declare the links that are actually wired.
  CAN and RS485 links can run at the same time: keep both blocks, each link with its own
  `canbus_id` or `rs485_id`. The dashboard shows up to 3 CAN links and 3 RS485 links. If you only
  use RS485, comment out the CAN block.
- **Balancing inferred:** EG4 LL V2, Seplos V1/V2, Seplos V3 and JK RS485 DISPLAY do not report
  balancing, and YamBMS now infers it from the cell spread. While a pack is seen as balancing, the
  charge only ends when the spread closes or the EOC timer expires, and the SoC stays at 98% until
  then. Set `bms_balance_trigger_voltage` to your BMS's actual setting and keep `EOC timer enabled`
  ON. See [Fake Equalizing](Changelog_Fake_Equalizing.md).

## How to update from 1.7.0 or 1.8.0

> [!IMPORTANT]
> Off-grid users: plan this for a moment when you can reach Home Assistant or the web server.
> Your inverter will report a BMS fault and stop using the battery until step 9 is done.

1. Save a copy of your current YAML and update ESPHome to **2026.10.0 or later**.
2. Start from the new [Remote Packages example](../../../YamBMS_Remote_Packages_example.yaml)
   ([Local Packages example](../../../YamBMS_Local_Packages_example.yaml) if you use local
   packages).
3. Report your own values one by one, without pasting your old `substitutions:` block:
   `hostname`, `friendly_name`, `yambms_name`, then **all your battery settings** (chemistry, cell
   count, voltages, currents) and your static IP if you have one. These are not checked by
   validation. Keep the new `yambms_cutoff_timer: '180'`.
4. Select your board and its options (PSRAM, display, web server). Do not copy your old UART and
   CAN includes, packages now declare them.
5. Paste your BMS, Shunt and Balancer blocks as they are ([you will find the updated examples in the examples folder](../../../examples/)).
   * Deye BMS on CAN: add `canbus_platform` to the `top` package.
   * If your board requires flow control, add `uart_flow_control_pin: ${talk_pin}` to the `vars:` of the package that uses that UART.
6. CAN inverter: keep the CAN block of the example and set `canbus_platform` (`esp32_can` or
   `mcp2515`, `external` with the espBerry board). With the web server, include `yambms_canbus_web_server.yaml` instead.

   ```yaml
   - path: 'packages/yambms/yambms_canbus.yaml'
     vars:
       canbus_id: '1'                      # Must be a number
       canbus_name: 'CANBUS 1'
       canbus_status_led_id: 'esp_light'
       canbus_link_timer_enabled: 'true'
       canbus_link_timer: '10s'            # min 6s with Deye
       # CAN setup
       canbus_platform: 'esp32_can'        # esp32_can / mcp2515
       canbus_node_id: 'canbus_inverter_1' # CAN bus node to which your inverter is connected
       canbus_bitrate: '500kbps'           # Default : 500kbps
   ```

7. RS485 inverter: uncomment the RS485 block of the example, then set `rs485_protocol` and
   `rs485_uart_id`. With the web server, include `yambms_rs485_web_server.yaml` instead.

   ```yaml
   - path: 'packages/yambms/yambms_rs485.yaml'
     vars:
       rs485_id: '1'                    # Must be a number
       rs485_name: 'RS485 1'
       rs485_protocol: 'pylon'          # pylon / voltronic
       rs485_update_timeout: '10s'
       rs485_status_led_id: 'esp_light'
       # UART setup
       rs485_uart_id: 'uart_esp_3'      # UART interface to which your inverter is connected
                                        # ESP32 : uart_esp_1 to uart_esp_3
                                        # WK2168 : uart_spi_0 to uart_spi_7 / uart_i2c_0 to uart_i2c_7
       rs485_uart_baud_rate: '9600'     # Default : 9600 / Epever : 115200
   ```

8. Run `esphome config your_file.yaml`, then flash.
9. Select your `Inverter brand` in Home Assistant or the web server, for each link. If it is not
   listed, select `Other` and set `Protocol` yourself. The link starts once this is done, and you
   only have to do it once. Read [Inverter Brand and Protocol](../YamBMS_functions.md#inverter-brand-and-protocol)
   before you start: it explains each setting and the battery mode to set on your inverter.
10. Replace your Home Assistant dashboard with its 1.8.1 version, from the
    [HomeAssistant_Dashboards](../../../HomeAssistant_Dashboards/) folder: open your dashboard,
    then *Edit dashboard* → *Raw configuration editor*, and paste the file that matches your
    setup. If you had customised it, carry your changes over to the new version.
11. Update any automations that use the old protocol entities. Coming from 1.7.0, also check the
    two C-Rate sliders and `Charger Offset V.` (formerly `Inverter Offset V.`).

## If validation fails

| Error | Cause |
| --- | --- |
| `Expected integer, but cannot parse ${uart_baud_rate}` | A UART include is still in your YAML. |
| `Bit rate ${CANBUS_BIT_RATE} is not supported` | A CAN include is still in your YAML. |
| `Cannot load include with unresolved substitutions` | `canbus_platform` or `rs485_protocol` is missing. |
| `Source for extension of ID 'rs4851_protocol' was not found` | You are still including `yambms_rs485_pylon.yaml`. |
| `ID uart_esp_1 redefined` | Two packages use the same UART. |

## PVbrain2

PVbrain2 users have a few more changes (board and expander files, `uart_spi_N` ids). Start from
the updated [PVbrain2 YAML](../../../YamBMS_RP_PVbrain2.yaml).

Coming from 1.7.0, the PVbrain2 board file is now split in two, depending on the revision of your
DevKitC-1:

- `board_ESP32-S3_DevKitC-1_PVbrain2_LED-48.yaml` for V1.0 (LED on GPIO 48, CAN TX on 38)
- `board_ESP32-S3_DevKitC-1_PVbrain2_LED-38.yaml` for V1.1 (LED on GPIO 38, CAN TX on 48)

## More information

Everything else is in the [changelog](Changelog.md) and the [inverter brand release note](Changelog_Inverter_brand_and_protocol.md).

If you encounter any difficulties, open an issue on [GitHub](https://github.com/Sleeper85/esphome-yambms).
