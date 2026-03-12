"""
Pad renderer for drawing drum pads with effects.
"""
import cv2
import numpy as np
from typing import List, Tuple
import config
from core.drum_pad import DrumPad
from core.coordinate_system import get_pad_screen_position, scale_radius_by_depth, sort_by_depth
from effects.visual_effects import EffectRenderer
from effects.particle_system import ParticleSystem, RippleSystem


class PadRenderer:
    """
    Renders all drum pads with their visual effects.
    Handles depth sorting and effect composition.
    """
    
    def __init__(self, screen_size: Tuple[int, int]):
        """
        Initialize the pad renderer.
        
        Args:
            screen_size: (width, height) of the display
        """
        self.screen_size = screen_size
        self.effect_renderer = EffectRenderer()
        self.particle_system = ParticleSystem(max_emitters=16)
        self.ripple_system = RippleSystem(max_ripples=24)
    
    def set_screen_size(self, width: int, height: int) -> None:
        """Update screen size."""
        self.screen_size = (width, height)
    
    def update(self, dt: float) -> None:
        """
        Update all effect systems.
        
        Args:
            dt: Delta time in seconds
        """
        self.effect_renderer.update(dt)
        self.particle_system.update(dt)
        self.ripple_system.update(dt)
    
    def trigger_effects(self, pad: DrumPad, trigger_point: Tuple[float, float, float]) -> None:
        """
        Trigger all visual effects for a pad.
        
        Args:
            pad: The triggered pad
            trigger_point: (x, y, z) point where trigger occurred
        """
        # Get screen position
        screen_pos = get_pad_screen_position(pad.position, self.screen_size)
        scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
        
        # Emit particles
        self.particle_system.emit(
            x=screen_pos[0],
            y=screen_pos[1],
            color=pad.color,
            count=config.PARTICLE_COUNT,
            speed=config.PARTICLE_SPEED * (0.8 + pad.last_velocity * 0.4),
            lifetime=config.PARTICLE_LIFETIME,
            size=config.PARTICLE_SIZE
        )
        
        # Create ripples
        self.ripple_system.create_ripples(
            x=screen_pos[0],
            y=screen_pos[1],
            start_radius=scaled_radius,
            max_radius=scaled_radius * config.RIPPLE_MAX_RADIUS,
            color=pad.get_rim_color(),
            count=config.RIPPLE_COUNT,
            duration=config.RIPPLE_DURATION
        )
    
    def render(self, frame: np.ndarray, pads: List[DrumPad]) -> np.ndarray:
        """
        Render all pads to the frame.
        
        Args:
            frame: Frame to render on
            pads: List of DrumPad instances
        
        Returns:
            Frame with pads rendered
        """
        # Sort pads by depth (farthest first)
        sorted_pads = sorted(pads, key=lambda p: p.z, reverse=True)
        
        # Render ripples first (behind pads)
        frame = self._render_ripples(frame)
        
        # Render each pad
        for pad in sorted_pads:
            if not pad.enabled:
                continue
            
            screen_pos = get_pad_screen_position(pad.position, self.screen_size)
            scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
            
            # Apply current scale
            display_radius = int(scaled_radius * pad.current_scale)
            
            if pad.is_triggered():
                frame = self.effect_renderer.render_triggered_pad(
                    frame=frame,
                    center=screen_pos,
                    radius=scaled_radius,
                    color=pad.get_glow_color(),
                    glow_intensity=pad.glow_intensity,
                    scale=pad.current_scale
                )
            else:
                frame = self.effect_renderer.render_idle_pad(
                    frame=frame,
                    center=screen_pos,
                    radius=display_radius,
                    color=pad.color,
                    opacity=pad.current_opacity
                )
        
        # Render particles on top
        frame = self._render_particles(frame)
        
        return frame
    
    def _render_ripples(self, frame: np.ndarray) -> np.ndarray:
        """Render all active ripples."""
        ripples = self.ripple_system.get_active_ripples()
        
        for ripple in ripples:
            if ripple.current_radius < 1:
                continue
            
            # Draw ripple circle with fading opacity
            overlay = frame.copy()
            cv2.circle(
                overlay,
                (int(ripple.x), int(ripple.y)),
                int(ripple.current_radius),
                ripple.color,
                ripple.thickness
            )
            alpha = ripple.alpha * 0.6
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def _render_particles(self, frame: np.ndarray) -> np.ndarray:
        """Render all active particles."""
        particles = self.particle_system.get_all_particles()
        
        for particle in particles:
            if particle.current_size < 1:
                continue
            
            # Draw particle as a small circle
            overlay = frame.copy()
            cv2.circle(
                overlay,
                (int(particle.x), int(particle.y)),
                particle.current_size,
                particle.color,
                -1
            )
            alpha = particle.alpha * 0.8
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def render_debug(self, frame: np.ndarray, pads: List[DrumPad]) -> np.ndarray:
        """
        Render debug information for pads.
        
        Args:
            frame: Frame to render on
            pads: List of DrumPad instances
        
        Returns:
            Frame with debug info
        """
        for pad in pads:
            if not pad.enabled:
                continue
            
            screen_pos = get_pad_screen_position(pad.position, self.screen_size)
            scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
            
            # Draw collision zone
            cv2.circle(
                frame,
                screen_pos,
                scaled_radius + config.COLLISION_THRESHOLD,
                (0, 255, 0) if pad.can_trigger() else (0, 0, 255),
                1
            )
            
            # Draw pad info
            info_text = f"{pad.name}: {pad.state}"
            cv2.putText(
                frame,
                info_text,
                (screen_pos[0] - 40, screen_pos[1] - scaled_radius - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1
            )
        
        return frame
    
    def clear_effects(self) -> None:
        """Clear all active effects."""
        self.particle_system.clear()
        self.ripple_system.clear()
