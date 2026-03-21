#!/bin/bash
# Build Debian package for Weather Shield

set -e

OUTPUT_DIR="${1:-.}"
mkdir -p "$OUTPUT_DIR"

# Get version from setup.py
VERSION=$(grep 'version=' setup.py | grep -oP '\d+\.\d+\.\d+' | head -1)

# Create debian build directory
DEB_BUILD="$OUTPUT_DIR/weather-shield-$VERSION"
mkdir -p "$DEB_BUILD/DEBIAN"
mkdir -p "$DEB_BUILD/usr/bin"
mkdir -p "$DEB_BUILD/usr/share/weather-shield"
mkdir -p "$DEB_BUILD/usr/share/weather-shield/templates"
mkdir -p "$DEB_BUILD/usr/share/weather-shield/static"
mkdir -p "$DEB_BUILD/etc/weather-shield"
mkdir -p "$DEB_BUILD/etc/systemd/system"

# Copy files
cp weather_shield.py "$DEB_BUILD/usr/share/weather-shield/"
cp app.py "$DEB_BUILD/usr/share/weather-shield/"
cp templates/* "$DEB_BUILD/usr/share/weather-shield/templates/"
cp static/* "$DEB_BUILD/usr/share/weather-shield/static/"
cp config.example.json "$DEB_BUILD/etc/weather-shield/config.json.example"
cp weather-shield.service "$DEB_BUILD/etc/systemd/system/"

# Create wrapper script
cat > "$DEB_BUILD/usr/bin/weather-shield" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/usr/share/weather-shield')
from weather_shield import main
if __name__ == '__main__':
    main()
EOF
chmod +x "$DEB_BUILD/usr/bin/weather-shield"

# Create control file
cat > "$DEB_BUILD/DEBIAN/control" << EOF
Package: weather-shield
Version: $VERSION
Architecture: amd64
Maintainer: Weather Shield Contributors <dev@weather-shield.io>
Depends: python3 (>= 3.8), python3-flask, python3-flask-cors, python3-requests, python3-gunicorn
Description: Real-time weather monitoring and computer control system
 Weather Shield monitors weather conditions and automatically controls
 computer power states based on weather patterns.
 .
 Features:
  - Real-time weather monitoring via OpenWeather API
  - Web-based dashboard for system status and control
  - Multi-computer support with individual tracking
  - Automatic shutdown on bad weather
  - Automatic boot when weather improves
  - ntfy.sh notifications for alerts and status changes
  - REST API for programmatic access
Homepage: https://github.com/palpitate013/weather-shield
EOF

# Create postinst script
cat > "$DEB_BUILD/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Enable systemd service
systemctl daemon-reload || true
echo "Weather Shield installed successfully!"
echo "To start the service: sudo systemctl start weather-shield"
echo "To enable on boot: sudo systemctl enable weather-shield"
echo "Configuration: /etc/weather-shield/config.json"

exit 0
EOF
chmod +x "$DEB_BUILD/DEBIAN/postinst"

# Create prerm script
cat > "$DEB_BUILD/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Stop service before removing
systemctl stop weather-shield || true

exit 0
EOF
chmod +x "$DEB_BUILD/DEBIAN/prerm"

# Build the package
fakeroot dpkg-deb --build "$DEB_BUILD" "$OUTPUT_DIR/weather-shield_${VERSION}_amd64.deb"

echo "✅ Debian package created: $OUTPUT_DIR/weather-shield_${VERSION}_amd64.deb"
