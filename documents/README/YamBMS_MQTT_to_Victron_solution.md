# YamBMS MQTT to Victron Integration Solution

## Overview

**YES!** You can absolutely use the MQTT multi-node solution combined with Victron's DBus-MQTT integration to eliminate the CAN bus connection entirely. This creates a fully network-based solution for both multi-node BMS communication AND inverter communication.

## Architecture Comparison

### Current Architecture (CAN Bus)
```
BMS Servers → MQTT → YamBMS Client → CAN Bus Hardware → Victron Cerbo GX
                                      (GPIO, $20-50)
```

### Proposed Architecture (Full MQTT)
```
BMS Servers → MQTT Broker ← YamBMS Client → Victron Cerbo GX
                                             (Network only, $0)
```

## Key Benefits

### 1. **No CAN Bus Hardware Required**
- **Cost Savings**: $20-50 for CAN transceiver eliminated
- **GPIO Savings**: 2 GPIO pins freed (TX/RX for CAN)
- **Simpler Hardware**: No external CAN chips (MCP2515, ESP32-CAN, etc.)
- **One Less Failure Point**: Network-only communication

### 2. **Unified MQTT Architecture**
- **Single Protocol**: Everything uses MQTT
- **Consistent Management**: One broker, one protocol, one monitoring approach
- **Better Observability**: All traffic visible in MQTT logs
- **Easier Debugging**: MQTT tools (MQTT Explorer, mosquitto_sub) vs CAN bus analyzers

### 3. **Greater Flexibility**
- **Remote Placement**: YamBMS doesn't need physical CAN connection to Cerbo
- **Multiple Inverters**: Can control multiple Victron systems from one YamBMS
- **Cloud Integration**: Could route through external MQTT brokers if needed
- **Easier Testing**: Can test without inverter hardware using MQTT simulator

### 4. **Performance Advantages**
- **Lower Latency**: Direct network vs CAN bus arbitration
- **Higher Bandwidth**: MQTT over WiFi/Ethernet vs 250kbps CAN
- **Bidirectional**: Easy request/response patterns
- **QoS Support**: MQTT quality of service guarantees delivery

## Available Solutions

### Solution 1: venus-os_dbus-mqtt-battery (Recommended)

