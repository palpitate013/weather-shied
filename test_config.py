#!/usr/bin/env python3
"""
Test script to verify Weather Shield configuration and API connectivity.
"""

import json
import sys
import requests
from pathlib import Path


def test_configuration():
    """Test if config.json exists and is valid."""
    print("=" * 60)
    print("Testing Configuration")
    print("=" * 60)

    if not Path('config.json').exists():
        print("❌ config.json not found")
        return False

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        required_keys = ['api_key', 'latitude', 'longitude']
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            print(f"❌ Missing required keys: {missing_keys}")
            return False

        if config['api_key'] == 'YOUR_OPENWEATHER_API_KEY_HERE':
            print("❌ API key not configured. Please update config.json")
            return False

        print("✓ config.json is valid")
        print(f"  - Location: {config['latitude']}, {config['longitude']}")
        print(f"  - Units: {config.get('units', 'metric')}")
        print(f"  - Check interval: {config.get('check_interval', 300)}s")
        print(f"  - Forecast window: {config.get('forecast_minutes', 30)}min")
        return True

    except json.JSONDecodeError:
        print("❌ config.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False


def test_api_key(config):
    """Test if API key is valid."""
    print("\n" + "=" * 60)
    print("Testing API Key")
    print("=" * 60)

    api_key = config['api_key']
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': config['latitude'],
        'lon': config['longitude'],
        'appid': api_key,
        'units': config.get('units', 'metric')
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            print("✓ API key is valid")
            data = response.json()

            if 'weather' in data:
                weather = data['weather'][0]
                print(f"  - Current weather: {weather['main']} ({weather['description']})")

            if 'main' in data:
                print(f"  - Temperature: {data['main']['temp']}°")
                print(f"  - Feels like: {data['main']['feels_like']}°")

            return True

        elif response.status_code == 401:
            print("❌ API key is invalid or unauthorized")
            return False

        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ API request timed out")
        return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Check your internet connection.")
        return False

    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False


def test_forecast_api(config):
    """Test if forecast API works."""
    print("\n" + "=" * 60)
    print("Testing Forecast API")
    print("=" * 60)

    api_key = config['api_key']
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': config['latitude'],
        'lon': config['longitude'],
        'appid': api_key,
        'units': config.get('units', 'metric')
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            forecast_count = len(data.get('list', []))
            print(f"✓ Forecast API is working")
            print(f"  - Forecast points available: {forecast_count}")
            if forecast_count > 0:
                print(f"  - First forecast: {data['list'][0]['weather'][0]['main']}")
            return True

        else:
            print(f"❌ Forecast API failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing forecast API: {e}")
        return False


def main():
    """Run all tests."""
    print("\n🌦️  Weather Shield - Configuration Test\n")

    # Test configuration
    if not test_configuration():
        print("\n❌ Configuration test failed")
        sys.exit(1)

    # Load config for API tests
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"\n❌ Failed to load config: {e}")
        sys.exit(1)

    # Test API
    if not test_api_key(config):
        print("\n❌ API test failed")
        sys.exit(1)

    # Test Forecast API
    if not test_forecast_api(config):
        print("\n❌ Forecast API test failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nYou can now run: python weather_monitor.py")
    print()


if __name__ == '__main__':
    main()
