# Troubleshooting

[![Badge License: GPLv3](https://img.shields.io/badge/License-GPLv3-brightgreen.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Badge Version](https://img.shields.io/github/v/release/Sleeper85/esphome-yambms?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/Sleeper85/esphome-yambms/releases/latest)
![GitHub stars](https://img.shields.io/github/stars/Sleeper85/esphome-yambms)
![GitHub forks](https://img.shields.io/github/forks/Sleeper85/esphome-yambms)
![GitHub watchers](https://img.shields.io/github/watchers/Sleeper85/esphome-yambms)

## UART logging

### Default UART GPIOs

The table below shows you the default UART GPIOs as well as the default logger hardware output.

When declaring a UART you can choose other GPIOs but keep in mind that you can declare max `3 UARTs` with an ESP32. If not needed, I will not use the GPIOs used for `UART0` because those are the GPIOs used to flash the ESP32 from USB.

| Board | UART0 | UART1 | UART2 | USB_CDC | USB_SERIAL_JTAG | Default logger HW |
| ----- | ----- | ----- | ----- | ------- | --------------- | ----------------- |
| ESP32 | TX: 1, RX: 3 | TX: 10, RX: 9 | TX: 17, RX: 16 | N/A | N/A | UART0 |
| ESP32-C3 | TX: 21, RX: 20 | Undefined | N/A | N/A | 18/19 | USB_SERIAL_JTAG |
| ESP32-S2 | TX: 43, RX: 44 | TX: 17, RX: 18 | N/A | 19/20 | N/A | USB_CDC |
| ESP32-S3 | TX: 43, RX: 44 | TX: 17, RX: 18 | Undefined | 19/20 | 19/20 | USB_SERIAL_JTAG |

### Change the default logger UART output

You are using an `ESP32-S3`, by default the logs are sent to the USB port labeled `USB` this corresponds to `USB_SERIAL_JTAG`.
If you want to flash the code and receive the logs on the port labeled `UART`, the option below allows you to choose the hardware that `logger` should use.

```YAML
logger:
  hardware_uart: UART0 # UART0 / USB_SERIAL_JTAG
```

### Don't use UART logging

> [!CAUTION] 
> Using `wk2168` and `canbus` (esp32can platform) components together is problematic and creates a boot loop (tested on ESP32-S3).
> Using `baud_rate: 0` avoids this problem.

By default an ESP32 has `3 UARTs`, one of which is used for the logger output. The option below allows you to free the UART used by `logger` so that you can use it and assign new GPIOs to it.

```YAML
logger:
  baud_rate: 0
```
