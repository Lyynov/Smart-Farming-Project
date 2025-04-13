#!/usr/bin/env python3
"""
Main server for Smart Farming System
Handles communication with ESP32 nodes, processes data with fuzzy logic,
manages computer vision detection, and serves web interface
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

# Import custom modules
from fuzzy_logic import FuzzyController
from wsn_handler import WSNHandler
from cv_detector import MaturityDetector
from data_storage import DataStorage
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../web_interface/static',
            template_folder='../web_interface/templates')

# Initialize components
data_storage = DataStorage('farm_data.db')
fuzzy_controller = FuzzyController()
wsn_handler = WSNHandler()
maturity_detector = MaturityDetector()

# Store node commands
node_commands = {}

# Last processed data from each node
node_data = {}

# Flag for camera capture
capture_active = False

def initialize_system():
    """Initialize system components"""
    logger.info("Initializing Smart Farming System...")
    
    # Create necessary directories
    os.makedirs('images', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initialize database
    data_storage.initialize_db()
    
    # Initialize maturity detector
    maturity_detector.load_model('models/maturity_model.h5')
    
    logger.info("System initialization complete")

def camera_capture_thread():
    """Thread for periodic camera capture and processing"""
    global capture_active
    
    while capture_active:
        try:
            logger.info("Capturing image from camera")
            image_path = 'images/capture_{}.jpg'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
            
            # Capture image
            success = maturity_detector.capture_image(image_path)
            
            if success:
                # Process image for maturity detection
                result = maturity_detector.detect_maturity(image_path)
                
                # Store result in database
                data_storage.store_maturity_data(image_path, result)
                
                logger.info(f"Maturity detection result: {result}")
            else:
                logger.error("Failed to capture image")
                
        except Exception as e:
            logger.error(f"Error in camera capture thread: {e}")
            
        # Wait for next capture
        time.sleep(config.CAMERA_CAPTURE_INTERVAL)

@app.route('/')
def index():
    """Serve the main page"""
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
    """API endpoint to get latest sensor data"""
    # Get latest data from storage
    data = data_storage.get_latest_data()
    return jsonify(data)

@app.route('/api/history')
def get_history():
    """API endpoint to get historical data"""
    days = request.args.get('days', default=7, type=int)
    data = data_storage.get_historical_data(days)
    return jsonify(data)

@app.route('/api/maturity')
def get_maturity():
    """API endpoint to get latest maturity detection"""
    data = data_storage.get_latest_maturity()
    return jsonify(data)

@app.route('/api/images/<path:filename>')
def get_image(filename):
    """Serve captured images"""
    return send_from_directory('images', filename)

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Endpoint for receiving data from ESP32 nodes"""
    try:
        data = request.json
        logger.info(f"Received data from node: {data}")
        
        # Store the data
        node_id = data.get('node_id')
        soil_moisture = data.get('soil_moisture')
        valve_status = data.get('valve_status')
        
        if node_id and soil_moisture is not None:
            # Store latest data for the node
            node_data[node_id] = data
            
            # Store in database
            data_storage.store_sensor_data(node_id, soil_moisture, valve_status)
            
            # Process with fuzzy logic
            valve_command = fuzzy_controller.evaluate(soil_moisture)
            
            # Store command for node to retrieve
            node_commands[node_id] = {'valve_command': valve_command}
            
            # Log decision
            logger.info(f"Fuzzy logic decision for {node_id}: moisture={soil_moisture}, valve={valve_command}")
            
            return jsonify({'status': 'success', 'message': 'Data received'})
        else:
            logger.warning("Received incomplete data")
            return jsonify({'status': 'error', 'message': 'Incomplete data'}), 400
    
    except Exception as e:
        logger.error(f"Error processing sensor data: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/node-command/<node_id>', methods=['GET'])
def get_node_command(node_id):
    """Endpoint for ESP32 nodes to get commands"""
    command = node_commands.get(node_id, {'valve_command': False})
    return jsonify(command)

@app.route('/api/manual-control', methods=['POST'])
def manual_control():
    """API endpoint for manual control from web interface"""
    try:
        data = request.json
        node_id = data.get('node_id')
        command = data.get('command')
        value = data.get('value')
        
        if node_id and command:
            if command == 'valve':
                # Update command for node
                if node_id in node_commands:
                    node_commands[node_id]['valve_command'] = bool(value)
                else:
                    node_commands[node_id] = {'valve_command': bool(value)}
                
                logger.info(f"Manual control: {node_id} valve set to {value}")
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'error', 'message': 'Unknown command'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    except Exception as e:
        logger.error(f"Error in manual control: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/capture', methods=['POST'])
def trigger_capture():
    """API endpoint to trigger a camera capture"""
    try:
        # Capture image
        image_path = 'images/capture_{}.jpg'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        success = maturity_detector.capture_image(image_path)
        
        if success:
            # Process image for maturity detection
            result = maturity_detector.detect_maturity(image_path)
            
            # Store result in database
            data_storage.store_maturity_data(image_path, result)
            
            return jsonify({
                'status': 'success',
                'image': image_path,
                'result': result
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to capture image'}), 500
    
    except Exception as e:
        logger.error(f"Error triggering capture: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def start_server():
    """Start the Flask server"""
    # Initialize system
    initialize_system()
    
    # Start camera capture thread
    global capture_active
    capture_active = True
    camera_thread = threading.Thread(target=camera_capture_thread)
    camera_thread.daemon = True
    camera_thread.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=config.SERVER_PORT, debug=False)

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        capture_active = False
        # Allow threads to cleanup
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error starting server: {e}")