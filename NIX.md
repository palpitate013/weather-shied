# NixOS Installation

## Quick Start with Flake

If you have flakes enabled in your NixOS:

```bash
# Add to your flake.nix inputs
inputs.weather-shield.url = "github:palpitate013/weather-shield";

# Or run directly without adding to flake:
nix run github:palpitate013/weather-shield
```

## Installation Methods

### Method 1: Using flake.nix (Recommended)

```bash
# Run directly
nix run github:palpitate013/weather-shield

# Or build and install
nix build github:palpitate013/weather-shield
```

### Method 2: Using NixOS Module

Add to your `configuration.nix`:

```nix
{ config, pkgs, ... }:

{
  imports = [
    # ... other imports
    (builtins.fetchGit "https://github.com/palpitate013/weather-shield").outPath + "/nixos/module.nix"
  ];

  services.weather-shield = {
    enable = true;
    openFirewall = true;
    config = {
      api_key = "your-openweather-api-key";
      latitude = 40.7128;
      longitude = -74.0060;
      units = "metric";
      check_interval = 300;
      forecast_minutes = 30;
      ntfy_topic = null;
      computers = [
        {
          id = "computer-1";
          name = "Main Computer";
          enabled = true;
        }
      ];
    };
  };
}
```

Then rebuild and switch:

```bash
sudo nixos-rebuild switch
```

### Method 3: Using devShell

```bash
# Enter development environment
nix flake github:palpitate013/weather-shield

# Run the application
python weather_shield.py
```

### Method 4: Build from source

```bash
# Clone repository
git clone https://github.com/palpitate013/weather-shield.git
cd weather-shield

# Build with nix
nix build

# Run
./result/bin/weather-shield
```

## Configuration

### Option 1: Edit config in NixOS module

```nix
services.weather-shield.config = {
  api_key = "YOUR_API_KEY";
  latitude = 40.7128;
  longitude = -74.0060;
};
```

### Option 2: Using environment file

Create `/etc/weather-shield/config.json`:

```json
{
  "api_key": "your-api-key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30,
  "ntfy_topic": null,
  "computers": [
    {
      "id": "computer-1",
      "name": "Main Computer",
      "enabled": true
    }
  ]
}
```

## Managing the Service

```bash
# Check service status
sudo systemctl status weather-shield

# View logs
sudo journalctl -u weather-shield -f

# Restart service
sudo systemctl restart weather-shield

# Manually stop/start
sudo systemctl stop weather-shield
sudo systemctl start weather-shield
```

## Firewall Configuration

### Opening port 5000

```nix
services.weather-shield.openFirewall = true;

# Or manually:
networking.firewall.allowedTCPPorts = [ 5000 ];
```

### Custom port

```nix
services.weather-shield.port = 8080;
```

## Accessing Dashboard

Once running, access the dashboard at:

```
http://localhost:5000
```

## Advanced Configuration

### With Wake-on-LAN support

```nix
services.weather-shield = {
  enable = true;
  openFirewall = true;
  config = {
    # ... other config ...
    computers = [
      {
        id = "gaming-pc";
        name = "Gaming PC";
        enabled = true;
        mac_address = "00:11:22:33:44:55";
      }
    ];
  };
};

# Install etherwake for WoL
environment.systemPackages = with pkgs; [ etherwake ];
```

### With ntfy notifications

```nix
services.weather-shield.config = {
  # ... other config ...
  ntfy_topic = "weather-shield-notifications";
};
```

## Troubleshooting

### Service won't start

```bash
# Check error logs
sudo journalctl -u weather-shield -n 50

# Try running manually
sudo -u weather-shield weather-shield
```

### Port already in use

```nix
services.weather-shield.port = 8000;  # Change to different port
```

### Permission issues

```bash
# Check ownership
ls -la /var/lib/weather-shield/

# Fix if needed
sudo chown -R weather-shield:weather-shield /var/lib/weather-shield
```

### API key not working

1. Get a free API key at https://openweathermap.org/api
2. Update config with correct key
3. Restart service: `sudo systemctl restart weather-shield`

## Uninstallation

### If using NixOS module

Remove from `configuration.nix`:

```nix
services.weather-shield.enable = false;  # Or remove the entire services.weather-shield block
```

Then rebuild:

```bash
sudo nixos-rebuild switch
```

### If using flake

Remove from your flake inputs and rebuild.

## Development

### Local development

```bash
cd weather-shield
nix develop

# Now in dev shell
python weather_shield.py
```

### Building custom package

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.callPackage ./nixos/default.nix {}
```

Then build with:

```bash
nix-build -A weather-shield
```

## Contributing

To contribute to NixOS packaging:

1. Fork the repository
2. Create a feature branch
3. Make changes to flake.nix or nixos/* files
4. Test with: `nix flake check`
5. Submit a pull request

## Resources

- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [NixOS Modules](https://nixos.org/manual/nixos/stable/#sec-writing-modules)
- [Weather Shield GitHub](https://github.com/palpitate013/weather-shield)
