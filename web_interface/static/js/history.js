// Global variables
let moistureHistoryChart = null;
let valveActivityChart = null;
let currentPage = 1;
let totalPages = 1;
let lastRefreshTime = null;

// Initialize charts and data when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeCharts();
    setupEventListeners();
    refreshHistoricalData();
});

/**
 * Initialize charts used in the history page
 */
function initializeCharts() {
    // Moisture History Chart
    const moistureCtx = document.getElementById('moistureHistoryChart').getContext('2d');
    moistureHistoryChart = new Chart(moistureCtx, {
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
            interaction: {
                mode: 'index',
                intersect: false,
            },
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
                        text: 'Date/Time'
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

    // Valve Activity Chart
    const valveCtx = document.getElementById('valveActivityChart').getContext('2d');
    valveActivityChart = new Chart(valveCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Node 1 Valve',
                    data: [],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgb(54, 162, 235)',
                    borderWidth: 1
                },
                {
                    label: 'Node 2 Valve',
                    data: [],
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgb(255, 99, 132)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Active Minutes'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Time range selector
    document.getElementById('timeRange').addEventListener('change', function() {
        refreshHistoricalData();
    });

    // Pagination buttons
    document.getElementById('prevPageBtn').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadSensorReadings(currentPage);
        }
    });

    document.getElementById('nextPageBtn').addEventListener('click', function() {
        if (currentPage < totalPages) {
            currentPage++;
            loadSensorReadings(currentPage);
        }
    });
}

/**
 * Refresh all historical data
 */
