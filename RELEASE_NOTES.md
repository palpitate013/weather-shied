# Weather Shield v2.0 - Release Notes

## Summary of Changes

This release adds comprehensive system control information and Wake on LAN (WoL) detection to Weather Shield, along with automated GitHub Actions for building and releasing deb/rpm packages.

## New Features

### 1. System Control Information Dashboard

The web dashboard now displays all information needed to remotely control your computer:

- **System Information**
  - Hostname (computer name)
  - FQDN (Fully Qualified Domain Name)
  - IP Address
  - MAC Address
  - System Architecture

- **Remote Control Details**
  - Docker Host connection string (SSH format)
  - Docker availability status

- **Wake on LAN (WoL) Status**
  - WoL enabled/disabled status
  - Network interface name
  - WoL support information
  - Helpful instructions if WoL is disabled

### 2. Clickable and Copyable Values

All system information values are clickable and automatically copy to clipboard for easy integration with remote control tools.

### 3. Enhanced GitHub Actions CI/CD

New GitHub Actions workflows for building and releasing packages:

- **Automated deb Package Build**: Creates Debian/Ubuntu packages
- **Automated RPM Package Build**: Creates Red Hat/Fedora/CentOS packages
- **GitHub Release Creation**: Automatically creates releases with all built packages
- **Multi-format Distribution**: Releases now include deb, rpm, and Python wheel packages

## API Endpoints

### New Endpoints

- **`/api/system-info`**: Get system information for Docker control
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

- **`/api/wol-status`**: Get Wake on LAN status
  ```json
  {
    "enabled": true,
    "status": "g",
    "device": "eth0",
    "supported": true
  }
  ```

- **`/api/control-info`**: Get all control information
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

## Installation

### From GitHub Releases

#### Debian/Ubuntu:
```bash
sudo apt install ./weather-shield_2.0.0_amd64.deb
sudo systemctl start weather-shield
```

#### Red Hat/Fedora/CentOS:
```bash
sudo dnf install weather-shield-2.0.0-1.x86_64.rpm
sudo systemctl start weather-shield
```

#### Docker:
```bash
docker run -d palpitate013/weather-shield:2.0.0
```

#### Python pip:
```bash
pip install weather-shield==2.0.0
```

## Build Scripts

Added build automation scripts:

- **`scripts/build-deb.sh`**: Builds Debian package
- **`scripts/build-rpm.sh`**: Builds RPM package

These scripts are used in the GitHub Actions CI/CD pipeline.

## Documentation

See the new comprehensive guide:
- **`docs/remote-control.md`**: Complete guide for remote computer control setup

## Technical Details

### Code Changes

**app.py**
- Added `socket` and `subprocess` imports
- Added `get_system_info()` method to retrieve system information
- Added `get_wake_on_lan_status()` method to detect WoL status
- Added `_get_mac_address()` helper method
- Added `_get_architecture()` helper method
- Added three new API endpoints

**templates/index.html**
- Added new "System Control Information" card
- Displays system info, Docker settings, and WoL status

**static/script.js**
- Added `updateSystemInfo()` method
- Added `renderSystemInfo()` method
- Added clipboard copy functionality for system information

**static/style.css**
- Added `.system-card` styles
- Added `.system-content` and `.system-section` styles
- Added `.wol-info` notification styles

**.github/workflows/ci-cd.yml**
- Added `build-packages` job for building deb/rpm
- Updated `release` job to upload built packages
- Improved release notes template

**scripts/build-deb.sh** (new)
- Creates Debian packages with systemd service integration
- Installs to `/usr/share/weather-shield/`
- Creates systemd service file at `/etc/systemd/system/`

**scripts/build-rpm.sh** (new)
- Creates RPM packages
- Includes proper systemd integration
- Uses standard FHS directory structure

## System Requirements

- Python 3.8 or higher
- Linux operating system
- ethtool (for WoL detection): `sudo apt install ethtool`
- Flask and dependencies (automatically installed)

## Known Limitations

- WoL detection requires `ethtool` utility
- Docker availability is detected by checking for socket files
- System information is read-only (no write access)

## Breaking Changes

None. This release is fully backward compatible.

## Security Notes

- System information is available via HTTP API (use HTTPS in production)
- Docker connection strings include IP addresses
- Consider restricting dashboard access to trusted networks
- SSH key authentication recommended for Docker remote control

## Bug Fixes

- Fixed bare except clauses in app.py (linting compliance)
- Removed unused loop variables (linting compliance)

## Files Modified

```
.github/workflows/ci-cd.yml         - Updated CI/CD pipeline
.github/release-template.md         - Added release template (new)
app.py                              - Added system control features
templates/index.html                - Added system info card
static/script.js                    - Added system info rendering
static/style.css                    - Added card styling
scripts/build-deb.sh               - Debian package builder (new)
scripts/build-rpm.sh               - RPM package builder (new)
docs/remote-control.md             - Remote control guide (new)
TODO                               - Updated tasks
```

## Next Steps

1. Set up SSH key authentication for remote Docker control
2. Enable Wake on LAN in BIOS/UEFI and configure with ethtool
3. Test remote Docker connections using the provided connection strings
4. Deploy to target computers using the new deb/rpm packages

## Support

For issues or questions, refer to:
- `docs/remote-control.md` - Remote control setup guide
- `docs/configuration.md` - Configuration reference
- `INSTALL.md` - Installation guide
- GitHub Issues - Bug reports and feature requests
