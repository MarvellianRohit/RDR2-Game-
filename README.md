# Crimson Trails: A Hybrid Isometric Engine

Crimson Trails is a high-performance, isometric game engine that combines the speed of **C** for core systems with the flexibility of **Python** for game logic and visualization.

## 🚀 Features

- **Hybrid Architecture**: Performance-critical components (Ballistics, Quadtree, Memory Tracking) are written in C and bridged to Python via `ctypes`.
- **Advanced Rendering**:
  - GPU-accelerated post-processing using **ModernGL** (Vignette, Day/Night Tinting).
  - High-fidelity isometric tile projection.
  - Camera culling system to optimize on-screen entity rendering.
- **Dynamic World**:
  - Procedural chunk-based environment loading.
  - A* Pathfinding for NPC intelligence.
  - Real-time AI Director system.
- **Rich UI/Audio**:
  - Vector-based HUD with Health, Ammo, and Minimap.
  - Priority-queued audio system for spatial sound effects.
  - Integrated Developer Console (`~` key).
- **Modding Support**: A secure, sandboxed Python modding API.

## 🛠 Installation & Build

### Prerequisites
- Python 3.9+
- A C compiler (GCC/Clang)
- `pygame`, `moderngl`, `numpy`

### Build and Run
1. Compile the C core:
   ```bash
   make
   ```
2. Start the engine:
   ```bash
   python3 main.py
   ```

## 🎮 Controls
- **WASD / Arrows**: Move Player
- **SPACE**: Shoot
- **E**: Interact / Dialogue
- **TAB**: Inventory
- **ESCAPE**: Pause Menu
- **~**: Developer Console

## 📂 Project Structure
- `/core`: C Source for ballistics, quadtree, and engine internals.
- `/src`: Python components for rendering, input, and game state.
- `/assets`: Sprites, SFX, and localization data.
- `/mods`: Community-created extensions.

---
*Created by Antigravity AI for MarvellianRohit.*
