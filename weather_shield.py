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
import requests as req_module
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
        self.logger = logging.getLogger('weather-shield.monitor')
        self.config_path = config_path
        
        self.config = self._load_config(config_path)
        self.api_key = self.config.get('api_key')
        self.latitude = self.config.get('latitude')
        self.longitude = self.config.get('longitude')
        self.check_interval = self.config.get('check_interval', 300)  # 5 minutes default
        self.forecast_minutes = self.config.get('forecast_minutes', 30)
        
        # Multi-computer support: Track status for each computer
        self.computers: Dict[str, Dict] = {}
        self._initialize_computers()
        
        self.is_bad_weather = False
        self.running = True

        # Check if we have all required config
        if not self.api_key or not self.latitude or not self.longitude:
            self.logger.warning("Missing required config: api_key, latitude, longitude - Weather monitoring disabled until configured")
            self.disabled = True
        else:
            self.disabled = False

    def _initialize_computers(self):
        """Initialize computer status tracking from config."""
        computers_config = self.config.get('computers', [])
        
        for comp in computers_config:
            comp_id = comp.get('id', f'computer-{len(self.computers) + 1}')
            self.computers[comp_id] = {
                'name': comp.get('name', f'Computer {len(self.computers) + 1}'),
                'enabled': comp.get('enabled', True),
                'is_on': False,
                'last_action': None,
                'action_time': None
            }
            self.logger.info(f"Initialized computer: {self.computers[comp_id]['name']} ({comp_id})")

    def _send_ntfy_notification(self, title: str, message: str, priority: str = "default"):
        """Send notification via ntfy.sh service."""
        try:
            ntfy_topic = self.config.get('ntfy_topic')
            if not ntfy_topic:
                return  # ntfy not configured, skip
            
            headers = {
                'Title': title,
                'Priority': priority,
                'Tags': 'weather-shield'
            }
            
            req_module.post(
                f'https://ntfy.sh/{ntfy_topic}',
                data=message.encode(encoding='utf-8'),
                headers=headers,
                timeout=5
            )
            self.logger.debug(f"Sent ntfy notification: {title}")
        except Exception as e:
            self.logger.warning(f"Failed to send ntfy notification: {e}")

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

    def shutdown_computer(self, computer_id: Optional[str] = None):
        """Send shutdown signal to the computer(s)."""
        from datetime import datetime
        
        # If no specific computer, shutdown all enabled ones
        target_computers = [computer_id] if computer_id else list(self.computers.keys())
        
        for comp_id in target_computers:
            if comp_id not in self.computers:
                self.logger.warning(f"Computer {comp_id} not found")
                continue
            
            comp = self.computers[comp_id]
            if not comp['enabled'] or not comp['is_on']:
                continue
            
            self.logger.info(f"Shutting down {comp['name']} due to bad weather...")
            self._send_ntfy_notification(
                "🌦️ Bad Weather Alert",
                f"{comp['name']} is being shut down due to bad weather conditions.",
                priority="high"
            )
            try:
                system = sys.platform
                if system == "win32":
                    subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                elif system in ["linux", "linux2"]:
                    subprocess.run(["sudo", "shutdown", "-h", "+1"], check=True)
                elif system == "darwin":
                    subprocess.run(
                        ["osascript", "-e", "tell application \"System Events\" to shut down"],
                        check=True
                    )
                comp['is_on'] = False
                comp['last_action'] = "shutdown"
                comp['action_time'] = datetime.now().isoformat()
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to shutdown {comp['name']}: {e}")

    def boot_computer(self, computer_id: Optional[str] = None):
        """Send boot signal to wake the computer(s)."""
        from datetime import datetime
        
        # If no specific computer, boot all enabled ones
        target_computers = [computer_id] if computer_id else list(self.computers.keys())
        
        for comp_id in target_computers:
            if comp_id not in self.computers:
                self.logger.warning(f"Computer {comp_id} not found")
                continue
            
            comp = self.computers[comp_id]
            if not comp['enabled'] or comp['is_on']:
                continue
            
            self.logger.info(f"Weather conditions improved for {comp['name']}. Computer can boot.")
            self._send_ntfy_notification(
                "✅ Weather Improved",
                f"Weather conditions improved for {comp['name']}. Ready to boot.",
                priority="default"
            )
            try:
                system = sys.platform
                if system == "win32":
                    self.logger.info(f"Boot signal for {comp['name']} on Windows (requires Wake-on-LAN)")
                elif system in ["linux", "linux2"]:
                    self.logger.info(f"Boot signal for {comp['name']} on Linux (requires Wake-on-LAN from another machine)")
                elif system == "darwin":
                    self.logger.info(f"Boot signal for {comp['name']} on macOS (requires Wake-on-LAN)")

                comp['is_on'] = True
                comp['last_action'] = "boot"
                comp['action_time'] = datetime.now().isoformat()
            except Exception as e:
                self.logger.error(f"Failed to boot {comp['name']}: {e}")

    def run(self):
        """Main monitoring loop."""
        if self.disabled:
            self.logger.info("Weather monitoring disabled - waiting for configuration...")
            # Periodically reload config to check if it's been set
            while self.running:
                time.sleep(5)
                try:
                    self.config = self._load_config(self.config_path)
                    self.api_key = self.config.get('api_key')
                    self.latitude = self.config.get('latitude')
                    self.longitude = self.config.get('longitude')
                    
                    if self.api_key and self.latitude and self.longitude:
                        self.disabled = False
                        self.logger.info("Configuration loaded! Weather monitoring enabled.")
                        break
                except Exception as e:
                    self.logger.debug(f"Error reloading config: {e}")
            
            if self.disabled:
                return
        
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

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes."""
        from flask import send_from_directory, render_template, request
        
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
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return self.jsonify({
                'api_key': config.get('api_key', ''),
                'latitude': config.get('latitude', ''),
                'longitude': config.get('longitude', ''),
                'location': f"{config.get('latitude', '')}, {config.get('longitude', '')}",
                'units': config.get('units', 'metric'),
                'check_interval': config.get('check_interval', 300),
                'forecast_minutes': config.get('forecast_minutes', 30)
            })

        @self.app.route('/api/settings', methods=['POST'])
        def save_settings():
            """Save settings to config.json and validate API key."""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['api_key', 'latitude', 'longitude', 'units', 'check_interval', 'forecast_minutes']
                if not all(field in data for field in required_fields):
                    return self.jsonify({
                        'success': False,
                        'message': 'Missing required fields'
                    }), 400
                
                # Validate coordinates
                try:
                    lat = float(data['latitude'])
                    lon = float(data['longitude'])
                    if lat < -90 or lat > 90:
                        return self.jsonify({
                            'success': False,
                            'message': 'Latitude must be between -90 and 90'
                        }), 400
                    if lon < -180 or lon > 180:
                        return self.jsonify({
                            'success': False,
                            'message': 'Longitude must be between -180 and 180'
                        }), 400
                except (ValueError, TypeError):
                    return self.jsonify({
                        'success': False,
                        'message': 'Invalid latitude or longitude'
                    }), 400
                
                # Validate API key by making a test call
                try:
                    import requests
                    url = "https://api.openweathermap.org/data/2.5/weather"
                    params = {
                        'lat': data['latitude'],
                        'lon': data['longitude'],
                        'appid': data['api_key'],
                        'units': data['units']
                    }
                    response = requests.get(url, params=params, timeout=5)
                    if response.status_code != 200:
                        return self.jsonify({
                            'success': False,
                            'message': 'Invalid API key or coordinates'
                        }), 400
                except Exception as e:
                    self.logger.error(f"Error validating API key: {e}")
                    return self.jsonify({
                        'success': False,
                        'message': f'Error validating API key: {str(e)}'
                    }), 400
                
                # Save configuration (preserve existing computers list)
                with open(self.config_file, 'r') as f:
                    existing_config = json.load(f)
                
                config = {
                    'api_key': data['api_key'],
                    'latitude': float(data['latitude']),
                    'longitude': float(data['longitude']),
                    'units': data['units'],
                    'check_interval': int(data['check_interval']),
                    'forecast_minutes': int(data['forecast_minutes']),
                    'computers': existing_config.get('computers', [])
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.logger.info(f"Settings saved: {config}")
                
                return self.jsonify({
                    'success': True,
                    'message': 'Settings saved successfully'
                }), 200
                
            except Exception as e:
                self.logger.error(f"Error saving settings: {e}")
                return self.jsonify({
                    'success': False,
                    'message': f'Error saving settings: {str(e)}'
                }), 500

        @self.app.route('/api/computers', methods=['GET'])
        def get_computers():
            """Get list of all configured computers."""
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                computers = config.get('computers', [])
                return self.jsonify({'computers': computers}), 200
            except Exception as e:
                self.logger.error(f"Error getting computers: {e}")
                return self.jsonify({'error': str(e), 'computers': []}), 500

        @self.app.route('/api/computers', methods=['POST'])
        def add_computer():
            """Add a new computer to monitor."""
            try:
                data = request.get_json()
                
                if not data.get('name'):
                    return self.jsonify({
                        'success': False,
                        'message': 'Computer name is required'
                    }), 400
                
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if 'computers' not in config:
                    config['computers'] = []
                
                # Generate unique ID
                existing_ids = {c.get('id') for c in config['computers']}
                new_id = f"computer-{len(config['computers']) + 1}"
                counter = 1
                while new_id in existing_ids:
                    counter += 1
                    new_id = f"computer-{counter}"
                
                new_computer = {
                    'id': new_id,
                    'name': data['name'],
                    'enabled': data.get('enabled', True)
                }
                
                config['computers'].append(new_computer)
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.logger.info(f"Added computer: {new_computer['name']} ({new_id})")
                
                # Reinitialize computers in monitor
                if hasattr(self, 'monitor_ref') and self.monitor_ref:
                    self.monitor_ref._initialize_computers()
                
                return self.jsonify({
                    'success': True,
                    'message': 'Computer added successfully',
                    'computer': new_computer
                }), 201
                
            except Exception as e:
                self.logger.error(f"Error adding computer: {e}")
                return self.jsonify({
                    'success': False,
                    'message': f'Error adding computer: {str(e)}'
                }), 500

        @self.app.route('/api/computers/<computer_id>', methods=['PUT'])
        def update_computer(computer_id):
            """Update a computer's configuration."""
            try:
                data = request.get_json()
                
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                computers = config.get('computers', [])
                computer = next((c for c in computers if c.get('id') == computer_id), None)
                
                if not computer:
                    return self.jsonify({
                        'success': False,
                        'message': 'Computer not found'
                    }), 404
                
                if 'name' in data:
                    computer['name'] = data['name']
                if 'enabled' in data:
                    computer['enabled'] = data['enabled']
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.logger.info(f"Updated computer: {computer['name']} ({computer_id})")
                
                # Reinitialize computers in monitor
                if hasattr(self, 'monitor_ref') and self.monitor_ref:
                    self.monitor_ref._initialize_computers()
                
                return self.jsonify({
                    'success': True,
                    'message': 'Computer updated successfully',
                    'computer': computer
                }), 200
                
            except Exception as e:
                self.logger.error(f"Error updating computer: {e}")
                return self.jsonify({
                    'success': False,
                    'message': f'Error updating computer: {str(e)}'
                }), 500

        @self.app.route('/api/computers/<computer_id>', methods=['DELETE'])
        def delete_computer(computer_id):
            """Delete a computer from monitoring."""
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                computers = config.get('computers', [])
                original_count = len(computers)
                
                config['computers'] = [c for c in computers if c.get('id') != computer_id]
                
                if len(config['computers']) == original_count:
                    return self.jsonify({
                        'success': False,
                        'message': 'Computer not found'
                    }), 404
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.logger.info(f"Deleted computer: {computer_id}")
                
                # Reinitialize computers in monitor
                if hasattr(self, 'monitor_ref') and self.monitor_ref:
                    self.monitor_ref._initialize_computers()
                
                return self.jsonify({
                    'success': True,
                    'message': 'Computer deleted successfully'
                }), 200
                
            except Exception as e:
                self.logger.error(f"Error deleting computer: {e}")
                return self.jsonify({
                    'success': False,
                    'message': f'Error deleting computer: {str(e)}'
                }), 500

        @self.app.route('/api/computers/<computer_id>/power', methods=['POST'])
        def toggle_computer_power(computer_id):
            """Manually toggle computer power state."""
            try:
                data = request.get_json()
                action = data.get('action')  # 'on' or 'off'
                
                if action not in ('on', 'off'):
                    return self.jsonify({
                        'success': False,
                        'message': 'Invalid action. Must be "on" or "off"'
                    }), 400
                
                # Update monitor's computer state
                if hasattr(self, 'monitor_ref') and self.monitor_ref:
                    if computer_id in self.monitor_ref.computers:
                        comp = self.monitor_ref.computers[computer_id]
                        comp['is_on'] = (action == 'on')
                        comp['last_action'] = action
                        comp['action_time'] = datetime.now().isoformat()
                        
                        self.logger.info(f"Manual power control: {comp['name']} - turning {action}")
                        
                        # Send ntfy notification
                        emoji = "⏻️" if action == 'on' else "⏼"
                        title = f"{emoji} Power {'On' if action == 'on' else 'Off'}"
                        self.monitor_ref._send_ntfy_notification(
                            title,
                            f"Manual control: {comp['name']} powered {action}",
                            priority="default"
                        )
                        
                        return self.jsonify({
                            'success': True,
                            'message': f'Computer powered {action} successfully',
                            'computer': comp
                        }), 200
                    else:
                        return self.jsonify({
                            'success': False,
                            'message': 'Computer not found'
                        }), 404
                else:
                    return self.jsonify({
                        'success': False,
                        'message': 'Monitor not available'
                    }), 500
            except Exception as e:
                self.logger.error(f"Error toggling computer power: {e}")
                return self.jsonify({
                    'success': False,
                    'message': f'Error toggling power: {str(e)}'
                }), 500

    def _get_weather_data(self) -> Dict:
        """Fetch current weather data."""
        try:
            # Load config fresh to get latest settings
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            if not config.get('api_key') or not config.get('latitude') or not config.get('longitude'):
                return {
                    'error': 'Configuration required',
                    'message': 'Please configure API key and location in settings'
                }
            
            import requests
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': config.get('latitude'),
                'lon': config.get('longitude'),
                'appid': config.get('api_key'),
                'units': config.get('units', 'metric')
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
            # Load config fresh to get latest settings
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            if not config.get('api_key') or not config.get('latitude') or not config.get('longitude'):
                return {
                    'error': 'Configuration required',
                    'forecasts': []
                }
            
            import requests
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': config.get('latitude'),
                'lon': config.get('longitude'),
                'appid': config.get('api_key'),
                'units': config.get('units', 'metric')
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
            return {'error': str(e), 'forecasts': []}

    def _get_device_status(self) -> Dict:
        """Get device monitoring status for all computers."""
        try:
            with open('weather_shield.log', 'r') as f:
                lines = f.readlines()
                last_check = lines[-1] if lines else 'Never'
        except FileNotFoundError:
            last_check = 'Never'

        # Get computer statuses from the monitor if available
        computers = []
        if hasattr(self, 'monitor_ref') and self.monitor_ref:
            for comp_id, comp_data in self.monitor_ref.computers.items():
                computers.append({
                    'id': comp_id,
                    'name': comp_data['name'],
                    'enabled': comp_data['enabled'],
                    'is_on': comp_data['is_on'],
                    'last_action': comp_data['last_action'],
                    'action_time': comp_data.get('action_time')
                })
        
        return {
            'status': 'running',
            'last_check': last_check,
            'is_monitoring': True,
            'computers': computers
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
            # Pass monitor reference to dashboard for accessing computer status
            self.dashboard.monitor_ref = self.monitor
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
