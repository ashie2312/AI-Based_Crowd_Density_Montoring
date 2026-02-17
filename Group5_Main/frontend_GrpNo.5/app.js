// Main Application JavaScript
// This file handles UI interactions and connects to the backend API

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication for protected pages
    const currentPage = document.body.getAttribute('data-page');
    const protectedPages = ['dashboard', 'analytics', 'upload-connect', 'settings'];
    
    if (protectedPages.includes(currentPage)) {
        if (!AuthAPI.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }
    }

    // Initialize page-specific functionality
    switch(currentPage) {
        case 'login':
            initLoginPage();
            break;
        case 'signup':
            initSignupPage();
            break;
        case 'dashboard':
            initDashboardPage();
            break;
        case 'analytics':
            initAnalyticsPage();
            break;
        case 'upload-connect':
            initUploadPage();
            break;
    }

    // Initialize common functionality
    initCommonHandlers();
    
    // Close video/image preview buttons
    document.querySelectorAll('[data-action="close-video"]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('video-player-section')?.classList.add('hidden');
            resetDropzone();
        });
    });
    
    document.querySelectorAll('[data-action="close-image"]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('image-preview-section')?.classList.add('hidden');
            resetDropzone();
        });
    });
});

// Common event handlers
function initCommonHandlers() {
    // Sign out button
    document.querySelectorAll('[data-action="signout"]').forEach(btn => {
        btn.addEventListener('click', () => {
            AuthAPI.logout();
        });
    });
}

// Login Page
function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const submitBtn = loginForm.querySelector('[data-action="login"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Signing in...';
            
            const result = await AuthAPI.login(email, password);
            
            if (result && result.ok) {
                window.location.href = 'dashboard.html';
            } else {
                alert(result?.data?.error || 'Login failed. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign in';
            }
        });
    }
}

