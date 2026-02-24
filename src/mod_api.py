import os
import importlib.util
import sys

# --- Mod Event Registry ---
_SHOOT_HOOKS = []
_DEATH_HOOKS = []

def register_on_player_shoot(func):
    """Decorator to register a function to trigger on player shooting."""
    _SHOOT_HOOKS.append(func)
    return func

def register_on_npc_death(func):
    """Decorator to register a function to trigger on NPC death."""
    _DEATH_HOOKS.append(func)
    return func

# --- Safe API Surface (Exposed to Modders) ---
class ModAPI:
    def __init__(self, engine_proxy):
        self._proxy = engine_proxy

    def spawn_particle(self, x, y, color=0xFFFFFFFF):
        """Safely emit a particle via the C engine."""
        if self._proxy.engine:
            self._proxy.engine.emit(x, y, 0, 0, 1.0, color)

    def play_sound(self, name):
        """Safely play a registered sound effect."""
        from src.asset_manager import AssetManager
        sound = AssetManager().get_sound(name)
        if sound and self._proxy.audio:
            self._proxy.audio.play_sound(sound, priority=2, category="sfx")

    def display_hud_message(self, message, duration=3.0):
        """Safely display a message on the HUD."""
        if hasattr(self._proxy, 'hud'):
            self._proxy.hud.add_message(message, duration)

    def log(self, message):
        """Log a message to the engine console."""
        print(f"[Mod] {message}")

class ModLoader:
    def __init__(self, engine_proxy):
        self.api = ModAPI(engine_proxy)
        self.mods_namespaces = [] # Store namespaces of loaded mods
        print("[Modding] Mod Loader initialized.")

    def load_mods(self, mods_dir="mods"):
        """Scans and loads Python scripts from the mods directory."""
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
            return

        print(f"[Modding] Scanning for mods in '{mods_dir}'...")
        for file in os.listdir(mods_dir):
            if file.endswith(".py") and not file.startswith("__"):
                self._load_mod_file(os.path.join(mods_dir, file))

    def _load_mod_file(self, path):
        mod_name = os.path.basename(path)[:-3]
        try:
            with open(path, 'r') as f:
                code = f.read()

            # Create a restricted namespace
            safe_builtins = {
                'print': self.api.log, # Redirect print to mod log
                'int': int, 'float': float, 'str': str,
                'list': list, 'dict': dict, 'tuple': tuple,
                'range': range, 'len': len, 'abs': abs,
                'min': min, 'max': max, 'round': round,
                'bool': bool, 'enumerate': enumerate,
                'Exception': Exception, 'ValueError': ValueError,
                'TypeError': TypeError, 'IndexError': IndexError,
                'KeyError': KeyError,
                # Prevent import and other dangerous builtins
                '__import__': None,
            }

            namespace = {
                '__builtins__': safe_builtins,
                'api': self.api,
                'register_on_player_shoot': register_on_player_shoot,
                'register_on_npc_death': register_on_npc_death,
            }

            # Execute the mod code in the restricted namespace
            exec(code, namespace)
            self.mods_namespaces.append(namespace)
            print(f"[Modding] Successfully loaded: {mod_name}")
        except Exception as e:
            print(f"[Modding] Error loading mod {mod_name}: {e}")

    def trigger_shoot(self, x, y):
        for hook in _SHOOT_HOOKS:
            try:
                hook(x, y)
            except Exception as e:
                print(f"[Modding] Error in shoot hook: {e}")

    def trigger_death(self, x, y):
        for hook in _DEATH_HOOKS:
            try:
                hook(x, y)
            except Exception as e:
                print(f"[Modding] Error in death hook: {e}")
