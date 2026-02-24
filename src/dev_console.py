import pygame
from src.localization import LocalizationManager

class DevConsole:
    """A developer console for real-time command execution."""
    def __init__(self, playing_state, font_scale=1.0):
        self.playing = playing_state
        self.active = False
        self.input_text = ""
        self.history = []
        self.history_index = -1
        self._update_fonts(font_scale)
        print(f"[Console] Developer Console initialized (Scale: {font_scale}).")

    def _update_fonts(self, scale):
        self.font = pygame.font.SysFont("Courier", int(24 * scale))

    def handle_input(self, event):
        """Processes keyboard events for the console input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.execute_command(self.input_text)
                    self.history.append(self.input_text)
                    self.history_index = -1
                    self.input_text = ""
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_UP:
                if self.history:
                    if self.history_index == -1:
                        self.history_index = len(self.history) - 1
                    else:
                        self.history_index = max(0, self.history_index - 1)
                    self.input_text = self.history[self.history_index]
            elif event.key == pygame.K_DOWN:
                if self.history:
                    if self.history_index != -1:
                        self.history_index += 1
                        if self.history_index >= len(self.history):
                            self.history_index = -1
                            self.input_text = ""
                        else:
                            self.input_text = self.history[self.history_index]
            else:
                # Handle text input
                if event.unicode and event.unicode.isprintable() and event.unicode != '`':
                    self.input_text += event.unicode
        return False

    def execute_command(self, cmd_str):
        """Parses and executes a command string."""
        parts = cmd_str.lower().split()
        if not parts: return
        
        loc = LocalizationManager()
        cmd = parts[0]
        args = parts[1:]
        
        print(loc.get("CONSOLE_EXECUTING", cmd_str))
        
        if cmd == "kill_all":
            if self.playing.engine:
                self.playing.engine.clear_entities()
                print(loc.get("CONSOLE_CLEARED"))
        
        elif cmd == "set_health":
            if args:
                try:
                    val = int(args[0])
                    self.playing.health = max(0, min(100, val))
                    print(loc.get("CONSOLE_HEALTH_SET", self.playing.health))
                except ValueError:
                    print(loc.get("CONSOLE_ERR_HEALTH"))
        
        elif cmd == "spawn_item":
            if args and self.playing.engine:
                px, py = self.playing.npc_pos
                self.playing.engine.add_entity(px, py)
                print(loc.get("CONSOLE_SPAWNED", args[0], f"{px:.2f}", f"{py:.2f}"))

        elif cmd == "help":
            print(loc.get("CONSOLE_CMD_HELP"))
        
        else:
            print(loc.get("CONSOLE_UNKNOWN", cmd))

    def draw(self, screen):
        """Renders the console overlay."""
        loc = LocalizationManager()
        scale = self.font.get_height() / 24.0
        screen_w, screen_h = screen.get_size()
        height = int(300 * scale)
        # Background
        overlay = pygame.Surface((screen_w, height), pygame.SRCALPHA)
        overlay.fill((20, 20, 25, 200)) # Dark transparent blue-grey
        screen.blit(overlay, (0, 0))
        
        # Border
        pygame.draw.line(screen, (0, 255, 100), (0, height), (screen_w, height), 2)
        
        # Text
        prompt = loc.get("CONSOLE_PROMPT", self.input_text)
        txt_surf = self.font.render(prompt, True, (0, 255, 100))
        screen.blit(txt_surf, (20, height - (40 * scale)))
        
        # History snippet (last 8)
        line_height = self.font.get_height() + (5 * scale)
        for i, cmd in enumerate(self.history[-8:][::-1]):
            hist_surf = self.font.render(f"  {cmd}", True, (150, 150, 150))
            screen.blit(hist_surf, (20, height - (80 * scale) - (i * line_height)))