// Signup Page
function initSignupPage() {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            if (password.length < 8) {
                alert('Password must be at least 8 characters');
                return;
            }
            
            const submitBtn = signupForm.querySelector('[data-action="signup"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating account...';
            
            const result = await AuthAPI.register(email, password, name);
            
            if (result && result.ok) {
                window.location.href = 'dashboard.html';
            } else {
                alert(result?.data?.error || 'Registration failed. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        });
    }
}

// Dashboard Page
function initDashboardPage() {
    loadDashboardMetrics();
    loadHeatmap();
    loadRecentAlerts();
    loadCameras();
    
    // Refresh every 30 seconds
    setInterval(() => {
        loadDashboardMetrics();
        loadHeatmap();
        loadRecentAlerts();
    }, 30000);
}

async function loadDashboardMetrics() {
    const result = await DashboardAPI.getMetrics(24);
    
    if (result && result.ok) {
        const data = result.data;
        
        // Update metrics
        updateMetric('metric-total-attendance', data.total_attendance.toLocaleString());
        updateMetricDelta('metric-total-attendance-delta', data.attendance_delta);
        
        updateMetric('metric-avg-density', `${data.avg_density}%`);
        updateMetricDelta('metric-avg-density-delta', data.density_delta);
        
        updateMetric('metric-active-alerts', data.active_alerts);
        updateMetric('metric-active-cameras', data.active_cameras);
        
        const statusEl = document.getElementById('metric-active-cameras-status');
        if (statusEl) {
            statusEl.textContent = data.cameras_status;
        }
    }
}

function updateMetric(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateMetricDelta(id, delta) {
    const el = document.getElementById(id);
    if (el) {
        const sign = delta >= 0 ? '+' : '';
        el.textContent = `${sign}${delta.toFixed(1)}%`;
    }
}

async function loadHeatmap() {
    const result = await DashboardAPI.getHeatmap();
    
    if (result && result.ok) {
        const zones = result.data.zones;
        // Update heatmap visualization (simplified - you may want to enhance this)
        const updatedEl = document.getElementById('heatmap-updated');
        if (updatedEl) {
            updatedEl.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
        }
    }
}

async function loadRecentAlerts() {
    const result = await DashboardAPI.getAlerts(4);
    
    if (result && result.ok) {
        const alerts = result.data.alerts;
        const container = document.getElementById('recent-alerts-list');
        
        if (container && alerts.length > 0) {
            container.innerHTML = alerts.map(alert => `
                <div class="rounded-xl bg-slate-900/60 p-4" data-alert-id="alert-${alert.id}">
                    <p class="text-sm text-white" data-alert-title>${alert.message}</p>
                    <p class="text-xs text-${getSeverityColor(alert.severity)}" data-alert-level>${alert.severity.toUpperCase()}</p>
                    <p class="text-xs text-slate-400" data-alert-time>${formatTimeAgo(alert.timestamp)}</p>
                </div>
            `).join('');
        }
    }
}

function getSeverityColor(severity) {
    const colors = {
        'critical': 'rose-400',
        'warning': 'amber-400',
        'info': 'blue-300',
        'success': 'emerald-300'
    };
    return colors[severity] || 'slate-400';
}

function formatTimeAgo(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

async function loadCameras() {
    const result = await DashboardAPI.getCameras();
    
    if (result && result.ok) {
        const cameras = result.data.cameras;
        // Update camera cards (simplified - you may want to enhance this)
        console.log('Cameras loaded:', cameras);
    }
}

// Analytics Page
function initAnalyticsPage() {
    loadAnalyticsData();
    
    // Export CSV button
    document.querySelectorAll('[data-action="export-csv"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.textContent = 'Exporting...';
            await AnalyticsAPI.exportCSV(24);
            btn.disabled = false;
            btn.textContent = 'Export CSV';
        });
    });
}

async function loadAnalyticsData() {
    // Load zone stats
    const statsResult = await AnalyticsAPI.getZoneStats(24);
    
    if (statsResult && statsResult.ok) {
        const zones = statsResult.data.zones;
        const tbody = document.getElementById('zone-stats-body');
        
        if (tbody) {
            tbody.innerHTML = zones.map(zone => `
                <tr>
                    <td class="text-white">${zone.zone_name}</td>
                    <td>${zone.avg_density}%</td>
                    <td>${zone.peak_time}</td>
                    <td>${zone.alerts_triggered}</td>
                    <td><span class="status-pill status-${zone.status.toLowerCase()}">${zone.status}</span></td>
                </tr>
            `).join('');
        }
    }
    
    // Load density trends (for charts - you may want to integrate a charting library)
    const trendsResult = await AnalyticsAPI.getDensityTrends(24);
    if (trendsResult && trendsResult.ok) {
        console.log('Density trends:', trendsResult.data.trends);
        // You can integrate Chart.js or another library here
    }
}

// Upload Page
function initUploadPage() {
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*,video/*';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);
    
    // Browse files button
    document.querySelectorAll('[data-action="browse-files"]').forEach(btn => {
        btn.addEventListener('click', () => {
            fileInput.click();
        });
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // Drag and drop
    if (dropzone) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });
        
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('drag-over');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length > 0) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }
}

async function handleFileUpload(file) {
    const isVideo = file.type.startsWith('video/');
    const isImage = file.type.startsWith('image/');
    
    if (!isVideo && !isImage) {
        alert('Please upload an image or video file');
        return;
    }
    
    // Hide previous previews
    document.getElementById('video-player-section')?.classList.add('hidden');
    document.getElementById('image-preview-section')?.classList.add('hidden');
    
    // Show loading state
    const dropzone = document.getElementById('upload-dropzone');
    if (dropzone) {
        dropzone.innerHTML = `
            <div class="flex flex-col items-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                <p class="text-white">Processing ${isVideo ? 'video' : 'image'}... Please wait.</p>
                <p class="text-xs text-slate-400 mt-2">${isVideo ? 'Video processing may take several minutes. Please do not close this page.' : 'This may take a few moments'}</p>
                <p class="text-xs text-slate-500 mt-1" id="processing-status">Uploading file...</p>
            </div>
        `;
    }
    
    try {
        let result;
        const statusEl = document.getElementById('processing-status');
        
        if (isImage) {
            if (statusEl) statusEl.textContent = 'Processing image with AI...';
            result = await UploadAPI.uploadImage(file);
        } else {
            if (statusEl) statusEl.textContent = 'Uploading video...';
            // For videos, use a longer timeout and show progress
            if (statusEl) statusEl.textContent = 'Processing video with YOLOv8 AI... This may take several minutes.';
            result = await UploadAPI.uploadVideo(file, null, null, 600000); // 10 minute timeout
        }
        
        if (result && result.ok) {
            // Hide dropzone
            if (dropzone) {
                dropzone.style.display = 'none';
            }
            
            if (isVideo) {
                displayProcessedVideo(result.data);
            } else {
                displayProcessedImage(result.data);
            }
            
            // Reload dashboard if on dashboard page
            if (document.body.getAttribute('data-page') === 'dashboard') {
                loadDashboardMetrics();
            }
        } else {
            const errorMsg = result?.data?.error || result?.error || 'Failed to process file';
            console.error('Upload error:', result);
            alert(`Error: ${errorMsg}\n\nCheck the browser console (F12) for more details.`);
            resetDropzone();
        }
    } catch (error) {
        alert('Error uploading file: ' + error.message);
        resetDropzone();
    }
}

function displayProcessedVideo(data) {
    const videoSection = document.getElementById('video-player-section');
    const videoElement = document.getElementById('processed-video');
    const personCountEl = document.getElementById('video-person-count');
    const densityEl = document.getElementById('video-density');
    const statusEl = document.getElementById('video-status');
    
    if (!videoSection || !videoElement) return;
    
    // Get processed video URL
    let videoUrl = null;
    if (data.result?.processed_video_url) {
        // Ensure URL starts with /api/files/
        const url = data.result.processed_video_url.startsWith('/api/files/')
            ? data.result.processed_video_url
            : `/api/files/${data.result.processed_video_url}`;
        videoUrl = `http://localhost:5000${url}`;
    }
    
    // Update stats
    const personCount = data.result?.average_person_count || 0;
    const density = data.result?.average_density || 0;
    
    personCountEl.textContent = Math.round(personCount);
    densityEl.textContent = `${density.toFixed(1)}%`;
    
    // Show video section first
    videoSection.classList.remove('hidden');
    videoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    if (videoUrl) {
        console.log('Loading video from:', videoUrl);
        statusEl.textContent = 'Loading video...';
        statusEl.className = 'mt-2 text-sm font-semibold text-amber-300';
        
        const token = localStorage.getItem('auth_token');
        
        // Fetch video with authentication
        fetch(videoUrl, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            console.log('Video fetch response status:', response.status);
            if (!response.ok) {
                throw new Error(`Failed to load video: ${response.status} ${response.statusText}`);
            }
            return response.blob();
        })
        .then(blob => {
            console.log('Video blob received, size:', blob.size, 'bytes');
            if (blob.size === 0) {
                throw new Error('Video file is empty');
            }
            
            // Check if blob is actually a video
            if (!blob.type.startsWith('video/') && blob.type !== 'application/octet-stream') {
                console.warn('Unexpected blob type:', blob.type);
            }
            
            const blobUrl = URL.createObjectURL(blob);
            console.log('Created blob URL:', blobUrl);
            
            // Clear any previous error
            videoElement.innerHTML = '';
            
            // Set video source
            videoElement.src = blobUrl;
            videoElement.type = 'video/mp4';
            
            // Add event listeners for debugging
            videoElement.onloadedmetadata = () => {
                console.log('Video metadata loaded');
                console.log('Video duration:', videoElement.duration);
                console.log('Video dimensions:', videoElement.videoWidth, 'x', videoElement.videoHeight);
                statusEl.textContent = 'Ready to play';
                statusEl.className = 'mt-2 text-sm font-semibold text-emerald-300';
            };
            
            videoElement.oncanplay = () => {
                console.log('Video can play');
            };
            
            videoElement.onloadeddata = () => {
                console.log('Video data loaded');
            };
            
            videoElement.onerror = (e) => {
                console.error('Video element error:', e);
                console.error('Video error code:', videoElement.error?.code);
                console.error('Video error message:', videoElement.error?.message);
                const errorMsg = videoElement.error?.message || 'Unknown video error';
                statusEl.textContent = `Error: ${errorMsg}`;
                statusEl.className = 'mt-2 text-sm font-semibold text-rose-300';
            };
            
            // Try to load the video
            videoElement.load();
            
            // Force play attempt after a short delay
            setTimeout(() => {
                if (videoElement.readyState >= 2) {
                    console.log('Video is ready, attempting to play');
                    videoElement.play().catch(err => {
                        console.log('Auto-play prevented:', err);
                    });
                }
            }, 500);
        })
        .catch(error => {
            console.error('Error loading video:', error);
            statusEl.textContent = `Error: ${error.message}`;
            statusEl.className = 'mt-2 text-sm font-semibold text-rose-300';
            
            // Show error message in video element
            videoElement.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-white p-8">
                    <p class="text-lg mb-2">Error loading video</p>
                    <p class="text-sm text-slate-400">${error.message}</p>
                    <p class="text-xs text-slate-500 mt-4">Check browser console for details</p>
                </div>
            `;
        });
    } else {
        console.warn('No processed video URL provided');
        statusEl.textContent = 'Processing complete - Video file may not be available';
        statusEl.className = 'mt-2 text-sm font-semibold text-amber-300';
        
        // Show message in video element
        videoElement.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-white p-8">
                <p class="text-lg mb-2">Video processed successfully</p>
                <p class="text-sm text-slate-400">Processed video file is being generated</p>
                <p class="text-xs text-slate-500 mt-4">Check the backend logs for processing status</p>
            </div>
        `;
    }
}

function displayProcessedImage(data) {
    const imageSection = document.getElementById('image-preview-section');
    const imageElement = document.getElementById('processed-image');
    const personCountEl = document.getElementById('image-person-count');
    const densityEl = document.getElementById('image-density');
    
    if (!imageSection || !imageElement) return;
    
    // Get processed image URL
    const imageUrl = data.result?.processed_image_url 
        ? `http://localhost:5000${data.result.processed_image_url}`
        : null;
    
    if (imageUrl) {
        imageElement.src = imageUrl;
        
        // Update stats
        const personCount = data.result?.person_count || 0;
        const density = data.result?.density_percentage || 0;
        
        personCountEl.textContent = personCount;
        densityEl.textContent = `${density.toFixed(1)}%`;
        
        // Show image section
        imageSection.classList.remove('hidden');
        
        // Scroll to image
        imageSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function resetDropzone() {
    const dropzone = document.getElementById('upload-dropzone');
    if (dropzone) {
        dropzone.style.display = 'block';
        dropzone.innerHTML = `
            <div class="flex h-14 w-14 items-center justify-center rounded-full bg-slate-800/70">
                <svg aria-hidden="true" class="h-6 w-6 text-slate-300" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M4 16.5a4.5 4.5 0 0 1 .9-8.9 5 5 0 0 1 9.8-1.5h.2a4 4 0 0 1 0 8H13"></path>
                    <path d="M12 12v9"></path>
                    <path d="m16 16-4-4-4 4"></path>
                </svg>
            </div>
            <p class="mt-4 text-sm text-white">Drag & Drop files here</p>
            <p class="mt-1 text-xs text-slate-400">Support for MP4, AVI, JPG, PNG (Max 500MB)</p>
            <button class="action-btn mt-4" data-action="browse-files" type="button">Browse Files</button>
        `;
        // Re-initialize browse button
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            document.querySelectorAll('[data-action="browse-files"]').forEach(btn => {
                btn.addEventListener('click', () => fileInput.click());
            });
        }
    }
}
