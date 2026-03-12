"""
Collision detection between hand landmarks and drum pads.
"""
import time
from typing import List, Tuple, Optional, Dict
import config
from core.drum_pad import DrumPad
from core.coordinate_system import get_pad_screen_position, scale_radius_by_depth
from utils.math_helpers import euclidean_distance_2d


class CollisionDetector:
    """
    Detects collisions between hand interaction points and drum pads.
    Handles 2D screen distance and Z-depth proximity checking.
    """
    
    def __init__(
        self,
        collision_threshold: float = config.COLLISION_THRESHOLD,
        depth_threshold: float = config.DEPTH_THRESHOLD
    ):
        """
        Initialize the collision detector.
        
        Args:
            collision_threshold: Base distance threshold in pixels
            depth_threshold: Maximum depth difference for collision
        """
        self.collision_threshold = collision_threshold
        self.depth_threshold = depth_threshold
        self.screen_size = config.RESOLUTION
    
    def set_screen_size(self, width: int, height: int) -> None:
        """Update screen size for coordinate calculations."""
        self.screen_size = (width, height)
    
    def check_collision(
        self,
        hand_point: Tuple[float, float, float],
        pad: DrumPad
    ) -> Tuple[bool, float]:
        """
        Check if a hand point collides with a pad.
        
        Args:
            hand_point: (x, y, z) hand position in pixel coordinates
            pad: DrumPad to check against
        
        Returns:
            Tuple of (collision_detected, distance)
        """
        if not pad.enabled or not pad.can_trigger():
            return (False, float('inf'))
        
        # Get pad screen position
        pad_screen_pos = get_pad_screen_position(pad.position, self.screen_size)
        
        # Get scaled pad radius based on depth
        scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
        
        # Calculate 2D screen distance
        hand_2d = (hand_point[0], hand_point[1])
        pad_2d = pad_screen_pos
        screen_distance = euclidean_distance_2d(hand_2d, pad_2d)
        
        # Calculate effective collision zone (pad radius + threshold)
        collision_zone = scaled_radius + self.collision_threshold
        
        # Check Z-depth (if hand is too far in front or behind, no collision)
        hand_z = hand_point[2] if len(hand_point) > 2 else 0
        depth_diff = abs(hand_z - pad.z)
        
        # Collision occurs if within 2D range and depth is acceptable
        is_collision = screen_distance < collision_zone and depth_diff < self.depth_threshold
        
        return (is_collision, screen_distance)
    
    def check_all_collisions(
        self,
        hand_points: List[Tuple[float, float, float]],
        pads: List[DrumPad]
    ) -> List[Tuple[DrumPad, float, Tuple[float, float, float]]]:
        """
        Check all hand points against all pads.
        
        Args:
            hand_points: List of (x, y, z) hand positions
            pads: List of DrumPad instances
        
        Returns:
            List of (pad, velocity, trigger_point) for each collision detected
        """
        collisions = []
        triggered_pads = set()  # Prevent multiple triggers per pad per frame
        
        for pad in pads:
            if not pad.enabled or not pad.can_trigger():
                continue
            
            if pad.id in triggered_pads:
                continue
            
            best_distance = float('inf')
            best_point = None
            
            for point in hand_points:
                is_collision, distance = self.check_collision(point, pad)
                
                if is_collision and distance < best_distance:
                    best_distance = distance
                    best_point = point
            
            if best_point is not None:
                # Calculate velocity (closer = harder hit = louder)
                pad_screen_pos = get_pad_screen_position(pad.position, self.screen_size)
                scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
                
                # Normalize distance to velocity (closer = higher velocity)
                max_range = scaled_radius + self.collision_threshold
                velocity = 1.0 - (best_distance / max_range)
                velocity = max(0.3, min(1.0, velocity))  # Clamp between 0.3 and 1.0
                
                collisions.append((pad, velocity, best_point))
                triggered_pads.add(pad.id)
        
        return collisions
    
    def get_closest_pad(
        self,
        hand_point: Tuple[float, float, float],
        pads: List[DrumPad]
    ) -> Tuple[Optional[DrumPad], float]:
        """
        Find the closest pad to a hand point.
        
        Args:
            hand_point: (x, y, z) hand position
            pads: List of DrumPad instances
        
        Returns:
            Tuple of (closest_pad, distance) or (None, inf) if no pads
        """
        closest_pad = None
        min_distance = float('inf')
        
        for pad in pads:
            if not pad.enabled:
                continue
            
            _, distance = self.check_collision(hand_point, pad)
            
            if distance < min_distance:
                min_distance = distance
                closest_pad = pad
        
        return (closest_pad, min_distance)
    
    def get_collision_zones(
        self,
        pads: List[DrumPad]
    ) -> List[Dict]:
        """
        Get collision zone information for debug visualization.
        
        Args:
            pads: List of DrumPad instances
        
        Returns:
            List of dicts with zone info (center, inner_radius, outer_radius)
        """
        zones = []
        
        for pad in pads:
            if not pad.enabled:
                continue
            
            screen_pos = get_pad_screen_position(pad.position, self.screen_size)
            scaled_radius = scale_radius_by_depth(pad.base_radius, pad.z)
            
            zones.append({
                'center': screen_pos,
                'inner_radius': scaled_radius,
                'outer_radius': scaled_radius + self.collision_threshold,
                'pad_id': pad.id,
                'can_trigger': pad.can_trigger()
            })
        
        return zones
