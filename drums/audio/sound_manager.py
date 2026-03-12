"""
Sound manager for drum pad audio playback using pygame.
"""
import os
import numpy as np
import pygame
from typing import Dict, Optional
import config


class SoundManager:
    """
    Manages audio playback for drum pads.
    Uses pygame.mixer for low-latency sound playback.
    Supports loading WAV files or generating synthetic sounds as fallback.
    """
    
    def __init__(
        self,
        channels: int = config.AUDIO_CHANNELS,
        sample_rate: int = config.SAMPLE_RATE
    ):
        """
        Initialize the sound manager.
        
        Args:
            channels: Number of audio channels for polyphonic playback
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.muted = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(channels)
        
        # Load sounds
        self._load_sounds()
    
    def _load_sounds(self) -> None:
        """Load drum sounds from files or generate synthetic ones."""
        sound_names = ['kick', 'snare', 'hihat', 'tom1', 'tom2', 'crash', 'clap', 'perc']
        
        for name in sound_names:
            sound_path = os.path.join(config.SOUND_DIRECTORY, f'{name}.wav')
            
            if os.path.exists(sound_path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(sound_path)
                    print(f"Loaded sound: {sound_path}")
                except Exception as e:
                    print(f"Error loading {sound_path}: {e}")
                    self.sounds[name] = self._generate_synthetic_sound(name)
            else:
                # Generate synthetic sound
                self.sounds[name] = self._generate_synthetic_sound(name)
                print(f"Generated synthetic sound for: {name}")
    
    def _generate_synthetic_sound(self, sound_name: str) -> pygame.mixer.Sound:
        """
        Generate a synthetic drum sound.
        
        Args:
            sound_name: Name of the sound to generate
        
        Returns:
            pygame.mixer.Sound object
        """
        duration = 0.3  # seconds
        
        # Get frequency and characteristics based on sound type
        freq = config.SYNTH_FREQUENCIES.get(sound_name, 200)
        
        # Generate samples
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        if sound_name == 'kick':
            # Kick: low frequency with pitch drop
            freq_env = freq * np.exp(-t * 20)
            wave = np.sin(2 * np.pi * freq_env * t)
            envelope = np.exp(-t * 8)
            
        elif sound_name == 'snare':
            # Snare: tone + noise
            tone = np.sin(2 * np.pi * freq * t) * 0.5
            noise = np.random.uniform(-1, 1, len(t)) * 0.5
            wave = tone + noise
            envelope = np.exp(-t * 15)
            
        elif sound_name == 'hihat':
            # Hi-hat: filtered noise
            noise = np.random.uniform(-1, 1, len(t))
            envelope = np.exp(-t * 40)
            wave = noise
            
        elif sound_name in ['tom1', 'tom2']:
            # Toms: sine with pitch drop
            freq_env = freq * np.exp(-t * 10)
            wave = np.sin(2 * np.pi * freq_env * t)
            envelope = np.exp(-t * 10)
            
        elif sound_name == 'crash':
            # Crash: noise with slow decay
            noise = np.random.uniform(-1, 1, len(t))
            wave = noise
            envelope = np.exp(-t * 3)
            
        elif sound_name == 'clap':
            # Clap: noise bursts
            noise = np.random.uniform(-1, 1, len(t))
            # Create multiple attacks
            attacks = np.zeros_like(t)
            for offset in [0, 0.01, 0.02]:
                attack_idx = int(offset * self.sample_rate)
                if attack_idx < len(attacks):
                    attacks[attack_idx:] = 1
            wave = noise * attacks
            envelope = np.exp(-t * 20)
            
        else:  # perc
            # Generic percussion: mid frequency tone
            wave = np.sin(2 * np.pi * freq * t)
            envelope = np.exp(-t * 15)
        
        # Apply envelope
        samples = wave * envelope
        
        # Normalize
        samples = samples / np.max(np.abs(samples)) * 0.8
        
        # Convert to 16-bit stereo
        samples_16bit = (samples * 32767).astype(np.int16)
        stereo = np.column_stack((samples_16bit, samples_16bit))
        
        # Create pygame Sound
        return pygame.mixer.Sound(buffer=stereo.tobytes())
    
    def play(self, sound_id: str, velocity: float = 1.0) -> bool:
        """
        Play a drum sound.
        
        Args:
            sound_id: ID of the sound to play
            velocity: Volume (0.0 to 1.0)
        
        Returns:
            True if sound was played, False otherwise
        """
        if self.muted:
            return False
        
        if sound_id not in self.sounds:
            print(f"Sound not found: {sound_id}")
            return False
        
        sound = self.sounds[sound_id]
        
        # Set volume based on velocity
        volume = max(0.1, min(1.0, velocity))
        sound.set_volume(volume)
        
        # Play on any available channel
        channel = sound.play()
        
        return channel is not None
    
    def mute(self) -> None:
        """Mute all audio."""
        self.muted = True
        pygame.mixer.pause()
    
    def unmute(self) -> None:
        """Unmute audio."""
        self.muted = False
        pygame.mixer.unpause()
    
    def toggle_mute(self) -> bool:
        """
        Toggle mute state.
        
        Returns:
            New mute state (True = muted)
        """
        if self.muted:
            self.unmute()
        else:
            self.mute()
        return self.muted
    
    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return self.muted
    
    def set_master_volume(self, volume: float) -> None:
        """
        Set master volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        pygame.mixer.stop()
    
    def cleanup(self) -> None:
        """Clean up pygame mixer resources."""
        pygame.mixer.quit()
