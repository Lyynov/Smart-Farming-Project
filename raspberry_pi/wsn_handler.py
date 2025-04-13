#!/usr/bin/env python3
"""
Wireless Sensor Network (WSN) Handler
Manages communication with ESP32 nodes
"""

import time
import requests
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class WSNHandler:
    """Handles communication with wireless sensor nodes (ESP32s)"""
    
    def __init__(self):
        """Initialize the WSN Handler"""
        self.nodes = {}  # Dictionary to store node information
        self.node_status = {}  # Track online status of nodes
        self.last_seen = {}  # Track when node was last seen
        self.monitoring_active = False
        self.monitor_thread = None
    
    def register_node(self, node_id, ip_address, port=80):
        """
        Register a new node in the system
        
        Args:
            node_id (str): Unique ID for the node
            ip_address (str): IP address of the node
            port (int): Port number for the node (default: 80)
        """
        self.nodes[node_id] = {
            'ip': ip_address,
            'port': port,
            'registered_at': datetime.now()
        }
        self.node_status[node_id] = False  # Initialize as offline
        self.last_seen[node_id] = None
        
        logger.info(f"Node {node_id} registered with IP {ip_address}:{port}")
    
    def get_node_status(self, node_id):
        """
        Get the current status of a node
        
        Args:
            node_id (str): ID of the node
            
        Returns:
            dict: Node status information
        """
        if node_id not in self.nodes:
            logger.warning(f"Attempted to get status of unregistered node: {node_id}")
            return None
        
        return {
            'node_id': node_id,
            'online': self.node_status.get(node_id, False),
            'last_seen': self.last_seen.get(node_id),
            'ip': self.nodes[node_id]['ip'],
            'port': self.nodes[node_id]['port']
        }
    
    def get_all_nodes_status(self):
        """
        Get status information for all registered nodes
        
        Returns:
            list: List of node status dictionaries
        """
        return [self.get_node_status(node_id) for node_id in self.nodes]
    
    def ping_node(self, node_id):
        """
        Ping a node to check if it's online
        
        Args:
            node_id (str): ID of the node to ping
            
        Returns:
            bool: True if node is online, False otherwise
        """
        if node_id not in self.nodes:
            logger.warning(f"Attempted to ping unregistered node: {node_id}")
            return False
        
        node_info = self.nodes[node_id]
        url = f"http://{node_info['ip']}:{node_info['port']}/ping"
        
        try:
            response = requests.get(url, timeout=5)
            online = response.status_code == 200
            
            # Update status
            self.node_status[node_id] = online
            if online:
                self.last_seen[node_id] = datetime.now()
            
            logger.debug(f"Pinged node {node_id}: {'online' if online else 'offline'}")
            return online
            
        except requests.RequestException:
            # Node is offline or unreachable
            self.node_status[node_id] = False
            logger.debug(f"Node {node_id} is unreachable")
            return False
    
    def send_command(self, node_id, command, params=None):
        """
        Send a command to a node
        
        Args:
            node_id (str): ID of the node to send command to
            command (str): Command type
            params (dict): Command parameters
            
        Returns:
            dict: Response from the node or error information
        """
        if node_id not in self.nodes:
            logger.warning(f"Attempted to send command to unregistered node: {node_id}")
            return {'status': 'error', 'message': 'Node not registered'}
        
        node_info = self.nodes[node_id]
        url = f"http://{node_info['ip']}:{node_info['port']}/command"
        
        # Prepare payload
        payload = {
            'command': command
        }
        
        if params:
            payload.update(params)
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            
            # Update last seen timestamp if node responds
            if response.status_code == 200:
                self.node_status[node_id] = True
                self.last_seen[node_id] = datetime.now()
            
            return {
                'status': 'success' if response.status_code == 200 else 'error',
                'code': response.status_code,
                'response': response.json() if response.status_code == 200 else None
            }
            
        except requests.RequestException as e:
            logger.error(f"Error sending command to node {node_id}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def start_monitoring(self, interval=60):
        """
        Start a background thread to monitor node status
        
        Args:
            interval (int): Monitoring interval in seconds
        """
        if self.monitoring_active:
            logger.warning("Node monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_nodes_thread,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"Started node monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop the node monitoring thread"""
        if not self.monitoring_active:
            logger.warning("Node monitoring is not active")
            return
        
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        logger.info("Stopped node monitoring")
    
    def _monitor_nodes_thread(self, interval):
        """
        Background thread function for monitoring nodes
        
        Args:
            interval (int): Monitoring interval in seconds
        """
        while self.monitoring_active:
            try:
                logger.debug("Running node status check")
                
                for node_id in self.nodes:
                    online = self.ping_node(node_id)
                    
                    # Log if status changed
                    prev_status = self.node_status.get(node_id, False)
                    if online != prev_status:
                        if online:
                            logger.info(f"Node {node_id} is now online")
                        else:
                            logger.warning(f"Node {node_id} is now offline")
                
                # Check for nodes that haven't been seen for a long time
                current_time = datetime.now()
                for node_id, last_seen in self.last_seen.items():
                    if last_seen is not None:
                        time_diff = (current_time - last_seen).total_seconds()
                        if time_diff > interval * 3:  # If not seen for 3 intervals
                            logger.warning(f"Node {node_id} hasn't been seen for {time_diff:.1f} seconds")
                
            except Exception as e:
                logger.error(f"Error in node monitoring thread: {e}")
            
            # Sleep for the interval
            time.sleep(interval)


# For standalone testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create handler
    wsn = WSNHandler()
    
    # Register test nodes (replace with your actual node information)
    wsn.register_node('node1', '192.168.1.101')
    wsn.register_node('node2', '192.168.1.102')
    
    # Start monitoring
    wsn.start_monitoring(interval=10)
    
    try:
        # Run for a while to test monitoring
        print("Monitoring nodes for 30 seconds...")
        time.sleep(30)
        
        # Get status
        statuses = wsn.get_all_nodes_status()
        for status in statuses:
            print(f"Node {status['node_id']}: {'Online' if status['online'] else 'Offline'}, Last seen: {status['last_seen']}")
        
    finally:
        # Stop monitoring
        wsn.stop_monitoring()
        print("Monitoring stopped")