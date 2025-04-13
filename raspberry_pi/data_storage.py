#!/usr/bin/env python3
"""
Data Storage Module for Smart Farming System
Manages persistent storage of sensor data and maturity detection results
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataStorage:
    """Handles persistent storage of system data"""
    
    def __init__(self, db_file='farm_data.db'):
        """
        Initialize the data storage module
        
        Args:
            db_file (str): SQLite database file path
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
    
    def initialize_db(self):
        """Initialize database and create necessary tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self._create_tables()
            
            logger.info(f"Database initialized: {self.db_file}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        # Soil moisture data table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS soil_moisture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            moisture_value REAL NOT NULL,
            valve_status INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Maturity detection table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS maturity_detection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            maturity_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            predictions TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Commit changes
        self.conn.commit()
    
    def store_sensor_data(self, node_id, moisture_value, valve_status):
        """
        Store soil moisture sensor data
        
        Args:
            node_id (str): ID of the sensor node
            moisture_value (float): Soil moisture percentage value
            valve_status (bool): Current status of the valve
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.conn is None:
                self.initialize_db()
            
            # Ensure proper types
            node_id = str(node_id)
            moisture_value = float(moisture_value)
            valve_status = 1 if valve_status else 0
            
            # Insert data
            self.cursor.execute(
                "INSERT INTO soil_moisture (node_id, moisture_value, valve_status) VALUES (?, ?, ?)",
                (node_id, moisture_value, valve_status)
            )
            self.conn.commit()
            
            logger.debug(f"Stored sensor data: node={node_id}, moisture={moisture_value}, valve={valve_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing sensor data: {e}")
            return False
    
    def store_maturity_data(self, image_path, detection_result):
        """
        Store plant maturity detection results
        
        Args:
            image_path (str): Path to the captured image
            detection_result (dict): Detection results
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.conn is None:
                self.initialize_db()
            
            # Check if detection result is valid
            if 'error' in detection_result:
                logger.warning(f"Not storing invalid detection result: {detection_result['error']}")
                return False
            
            # Extract data
            maturity_class = detection_result.get('maturity_class', 'unknown')
            confidence = detection_result.get('confidence', 0.0)
            predictions = json.dumps(detection_result.get('predictions', {}))
            
            # Insert data
            self.cursor.execute(
                "INSERT INTO maturity_detection (image_path, maturity_class, confidence, predictions) VALUES (?, ?, ?, ?)",
                (image_path, maturity_class, confidence, predictions)
            )
            self.conn.commit()
            
            logger.debug(f"Stored maturity data: image={image_path}, class={maturity_class}, confidence={confidence}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing maturity data: {e}")
            return False
    
    def get_latest_data(self):
        """
        Get latest data from all sensors
        
        Returns:
            dict: Dictionary containing the latest data
        """
        try:
            if self.conn is None:
                self.initialize_db()
            
            # Get latest moisture data for each node
            self.cursor.execute("""
                SELECT sm.node_id, sm.moisture_value, sm.valve_status, sm.timestamp
                FROM soil_moisture sm
                JOIN (
                    SELECT node_id, MAX(timestamp) as max_time
                    FROM soil_moisture
                    GROUP BY node_id
                ) latest ON sm.node_id = latest.node_id AND sm.timestamp = latest.max_time
            """)
            
            moisture_data = {}
            for row in self.cursor.fetchall():
                node_id, moisture, valve, timestamp = row
                moisture_data[node_id] = {
                    'moisture': moisture,
                    'valve': bool(valve),
                    'timestamp': timestamp
                }
            
            # Get latest maturity detection
            self.cursor.execute("""
                SELECT image_path, maturity_class, confidence, predictions, timestamp
                FROM maturity_detection
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            maturity_data = None
            row = self.cursor.fetchone()
            if row:
                image_path, maturity_class, confidence, predictions, timestamp = row
                maturity_data = {
                    'image_path': image_path,
                    'maturity_class': maturity_class,
                    'confidence': confidence,
                    'predictions': json.loads(predictions),
                    'timestamp': timestamp
                }
            
            return {
                'soil_moisture': moisture_data,
                'maturity': maturity_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return {'error': str(e)}
    
    def get_historical_data(self, days=7):
        """
        Get historical data for the specified number of days
        
        Args:
            days (int): Number of days to retrieve
            
        Returns:
            dict: Dictionary containing historical data
        """
        try:
            if self.conn is None:
                self.initialize_db()
            
            # Calculate date threshold
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get moisture data
            self.cursor.execute("""
                SELECT node_id, moisture_value, valve_status, timestamp
                FROM soil_moisture
                WHERE timestamp >= ?
                ORDER BY timestamp
            """, (threshold,))
            
            moisture_data = {}
            for row in self.cursor.fetchall():
                node_id, moisture, valve, timestamp = row
                
                if node_id not in moisture_data:
                    moisture_data[node_id] = []
                
                moisture_data[node_id].append({
                    'moisture': moisture,
                    'valve': bool(valve),
                    'timestamp': timestamp
                })
            
            # Get maturity detections
            self.cursor.execute("""
                SELECT image_path, maturity_class, confidence, timestamp
                FROM maturity_detection
                WHERE timestamp >= ?
                ORDER BY timestamp
            """, (threshold,))
            
            maturity_data = []
            for row in self.cursor.fetchall():
                image_path, maturity_class, confidence, timestamp = row
                
                maturity_data.append({
                    'image_path': image_path,
                    'maturity_class': maturity_class,
                    'confidence': confidence,
                    'timestamp': timestamp
                })
            
            return {
                'soil_moisture': moisture_data,
                'maturity': maturity_data,
                'days': days,
                'start_date': threshold,
                'end_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return {'error': str(e)}
    
    def get_latest_maturity(self):
        """
        Get latest maturity detection result
        
        Returns:
            dict: Latest maturity detection data
        """
        try:
            if self.conn is None:
                self.initialize_db()
            
            self.cursor.execute("""
                SELECT image_path, maturity_class, confidence, predictions, timestamp
                FROM maturity_detection
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = self.cursor.fetchone()
            if row:
                image_path, maturity_class, confidence, predictions, timestamp = row
                return {
                    'image_path': image_path,
                    'maturity_class': maturity_class,
                    'confidence': confidence,
                    'predictions': json.loads(predictions),
                    'timestamp': timestamp
                }
            else:
                return {'error': 'No maturity detection data available'}
            
        except Exception as e:
            logger.error(f"Error getting latest maturity data: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.debug("Database connection closed")
    
    def __del__(self):
        """Destructor to ensure database connection is closed"""
        self.close()


# For standalone testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create storage instance
    storage = DataStorage("test_data.db")
    
    # Initialize database
    storage.initialize_db()
    
    # Test storing sensor data
    storage.store_sensor_data("node1", 45.7, False)
    storage.store_sensor_data("node2", 23.2, True)
    
    # Test storing maturity data
    storage.store_maturity_data("test.jpg", {
        "maturity_class": "semi_mature",
        "confidence": 0.85,
        "predictions": {"immature": 0.1, "semi_mature": 0.85, "mature": 0.05}
    })
    
    # Test retrieving data
    latest_data = storage.get_latest_data()
    print("Latest data:", json.dumps(latest_data, indent=2))
    
    # Test historical data
    hist_data = storage.get_historical_data(days=1)
    print("Historical data:", json.dumps(hist_data, indent=2))
    
    # Clean up
    storage.close()
    # Consider removing the test database
    # os.remove("test_data.db")