import os
import pygame

class AssetManager:
    """
    Singleton Asset Manager for high-performance memory caching.
    Ensures zero disk I/O during gameplay.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self._sprites = {}
        self._sounds = {}
        self._total_bytes = 0
        print("[Assets] Asset Manager initialized.")

    def load_directory(self, root_path, default_scales=None):
        """
        Recursively loads all .png and .wav files.
        default_scales: optional dict {file_basename: target_scale}
        """
        if not os.path.exists(root_path):
            print(f"[Assets] Warning: Directory {root_path} not found.")
            return

        default_scales = default_scales or {}
        print(f"[Assets] Preloading assets from '{root_path}'...")
        for root, _, files in os.walk(root_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                full_path = os.path.join(root, file)
                name = os.path.splitext(file)[0]

                if ext == '.png':
                    scale = default_scales.get(name)
                    self.load_sprite(name, full_path, target_scale=scale)
                elif ext == '.wav':
                    self._load_sound(name, full_path)

        self._print_memory_stats()

    def load_sprite(self, name, path, target_scale=None):
        """Loads, scales, and converts an image for high-performance alpha rendering."""
        try:
            if not os.path.exists(path):
                print(f"[Assets] Warning: Sprite file {path} not found.")
                return False
                
            sprite = pygame.image.load(path)
            
            # Apply scaling before convert_alpha to save VRAM and CPU
            if target_scale:
                w, h = sprite.get_size()
                if isinstance(target_scale, (int, float)):
                    new_size = (int(w * target_scale), int(h * target_scale))
                else:
                    new_size = target_scale
                
                # Use smoothscale for high-quality downsampling of large assets
                sprite = pygame.transform.smoothscale(sprite, new_size)
            
            # Final conversion to display format
            sprite = sprite.convert_alpha()
            
            self._sprites[name] = sprite
            self._total_bytes += sprite.get_width() * sprite.get_height() * 4
            return True
        except pygame.error as e:
            print(f"[Assets] Failed to load sprite {path}: {e}")
            return False

    def _load_sound(self, name, path):
        try:
            sound = pygame.mixer.Sound(path)
            self._sounds[name] = sound
            # Estimation of memory usage (raw buffer length)
            self._total_bytes += len(sound.get_raw())
        except pygame.error as e:
            print(f"[Assets] Failed to load sound {path}: {e}")

    def get_sprite(self, name):
        """Fetches a sprite by name from memory."""
        return self._sprites.get(name)

    def get_sound(self, name):
        """Fetches a sound by name from memory."""
        return self._sounds.get(name)

    def _print_memory_stats(self):
        mb = self._total_bytes / (1024 * 1024)
        count = len(self._sprites) + len(self._sounds)
        print(f"[Assets] Successfully cached {count} items.")
        print(f"[Assets] Total memory allocated: {mb:.2f} MB")

    def get_total_memory_usage(self):
        """Returns the total memory used by cached assets in bytes."""
        return self._total_bytes
