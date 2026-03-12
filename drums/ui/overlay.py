"""
On-screen overlay display for UI elements.
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import config


class Overlay:
    """
    Renders on-screen UI elements like FPS counter,
    recording indicator, and help text.
    """
    
    def __init__(self):
        """Initialize the overlay renderer."""
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = config.FONT_SCALE
        self.font_thickness = config.FONT_THICKNESS
        self.show_help = False
    
    def draw_fps(self, frame: np.ndarray, fps: float) -> np.ndarray:
        """
        Draw FPS counter.
        
        Args:
            frame: Frame to draw on
            fps: Current FPS value
        
        Returns:
            Frame with FPS drawn
        """
        text = f"FPS: {fps:.1f}"
        pos = config.FPS_POSITION
        
        # Draw shadow
        cv2.putText(
            frame, text,
            (pos[0] + 1, pos[1] + 1),
            self.font, self.font_scale,
            config.UI_SHADOW_COLOR, self.font_thickness + 1
        )
        
        # Draw text
        color = (0, 255, 0) if fps >= 25 else (0, 165, 255) if fps >= 15 else (0, 0, 255)
        cv2.putText(
            frame, text, pos,
            self.font, self.font_scale,
            color, self.font_thickness
        )
        
        return frame
    
    def draw_recording_indicator(
        self,
        frame: np.ndarray,
        is_recording: bool,
        duration: float = 0.0
    ) -> np.ndarray:
        """
        Draw recording indicator.
        
        Args:
            frame: Frame to draw on
            is_recording: Whether recording is active
            duration: Recording duration in seconds
        
        Returns:
            Frame with indicator drawn
        """
        if not is_recording:
            return frame
        
        pos = config.RECORDING_INDICATOR_POSITION
        
        # Blinking red dot
        import time
        if int(time.time() * 2) % 2 == 0:
            cv2.circle(frame, (pos[0] + 8, pos[1] - 5), 8, config.RECORDING_COLOR, -1)
        
        # Recording text with duration
        text = f"REC {duration:.1f}s"
        cv2.putText(
            frame, text,
            (pos[0] + 22, pos[1]),
            self.font, self.font_scale,
            config.RECORDING_COLOR, self.font_thickness
        )
        
        return frame
    
    def draw_mute_indicator(self, frame: np.ndarray, is_muted: bool) -> np.ndarray:
        """
        Draw mute indicator.
        
        Args:
            frame: Frame to draw on
            is_muted: Whether audio is muted
        
        Returns:
            Frame with indicator drawn
        """
        if not is_muted:
            return frame
        
        pos = config.MUTE_INDICATOR_POSITION
        text = "MUTED"
        
        cv2.putText(
            frame, text, pos,
            self.font, self.font_scale,
            (0, 165, 255), self.font_thickness
        )
        
        return frame
    
    def draw_help_panel(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw help panel with keyboard shortcuts.
        
        Args:
            frame: Frame to draw on
        
        Returns:
            Frame with help panel drawn
        """
        if not self.show_help:
            # Just show hint to press H
            hint = "Press 'H' for help"
            h, w = frame.shape[:2]
            cv2.putText(
                frame, hint,
                (w - 180, 30),
                self.font, 0.5,
                (200, 200, 200), 1
            )
            return frame
        
        # Help text
        help_lines = [
            "=== CONTROLS ===",
            "Q/ESC: Quit",
            "S: Screenshot",
            "R: Record",
            "M: Mute/Unmute",
            "D: Debug mode",
            "P: Toggle pads",
            "+/-: Sensitivity",
            "Space: Reset",
            "1-8: Toggle pad",
            "H: Hide help",
        ]
        
        # Calculate panel size
        panel_width = 200
        panel_height = len(help_lines) * 25 + 20
        
        # Draw semi-transparent background
        h, w = frame.shape[:2]
        x = w - panel_width - 20
        y = 20
        
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x, y),
            (x + panel_width, y + panel_height),
            (30, 30, 30),
            -1
        )
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Draw border
        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_width, y + panel_height),
            (100, 100, 100),
            1
        )
        
        # Draw text
        for i, line in enumerate(help_lines):
            text_y = y + 25 + i * 22
            color = (255, 255, 255) if i == 0 else (200, 200, 200)
            scale = 0.55 if i == 0 else 0.45
            cv2.putText(
                frame, line,
                (x + 10, text_y),
                self.font, scale,
                color, 1
            )
        
        return frame
    
    def draw_sensitivity_indicator(
        self,
        frame: np.ndarray,
        sensitivity: float,
        show_time: float = 0.0
    ) -> np.ndarray:
        """
        Draw sensitivity adjustment indicator.
        
        Args:
            frame: Frame to draw on
            sensitivity: Current sensitivity value
            show_time: Time remaining to show indicator
        
        Returns:
            Frame with indicator drawn
        """
        if show_time <= 0:
            return frame
        
        h, w = frame.shape[:2]
        text = f"Sensitivity: {sensitivity:.0f}px"
        
        # Center position
        text_size = cv2.getTextSize(text, self.font, 0.7, 2)[0]
        x = (w - text_size[0]) // 2
        y = h - 50
        
        # Background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - 15, y - 25),
            (x + text_size[0] + 15, y + 10),
            (40, 40, 40),
            -1
        )
        alpha = min(1.0, show_time)
        cv2.addWeighted(overlay, alpha * 0.8, frame, 1 - alpha * 0.8, 0, frame)
        
        # Text
        cv2.putText(
            frame, text,
            (x, y),
            self.font, 0.7,
            (255, 255, 255), 2
        )
        
        return frame
    
    def draw_pad_labels(
        self,
        frame: np.ndarray,
        pad_positions: list,
        pad_names: list
    ) -> np.ndarray:
        """
        Draw pad name labels.
        
        Args:
            frame: Frame to draw on
            pad_positions: List of (x, y) screen positions
            pad_names: List of pad names
        
        Returns:
            Frame with labels drawn
        """
        for pos, name in zip(pad_positions, pad_names):
            if not name:
                continue
            
            text_size = cv2.getTextSize(name, self.font, 0.4, 1)[0]
            x = int(pos[0]) - text_size[0] // 2
            y = int(pos[1]) + 5
            
            # Shadow
            cv2.putText(
                frame, name,
                (x + 1, y + 1),
                self.font, 0.4,
                (0, 0, 0), 2
            )
            
            # Text
            cv2.putText(
                frame, name,
                (x, y),
                self.font, 0.4,
                (255, 255, 255), 1
            )
        
        return frame
    
    def toggle_help(self) -> bool:
        """
        Toggle help panel visibility.
        
        Returns:
            New visibility state
        """
        self.show_help = not self.show_help
        return self.show_help
    
    def render(
        self,
        frame: np.ndarray,
        fps: float = 0.0,
        is_recording: bool = False,
        recording_duration: float = 0.0,
        is_muted: bool = False,
        sensitivity: float = 0.0,
        sensitivity_show_time: float = 0.0
    ) -> np.ndarray:
        """
        Render all overlay elements.
        
        Args:
            frame: Frame to render on
            fps: Current FPS
            is_recording: Recording state
            recording_duration: Recording duration
            is_muted: Mute state
            sensitivity: Current sensitivity
            sensitivity_show_time: Time to show sensitivity indicator
        
        Returns:
            Frame with all overlays
        """
        frame = self.draw_fps(frame, fps)
        frame = self.draw_recording_indicator(frame, is_recording, recording_duration)
        frame = self.draw_mute_indicator(frame, is_muted)
        frame = self.draw_help_panel(frame)
        frame = self.draw_sensitivity_indicator(frame, sensitivity, sensitivity_show_time)
        
        return frame
