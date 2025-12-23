# YamBMS TCP Multi-Node Examples

## Quick Start

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

## Documentation

Full documentation: `../../documents/README/YamBMS_multi-node_TCP_modbus_solution.md`
