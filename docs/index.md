# Weather Shield Documentation

Welcome to the Weather Shield documentation! This comprehensive guide covers installation, usage, configuration, and deployment options.

## Quick Start

```bash
# Using Docker (Recommended)
git clone https://github.com/palpitate013/weather-shield.git
cd weather-shield
docker-compose up -d

# Access at http://localhost:5000
```

## What is Weather Shield?

Weather Shield is a real-time weather monitoring system that automatically controls computer power states based on weather conditions. It helps protect your equipment from damage during severe weather by automatically shutting down computers when dangerous weather approaches.

### Key Features

- **Real-time Weather Monitoring**: Fetches weather data from OpenWeather API
- **Multi-Computer Support**: Monitor and control multiple computers from one dashboard
- **Automatic Control**: Shutdown on bad weather, boot when conditions improve
- **Manual Control**: Override automatic behavior with manual on/off controls
- **Web Dashboard**: Beautiful, responsive UI for monitoring and control
- **Notifications**: ntfy.sh integration for alerts and status updates
- **REST API**: Programmatic access to all features
- **Multi-platform**: Linux, macOS, Windows (WSL2), Docker

## Installation

Choose your preferred installation method:

- [**Docker** (Recommended)](./docker.md) - Containerized deployment
- [**Linux (.deb package)**](./installation.md) - Debian/Ubuntu users
- [**pip/Python**](./installation.md) - Developer-friendly
- [**NixOS/Nix Flakes**](./nixos.md) - For NixOS users

## Configuration

See [Configuration Guide](./configuration.md) for:
- API key setup
- Location configuration
- Computer setup
- Notification configuration
- Advanced settings

## Usage

Access the dashboard at `http://localhost:5000` after starting the application.

### Dashboard Features

- **Current Weather**: Real-time conditions, temperature, humidity, wind
- **Forecast**: 12-hour weather forecast
- **Computer Status**: Monitor multiple computers
- **Manual Control**: Turn computers on/off manually
- **Settings**: Configure API key and location

### API Reference

See [API Documentation](./api.md) for complete REST API reference.

## Deployment

- [Docker Deployment](./docker.md)
- [Linux Deployment](./installation.md)
- [NixOS Deployment](./nixos.md)
- [CI/CD Pipeline](./ci-cd.md)

## Troubleshooting

### Common Issues

**Port 5000 already in use**
```bash
# Change port in config.json or use different port
docker-compose -f docker-compose.yml -p 8000 up
```

**Weather API errors**
- Verify API key at https://openweathermap.org/api
- Check latitude/longitude are valid
- Ensure internet connection is working

**Computer won't boot**
- Enable Wake-on-LAN in BIOS
- Install etherwake: `sudo apt-get install etherwake`
- Verify MAC addresses in dashboard

See [Troubleshooting Guide](./troubleshooting.md) for more help.

## Development

- [Development Setup](./development.md)
- [Contributing Guidelines](https://github.com/palpitate013/weather-shield/blob/main/CONTRIBUTING.md)
- [Architecture](./architecture.md)

## Support

- 🐛 [Report Bugs](https://github.com/palpitate013/weather-shield/issues)
- 💡 [Request Features](https://github.com/palpitate013/weather-shield/discussions)
- 📖 [Read More](https://github.com/palpitate013/weather-shield)

## License

MIT License - See LICENSE file for details

## About

Weather Shield is an open-source project maintained by the community. We welcome contributions and feedback!

---

**Latest Version**: 1.0.0  
**Last Updated**: March 21, 2026  
**Repository**: https://github.com/palpitate013/weather-shield
