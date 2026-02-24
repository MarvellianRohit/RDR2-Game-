import json
from src.localization import LocalizationManager

class DialogueNode:
    """A node in the dialogue tree representing NPC speech and player options."""
    def __init__(self, text, options=None, is_dynamic=False):
        self.text = text
        self.options = options if options else [] # List of strings
        self.children = [] # List of DialogueNode objects
        self.is_dynamic = is_dynamic

    def add_choice(self, response_text, child_node):
        """Adds a player response and the resulting dialogue node."""
        self.options.append(response_text)
        self.children.append(child_node)

class AILink:
    """Handles communication with local LLM server."""
    URL = "http://localhost:8080/api/generate" # Example endpoint

    @staticmethod
    def get_response(persona, reputation, player_input):
        payload = {
            "prompt": f"Persona: {persona}\nReputation: {reputation}\nPlayer: {player_input}\nResponse:",
            "max_tokens": 100,
            "temperature": 0.7
        }
        try:
            # We use a short timeout to prevent game freeze if server is down
            response = requests.post(AILink.URL, json=payload, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
        except Exception as e:
            print(f"[AI Link] Connection failed: {e}")
        return None

class DialogueManager:
    """Handles traversal through the dialogue tree and AI integration."""
    def __init__(self, root_node, persona="Generic NPC", reputation=50):
        self.root = root_node
        self.current_node = root_node
        self.persona = persona
        self.reputation = reputation
        self.is_thinking = False

    def make_choice(self, index):
        """Selects a choice by index (0-based) and moves to that node."""
        if 0 <= index < len(self.current_node.children):
            target = self.current_node.children[index]
            
            # If the choice is a trigger for AI
            if target.is_dynamic:
                return self.handle_ai_choice(index)
            
            self.current_node = target
            return True
        return False

    def handle_ai_choice(self, index):
        """Sends input to LLM and replaces the dynamic node with result."""
        player_input = self.current_node.options[index]
        self.is_thinking = True
        
        reply = AILink.get_response(self.persona, self.reputation, player_input)
        self.is_thinking = False
        
        if reply:
            # Create a real node from the AI reply
            new_node = DialogueNode(reply)
            new_node.add_choice(LocalizationManager().get("UI_END_CONVERSATION"), self.root) # Loop back or end
            self.current_node = new_node
            return True
        else:
            # Fallback to the next static child if AI fails
            if len(self.current_node.children) > index:
                loc = LocalizationManager()
                self.current_node = DialogueNode(loc.get("UI_AI_OFFLINE"))
                self.current_node.add_choice(loc.get("UI_BACK"), self.root)
                return True
        return False

    def is_end(self):
        """Returns True if there are no more responses possible."""
        return len(self.current_node.options) == 0

    def get_text(self):
        loc = LocalizationManager()
        if self.is_thinking:
            return loc.get("UI_THINKING")
        return self.current_node.text

    def get_options(self):
        if self.is_thinking:
            return []
        return self.current_node.options
