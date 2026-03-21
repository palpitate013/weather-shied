#!/bin/bash
# Build RPM package for Weather Shield

set -e

OUTPUT_DIR="${1:-.}"
mkdir -p "$OUTPUT_DIR"

# Get version from setup.py
VERSION=$(grep 'version=' setup.py | grep -oP '\d+\.\d+\.\d+' | head -1)

# Create RPM build directories
mkdir -p "$OUTPUT_DIR/BUILDROOT/usr/bin"
mkdir -p "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/templates"
mkdir -p "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/static"
mkdir -p "$OUTPUT_DIR/BUILDROOT/etc/weather-shield"
mkdir -p "$OUTPUT_DIR/BUILDROOT/etc/systemd/system"
mkdir -p "$OUTPUT_DIR/SPECS"

# Copy files
cp weather_shield.py "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/"
cp app.py "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/"
cp templates/* "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/templates/"
cp static/* "$OUTPUT_DIR/BUILDROOT/usr/share/weather-shield/static/"
cp config.example.json "$OUTPUT_DIR/BUILDROOT/etc/weather-shield/config.json.example"
cp weather-shield.service "$OUTPUT_DIR/BUILDROOT/etc/systemd/system/"

# Create wrapper script
cat > "$OUTPUT_DIR/BUILDROOT/usr/bin/weather-shield" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/usr/share/weather-shield')
from weather_shield import main
if __name__ == '__main__':
    main()
EOF
chmod +x "$OUTPUT_DIR/BUILDROOT/usr/bin/weather-shield"

# Create .spec file
cat > "$OUTPUT_DIR/SPECS/weather-shield.spec" << EOF
Name:           weather-shield
Version:        $VERSION
Release:        1
Summary:        Real-time weather monitoring and computer control system
License:        MIT
URL:            https://github.com/palpitate013/weather-shield

Requires:       python3 >= 3.8, python3-flask, python3-flask-cors, python3-requests, python3-gunicorn

%description
Weather Shield monitors weather conditions and automatically controls
computer power states based on weather patterns.

Features:
- Real-time weather monitoring via OpenWeather API
- Web-based dashboard for system status and control
- Multi-computer support with individual tracking
- Automatic shutdown on bad weather
- Automatic boot when weather improves
- ntfy.sh notifications for alerts and status changes
- REST API for programmatic access

%files
/usr/bin/weather-shield
/usr/share/weather-shield/
/etc/systemd/system/weather-shield.service
%config(noreplace) /etc/weather-shield/config.json.example

%post
systemctl daemon-reload || true

%preun
systemctl stop weather-shield || true
EOF

# Build the RPM
rpmbuild --define "_topdir $OUTPUT_DIR" -bb "$OUTPUT_DIR/SPECS/weather-shield.spec"

# Move the built RPM to output directory
find "$OUTPUT_DIR" -name "weather-shield-*.rpm" -exec mv {} "$OUTPUT_DIR/" \;

echo "✅ RPM package created: $OUTPUT_DIR/weather-shield-${VERSION}-1.x86_64.rpm"
