# Configuration Guide

Weather Shield is configured via `config.json` in the application directory.

## Configuration File

### Default config.json

```json
{
  "api_key": "your_api_key_here",
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

## Configuration Options

### api_key (Required)

OpenWeather API key for weather data fetching.

- Type: String
- Get free key at: https://openweathermap.org/api
- Required for weather monitoring to work

### latitude (Required)

Latitude of your location for weather monitoring.

- Type: Number (float)
- Example: 40.7128 (New York)
- Range: -90 to 90

### longitude (Required)

Longitude of your location for weather monitoring.

- Type: Number (float)
- Example: -74.0060 (New York)
- Range: -180 to 180

### units (Optional)

Temperature units for weather display.

- Type: String
- Options:
  - `"metric"` - Celsius (default)
  - `"imperial"` - Fahrenheit
  - `"kelvin"` - Kelvin
- Default: `"metric"`

### check_interval (Optional)

How often to check weather in seconds.

- Type: Integer
- Default: 300 (5 minutes)
- Minimum: 60 (1 minute)
- Note: More frequent checks use more API calls

### forecast_minutes (Optional)

How far into the future to check the forecast.

- Type: Integer
- Default: 30 (minutes)
- Options: 15, 30, 45, 60, etc.
- Used to decide whether to shutdown before bad weather arrives

### ntfy_topic (Optional)

Topic for ntfy.sh notifications.

- Type: String or null
- Default: null (disabled)
- Example: `"my-weather-alerts"`
- Leave null to disable notifications
- To use: set to any unique topic name

### computers (Optional)

Array of computers to monitor.

- Type: Array of objects
- Default: One default computer

## Computer Configuration

Each computer in the array has:

```json
{
  "id": "computer-1",
  "name": "Main Computer",
  "enabled": true
}
```

### id

Unique identifier for the computer.

- Type: String
- Auto-generated if not provided
- Format: `computer-N`

### name

Human-readable name for the computer.

- Type: String
- Used in dashboard and notifications
- Example: "Gaming PC", "Office Computer"

### enabled

Whether weather-based control is enabled for this computer.

- Type: Boolean
- Default: true
- If false: computer won't be auto-shutdown/booted by weather

## Setup Examples

### Example 1: Simple Setup (Single Computer)

```json
{
  "api_key": "your_api_key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30,
  "computers": [
    {
      "id": "main",
      "name": "Main Computer",
      "enabled": true
    }
  ]
}
```

### Example 2: Multiple Computers

```json
{
  "api_key": "your_api_key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "imperial",
  "check_interval": 600,
  "forecast_minutes": 60,
  "computers": [
    {
      "id": "pc1",
      "name": "Office Computer",
      "enabled": true
    },
    {
      "id": "pc2",
      "name": "Gaming PC",
      "enabled": true
    },
    {
      "id": "server",
      "name": "Home Server",
      "enabled": false
    }
  ]
}
```

### Example 3: With Notifications

```json
{
  "api_key": "your_api_key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30,
  "ntfy_topic": "weather-shield-alerts",
  "computers": [
    {
      "id": "pc1",
      "name": "Main Computer",
      "enabled": true
    }
  ]
}
```

## Getting an API Key

1. Visit https://openweathermap.org/api
2. Click "Sign Up" and create an account
3. Go to API keys section
4. Copy your API key
5. Add to config.json: `"api_key": "your_copied_key"`

Note: Free tier allows 1000 calls/day (sufficient for check_interval ≥ 86 seconds)

## Finding Coordinates

### Using Google Maps

1. Open https://maps.google.com
2. Right-click on location
3. Click coordinates to copy
4. Paste into config.json

### Using OpenWeather API

```bash
curl "https://api.openweathermap.org/geo/1.0/direct?q=New York&limit=1&appid=YOUR_API_KEY"
```

### Common Coordinates

- New York: 40.7128, -74.0060
- London: 51.5074, -0.1278
- Tokyo: 35.6762, 139.6503
- Sydney: -33.8688, 151.2093
- Toronto: 43.6532, -79.3832

## Hot Reload

Configuration changes are loaded:

1. **Web Dashboard Settings**: Takes effect immediately
2. **Manual config.json edits**: Requires application restart

To restart:

```bash
# If running with systemd
sudo systemctl restart weather-shield

# If running with Docker
docker-compose restart weather-shield
```

## Validation

Config is validated on startup. If invalid:

1. Error message appears in logs
2. Application exits with error
3. Check config.json syntax (valid JSON)
4. Verify required fields are set

## Environment Variables

Override config via environment variables:

```bash
export WEATHER_SHIELD_API_KEY="your_api_key"
export WEATHER_SHIELD_LATITUDE="40.7128"
export WEATHER_SHIELD_LONGITUDE="-74.0060"
```

## Advanced Options

### Optimize API Calls

- Set `check_interval` to 600+ (reduce checks)
- Set `forecast_minutes` to 60 (check less frequently)

### Disable Weather Features

Set api_key to empty string:

```json
{
  "api_key": "",
  ...
}
```

### Manual-Only Mode

Disable weather-based control:

```json
{
  "computers": [
    {
      "id": "pc1",
      "name": "Computer",
      "enabled": false
    }
  ]
}
```

Now you can manually control computers only via API/dashboard.

## Troubleshooting

### Invalid API key

Error in logs: `Configuration required`

Fix: Get new key from https://openweathermap.org/api

### JSON syntax error

Error: `JSON decode error` or `Expecting value`

Fix: Validate JSON at https://jsonlint.com/

### Invalid coordinates

Error: `lat not in range` or `lon not in range`

Fix: Use coordinates within valid ranges:
- Latitude: -90 to 90
- Longitude: -180 to 180

### Computer not showing up

Check:
- Computer ID is unique
- JSON syntax is valid
- Application is restarted
- Computer is enabled in dashboard

## Best Practices

1. **Backup config.json** before making changes
2. **Use reasonable check intervals** (300+ seconds)
3. **Enable notifications** for important alerts
4. **Set forecast window** based on your weather patterns
5. **Test Wake-on-LAN** before relying on auto-boot
6. **Monitor logs** for configuration issues

## Support

For help:
- Check logs: `tail -f weather_shield.log`
- See [Troubleshooting Guide](./troubleshooting.md)
- Open issue: https://github.com/palpitate013/weather-shield/issues
