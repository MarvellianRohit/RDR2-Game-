import json
import os

class LocalizationManager:
    """Singleton Manager for handling game strings and internationalization."""
    _instance = None
    _data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalizationManager, cls).__new__(cls)
            # Default to English
            cls._instance.load_language("en_US")
        return cls._instance

    def load_language(self, lang_code):
        """Loads a JSON language file from assets/lang/."""
        path = f"assets/lang/{lang_code}.json"
        if not os.path.exists(path):
            print(f"[Loc] Warning: Language file {path} not found.")
            return

        try:
            with open(path, 'r') as f:
                self._data = json.load(f)
            print(f"[Loc] Loaded language: {lang_code}")
        except Exception as e:
            print(f"[Loc] Failed to load {lang_code}: {e}")

    def get(self, key, *args):
        """Fetches a formatted string by key."""
        text = self._data.get(key, key)
        try:
            return text.format(*args)
        except Exception:
            return text
