# Installation Guide

## System Requirements

- Python 3.8 or higher
- Linux, macOS, or Windows (with WSL2 recommended)
- sudo access for shutdown commands
- Internet connection for weather API

## Installation Methods

### Method 1: pip (Recommended for most users)

```bash
# Clone the repository
git clone https://github.com/palpitate013/weather-shield.git
cd weather-shield

# Install with pip
sudo pip install -e .

# Or install as user-local
pip install --user -e .
```

### Method 2: Debian/Ubuntu (.deb package)

```bash
# Build the .deb package
./debian/build.sh

# Install the package
sudo dpkg -i weather-shield_1.0.0-1_all.deb
sudo apt-get install -f  # Install dependencies if needed

# Verify installation
weather-shield --version

# Start the service
sudo systemctl start weather-shield
sudo systemctl enable weather-shield
```

### Method 3: Docker (Recommended for containerized deployment)

```bash
# Using docker-compose
docker-compose up -d

# Or manual Docker build
docker build -t weather-shield:latest .
docker run -d -p 5000:5000 -v $(pwd)/config.json:/app/config.json weather-shield:latest
```

### Method 4: Manual Installation

```bash
# Install dependencies
sudo apt-get install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run the application
python3 weather_shield.py
```

## Configuration

1. Edit `config.json`:

```bash
nano config.json
```

2. Set your OpenWeather API key:
   - Get a free API key at https://openweathermap.org/api
   - Add it to `config.json`

3. Set your location:
   ```json
   {
     "latitude": 40.7128,
     "longitude": -74.0060,
     "api_key": "YOUR_API_KEY"
   }
   ```

4. (Optional) Enable ntfy notifications:
   ```json
   {
     "ntfy_topic": "your_custom_topic"
   }
   ```

## Post-Installation

### Enable as System Service (Linux)

```bash
# Copy service file
sudo cp debian/weather-shield.service /etc/systemd/system/

# Create user
sudo useradd -r -s /bin/false weather-shield

# Copy application files
sudo mkdir -p /opt/weather-shield
sudo cp -r weather_shield.py config.json templates static /opt/weather-shield/
sudo chown -R weather-shield:weather-shield /opt/weather-shield

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable weather-shield
sudo systemctl start weather-shield

# Check status
sudo systemctl status weather-shield
```

### Configure Wake-on-LAN

For boot functionality to work, you'll need to set up Wake-on-LAN on your target computers:

**Linux:**
```bash
sudo apt-get install ethtool
sudo ethtool -s eth0 wol g
```

**macOS:**
System Preferences → Energy Saver → Allow your Mac to wake for network access

**Windows:**
Device Manager → Network Adapters → Properties → Power Management → Wake on Magic Packet

### Verify Installation

```bash
# Check if service is running
sudo systemctl status weather-shield

# View logs
sudo journalctl -u weather-shield -f

# Test the API
curl http://localhost:5000/api/weather

# Open dashboard
# Visit: http://localhost:5000
```

## Uninstallation

### If installed with pip:
```bash
sudo pip uninstall weather-shield
```

### If installed with .deb:
```bash
sudo apt-get remove weather-shield
sudo apt-get autoremove
```

### If installed manually:
```bash
# Stop the service
sudo systemctl stop weather-shield
sudo systemctl disable weather-shield

# Remove files
sudo rm -rf /opt/weather-shield
sudo rm /etc/systemd/system/weather-shield.service
```

## Troubleshooting

### Port 5000 is already in use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Change port in config.json or start with different port
python3 weather_shield.py --port 8000
```

### Permission denied on shutdown

```bash
# Add weather-shield user to sudoers
sudo visudo

# Add this line:
weather-shield ALL=(ALL) NOPASSWD: /sbin/shutdown
```

### Wake-on-LAN not working

1. Ensure Wake-on-LAN is enabled in BIOS
2. Verify etherwake is installed: `sudo apt-get install etherwake`
3. Check MAC addresses in dashboard

### Weather API errors

- Verify API key is correct in config.json
- Check internet connection
- Ensure latitude/longitude are valid

## Getting Help

- Check logs: `sudo journalctl -u weather-shield -n 50`
- See application logs: `tail -f weather_shield.log`
- Open an issue: https://github.com/palpitate013/weather-shield/issues
