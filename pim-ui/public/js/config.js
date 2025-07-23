// Configuration management for PIM UI
let API_BASE_URL = 'http://localhost:8000';

// Load configuration from server
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        API_BASE_URL = config.apiBaseUrl;
        console.log('Loaded configuration:', config);
    } catch (error) {
        console.error('Failed to load configuration, using default:', error);
    }
}

// Initialize configuration on page load
window.addEventListener('DOMContentLoaded', loadConfig);