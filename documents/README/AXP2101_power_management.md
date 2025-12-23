# AXP2101 Power Management Guide

## Overview

The AXP2101 is a comprehensive Power Management Unit (PMU) found in M5Stack CoreS3 and other ESP32-based hardware. It provides multiple configurable power rails, battery management, and monitoring capabilities.

## Features

- **14 Power Rails**: DCDC1-5, ALDO1-4, BLDO1-2, DLDO1-2, CPUSLDO
- **Battery Monitoring**: Voltage, level (%), and temperature sensors
- **Temperature Monitoring**: PMU temperature sensor
- **Dynamic Control**: Enable/disable rails, adjust voltages
- **Power Efficiency**: Disable unused rails to maximize battery life

## Quick Start

### Basic Usage (CoreS3)

The CoreS3 board includes power management by default:

```yaml
packages:
  board: !include ../../packages/board/board_ESP32-S3_CoreS3.yaml
```

This automatically provides:
- LCD backlight control
- Battery monitoring sensors
- Essential power rails (ALDO1, ALDO2, BLDO1, BLDO2)

### Customizing Power Rails

Override default voltages using substitutions:

```yaml
substitutions:
  # Custom voltages (mV)
  axp2101_aldo1_voltage: "1800"  # System 1.8V
  axp2101_aldo2_voltage: "3300"  # System 3.3V
  axp2101_backlight_min: "2500"  # Backlight min
  axp2101_backlight_max: "3300"  # Backlight max
  axp2101_update_interval: "30s" # Sensor update rate

packages:
  board: !include ../../packages/board/board_ESP32-S3_CoreS3.yaml
```

## Power Rails Reference

### DCDC Converters (High Current)

Buck converters optimized for high current loads (up to 2A each):

| Rail  | Voltage Range | Typical Use        |
|-------|---------------|-------------------|
| DCDC1 | 500-3400mV    | External 3.3V     |
| DCDC2 | 500-3400mV    | External 1.8V     |
| DCDC3 | 500-3400mV    | External 1.2V     |
| DCDC4 | 500-3400mV    | External 1.1V     |
| DCDC5 | 500-3400mV    | External 1.4V     |

**Best For**: High current devices, motors, displays, LEDs

### ALDO - Analog LDOs (Low Noise)

Low-dropout regulators optimized for analog circuits (up to 300mA each):

| Rail  | Voltage Range | CoreS3 Usage      |
|-------|---------------|-------------------|
| ALDO1 | 500-3500mV    | System 1.8V       |
| ALDO2 | 500-3500mV    | System 3.3V       |
| ALDO3 | 500-3500mV    | Available         |
| ALDO4 | 500-3500mV    | Available         |

**Best For**: Sensors, ADCs, audio circuits, RF modules

### BLDO - Battery LDOs (Backup Power)

Battery-powered LDOs that maintain power during main supply loss (up to 300mA each):

| Rail  | Voltage Range | CoreS3 Usage      |
|-------|---------------|-------------------|
| BLDO1 | 500-3500mV    | Board functions   |
| BLDO2 | 500-3500mV    | Board functions   |

**Best For**: RTC backup, memory retention, always-on circuits

### DLDO - Digital LDOs (General Purpose)

General-purpose digital LDOs (up to 300mA each):

| Rail  | Voltage Range | CoreS3 Usage      |
|-------|---------------|-------------------|
| DLDO1 | 500-3400mV    | LCD Backlight     |
| DLDO2 | 500-3400mV    | Available         |

**Best For**: Digital peripherals, I2C/SPI devices, GPIO-powered components

### CPUSLDO - CPU Supply

Dedicated CPU power supply (up to 200mA):

| Rail     | Voltage Range | Typical Use       |
|----------|---------------|-------------------|
| CPUSLDO  | 500-1400mV    | CPU core voltage  |

**Best For**: CPU core voltage regulation

## Configuration Examples

### Enable Additional Power Rail

```yaml
# Add to your configuration
output:
  - platform: axp2101
    channel: DCDC1
    voltage: 3300  # 3.3V
    id: axp2101_dcdc1

switch:
  - platform: output
    name: "External 3.3V Power"
    output: axp2101_dcdc1
    icon: "mdi:power-plug"
    restore_mode: RESTORE_DEFAULT_OFF
```

