// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Function to get current auth token
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// Update authToken variable
let authToken = getAuthToken();

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('auth_token');
            window.location.href = 'login.html';
            return null;
        }

        const data = await response.json();
        return { ok: response.ok, data, status: response.status };
    } catch (error) {
        console.error('API Request Error:', error);
        return { ok: false, error: error.message };
    }
}

// Authentication API
const AuthAPI = {
    async login(email, password) {
        const result = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (result && result.ok && result.data.access_token) {
            authToken = result.data.access_token;
            localStorage.setItem('auth_token', authToken);
            localStorage.setItem('user', JSON.stringify(result.data.user));
        }
        
        return result;
    },

    async register(email, password, name = '') {
        const result = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, name })
        });
        
        if (result && result.ok && result.data.access_token) {
            const token = result.data.access_token;
            authToken = token;
            localStorage.setItem('auth_token', token);
            localStorage.setItem('user', JSON.stringify(result.data.user));
        }
        
        return result;
    },

    logout() {
        authToken = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    getCurrentUser() {
        return JSON.parse(localStorage.getItem('user') || 'null');
    },

    isAuthenticated() {
        return !!authToken;
    }
};

// Dashboard API
const DashboardAPI = {
    async getMetrics(hours = 24) {
        return await apiRequest(`/dashboard/metrics?hours=${hours}`);
    },

    async getHeatmap() {
        return await apiRequest('/dashboard/heatmap');
    },

    async getAlerts(limit = 10) {
        return await apiRequest(`/dashboard/alerts?limit=${limit}`);
    },

    async getCameras() {
        return await apiRequest('/dashboard/cameras');
    }
};

// Analytics API
const AnalyticsAPI = {
    async getDensityTrends(hours = 24, zoneId = null) {
        let url = `/analytics/density-trends?hours=${hours}`;
        if (zoneId) url += `&zone_id=${zoneId}`;
        return await apiRequest(url);
    },

    async getZoneStats(hours = 24) {
        return await apiRequest(`/analytics/zone-stats?hours=${hours}`);
    },

    async exportCSV(hours = 24) {
        const result = await apiRequest(`/analytics/export?hours=${hours}`);
        if (result && result.ok) {
            // Download CSV
            const blob = new Blob([result.data.csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = result.data.filename;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        return result;
    }
};

// Upload API
const UploadAPI = {
    async uploadImage(file, zoneId = null, cameraId = null) {
        // Get fresh token from localStorage
        const token = localStorage.getItem('auth_token');
        if (!token) {
            window.location.href = 'login.html';
            return { ok: false, error: 'Not authenticated' };
        }

        const formData = new FormData();
        formData.append('file', file);
        if (zoneId) formData.append('zone_id', zoneId);
        if (cameraId) formData.append('camera_id', cameraId);

        const url = `${API_BASE_URL}/upload/image`;
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        // Don't set Content-Type - let browser set it with boundary for FormData

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData
            });

            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                window.location.href = 'login.html';
                return null;
            }

            const data = await response.json();
            return { ok: response.ok, data, status: response.status };
        } catch (error) {
            console.error('Upload Error:', error);
            return { ok: false, error: error.message };
        }
    },

    async uploadVideo(file, zoneId = null, cameraId = null, timeout = 600000) {
        // Get fresh token from localStorage
        const token = localStorage.getItem('auth_token');
        if (!token) {
            window.location.href = 'login.html';
            return { ok: false, error: 'Not authenticated' };
        }

        const formData = new FormData();
        formData.append('file', file);
        if (zoneId) formData.append('zone_id', zoneId);
        if (cameraId) formData.append('camera_id', cameraId);

        const url = `${API_BASE_URL}/upload/video`;
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        // Don't set Content-Type - let browser set it with boundary for FormData

        try {
            // Create AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);

            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                window.location.href = 'login.html';
                return null;
            }

            const data = await response.json();
            return { ok: response.ok, data, status: response.status };
        } catch (error) {
            console.error('Upload Error:', error);
            if (error.name === 'AbortError') {
                return { ok: false, error: 'Request timed out. Video processing is taking longer than expected. Please try a shorter video or wait and check back later.' };
            }
            if (error.message === 'Failed to fetch') {
                return { ok: false, error: 'Connection lost. The server may still be processing your video. Please wait a moment and refresh the page.' };
            }
            return { ok: false, error: error.message };
        }
    }
};

// Camera API
const CameraAPI = {
    async getCameras() {
        return await apiRequest('/cameras');
    },

    async createCamera(name, location, zone, streamUrl) {
        return await apiRequest('/cameras', {
            method: 'POST',
            body: JSON.stringify({ name, location, zone, stream_url: streamUrl, is_active: true })
        });
    }
};

// Zone API
const ZoneAPI = {
    async getZones() {
        return await apiRequest('/zones');
    },

    async createZone(name, description, maxCapacity, thresholdWarning, thresholdCritical) {
        return await apiRequest('/zones', {
            method: 'POST',
            body: JSON.stringify({
                name,
                description,
                max_capacity: maxCapacity,
                threshold_warning: thresholdWarning,
                threshold_critical: thresholdCritical
            })
        });
    }
};
