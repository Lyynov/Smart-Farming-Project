#!/usr/bin/env python3
"""
Web Interface for Smart Farming System
Provides a dashboard for monitoring and controlling the system
"""

import os
import json
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("web_interface.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
SERVER_URL = "http://localhost:5000"  # URL of the main Raspberry Pi server

@app.route('/')
def index():
    """Serve the home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')

@app.route('/history')
def history():
    """Serve the history page"""
    return render_template('history.html')

@app.route('/api/data')
def get_data():
    """
    Proxy endpoint to get latest data from the main server
    """
    try:
        response = requests.get(f"{SERVER_URL}/api/data")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """
    Proxy endpoint to get historical data from the main server
    """
    try:
        days = request.args.get('days', default=7, type=int)
        response = requests.get(f"{SERVER_URL}/api/history?days={days}")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/maturity')
def get_maturity():
    """
    Proxy endpoint to get latest maturity detection from the main server
    """
    try:
        response = requests.get(f"{SERVER_URL}/api/maturity")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error getting maturity data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/manual-control', methods=['POST'])
def manual_control():
    """
    Proxy endpoint for manual control of the system
    """
    try:
        data = request.json
        response = requests.post(f"{SERVER_URL}/api/manual-control", json=data)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error in manual control: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/capture', methods=['POST'])
def trigger_capture():
    """
    Proxy endpoint to trigger a camera capture
    """
    try:
        response = requests.post(f"{SERVER_URL}/api/capture")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error triggering capture: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<path:filename>')
def get_image(filename):
    """
    Proxy endpoint to serve captured images
    """
    try:
        response = requests.get(f"{SERVER_URL}/api/images/{filename}", stream=True)
        
        # Check if image exists
        if response.status_code == 200:
            # Save to temporary location and serve
            temp_dir = 'static/temp_images'
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return send_from_directory('static/temp_images', filename)
        else:
            return "Image not found", 404
    except Exception as e:
        logger.error(f"Error getting image: {e}")
        return "Error fetching image", 500

def start_web_interface():
    """Start the Flask web interface"""
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    try:
        # Create necessary directories
        os.makedirs('static/temp_images', exist_ok=True)
        
        # Start web interface
        logger.info("Starting web interface on port 8080")
        start_web_interface()
    except KeyboardInterrupt:
        logger.info("Web interface shutting down...")
    except Exception as e:
        logger.error(f"Error starting web interface: {e}")