### Variable Voltage Rail

```yaml
output:
  - platform: axp2101
    type: range
    channel: DCDC2
    id: variable_power
    min_voltage: 1800
    max_voltage: 3300

number:
  - platform: template
    name: "Variable Power Voltage"
    min_value: 1.8
    max_value: 3.3
    step: 0.1
    unit_of_measurement: "V"
    set_action:
      - output.set_level:
          id: variable_power
          level: !lambda 'return (x - 1.8) / (3.3 - 1.8);'
```

### Power-Managed Sensor

```yaml
# Power sensor only when reading
output:
  - platform: axp2101
    channel: ALDO3
    voltage: 3300
    id: sensor_power

script:
  - id: read_sensor_with_power
    then:
      # Enable sensor power
      - output.turn_on: sensor_power
      - delay: 100ms
      # Read sensor
      - component.update: my_sensor
      # Disable to save power
      - delay: 1s
      - output.turn_off: sensor_power

interval:
  - interval: 60s
    then:
      - script.execute: read_sensor_with_power
```

### All Power Rails Example

See `examples/boards/CoreS3_advanced_power_example.yaml` for complete example with all power rails enabled and controlled via switches.

## Monitoring

### Available Sensors

The power management package provides these sensors automatically:

```yaml
sensor:
  - platform: axp2101
    type: battery_level      # Battery % (0-100)
  - platform: axp2101
    type: battery_voltage    # Battery voltage (V)
  - platform: axp2101
    type: temperature        # PMU temperature (°C)
```

### Monitoring in Home Assistant

All sensors appear automatically in Home Assistant:
- **Battery Level**: Shows battery percentage with battery icon
- **Battery Voltage**: Precise voltage reading (3 decimals)
- **PMU Temperature**: Internal temperature monitoring
- **LCD Backlight**: Brightness control slider

## Power Optimization

### Disable Unused Rails

Save power by disabling rails you don't need:

```yaml
# In your configuration
switch:
  - platform: output
    name: "External Power"
    output: axp2101_dcdc1
    # Start disabled
    restore_mode: RESTORE_DEFAULT_OFF

# Turn on only when needed
automation:
  - platform: time
    at: "08:00:00"
    then:
      - switch.turn_on: external_power
  - platform: time
    at: "22:00:00"
    then:
      - switch.turn_off: external_power
```

### Choose Efficient Regulators

| Load Type | Best Choice | Why |
|-----------|-------------|-----|
| High current (>300mA) | DCDC | More efficient for high loads |
| Low noise analog | ALDO | Cleanest power for sensors |
| Backup power | BLDO | Maintains power on battery |
| Digital peripherals | DLDO | General purpose digital |

### Battery Life Tips

1. **Disable unused rails**: Each disabled rail saves ~1-5mA
2. **Lower backlight**: Reduce LCD backlight voltage when possible
3. **Use DCDC for high current**: More efficient than LDOs
4. **Power cycle peripherals**: Only power sensors when reading
5. **Monitor temperature**: High temperature indicates inefficiency

## Safety and Best Practices

### Critical System Rails

**⚠️ WARNING**: Do NOT disable these on CoreS3:
- **ALDO1** (1.8V): Touch controller, sensors, I2C pullups
- **ALDO2** (3.3V): System peripherals, I2C devices
- **BLDO1/BLDO2**: Board-specific functions

Disabling these will cause system instability or failure.

### Current Limits

Never exceed these limits per rail:

| Rail Type | Max Current | Notes |
|-----------|-------------|-------|
| DCDC1-5   | 2000mA      | High current capable |
| ALDO1-4   | 300mA       | Low noise |
| BLDO1-2   | 300mA       | Backup capable |
| DLDO1-2   | 300mA       | General purpose |
| CPUSLDO   | 200mA       | CPU only |

### Voltage Ranges

Respect component voltage requirements:

```yaml
# BAD - might damage 3.3V device
output:
  - platform: axp2101
    channel: DCDC1
    voltage: 5000  # ERROR: Max is 3400mV!

# GOOD - safe voltage
output:
  - platform: axp2101
    channel: DCDC1
    voltage: 3300  # 3.3V, within range
```

### Temperature Monitoring

