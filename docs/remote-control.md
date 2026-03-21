# Remote Computer Control Guide

## Overview

Weather Shield now includes comprehensive support for remote computer control and monitoring. This guide explains how to use the Docker-compatible control information and Wake on LAN (WoL) features.

## System Control Information

The dashboard now displays all information needed to control your computer remotely via Docker:

### Available Information

- **Hostname**: The system's hostname (computer name)
- **FQDN**: Fully Qualified Domain Name for DNS resolution
- **IP Address**: The computer's local network IP address
- **MAC Address**: Used for Wake on LAN and remote identification
- **Architecture**: System architecture (x86_64, arm64, etc.)
- **Docker Host**: SSH connection string for remote Docker management

### Accessing Control Information

1. Open the Weather Shield dashboard
2. Scroll down to the **System Control Information** card
3. All values are clickable and can be copied to clipboard
4. The Docker Host string is formatted for direct use with Docker CLI

## Wake on LAN (WoL) Status

Wake on LAN allows you to remotely power on your computer from another machine.

### What the Dashboard Shows

The dashboard displays:
- **WoL Status**: Whether WoL is currently enabled or disabled
- **Device**: The network interface where WoL is configured (e.g., eth0, enp0s31f6)
- **Supported**: Whether your network interface supports WoL
- **Helpful Information**: Instructions for enabling WoL if it's not already enabled

### Enabling Wake on LAN

If WoL is supported but disabled, you'll see instructions on the dashboard.

#### On Linux (via ethtool):

```bash
# First, identify your network interface
ip link show

# Enable WoL on the interface (replace eth0 with your interface)
sudo ethtool -s eth0 wol g

# Make it permanent (add to /etc/network/interfaces or netplan)
# For netplan (Ubuntu 18.04+):
sudo nano /etc/netplan/00-installer-config.yaml
```

Add to your netplan config:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
      wakeonlan: true
```

Then apply:
```bash
sudo netplan apply
```

### Prerequisites

- **ethtool**: Required to detect WoL status
  - Ubuntu/Debian: `sudo apt-get install ethtool`
  - Fedora/CentOS: `sudo dnf install ethtool`

- **Hardware Support**: Your network card must support WoL

- **BIOS**: WoL must be enabled in BIOS/UEFI settings

## Remote Docker Control

Weather Shield is designed to work with remote Docker daemons for computer control.

### Docker Connection String

The dashboard provides a ready-to-use Docker connection string in this format:
```
ssh://root@<IP_ADDRESS>
```

### Using with Docker Commands

```bash
# Set the Docker host
export DOCKER_HOST=ssh://root@192.168.1.100

# List containers on remote machine
docker ps

# Run a command on the remote machine
docker exec <container-id> <command>

# Use with docker-compose
docker-compose -H ssh://root@192.168.1.100 up
```

### Using with Docker in Docker Compose

```yaml
version: '3'

services:
  controller:
    build: .
    environment:
      DOCKER_HOST: ssh://root@192.168.1.100
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

## Setting Up Remote Control

### Prerequisites

1. **SSH Access**: Ensure SSH is configured and accessible
2. **Docker Daemon**: Docker must be running on the remote machine
3. **SSH Key Authentication**: Set up key-based authentication for automation

### Step 1: Add SSH Keys

On the control machine:
```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096 -f ~/.ssh/weather_shield

# Add the public key to the remote machine
ssh-copy-id -i ~/.ssh/weather_shield root@<IP_ADDRESS>
```

### Step 2: Configure Docker Socket Access

On the remote machine, ensure Docker socket permissions allow SSH access:
```bash
# Check Docker socket permissions
ls -la /var/run/docker.sock

# The socket should be accessible by root (which SSH connects as)
```

### Step 3: Test Connection

```bash
# Test SSH connection
ssh root@<IP_ADDRESS> "echo 'Connected successfully'"

# Test Docker access
export DOCKER_HOST=ssh://root@<IP_ADDRESS>
docker info
```

## API Endpoints

The Weather Shield API provides several endpoints for accessing control information:

### `/api/system-info`

Returns system information needed for Docker control.

**Response:**
```json
{
  "hostname": "gaming-pc",
  "fqdn": "gaming-pc.local",
  "ip_address": "192.168.1.100",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "architecture": "x86_64",
  "docker_host": "ssh://root@192.168.1.100"
}
```

### `/api/wol-status`

Returns the Wake on LAN status.

**Response (WoL Enabled):**
```json
{
  "enabled": true,
  "status": "g",
  "device": "eth0",
  "supported": true
}
```

**Response (WoL Disabled):**
```json
{
  "enabled": false,
  "status": "off",
  "device": "eth0",
  "supported": true
}
```

**Response (WoL Not Detected):**
```json
{
  "enabled": false,
  "status": "unknown",
  "supported": false,
  "message": "ethtool not found. Install it with: sudo apt install ethtool"
}
```

### `/api/control-info`

Returns combined control information including system info, WoL status, and Docker availability.

**Response:**
```json
{
  "system": { ... },
  "wol": { ... },
  "docker_available": true,
  "service": {
    "name": "weather-shield",
    "port": 5000,
    "protocol": "http"
  }
}
```

## Troubleshooting

### WoL Not Detected

1. **Install ethtool**: `sudo apt install ethtool`
2. **Check network interface**: Run `ip link show` to see available interfaces
3. **Check BIOS**: Ensure WoL is enabled in BIOS settings
4. **Update drivers**: Ensure network drivers are up-to-date

### Docker Connection Fails

1. **Test SSH**: `ssh root@<IP> echo "test"`
2. **Check Docker daemon**: `sudo systemctl status docker`
3. **Verify socket**: `sudo ls -la /var/run/docker.sock`
4. **Check firewall**: Ensure SSH port (22) is accessible

### Cannot Copy Values

- Ensure your browser supports clipboard API
- Check if running in a secure context (HTTPS or localhost)
- Manually select and copy text from the fields

## Security Considerations

- **SSH Keys**: Use strong SSH key passphrases
- **Network**: Keep devices on trusted networks
- **Docker Access**: Restrict Docker daemon access to authorized users
- **Firewall**: Limit SSH access to known IP addresses
- **Credentials**: Never share connection strings containing sensitive information

## Integration Examples

### Automated Wake on LAN

```bash
#!/bin/bash
# wake-computer.sh

IP_ADDRESS=$1
MAC_ADDRESS=$2

# Get the broadcast address
BROADCAST=$(ipcalc -b $IP_ADDRESS/24 | grep Broadcast | awk '{print $2}')

# Send WoL packet
wakeonlan -i $BROADCAST $MAC_ADDRESS

echo "Wake on LAN packet sent to $MAC_ADDRESS via $BROADCAST"
```

### Integration with cron

```bash
# Wake computer at 7 AM every weekday
0 7 * * 1-5 /path/to/wake-computer.sh 192.168.1.100 00:1A:2B:3C:4D:5E
```

## See Also

- [Installation Guide](./INSTALL.md)
- [Configuration Guide](./configuration.md)
- [Docker Deployment](./DOCKER.md)
