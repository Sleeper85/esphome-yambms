# YamBMS Multi-Node Examples

## Recommended: MQTT Multi-Node + Victron

**NEW!** Full MQTT solution for both multi-node BMS communication AND Victron integration.

### Why MQTT?

- **$0 cost** (no hardware bridges needed!)
- **0 GPIO pins** used (network only)
- **No CAN bus** hardware needed for Victron
- **Better performance** (lower latency, higher bandwidth)
- **Easier debugging** (standard MQTT tools)
- **Native mDNS/IPv6** support

### Quick Start (MQTT)

1. **Set up MQTT broker** (Home Assistant has one built-in!)

2. **Copy and configure secrets:**
   ```bash
   cp secrets.yaml.example secrets.yaml
   # Edit mqtt_broker, mqtt_username, mqtt_password
   ```

3. **Flash BMS server nodes:**
   ```bash
   esphome run MQTT_example_multi-node_YamBMS_server_1.yaml
   esphome run MQTT_example_multi-node_YamBMS_server_2.yaml
   ```

4. **Flash client/master node:**
   ```bash
   esphome run MQTT_example_multi-node_YamBMS_client_victron.yaml
   ```

5. **Optional: Configure Victron Cerbo GX**
   - Install venus-os_dbus-mqtt-battery driver
   - Configure to subscribe to yambms/victron/battery
   - No CAN bus hardware needed!

### Architecture

```
BMS Server 1 → MQTT Broker ← YamBMS Client → Victron Cerbo GX
BMS Server 2 →                              (Network only, $0!)
```

**That's it!** No hardware bridges, no CAN bus, just network connectivity.

### Documentation

