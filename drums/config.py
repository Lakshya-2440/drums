"""
Configuration settings for Interactive Drum Pad AR Filter
"""
from typing import Tuple, List, Dict, Any

# =============================================================================
# VIDEO SETTINGS
# =============================================================================
CAMERA_ID: int = 0
RESOLUTION: Tuple[int, int] = (1280, 720)
FPS_TARGET: int = 30

# =============================================================================
# HAND TRACKING SETTINGS
# =============================================================================
MAX_HANDS: int = 2
MIN_DETECTION_CONFIDENCE: float = 0.7
MIN_TRACKING_CONFIDENCE: float = 0.7
MODEL_COMPLEXITY: int = 1  # 0=lite, 1=full

# Key landmark indices
FINGERTIP_LANDMARKS: List[int] = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
PALM_LANDMARKS: List[int] = [0, 5, 9, 13, 17]  # wrist + finger MCPs

# =============================================================================
# DRUM PAD CONFIGURATION
# =============================================================================
# Each pad: position (x, y, z), radius, color (BGR), sound name
DRUM_PADS: List[Dict[str, Any]] = [
    {
        'id': 'pad1',
        'pos': (-200, -150, 100),
        'radius': 100,
        'color': (255, 255, 0),      # Cyan (BGR)
        'sound': 'kick',
        'name': 'Kick'
    },
    {
        'id': 'pad2',
        'pos': (0, -150, 150),
        'radius': 100,
        'color': (255, 0, 255),      # Magenta (BGR)
        'sound': 'snare',
        'name': 'Snare'
    },
    {
        'id': 'pad3',
        'pos': (200, -150, 100),
        'radius': 100,
        'color': (0, 128, 255),      # Orange (BGR)
        'sound': 'hihat',
        'name': 'Hi-Hat'
    },
    {
        'id': 'pad4',
        'pos': (-250, 0, 80),
        'radius': 90,
        'color': (255, 0, 128),      # Purple (BGR)
        'sound': 'tom1',
        'name': 'Tom 1'
    },
    {
        'id': 'pad5',
        'pos': (250, 0, 80),
        'radius': 90,
        'color': (128, 255, 0),      # Green (BGR)
        'sound': 'tom2',
        'name': 'Tom 2'
    },
    {
        'id': 'pad6',
        'pos': (-200, 150, 120),
        'radius': 95,
        'color': (0, 255, 255),      # Yellow (BGR)
        'sound': 'crash',
        'name': 'Crash'
    },
    {
        'id': 'pad7',
        'pos': (0, 200, 100),
        'radius': 85,
        'color': (128, 0, 255),      # Pink (BGR)
        'sound': 'clap',
        'name': 'Clap'
    },
    {
        'id': 'pad8',
        'pos': (200, 150, 120),
        'radius': 95,
        'color': (255, 128, 0),      # Blue (BGR)
        'sound': 'perc',
        'name': 'Perc'
    },
]

# =============================================================================
# COLLISION DETECTION
# =============================================================================
COLLISION_THRESHOLD: int = 70  # pixels - distance to trigger
DEPTH_THRESHOLD: int = 150  # depth units - max z difference for collision
TRIGGER_COOLDOWN: float = 0.1  # seconds - prevent rapid re-triggers

# =============================================================================
# VISUAL EFFECTS
# =============================================================================
# Glow effect
GLOW_DURATION: float = 0.3  # seconds
IDLE_OPACITY: float = 0.35
TRIGGERED_OPACITY: float = 1.0

# Scale effect
SCALE_DURATION: float = 0.2  # seconds
SCALE_FACTOR: float = 1.2  # max scale when triggered

# Particle effect
PARTICLE_COUNT: int = 8
PARTICLE_LIFETIME: float = 0.3  # seconds
PARTICLE_SPEED: float = 150  # pixels per second
PARTICLE_SIZE: int = 6

# Ripple effect
RIPPLE_COUNT: int = 3
RIPPLE_DURATION: float = 0.4  # seconds
RIPPLE_MAX_RADIUS: float = 1.8  # multiplier of pad radius

# =============================================================================
# AUDIO SETTINGS
# =============================================================================
AUDIO_CHANNELS: int = 8
SAMPLE_RATE: int = 44100
SOUND_DIRECTORY: str = 'audio/sounds'

# Fallback synthesized sound frequencies (Hz)
SYNTH_FREQUENCIES: Dict[str, float] = {
    'kick': 60,
    'snare': 200,
    'hihat': 8000,
    'tom1': 150,
    'tom2': 120,
    'crash': 500,
    'clap': 1000,
    'perc': 400,
}

# =============================================================================
# UI SETTINGS
# =============================================================================
FONT_SCALE: float = 0.6
FONT_THICKNESS: int = 2
FPS_POSITION: Tuple[int, int] = (20, 30)
RECORDING_INDICATOR_POSITION: Tuple[int, int] = (20, 60)
MUTE_INDICATOR_POSITION: Tuple[int, int] = (20, 90)

# Colors (BGR)
UI_TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)
UI_SHADOW_COLOR: Tuple[int, int, int] = (0, 0, 0)
RECORDING_COLOR: Tuple[int, int, int] = (0, 0, 255)  # Red

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================
SCREENSHOT_DIR: str = 'outputs/screenshots'
RECORDING_DIR: str = 'outputs/recordings'
VIDEO_CODEC: str = 'mp4v'
VIDEO_EXTENSION: str = '.mp4'

# =============================================================================
# DEBUG SETTINGS
# =============================================================================
DEBUG_MODE: bool = False
SHOW_HAND_LANDMARKS: bool = False
SHOW_COLLISION_ZONES: bool = False
