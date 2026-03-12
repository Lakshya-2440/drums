"""
MediaPipe Hand Tracker wrapper for detecting and tracking hands.
Uses the new MediaPipe Tasks API (0.10.x+).
"""
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import List, Optional, Tuple, Dict, Any
import config
import os
import urllib.request


# Hand landmark indices (same as before)
HAND_LANDMARKS = {
    'WRIST': 0,
    'THUMB_CMC': 1, 'THUMB_MCP': 2, 'THUMB_IP': 3, 'THUMB_TIP': 4,
    'INDEX_MCP': 5, 'INDEX_PIP': 6, 'INDEX_DIP': 7, 'INDEX_TIP': 8,
    'MIDDLE_MCP': 9, 'MIDDLE_PIP': 10, 'MIDDLE_DIP': 11, 'MIDDLE_TIP': 12,
    'RING_MCP': 13, 'RING_PIP': 14, 'RING_DIP': 15, 'RING_TIP': 16,
    'PINKY_MCP': 17, 'PINKY_PIP': 18, 'PINKY_DIP': 19, 'PINKY_TIP': 20,
}


def download_model_if_needed(model_path: str = "hand_landmarker.task") -> str:
    """Download the hand landmarker model if not present."""
    if os.path.exists(model_path):
        return model_path
    
    print(f"  Downloading hand landmarker model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    try:
        urllib.request.urlretrieve(url, model_path)
        print(f"  Model downloaded to {model_path}")
    except Exception as e:
        print(f"  Warning: Could not download model: {e}")
        raise
    return model_path


class HandTracker:
    """
    Wrapper for MediaPipe Hands for detecting and tracking hands.
    Uses the new Tasks API (mediapipe 0.10.x+).
    """
    
    def __init__(
        self,
        max_hands: int = config.MAX_HANDS,
        detection_confidence: float = config.MIN_DETECTION_CONFIDENCE,
        tracking_confidence: float = config.MIN_TRACKING_CONFIDENCE,
        model_complexity: int = config.MODEL_COMPLEXITY
    ):
        """
        Initialize the hand tracker.
        
        Args:
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum detection confidence
            tracking_confidence: Minimum tracking confidence  
            model_complexity: Model complexity (0=lite, 1=full)
        """
        # Download model if needed
        model_path = download_model_if_needed()
        
        # Configure the hand landmarker
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # Store latest results
        self.results = None
        self.frame_shape = None
    
    def process_frame(self, frame: np.ndarray) -> bool:
        """
        Process a frame to detect hands.
        
        Args:
            frame: BGR image from OpenCV
        
        Returns:
            True if hands were detected, False otherwise
        """
        self.frame_shape = frame.shape
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        self.results = self.detector.detect(mp_image)
        
        return len(self.results.hand_landmarks) > 0
    
    def get_hand_count(self) -> int:
        """Get the number of detected hands."""
        if self.results and self.results.hand_landmarks:
            return len(self.results.hand_landmarks)
        return 0
    
    def get_all_landmarks(self) -> List[List[Tuple[float, float, float]]]:
        """
        Get all landmarks for all detected hands.
        
        Returns:
            List of hands, each containing list of (x, y, z) landmarks in pixel coordinates
        """
        if not self.results or not self.results.hand_landmarks:
            return []
        
        all_hands = []
        h, w, _ = self.frame_shape
        
        for hand_landmarks in self.results.hand_landmarks:
            landmarks = []
            for lm in hand_landmarks:
                # Convert normalized coordinates to pixel coordinates
                x = lm.x * w
                y = lm.y * h
                z = lm.z * w  # Scale z similarly for consistency
                landmarks.append((x, y, z))
            all_hands.append(landmarks)
        
        return all_hands
    
    def get_fingertip_positions(self) -> List[List[Tuple[float, float, float]]]:
        """
        Get fingertip positions for all detected hands.
        
        Returns:
            List of hands, each containing 5 fingertip positions (thumb to pinky)
        """
        all_landmarks = self.get_all_landmarks()
        fingertips = []
        
        for landmarks in all_landmarks:
            hand_fingertips = []
            for idx in config.FINGERTIP_LANDMARKS:
                if idx < len(landmarks):
                    hand_fingertips.append(landmarks[idx])
            fingertips.append(hand_fingertips)
        
        return fingertips
    
    def get_palm_center(self, hand_index: int = 0) -> Optional[Tuple[float, float, float]]:
        """
        Calculate the palm center for a specific hand.
        
        Args:
            hand_index: Index of the hand (0 or 1)
        
        Returns:
            (x, y, z) palm center position or None
        """
        all_landmarks = self.get_all_landmarks()
        
        if hand_index >= len(all_landmarks):
            return None
        
        landmarks = all_landmarks[hand_index]
        palm_points = []
        
        for idx in config.PALM_LANDMARKS:
            if idx < len(landmarks):
                palm_points.append(landmarks[idx])
        
        if not palm_points:
            return None
        
        # Calculate centroid
        x = sum(p[0] for p in palm_points) / len(palm_points)
        y = sum(p[1] for p in palm_points) / len(palm_points)
        z = sum(p[2] for p in palm_points) / len(palm_points)
        
        return (x, y, z)
    
    def get_all_palm_centers(self) -> List[Tuple[float, float, float]]:
        """
        Get palm centers for all detected hands.
        
        Returns:
            List of (x, y, z) palm center positions
        """
        centers = []
        for i in range(self.get_hand_count()):
            center = self.get_palm_center(i)
            if center:
                centers.append(center)
        return centers
    
    def estimate_hand_depth(self, hand_index: int = 0) -> float:
        """
        Estimate depth of a hand using size and z-coordinates.
        
        Args:
            hand_index: Index of the hand
        
        Returns:
            Estimated depth value (0 = neutral, negative = closer, positive = farther)
        """
        all_landmarks = self.get_all_landmarks()
        
        if hand_index >= len(all_landmarks):
            return 0.0
        
        landmarks = all_landmarks[hand_index]
        
        # Method 1: Hand size (wrist to middle finger MCP distance)
        if len(landmarks) >= 10:
            wrist = landmarks[0]
            middle_mcp = landmarks[9]
            dx = wrist[0] - middle_mcp[0]
            dy = wrist[1] - middle_mcp[1]
            hand_size = np.sqrt(dx**2 + dy**2)
            # Normalize: larger hand = closer (negative depth)
            size_depth = (150.0 - hand_size) * 1.5
        else:
            size_depth = 0.0
        
        # Method 2: Average z-coordinate
        avg_z = sum(lm[2] for lm in landmarks) / len(landmarks)
        z_depth = avg_z * 2.0  # Scale for more sensitivity
        
        # Combine estimates (weight size more heavily)
        combined_depth = size_depth * 0.7 + z_depth * 0.3
        
        return combined_depth
    
    def get_all_interaction_points(self) -> List[Tuple[float, float, float]]:
        """
        Get all points that can interact with drum pads.
        Includes fingertips and palm centers.
        
        Returns:
            List of all interaction points (x, y, z)
        """
        points = []
        
        # Add all fingertips
        fingertips = self.get_fingertip_positions()
        for hand_tips in fingertips:
            points.extend(hand_tips)
        
        # Add palm centers
        palm_centers = self.get_all_palm_centers()
        points.extend(palm_centers)
        
        return points
    
    def draw_landmarks(self, frame: np.ndarray, draw_connections: bool = True) -> np.ndarray:
        """
        Draw hand landmarks on frame for debugging.
        
        Args:
            frame: Frame to draw on
            draw_connections: Whether to draw connections between landmarks
        
        Returns:
            Frame with landmarks drawn
        """
        if not self.results or not self.results.hand_landmarks:
            return frame
        
        h, w, _ = frame.shape
        
        # Define connections between landmarks
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (5, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (9, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (0, 17),  # Wrist to pinky base
        ]
        
        for hand_landmarks in self.results.hand_landmarks:
            # Extract pixel coordinates
            points = []
            for lm in hand_landmarks:
                x, y = int(lm.x * w), int(lm.y * h)
                points.append((x, y))
            
            # Draw connections
            if draw_connections:
                for start, end in connections:
                    if start < len(points) and end < len(points):
                        cv2.line(frame, points[start], points[end], (0, 255, 0), 2)
            
            # Draw points
            for i, (x, y) in enumerate(points):
                color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (0, 255, 0)
                cv2.circle(frame, (x, y), 5, color, -1)
        
        return frame
    
    def release(self) -> None:
        """Release resources."""
        if self.detector:
            self.detector.close()
