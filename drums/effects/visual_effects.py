"""
Visual effects for drum pads including glow, color burst, and animations.
"""
import cv2
import numpy as np
from typing import Tuple, List
import config


def apply_glow_effect(
    frame: np.ndarray,
    center: Tuple[int, int],
    radius: int,
    color: Tuple[int, int, int],
    intensity: float = 1.0,
    layers: int = 5
) -> np.ndarray:
    """
    Apply a multi-layer glow effect around a point.
    
    Args:
        frame: Image to draw on
        center: (x, y) center of glow
        radius: Base radius of glow
        color: BGR color
        intensity: Glow intensity (0.0 to 1.0)
        layers: Number of glow layers
    
    Returns:
        Modified frame
    """
    if intensity <= 0:
        return frame
    
    overlay = frame.copy()
    
    for i in range(layers, 0, -1):
        # Each layer is larger and more transparent
        layer_radius = int(radius * (1 + (i / layers) * 0.8))
        layer_alpha = intensity * (1 - (i / (layers + 1)))
        
        # Draw filled circle for glow
        glow_overlay = frame.copy()
        cv2.circle(glow_overlay, center, layer_radius, color, -1)
        
        # Blur for soft glow
        if layer_radius > 20:
            kernel_size = min(31, (layer_radius // 4) * 2 + 1)
            glow_overlay = cv2.GaussianBlur(glow_overlay, (kernel_size, kernel_size), 0)
        
        cv2.addWeighted(glow_overlay, layer_alpha * 0.3, overlay, 1, 0, overlay)
    
    return overlay


def draw_rim_highlight(
    frame: np.ndarray,
    center: Tuple[int, int],
    radius: int,
    color: Tuple[int, int, int],
    thickness: int = 3,
    glow: bool = True
) -> np.ndarray:
    """
    Draw a glowing rim highlight around a pad.
    
    Args:
        frame: Image to draw on
        center: (x, y) center
        radius: Radius of the rim
        color: BGR color
        thickness: Line thickness
        glow: Whether to add glow effect
    
    Returns:
        Modified frame
    """
    if glow:
        # Draw outer glow
        overlay = frame.copy()
        for i in range(3):
            glow_radius = radius + 4 - i
            alpha = 0.2 - i * 0.05
            cv2.circle(overlay, center, glow_radius, color, thickness + 4 - i * 2)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    # Main rim
    cv2.circle(frame, center, radius, color, thickness)
    
    return frame


def create_color_burst(
    size: Tuple[int, int],
    center: Tuple[int, int],
    inner_radius: int,
    outer_radius: int,
    color: Tuple[int, int, int],
    intensity: float = 1.0
) -> np.ndarray:
    """
    Create a color burst effect (expanding ring).
    
    Args:
        size: (width, height) of output image
        center: (x, y) center of burst
        inner_radius: Inner radius of ring
        outer_radius: Outer radius of ring
        color: BGR color
        intensity: Effect intensity
    
    Returns:
        BGRA image with the burst effect
    """
    burst = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    
    # Draw gradient ring
    for r in range(inner_radius, outer_radius):
        # Calculate alpha based on position in ring
        ring_progress = (r - inner_radius) / max(1, outer_radius - inner_radius)
        alpha = int(255 * intensity * (1 - ring_progress) * 0.5)
        
        color_with_alpha = (*color, alpha)
        cv2.circle(burst, center, r, color_with_alpha, 1)
    
    return burst


def blend_additive(
    base: np.ndarray,
    overlay: np.ndarray,
    alpha: float = 1.0
) -> np.ndarray:
    """
    Blend overlay onto base using additive blending.
    
    Args:
        base: Base image
        overlay: Overlay image (same size as base)
        alpha: Overall blend alpha
    
    Returns:
        Blended image
    """
    if overlay.shape[:2] != base.shape[:2]:
        return base
    
    # Ensure same number of channels
    if len(overlay.shape) == 2:
        overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR)
    
    # Additive blend (clamped)
    result = np.clip(base.astype(np.float32) + overlay.astype(np.float32) * alpha, 0, 255)
    return result.astype(np.uint8)


def draw_gradient_circle(
    frame: np.ndarray,
    center: Tuple[int, int],
    radius: int,
    color: Tuple[int, int, int],
    opacity: float = 0.5
) -> np.ndarray:
    """
    Draw a circle with radial gradient (brighter in center).
    
    Args:
        frame: Image to draw on
        center: (x, y) center
        radius: Circle radius
        color: BGR color
        opacity: Overall opacity
    
    Returns:
        Modified frame
    """
    overlay = np.zeros_like(frame, dtype=np.float32)
    
    # Create radial gradient mask
    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    
    # Normalize distance and invert (1 at center, 0 at edge)
    mask = np.clip(1 - dist_from_center / max(radius, 1), 0, 1)
    mask = mask * opacity
    
    # Apply color
    for c in range(3):
        overlay[:, :, c] = mask * color[c]
    
    # Blend
    result = np.clip(frame.astype(np.float32) + overlay, 0, 255)
    return result.astype(np.uint8)


def pulse_effect(
    t: float,
    frequency: float = 2.0,
    amplitude: float = 0.1
) -> float:
    """
    Generate a pulsing value for subtle idle animations.
    
    Args:
        t: Current time
        frequency: Pulse frequency in Hz
        amplitude: Pulse amplitude
    
    Returns:
        Pulse multiplier (around 1.0)
    """
    import math
    return 1.0 + amplitude * math.sin(t * frequency * 2 * math.pi)


class EffectRenderer:
    """
    Renders all visual effects for drum pads.
    """
    
    def __init__(self):
        self.time = 0.0
    
    def update(self, dt: float) -> None:
        """Update internal time for animations."""
        self.time += dt
    
    def render_idle_pad(
        self,
        frame: np.ndarray,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        opacity: float = 0.35
    ) -> np.ndarray:
        """
        Render a pad in idle state with semi-transparent appearance.
        
        Args:
            frame: Frame to render on
            center: Pad center
            radius: Pad radius
            color: Pad color
            opacity: Transparency
        
        Returns:
            Modified frame
        """
        overlay = frame.copy()
        
        # Subtle pulse effect
        pulse = pulse_effect(self.time, frequency=1.5, amplitude=0.05)
        display_radius = int(radius * pulse)
        
        # Draw semi-transparent filled circle
        cv2.circle(overlay, center, display_radius, color, -1)
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        
        # Draw glowing rim
        rim_color = (
            min(255, color[0] + 60),
            min(255, color[1] + 60),
            min(255, color[2] + 60)
        )
        frame = draw_rim_highlight(frame, center, display_radius, rim_color, 2, glow=True)
        
        return frame
    
    def render_triggered_pad(
        self,
        frame: np.ndarray,
        center: Tuple[int, int],
        radius: int,
        color: Tuple[int, int, int],
        glow_intensity: float,
        scale: float
    ) -> np.ndarray:
        """
        Render a pad in triggered state with full glow.
        
        Args:
            frame: Frame to render on
            center: Pad center
            radius: Base pad radius
            color: Pad color
            glow_intensity: Current glow intensity (0-1)
            scale: Current scale factor
        
        Returns:
            Modified frame
        """
        display_radius = int(radius * scale)
        
        # Apply glow effect
        if glow_intensity > 0:
            frame = apply_glow_effect(
                frame, center, display_radius,
                color, glow_intensity, layers=4
            )
        
        # Draw main pad at higher opacity
        overlay = frame.copy()
        opacity = 0.4 + glow_intensity * 0.6
        cv2.circle(overlay, center, display_radius, color, -1)
        cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
        
        # Bright rim
        bright_color = (
            min(255, int(color[0] * 1.5)),
            min(255, int(color[1] * 1.5)),
            min(255, int(color[2] * 1.5))
        )
        frame = draw_rim_highlight(frame, center, display_radius, bright_color, 3, glow=True)
        
        return frame
