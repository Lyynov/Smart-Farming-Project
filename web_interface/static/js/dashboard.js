// Global variables
let moistureChart = null;
const refreshInterval = 10000; // Refresh data every 10 seconds
let lastRefreshTime = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeChart();
    refreshData();
    
    // Set interval for automatic refresh
    setInterval(refreshData, refreshInterval);
});

/**
 * Initialize the moisture trend chart
 */
function initializeChart() {
    const ctx = document.getElementById('moistureChart').getContext('2d');
    
    moistureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Node 1 Moisture',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Node 2 Moisture',
                    data: [],
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Moisture (%)'
                    }
                }
            }
        }
    });
}

/**
 * Refresh all dashboard data
 */
function refreshData() {
    // Fetch latest data
    fetch('/api/data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateDashboard(data);
            lastRefreshTime = new Date();
            updateLastRefreshTime();
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showNotification('Error', 'Failed to fetch latest data. Please check server connection.', 'error');
            
            // Mark server as offline
            updateServerStatus(false);
        });
    
    // Fetch historical data for chart
    fetch('/api/history?days=1')
        .then(response => response.json())
        .then(data => {
            updateMoistureChart(data);
        })
        .catch(error => {
            console.error('Error fetching historical data:', error);
        });
    
    // Fetch latest maturity data
    fetch('/api/maturity')
        .then(response => response.json())
        .then(data => {
            updateMaturityData(data);
        })
        .catch(error => {
            console.error('Error fetching maturity data:', error);
        });
}

/**
 * Update dashboard with latest data
 */
function updateDashboard(data) {
    // Update server status
    updateServerStatus(true);
    
    // Update soil moisture data
    const moistureData = data.soil_moisture || {};
    
    // Update Node 1
    if (moistureData.node1) {
        const node1 = moistureData.node1;
        document.getElementById('moisture1Value').textContent = `Moisture: ${node1.moisture.toFixed(1)}%`;
        document.getElementById('moisture1Progress').style.width = `${node1.moisture}%`;
        
        // Adjust color based on moisture level
        let progressColor = 'bg-danger';
        if (node1.moisture > 70) {
            progressColor = 'bg-success';
        } else if (node1.moisture > 30) {
            progressColor = 'bg-warning';
        }
        document.getElementById('moisture1Progress').className = `progress-bar ${progressColor}`;
        
        // Update valve status
        document.getElementById('valve1Status').textContent = `Valve: ${node1.valve ? 'ON' : 'OFF'}`;
        document.getElementById('valve1Status').className = node1.valve ? 'text-success' : 'text-secondary';
        
        // Update node status
        document.getElementById('node1Status').innerHTML = `<span class="badge bg-success">Online</span>`;
    } else {
        document.getElementById('node1Status').innerHTML = `<span class="badge bg-danger">Offline</span>`;
    }
    
    // Update Node 2
    if (moistureData.node2) {
        const node2 = moistureData.node2;
        document.getElementById('moisture2Value').textContent = `Moisture: ${node2.moisture.toFixed(1)}%`;
        document.getElementById('moisture2Progress').style.width = `${node2.moisture}%`;
        
        // Adjust color based on moisture level
        let progressColor = 'bg-danger';
        if (node2.moisture > 70) {
            progressColor = 'bg-success';
        } else if (node2.moisture > 30) {
            progressColor = 'bg-warning';
        }
        document.getElementById('moisture2Progress').className = `progress-bar ${progressColor}`;
        
        // Update valve status
        document.getElementById('valve2Status').textContent = `Valve: ${node2.valve ? 'ON' : 'OFF'}`;
        document.getElementById('valve2Status').className = node2.valve ? 'text-success' : 'text-secondary';
        
        // Update node status
        document.getElementById('node2Status').innerHTML = `<span class="badge bg-success">Online</span>`;
    } else {
        document.getElementById('node2Status').innerHTML = `<span class="badge bg-danger">Offline</span>`;
    }
}

/**
 * Update the moisture chart with historical data
 */
function updateMoistureChart(data) {
    if (!data || !data.soil_moisture) {
        return;
    }
    
    const moistureData = data.soil_moisture;
    const node1Data = moistureData.node1 || [];
    const node2Data = moistureData.node2 || [];
    
    // Build datasets
    const node1Values = [];
    const node2Values = [];
    const timeLabels = [];
    
    // Get data for last 24 hours, sampling at reasonable intervals
    const maxPoints = 24; // Show 24 points (one per hour)
    const node1Length = node1Data.length;
    const node2Length = node2Data.length;
    
    if (node1Length > 0 || node2Length > 0) {
        // Determine sampling rate
        const node1Interval = Math.max(1, Math.floor(node1Length / maxPoints));
        const node2Interval = Math.max(1, Math.floor(node2Length / maxPoints));
        
        // Get sampled data points for Node 1
        for (let i = 0; i < node1Length; i += node1Interval) {
            const entry = node1Data[i];
            const date = new Date(entry.timestamp);
            timeLabels.push(formatTime(date));
            node1Values.push(entry.moisture);
        }
        
        // Get sampled data points for Node 2
        let j = 0;
        for (let i = 0; i < node2Length; i += node2Interval) {
            const entry = node2Data[i];
            const date = new Date(entry.timestamp);
            
            // Only add label if we don't have enough from Node 1
            if (j < timeLabels.length) {
                node2Values.push(entry.moisture);
            } else {
                timeLabels.push(formatTime(date));
                node2Values.push(entry.moisture);
            }
            j++;
        }
        
        // Update chart data
        moistureChart.data.labels = timeLabels;
        moistureChart.data.datasets[0].data = node1Values;
        moistureChart.data.datasets[1].data = node2Values;
        moistureChart.update();
    }
}