**Project**: [mr-manuel/venus-os_dbus-mqtt-battery](https://github.com/mr-manuel/venus-os_dbus-mqtt-battery)

**What It Does**:
- Installs as driver on Victron Cerbo GX / Venus OS
- Subscribes to MQTT topic for battery data (JSON format)
- Publishes to Venus DBus as `com.victronenergy.battery.mqtt_battery`
- Appears as native battery in Victron system

**MQTT Topic Format**:
```
/N/<VRM_ID>/battery/<BATTERY_INSTANCE>/JsonData
```

**Supported Data Fields**:
- DC voltage, current, power
- State of charge (SoC), state of health (SoH)
- Temperature (battery, cells)
- Cell voltages (individual)
- Charge/discharge current limits
- Capacity (total, consumed, remaining)
- Alarms (voltage, current, temperature, cell imbalance)
- Time to empty/full
- Cell balancing status

**ESPHome Compatibility**: ✅ **Perfect Match**
- ESPHome MQTT native support
- JSON publish capability built-in
- All YamBMS data already available

### Solution 2: dbus-mqtt-devices

**Project**: [freakent/dbus-mqtt-devices](https://github.com/freakent/dbus-mqtt-devices)

**What It Does**:
- More generic device registration framework
- Supports multiple device types (battery, temperature, tank, PV, etc.)
- Wi-Fi devices self-register via MQTT
- More complex but more flexible

**Use Case**: If you want to register multiple device types or need more control

### Solution 3: dbus-mqtt-services

**Community Project**: Available on Victron Community

**What It Does**:
- Create any dbus service from MQTT without custom driver
- Lightweight, no installation required
- More manual configuration

## Implementation Design

### Component Architecture

```yaml
┌─────────────────────────────────────────────────────────────┐
│                    MQTT Broker                               │
│              (Home Assistant / Mosquitto)                    │
└───────┬──────────────────────────────────────┬──────────────┘
        │                                      │
   ┌────▼─────────┐                      ┌────▼──────────────┐
   │  BMS Servers │                      │  Victron Cerbo GX │
   │              │                      │   (Venus OS)       │
   │ - Server 1   │                      │                    │
   │ - Server 2   │                      │ dbus-mqtt-battery  │
   │ - Server N   │                      │      driver        │
   └────┬─────────┘                      └────▲──────────────┘
        │                                     │
        │ Publish BMS data:                  │ Subscribe:
        │ yambms/server1/...                 │ yambms/combined/battery
        │                                    │
   ┌────▼─────────────────────────────────────┴──────────────┐
   │              YamBMS Client (Master)                      │
   │                                                           │
   │ 1. Subscribe to all BMS server topics                   │
   │ 2. Combine/calculate aggregated data                    │
   │ 3. Publish to Victron MQTT topic (JSON)                │
   │                                                           │
   │ No CAN bus hardware required!                            │
   └─────────────────────────────────────────────────────────┘
```

### YamBMS to Victron Data Mapping

YamBMS currently sends this data via CAN (PYLON protocol):

| CAN ID | YamBMS Data | Victron MQTT Field | Notes |
|--------|-------------|-------------------|-------|
| 0x351 | Charge voltage/current limits | `ChargeVoltage`, `MaxChargeCurrent` | Direct mapping |
| 0x351 | Discharge voltage/current limits | `DischargeVoltage`, `MaxDischargeCurrent` | Direct mapping |
| 0x355 | SOC, SOH | `Soc`, `Soh` | Percentage values |
| 0x355 | Capacity remaining | `InstalledCapacity`, `ConsumedAmphours` | Calculate consumed |
| 0x356 | Total voltage, current | `Voltage`, `Current`, `Power` | Power = V × I |
| 0x356 | Temperature (avg) | `Temperature` | Average of min/max |
| 0x35A | Alarms (over/under voltage/temp/current) | `Alarms` object | Map bitmask to JSON |
| 0x35B | Warnings | `Warnings` object | Map bitmask to JSON |
| 0x35E | Battery name | `ProductName`, `FirmwareVersion` | Metadata |
| 0x370 | Min/max cell voltages | `MinCellVoltage`, `MaxCellVoltage` | mV to V |
| 0x371 | Cell voltage sensor IDs | `MinVoltageCellId`, `MaxVoltageCellId` | Cell numbers |
| 0x373 | Min/max temperatures | `MinTemperature`, `MaxTemperature` | Include sensor IDs |
| 0x374 | Min cell ID | `MinVoltageCellId` | ASCII format |
| 0x375 | Max cell ID | `MaxVoltageCellId` | ASCII format |

**Perfect Alignment**: The data YamBMS sends via CAN is nearly identical to what Victron expects via MQTT!

### Example MQTT Payload

```json
{
  "Voltage": 51.2,
  "Current": 12.5,
  "Power": 640,
  "Soc": 85,
  "Soh": 98,
  "Temperature": 23.5,
  "MaxChargeCurrent": 50,
  "MaxDischargeCurrent": 100,
  "ChargeVoltage": 58.4,
  "DischargeVoltage": 42.0,
  "InstalledCapacity": 280,
  "ConsumedAmphours": 42,
  "MinCellVoltage": 3.198,
  "MaxCellVoltage": 3.215,
  "MinVoltageCellId": "04",
  "MaxVoltageCellId": "09",
  "MinTemperature": 22.1,
  "MaxTemperature": 24.8,
  "Alarms": {
    "HighVoltage": 0,
    "LowVoltage": 0,
    "HighTemperature": 0,
    "LowTemperature": 0,
    "HighChargeCurrent": 0,
    "HighDischargeCurrent": 0,
    "CellImbalance": 0,
    "InternalFailure": 0
  },
  "Warnings": {
    "HighVoltage": 0,
    "LowVoltage": 0,
    "HighTemperature": 0,
    "LowTemperature": 0
  },
  "ProductName": "YamBMS",
  "FirmwareVersion": "1.0.0",
  "TimeToGo": 3600,
  "Balancing": 0
}
```

## Implementation Steps

### 1. Install venus-os_dbus-mqtt-battery on Cerbo GX

```bash
# SSH into Cerbo GX
ssh root@cerbo-gx.local

# Download and install driver
wget -O /tmp/install.sh https://raw.githubusercontent.com/mr-manuel/venus-os_dbus-mqtt-battery/master/install.sh
bash /tmp/install.sh
```

### 2. Configure Driver

Edit `/data/etc/dbus-mqtt-battery/config.ini`:

```ini
[DEFAULT]
# MQTT broker settings
MQTT_BROKER = homeassistant.local
MQTT_PORT = 1883
MQTT_USERNAME = victron
MQTT_PASSWORD = your_password

# Topic to subscribe to
MQTT_TOPIC = yambms/combined/battery

# Battery instance
BATTERY_INSTANCE = 1
```

### 3. Create YamBMS MQTT Package

New file: `packages/inverter/inverter_victron_mqtt.yaml`

```yaml
# Victron MQTT Integration Package
# Publishes battery data to Victron Cerbo GX via MQTT

mqtt:
  broker: !secret mqtt_broker
  username: !secret mqtt_username
  password: !secret mqtt_password
  topic_prefix: yambms/combined

  # Publish combined battery data as JSON
  on_message:
    - topic: yambms/publish_trigger
      then:
        - mqtt.publish_json:
            topic: yambms/combined/battery
            payload: !lambda |-
              return {
                {"Voltage", id(yambms_total_voltage).state},
                {"Current", id(yambms_current).state},
                {"Power", id(yambms_power).state},
                {"Soc", (int)id(yambms_battery_soc).state},
                {"Soh", (int)id(yambms_battery_soh).state},
                {"Temperature", (id(yambms_min_temperature).state + id(yambms_max_temperature).state) / 2.0},
                {"MaxChargeCurrent", id(yambms_requested_charge_current).state},
                {"MaxDischargeCurrent", id(yambms_requested_discharge_current).state},
                {"ChargeVoltage", id(yambms_requested_charge_voltage).state},
                {"DischargeVoltage", id(yambms_requested_discharge_voltage).state},
                {"InstalledCapacity", id(yambms_battery_capacity_total).state},
                {"ConsumedAmphours", id(yambms_battery_capacity_total).state - id(yambms_battery_capacity_remaining).state},
                {"MinCellVoltage", id(yambms_min_cell_voltage).state},
                {"MaxCellVoltage", id(yambms_max_cell_voltage).state},
                {"MinVoltageCellId", std::to_string((int)id(yambms_min_voltage_cell).state)},
                {"MaxVoltageCellId", std::to_string((int)id(yambms_max_voltage_cell).state)},
                {"MinTemperature", id(yambms_min_temperature).state},
                {"MaxTemperature", id(yambms_max_temperature).state},
                {"ProductName", "YamBMS"},
                {"FirmwareVersion", "1.0.0"},
                {"Balancing", id(yambms_balancing).state ? 1 : 0}
              };

# Publish battery data every 1 second
interval:
  - interval: 1s
    then:
      - mqtt.publish:
          topic: yambms/publish_trigger
          payload: "trigger"
```

### 4. Update Multi-Node Client Configuration

```yaml
# Use MQTT instead of CAN bus
packages:
  # Multi-node BMS via MQTT
  bms1: !include
    file: ../../packages/bms/bms_combine_mqtt_client.yaml
    vars:
      bms_id: '1'
      mqtt_topic: 'yambms/server1'

  bms2: !include
    file: ../../packages/bms/bms_combine_mqtt_client.yaml
    vars:
      bms_id: '2'
      mqtt_topic: 'yambms/server2'

  # YamBMS combination logic
  yambms: !include ../../packages/yambms.yaml

  # Victron via MQTT (instead of CAN bus!)
  inverter: !include
    file: ../../packages/inverter/inverter_victron_mqtt.yaml
    vars:
      mqtt_broker: !secret mqtt_broker

# No CAN bus hardware needed!
# No UART configuration!
# Just network connectivity!
```

## Performance Comparison

### CAN Bus Approach
| Metric | Value | Notes |
|--------|-------|-------|
| Latency | 10-50ms | CAN bus arbitration |
| Bandwidth | 250 kbps | CAN 2.0B limit |
| Update Rate | 1 Hz | Limited by CAN frame rate |
| Hardware Cost | $20-50 | CAN transceiver required |
| GPIO Usage | 2 pins | TX/RX |
| Debugging | Difficult | Requires CAN analyzer |
| Flexibility | Low | Physical connection required |

### MQTT Approach
| Metric | Value | Notes |
|--------|-------|-------|
| Latency | 5-20ms | Direct TCP/IP |
| Bandwidth | 10+ Mbps | WiFi/Ethernet |
| Update Rate | 1-10 Hz | Configurable, limited only by network |
| Hardware Cost | $0 | Uses existing network |
| GPIO Usage | 0 pins | Network only |
| Debugging | Easy | Standard MQTT tools |
| Flexibility | High | Can be anywhere on network |

**Winner**: MQTT is faster, cheaper, easier to debug, and more flexible!

## Security Considerations

### MQTT Security (Recommended)
```yaml
mqtt:
  broker: !secret mqtt_broker
  port: 8883  # TLS/SSL
  username: !secret mqtt_username
  password: !secret mqtt_password
  # Optional: client certificate
  certificate_authority: !secret mqtt_ca_cert
```

### Network Segmentation
- Place MQTT broker on isolated VLAN
- Use firewall rules to restrict access
- Consider VPN for remote access
- Enable Victron firewall rules

### Access Control
```ini
# Mosquitto ACL example
user victron
topic read yambms/combined/#
topic write yambms/combined/battery

user yambms
topic write yambms/#
topic read yambms/combined/battery/status
```

## Monitoring and Debugging

### MQTT Explorer
- View all topics in real-time
- Inspect JSON payloads
- Manually publish test messages
- Monitor connection status

### Home Assistant
```yaml
# Monitor MQTT traffic
sensor:
  - platform: mqtt
    name: "YamBMS Battery Voltage"
    state_topic: "yambms/combined/battery"
    value_template: "{{ value_json.Voltage }}"
    unit_of_measurement: "V"
    device_class: voltage

  - platform: mqtt
    name: "YamBMS Battery Current"
    state_topic: "yambms/combined/battery"
    value_template: "{{ value_json.Current }}"
    unit_of_measurement: "A"
    device_class: current
```

### Venus OS Monitoring
```bash
# View DBus battery service
dbus -y com.victronenergy.battery.mqtt_battery

# Monitor MQTT traffic on Cerbo
mosquitto_sub -h localhost -t "yambms/#" -v

# Check driver status
svstat /service/dbus-mqtt-battery
```

## Migration Path

### Phase 1: Parallel Operation (Testing)
1. Keep existing CAN bus connection active
2. Add MQTT publishing to YamBMS
3. Install dbus-mqtt-battery on Cerbo
4. Monitor both connections in parallel
5. Verify MQTT data matches CAN data

### Phase 2: MQTT Cutover
1. Disable CAN bus in YamBMS configuration
2. Switch Victron to use MQTT battery
3. Monitor for 24-48 hours
4. Verify all alarms/warnings work correctly

### Phase 3: Hardware Removal
1. Remove CAN transceiver hardware
2. Free GPIO pins for other uses
3. Update documentation
4. Celebrate simplified system!

## Limitations and Considerations

### 1. Network Dependency
- **Risk**: MQTT communication depends on network reliability
- **Mitigation**: Use wired Ethernet where possible, monitor network health
- **Fallback**: Keep CAN hardware as backup option

### 2. Venus OS Updates
- **Risk**: Venus OS updates might overwrite driver installation
- **Mitigation**: Document installation, create backup script
- **Solution**: Driver supports persistence across most updates

### 3. MQTT Broker Availability
- **Risk**: Broker failure breaks communication
- **Mitigation**: Use HA broker setup, monitor broker health
- **Fallback**: Local broker on Cerbo GX as backup

### 4. Update Rate
- **Limit**: Don't exceed 10 Hz update rate (MQTT overhead)
- **Recommendation**: 1 Hz is sufficient for battery monitoring
- **Note**: Faster than CAN bus anyway (typically limited to 1 Hz)

## Cost-Benefit Analysis

### Savings
- CAN transceiver hardware: $20-50 saved
- 2 GPIO pins freed: Value depends on board
- Simplified wiring: Easier installation
- Development time: Faster debugging with MQTT tools

### Costs
- MQTT broker: $0 (use existing) or ~$5-10/month (cloud)
- Venus driver installation: 15 minutes one-time
- Learning curve: Understanding MQTT and dbus-mqtt integration

**Net Benefit**: Significant savings and improved flexibility!

## Conclusion

**YES, implementing the full MQTT solution is not only possible but RECOMMENDED!**

### Why This Is Better

1. **Eliminates CAN Bus Hardware**: $20-50 saved, 2 GPIO pins freed
2. **Unified Architecture**: Everything uses MQTT, simpler to understand
3. **Better Performance**: Lower latency, higher bandwidth than CAN
4. **Easier Debugging**: Standard MQTT tools vs specialized CAN analyzers
5. **More Flexible**: Remote placement, multiple inverters, cloud integration
6. **Already Proven**: Multiple community projects demonstrate success
7. **Perfect Data Match**: YamBMS data maps cleanly to Victron MQTT format

### Recommended Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│  BMS        │ MQTT    │  MQTT       │ MQTT    │   Victron    │
│  Server 1   ├────────►│  Broker     │◄────────┤   Cerbo GX   │
└─────────────┘         │             │         │              │
┌─────────────┐         │ (Home       │         │ dbus-mqtt-   │
│  BMS        │ MQTT    │  Assistant  │         │   battery    │
│  Server 2   ├────────►│  Mosquitto) │         │   driver     │
└─────────────┘         └──────▲──────┘         └──────────────┘
┌─────────────┐                │
│  BMS        │ MQTT            │ MQTT
│  Server N   ├────────────────┘
└─────────────┘

All communication over network - NO CAN bus hardware needed!
```

### Next Steps

1. Implement MQTT multi-node solution (from previous analysis)
2. Install venus-os_dbus-mqtt-battery on Cerbo GX
3. Create YamBMS Victron MQTT package
4. Test in parallel with existing CAN bus
5. Cut over to full MQTT operation
6. Remove CAN hardware

**This is the future of YamBMS multi-node + Victron integration!**

## References

- [venus-os_dbus-mqtt-battery](https://github.com/mr-manuel/venus-os_dbus-mqtt-battery) - MQTT to Victron battery driver
- [dbus-mqtt-devices](https://github.com/freakent/dbus-mqtt-devices) - Generic device registration framework
- [Victron dbus-mqtt](https://github.com/victronenergy/dbus-mqtt) - Official Venus OS MQTT gateway (now dbus-flashmq)
- [ESPHome MQTT](https://esphome.io/components/mqtt.html) - Native MQTT support
- [YamBMS MQTT Analysis](YamBMS_MQTT_vs_ModbusTCP_analysis.md) - Our previous multi-node MQTT analysis
- [Victron Community: BMS via MQTT](https://community.victronenergy.com/t/bms-communication-via-mqtt-to-victron-gx/15473) - Community discussion

## Version History

- **1.0.0** (2025-12-23): Initial analysis
  - Full MQTT architecture design
  - Data mapping CAN to MQTT
  - Implementation guide
  - Performance comparison
  - Security recommendations
