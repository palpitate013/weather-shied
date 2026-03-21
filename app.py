#!/usr/bin/env python3
"""
Weather Shield Web Dashboard
A Flask-based web interface for Weather Shield monitoring.
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests
from pathlib import Path

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
CONFIG_FILE = 'config.json'
LOG_FILE = 'weather_monitor.log'

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
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def get_weather_data(self):
        """Fetch current weather data."""
        if not self.config.get('api_key'):
            return {'error': 'API key not configured'}
        
        try:
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
            
            self.current_weather = {
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
            
            return self.current_weather
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_forecast_data(self):
        """Fetch forecast data."""
        if not self.config.get('api_key'):
            return {'error': 'API key not configured'}
        
        try:
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
            
            # Get next 4 forecasts (3-hour intervals)
            forecasts = []
            for item in data['list'][:4]:
                forecasts.append({
                    'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'].title(),
                    'main': item['weather'][0]['main'],
                    'wind_speed': item['wind']['speed']
                })
            
            return forecasts
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_device_status(self):
        """Parse logs to get device status."""
        if not os.path.exists(LOG_FILE):
            return {
                'status': 'idle',
                'last_action': 'none',
                'last_check': 'never',
                'is_bad_weather': False
            }
        
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return {
                    'status': 'idle',
                    'last_action': 'none',
                    'last_check': 'never',
                    'is_bad_weather': False
                }
            
            # Get last few lines
            last_lines = lines[-10:]
            
            status = {
                'status': 'monitoring',
                'last_action': 'none',
                'last_check': 'unknown',
                'is_bad_weather': False
            }
            
            for line in reversed(last_lines):
                if 'shutdown' in line.lower():
                    status['last_action'] = 'shutdown'
                    status['is_bad_weather'] = True
                    break
                elif 'boot' in line.lower() or 'wake' in line.lower():
                    status['last_action'] = 'boot'
                    status['is_bad_weather'] = False
                    break
            
            if lines:
                last_line = lines[-1]
                try:
                    status['last_check'] = last_line.split(' - ')[0]
                except:
                    status['last_check'] = 'unknown'
            
            return status
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_action': 'none',
                'last_check': 'never',
                'is_bad_weather': False
            }

dashboard = WeatherShieldDashboard()

@app.route('/')
def index():
    """Render main dashboard."""
    return render_template('index.html')

@app.route('/api/weather')
def api_weather():
    """Get current weather data."""
    return jsonify(dashboard.get_weather_data())

@app.route('/api/forecast')
def api_forecast():
    """Get forecast data."""
    return jsonify(dashboard.get_forecast_data())

@app.route('/api/device-status')
def api_device_status():
    """Get device status."""
    return jsonify(dashboard.get_device_status())

@app.route('/api/config')
def api_config():
    """Get public configuration."""
    return jsonify({
        'location': f"{dashboard.config.get('latitude')}, {dashboard.config.get('longitude')}",
        'check_interval': dashboard.config.get('check_interval', 300),
        'forecast_minutes': dashboard.config.get('forecast_minutes', 30),
        'units': dashboard.config.get('units', 'metric')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
