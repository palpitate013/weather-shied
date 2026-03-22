#!/usr/bin/env python3
"""
Weather Shield Web Dashboard
A Flask-based web interface for Weather Shield monitoring.
"""

import json
import os
import socket
import subprocess
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Configuration
CONFIG_FILE = "config.json"
LOG_FILE = "weather_monitor.log"


class WeatherShieldDashboard:
    """Dashboard backend for Weather Shield monitoring."""

    def __init__(self):
        self.config = self._load_config()
        self.last_update = None
        self.current_weather = None
        self.device_status = None

    def _load_config(self):
        """Load configuration from config.json."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def get_weather_data(self):
        """Fetch current weather data."""
        if not self.config.get("api_key"):
            return {"error": "API key not configured"}

        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": self.config.get("latitude"),
                "lon": self.config.get("longitude"),
                "appid": self.config.get("api_key"),
                "units": self.config.get("units", "metric"),
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            self.current_weather = {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"].title(),
                "main": data["weather"][0]["main"],
                "code": data["weather"][0]["id"],
                "wind_speed": data["wind"]["speed"],
                "location": f"{data['name']}, {data['sys'].get('country', '')}",
                "timestamp": datetime.now().isoformat(),
            }

            return self.current_weather

        except Exception as e:
            return {"error": str(e)}

    def get_forecast_data(self):
        """Fetch forecast data."""
        if not self.config.get("api_key"):
            return {"error": "API key not configured"}

        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": self.config.get("latitude"),
                "lon": self.config.get("longitude"),
                "appid": self.config.get("api_key"),
                "units": self.config.get("units", "metric"),
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Get next 4 forecasts (3-hour intervals)
            forecasts = []
            for item in data["list"][:4]:
                forecasts.append(
                    {
                        "time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"].title(),
                        "main": item["weather"][0]["main"],
                        "wind_speed": item["wind"]["speed"],
                    }
                )

            return forecasts

        except Exception as e:
            return {"error": str(e)}

    def get_device_status(self):
        """Parse logs to get device status."""
        if not os.path.exists(LOG_FILE):
            return {
                "status": "idle",
                "last_action": "none",
                "last_check": "never",
                "is_bad_weather": False,
            }

        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()

            if not lines:
                return {
                    "status": "idle",
                    "last_action": "none",
                    "last_check": "never",
                    "is_bad_weather": False,
                }

            # Get last few lines
            last_lines = lines[-10:]

            status = {
                "status": "monitoring",
                "last_action": "none",
                "last_check": "unknown",
                "is_bad_weather": False,
            }

            for line in reversed(last_lines):
                if "shutdown" in line.lower():
                    status["last_action"] = "shutdown"
                    status["is_bad_weather"] = True
                    break
                elif "boot" in line.lower() or "wake" in line.lower():
                    status["last_action"] = "boot"
                    status["is_bad_weather"] = False
                    break

            if lines:
                last_line = lines[-1]
                try:
                    status["last_check"] = last_line.split(" - ")[0]
                except Exception:
                    status["last_check"] = "unknown"

            return status

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_action": "none",
                "last_check": "never",
                "is_bad_weather": False,
            }

    def get_system_info(self):
        """Get system information for docker control."""
        try:
            hostname = socket.gethostname()

            # Get IP address
            ip_address = socket.gethostbyname(hostname)

            # Get MAC address
            mac_address = self._get_mac_address()

            # Get architecture
            architecture = self._get_architecture()

            # Get hostname for easy identification
            fqdn = socket.getfqdn()

            return {
                "hostname": hostname,
                "fqdn": fqdn,
                "ip_address": ip_address,
                "mac_address": mac_address,
                "architecture": architecture,
                "docker_host": f"ssh://root@{ip_address}",
            }
        except Exception as e:
            return {
                "error": str(e),
                "hostname": "unknown",
                "ip_address": "unknown",
                "mac_address": "unknown",
                "architecture": "unknown",
            }

    def get_wake_on_lan_status(self):
        """Check if Wake on LAN (WoL) is enabled."""
        try:
            # For Linux systems, check with ethtool
            result = subprocess.run(
                ["ethtool", "eth0"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                output = result.stdout
                if "Wake-on:" in output:
                    # Extract WoL status
                    for line in output.split("\n"):
                        if "Wake-on:" in line:
                            status = line.split("Wake-on:")[1].strip().split()[0]
                            # 'g' or 'd' typically indicate WoL is enabled
                            is_enabled = status.lower() not in ["off", "disabled"]
                            return {
                                "enabled": is_enabled,
                                "status": status,
                                "device": "eth0",
                                "supported": True,
                            }

            # Try other common interface names
            for iface in ["eth0", "enp0s3", "enp0s31f6", "eno1", "wlan0"]:
                try:
                    result = subprocess.run(
                        ["ethtool", iface], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and "Wake-on:" in result.stdout:
                        for line in result.stdout.split("\n"):
                            if "Wake-on:" in line:
                                status = line.split("Wake-on:")[1].strip().split()[0]
                                is_enabled = status.lower() not in ["off", "disabled"]
                                return {
                                    "enabled": is_enabled,
                                    "status": status,
                                    "device": iface,
                                    "supported": True,
                                }
                except Exception:
                    continue

            return {
                "enabled": False,
                "status": "unknown",
                "supported": False,
                "message": "WoL status could not be determined",
            }

        except FileNotFoundError:
            return {
                "enabled": False,
                "status": "unknown",
                "supported": False,
                "message": "ethtool not found. Install it with: sudo apt install ethtool",
            }
        except Exception as e:
            return {
                "enabled": False,
                "status": "error",
                "supported": False,
                "error": str(e),
            }

    def _get_mac_address(self):
        """Get MAC address of the primary network interface."""
        try:
            result = subprocess.run(
                ["ip", "link", "show"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "link/ether" in line:
                        mac = line.split("link/ether")[1].strip().split()[0]
                        return mac

            return "unknown"
        except Exception:
            return "unknown"

    def _get_architecture(self):
        """Get system architecture."""
        try:
            result = subprocess.run(
                ["uname", "-m"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"


dashboard = WeatherShieldDashboard()


@app.route("/")
def index():
    """Render main dashboard."""
    return render_template("index.html")


@app.route("/api/weather")
def api_weather():
    """Get current weather data."""
    return jsonify(dashboard.get_weather_data())


@app.route("/api/forecast")
def api_forecast():
    """Get forecast data."""
    return jsonify(dashboard.get_forecast_data())


@app.route("/api/device-status")
def api_device_status():
    """Get device status."""
    return jsonify(dashboard.get_device_status())


@app.route("/api/config")
def api_config():
    """Get public configuration."""
    return jsonify(
        {
            "location": f"{dashboard.config.get('latitude')}, {dashboard.config.get('longitude')}",
            "check_interval": dashboard.config.get("check_interval", 300),
            "forecast_minutes": dashboard.config.get("forecast_minutes", 30),
            "units": dashboard.config.get("units", "metric"),
        }
    )


@app.route("/api/system-info")
def api_system_info():
    """Get system information for docker control."""
    return jsonify(dashboard.get_system_info())


@app.route("/api/wol-status")
def api_wol_status():
    """Get Wake on LAN status."""
    return jsonify(dashboard.get_wake_on_lan_status())


@app.route("/api/control-info")
def api_control_info():
    """Get all information needed to control this computer remotely."""
    return jsonify(
        {
            "system": dashboard.get_system_info(),
            "wol": dashboard.get_wake_on_lan_status(),
            "docker_available": os.path.exists("/var/run/docker.sock")
            or os.path.exists("/run/docker.sock"),
            "service": {"name": "weather-shield", "port": 5000, "protocol": "http"},
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
