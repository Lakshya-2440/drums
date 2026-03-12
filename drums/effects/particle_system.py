"""
Particle system for drum pad trigger effects.
"""
import random
import math
import time
from typing import List, Tuple, Optional
import numpy as np
import config


class Particle:
    """A single particle in an effect."""
    
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: int = 6,
        lifetime: float = 0.3
    ):
        """
        Initialize a particle.
        
        Args:
            x, y: Initial position
            vx, vy: Velocity components
            color: BGR color
            size: Particle size in pixels
            lifetime: Time until particle dies (seconds)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0.0
        self.alive = True
    
    def update(self, dt: float) -> None:
        """Update particle position and age."""
        if not self.alive:
            return
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        
        # Apply slight gravity/drag
        self.vy += 50 * dt  # Slight downward drift
        self.vx *= 0.98  # Drag
        self.vy *= 0.98
        
        if self.age >= self.lifetime:
            self.alive = False
    
    @property
    def alpha(self) -> float:
        """Get current alpha based on age."""
        if self.age >= self.lifetime:
            return 0.0
        return 1.0 - (self.age / self.lifetime)
    
    @property
    def current_size(self) -> int:
        """Get current size (shrinks as particle ages)."""
        return max(1, int(self.size * self.alpha))
    
    @property
    def current_color(self) -> Tuple[int, int, int]:
        """Get color with applied alpha (for blending)."""
        alpha = self.alpha
        return (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha)
        )


class ParticleEmitter:
    """Emitter that spawns particles at a location."""
    
    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 8,
        speed: float = 150,
        lifetime: float = 0.3,
        size: int = 6
    ):
        """
        Initialize an emitter.
        
        Args:
            x, y: Emission center
            color: Particle color
            count: Number of particles to emit
            speed: Initial particle speed
            lifetime: Particle lifetime
            size: Particle size
        """
        self.x = x
        self.y = y
        self.color = color
        self.particles: List[Particle] = []
        self.alive = True
        
        # Emit particles in a radial pattern
        for i in range(count):
            angle = (2 * math.pi * i / count) + random.uniform(-0.2, 0.2)
            speed_var = speed * random.uniform(0.7, 1.3)
            vx = math.cos(angle) * speed_var
            vy = math.sin(angle) * speed_var
            
            # Slight color variation
            color_var = (
                min(255, max(0, color[0] + random.randint(-20, 20))),
                min(255, max(0, color[1] + random.randint(-20, 20))),
                min(255, max(0, color[2] + random.randint(-20, 20)))
            )
            
            particle = Particle(
                x=x + random.uniform(-5, 5),
                y=y + random.uniform(-5, 5),
                vx=vx,
                vy=vy,
                color=color_var,
                size=size + random.randint(-2, 2),
                lifetime=lifetime * random.uniform(0.8, 1.2)
            )
            self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update all particles."""
        for particle in self.particles:
            particle.update(dt)
        
        # Check if all particles are dead
        if all(not p.alive for p in self.particles):
            self.alive = False
    
    def get_active_particles(self) -> List[Particle]:
        """Get list of active particles for rendering."""
        return [p for p in self.particles if p.alive]


class ParticleSystem:
    """
    Manages multiple particle emitters for the drum pad effects.
    """
    
    def __init__(self, max_emitters: int = 16):
        """
        Initialize the particle system.
        
        Args:
            max_emitters: Maximum number of active emitters
        """
        self.emitters: List[ParticleEmitter] = []
        self.max_emitters = max_emitters
    
    def emit(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = config.PARTICLE_COUNT,
        speed: float = config.PARTICLE_SPEED,
        lifetime: float = config.PARTICLE_LIFETIME,
        size: int = config.PARTICLE_SIZE
    ) -> None:
        """
        Create a new particle emitter at the specified location.
        
        Args:
            x, y: Emission center
            color: Particle color
            count: Number of particles
            speed: Initial speed
            lifetime: Particle lifetime
            size: Particle size
        """
        # Remove oldest emitter if at max
        if len(self.emitters) >= self.max_emitters:
            self.emitters.pop(0)
        
        emitter = ParticleEmitter(
            x=x,
            y=y,
            color=color,
            count=count,
            speed=speed,
            lifetime=lifetime,
            size=size
        )
        self.emitters.append(emitter)
    
    def update(self, dt: float) -> None:
        """Update all emitters and remove dead ones."""
        for emitter in self.emitters:
            emitter.update(dt)
        
        # Remove dead emitters
        self.emitters = [e for e in self.emitters if e.alive]
    
    def get_all_particles(self) -> List[Particle]:
        """Get all active particles from all emitters."""
        particles = []
        for emitter in self.emitters:
            particles.extend(emitter.get_active_particles())
        return particles
    
    def clear(self) -> None:
        """Remove all emitters and particles."""
        self.emitters.clear()
    
    @property
    def particle_count(self) -> int:
        """Get total number of active particles."""
        return sum(len(e.get_active_particles()) for e in self.emitters)


