import json
import os

class SaveManager:
    """Handles game state serialization and deserialization using JSON."""
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        self.save_file = os.path.join(save_dir, "save_slot_1.json")
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"[SaveSystem] Created directory: {self.save_dir}")

    def save_game(self, state_dict):
        """Serializes the provided dictionary to a JSON file."""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(state_dict, f, indent=4)
            print(f"[SaveSystem] Game saved to {self.save_file}")
            return True
        except Exception as e:
            print(f"[SaveSystem] Error saving game: {e}")
            return False

    def load_game(self):
        """Reads and returns the state dictionary from the JSON file."""
        if not os.path.exists(self.save_file):
            print(f"[SaveSystem] No save file found at {self.save_file}")
            return None
            
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            print(f"[SaveSystem] Game loaded from {self.save_file}")
            return data
        except Exception as e:
            print(f"[SaveSystem] Error loading game: {e}")
            return None
