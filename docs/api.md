# API Reference

Weather Shield provides a comprehensive REST API for programmatic access to all functionality.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. Future versions may support API keys.

## Endpoints

### Weather Endpoints

#### Get Current Weather

```
GET /api/weather
```

Returns current weather conditions.

**Response:**
```json
{
  "temperature": 22.5,
  "feels_like": 21.0,
  "humidity": 65,
  "pressure": 1013,
  "description": "Partly Cloudy",
  "main": "Clouds",
  "code": 803,
  "wind_speed": 3.5,
  "location": "New York, US",
  "timestamp": "2026-03-21T14:25:00.000000"
}
```

#### Get Weather Forecast

```
GET /api/forecast
```

Returns 12-hour weather forecast.

**Response:**
```json
{
  "forecasts": [
    {
      "time": "16:00",
      "temperature": 23.0,
      "description": "Sunny",
      "main": "Clear",
      "wind_speed": 2.5
    }
  ]
}
```

### Computer Management

#### List All Computers

```
GET /api/computers
```

Returns all configured computers.

**Response:**
```json
{
  "computers": [
    {
      "id": "computer-1",
      "name": "Main Computer",
      "enabled": true
    }
  ]
}
```

#### Add Computer

```
POST /api/computers
Content-Type: application/json

{
  "name": "Gaming PC",
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Computer added successfully",
  "computer": {
    "id": "computer-2",
    "name": "Gaming PC",
    "enabled": true
  }
}
```

#### Update Computer

```
PUT /api/computers/{computer_id}
Content-Type: application/json

{
  "name": "Gaming PC Updated",
  "enabled": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Computer updated successfully",
  "computer": {
    "id": "computer-2",
    "name": "Gaming PC Updated",
    "enabled": false
  }
}
```

#### Delete Computer

```
DELETE /api/computers/{computer_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Computer deleted successfully"
}
```

### Power Control

#### Manual Power Control

```
POST /api/computers/{computer_id}/power
Content-Type: application/json

{
  "action": "on"
}
```

**Parameters:**
- `action` (required): `"on"` or `"off"`

**Response:**
```json
{
  "success": true,
  "message": "Computer powered on successfully",
  "computer": {
    "id": "computer-1",
    "name": "Main Computer",
    "enabled": true,
    "is_on": true,
    "last_action": "on",
    "action_time": "2026-03-21T14:25:00.000000"
  }
}
```

### Device Status

#### Get Device Status

```
GET /api/device-status
```

Returns overall system status and all computer statuses.

**Response:**
```json
{
  "status": "running",
  "last_check": "2026-03-21 14:25:06,945",
  "is_monitoring": true,
  "computers": [
    {
      "id": "computer-1",
      "name": "Main Computer",
      "enabled": true,
      "is_on": true,
      "last_action": "boot",
      "action_time": "2026-03-21T14:25:00.000000"
    }
  ]
}
```

### Configuration

#### Get Configuration

```
GET /api/config
```

Returns current configuration (API key is masked).

**Response:**
```json
{
  "api_key": "****...****",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30
}
```

#### Get Settings

```
GET /api/settings
```

Alias for `/api/config`.

#### Update Settings

```
POST /api/settings
Content-Type: application/json

{
  "api_key": "your-api-key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "message": "Invalid action. Must be \"on\" or \"off\""
}
```

### 404 Not Found

```json
{
  "success": false,
  "message": "Computer not found"
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "message": "Error description"
}
```

## Examples

### Python

```python
import requests

# Get current weather
response = requests.get('http://localhost:5000/api/weather')
weather = response.json()
print(f"Temperature: {weather['temperature']}°C")

# Turn on a computer
response = requests.post(
    'http://localhost:5000/api/computers/computer-1/power',
    json={'action': 'on'}
)
print(response.json())

# Add a new computer
response = requests.post(
    'http://localhost:5000/api/computers',
    json={'name': 'New Computer', 'enabled': True}
)
print(response.json())
```

### cURL

```bash
# Get weather
curl http://localhost:5000/api/weather

# Power control
curl -X POST http://localhost:5000/api/computers/computer-1/power \
  -H "Content-Type: application/json" \
  -d '{"action":"on"}'

# Add computer
curl -X POST http://localhost:5000/api/computers \
  -H "Content-Type: application/json" \
  -d '{"name":"Gaming PC","enabled":true}'
```

### JavaScript/Fetch

```javascript
// Get weather
const weather = await fetch('http://localhost:5000/api/weather')
  .then(r => r.json());
console.log(`Temp: ${weather.temperature}°C`);

// Power control
const result = await fetch('http://localhost:5000/api/computers/computer-1/power', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ action: 'on' })
}).then(r => r.json());
```

## Rate Limiting

No rate limiting is currently implemented. High-frequency requests should be avoided.

## Changelog

### v1.0.0

- Initial release
- All endpoints listed above
