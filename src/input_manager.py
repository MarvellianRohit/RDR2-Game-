import pygame
import json
import os

class InputManager:
    """Manages virtual action mapping and persistent keybindings."""
    _instance = None
    SETTINGS_FILE = "settings.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        
        # Default bindings: mapping virtual actions to physical Pygame key codes
        self.bindings = {
            "ACTION_SHOOT": pygame.K_SPACE,
            "ACTION_PAUSE": pygame.K_ESCAPE,
            "ACTION_INTERACT": pygame.K_e,
            "ACTION_SAVE": pygame.K_F5,
            "ACTION_LOAD": pygame.K_F9,
            "ACTION_CUTSCENE": pygame.K_c,
            "ACTION_CONSOLE": pygame.K_BACKQUOTE,
            "ACTION_MOVE_UP": pygame.K_w,
            "ACTION_MOVE_DOWN": pygame.K_s,
            "ACTION_MOVE_LEFT": pygame.K_a,
            "ACTION_MOVE_RIGHT": pygame.K_d,
            "ACTION_INVENTORY": pygame.K_TAB,
            "ACTION_EDITOR": pygame.K_F1
        }
        
        self.load_settings()
        if not os.path.exists(self.SETTINGS_FILE):
            self.save_settings()
        self._initialized = True
        print("[Input] Input Manager initialized.")

    def load_settings(self):
        """Loads custom bindings from settings.json."""
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    saved_bindings = json.load(f)
                    # Merge saved bindings into current defaults
                    for action, key in saved_bindings.items():
                        if action in self.bindings:
                            self.bindings[action] = key
                print(f"[Input] Settings loaded from {self.SETTINGS_FILE}")
            except Exception as e:
                print(f"[Input] Error loading settings: {e}")

    def save_settings(self):
        """Saves current bindings to settings.json."""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.bindings, f, indent=4)
            print(f"[Input] Settings saved to {self.SETTINGS_FILE}")
        except Exception as e:
            print(f"[Input] Error saving settings: {e}")

    def get_mouse_pos(self):
        """Returns the current screen coordinates of the mouse cursor."""
        return pygame.mouse.get_pos()

    def get_action(self, event):
        """Translates a Pygame event into a virtual action string (if any)."""
        if event.type == pygame.KEYDOWN:
            for action, key in self.bindings.items():
                if event.key == key:
                    return action
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Mouse Button
                return "PLAYER_SHOOT"
        return None

    def is_action_pressed(self, action_name):
        """Checks if the key for a specific action is currently held down."""
        if action_name in self.bindings:
            keys = pygame.key.get_pressed()
            return keys[self.bindings[action_name]]
        return False

    def rebind_key(self, action_name, new_key):
        """Safely updates a binding and persists it."""
        if action_name in self.bindings:
            self.bindings[action_name] = new_key
            self.save_settings()
            return True
        return False
