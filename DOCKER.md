# Docker Deployment

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/palpitate013/weather-shied.git
cd weather-shied

# Configure your settings
nano config.json

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f weather-shield

# Stop the application
docker-compose down
```

### Manual Docker Build

```bash
# Build the image
docker build -t weather-shield:latest .

# Run the container
docker run -d \
  --name weather-shield \
  -p 5000:5000 \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/weather_shield.log:/app/weather_shield.log \
  weather-shield:latest
```

## Configuration

Before running, edit `config.json`:

```json
{
  "api_key": "your_openweathermap_api_key",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "units": "metric",
  "check_interval": 300,
  "forecast_minutes": 30,
  "ntfy_topic": "your_ntfy_topic",
  "computers": [
    {
      "id": "computer-1",
      "name": "Main Computer",
      "enabled": true
    }
  ]
}
```

## Accessing the Dashboard

Open your browser and navigate to: `http://localhost:5000`

## Environment Variables

You can override configuration using environment variables:

```bash
docker run -d \
  --name weather-shield \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  weather-shield:latest
```

## Updating

```bash
# Pull latest changes
git pull

# Rebuild the image
docker-compose build --no-cache

# Restart the service
docker-compose restart
```

## Troubleshooting

### Port already in use

Change the port in `docker-compose.yml`:

```yaml
ports:
  - "8000:5000"  # Access at localhost:8000
```

### Permission issues with config file

Ensure proper permissions:

```bash
chmod 644 config.json
```

### View detailed logs

```bash
docker-compose logs -f weather-shield --tail=100
```

## Advanced Configuration

### Running behind a reverse proxy (nginx)

```yaml
services:
  weather-shield:
    # ... existing config ...
    environment:
      - FLASK_ENV=production
      - SERVER_NAME=yourdomain.com
```

### Using Docker volumes for persistence

```yaml
volumes:
  config_data:
  log_data:

services:
  weather-shield:
    volumes:
      - config_data:/app/config
      - log_data:/app/logs
```
