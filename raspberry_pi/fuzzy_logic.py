#!/usr/bin/env python3
"""
Fuzzy Logic Controller for Smart Farming System
Implements a Mamdani fuzzy inference system to control irrigation based on soil moisture
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import logging

logger = logging.getLogger(__name__)

class FuzzyController:
    """Fuzzy Logic Controller for irrigation decision making"""
    
    def __init__(self):
        """Initialize the fuzzy logic controller"""
        logger.info("Initializing Fuzzy Logic Controller")
        
        try:
            # Create a new fuzzy control system
            self._create_fuzzy_system()
            logger.info("Fuzzy Logic Controller initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing fuzzy controller: {e}")
            raise
    
    def _create_fuzzy_system(self):
        """Create the fuzzy control system with rules"""
        
        # Define input variable - soil moisture
        soil_moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'soil_moisture')
        
        # Define output variable - irrigation control (valve)
        valve_control = ctrl.Consequent(np.arange(0, 101, 1), 'valve_control')
        
        # Define membership functions for soil moisture
        soil_moisture['dry'] = fuzz.trapmf(soil_moisture.universe, [0, 0, 20, 40])
        soil_moisture['moderate'] = fuzz.trimf(soil_moisture.universe, [20, 50, 80])
        soil_moisture['wet'] = fuzz.trapmf(soil_moisture.universe, [60, 80, 100, 100])
        
        # Define membership functions for valve control
        valve_control['off'] = fuzz.trapmf(valve_control.universe, [0, 0, 10, 30])
        valve_control['moderate'] = fuzz.trimf(valve_control.universe, [20, 50, 80])
        valve_control['on'] = fuzz.trapmf(valve_control.universe, [70, 90, 100, 100])
        
        # Define rules
        rule1 = ctrl.Rule(soil_moisture['dry'], valve_control['on'])
        rule2 = ctrl.Rule(soil_moisture['moderate'], valve_control['moderate'])
        rule3 = ctrl.Rule(soil_moisture['wet'], valve_control['off'])
        
        # Create control system
        irrigation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        
        # Create simulation
        self.irrigation_sim = ctrl.ControlSystemSimulation(irrigation_ctrl)
    
    def evaluate(self, moisture_value):
        """
        Evaluate soil moisture and determine valve control output
        
        Args:
            moisture_value (float): Soil moisture percentage (0-100)
            
        Returns:
            bool: True if valve should be turned on, False otherwise
        """
        try:
            # Ensure value is within range
            moisture_value = max(0, min(100, moisture_value))
            
            # Set input value
            self.irrigation_sim.input['soil_moisture'] = moisture_value
            
            # Compute result
            self.irrigation_sim.compute()
            
            # Get defuzzified result
            valve_output = self.irrigation_sim.output['valve_control']
            
            logger.debug(f"Fuzzy evaluation: moisture={moisture_value}, output={valve_output}")
            
            # Convert to binary decision (threshold at 50)
            return valve_output >= 50
            
        except Exception as e:
            logger.error(f"Error in fuzzy evaluation: {e}")
            # Default to off in case of error (fail-safe)
            return False
    
    def get_membership_values(self, moisture_value):
        """
        Get membership values for a given moisture input
        Useful for debugging and visualization
        
        Args:
            moisture_value (float): Soil moisture percentage (0-100)
            
        Returns:
            dict: Membership values for each fuzzy set
        """
        # Ensure value is within range
        moisture_value = max(0, min(100, moisture_value))
        
        # Create array for moisture value
        x = np.array([moisture_value])
        
        # Calculate membership values
        dry_membership = fuzz.interp_membership(
            np.arange(0, 101, 1), 
            self.irrigation_sim.ctrl.antecedents[0].terms['dry'].mf, 
            x
        )
        moderate_membership = fuzz.interp_membership(
            np.arange(0, 101, 1), 
            self.irrigation_sim.ctrl.antecedents[0].terms['moderate'].mf, 
            x
        )
        wet_membership = fuzz.interp_membership(
            np.arange(0, 101, 1), 
            self.irrigation_sim.ctrl.antecedents[0].terms['wet'].mf, 
            x
        )
        
        return {
            'dry': float(dry_membership),
            'moderate': float(moderate_membership),
            'wet': float(wet_membership)
        }


# For standalone testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create controller
    controller = FuzzyController()
    
    # Test with different moisture levels
    test_values = [0, 10, 25, 50, 75, 90, 100]
    
    print("Testing Fuzzy Logic Controller")
    print("-----------------------------")
    print("Moisture | Decision | Membership Values")
    print("-----------------------------")
    
    for value in test_values:
        decision = controller.evaluate(value)
        memberships = controller.get_membership_values(value)
        
        print(f"{value:7} | {'ON' if decision else 'OFF':8} | {memberships}")