# Weather Shield Release

## Changes
See [CHANGELOG](https://github.com/palpitate013/weather-shield/blob/main/CHANGELOG.md) for details.

## Installation Methods

### Docker
```bash
docker pull palpitate013/weather-shield:latest
```

### pip
```bash
pip install weather-shield
```

### Debian/Ubuntu
```bash
sudo apt install ./weather-shield_*_amd64.deb
```

### Red Hat/Fedora/CentOS
```bash
sudo dnf install weather-shield-*.x86_64.rpm
```

### NixOS
Add to your configuration.nix:
```nix
environment.systemPackages = with pkgs; [ weather-shield ];
```

## What's New
This release includes:
- Deb package for Debian/Ubuntu systems
- RPM package for Red Hat/Fedora/CentOS systems
- Enhanced web dashboard with system control information
- Wake on LAN (WoL) status detection
- Docker integration information for remote computer control

## System Requirements
- Python 3.8 or higher
- Linux operating system
- OpenWeather API key (for weather monitoring)

See [Installation Guide](https://github.com/palpitate013/weather-shield/blob/main/INSTALL.md) for detailed instructions.