function refreshHistoricalData() {
    const days = document.getElementById('timeRange').value;
    
    // Fetch historical data
    fetch(`/api/history?days=${days}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateHistoricalCharts(data);
            updateIrrigationStats(data);
            loadMaturityHistory(data);
            
            // Reset to first page of sensor readings
            currentPage = 1;
            loadSensorReadings(currentPage, data);
            
            // Update last refresh time
            lastRefreshTime = new Date();
            updateLastRefreshTime();
        })
        .catch(error => {
            console.error('Error fetching historical data:', error);
            alert('Error fetching historical data. Please try again later.');
        });
}

/**
 * Update the historical charts with data
 */
function updateHistoricalCharts(data) {
    if (!data || !data.soil_moisture) {
        return;
    }
    
    const moistureData = data.soil_moisture;
    const node1Data = moistureData.node1 || [];
    const node2Data = moistureData.node2 || [];
    
    // Process data for moisture history chart
    const timeLabels = [];
    const node1Values = [];
    const node2Values = [];
    
    // Sample data at reasonable intervals based on date range
    const days = parseInt(document.getElementById('timeRange').value);
    const maxPoints = Math.min(days * 24, 168); // Max 1 point per hour, up to 168 (1 week hourly)
    
    // Get data for node 1
    if (node1Data.length > 0) {
        const interval = Math.max(1, Math.floor(node1Data.length / maxPoints));
        
        for (let i = 0; i < node1Data.length; i += interval) {
            const entry = node1Data[i];
            timeLabels.push(formatDateTime(new Date(entry.timestamp)));
            node1Values.push(entry.moisture);
        }
    }
    
    // Get data for node 2 (align with timeLabels if possible)
    if (node2Data.length > 0) {
        const interval = Math.max(1, Math.floor(node2Data.length / maxPoints));
        
        // If node1 has data, try to align time points
        if (timeLabels.length > 0) {
            // Find nearest data points to match timestamps
            for (const label of timeLabels) {
                const date = new Date(label);
                let bestMatch = null;
                let minDiff = Infinity;
                
                for (const entry of node2Data) {
                    const entryDate = new Date(entry.timestamp);
                    const diff = Math.abs(date - entryDate);
                    if (diff < minDiff) {
                        minDiff = diff;
                        bestMatch = entry;
                    }
                }
                
                node2Values.push(bestMatch ? bestMatch.moisture : null);
            }
        } else {
            // No node1 data, create our own timeline
            for (let i = 0; i < node2Data.length; i += interval) {
                const entry = node2Data[i];
                timeLabels.push(formatDateTime(new Date(entry.timestamp)));
                node2Values.push(entry.moisture);
            }
        }
    }
    
    // Update moisture history chart
    moistureHistoryChart.data.labels = timeLabels;
    moistureHistoryChart.data.datasets[0].data = node1Values;
    moistureHistoryChart.data.datasets[1].data = node2Values;
    moistureHistoryChart.update();
    
    // Process data for valve activity chart
    updateValveActivityChart(node1Data, node2Data, days);
}

/**
 * Update valve activity chart
 */
function updateValveActivityChart(node1Data, node2Data, days) {
    // Group valve activity by day
    const valveActivityByDay = {};
    
    // Initialize dates for the selected range
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    // Create date labels for each day in the range
    const dateLabels = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
        const dateStr = formatDate(currentDate);
        dateLabels.push(dateStr);
        valveActivityByDay[dateStr] = { node1: 0, node2: 0 };
        
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    // Calculate valve activity duration for node 1
    if (node1Data.length > 0) {
        let lastStatus = false;
        let lastTimestamp = null;
        
        for (let i = 0; i < node1Data.length; i++) {
            const entry = node1Data[i];
            const entryDate = new Date(entry.timestamp);
            const dateStr = formatDate(entryDate);
            
            if (dateStr in valveActivityByDay) {
                // Check valve state change
                if (lastTimestamp && lastStatus) {
                    // Calculate duration in minutes if valve was on
                    const duration = (entryDate - lastTimestamp) / (1000 * 60);
                    valveActivityByDay[dateStr].node1 += duration;
                }
                
                lastStatus = entry.valve;
                lastTimestamp = entryDate;
            }
        }
    }
    
    // Calculate valve activity duration for node 2
    if (node2Data.length > 0) {
        let lastStatus = false;
        let lastTimestamp = null;
        
        for (let i = 0; i < node2Data.length; i++) {
            const entry = node2Data[i];
            const entryDate = new Date(entry.timestamp);
            const dateStr = formatDate(entryDate);
            
            if (dateStr in valveActivityByDay) {
                // Check valve state change
                if (lastTimestamp && lastStatus) {
                    // Calculate duration in minutes if valve was on
                    const duration = (entryDate - lastTimestamp) / (1000 * 60);
                    valveActivityByDay[dateStr].node2 += duration;
                }
                
                lastStatus = entry.valve;
                lastTimestamp = entryDate;
            }
        }
    }
    
    // Extract data for chart
    const node1ActivityData = dateLabels.map(date => 
        Math.round(valveActivityByDay[date].node1 * 10) / 10
    );
    
    const node2ActivityData = dateLabels.map(date => 
        Math.round(valveActivityByDay[date].node2 * 10) / 10
    );
    
    // Update valve activity chart
    valveActivityChart.data.labels = dateLabels;
    valveActivityChart.data.datasets[0].data = node1ActivityData;
    valveActivityChart.data.datasets[1].data = node2ActivityData;
    valveActivityChart.update();
}

/**
 * Update irrigation statistics
 */
function updateIrrigationStats(data) {
    if (!data || !data.soil_moisture) {
        return;
    }
    
    const moistureData = data.soil_moisture;
    const node1Data = moistureData.node1 || [];
    const node2Data = moistureData.node2 || [];
    
    // Count irrigation events (valve on transitions)
    let node1Count = 0;
    let node2Count = 0;
    
    // Calculate moisture before/after irrigation
    let totalMoistureBefore = 0;
    let totalMoistureAfter = 0;
    let irrigationEventCount = 0;
    
    // Process node 1 data
    if (node1Data.length > 1) {
        for (let i = 1; i < node1Data.length; i++) {
            // If valve transitions from off to on, count as irrigation event
            if (!node1Data[i-1].valve && node1Data[i].valve) {
                node1Count++;
                totalMoistureBefore += node1Data[i-1].moisture;
                
                // Look ahead for valve turning off again
                for (let j = i + 1; j < node1Data.length; j++) {
                    if (!node1Data[j].valve) {
                        totalMoistureAfter += node1Data[j].moisture;
                        irrigationEventCount++;
                        break;
                    }
                }
            }
        }
    }
    
    // Process node 2 data
    if (node2Data.length > 1) {
        for (let i = 1; i < node2Data.length; i++) {
            // If valve transitions from off to on, count as irrigation event
            if (!node2Data[i-1].valve && node2Data[i].valve) {
                node2Count++;
                totalMoistureBefore += node2Data[i-1].moisture;
                
                // Look ahead for valve turning off again
                for (let j = i + 1; j < node2Data.length; j++) {
                    if (!node2Data[j].valve) {
                        totalMoistureAfter += node2Data[j].moisture;
                        irrigationEventCount++;
                        break;
                    }
                }
            }
        }
    }
    
    // Calculate averages
    const avgMoistureBefore = irrigationEventCount > 0 
        ? totalMoistureBefore / irrigationEventCount 
        : 0;
    
    const avgMoistureAfter = irrigationEventCount > 0 
        ? totalMoistureAfter / irrigationEventCount 
        : 0;
    
    // Update UI
    document.getElementById('totalIrrigationCount').textContent = node1Count + node2Count;
    document.getElementById('node1IrrigationCount').textContent = node1Count;
    document.getElementById('node2IrrigationCount').textContent = node2Count;
    
    // Update progress bars
    document.getElementById('avgMoistureBeforeProgress').style.width = `${avgMoistureBefore}%`;
    document.getElementById('avgMoistureBeforeValue').textContent = `${avgMoistureBefore.toFixed(1)}%`;
    
    document.getElementById('avgMoistureAfterProgress').style.width = `${avgMoistureAfter}%`;
    document.getElementById('avgMoistureAfterValue').textContent = `${avgMoistureAfter.toFixed(1)}%`;
}

/**
 * Load maturity detection history
 */
function loadMaturityHistory(data) {
    const maturityTable = document.getElementById('maturityTable');
    
    if (!data || !data.maturity || data.maturity.length === 0) {
        maturityTable.innerHTML = '<tr><td colspan="4" class="text-center">No maturity detection data available</td></tr>';
        return;
    }
    
    // Clear table
    maturityTable.innerHTML = '';
    
    // Add each maturity detection record
    const maturityData = data.maturity;
    
    for (const record of maturityData) {
        const row = document.createElement('tr');
        
        // Date/Time
        const timeCell = document.createElement('td');
        timeCell.textContent = formatDateTime(new Date(record.timestamp));
        row.appendChild(timeCell);
        
        // Image
        const imageCell = document.createElement('td');
        const image = document.createElement('img');
        image.src = `/api/images/${record.image_path}`;
        image.alt = 'Plant Image';
        image.style.width = '80px';
        image.style.height = '60px';
        image.style.objectFit = 'cover';
        image.style.borderRadius = '4px';
        image.classList.add('img-thumbnail');
        imageCell.appendChild(image);
        row.appendChild(imageCell);
        
        // Maturity
        const maturityCell = document.createElement('td');
        maturityCell.textContent = formatMaturityClass(record.maturity_class);
        row.appendChild(maturityCell);
        
        // Confidence
        const confidenceCell = document.createElement('td');
        confidenceCell.textContent = `${(record.confidence * 100).toFixed(1)}%`;
        row.appendChild(confidenceCell);
        
        maturityTable.appendChild(row);
    }
}

/**
 * Load sensor readings with pagination
 */
function loadSensorReadings(page, data = null) {
    const rowsPerPage = 15;
    
    if (!data) {
        // If data wasn't provided, fetch it first
        const days = document.getElementById('timeRange').value;
        
        fetch(`/api/history?days=${days}`)
            .then(response => response.json())
            .then(data => {
                processSensorReadings(data, page, rowsPerPage);
            })
            .catch(error => {
                console.error('Error fetching sensor readings:', error);
            });
    } else {
        processSensorReadings(data, page, rowsPerPage);
    }
}

/**
 * Process and display sensor readings
 */
function processSensorReadings(data, page, rowsPerPage) {
    const sensorTable = document.getElementById('sensorReadingsTable');
    
    if (!data || !data.soil_moisture) {
        sensorTable.innerHTML = '<tr><td colspan="4" class="text-center">No sensor data available</td></tr>';
        return;
    }
    
    // Combine data from both nodes and sort by timestamp (newest first)
    const combinedData = [];
    
    if (data.soil_moisture.node1) {
        data.soil_moisture.node1.forEach(entry => {
            combinedData.push({
                ...entry,
                node_id: 'node1'
            });
        });
    }
    
    if (data.soil_moisture.node2) {
        data.soil_moisture.node2.forEach(entry => {
            combinedData.push({
                ...entry,
                node_id: 'node2'
            });
        });
    }
    
    // Sort by timestamp (newest first)
    combinedData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Calculate pagination
    totalPages = Math.ceil(combinedData.length / rowsPerPage);
    
    // Update page info
    document.getElementById('pageInfo').textContent = `Page ${page} of ${totalPages}`;
    
    // Enable/disable pagination buttons
    document.getElementById('prevPageBtn').disabled = page <= 1;
    document.getElementById('nextPageBtn').disabled = page >= totalPages;
    
    // Get subset of data for current page
    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, combinedData.length);
    const pageData = combinedData.slice(startIndex, endIndex);
    
    // Clear table
    sensorTable.innerHTML = '';
    
    // Add each sensor reading record
    for (const record of pageData) {
        const row = document.createElement('tr');
        
        // Date/Time
        const timeCell = document.createElement('td');
        timeCell.textContent = formatDateTime(new Date(record.timestamp));
        row.appendChild(timeCell);
        
        // Node
        const nodeCell = document.createElement('td');
        nodeCell.textContent = record.node_id === 'node1' ? 'Node 1' : 'Node 2';
        row.appendChild(nodeCell);
        
        // Soil Moisture
        const moistureCell = document.createElement('td');
        moistureCell.textContent = `${record.moisture.toFixed(1)}%`;
        
        // Add color indicator based on moisture level
        if (record.moisture < 30) {
            moistureCell.classList.add('text-danger');
        } else if (record.moisture < 70) {
            moistureCell.classList.add('text-warning');
        } else {
            moistureCell.classList.add('text-success');
        }
        
        row.appendChild(moistureCell);
        
        // Valve Status
        const valveCell = document.createElement('td');
        valveCell.textContent = record.valve ? 'ON' : 'OFF';
        valveCell.classList.add(record.valve ? 'text-success' : 'text-secondary');
        row.appendChild(valveCell);
        
        sensorTable.appendChild(row);
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
 * Format date only (YYYY-MM-DD)
 */
function formatDate(date) {
    return date.toISOString().split('T')[0];
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