Monitor PMU temperature under load:

```yaml
sensor:
  - platform: axp2101
    type: temperature
    name: "PMU Temperature"
    on_value:
      then:
        - if:
            condition:
              lambda: 'return x > 80.0;'  # 80°C threshold
            then:
              - logger.log: "WARNING: PMU overheating!"
              # Reduce load or disable non-critical rails
```

## Troubleshooting

### System Won't Boot

**Symptom**: Board fails to start or reboots continuously

**Causes**:
- Critical rail (ALDO1/ALDO2) disabled
- Voltage set too low for components
- Overcurrent on rail

**Solution**:
1. Remove power management customizations
2. Flash with default configuration
3. Re-enable rails one at a time
4. Monitor PMU temperature

### Backlight Not Working

**Symptom**: LCD backlight stays off or dim

**Check**:
```yaml
# Verify backlight voltage range
substitutions:
  axp2101_backlight_min: "2600"  # Not too low
  axp2101_backlight_max: "3300"  # Not too high

# Check light entity
light:
  - platform: monochromatic
    name: "LCD Backlight"
    output: lcd_backlight_output
    # Should default to ON
    restore_mode: RESTORE_DEFAULT_ON
```

### Battery Not Charging

**Symptom**: Battery percentage decreases even when connected

**Check**:
1. Monitor battery voltage - should increase when charging
2. Check power supply provides enough current (1A+ recommended)
3. Verify USB-C cable supports power delivery
4. Check battery temperature isn't too high/low

### Power Rail Not Responding

**Symptom**: Switch doesn't control power rail

**Check**:
```yaml
# Verify output is defined
output:
  - platform: axp2101
    channel: DCDC1
    voltage: 3300
    id: my_power_rail  # ID is required!

# Verify switch references correct output
switch:
  - platform: output
    name: "My Power"
    output: my_power_rail  # Must match output ID
```

## Advanced Features

### Custom Voltage Regulation

Create dynamic voltage control:

```yaml
globals:
  - id: target_voltage
    type: float
    initial_value: '3.3'

number:
  - platform: template
    name: "Rail Voltage"
    min_value: 1.8
    max_value: 3.3
    step: 0.1
    optimistic: true
    set_action:
      - globals.set:
          id: target_voltage
          value: !lambda 'return x;'
      - output.set_level:
          id: variable_rail
          level: !lambda 'return (x - 1.8) / 1.5;'
```

### Power Sequencing

Control power-up order for sensitive hardware:

```yaml
script:
  - id: power_up_sequence
    then:
      # Step 1: Core power
      - switch.turn_on: rail_1v8
      - delay: 10ms
      # Step 2: I/O power
      - switch.turn_on: rail_3v3
      - delay: 10ms
      # Step 3: Peripheral power
      - switch.turn_on: rail_external
      - logger.log: "Power sequence complete"
```

### Battery Management

Monitor and protect battery:

```yaml
sensor:
  - platform: axp2101
    type: battery_voltage
    name: "Battery Voltage"
    on_value:
      then:
        # Low battery warning
        - if:
            condition:
              lambda: 'return x < 3.3;'
            then:
              - logger.log: "Low battery - shutting down peripherals"
              - switch.turn_off: external_power
        # Critical battery shutdown
        - if:
            condition:
              lambda: 'return x < 3.0;'
            then:
              - logger.log: "Critical battery - emergency shutdown"
              - deep_sleep.enter:
                  id: deep_sleep_control
```

## Reference Documents

- **Package**: `packages/board/board_options_power_axp2101.yaml`
- **Example**: `examples/boards/CoreS3_advanced_power_example.yaml`
- **Board**: `packages/board/board_ESP32-S3_CoreS3.yaml`
- **Datasheet**: [AXP2101 Datasheet](https://github.com/m5stack/M5-Schematic/blob/master/datasheet/AXP2101.pdf)

## Support

For issues or questions:
- GitHub: https://github.com/Sleeper85/esphome-yambms/issues
- ESPHome Community: https://community.home-assistant.io/c/esphome/

## Version History

- **1.0.0** (2025-12-23): Initial power management package release
  - 14 configurable power rails
  - Battery monitoring sensors
  - Comprehensive documentation
  - Advanced power example