- [MQTT Multi-Node Setup](#mqtt-multi-node-setup) (below)
- [YamBMS_MQTT_to_Victron_solution.md](../../documents/README/YamBMS_MQTT_to_Victron_solution.md) - Complete Victron integration guide
- [YamBMS_MQTT_vs_ModbusTCP_analysis.md](../../documents/README/YamBMS_MQTT_vs_ModbusTCP_analysis.md) - Performance comparison

---

## Alternative: TCP/Modbus Multi-Node (Legacy)

If you need TCP/Modbus for specific requirements:

## Quick Start (TCP/Modbus)

1. **Copy secrets template:**
   ```bash
   cp secrets.yaml.example secrets.yaml
   ```

2. **Edit secrets.yaml:**
   - Configure WiFi credentials
   - Set network settings (gateway, subnet)
   - Assign IP addresses or hostnames for each node

3. **Choose your addressing method:**
   - **Static IPv4** (recommended): Set `server1_ip`, `server2_ip`, etc.
   - **mDNS** (easier): Set `server1_hostname`, `server2_hostname`, etc.
   - **IPv6** (advanced): Set `server1_ipv6`, `server2_ipv6`, etc.

4. **Flash server nodes:**
   ```bash
   esphome run TCP_example_multi-node_YamBMS_server_1.yaml
   esphome run TCP_example_multi-node_YamBMS_server_2.yaml
   ```

5. **Configure hardware bridge** (for client)
   - Map Modbus addresses to server IPs from secrets.yaml

6. **Flash client node:**
   ```bash
   esphome run TCP_example_multi-node_YamBMS_client.yaml
   ```

## Addressing Methods

### Static IPv4 (Recommended)

**Pros:**
- Most reliable
- Works with all hardware bridges
- Easy troubleshooting

**Cons:**
- Manual IP management

**Configuration:**
```yaml
# secrets.yaml
server1_ip: "192.168.1.101"
server2_ip: "192.168.1.102"
```

### mDNS Hostnames

**Pros:**
- Easy to remember (server1.local)
- No IP management
- Auto-discovery

**Cons:**
- Hardware bridges may not support
- Requires mDNS on network
- Best for MQTT, not Modbus TCP

**Configuration:**
```yaml
# secrets.yaml
server1_hostname: "yambms-server-1"  # Resolves to yambms-server-1.local
server2_hostname: "yambms-server-2"
```

**Note:** For Modbus TCP with hardware bridge, still use static IPs in bridge configuration. mDNS is for node identification only.

### IPv6

**Pros:**
- Future-proof
- More addresses
- Link-local auto-configuration

**Cons:**
- May have compatibility issues
- Complex troubleshooting
- Not all bridges support IPv6

**Configuration:**
```yaml
# secrets.yaml
server1_ipv6: "fd00::101"  # ULA (stable)
server2_ipv6: "fd00::102"
```

**Note:** Use ULA (fd00::/8) addresses for stability. Avoid link-local (fe80::) as they change on reboot.

## Network Discovery

Each server node includes an "Access URLs" sensor showing all connection methods:

```
IPv4: 192.168.1.101:502
IPv6: [fd00::101]:502
mDNS: yambms-server-1.local:502
```

Check this sensor in Home Assistant or logs to find connection info.

## mDNS Service Discovery

Servers advertise themselves via mDNS with service type `_modbus-tcp._tcp.local`:

```bash
# Discover all Modbus TCP servers on network
dns-sd -B _modbus-tcp._tcp

# Or using avahi
avahi-browse -t _modbus-tcp._tcp
```

Service includes metadata:
- `bms_id`: Modbus address
- `role`: server or client
- `version`: Protocol version

## Security

**IMPORTANT:**
- Never commit `secrets.yaml` to git!
- The `.gitignore` file prevents accidental commits
- Use strong passwords
- Consider network segmentation (VLANs)

## Files

- `secrets.yaml.example` - Template (copy and customize)
- `secrets.yaml` - Your actual secrets (gitignored)
- `TCP_example_multi-node_YamBMS_server_1.yaml` - Server node 1
- `TCP_example_multi-node_YamBMS_server_2.yaml` - Server node 2
- `TCP_example_multi-node_YamBMS_client.yaml` - Master/client node

## Troubleshooting

### Can't resolve mDNS hostname

```bash
# Test mDNS resolution
ping yambms-server-1.local

# Check mDNS service
avahi-browse -a | grep modbus
```

If not working:
- Ensure mDNS enabled on all nodes
- Check firewall (UDP port 5353)
- Some networks block mDNS
- Use static IP instead

### IPv6 not working

```bash
# Check IPv6 address
esphome logs TCP_example_multi-node_YamBMS_server_1.yaml

# Ping IPv6
ping6 fd00::101
```

If not working:
- Ensure `enable_ipv6: true` in config
- Check router supports IPv6
- Verify no IPv6 firewall rules
- Use IPv4 instead

### Hardware bridge can't connect

Hardware bridges usually require:
- Static IPv4 addresses (not hostnames)
- Direct network connectivity
- Port 502 accessible

Use static IPs from secrets.yaml in bridge configuration.

## MQTT Multi-Node Setup

### Prerequisites

1. **MQTT Broker**
   - Home Assistant (has built-in Mosquitto)
   - Standalone Mosquitto
   - Any MQTT 3.1.1+ broker

2. **Network Connectivity**
   - WiFi or Ethernet
   - All nodes must reach broker
   - Recommended: wired Ethernet for servers

### Configuration Steps

#### 1. Configure secrets.yaml

```yaml
# MQTT Broker
mqtt_broker: "homeassistant.local"
mqtt_username: "yambms"
mqtt_password: "your_secure_password"

# Node addresses (for management/monitoring)
server1_hostname: "yambms-server-1"
server2_hostname: "yambms-server-2"
client_hostname: "yambms-client"
```

#### 2. Flash BMS Server Nodes

Each server monitors local BMS and publishes to MQTT:

```bash
# Server 1
esphome run MQTT_example_multi-node_YamBMS_server_1.yaml

# Server 2
esphome run MQTT_example_multi-node_YamBMS_server_2.yaml
```

**What servers do:**
- Read local BMS data via UART/BLE
- Publish all sensors to MQTT automatically
- Heartbeat every 10 seconds
- Birth/will messages for online status

**Topics published:**
```
yambms/server1/status                    → "online"/"offline"
yambms/server1/heartbeat                 → timestamp
yambms/server1/bms_1_total_voltage/state → 51.2
yambms/server1/bms_1_current/state       → 12.5
yambms/server1/bms_1_state_of_charge/state → 85
... (all BMS sensors)
```

#### 3. Flash Client/Master Node

```bash
esphome run MQTT_example_multi-node_YamBMS_client_victron.yaml
```

**What client does:**
- Subscribes to all server topics
- Combines BMS data using YamBMS logic
- Monitors server online status
- Publishes to Victron (optional)

#### 4. Optional: Victron Integration

**Install driver on Cerbo GX:**
```bash
ssh root@cerbo-gx.local
wget https://raw.githubusercontent.com/mr-manuel/venus-os_dbus-mqtt-battery/master/install.sh
bash install.sh
```

**Configure driver:**
```ini
# /data/etc/dbus-mqtt-battery/config.ini
[DEFAULT]
MQTT_BROKER = homeassistant.local
MQTT_PORT = 1883
MQTT_USERNAME = victron
MQTT_PASSWORD = your_password
MQTT_TOPIC = yambms/victron/battery
BATTERY_INSTANCE = 1
```

**Restart driver:**
```bash
svc -t /service/dbus-mqtt-battery
```

**Verify:**
- Check Cerbo GX → Settings → Battery Monitor
- Battery should appear as "MQTT Battery"
- All data visible in VRM Portal

### Monitoring

#### MQTT Explorer

Visual tool for monitoring all MQTT traffic:
- Download: [mqtt-explorer.com](http://mqtt-explorer.com)
- Connect to broker
- View all topics in real-time
- Inspect JSON payloads

#### mosquitto_sub

Command-line monitoring:

```bash
# Monitor all YamBMS topics
mosquitto_sub -h homeassistant.local -t "yambms/#" -v

# Monitor specific server
mosquitto_sub -h homeassistant.local -t "yambms/server1/#" -v

# Monitor Victron data
mosquitto_sub -h homeassistant.local -t "yambms/victron/battery" -v

# Check server status
mosquitto_sub -h homeassistant.local -t "yambms/server1/status" -v
```

#### Home Assistant

All sensors automatically discovered:
- Individual BMS sensors
- Combined YamBMS sensors
- Victron status sensors
- Online status for each server

### Troubleshooting

#### Server Not Publishing

**Check:**
1. MQTT broker accessible: `ping homeassistant.local`
2. Credentials correct in secrets.yaml
3. ESPHome logs: `esphome logs MQTT_example_...yaml`

**Look for:**
```
[mqtt:XXX] Connecting to MQTT...
[mqtt:XXX] MQTT Connected!
```

#### Client Not Receiving Data

**Check:**
1. Server online: `mosquitto_sub -t "yambms/server1/status"`
2. Server publishing: `mosquitto_sub -t "yambms/server1/#"`
3. Client subscribed: Check ESPHome logs
4. Heartbeat timeout: Max 30 seconds

#### Victron Not Seeing Battery

**Check:**
1. Driver installed: `svstat /service/dbus-mqtt-battery`
2. Driver logs: `tail -f /var/log/dbus-mqtt-battery/current`
3. MQTT topic correct in config.ini
4. Data publishing: `mosquitto_sub -t "yambms/victron/battery"`

**Expected JSON:**
```json
{
  "Voltage": 51.2,
  "Current": 12.5,
  "Soc": 85,
  "MaxChargeCurrent": 50,
  "MaxDischargeCurrent": 100,
  ...
}
```

### Performance

**Network Bandwidth:**
- Per server: ~1-2 kbps
- Total (3 servers): ~3-6 kbps
- Victron updates: ~500 bytes/sec

**Update Rates:**
- Server publish: As BMS updates (1-5 Hz)
- Client subscribe: Real-time (< 50ms latency)
- Victron publish: 1 Hz (configurable)
- Heartbeat: 10 seconds

**CPU Usage:**
- Server: 3-5% (vs 15% for TCP bridge)
- Client: 5-8% (combining + Victron)
- Network overhead: Minimal

### Security

**Production Recommendations:**

1. **Enable TLS/SSL:**
```yaml
mqtt:
  broker: homeassistant.local
  port: 8883  # SSL port
  certificate_authority: !secret mqtt_ca_cert
```

2. **Use ACLs (Mosquitto):**
```
# /etc/mosquitto/acl
user yambms_server1
topic write yambms/server1/#

user yambms_client
topic read yambms/server1/#
topic read yambms/server2/#
topic write yambms/victron/#

user victron
topic read yambms/victron/#
```

3. **Network Segmentation:**
- Dedicated VLAN for BMS/MQTT traffic
- Firewall rules restricting access
- VPN for remote monitoring

4. **Strong Passwords:**
- Different password per service
- 16+ characters
- Rotate periodically

### Comparison

| Feature | MQTT | TCP/Modbus | CAN Bus |
|---------|------|------------|---------|
| Hardware Cost | $0 | $30-100 | $20-50 |
| GPIO Pins | 0 | 0 | 2 |
| Latency | 5-20ms | 50-200ms | 10-50ms |
| Bandwidth | 10+ Mbps | 10+ Mbps | 250 kbps |
| Debugging | Easy | Medium | Hard |
| mDNS Support | ✅ | ❌ | ❌ |
| IPv6 Support | ✅ | ✅ | ❌ |
| Remote Access | ✅ | ✅ | ❌ |
| Setup Complexity | Low | Medium | Medium |
| Protocol | MQTT/JSON | Modbus TCP | CAN 2.0B |

**Winner:** MQTT for cost, flexibility, and ease of use!

---

## TCP/Modbus Documentation

Full documentation: `../../documents/README/YamBMS_multi-node_TCP_modbus_solution.md`
