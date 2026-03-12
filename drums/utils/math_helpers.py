"""
Math helper utilities for 3D calculations and interpolation.
"""
import numpy as np
from typing import Tuple, List, Optional
from collections import deque


def euclidean_distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate 2D Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def euclidean_distance_3d(p1: Tuple[float, float, float], 
                          p2: Tuple[float, float, float]) -> float:
    """Calculate 3D Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by t (0.0 to 1.0)."""
    return a + (b - a) * max(0.0, min(1.0, t))


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out function for smooth animations."""
    return 1 - (1 - t) ** 2


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out function for smooth animations."""
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out for bouncy animations."""
    if t == 0 or t == 1:
        return t
    c4 = (2 * np.pi) / 3
    return np.power(2, -10 * t) * np.sin((t * 10 - 0.75) * c4) + 1


def sigmoid(x: float, sensitivity: float = 1.0) -> float:
    """Sigmoid function for velocity normalization."""
    return 1 / (1 + np.exp(-x * sensitivity))


class VelocityTracker:
    """Track velocity of a point over time for dynamic effects."""
    
    def __init__(self, history_size: int = 5):
        self.positions: deque = deque(maxlen=history_size)
        self.timestamps: deque = deque(maxlen=history_size)
    
    def update(self, position: Tuple[float, float, float], timestamp: float) -> None:
        """Add a new position with timestamp."""
        self.positions.append(position)
        self.timestamps.append(timestamp)
    
    def get_velocity(self) -> float:
        """Calculate current velocity magnitude."""
        if len(self.positions) < 2:
            return 0.0
        
        # Calculate velocity from last two positions
        p1 = self.positions[-2]
        p2 = self.positions[-1]
        t1 = self.timestamps[-2]
        t2 = self.timestamps[-1]
        
        dt = t2 - t1
        if dt <= 0:
            return 0.0
        
        distance = euclidean_distance_3d(p1, p2)
        return distance / dt
    
    def get_normalized_velocity(self, max_velocity: float = 500.0) -> float:
        """Get velocity normalized to 0.0-1.0 range."""
        velocity = self.get_velocity()
        return min(1.0, velocity / max_velocity)
    
    def clear(self) -> None:
        """Clear position history."""
        self.positions.clear()
        self.timestamps.clear()


def smooth_value(current: float, target: float, smoothing: float = 0.1) -> float:
    """Exponential smoothing for jitter reduction."""
    return current + (target - current) * smoothing


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))


def normalize_angle(angle: float) -> float:
    """Normalize angle to -pi to pi range."""
    while angle > np.pi:
        angle -= 2 * np.pi
    while angle < -np.pi:
        angle += 2 * np.pi
    return angle


def calculate_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate centroid of a list of 2D points."""
    if not points:
        return (0.0, 0.0)
    x = sum(p[0] for p in points) / len(points)
    y = sum(p[1] for p in points) / len(points)
    return (x, y)


def calculate_centroid_3d(points: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    """Calculate centroid of a list of 3D points."""
    if not points:
        return (0.0, 0.0, 0.0)
    x = sum(p[0] for p in points) / len(points)
    y = sum(p[1] for p in points) / len(points)
    z = sum(p[2] for p in points) / len(points)
    return (x, y, z)
