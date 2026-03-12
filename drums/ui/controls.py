"""
Keyboard input handler for controlling the application.
"""
import cv2
from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Action(Enum):
    """Enum of possible control actions."""
    QUIT = 'quit'
    SCREENSHOT = 'screenshot'
    RECORD = 'record'
    MUTE = 'mute'
    DEBUG = 'debug'
    TOGGLE_PADS = 'toggle_pads'
    INCREASE_SENSITIVITY = 'increase_sensitivity'
    DECREASE_SENSITIVITY = 'decrease_sensitivity'
    RESET = 'reset'
    TOGGLE_HELP = 'toggle_help'
    TOGGLE_PAD_1 = 'toggle_pad_1'
    TOGGLE_PAD_2 = 'toggle_pad_2'
    TOGGLE_PAD_3 = 'toggle_pad_3'
    TOGGLE_PAD_4 = 'toggle_pad_4'
    TOGGLE_PAD_5 = 'toggle_pad_5'
    TOGGLE_PAD_6 = 'toggle_pad_6'
    TOGGLE_PAD_7 = 'toggle_pad_7'
    TOGGLE_PAD_8 = 'toggle_pad_8'


@dataclass
class KeyBinding:
    """A key binding configuration."""
    key: int
    action: Action
    description: str


class Controls:
    """
    Handles keyboard input and maps keys to actions.
    """
    
    # Default key bindings
    DEFAULT_BINDINGS = [
        KeyBinding(ord('q'), Action.QUIT, "Quit application"),
        KeyBinding(27, Action.QUIT, "Quit (ESC)"),  # ESC key
        KeyBinding(ord('s'), Action.SCREENSHOT, "Take screenshot"),
        KeyBinding(ord('r'), Action.RECORD, "Toggle recording"),
        KeyBinding(ord('m'), Action.MUTE, "Toggle mute"),
        KeyBinding(ord('d'), Action.DEBUG, "Toggle debug mode"),
        KeyBinding(ord('p'), Action.TOGGLE_PADS, "Toggle pad visibility"),
        KeyBinding(ord('+'), Action.INCREASE_SENSITIVITY, "Increase sensitivity"),
        KeyBinding(ord('='), Action.INCREASE_SENSITIVITY, "Increase sensitivity"),
        KeyBinding(ord('-'), Action.DECREASE_SENSITIVITY, "Decrease sensitivity"),
        KeyBinding(ord('_'), Action.DECREASE_SENSITIVITY, "Decrease sensitivity"),
        KeyBinding(ord(' '), Action.RESET, "Reset pads"),
        KeyBinding(ord('h'), Action.TOGGLE_HELP, "Toggle help"),
        KeyBinding(ord('1'), Action.TOGGLE_PAD_1, "Toggle pad 1"),
        KeyBinding(ord('2'), Action.TOGGLE_PAD_2, "Toggle pad 2"),
        KeyBinding(ord('3'), Action.TOGGLE_PAD_3, "Toggle pad 3"),
        KeyBinding(ord('4'), Action.TOGGLE_PAD_4, "Toggle pad 4"),
        KeyBinding(ord('5'), Action.TOGGLE_PAD_5, "Toggle pad 5"),
        KeyBinding(ord('6'), Action.TOGGLE_PAD_6, "Toggle pad 6"),
        KeyBinding(ord('7'), Action.TOGGLE_PAD_7, "Toggle pad 7"),
        KeyBinding(ord('8'), Action.TOGGLE_PAD_8, "Toggle pad 8"),
    ]
    
    def __init__(self):
        """Initialize the controls handler."""
        self.bindings: Dict[int, Action] = {}
        self.callbacks: Dict[Action, Callable] = {}
        
        # Load default bindings
        for binding in self.DEFAULT_BINDINGS:
            self.bindings[binding.key] = binding.action
    
    def register_callback(self, action: Action, callback: Callable) -> None:
        """
        Register a callback for an action.
        
        Args:
            action: The action to register for
            callback: Function to call when action is triggered
        """
        self.callbacks[action] = callback
    
    def register_callbacks(self, callbacks: Dict[Action, Callable]) -> None:
        """
        Register multiple callbacks at once.
        
        Args:
            callbacks: Dict mapping actions to callbacks
        """
        self.callbacks.update(callbacks)
    
    def process_key(self, key: int) -> Optional[Action]:
        """
        Process a key press and trigger associated action.
        
        Args:
            key: OpenCV key code
        
        Returns:
            The action triggered, or None if no action
        """
        if key == -1 or key == 255:
            return None
        
        # Handle different key code formats
        key = key & 0xFF
        
        if key not in self.bindings:
            return None
        
        action = self.bindings[key]
        
        # Call callback if registered
        if action in self.callbacks:
            self.callbacks[action]()
        
        return action
    
    def wait_key(self, timeout_ms: int = 1) -> Optional[Action]:
        """
        Wait for a key press and process it.
        
        Args:
            timeout_ms: Timeout in milliseconds
        
        Returns:
            The action triggered, or None
        """
        key = cv2.waitKey(timeout_ms)
        return self.process_key(key)
    
    def get_action_for_key(self, key: int) -> Optional[Action]:
        """
        Get the action for a key without triggering callback.
        
        Args:
            key: Key code
        
        Returns:
            Associated action or None
        """
        key = key & 0xFF
        return self.bindings.get(key)
    
    def get_bindings_description(self) -> str:
        """
        Get a human-readable description of all bindings.
        
        Returns:
            Formatted string of all key bindings
        """
        lines = ["Keyboard Controls:"]
        for binding in self.DEFAULT_BINDINGS:
            key_name = chr(binding.key) if 32 <= binding.key < 127 else f"[{binding.key}]"
            lines.append(f"  {key_name}: {binding.description}")
        return "\n".join(lines)


class AppState:
    """
    Manages application state that can be modified by controls.
    """
    
    def __init__(self):
        """Initialize application state."""
        self.running = True
        self.debug_mode = False
        self.pads_visible = True
        self.sensitivity = 70.0  # pixels
        self.sensitivity_min = 30.0
        self.sensitivity_max = 150.0
        self.sensitivity_step = 10.0
        self.sensitivity_show_time = 0.0
    
    def quit(self) -> None:
        """Signal application to quit."""
        self.running = False
    
    def toggle_debug(self) -> bool:
        """Toggle debug mode."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
    
    def toggle_pads(self) -> bool:
        """Toggle pad visibility."""
        self.pads_visible = not self.pads_visible
        return self.pads_visible
    
    def increase_sensitivity(self) -> float:
        """Increase collision sensitivity."""
        self.sensitivity = min(
            self.sensitivity_max,
            self.sensitivity + self.sensitivity_step
        )
        self.sensitivity_show_time = 2.0
        return self.sensitivity
    
    def decrease_sensitivity(self) -> float:
        """Decrease collision sensitivity."""
        self.sensitivity = max(
            self.sensitivity_min,
            self.sensitivity - self.sensitivity_step
        )
        self.sensitivity_show_time = 2.0
        return self.sensitivity
    
    def update(self, dt: float) -> None:
        """Update time-based state."""
        if self.sensitivity_show_time > 0:
            self.sensitivity_show_time -= dt