class Ripple:
    """A ripple effect that expands from a center point."""
    
    def __init__(
        self,
        x: float,
        y: float,
        start_radius: float,
        max_radius: float,
        color: Tuple[int, int, int],
        duration: float = 0.4,
        thickness: int = 3
    ):
        """
        Initialize a ripple.
        
        Args:
            x, y: Center position
            start_radius: Initial radius
            max_radius: Final radius
            color: Ripple color
            duration: Time to expand to max radius
            thickness: Line thickness
        """
        self.x = x
        self.y = y
        self.start_radius = start_radius
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.thickness = thickness
        self.age = 0.0
        self.alive = True
    
    def update(self, dt: float) -> None:
        """Update ripple age."""
        self.age += dt
        if self.age >= self.duration:
            self.alive = False
    
    @property
    def progress(self) -> float:
        """Get animation progress (0 to 1)."""
        return min(1.0, self.age / self.duration)
    
    @property
    def current_radius(self) -> float:
        """Get current radius based on progress."""
        return self.start_radius + (self.max_radius - self.start_radius) * self.progress
    
    @property
    def alpha(self) -> float:
        """Get current alpha (fades out as it expands)."""
        return 1.0 - self.progress
    
    @property
    def current_color(self) -> Tuple[int, int, int]:
        """Get color with alpha applied."""
        alpha = self.alpha
        return (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha)
        )


class RippleSystem:
    """Manages ripple effects for pad triggers."""
    
    def __init__(self, max_ripples: int = 24):
        """
        Initialize the ripple system.
        
        Args:
            max_ripples: Maximum number of active ripples
        """
        self.ripples: List[Ripple] = []
        self.max_ripples = max_ripples
    
    def create_ripples(
        self,
        x: float,
        y: float,
        start_radius: float,
        max_radius: float,
        color: Tuple[int, int, int],
        count: int = config.RIPPLE_COUNT,
        duration: float = config.RIPPLE_DURATION
    ) -> None:
        """
        Create a set of ripples at a location.
        
        Args:
            x, y: Center position
            start_radius: Initial radius
            max_radius: Final radius
            color: Ripple color
            count: Number of ripples to create (staggered)
            duration: Total duration
        """
        for i in range(count):
            # Remove oldest if at max
            if len(self.ripples) >= self.max_ripples:
                self.ripples.pop(0)
            
            # Stagger the ripples slightly
            ripple = Ripple(
                x=x,
                y=y,
                start_radius=start_radius,
                max_radius=max_radius,
                color=color,
                duration=duration,
                thickness=max(1, 3 - i)
            )
            # Delay start by staggering age negatively
            ripple.age = -i * 0.05
            self.ripples.append(ripple)
    
    def update(self, dt: float) -> None:
        """Update all ripples and remove dead ones."""
        for ripple in self.ripples:
            ripple.update(dt)
        
        self.ripples = [r for r in self.ripples if r.alive]
    
    def get_active_ripples(self) -> List[Ripple]:
        """Get ripples that are currently visible (age >= 0)."""
        return [r for r in self.ripples if r.alive and r.age >= 0]
    
    def clear(self) -> None:
        """Remove all ripples."""
        self.ripples.clear()
