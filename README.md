# Weather Shield - Weather-Based Computer Control System

A Python application that monitors weather conditions using the OpenWeather API and automatically shuts down or boots up your computer based on weather forecasts.

## Features

- **Real-time Weather Monitoring**: Checks current weather conditions and forecasts
- **Intelligent Weather Detection**: Recognizes bad weather (thunderstorms, heavy rain, snow, fog, etc.)
- **Automatic Shutdown**: Triggers shutdown when bad weather is detected or forecasted within 30 minutes
- **Automatic Boot**: Signals when conditions improve (requires Wake-on-LAN for remote boot)
- **Configurable**: Easy-to-customize JSON configuration file
- **Logging**: Detailed logs for monitoring and debugging

## Bad Weather Conditions Detected

The system considers the following as "bad weather":

- **Thunderstorms**: Including lightning and severe thunder
- **Heavy Precipitation**: Heavy rain, extreme rain, freezing rain, sleet, hail
- **Snow**: Heavy snow, blizzard conditions
- **Atmospheric Hazards**: Fog, mist, dust, smoke, ash, haze
- **Severe Weather**: Tornadoes, squalls, hurricanes

## Requirements

- Python 3.7+
- OpenWeather API key (free tier available at [OpenWeather](https://openweathermap.org/api))
- Internet connection
- Administrator/sudo privileges (for shutdown commands)

## Installation

### 1. Clone or set up the project

```bash
cd weather-shied
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get an API Key

1. Visit [OpenWeather API](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key from your account dashboard
4. Copy your API key

### 4. Configure the application

Edit `config.json` and update the following:

```jsonc
{
  "api_key": "YOUR_ACTUAL_API_KEY",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30
}
```

**Configuration Parameters:**

- `api_key`: Your OpenWeather API key
- `latitude`: Latitude of the location to monitor
- `longitude`: Longitude of the location to monitor
- `units`: Temperature units - `metric` (Celsius), `imperial` (Fahrenheit), or `standard` (Kelvin)
- `check_interval`: How often to check weather (in seconds, default: 300 = 5 minutes)
- `forecast_minutes`: How far ahead to forecast for bad weather (default: 30 minutes)

### 5. Run the application

```bash
python weather_monitor.py
```

Or specify a custom config file:

```bash
python weather_monitor.py /path/to/config.json
```

## Usage

### Running as a Background Service (Linux)

Create a systemd service file at `/etc/systemd/system/weather-shield.service`:

```ini
[Unit]
Description=Weather Shield - Weather-Based Computer Control
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/weather-shied
ExecStart=/usr/bin/python3 /path/to/weather-shied/weather_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl enable weather-shield
sudo systemctl start weather-shield
```

Check status:

```bash
sudo systemctl status weather-shield
```

View logs:

```bash
sudo journalctl -u weather-shield -f
```

### Running as a Background Service (Windows)

Use a task scheduler or create a batch file to run the script at startup:

```batch
@echo off
python C:\path\to\weather-shied\weather_monitor.py
```

### Setting Up Wake-on-LAN (Optional)

For automatic boot when weather improves:

**Windows:**

- Enable Wake-on-LAN in network adapter settings
- Enable Wake-on-LAN in BIOS/UEFI

**Linux:**

- Install ethtool: `sudo apt-get install ethtool`
- Enable WoL: `sudo ethtool -s eth0 wol g` (replace eth0 with your interface)

**macOS:**

- Enable "Wake for network access" in System Preferences > Energy Saver

## How It Works

1. **Weather Check**: The application checks weather every `check_interval` seconds
2. **Current Conditions**: Analyzes current weather at your location
3. **Forecast Analysis**: Checks forecast for bad weather within the next `forecast_minutes`
4. **Action Triggers**:
   - **Shutdown**: Triggered if current weather is bad OR bad weather is forecasted
   - **Boot Signal**: Triggered when current weather is good AND no bad weather is forecasted
5. **State Management**: Tracks computer state to avoid duplicate commands

## Logging

Logs are written to `weather_monitor.log` in the working directory and also displayed in the console.

Example log output:

```text
2026-03-21 14:30:45,123 - INFO - Weather Shield started
2026-03-21 14:30:45,124 - INFO - Location: 40.7128, -74.0060
2026-03-21 14:30:50,456 - INFO - Current weather: Clear (clear sky) - Code: 800 - Bad: False
2026-03-21 14:30:55,789 - WARNING - Bad weather detected! Initiating shutdown...
2026-03-21 14:31:00,012 - INFO - Linux shutdown command sent
```

## Troubleshooting

### API Key Not Working

- Verify your API key is correct in `config.json`
- Check that your API key is activated (check OpenWeather account)
- Ensure you have an internet connection

### Shutdown Not Working

- On Linux: Ensure the script runs with `sudo` privileges
- On Windows: Run as Administrator
- Check logs for error messages

### Forecast Not Working

- Verify latitude and longitude are correct
- Check that your API key supports the Forecast API (free tier includes this)

## License

This project is provided as-is for personal use.

## Support

For issues or questions about the OpenWeather API, visit: [OpenWeather Documentation](https://openweathermap.org/api)
