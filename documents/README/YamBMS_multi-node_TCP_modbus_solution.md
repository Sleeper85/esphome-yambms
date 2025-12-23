# YamBMS Multi-Node TCP/IP Modbus Solution

**Version:** 1.0.0
**Updated:** 2025-12-23
**Author:** YamBMS Community

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Benefits vs RS485](#benefits-vs-rs485)
4. [Requirements](#requirements)
5. [Quick Start Guide](#quick-start-guide)
6. [Server Node Configuration](#server-node-configuration)
7. [Client Node Configuration](#client-node-configuration)
8. [Network Setup](#network-setup)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tuning](#performance-tuning)
11. [Security Considerations](#security-considerations)
12. [FAQ](#faq)

---

## Overview

The TCP/IP Modbus solution enables YamBMS multi-node configurations to communicate over network (WiFi/Ethernet) instead of RS485 serial bus. This is achieved using the `esphome_modbus_bridge` component which provides transparent Modbus TCP ↔ RTU bridging.

### Traditional RS485 Multi-Node

```
┌─────────┐    RS485    ┌─────────┐    RS485    ┌─────────┐
│ Master  │◄────────────►│ BMS 1   │◄────────────►│ BMS 2   │
│ (Client)│   shared bus │ Server  │  shared bus  │ Server  │
└─────────┘              └─────────┘              └─────────┘
```

**Limitations:**
- Max distance: ~1200m
- Single shared bus
- Complex wiring for distributed systems
- RS485 transceivers required
- Termination resistors needed

### New TCP/IP Multi-Node

```
                    Network (WiFi/Ethernet)
                    ┌────────────┬────────────┐
                    │            │            │
               ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
               │ Master  │  │ BMS 1   │  │ BMS 2   │
               │ (Client)│  │ Server  │  │ Server  │
               └─────────┘  └─────────┘  └─────────┘
                   :502         :502         :502
```

**Advantages:**
- No distance limits (network reach)
- Easy to add/remove nodes
- Uses existing network infrastructure
- No RS485 hardware needed on network segments
- Flexible topology

---

## Architecture

### Component Stack

#### Server Nodes (BMS/Shunt monitoring)

```
┌─────────────────────────────────────┐
│         Network (WiFi/Ethernet)     │
│              Port 502               │
├─────────────────────────────────────┤
│     esphome_modbus_bridge           │
│   (TCP ↔ RTU Translation)           │
├─────────────────────────────────────┤
│     Modbus RTU Server               │
│   (BMS Data Registers)              │
├─────────────────────────────────────┤
│     Local BMS/Shunt                 │
│   (UART Communication)              │
└─────────────────────────────────────┘
```

**Exposed Modbus TCP Registers:**
- Register 1: online_status
- Register 2-3: charging/discharging_allowed
- Register 5-6: total_voltage (mV)
- Register 7-8: current (mA)
- Register 9-10: power (mW)
- Register 11-33+: SoC, capacity, temperatures, cell voltages, etc.

#### Client Node (Master)

**Current Implementation:** Hardware Bridge Approach

```
┌─────────────────────────────────────┐
│         ESP32 (YamBMS Client)       │
│    (Modbus RTU Client)              │
├─────────────────────────────────────┤
│         UART / RS485                │
├─────────────────────────────────────┤
│   Hardware TCP-to-RS485 Bridge      │
│   (Modbus TCP Client)               │
│   Maps Addr 1→IP1, Addr 2→IP2       │
├─────────────────────────────────────┤
│      Network (WiFi/Ethernet)        │
│    Connects to Server Nodes         │
└─────────────────────────────────────┘
```

**Future:** Native TCP client when ESPHome adds support (see [Issue #708](https://github.com/esphome/feature-requests/issues/708))

---

## Benefits vs RS485

| Feature | RS485 | TCP/IP |
|---------|-------|--------|
| **Max Distance** | ~1200m | Unlimited (network reach) |
| **Topology** | Shared bus | Star/any network topology |
| **Wiring Complexity** | High (long runs) | Low (use existing network) |
| **Adding Nodes** | Rewire bus | Just add to network |
| **Hardware Cost** | RS485 transceivers + cable | Use existing WiFi/Ethernet |
| **Latency** | <1ms | 5-50ms (WiFi), 2-10ms (Ethernet) |
| **Reliability** | Very high (wired) | High (Ethernet), Medium (WiFi) |
| **Installation** | Complex for distributed | Simple (network) |
| **Troubleshooting** | Multimeter/scope | Standard network tools |
| **Security** | Physical access only | Network security required |

**Use TCP/IP When:**
- ✅ Nodes are far apart (>100m)
- ✅ Using existing network infrastructure
- ✅ Frequently adding/removing nodes
- ✅ Distributed battery installations
- ✅ Difficult to run cables

**Use RS485 When:**
- ✅ All nodes in same location
- ✅ Need lowest latency
- ✅ Maximum reliability required
- ✅ No network infrastructure
- ✅ Security concerns with network

---

## Requirements

### Hardware Requirements

#### Server Nodes
- ESP32 board (any variant)
- Network connectivity:
  - **WiFi:** Built-in on all ESP32
  - **Ethernet:** Boards with Ethernet support (recommended):
    - ESP32-C3-ETH01-EVO
    - ESP32-WT32-ETH01
    - ESP32-S3-WS-ETH
- BMS connection (UART)
- Power supply

#### Client Node
- ESP32 board with RS485 interface OR
- ESP32 board + RS485 transceiver
- Hardware TCP-to-RS485 bridge:
  - EBYTE NT1 (~$40)
  - USR-TCP232-410S (~$30)
  - Elfin-EE11 (~$50)
  - WaveShare RS485 to ETH (~$25)
- OR: Spare ESP32 as DIY bridge
- CAN interface for inverter
- Power supply

### Network Requirements
- Local network (WiFi AP or Ethernet switch)
- All nodes on same network or routable
- Port 502 accessible between nodes
- Recommended: Static IP addresses or DHCP reservations
- Optional: mDNS support for discovery

### Software Requirements
- ESPHome 2024.11.0 or newer
- External component: `esphome_modbus_bridge`
- YamBMS packages (this repository)

---

## Quick Start Guide

### Step 1: Plan Your Network

1. **Assign IP Addresses** (static recommended):
   - Master: 192.168.1.100
   - Server 1: 192.168.1.101
   - Server 2: 192.168.1.102
   - Server 3: 192.168.1.103
   - etc.

2. **Assign Modbus Addresses:**
   - Server 1: `bms_id: '1'`
   - Server 2: `bms_id: '2'`
   - Server 3: `bms_id: '3'`
   - etc.

3. **Network Infrastructure:**
   - WiFi: Configure SSID/password
   - Ethernet: Prepare network cables
   - Ensure port 502 is not blocked

### Step 2: Configure Server Nodes

1. **Copy Example Configuration:**
   ```bash
   cp examples/multi-node/TCP_example_multi-node_YamBMS_server_1.yaml \
      my_bms_server_1.yaml
   ```

2. **Edit Configuration:**
   ```yaml
   substitutions:
     hostname: 'yambms-tcp-server-1'
     bms_id: '1'  # Unique for each server
     static_ip: '192.168.1.101'  # Unique for each server
   ```

3. **Select Your Board:**
   - Uncomment appropriate board package
   - Configure UART pins for your board

4. **Configure Your BMS:**
   - Select BMS package (JK, Daly, etc.)
   - Configure UART pins

5. **Compile and Flash:**
   ```bash
   esphome run my_bms_server_1.yaml
   ```

6. **Verify Operation:**
   - Check logs for "Modbus TCP Bridge Active"
   - Note IP address from logs
   - Test with Modbus TCP tool:
     ```bash
     # Linux/Mac
     mbpoll -a 1 -r 1 -c 10 192.168.1.101
     ```

7. **Repeat for Each Server Node**
   - Server 2: `bms_id: '2'`, `static_ip: '192.168.1.102'`
   - Server 3: `bms_id: '3'`, `static_ip: '192.168.1.103'`

### Step 3: Configure Hardware Bridge

**Option A: Commercial Bridge (EBYTE NT1 example)**

1. Connect bridge to network
2. Access web interface (check bridge documentation)
3. Configure Modbus TCP Client mode
4. Add server mappings:
   - Modbus Address 1 → 192.168.1.101:502
   - Modbus Address 2 → 192.168.1.102:502
   - Modbus Address 3 → 192.168.1.103:502
5. Configure RS485 settings:
   - Baud: 19200
   - Data: 8
   - Parity: None
   - Stop: 1

**Option B: DIY ESP32 Bridge**

(Advanced - requires custom configuration)

### Step 4: Configure Client Node

1. **Copy Example:**
   ```bash
   cp examples/multi-node/TCP_example_multi-node_YamBMS_client.yaml \
      my_bms_client.yaml
   ```

2. **Edit Configuration:**
   ```yaml
   substitutions:
     hostname: 'yambms-tcp-client'

   # Include BMS clients for each server
   packages:
     bms1: !include
       file: ../../packages/bms/bms_combine_modbus_client.yaml
       vars:
         bms_id: '1'
     bms2: !include
       file: ../../packages/bms/bms_combine_modbus_client.yaml
       vars:
         bms_id: '2'
   ```

3. **Wire Hardware:**
   - ESP32 RS485 ↔ Hardware Bridge RS485
   - Hardware Bridge Ethernet ↔ Network

4. **Flash and Test:**
   ```bash
   esphome run my_bms_client.yaml
   ```

5. **Verify:**
   - Check logs for successful BMS polling
   - Monitor "BMS X Online Status" sensors
   - Verify data from all server nodes

### Step 5: Integrate with Inverter

1. **Configure CAN Interface:**
   ```yaml
   packages:
     canbus: !include
       file: packages/board/board_options_itf_canbus_esp32_can.yaml
   ```

2. **Configure Inverter Protocol:**
   ```yaml
   packages:
     inverter: !include
       file: packages/inverter/protocol_PYLON_CAN.yaml
   ```

3. **Test End-to-End:**
   - Verify combined BMS data
   - Check inverter communication
   - Monitor charging/discharging

---

## Server Node Configuration

### Full Example with Comments

See: `examples/multi-node/TCP_example_multi-node_YamBMS_server_1.yaml`

### Key Configuration Points

#### Network Configuration

**WiFi with Static IP (Recommended):**
```yaml
wifi:
  id: my_network
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  manual_ip:
    static_ip: 192.168.1.101
    gateway: 192.168.1.1
    subnet: 255.255.255.0
```

**Ethernet with Static IP (Most Reliable):**
```yaml
ethernet:
  id: my_network
  type: LAN8720  # Or W5500, DM9051
  mdc_pin: GPIO23
  mdio_pin: GPIO18
  clk_mode: GPIO0_IN
  phy_addr: 1
  manual_ip:
    static_ip: 192.168.1.101
    gateway: 192.168.1.1
    subnet: 255.255.255.0
```

#### Modbus TCP Server Package

```yaml
packages:
  bms_tcp: !include
    file: packages/bms/bms_modbus_tcp_server.yaml
    vars:
      bms_id: '1'  # Unique Modbus address
      modbus_uart_id: 'uart_esp_1'
      modbus_role: 'server'
```

This package includes:
- Modbus RTU server (bms_modbus_server.yaml)
- TCP bridge (board_options_itf_modbus_tcp_bridge.yaml)
- Network monitoring sensors

#### BMS Configuration

Choose your BMS type:

```yaml
packages:
  bms1: !include
    file: packages/bms/bms_JK_UART.yaml  # or bms_Daly_UART.yaml, etc.
    vars:
      bms_id: '1'
      bms_name: 'JK-BMS 1'
      bms_uart_id: 'uart_esp_2'  # Different from modbus_uart_id
      bms_cell_max_cycles: '6000.0'
```

#### UART Pin Configuration

```yaml
uart:
  # UART for Modbus bridge (internal use)
  - id: uart_esp_1
    tx_pin: GPIO17
    rx_pin: GPIO16
    baud_rate: 19200

  # UART for BMS communication
  - id: uart_esp_2
    tx_pin: GPIO14
    rx_pin: GPIO12
    baud_rate: 115200  # Match your BMS
```

### Monitoring Server Status

The TCP server configuration includes sensors:

- **Binary Sensor:** `Modbus TCP Bridge Active`
  - Shows if bridge is operational
- **Sensor:** `WiFi Signal` (if using WiFi)
  - Monitor connection quality
- **Text Sensor:** `IP Address`
  - Shows current IP address

### Board-Specific Configurations

#### ESP32-C3-ETH01-EVO (Ethernet)

```yaml
packages:
  board: !include packages/board/board_ESP32-C3_ETH01-EVO.yaml

ethernet:
  id: my_network
  type: DM9051
  spi_id: spi_bus
  cs_pin: GPIO7
  interrupt_pin: GPIO8
  reset_pin: GPIO9
```

#### M5Stack CoreS3 (WiFi)

```yaml
packages:
  board: !include packages/board/board_ESP32-S3_CoreS3.yaml

wifi:
  id: my_network
  ssid: !secret wifi_ssid
  password: !secret wifi_password
```

---

## Client Node Configuration

### Hardware Bridge Setup

**Critical:** ESPHome does not currently support native Modbus TCP client.
You MUST use a hardware bridge or wait for future ESPHome support.

#### Commercial Bridge Configuration

Using EBYTE NT1 as example:

1. **Physical Connection:**
   ```
   ESP32 GPIO17 (TX) → RS485 A
   ESP32 GPIO16 (RX) → RS485 B
   RS485 GND → GND

   Bridge RS485 ↔ ESP32 RS485
   Bridge Ethernet ↔ Network Switch
   ```

2. **Bridge Web Configuration:**
   - Access: http://192.168.1.xxx (default from bridge)
   - Mode: **Modbus TCP Client**
   - Add servers:
     ```
     Server 1: 192.168.1.101:502, Modbus Address: 1
     Server 2: 192.168.1.102:502, Modbus Address: 2
     Server 3: 192.168.1.103:502, Modbus Address: 3
     ```
   - RS485 Settings:
     - Baud: 19200
     - Data Bits: 8
     - Parity: None
     - Stop Bits: 1
   - Save and reboot bridge

3. **ESP32 Configuration:**
   ```yaml
   packages:
     modbus_itf: !include
       file: packages/board/board_options_itf_modbus.yaml
       vars:
         modbus_role: 'client'
         modbus_uart_id: 'uart_esp_1'

     bms1: !include
       file: packages/bms/bms_combine_modbus_client.yaml
       vars:
         bms_id: '1'  # Bridge translates to 192.168.1.101:502

     bms2: !include
       file: packages/bms/bms_combine_modbus_client.yaml
       vars:
         bms_id: '2'  # Bridge translates to 192.168.1.102:502
   ```

#### DIY ESP32 Bridge

**Advanced Users:** Use spare ESP32 as bridge

Configuration coming soon (requires custom bridge client code)

---

## Network Setup

### IP Address Planning

#### Option 1: Static IPs (Recommended)

**Advantages:**
- Predictable addresses
- Easier troubleshooting
- No DHCP dependency

**Configuration:**
```yaml
wifi:
  manual_ip:
    static_ip: 192.168.1.101
    gateway: 192.168.1.1
    subnet: 255.255.255.0
    dns1: 192.168.1.1
```

**IP Assignment Table:**

| Node | Purpose | IP Address |
|------|---------|------------|
| Router | Gateway | 192.168.1.1 |
| Master | Client | 192.168.1.100 |
| BMS Server 1 | Server | 192.168.1.101 |
| BMS Server 2 | Server | 192.168.1.102 |
| BMS Server 3 | Server | 192.168.1.103 |
| Bridge | Hardware | 192.168.1.105 |

#### Option 2: DHCP with Reservations

**Advantages:**
- Automatic configuration
- Easier initial setup

**Router Configuration:**
- Reserve IPs based on MAC address
- Note: MAC address shown in ESPHome logs

### Firewall Configuration

**Port Requirements:**
- **502/TCP:** Modbus TCP (server nodes)
- **6053/TCP:** ESPHome API (all nodes)
- **3232/UDP:** mDNS discovery (optional)

**Firewall Rules (example iptables):**
```bash
# Allow Modbus TCP to server nodes
iptables -A INPUT -p tcp --dport 502 -j ACCEPT

# Allow ESPHome API
iptables -A INPUT -p tcp --dport 6053 -j ACCEPT

# Allow mDNS
iptables -A INPUT -p udp --dport 5353 -j ACCEPT
```

### VLAN Isolation (Optional)

For security, isolate BMS network:

```
VLAN 10: Main Network
VLAN 20: BMS Network (isolated)
  - All BMS nodes
  - Home Assistant server (trunk)
```

**Benefits:**
- Network isolation
- Security
- QoS control

### Network Diagnostics

#### Test Connectivity

**From Client to Server:**
```bash
# Ping test
ping 192.168.1.101

# Port test
nc -zv 192.168.1.101 502

# Modbus test (requires modbus tools)
mbpoll -a 1 -r 1 -c 5 192.168.1.101
```

#### Monitor Network

**ESPHome Sensors:**
```yaml
sensor:
  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s
```

**External Tools:**
- Wireshark: Capture Modbus TCP packets
- nmap: Scan for open ports
- ping: Monitor latency

---

## Troubleshooting

### Server Node Issues

#### Problem: Bridge Not Active

**Symptoms:**
- "Modbus TCP Bridge Active" sensor shows false
- Port 502 not responding

**Solutions:**
1. Check network connectivity:
   ```bash
   ping <server_ip>
   ```
2. Verify WiFi/Ethernet connection in logs
3. Check firewall rules
4. Verify external_components loaded:
   ```
   [modbus_bridge:xxx] Component loaded
   ```
5. Review bridge configuration

#### Problem: RTU Timeouts

**Symptoms:**
- Logs show "Modbus RTU timeout"
- No BMS data

**Solutions:**
1. Verify BMS UART connection
2. Check baud rate matches BMS
3. Test BMS separately (without bridge)
4. Check UART pin configuration
5. Verify BMS is powered and responding

#### Problem: Cannot Connect to Port 502

**Symptoms:**
- `nc -zv <ip> 502` fails
- Client cannot reach server

**Solutions:**
1. Check IP address is correct
2. Verify network connectivity
3. Check firewall:
   ```bash
   # On server, check if port is listening
   netstat -an | grep 502
   ```
4. Verify bridge component loaded
5. Review ESPHome logs for errors

### Client Node Issues

#### Problem: No BMS Data

**Symptoms:**
- All BMS sensors show 0 or unavailable
- "BMS X Online Status" = false

**Solutions:**
1. **Check hardware bridge:**
   - Verify bridge has power
   - Check bridge network connection
   - Review bridge logs/status
   - Verify bridge configuration

2. **Check ESP32 to bridge connection:**
   - Verify RS485 wiring (A↔A, B↔B)
   - Check UART baud rate (19200)
   - Review ESP32 logs for Modbus errors

3. **Check network path:**
   - Bridge can ping servers:
     ```bash
     ping 192.168.1.101
     ping 192.168.1.102
     ```
   - Bridge can connect to port 502:
     ```bash
     nc -zv 192.168.1.101 502
     ```

4. **Check Modbus addressing:**
   - Verify bridge maps addresses correctly:
     - Modbus Addr 1 → 192.168.1.101:502
     - Modbus Addr 2 → 192.168.1.102:502
   - Verify ESP32 uses correct bms_id values

#### Problem: Partial Data

**Symptoms:**
- Some BMS nodes work, others don't
- Intermittent data

**Solutions:**
1. Check each server individually
2. Verify network connectivity to each server
3. Check bridge mapping for each address
4. Monitor for timeout errors in logs
5. Increase `modbus_update_interval`

#### Problem: Slow Updates

**Symptoms:**
- Data updates slowly
- Long delays between polls

**Solutions:**
1. Check network latency:
   ```bash
   ping -c 10 192.168.1.101
   # Look for average latency
   ```
2. Use Ethernet instead of WiFi
3. Increase `modbus_update_interval` to reduce load
4. Check for network congestion
5. Verify bridge performance

### Network Issues

#### Problem: WiFi Disconnections

**Symptoms:**
- Intermittent connectivity
- "WiFi Signal" sensor low

**Solutions:**
1. Check WiFi signal strength (>-70 dBm)
2. Move closer to AP or add repeater
3. Use 2.4GHz band (better range)
4. Switch to Ethernet if possible
5. Check for interference
6. Add WiFi failover:
   ```yaml
   wifi:
     networks:
       - ssid: "Primary"
       - ssid: "Backup"
   ```

#### Problem: IP Conflicts

**Symptoms:**
- Cannot connect to nodes
- Intermittent connectivity

**Solutions:**
1. Verify unique IPs for all nodes
2. Check DHCP range vs static IPs
3. Use `arp -a` to find conflicts
4. Set static IPs outside DHCP range

### General Debugging

#### Enable Verbose Logging

```yaml
logger:
  level: DEBUG
  logs:
    modbus_controller: DEBUG
    modbus: DEBUG
    modbus_bridge: DEBUG
    wifi: INFO
```

#### Monitor in Real-Time

```bash
esphome logs my_config.yaml
```

#### Test Modbus Directly

**Server Test:**
```bash
# Read register 1 (online_status) from server
mbpoll -a 1 -r 1 -c 1 192.168.1.101

# Read registers 1-10 from server
mbpoll -a 1 -r 1 -c 10 192.168.1.101
```

**Client Test:**
```bash
# Act as Modbus TCP client to test server
modpoll -m tcp -a 1 -r 1 -c 10 192.168.1.101
```

---

## Performance Tuning

### Latency Expectations

| Connection | Typical Latency | Range |
|------------|----------------|-------|
| RS485 | <1ms | Consistent |
| Ethernet | 2-10ms | 1-20ms |
| WiFi | 5-50ms | 2-200ms |

### Optimize Update Interval

**Default:** 5 seconds

```yaml
packages:
  modbus_itf: !include
    file: packages/board/board_options_itf_modbus.yaml
    vars:
      modbus_update_interval: '5s'  # Balance speed vs load
```

**Recommendations:**
- **Critical systems:** 3s (Ethernet only)
- **Normal operation:** 5s (default)
- **Many nodes (>5):** 10s
- **WiFi reliability issues:** 10-15s

### Network Optimization

#### WiFi

1. **Use 2.4GHz for range, 5GHz for speed:**
   ```yaml
   wifi:
     power_save_mode: none  # Disable power saving
   ```

2. **Dedicated AP for BMS network**
   - Reduces interference
   - Better QoS control

3. **WiFi 6 (802.11ax) if available**
   - Better handling of multiple devices

#### Ethernet

1. **100Mbps is sufficient** (Modbus TCP is low bandwidth)
2. **Full duplex mode**
3. **Unmanaged switch OK** for small setups
4. **Managed switch** for QoS in large installations

### Bridge Performance

#### Hardware Bridge

- **Processing delay:** ~1-5ms typical
- **Concurrent connections:** Check bridge specs
- **Throughput:** Usually not a bottleneck

**Tips:**
- Update bridge firmware
- Use bridge diagnostics
- Monitor bridge CPU/memory

#### ESP32 as Bridge

- **WiFi + RS485:** ~10-20ms additional latency
- **Ethernet + RS485:** ~5-10ms additional latency

### Scaling Considerations

| Nodes | Update Interval | Network | Notes |
|-------|----------------|---------|-------|
| 2-3 | 5s | WiFi OK | Standard setup |
| 4-6 | 5-10s | WiFi/Ethernet | Monitor WiFi signal |
| 7-10 | 10s | Ethernet preferred | Consider QoS |
| 10+ | 10-15s | Ethernet required | May need multiple clients |

---

## Security Considerations

### Modbus TCP Security

**Important:** Modbus TCP has **NO built-in security**:
- No encryption
- No authentication
- Plain text communication
- Anyone on network can read/write registers

### Recommended Security Measures

#### 1. Network Isolation

**VLAN Separation:**
```
Internet ─┬─ VLAN 10: Main Network
          └─ VLAN 20: BMS Network (isolated)
                └─ Access only from Home Assistant
```

#### 2. Firewall Rules

**Only allow required traffic:**
```bash
# Allow only from master node
iptables -A INPUT -p tcp --dport 502 -s 192.168.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 502 -j DROP
```

#### 3. VPN for Remote Access

**Never expose port 502 to Internet**

Use VPN (WireGuard, OpenVPN):
```
Remote User → VPN → Local Network → BMS Network
```

#### 4. Physical Security

- Secure WiFi credentials
- Change default passwords
- Physical access control to network equipment

#### 5. Monitoring

**Log suspicious activity:**
```yaml
logger:
  logs:
    modbus_bridge: INFO  # Log all connections
```

**Monitor for:**
- Unexpected connections
- Failed authentication attempts (if using bridge with auth)
- Unusual traffic patterns

### Best Practices

1. **Use Ethernet over WiFi** when possible (harder to intercept)
2. **Segment networks** (BMS, IoT, Main separate)
3. **Regular firmware updates** on all devices
4. **Strong WiFi passwords** (WPA3 if available)
5. **Disable unused services** (web_server, etc.)
6. **Monitor logs** for anomalies

---

## FAQ

### General Questions

**Q: Should I use TCP/IP or stick with RS485?**

A:
- Use TCP/IP if: Nodes are far apart, distributed installation, using existing network
- Use RS485 if: All nodes nearby, maximum reliability needed, no network infrastructure

**Q: Will this work with existing YamBMS RS485 setups?**

A: Yes! You can mix RS485 and TCP nodes. Some nodes can use RS485 while others use TCP.

**Q: Do I need to modify my BMS packages?**

A: No. The existing BMS packages work unchanged. The TCP bridge is transparent.

### Technical Questions

**Q: Why doesn't ESPHome support Modbus TCP client natively?**

A: It's a feature request ([#708](https://github.com/esphome/feature-requests/issues/708)). The community is working on it.

**Q: Can I use the TCP bridge on the client side too?**

A: Currently, the bridge is designed for server side. Client side requires hardware bridge or future ESPHome support.

**Q: What's the maximum number of nodes?**

A: Theoretical: 255 Modbus addresses. Practical: Limited by network and update timing. 10-20 nodes is reasonable.

**Q: Does this work with Home Assistant?**

A: Yes! All nodes connect to Home Assistant via ESPHome API as normal. The TCP communication is only between YamBMS nodes.

**Q: Can I use this over the Internet?**

A: Technically yes, but **NOT RECOMMENDED** due to security. Use VPN if you need remote access.

### Hardware Questions

**Q: Which Ethernet board should I use?**

A: Recommendations:
- **ESP32-C3-ETH01-EVO:** Good balance of price/features
- **ESP32-WT32-ETH01:** Widely available
- **ESP32-S3-WS-ETH:** Latest platform

**Q: Which hardware bridge should I buy?**

A: For beginners: **EBYTE NT1** (easiest to configure)
For advanced: **Elfin-EE11** (industrial quality)
For budget: **USR-TCP232-410S** (good value)

**Q: Can I use WiFi for critical installations?**

A: Not recommended. WiFi can have disconnections. Use Ethernet for:
- Critical battery systems
- Off-grid installations
- Systems requiring high reliability

**Q: Do I need a managed switch?**

A: No, for small installations (2-5 nodes) an unmanaged switch is fine. Use managed switch for:
- Large installations (>5 nodes)
- QoS requirements
- VLAN isolation

### Configuration Questions

**Q: How do I assign IP addresses?**

A: Two options:
1. **Static IPs** (recommended): Configure in `wifi: manual_ip:`
2. **DHCP reservations**: Configure in router based on MAC address

**Q: What if my server IP changes?**

A: If using DHCP without reservations:
- Server IP change is transparent (bridge auto-connects)
- Update bridge configuration with new IP
- Use mDNS: `<hostname>.local` instead of IP

**Q: Can I use different update intervals for different nodes?**

A: Yes! Each BMS client can have its own update_interval:
```yaml
bms1: !include
  vars:
    modbus_update_interval: '5s'
bms2: !include
  vars:
    modbus_update_interval: '10s'
```

### Troubleshooting Questions

**Q: Why do I see RTU timeouts?**

A: Common causes:
1. BMS not connected properly
2. Wrong baud rate
3. Wrong UART pins
4. BMS not powered
5. BMS protocol mismatch

**Q: Why is my WiFi signal weak?**

A: Solutions:
- Move node closer to AP
- Add WiFi repeater/mesh
- Use external antenna ESP32 board
- Switch to Ethernet

**Q: Why does the client show all sensors as 0?**

A: Check in order:
1. Are servers online? (check server logs)
2. Is hardware bridge configured? (check bridge status)
3. Is network working? (ping servers from bridge)
4. Are Modbus addresses correct? (check bridge mapping)

### Future Development

**Q: When will ESPHome have native Modbus TCP client?**

A: Unknown. Track: https://github.com/esphome/feature-requests/issues/708

**Q: Will YamBMS support other protocols (MQTT, HTTP)?**

A: Modbus is the current standard. Other protocols could be added by community.

**Q: Can I contribute improvements?**

A: Yes! Submit pull requests to the YamBMS repository.

---

## Additional Resources

### Documentation
- [YamBMS Multi-Node RS485 Guide](./YamBMS_multi-node_RS485_modbus_solution.md)
- [ESPHome Modbus Component](https://esphome.io/components/modbus.html)
- [ESPHome Modbus Controller](https://esphome.io/components/modbus_controller/)

### External Components
- [esphome_modbus_bridge](https://github.com/rosenrot00/esphome_modbus_bridge)
- [ESPHome Feature Request #708](https://github.com/esphome/feature-requests/issues/708)

### Tools
- **mbpoll:** Modbus TCP testing tool
- **modpoll:** Commercial Modbus tool
- **Wireshark:** Network packet analysis
- **QModBus:** GUI Modbus tool

### Hardware
- [EBYTE NT1](https://www.ebyte.com/) - Modbus gateway
- [USR-TCP232-410S](https://www.pusr.com/) - Serial to Ethernet
- [Elfin-EE11](https://www.hi-flying.com/) - Industrial gateway

---

## Support

### Community
- **GitHub Issues:** https://github.com/Sleeper85/esphome-yambms/issues
- **Discussions:** https://github.com/Sleeper85/esphome-yambms/discussions

### Contributing
Pull requests welcome! Areas needing help:
- Native Modbus TCP client component
- Additional hardware bridge configurations
- Performance testing results
- Documentation improvements

---

## Changelog

### Version 1.0.0 (2025-12-23)
- Initial TCP/IP multi-node documentation
- Created server/client configurations
- Added example files
- Comprehensive troubleshooting guide

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-23
**License:** GNU GPL v3.0
