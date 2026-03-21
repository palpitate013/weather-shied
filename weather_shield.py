#!/usr/bin/env python3
"""
Weather Shield - Unified Application
Combined weather monitoring daemon and web dashboard.
Runs both weather_monitor and Flask app in separate threads.
"""

import os
import sys
import time
import subprocess
import logging
import threading
import json
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_shield.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('weather-shield')


class WeatherMonitor:
    """Monitor weather conditions and control computer power state."""

    # Weather conditions considered "bad"
    BAD_WEATHER_CONDITIONS = {
        'Thunderstorm', 'Tornado', 'Squall', 'Hurricane',
        'Heavy rain', 'Extreme rain', 'Freezing rain',
        'Heavy snow', 'Blizzard', 'Heavy sleet',
        'Hail', 'Dust', 'Dust whirls', 'Fog', 'Mist'
    }

    # Warning codes (OpenWeather API)
    BAD_WEATHER_CODES = {
        # Thunderstorm (2xx)
        200, 201, 202, 210, 211, 212, 221, 230, 231, 232,
        # Drizzle (3xx)
        300, 301, 302, 310, 311, 312, 313, 314, 321,
        # Rain (5xx)
        500, 501, 502, 503, 504, 511, 520, 521, 522, 531,
        # Snow (6xx)
        600, 601, 602, 610, 611, 612, 613, 614, 615, 616, 620, 621, 622,
        # Atmosphere (7xx)
        701, 711, 721, 731, 741, 751, 761, 762, 771, 781
    }

    def __init__(self, config_path: str = 'config.json'):
        """Initialize the weather monitor."""
        self.config = self._load_config(config_path)
        self.api_key = self.config.get('api_key')
        self.latitude = self.config.get('latitude')
        self.longitude = self.config.get('longitude')
        self.check_interval = self.config.get('check_interval', 300)  # 5 minutes default
        self.forecast_minutes = self.config.get('forecast_minutes', 30)
        self.is_computer_on = False
        self.is_bad_weather = False
        self.last_action = None
        self.running = True
        self.logger = logging.getLogger('weather-shield.monitor')

        if not self.api_key or not self.latitude or not self.longitude:
            raise ValueError("Missing required config: api_key, latitude, longitude")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            self.logger = logging.getLogger('weather-shield.monitor')
            self.logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            return json.load(f)

    def get_weather_data(self) -> Optional[Dict]:
        """Fetch current weather data from OpenWeather API."""
        try:
            import requests
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'appid': self.api_key,
                'units': self.config.get('units', 'metric')
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            return None

    def get_forecast_data(self) -> Optional[Dict]:
        """Fetch forecast data from OpenWeather API."""
        try:
            import requests
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'appid': self.api_key,
                'units': self.config.get('units', 'metric')
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self.logger.error(f"Failed to fetch forecast data: {e}")
            return None

    def check_current_weather(self) -> bool:
        """Check if current weather conditions are bad."""
        weather_data = self.get_weather_data()
        if not weather_data:
            return False

        weather_code = weather_data['weather'][0]['id']
        weather_desc = weather_data['weather'][0]['main']

        is_bad = weather_code in self.BAD_WEATHER_CODES or \
                 weather_desc in self.BAD_WEATHER_CONDITIONS

        self.logger.info(
            f"Current weather: {weather_desc} (Code: {weather_code}) - Bad: {is_bad}"
        )
        return is_bad

    def check_forecast_weather(self) -> bool:
        """Check if bad weather is predicted within the forecast window."""
        forecast_data = self.get_forecast_data()
        if not forecast_data:
            return False

        forecast_threshold = datetime.now() + timedelta(minutes=self.forecast_minutes)
        has_bad_weather = False

        for item in forecast_data['list']:
            item_time = datetime.fromtimestamp(item['dt'])

            if item_time > forecast_threshold:
                break

            weather_code = item['weather'][0]['id']
            weather_desc = item['weather'][0]['main']

            if weather_code in self.BAD_WEATHER_CODES or \
               weather_desc in self.BAD_WEATHER_CONDITIONS:
                has_bad_weather = True
                self.logger.info(
                    f"Bad weather forecasted at {item_time}: {weather_desc} ({weather_code})"
                )
                break

        if not has_bad_weather:
            self.logger.info(f"No bad weather forecasted in next {self.forecast_minutes} minutes")

        return has_bad_weather

    def should_shutdown(self) -> bool:
        """Determine if computer should shutdown."""
        current_bad = self.check_current_weather()
        forecast_bad = self.check_forecast_weather()
        should_shutdown = current_bad or forecast_bad

        self.logger.info(
            f"Should shutdown: {should_shutdown} "
            f"(current_bad={current_bad}, forecast_bad={forecast_bad})"
        )
        return should_shutdown

    def should_boot(self) -> bool:
        """Determine if computer should boot."""
        current_bad = self.check_current_weather()
        forecast_bad = self.check_forecast_weather()
        should_boot = not (current_bad or forecast_bad)

        return should_boot

    def shutdown_computer(self):
        """Send shutdown signal to the computer."""
        if self.is_computer_on:
            self.logger.info("Shutting down computer due to bad weather...")
            try:
                system = sys.platform
                if system == "win32":
                    subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                elif system in ["linux", "linux2"]:
                    subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                elif system == "darwin":
                    subprocess.run(
                        ["osascript", "-e", "tell application \"System Events\" to "
                         "shut down"],
                        check=True
                    )
                self.is_computer_on = False
                self.last_action = "shutdown"
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to shutdown: {e}")

    def boot_computer(self):
        """Send boot signal to wake the computer."""
        if not self.is_computer_on:
            self.logger.info("Weather conditions improved. Computer can boot.")
            try:
                system = sys.platform
                if system == "win32":
                    self.logger.info("Boot signal for Windows (requires Wake-on-LAN)")
                elif system in ["linux", "linux2"]:
                    self.logger.info("Boot signal for Linux (requires Wake-on-LAN from another machine)")
                elif system == "darwin":
                    self.logger.info("Boot signal for macOS (requires Wake-on-LAN)")

                self.is_computer_on = True
                self.last_action = "boot"
            except Exception as e:
                self.logger.error(f"Failed to boot: {e}")

    def run(self):
        """Main monitoring loop."""
        self.logger.info("Weather Shield started")
        self.logger.info(f"Location: {self.latitude}, {self.longitude}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info(f"Forecast window: {self.forecast_minutes} minutes")

        while self.running:
            try:
                if self.should_shutdown():
                    self.shutdown_computer()
                elif self.should_boot():
                    self.boot_computer()

                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, shutting down...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

    def stop(self):
        """Stop the monitoring loop."""
        self.logger.info("Stopping weather monitor...")
        self.running = False


class DashboardApp:
    """Flask-based web dashboard."""

    def __init__(self, config_path: str = 'config.json'):
        """Initialize the dashboard."""
        try:
            from flask import Flask, render_template, jsonify
            from flask_cors import CORS
        except ImportError as e:
            raise ImportError(f"Flask not installed: {e}")

        # Get the directory where weather_shield.py is located
        app_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(app_dir, 'templates')
        static_dir = os.path.join(app_dir, 'static')

        self.app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
        CORS(self.app)
        self.jsonify = jsonify
        self.config_file = config_path
        self.logger = logging.getLogger('weather-shield.dashboard')
        self.running = True

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes."""
        from flask import send_from_directory, render_template
        
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/weather')
        def get_weather():
            return self.jsonify(self._get_weather_data())

        @self.app.route('/api/forecast')
        def get_forecast():
            return self.jsonify(self._get_forecast_data())

        @self.app.route('/api/device-status')
        def get_device_status():
            return self.jsonify(self._get_device_status())

        @self.app.route('/api/config')
        def get_config():
            return self.jsonify({
                'location': f"{self.config.get('latitude')}, {self.config.get('longitude')}",
                'units': self.config.get('units', 'metric'),
                'check_interval': self.config.get('check_interval', 300),
                'forecast_minutes': self.config.get('forecast_minutes', 30)
            })

    def _get_weather_data(self) -> Dict:
        """Fetch current weather data."""
        try:
            import requests
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.config.get('latitude'),
                'lon': self.config.get('longitude'),
                'appid': self.config.get('api_key'),
                'units': self.config.get('units', 'metric')
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'main': data['weather'][0]['main'],
                'code': data['weather'][0]['id'],
                'wind_speed': data['wind']['speed'],
                'location': f"{data['name']}, {data['sys'].get('country', '')}",
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error fetching weather: {e}")
            return {'error': str(e)}

    def _get_forecast_data(self) -> Dict:
        """Fetch forecast data."""
        try:
            import requests
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': self.config.get('latitude'),
                'lon': self.config.get('longitude'),
                'appid': self.config.get('api_key'),
                'units': self.config.get('units', 'metric')
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data['list'][:4]:
                forecasts.append({
                    'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'].title(),
                    'main': item['weather'][0]['main'],
                    'wind_speed': item['wind']['speed']
                })

            return {'forecasts': forecasts}
        except Exception as e:
            self.logger.error(f"Error fetching forecast: {e}")
            return {'error': str(e)}

    def _get_device_status(self) -> Dict:
        """Get device monitoring status."""
        try:
            with open('weather_shield.log', 'r') as f:
                lines = f.readlines()
                last_check = lines[-1] if lines else 'Never'
        except FileNotFoundError:
            last_check = 'Never'

        return {
            'status': 'running',
            'last_check': last_check,
            'is_monitoring': True
        }

    def run(self, host: str = 'localhost', port: int = 5000, debug: bool = False):
        """Run the Flask app."""
        self.logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

    def stop(self):
        """Stop the Flask app."""
        self.logger.info("Stopping dashboard...")
        self.running = False


class WeatherShield:
    """Combined Weather Shield application."""

    def __init__(self):
        """Initialize the combined application."""
        self.logger = logging.getLogger('weather-shield')
        self.monitor = None
        self.dashboard = None
        self.monitor_thread = None
        self.dashboard_thread = None
        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def start(self, dashboard_port: int = 5000):
        """Start both monitor and dashboard."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🌦️  Weather Shield Starting")
            self.logger.info("=" * 60)

            # Initialize monitor
            self.monitor = WeatherMonitor('config.json')
            self.monitor_thread = threading.Thread(target=self.monitor.run, daemon=True)
            self.monitor_thread.start()
            self.logger.info("✅ Weather Monitor started")

            # Initialize dashboard
            self.dashboard = DashboardApp('config.json')
            self.dashboard_thread = threading.Thread(
                target=self.dashboard.run,
                args=('0.0.0.0', dashboard_port),
                daemon=True
            )
            self.dashboard_thread.start()
            self.logger.info(f"✅ Dashboard started on port {dashboard_port}")

            self.logger.info("=" * 60)
            self.logger.info("🌦️  Weather Shield Running")
            self.logger.info(f"Dashboard: http://localhost:{dashboard_port}")
            self.logger.info("=" * 60)
            self.logger.info("Press Ctrl+C to stop")

            # Keep main thread alive and responsive to signals
            try:
                while self.running:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.logger.info("Received Ctrl+C, shutting down...")
                self.stop()

        except Exception as e:
            self.logger.error(f"Failed to start Weather Shield: {e}")
            self.stop()
            sys.exit(1)

    def stop(self):
        """Stop both monitor and dashboard."""
        self.logger.info("Stopping Weather Shield...")
        self.running = False

        if self.monitor:
            self.monitor.stop()

        if self.dashboard:
            self.dashboard.stop()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        if self.dashboard_thread:
            self.dashboard_thread.join(timeout=5)

        self.logger.info("Weather Shield stopped")


if __name__ == '__main__':
    app = WeatherShield()
    try:
        app.start()
    except KeyboardInterrupt:
        app.logger.info("Received interrupt, stopping...")
        app.stop()
    finally:
        sys.exit(0)
