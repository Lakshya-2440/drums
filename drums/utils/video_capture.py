"""
Video capture wrapper for webcam access.
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import config


class VideoCapture:
    """
    Wrapper for OpenCV video capture with configuration
    and error handling.
    """
    
    def __init__(
        self,
        camera_id: int = config.CAMERA_ID,
        resolution: Tuple[int, int] = config.RESOLUTION,
        fps: int = config.FPS_TARGET
    ):
        """
        Initialize video capture.
        
        Args:
            camera_id: Camera device ID
            resolution: (width, height) target resolution
            fps: Target frame rate
        """
        self.camera_id = camera_id
        self.target_resolution = resolution
        self.target_fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.actual_resolution = resolution
    
    def open(self) -> bool:
        """
        Open the camera.
        
        Returns:
            True if successful, False otherwise
        """
        # Try to open the camera
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            # Try alternate camera IDs
            for alt_id in [0, 1, 2]:
                if alt_id != self.camera_id:
                    self.cap = cv2.VideoCapture(alt_id)
                    if self.cap.isOpened():
                        print(f"Using alternate camera ID: {alt_id}")
                        break
        
        if not self.cap.isOpened():
            print("Error: Could not open any camera")
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Get actual resolution
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_resolution = (actual_width, actual_height)
        
        print(f"Camera opened: {self.actual_resolution[0]}x{self.actual_resolution[1]}")
        
        return True
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame)
        """
        if self.cap is None or not self.cap.isOpened():
            return (False, None)
        
        ret, frame = self.cap.read()
        
        if not ret:
            return (False, None)
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        return (True, frame)
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get actual camera resolution."""
        return self.actual_resolution
    
    def get_fps(self) -> float:
        """Get actual camera FPS."""
        if self.cap is None:
            return 0.0
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self.cap is not None and self.cap.isOpened()
    
    def release(self) -> None:
        """Release the camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
