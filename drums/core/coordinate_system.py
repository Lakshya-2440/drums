"""
3D Coordinate System utilities for projecting pad positions to screen space.
"""
import numpy as np
from typing import Tuple
import config


def project_3d_to_2d(
    point_3d: Tuple[float, float, float],
    screen_center: Tuple[int, int],
    focal_length: float = 500.0
) -> Tuple[int, int]:
    """
    Project a 3D point to 2D screen coordinates using perspective projection.
    
    Args:
        point_3d: (x, y, z) position in 3D space
        screen_center: (cx, cy) center of the screen
        focal_length: Virtual camera focal length for perspective
    
    Returns:
        (screen_x, screen_y) in pixel coordinates
    """
    x, y, z = point_3d
    cx, cy = screen_center
    
    # Avoid division by zero
    z_offset = max(z + focal_length, 1.0)
    
    # Perspective projection
    scale = focal_length / z_offset
    screen_x = int(cx + x * scale)
    screen_y = int(cy + y * scale)
    
    return (screen_x, screen_y)


def get_perspective_scale(z: float, focal_length: float = 500.0) -> float:
    """
    Calculate scale factor based on depth for perspective rendering.
    
    Args:
        z: Depth value (positive = farther from camera)
        focal_length: Virtual camera focal length
    
    Returns:
        Scale factor (1.0 at z=0, smaller for larger z)
    """
    z_offset = max(z + focal_length, 1.0)
    return focal_length / z_offset


def scale_radius_by_depth(radius: float, z: float, focal_length: float = 500.0) -> int:
    """
    Scale a radius based on depth for perspective effect.
    
    Args:
        radius: Original radius in pixels
        z: Depth value
        focal_length: Virtual camera focal length
    
    Returns:
        Scaled radius in pixels
    """
    scale = get_perspective_scale(z, focal_length)
    return max(10, int(radius * scale))


def screen_to_normalized(
    screen_point: Tuple[int, int],
    screen_size: Tuple[int, int]
) -> Tuple[float, float]:
    """
    Convert screen coordinates to normalized coordinates (0-1 range).
    
    Args:
        screen_point: (x, y) in pixel coordinates
        screen_size: (width, height) of screen
    
    Returns:
        (nx, ny) normalized coordinates
    """
    width, height = screen_size
    x, y = screen_point
    return (x / width, y / height)


def normalized_to_screen(
    normalized_point: Tuple[float, float],
    screen_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Convert normalized coordinates to screen coordinates.
    
    Args:
        normalized_point: (nx, ny) in 0-1 range
        screen_size: (width, height) of screen
    
    Returns:
        (x, y) in pixel coordinates
    """
    width, height = screen_size
    nx, ny = normalized_point
    return (int(nx * width), int(ny * height))


def get_pad_screen_position(
    pad_pos_3d: Tuple[float, float, float],
    screen_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Get the screen position for a drum pad.
    
    Args:
        pad_pos_3d: (x, y, z) pad position relative to center
        screen_size: (width, height) of screen
    
    Returns:
        (screen_x, screen_y) absolute screen position
    """
    cx = screen_size[0] // 2
    cy = screen_size[1] // 2
    return project_3d_to_2d(pad_pos_3d, (cx, cy))


def estimate_hand_depth_from_size(
    hand_size: float,
    reference_size: float = 150.0,
    reference_depth: float = 0.0
) -> float:
    """
    Estimate hand depth based on apparent hand size.
    
    Args:
        hand_size: Current measured hand size (e.g., wrist to middle finger distance)
        reference_size: Reference size when hand is at reference_depth
        reference_depth: Depth at reference size
    
    Returns:
        Estimated depth value
    """
    if hand_size <= 0:
        return reference_depth
    
    # Larger hand = closer (negative depth), smaller = farther (positive depth)
    scale_ratio = reference_size / hand_size
    estimated_depth = reference_depth + (scale_ratio - 1.0) * 200.0
    return estimated_depth


def combine_depth_estimates(
    size_based_depth: float,
    z_coord_depth: float,
    size_weight: float = 0.7
) -> float:
    """
    Combine size-based and Z-coordinate based depth estimates.
    
    Args:
        size_based_depth: Depth estimated from hand size
        z_coord_depth: Depth from MediaPipe Z coordinates
        size_weight: Weight for size-based estimate (0-1)
    
    Returns:
        Combined depth estimate
    """
    z_weight = 1.0 - size_weight
    return size_based_depth * size_weight + z_coord_depth * z_weight


def sort_by_depth(items: list, depth_key: str = 'z') -> list:
    """
    Sort items by depth for back-to-front rendering.
    
    Args:
        items: List of items with depth information
        depth_key: Key to access depth value (for dicts) or attribute name
    
    Returns:
        Sorted list (farthest first)
    """
    if not items:
        return []
    
    if isinstance(items[0], dict):
        return sorted(items, key=lambda x: x.get(depth_key, 0), reverse=True)
    else:
        return sorted(items, key=lambda x: getattr(x, depth_key, 0), reverse=True)
