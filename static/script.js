/**
 * Weather Shield Dashboard - JavaScript
 * Real-time weather monitoring interface
 */

// Bad weather conditions that trigger alerts
const BAD_WEATHER_CONDITIONS = {
    'Thunderstorm': true,
    'Tornado': true,
    'Squall': true,
    'Hurricane': true,
    'Heavy Rain': true,
    'Extreme Rain': true,
    'Freezing Rain': true,
    'Heavy Snow': true,
    'Blizzard': true,
    'Heavy Sleet': true,
    'Hail': true,
    'Dust': true,
    'Dust Whirls': true,
    'Fog': true,
    'Mist': true,
    'Drizzle': true,
    'Rain': true,
    'Snow': true,
    'Smoke': true,
    'Ash': true
};

const BAD_WEATHER_CODES = new Set([
    200, 201, 202, 210, 211, 212, 221, 230, 231, 232, // Thunderstorm
    300, 301, 302, 310, 311, 312, 313, 314, 321,     // Drizzle
    500, 501, 502, 503, 504, 511, 520, 521, 522, 531, // Rain
    600, 601, 602, 610, 611, 612, 613, 614, 615, 616, 620, 621, 622, // Snow
    701, 711, 721, 731, 741, 751, 761, 762, 771, 781  // Atmosphere
]);

class WeatherShieldDashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.init();
    }

    init() {
        console.log('Initializing Weather Shield Dashboard...');
        this.startAutoUpdate();
        this.update();
    }

    startAutoUpdate() {
        setInterval(() => this.update(), this.updateInterval);
    }

    update() {
        this.updateWeather();
        this.updateForecast();
        this.updateDeviceStatus();
        this.updateConfig();
        this.updateTime();
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('updateTime').textContent = timeString;
    }

    async updateWeather() {
        try {
            const response = await fetch('/api/weather');
            const data = await response.json();

            if (data.error) {
                console.error('Weather error:', data.error);
                this.showWeatherError(data.error);
                return;
            }

            this.renderWeather(data);
        } catch (error) {
            console.error('Failed to fetch weather:', error);
            this.showWeatherError('Failed to fetch weather data');
        }
    }

    async updateForecast() {
        try {
            const response = await fetch('/api/forecast');
            const data = await response.json();

            if (data.error) {
                console.error('Forecast error:', data.error);
                return;
            }

            this.renderForecast(data);
        } catch (error) {
            console.error('Failed to fetch forecast:', error);
        }
    }

    async updateDeviceStatus() {
        try {
            const response = await fetch('/api/device-status');
            const data = await response.json();

            this.renderDeviceStatus(data);
        } catch (error) {
            console.error('Failed to fetch device status:', error);
        }
    }

    async updateConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();

            this.renderConfig(data);
        } catch (error) {
            console.error('Failed to fetch config:', error);
        }
    }

    renderWeather(weather) {
        // Temperature
        document.getElementById('temperature').textContent = 
            Math.round(weather.temperature);

        // Description
        document.getElementById('weatherDescription').textContent = 
            weather.description;

        // Location
        document.getElementById('location').textContent = 
            weather.location;

        // Feels like
        document.getElementById('feelsLike').textContent = 
            Math.round(weather.feels_like) + '°';

        // Humidity
        document.getElementById('humidity').textContent = 
            weather.humidity + '%';

        // Wind speed
        document.getElementById('windSpeed').textContent = 
            Math.round(weather.wind_speed * 10) / 10 + ' m/s';

        // Pressure
        document.getElementById('pressure').textContent = 
            weather.pressure + ' hPa';
    }

    renderForecast(forecasts) {
        const container = document.getElementById('forecastContainer');

        if (!forecasts || forecasts.length === 0) {
            container.innerHTML = '<div class="forecast-loading">No forecast data available</div>';
            return;
        }

        container.innerHTML = forecasts.map(forecast => `
            <div class="forecast-item">
                <div class="forecast-time">${forecast.time}</div>
                <div class="forecast-temp">${Math.round(forecast.temperature)}°</div>
                <div class="forecast-description">${forecast.description}</div>
                <div class="forecast-wind">💨 ${Math.round(forecast.wind_speed * 10) / 10} m/s</div>
            </div>
        `).join('');
    }

    renderDeviceStatus(status) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const deviceStatus = document.getElementById('deviceStatus');
        const lastAction = document.getElementById('lastAction');
        const weatherAlert = document.getElementById('weatherAlert');
        const lastCheck = document.getElementById('lastCheck');

        // Update status dot and text
        statusDot.className = 'status-dot';
        if (status.status === 'error') {
            statusDot.classList.add('error');
            statusText.textContent = 'Error';
        } else if (status.is_bad_weather) {
            statusDot.classList.add('alert');
            statusText.textContent = 'Bad Weather Alert';
        } else {
            statusDot.classList.add('monitoring');
            statusText.textContent = 'Monitoring';
        }

        // Device status
        deviceStatus.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);

        // Last action
        if (status.last_action === 'shutdown') {
            lastAction.textContent = '🔴 Shutdown';
            lastAction.classList.add('shutdown');
            lastAction.classList.remove('boot');
        } else if (status.last_action === 'boot') {
            lastAction.textContent = '🟢 Boot';
            lastAction.classList.add('boot');
            lastAction.classList.remove('shutdown');
        } else {
            lastAction.textContent = '⚪ None';
            lastAction.classList.remove('shutdown', 'boot');
        }

        // Weather alert
        if (status.is_bad_weather) {
            weatherAlert.textContent = '🔴 Bad Weather';
            weatherAlert.classList.add('danger');
            weatherAlert.classList.remove('warning');
        } else {
            weatherAlert.textContent = '🟢 Clear';
            weatherAlert.classList.add('warning');
            weatherAlert.classList.remove('danger');
        }

        // Last check
        lastCheck.textContent = status.last_check || '--';
    }

    renderConfig(config) {
        const container = document.getElementById('configContent');

        container.innerHTML = `
            <div class="config-item">
                <span class="config-label">Location</span>
                <span class="config-value">${config.location || '--'}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Check Interval</span>
                <span class="config-value">${config.check_interval || '--'} sec</span>
            </div>
            <div class="config-item">
                <span class="config-label">Forecast Window</span>
                <span class="config-value">${config.forecast_minutes || '--'} min</span>
            </div>
            <div class="config-item">
                <span class="config-label">Temperature Units</span>
                <span class="config-value">${config.units === 'metric' ? '°C' : '°F'}</span>
            </div>
        `;
    }

    showWeatherError(error) {
        const errorMsg = String(error || 'Error');
        
        if (errorMsg.includes('Configuration required')) {
            document.getElementById('temperature').textContent = '⚙️';
            document.getElementById('weatherDescription').textContent = 'Configuration Required';
            document.getElementById('location').textContent = 'Click ⚙️ to configure your settings';
        } else {
            document.getElementById('temperature').textContent = '!';
            document.getElementById('weatherDescription').textContent = 'Error';
            document.getElementById('location').textContent = errorMsg;
        }
    }
}

