#!/usr/bin/env python3
"""
Interactive Hand-Tracking Drum Pad AR Filter

A real-time augmented reality drum pad application that uses hand tracking
to trigger virtual drum pads with visual effects and audio feedback.

Usage:
    python main.py

Controls:
    Q/ESC   - Quit
    S       - Screenshot
    R       - Start/stop recording
    M       - Mute/unmute audio
    D       - Toggle debug mode
    P       - Toggle pad visibility
    +/-     - Adjust sensitivity
    Space   - Reset pads
    1-8     - Toggle individual pads
    H       - Toggle help panel
"""

import sys
import time
import cv2
import numpy as np

# Import configuration
import config

# Import core modules
from core.hand_tracker import HandTracker
from core.drum_pad import DrumPad, create_pads_from_config
from core.collision_detector import CollisionDetector
from core.coordinate_system import get_pad_screen_position, scale_radius_by_depth

# Import effects
from effects.pad_renderer import PadRenderer

# Import audio
from audio.sound_manager import SoundManager

# Import UI
from ui.overlay import Overlay
from ui.controls import Controls, Action, AppState

# Import utilities
from utils.video_capture import VideoCapture
from utils.video_recorder import VideoRecorder


class DrumPadApp:
    """
    Main application class for the interactive drum pad AR filter.
    """
    
    def __init__(self):
        """Initialize all components."""
        print("=" * 50)
        print("Interactive Drum Pad AR Filter")
        print("=" * 50)
        
        # Application state
        self.state = AppState()
        self.last_time = time.time()
        self.fps = 0.0
        self.fps_update_time = 0.0
        self.frame_count = 0
        
        # Initialize video capture
        print("\n[1/6] Initializing camera...")
        self.video_capture = VideoCapture()
        if not self.video_capture.open():
            print("ERROR: Could not open camera!")
            sys.exit(1)
        
        self.screen_size = self.video_capture.get_resolution()
        print(f"  Camera resolution: {self.screen_size[0]}x{self.screen_size[1]}")
        
        # Initialize hand tracker
        print("\n[2/6] Initializing hand tracker...")
        self.hand_tracker = HandTracker()
        print("  Hand tracking ready")
        
        # Initialize drum pads
        print("\n[3/6] Creating drum pads...")
        self.pads = create_pads_from_config()
        print(f"  Created {len(self.pads)} drum pads")
        
        # Initialize collision detector
        print("\n[4/6] Setting up collision detection...")
        self.collision_detector = CollisionDetector()
        self.collision_detector.set_screen_size(*self.screen_size)
        print("  Collision detection ready")
        
        # Initialize pad renderer
        self.pad_renderer = PadRenderer(self.screen_size)
        
        # Initialize sound manager
        print("\n[5/6] Loading audio system...")
        self.sound_manager = SoundManager()
        print("  Audio system ready")
        
        # Initialize UI components
        print("\n[6/6] Setting up UI...")
        self.overlay = Overlay()
        self.video_recorder = VideoRecorder(
            resolution=self.screen_size
        )
        
        # Initialize controls
        self.controls = Controls()
        self._setup_controls()
        
        print("\n" + "=" * 50)
        print("Ready! Show your hands to play.")
        print("Press 'H' for controls, 'Q' to quit.")
        print("=" * 50 + "\n")
    
    def _setup_controls(self):
        """Set up control callbacks."""
        self.controls.register_callbacks({
            Action.QUIT: self.state.quit,
            Action.SCREENSHOT: lambda: self.video_recorder.save_screenshot(self.current_frame) if hasattr(self, 'current_frame') else None,
            Action.RECORD: self.video_recorder.toggle_recording,
            Action.MUTE: self.sound_manager.toggle_mute,
            Action.DEBUG: self.state.toggle_debug,
            Action.TOGGLE_PADS: self.state.toggle_pads,
            Action.INCREASE_SENSITIVITY: self._increase_sensitivity,
            Action.DECREASE_SENSITIVITY: self._decrease_sensitivity,
            Action.RESET: self._reset_pads,
            Action.TOGGLE_HELP: self.overlay.toggle_help,
            Action.TOGGLE_PAD_1: lambda: self._toggle_pad(0),
            Action.TOGGLE_PAD_2: lambda: self._toggle_pad(1),
            Action.TOGGLE_PAD_3: lambda: self._toggle_pad(2),
            Action.TOGGLE_PAD_4: lambda: self._toggle_pad(3),
            Action.TOGGLE_PAD_5: lambda: self._toggle_pad(4),
            Action.TOGGLE_PAD_6: lambda: self._toggle_pad(5),
            Action.TOGGLE_PAD_7: lambda: self._toggle_pad(6),
            Action.TOGGLE_PAD_8: lambda: self._toggle_pad(7),
        })
    
    def _increase_sensitivity(self):
        """Increase collision sensitivity."""
        new_sens = self.state.increase_sensitivity()
        self.collision_detector.collision_threshold = new_sens
    
    def _decrease_sensitivity(self):
        """Decrease collision sensitivity."""
        new_sens = self.state.decrease_sensitivity()
        self.collision_detector.collision_threshold = new_sens
    
    def _toggle_pad(self, index: int):
        """Toggle a specific pad."""
        if 0 <= index < len(self.pads):
            self.pads[index].toggle_enabled()
    
    def _reset_pads(self):
        """Reset all pads to initial state."""
        for pad in self.pads:
            pad.reset()
            pad.enabled = True
        self.pad_renderer.clear_effects()
    
    def _calculate_fps(self, dt: float):
        """Calculate and update FPS."""
        self.frame_count += 1
        self.fps_update_time += dt
        
        if self.fps_update_time >= 0.5:  # Update every 0.5 seconds
            self.fps = self.frame_count / self.fps_update_time
            self.frame_count = 0
            self.fps_update_time = 0.0
    
    def run(self):
        """Main application loop."""
        window_name = "Drum Pad AR Filter"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.screen_size[0], self.screen_size[1])
        
        try:
            while self.state.running:
                # Calculate delta time
                current_time = time.time()
                dt = current_time - self.last_time
                self.last_time = current_time
                
                # Update FPS
                self._calculate_fps(dt)
                
                # Update state
                self.state.update(dt)
                
                # Capture frame
                ret, frame = self.video_capture.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                self.current_frame = frame.copy()
                
                # Process hand tracking
                hands_detected = self.hand_tracker.process_frame(frame)
                
                # Get interaction points
                interaction_points = []
                if hands_detected:
                    interaction_points = self.hand_tracker.get_all_interaction_points()
                
                # Update pads
                for pad in self.pads:
                    pad.update(dt)
                
                # Update effects
                self.pad_renderer.update(dt)
                
                # Check collisions and trigger pads
                if self.state.pads_visible and interaction_points:
                    collisions = self.collision_detector.check_all_collisions(
                        interaction_points,
                        self.pads
                    )
                    
                    for pad, velocity, trigger_point in collisions:
                        if pad.trigger(velocity):
                            # Play sound
                            self.sound_manager.play(pad.sound_id, velocity)
                            # Trigger visual effects
                            self.pad_renderer.trigger_effects(pad, trigger_point)
                
                # Render pads
                if self.state.pads_visible:
                    frame = self.pad_renderer.render(frame, self.pads)
                
                # Draw debug info
                if self.state.debug_mode:
                    # Draw hand landmarks
                    frame = self.hand_tracker.draw_landmarks(frame)
                    # Draw collision zones
                    frame = self.pad_renderer.render_debug(frame, self.pads)
                    # Draw interaction points
                    for point in interaction_points:
                        cv2.circle(frame, (int(point[0]), int(point[1])), 8, (0, 255, 255), 2)
                
                # Render overlay
                frame = self.overlay.render(
                    frame,
                    fps=self.fps,
                    is_recording=self.video_recorder.is_recording,
                    recording_duration=self.video_recorder.get_recording_duration(),
                    is_muted=self.sound_manager.is_muted(),
                    sensitivity=self.state.sensitivity,
                    sensitivity_show_time=self.state.sensitivity_show_time
                )
                
                # Write to recording if active
                if self.video_recorder.is_recording:
                    self.video_recorder.write_frame(frame)
                
                # Store current frame for screenshots
                self.current_frame = frame.copy()
                
                # Display
                cv2.imshow(window_name, frame)
                
                # Process keyboard input
                action = self.controls.wait_key(1)
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        self.video_capture.release()
        self.hand_tracker.release()
        self.sound_manager.cleanup()
        self.video_recorder.cleanup()
        cv2.destroyAllWindows()
        print("Done!")


def main():
    """Entry point."""
    app = DrumPadApp()
    app.run()


if __name__ == "__main__":
    main()