/**
 * Update maturity detection data
 */
function updateMaturityData(data) {
    if (!data || data.error) {
        return;
    }
    
    // Update image
    const imagePath = data.image_path;
    if (imagePath) {
        document.getElementById('capturedImage').innerHTML = 
            `<img src="/api/images/${imagePath}" class="img-fluid captured-image" alt="Latest capture">`;
    }
    
    // Update maturity class and confidence
    const maturityClass = data.maturity_class || 'unknown';
    const confidence = data.confidence || 0;
    
    document.getElementById('maturityClass').textContent = 
        `Status: ${formatMaturityClass(maturityClass)}`;
    document.getElementById('maturityConfidence').textContent = 
        `Confidence: ${(confidence * 100).toFixed(1)}%`;
    
    // Update last capture time
    const timestamp = data.timestamp;
    if (timestamp) {
        document.getElementById('lastCapture').textContent = formatDateTime(new Date(timestamp));
    }
    
    // Update prediction details
    const predictions = data.predictions || {};
    
    // Immature
    const immatureValue = (predictions.immature || 0) * 100;
    document.getElementById('immatureProgress').style.width = `${immatureValue}%`;
    document.getElementById('immatureValue').textContent = `${immatureValue.toFixed(1)}%`;
    
    // Semi-mature
    const semiMatureValue = (predictions.semi_mature || 0) * 100;
    document.getElementById('semiMatureProgress').style.width = `${semiMatureValue}%`;
    document.getElementById('semiMatureValue').textContent = `${semiMatureValue.toFixed(1)}%`;
    
    // Mature
    const matureValue = (predictions.mature || 0) * 100;
    document.getElementById('matureProgress').style.width = `${matureValue}%`;
    document.getElementById('matureValue').textContent = `${matureValue.toFixed(1)}%`;
}

/**
 * Control valve state
 */
function controlValve(nodeId, state) {
    fetch('/api/manual-control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            node_id: nodeId,
            command: 'valve',
            value: state
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(
                'Valve Control',
                `${nodeId} valve ${state ? 'turned ON' : 'turned OFF'} successfully.`,
                'success'
            );
            
            // Update system mode
            document.getElementById('systemMode').innerHTML = 
                '<span class="badge bg-warning">Manual</span>';
                
            // Refresh data after a short delay
            setTimeout(refreshData, 1000);
        } else {
            showNotification(
                'Valve Control Error',
                data.message || 'Failed to control valve.',
                'error'
            );
        }
    })
    .catch(error => {
        console.error('Error controlling valve:', error);
        showNotification(
            'Valve Control Error',
            'Failed to send command to server.',
            'error'
        );
    });
}

/**
 * Trigger camera capture
 */
function triggerCapture() {
    showNotification(
        'Camera',
        'Capturing image... please wait.',
        'info'
    );
    
    fetch('/api/capture', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(
                'Camera',
                'Image captured and processed successfully.',
                'success'
            );
            
            // Update maturity data with new result
            updateMaturityData(data);
        } else {
            showNotification(
                'Camera Error',
                data.message || 'Failed to capture image.',
                'error'
            );
        }
    })
    .catch(error => {
        console.error('Error triggering capture:', error);
        showNotification(
            'Camera Error',
            'Failed to send capture command to server.',
            'error'
        );
    });
}

/**
 * Update server status indicator
 */
function updateServerStatus(online) {
    const serverStatus = document.getElementById('serverStatus');
    
    if (online) {
        serverStatus.innerHTML = '<span class="badge bg-success">Online</span>';
    } else {
        serverStatus.innerHTML = '<span class="badge bg-danger">Offline</span>';
    }
}

/**
 * Update the last refresh time
 */
function updateLastRefreshTime() {
    if (lastRefreshTime) {
        document.getElementById('lastUpdate').textContent = 
            `Last update: ${formatTime(lastRefreshTime)}`;
    }
}

/**
 * Show notification toast
 */
function showNotification(title, message, type = 'info') {
    // Set toast content
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastMessage').textContent = message;
    document.getElementById('toastTime').textContent = formatTime(new Date());
    
    // Set toast color based on type
    const toast = document.getElementById('notificationToast');
    toast.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info');
    
    switch (type) {
        case 'success':
            toast.classList.add('bg-success', 'text-white');
            break;
        case 'error':
            toast.classList.add('bg-danger', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-warning', 'text-dark');
            break;
        default:
            toast.classList.add('bg-info', 'text-white');
    }
    
    // Show the toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

/**
 * Format time for display (HH:MM:SS)
 */
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

/**
 * Format date and time for display
 */
function formatDateTime(date) {
    return date.toLocaleString([], { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit'
    });
}

/**
 * Format maturity class for display
 */
function formatMaturityClass(className) {
    switch (className) {
        case 'immature':
            return 'Immature (Not Ready)';
        case 'semi_mature':
            return 'Semi-Mature (Almost Ready)';
        case 'mature':
            return 'Mature (Ready to Harvest)';
        default:
            return 'Unknown';
    }
}