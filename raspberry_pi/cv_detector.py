#!/usr/bin/env python3
"""
Computer Vision Module for Plant Maturity Detection
Uses a pre-trained deep learning model to detect plant maturity from images
"""

import os
import time
import logging
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

logger = logging.getLogger(__name__)

class MaturityDetector:
    """Detects plant maturity using computer vision"""
    
    def __init__(self):
        """Initialize the maturity detector"""
        self.model = None
        self.classes = ['immature', 'semi_mature', 'mature']
        self.image_size = (224, 224)  # Default for many CNN models
        self.camera = None
    
    def load_model(self, model_path):
        """
        Load the pre-trained TensorFlow/Keras model
        
        Args:
            model_path (str): Path to the .h5 model file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Loading maturity detection model from {model_path}")
            self.model = load_model(model_path)
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def initialize_camera(self):
        """Initialize the camera connection"""
        try:
            logger.info("Initializing camera")
            self.camera = cv2.VideoCapture(0)  # Use default camera (change if needed)
            
            # Check if camera opened successfully
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set camera properties (adjust as needed)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            # Warm up the camera
            for _ in range(5):
                success, _ = self.camera.read()
                time.sleep(0.1)
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self, save_path):
        """
        Capture an image from the camera and save it
        
        Args:
            save_path (str): Path to save the captured image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize camera if not already done
            if self.camera is None or not self.camera.isOpened():
                if not self.initialize_camera():
                    return False
            
            # Capture frame
            logger.info("Capturing image")
            success, frame = self.camera.read()
            
            if not success:
                logger.error("Failed to capture image")
                return False
            
            # Save the image
            cv2.imwrite(save_path, frame)
            logger.info(f"Image saved to {save_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return False
    
    def release_camera(self):
        """Release the camera resource"""
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
            logger.info("Camera released")
    
    def preprocess_image(self, img_path):
        """
        Preprocess an image for the neural network
        
        Args:
            img_path (str): Path to the image file
            
        Returns:
            numpy.ndarray: Preprocessed image array
        """
        try:
            # Load and resize image
            img = cv2.imread(img_path)
            img = cv2.resize(img, self.image_size)
            
            # Convert to RGB (from BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values
            img = img.astype(np.float32) / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def detect_maturity(self, img_path):
        """
        Detect plant maturity from an image
        
        Args:
            img_path (str): Path to the image file
            
        Returns:
            dict: Detection results including class and confidence
        """
        try:
            if self.model is None:
                logger.error("Model not loaded")
                return {"error": "Model not loaded"}
            
            # Check if file exists
            if not os.path.exists(img_path):
                logger.error(f"Image file not found: {img_path}")
                return {"error": "Image file not found"}
            
            # Preprocess image
            processed_img = self.preprocess_image(img_path)
            
            if processed_img is None:
                return {"error": "Failed to preprocess image"}
            
            # Make prediction
            predictions = self.model.predict(processed_img)
            
            # Get class index with highest probability
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            
            # Get class name
            class_name = self.classes[class_idx]
            
            logger.info(f"Detected maturity: {class_name} with confidence {confidence:.2f}")
            
            # Return results
            return {
                "maturity_class": class_name,
                "confidence": confidence,
                "predictions": {
                    cls: float(pred) for cls, pred in zip(self.classes, predictions[0])
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting maturity: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Destructor to ensure camera is released"""
        self.release_camera()


# For standalone testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create detector
    detector = MaturityDetector()
    
    # Test model loading (replace with your model path)
    detector.load_model("models/maturity_model.h5")
    
    # Test camera
    test_image_path = "test_capture.jpg"
    if detector.capture_image(test_image_path):
        print(f"Successfully captured test image: {test_image_path}")
        
        # Test detection
        result = detector.detect_maturity(test_image_path)
        print("Detection result:", result)
    else:
        print("Failed to capture test image")
    
    # Clean up
    detector.release_camera()