import pygame
from src.minimap import Minimap
from src.localization import LocalizationManager

class HUDManager:
    """Manages 2D screen-space overlays (Heads-Up Display)."""
    def __init__(self, font_scale=1.0):
        self._update_fonts(font_scale)
        self.minimap = Minimap(200)
        self.messages = [] # List of (text, expiry_time)
        print(f"[HUD] HUD Manager initialized (Scale: {font_scale}).")

    def _update_fonts(self, scale):
        self.font_small = pygame.font.SysFont("Arial", int(24 * scale), bold=True)
        self.font_main = pygame.font.SysFont("Arial", int(36 * scale), bold=True)

    def add_message(self, text, duration=3.0):
        """Adds a temporary message to the HUD."""
        expiry = pygame.time.get_ticks() + (duration * 1000)
        self.messages.append((text, expiry))

    def render(self, screen, health, weapon_node, player_pos, entities_head=None, static_npcs=None, inventory=None, show_inventory=False, time_str="12:00"):
        """Main rendering pass for UI elements."""
        self._update_messages()
        self.draw_health_bar(screen, health)
        self.draw_ammo_counter(screen, weapon_node)
        self.draw_messages(screen)
        self.draw_clock(screen, time_str)
        self.minimap.render(screen, player_pos, entities_head, static_npcs)
        
        if show_inventory and inventory:
            self.draw_inventory(screen, inventory)

    def draw_clock(self, screen, time_str):
        """Displays the formatted in-game time."""
        screen_w, _ = screen.get_size()
        scale = self.font_main.get_height() / 36.0
        
        surf = self.font_main.render(time_str, True, (255, 255, 255))
        rect = surf.get_rect(topright=(screen_w - 50, 50))
        
        # Shadow/Background
        bg_rect = rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect)
        screen.blit(surf, rect)

    def draw_inventory(self, screen, inventory):
        """Renders the 4x6 inventory grid."""
        screen_w, screen_h = screen.get_size()
        scale = self.font_main.get_height() / 36.0
        
        # Grid settings
        rows, cols = inventory.rows, inventory.cols
        slot_size = int(80 * scale)
        padding = int(10 * scale)
        grid_w = cols * slot_size + (cols - 1) * padding
        grid_h = rows * slot_size + (rows - 1) * padding
        
        # Center background
        bg_rect = pygame.Rect(0, 0, grid_w + padding * 4, grid_h + padding * 4)
        bg_rect.center = (screen_w // 2, screen_h // 2)
        
        overlay = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        overlay.fill((20, 20, 25, 230))
        screen.blit(overlay, bg_rect.topleft)
        pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2)
        
        # Header
        loc = LocalizationManager()
        title_surf = self.font_main.render(loc.get("UI_INVENTORY_TITLE", "INVENTORY"), True, (255, 255, 255))
        screen.blit(title_surf, (bg_rect.left + padding * 2, bg_rect.top + padding))

        # Start drawing slots
        start_x = bg_rect.left + padding * 2
        start_y = bg_rect.top + padding * 6
        
        for r in range(rows):
            for c in range(cols):
                slot_rect = pygame.Rect(start_x + c * (slot_size + padding), 
                                        start_y + r * (slot_size + padding), 
                                        slot_size, slot_size)
                
                # Slot background
                pygame.draw.rect(screen, (40, 40, 45), slot_rect)
                pygame.draw.rect(screen, (60, 60, 70), slot_rect, 1)
                
                # Item in slot
                item = inventory.get_item_at(r, c)
                if item:
                    # Draw icon placeholder (colored square for now)
                    icon_rect = slot_rect.inflate(-10, -10)
                    pygame.draw.rect(screen, (80, 80, 150), icon_rect)
                    
                    # Stack size
                    if item.stack_size > 1:
                        count_surf = self.font_small.render(str(item.stack_size), True, (255, 255, 255))
                        screen.blit(count_surf, (slot_rect.right - count_surf.get_width() - 5, 
                                                 slot_rect.bottom - count_surf.get_height() - 5))

    def _update_messages(self):
        now = pygame.time.get_ticks()
        self.messages = [m for m in self.messages if m[1] > now]

    def draw_messages(self, screen):
        if not self.messages:
            return
        
        screen_w, _ = screen.get_size()
        y = 150
        for text, _ in self.messages:
            surf = self.font_main.render(text, True, (255, 255, 255))
            rect = surf.get_rect(center=(screen_w // 2, y))
            # Dark background for readability
            bg_rect = rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect)
            screen.blit(surf, rect)
            y += surf.get_height() + 10

    def draw_health_bar(self, screen, health):
        loc = LocalizationManager()
        scale = self.font_small.get_height() / 24.0
        # Background bar
        bar_width, bar_height = int(300 * scale), int(30 * scale)
        x, y = 50, 50
        pygame.draw.rect(screen, (50, 0, 0), (x, y, bar_width, bar_height))
        
        # Health bar (red)
        health_width = int(bar_width * (max(0, health) / 100))
        pygame.draw.rect(screen, (200, 50, 50), (x, y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        # Label
        text = loc.get("HUD_HEALTH", int(health))
        label = self.font_small.render(text, True, (255, 255, 255))
        screen.blit(label, (x, y - (10 * scale + label.get_height())))

    def draw_ammo_counter(self, screen, weapon_node):
        if not weapon_node:
            return
            
        loc = LocalizationManager()
        weapon = weapon_node
        screen_w, screen_h = screen.get_size()
        
        # Container info
        label_str = loc.get("HUD_LABEL_AMMO")
        name_str = weapon.name.upper()
        ammo_str = f"{weapon.current_ammo}{loc.get('HUD_AMMO_DIVIDER')}{weapon.ammo_capacity}"
        
        txt_label = self.font_small.render(label_str, True, (150, 150, 150))
        txt_name = self.font_main.render(name_str, True, (255, 255, 255))
        txt_ammo = self.font_main.render(ammo_str, True, (200, 200, 100))
        
        ammo_rect = txt_ammo.get_rect(bottomright=(screen_w - 50, screen_h - 50))
        name_rect = txt_name.get_rect(bottomright=(screen_w - 50, ammo_rect.top - 5))
        label_rect = txt_label.get_rect(bottomright=(name_rect.left - 10, name_rect.centery))
        
        # Shadow effects
        offset = 2
        screen.blit(self.font_main.render(name_str, True, (0, 0, 0)), (name_rect.x + offset, name_rect.y + offset))
        screen.blit(txt_name, name_rect)
        
        screen.blit(self.font_main.render(ammo_str, True, (0, 0, 0)), (ammo_rect.x + offset, ammo_rect.y + offset))
        screen.blit(txt_ammo, ammo_rect)
        
        screen.blit(txt_label, label_rect)