// Settings Modal Functions
function openSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.add('active');
    loadSettingsForm();
}

function closeSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.remove('active');
    clearSettingsMessage();
}

function loadSettingsForm() {
    // Fetch current config and populate form
    fetch('/api/config')
        .then(response => response.json())
        .then(config => {
            document.getElementById('apiKey').value = config.api_key || '';
            document.getElementById('latitude').value = config.latitude || '';
            document.getElementById('longitude').value = config.longitude || '';
            document.getElementById('units').value = config.units || 'metric';
            document.getElementById('checkInterval').value = config.check_interval || '300';
            document.getElementById('forecastMinutes').value = config.forecast_minutes || '30';
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showSettingsMessage('Error loading settings', 'error');
        });
}

function handleSettingsSubmit(event) {
    event.preventDefault();
    
    const settings = {
        api_key: document.getElementById('apiKey').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        units: document.getElementById('units').value,
        check_interval: parseInt(document.getElementById('checkInterval').value),
        forecast_minutes: parseInt(document.getElementById('forecastMinutes').value)
    };

    // Validate required fields
    if (!settings.api_key || !settings.latitude || !settings.longitude) {
        showSettingsMessage('Please fill in all required fields', 'error');
        return;
    }

    // Validate coordinates
    if (settings.latitude < -90 || settings.latitude > 90) {
        showSettingsMessage('Latitude must be between -90 and 90', 'error');
        return;
    }
    if (settings.longitude < -180 || settings.longitude > 180) {
        showSettingsMessage('Longitude must be between -180 and 180', 'error');
        return;
    }

    // Show loading state
    showSettingsMessage('Saving settings...', 'success');
    
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSettingsMessage('Settings saved successfully! Dashboard will refresh...', 'success');
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showSettingsMessage(data.message || 'Error saving settings', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showSettingsMessage('Error saving settings: ' + error.message, 'error');
    });
}

function showSettingsMessage(message, type) {
    const messageEl = document.getElementById('settingsMessage');
    messageEl.textContent = message;
    messageEl.className = 'settings-message ' + type;
}

function clearSettingsMessage() {
    const messageEl = document.getElementById('settingsMessage');
    messageEl.textContent = '';
    messageEl.className = 'settings-message';
}

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    const modal = document.getElementById('settingsModal');
    if (event.target === modal) {
        closeSettings();
    }
});

// Attach form submission handler
document.addEventListener('DOMContentLoaded', () => {
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', handleSettingsSubmit);
    }
});

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherShieldDashboard();
});
