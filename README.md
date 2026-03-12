# Interactive Hand-Tracking Drum Pad AR Filter

An augmented reality drum pad application that uses hand tracking to trigger virtual drum pads with stunning visual effects and audio feedback. Similar to Instagram AR filters!


## Features

- 🖐️ **Real-time Hand Tracking** - Tracks both hands with 21 landmarks each
- 🥁 **8 Virtual Drum Pads** - Positioned in 3D space around you
- ✨ **Beautiful Visual Effects** - Glow, particles, ripples, and animations
- 🔊 **Low-Latency Audio** - 8 unique drum sounds with velocity sensitivity
- 📹 **Video Recording** - Capture your performances
- 📸 **Screenshots** - Save moments with a keypress
- ⚙️ **Customizable** - Adjust sensitivity, toggle pads, debug mode

## Quick Start

### Installation

1. **Clone or download** this project
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### Requirements

- Python 3.8+
- Webcam
- The following packages (installed via requirements.txt):
  - opencv-python >= 4.8.0
  - mediapipe >= 0.10.0
  - numpy >= 1.24.0
  - Pillow >= 10.0.0
  - pygame >= 2.5.0
  - scipy >= 1.11.0

## Controls

| Key         | Action                 |
| ----------- | ---------------------- |
| `Q` / `ESC` | Quit application       |
| `S`         | Take screenshot        |
| `R`         | Start/stop recording   |
| `M`         | Mute/unmute audio      |
| `D`         | Toggle debug mode      |
| `P`         | Toggle pad visibility  |
| `+` / `-`   | Adjust sensitivity     |
| `Space`     | Reset all pads         |
| `1-8`       | Toggle individual pads |
| `H`         | Toggle help panel      |

## How to Play

1. **Position yourself** in front of your webcam
2. **Show your hands** to the camera
3. **Move your fingertips** toward the drum pads
4. Pads will **light up and play sounds** when touched!
5. Hit pads **harder (faster)** for louder sounds

## Drum Pad Layout

```
       [Kick]      [Snare]     [Hi-Hat]
         🟦          🟪          🟧

  [Tom 1]                         [Tom 2]
    🟣                              🟢

      [Crash]      [Clap]       [Perc]
        🟨          🟫           🔵
```

## Adding Custom Sounds

Place your own `.wav` files in the `audio/sounds/` directory:

- `kick.wav` - Bass drum
- `snare.wav` - Snare drum
- `hihat.wav` - Hi-hat cymbal
- `tom1.wav` - High tom
- `tom2.wav` - Mid tom
- `crash.wav` - Crash cymbal
- `clap.wav` - Hand clap
- `perc.wav` - Percussion

If sound files are missing, the app generates synthetic sounds automatically.

## Configuration

Edit `config.py` to customize:

- **Resolution & FPS** - Camera settings
- **Pad positions** - 3D coordinates for each pad
- **Colors** - Pad and effect colors
- **Sensitivity** - Collision detection threshold
- **Effect durations** - Animation timings

## Project Structure

```
drums_anti/
├── main.py              # Entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── README.md            # This file
├── core/                # Core modules
│   ├── hand_tracker.py  # MediaPipe hand tracking
│   ├── drum_pad.py      # DrumPad class
│   ├── collision_detector.py
│   └── coordinate_system.py
├── effects/             # Visual effects
│   ├── visual_effects.py
│   ├── pad_renderer.py
│   └── particle_system.py
├── audio/               # Audio system
│   ├── sound_manager.py
│   └── sounds/          # Sound files
├── ui/                  # User interface
│   ├── overlay.py
│   └── controls.py
├── utils/               # Utilities
│   ├── video_capture.py
│   ├── video_recorder.py
│   └── math_helpers.py
└── outputs/             # Recordings & screenshots
    ├── screenshots/
    └── recordings/
```

## Troubleshooting

### Camera not detected

- Check if another application is using the camera
- Try changing `CAMERA_ID` in `config.py` to `1` or `2`

### Low FPS

- Close other applications
- Reduce resolution in `config.py`
- Disable debug mode (`D` key)

### Hands not tracking

- Ensure good lighting
- Keep hands fully visible in frame
- Avoid fast movements initially

### No sound

- Check if muted (press `M` to unmute)
- Verify pygame is installed correctly
- Check system volume

## Performance Tips

- Use in **well-lit environment** for best tracking
- Keep hands **within the frame**
- Maintain **30+ FPS** for smooth experience
- Close unnecessary applications

## License

MIT License - Feel free to use and modify!

## Credits

- **MediaPipe** by Google for hand tracking
- **OpenCV** for video processing
- **Pygame** for audio playback

---

Made with ❤️ for AR enthusiasts and musicians!
