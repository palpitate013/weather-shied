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
        loadComputers();
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

// Computer Management Functions
function openComputerModal() {
    const modal = document.getElementById('computerModal');
    modal.classList.add('active');
    document.getElementById('computerForm').reset();
    clearComputerMessage();
}

function closeComputerModal() {
    const modal = document.getElementById('computerModal');
    modal.classList.remove('active');
    clearComputerMessage();
}

function handleComputerFormSubmit(event) {
    event.preventDefault();
    
    const computerData = {
        name: document.getElementById('computerName').value,
        enabled: document.getElementById('computerEnabled').checked
    };

    if (!computerData.name.trim()) {
        showComputerMessage('Computer name is required', 'error');
        return;
    }

    showComputerMessage('Adding computer...', 'success');
    
    fetch('/api/computers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(computerData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showComputerMessage('Computer added successfully!', 'success');
            setTimeout(() => {
                closeComputerModal();
                loadComputers();
            }, 1000);
        } else {
            showComputerMessage(data.message || 'Error adding computer', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding computer:', error);
        showComputerMessage('Error adding computer: ' + error.message, 'error');
    });
}

function loadComputers() {
    fetch('/api/computers')
        .then(response => response.json())
        .then(data => {
            renderComputers(data.computers || []);
        })
        .catch(error => {
            console.error('Error loading computers:', error);
            renderComputers([]);
        });
}

function renderComputers(computers) {
    const container = document.getElementById('computersContent');
    
    if (!computers || computers.length === 0) {
        container.innerHTML = '<div class="empty-message">No computers configured. Click "Add" to add one.</div>';
        return;
    }

    // Also fetch current device status to get real-time computer states
    fetch('/api/device-status')
        .then(response => response.json())
        .then(status => {
            const computerStates = {};
            if (status.computers) {
                status.computers.forEach(comp => {
                    computerStates[comp.id] = comp;
                });
            }

            let html = '';
            computers.forEach(comp => {
                const state = computerStates[comp.id] || {};
                const isOn = state.is_on || false;
                const isEnabled = comp.enabled !== false;
                const statusClass = !isEnabled ? 'disabled' : (isOn ? 'on' : 'off');
                const statusText = !isEnabled ? 'Disabled' : (isOn ? 'Online' : 'Offline');
                const statusEmoji = !isEnabled ? '⊘' : (isOn ? '🟢' : '🔴');

                html += `
                    <div class="computer-item">
                        <div class="computer-info">
                            <div class="computer-status ${statusClass}">
                                <div class="status-indicator-small ${statusClass}"></div>
                                ${statusEmoji} ${statusText}
                            </div>
                            <div class="computer-details">
                                <div class="computer-name">${escapeHtml(comp.name)}</div>
                                <div class="computer-meta">
                                    ${state.last_action ? `Last action: ${state.last_action}` : 'No actions yet'}
                                    ${state.action_time ? ` (${new Date(state.action_time).toLocaleTimeString()})` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="computer-actions">
                            <button class="btn-icon" onclick="editComputer('${comp.id}', '${escapeHtml(comp.name)}', ${comp.enabled})" title="Edit">✏️</button>
                            <button class="btn-icon danger" onclick="deleteComputer('${comp.id}', '${escapeHtml(comp.name)}')" title="Delete">🗑️</button>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Error fetching device status:', error);
            // Render computers without live state
            let html = '';
            computers.forEach(comp => {
                html += `
                    <div class="computer-item">
                        <div class="computer-info">
                            <div class="computer-status disabled">
                                <div class="status-indicator-small disabled"></div>
                                ? Unknown
                            </div>
                            <div class="computer-details">
                                <div class="computer-name">${escapeHtml(comp.name)}</div>
                            </div>
                        </div>
                        <div class="computer-actions">
                            <button class="btn-icon" onclick="editComputer('${comp.id}', '${escapeHtml(comp.name)}', ${comp.enabled})" title="Edit">✏️</button>
                            <button class="btn-icon danger" onclick="deleteComputer('${comp.id}', '${escapeHtml(comp.name)}')" title="Delete">🗑️</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        });
}

function editComputer(computerId, computerName, isEnabled) {
    const newName = prompt('Edit computer name:', computerName);
    if (newName === null) return;
    
    if (!newName.trim()) {
        alert('Computer name cannot be empty');
        return;
    }

    fetch(`/api/computers/${computerId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: newName,
            enabled: isEnabled
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadComputers();
        } else {
            alert('Error updating computer: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error updating computer:', error);
        alert('Error updating computer');
    });
}

function deleteComputer(computerId, computerName) {
    if (!confirm(`Delete "${computerName}"? This cannot be undone.`)) {
        return;
    }

    fetch(`/api/computers/${computerId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadComputers();
        } else {
            alert('Error deleting computer: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error deleting computer:', error);
        alert('Error deleting computer');
    });
}

function showComputerMessage(message, type) {
    const messageEl = document.getElementById('computerMessage');
    messageEl.textContent = message;
    messageEl.className = 'settings-message ' + type;
}

function clearComputerMessage() {
    const messageEl = document.getElementById('computerMessage');
    messageEl.textContent = '';
    messageEl.className = 'settings-message';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    const modal = document.getElementById('settingsModal');
    if (event.target === modal) {
        closeSettings();
    }
});

// Close computer modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('computerModal');
    if (event.target === modal) {
        closeComputerModal();
    }
});

// Attach form submission handler
document.addEventListener('DOMContentLoaded', () => {
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', handleSettingsSubmit);
    }

    const computerForm = document.getElementById('computerForm');
    if (computerForm) {
        computerForm.addEventListener('submit', handleComputerFormSubmit);
    }
});

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherShieldDashboard();
    loadComputers();
});
