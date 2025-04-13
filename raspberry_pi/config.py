#!/usr/bin/env python3
"""
Configuration file for the Smart Farming System
"""

# Server configuration
SERVER_PORT = 5000
SERVER_HOST = '0.0.0.0'

# Database configuration
DATABASE_FILE = 'farm_data.db'

# Camera configuration
CAMERA_TYPE = 'raspicam'  # Options: 'raspicam', 'webcam'
CAMERA_RESOLUTION = (1280, 720)
CAMERA_CAPTURE_INTERVAL = 1800  # Seconds (30 minutes)

# Computer Vision configuration
CV_MODEL_PATH = 'models/maturity_model.h5'
CV_IMAGE_SIZE = (224, 224)
CV_CLASSES = ['immature', 'semi_mature', 'mature']

# WSN configuration
WSN_MONITORING_INTERVAL = 60  # Seconds
WSN_NODES = {
    'node1': {
        'description': 'Node 1 - North Garden',
        'initial_ip': '192.168.1.101'
    },
    'node2': {
        'description': 'Node 2 - South Garden',
        'initial_ip': '192.168.1.102'
    }
}

# Fuzzy Logic configuration
FUZZY_DRY_THRESHOLD = 30  # Soil moisture percentage below which considered 'dry'
FUZZY_WET_THRESHOLD = 70  # Soil moisture percentage above which considered 'wet'

# Web interface configuration
WEB_SESSION_SECRET = 'change-this-secret-key'
WEB_REFRESH_INTERVAL = 10  # Seconds between data refreshes on dashboard

# Irrigation thresholds
MIN_IRRIGATION_DURATION = 10  # Minimum irrigation time in seconds
MAX_IRRIGATION_DURATION = 300  # Maximum irrigation time in seconds
IRRIGATION_COOLDOWN = 3600  # Minimum time between irrigations in seconds

# System paths
IMAGES_PATH = 'images/'
DATA_PATH = 'data/'
LOGS_PATH = 'logs/'