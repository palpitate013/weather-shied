#!/usr/bin/env python3
"""
Weather-based Computer Control System
Monitors weather conditions and sends shutdown/boot signals based on conditions.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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

        if not self.api_key or not self.latitude or not self.longitude:
            raise ValueError("Missing required config: api_key, latitude, longitude")

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        if not os.path.exists(config_path):
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            return json.load(f)

    def get_weather_data(self) -> Optional[Dict]:
        """Fetch current and forecast weather data from OpenWeather API."""
        try:
            # One Call API 2.5 endpoint - includes current and forecast
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None

    def get_forecast_data(self) -> Optional[Dict]:
        """Fetch forecast data from OpenWeather API."""
        try:
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch forecast data: {e}")
            return None

    def is_bad_weather_condition(self, condition_code: int, condition_main: str, condition_desc: str) -> bool:
        """Check if weather condition is considered bad."""
        # Check by code
        if condition_code in self.BAD_WEATHER_CODES:
            return True

        # Check by description
        if condition_desc.lower() in [desc.lower() for desc in self.BAD_WEATHER_CONDITIONS]:
            return True

        # Check main category (more lenient)
        main_bad = {'Thunderstorm', 'Drizzle', 'Rain', 'Snow', 'Mist', 'Smoke', 'Haze', 'Dust', 'Fog', 'Ash', 'Squall', 'Tornado'}
        if condition_main in main_bad:
            return True

        return False

    def check_current_weather(self) -> bool:
        """Check if current weather is bad. Returns True if bad."""
        weather_data = self.get_weather_data()
        if not weather_data:
            logger.warning("Could not fetch weather data, assuming safe conditions")
            return False

        weather = weather_data.get('weather', [{}])[0]
        condition_code = weather.get('id', 800)
        condition_main = weather.get('main', 'Clear')
        condition_desc = weather.get('description', 'clear sky')

        is_bad = self.is_bad_weather_condition(condition_code, condition_main, condition_desc)

        logger.info(f"Current weather: {condition_main} ({condition_desc}) - Code: {condition_code} - Bad: {is_bad}")
        return is_bad

    def check_forecast_weather(self) -> bool:
        """Check if bad weather is forecasted within the next N minutes. Returns True if bad."""
        forecast_data = self.get_forecast_data()
        if not forecast_data:
            logger.warning("Could not fetch forecast data")
            return False

        cutoff_time = datetime.now() + timedelta(minutes=self.forecast_minutes)
        forecast_list = forecast_data.get('list', [])

        bad_weather_forecasted = False
        for forecast in forecast_list:
            forecast_time = datetime.fromtimestamp(forecast['dt'])

            if forecast_time > cutoff_time:
                break

            weather = forecast.get('weather', [{}])[0]
            condition_code = weather.get('id', 800)
            condition_main = weather.get('main', 'Clear')
            condition_desc = weather.get('description', 'clear sky')

            if self.is_bad_weather_condition(condition_code, condition_main, condition_desc):
                bad_weather_forecasted = True
                logger.info(f"Bad weather forecasted at {forecast_time}: {condition_main} ({condition_desc})")
                break

        if not bad_weather_forecasted:
            logger.info(f"No bad weather forecasted in next {self.forecast_minutes} minutes")

        return bad_weather_forecasted

    def should_shutdown(self) -> bool:
        """Determine if computer should shut down."""
        current_bad = self.check_current_weather()
        forecast_bad = self.check_forecast_weather()

        should_shut = current_bad or forecast_bad
        logger.info(f"Should shutdown: {should_shut} (current_bad={current_bad}, forecast_bad={forecast_bad})")
        return should_shut

    def should_boot(self) -> bool:
        """Determine if computer should boot up."""
        current_bad = self.check_current_weather()
        forecast_bad = self.check_forecast_weather()

        should_boot = not current_bad and not forecast_bad
        logger.info(f"Should boot: {should_boot} (current_bad={current_bad}, forecast_bad={forecast_bad})")
        return should_boot

    def shutdown_computer(self):
        """Send shutdown signal to computer."""
        try:
            if sys.platform == 'win32':
                subprocess.run(['shutdown', '/s', '/t', '60'], check=True)
                logger.info("Windows shutdown command sent")
            elif sys.platform in ['linux', 'linux2']:
                # For Linux, use systemctl or shutdown command
                subprocess.run(['sudo', 'shutdown', '-h', '+1'], check=True)
                logger.info("Linux shutdown command sent")
            elif sys.platform == 'darwin':
                subprocess.run(['osascript', '-e', 'tell application "System Events" to shut down'], check=True)
                logger.info("macOS shutdown command sent")

            self.is_computer_on = False
            self.last_action = 'shutdown'

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to shutdown computer: {e}")

    def boot_computer(self):
        """Send boot signal to computer."""
        try:
            # Note: Waking a computer remotely requires Wake-on-LAN or BIOS settings
            if sys.platform == 'win32':
                subprocess.run(['powercfg', '/lastwake'], check=False)
                logger.info("Windows wake command prepared")
            elif sys.platform in ['linux', 'linux2']:
                # For Linux, this would typically require Wake-on-LAN from another machine
                logger.info("Boot signal for Linux (requires Wake-on-LAN from another machine)")
            elif sys.platform == 'darwin':
                logger.info("Boot signal for macOS (requires Wake-on-LAN from another machine)")

            self.is_computer_on = True
            self.last_action = 'boot'

        except Exception as e:
            logger.error(f"Failed to boot computer: {e}")

    def run(self):
        """Main monitoring loop."""
        logger.info("Weather Shield started")
        logger.info(f"Location: {self.latitude}, {self.longitude}")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Forecast window: {self.forecast_minutes} minutes")

        try:
            while True:
                should_shut = self.should_shutdown()

                if should_shut and (not self.is_computer_on or self.last_action != 'shutdown'):
                    logger.warning("Bad weather detected! Initiating shutdown...")
                    self.shutdown_computer()

                elif not should_shut and (self.is_computer_on is False or self.last_action != 'boot'):
                    logger.info("Weather conditions improved. Computer can boot.")
                    self.boot_computer()

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Weather Shield stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)


def main():
    """Entry point for the application."""
    try:
        config_path = 'config.json'
        if len(sys.argv) > 1:
            config_path = sys.argv[1]

        monitor = WeatherMonitor(config_path)
        monitor.run()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
