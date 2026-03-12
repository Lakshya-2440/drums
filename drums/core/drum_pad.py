"""
DrumPad class representing a virtual drum pad in 3D space.
"""
import time
from typing import Tuple, Optional
import config
from utils.math_helpers import lerp, ease_out_quad, ease_in_out_quad


class DrumPad:
    """
    Represents a single virtual drum pad with position, appearance,
    and animation state.
    """
    
    # States
    STATE_IDLE = 'idle'
    STATE_TRIGGERED = 'triggered'
    STATE_COOLDOWN = 'cooldown'
    
    def __init__(
        self,
        pad_id: str,
        position: Tuple[float, float, float],
        radius: float,
        color: Tuple[int, int, int],
        sound_id: str,
        name: str = ''
    ):
        """
        Initialize a drum pad.
        
        Args:
            pad_id: Unique identifier for the pad
            position: (x, y, z) position relative to screen center
            radius: Base radius in pixels
            color: BGR color tuple
            sound_id: ID of the sound to play when triggered
            name: Human-readable name for the pad
        """
        self.id = pad_id
        self.x, self.y, self.z = position
        self.base_radius = radius
        self.color = color
        self.sound_id = sound_id
        self.name = name
        
        # State
        self.state = self.STATE_IDLE
        self.enabled = True
        
        # Animation properties
        self.trigger_time: float = 0.0
        self.animation_progress: float = 0.0
        self.last_velocity: float = 0.0
        
        # Current animated values
        self.current_opacity: float = config.IDLE_OPACITY
        self.current_scale: float = 1.0
        self.glow_intensity: float = 0.0
        
        # Cooldown tracking
        self.cooldown_end_time: float = 0.0
    
    @property
    def position(self) -> Tuple[float, float, float]:
        """Get the 3D position of the pad."""
        return (self.x, self.y, self.z)
    
    @property
    def radius(self) -> float:
        """Get the current animated radius."""
        return self.base_radius * self.current_scale
    
    def trigger(self, velocity: float = 1.0) -> bool:
        """
        Trigger the pad with the given velocity.
        
        Args:
            velocity: Trigger velocity (0.0 to 1.0) for volume control
        
        Returns:
            True if successfully triggered, False if in cooldown
        """
        if not self.enabled:
            return False
        
        current_time = time.time()
        
        # Check cooldown
        if self.state == self.STATE_COOLDOWN:
            if current_time < self.cooldown_end_time:
                return False
        
        # Trigger the pad
        self.state = self.STATE_TRIGGERED
        self.trigger_time = current_time
        self.animation_progress = 0.0
        self.last_velocity = max(0.0, min(1.0, velocity))
        
        # Reset animated values for new trigger
        self.current_opacity = config.TRIGGERED_OPACITY
        self.current_scale = 1.0
        self.glow_intensity = 1.0
        
        return True
    
    def update(self, dt: float) -> None:
        """
        Update the pad's animation state.
        
        Args:
            dt: Delta time since last update (seconds)
        """
        if not self.enabled:
            return
        
        current_time = time.time()
        
        if self.state == self.STATE_TRIGGERED:
            elapsed = current_time - self.trigger_time
            
            # Update glow animation
            glow_progress = min(1.0, elapsed / config.GLOW_DURATION)
            if glow_progress < 0.3:
                # Ramp up
                self.current_opacity = lerp(
                    config.IDLE_OPACITY,
                    config.TRIGGERED_OPACITY,
                    ease_out_quad(glow_progress / 0.3)
                )
                self.glow_intensity = ease_out_quad(glow_progress / 0.3)
            else:
                # Fade back
                fade_progress = (glow_progress - 0.3) / 0.7
                self.current_opacity = lerp(
                    config.TRIGGERED_OPACITY,
                    config.IDLE_OPACITY,
                    ease_out_quad(fade_progress)
                )
                self.glow_intensity = 1.0 - ease_out_quad(fade_progress)
            
            # Update scale animation
            scale_progress = min(1.0, elapsed / config.SCALE_DURATION)
            if scale_progress < 0.4:
                # Scale up
                self.current_scale = lerp(
                    1.0,
                    config.SCALE_FACTOR,
                    ease_out_quad(scale_progress / 0.4)
                )
            else:
                # Scale back down
                shrink_progress = (scale_progress - 0.4) / 0.6
                self.current_scale = lerp(
                    config.SCALE_FACTOR,
                    1.0,
                    ease_in_out_quad(shrink_progress)
                )
            
            # Check if animation is complete
            if elapsed >= config.GLOW_DURATION:
                self.state = self.STATE_COOLDOWN
                self.cooldown_end_time = current_time + config.TRIGGER_COOLDOWN
                self.current_opacity = config.IDLE_OPACITY
                self.current_scale = 1.0
                self.glow_intensity = 0.0
        
        elif self.state == self.STATE_COOLDOWN:
            if current_time >= self.cooldown_end_time:
                self.state = self.STATE_IDLE
    
    def is_triggered(self) -> bool:
        """Check if the pad is currently in triggered state."""
        return self.state == self.STATE_TRIGGERED
    
    def can_trigger(self) -> bool:
        """Check if the pad can be triggered right now."""
        if not self.enabled:
            return False
        if self.state == self.STATE_COOLDOWN:
            return time.time() >= self.cooldown_end_time
        return self.state == self.STATE_IDLE
    
    def get_glow_color(self) -> Tuple[int, int, int]:
        """Get the current glow color based on intensity."""
        if self.glow_intensity <= 0:
            return self.color
        
        # Brighten color based on glow intensity
        factor = 1.0 + self.glow_intensity * 0.5
        return (
            min(255, int(self.color[0] * factor)),
            min(255, int(self.color[1] * factor)),
            min(255, int(self.color[2] * factor))
        )
    
    def get_rim_color(self) -> Tuple[int, int, int]:
        """Get the rim highlight color."""
        # Brighter version of the base color
        return (
            min(255, self.color[0] + 80),
            min(255, self.color[1] + 80),
            min(255, self.color[2] + 80)
        )
    
    def reset(self) -> None:
        """Reset the pad to idle state."""
        self.state = self.STATE_IDLE
        self.animation_progress = 0.0
        self.current_opacity = config.IDLE_OPACITY
        self.current_scale = 1.0
        self.glow_intensity = 0.0
        self.cooldown_end_time = 0.0
    
    def toggle_enabled(self) -> None:
        """Toggle the pad on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.reset()
    
    def __repr__(self) -> str:
        return f"DrumPad(id={self.id}, pos=({self.x}, {self.y}, {self.z}), state={self.state})"


def create_pads_from_config() -> list:
    """
    Create DrumPad instances from the configuration.
    
    Returns:
        List of DrumPad instances
    """
    pads = []
    for pad_config in config.DRUM_PADS:
        pad = DrumPad(
            pad_id=pad_config['id'],
            position=pad_config['pos'],
            radius=pad_config['radius'],
            color=pad_config['color'],
            sound_id=pad_config['sound'],
            name=pad_config.get('name', '')
        )
        pads.append(pad)
    return pads
