"""
Video recorder for saving recordings and screenshots.
"""
import cv2
import os
import numpy as np
from datetime import datetime
from typing import Tuple, Optional
import config


class VideoRecorder:
    """
    Records video and captures screenshots with timestamps.
    """
    
    def __init__(
        self,
        output_dir: str = config.RECORDING_DIR,
        screenshot_dir: str = config.SCREENSHOT_DIR,
        resolution: Tuple[int, int] = config.RESOLUTION,
        fps: int = config.FPS_TARGET,
        codec: str = config.VIDEO_CODEC
    ):
        """
        Initialize the video recorder.
        
        Args:
            output_dir: Directory for video recordings
            screenshot_dir: Directory for screenshots
            resolution: (width, height) of recordings
            fps: Recording frame rate
            codec: Video codec (e.g., 'mp4v')
        """
        self.output_dir = output_dir
        self.screenshot_dir = screenshot_dir
        self.resolution = resolution
        self.fps = fps
        self.codec = codec
        
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self.current_filename: Optional[str] = None
        self.frame_count = 0
        
        # Ensure directories exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(screenshot_dir, exist_ok=True)
    
    def start_recording(self) -> str:
        """
        Start a new recording.
        
        Returns:
            Path to the recording file
        """
        if self.is_recording:
            self.stop_recording()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_filename = os.path.join(
            self.output_dir,
            f"drum_session_{timestamp}{config.VIDEO_EXTENSION}"
        )
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.writer = cv2.VideoWriter(
            self.current_filename,
            fourcc,
            self.fps,
            self.resolution
        )
        
        if self.writer.isOpened():
            self.is_recording = True
            self.frame_count = 0
            print(f"Recording started: {self.current_filename}")
        else:
            print("Error: Could not start recording")
            self.current_filename = None
        
        return self.current_filename or ""
    
    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write a frame to the recording.
        
        Args:
            frame: Frame to write
        """
        if not self.is_recording or self.writer is None:
            return
        
        # Resize if necessary
        if frame.shape[1] != self.resolution[0] or frame.shape[0] != self.resolution[1]:
            frame = cv2.resize(frame, self.resolution)
        
        self.writer.write(frame)
        self.frame_count += 1
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop the current recording.
        
        Returns:
            Path to the saved recording file
        """
        if not self.is_recording or self.writer is None:
            return None
        
        self.writer.release()
        self.writer = None
        self.is_recording = False
        
        filename = self.current_filename
        duration = self.frame_count / self.fps if self.fps > 0 else 0
        
        print(f"Recording saved: {filename} ({self.frame_count} frames, {duration:.1f}s)")
        
        self.current_filename = None
        self.frame_count = 0
        
        return filename
    
    def toggle_recording(self) -> bool:
        """
        Toggle recording on/off.
        
        Returns:
            New recording state (True = recording)
        """
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
        
        return self.is_recording
    
    def save_screenshot(self, frame: np.ndarray) -> str:
        """
        Save a screenshot.
        
        Args:
            frame: Frame to save
        
        Returns:
            Path to the saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
        
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved: {filename}")
        
        return filename
    
    def get_recording_duration(self) -> float:
        """
        Get duration of current recording in seconds.
        
        Returns:
            Recording duration in seconds
        """
        if not self.is_recording:
            return 0.0
        return self.frame_count / self.fps if self.fps > 0 else 0.0
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.is_recording:
            self.stop_recording()
