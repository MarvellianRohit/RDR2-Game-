import pygame
from src.state_manager import GameState
from src.utils import cartesian_to_iso, iso_to_cartesian, draw_iso_tile, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_WIDTH, TILE_HEIGHT
from src.asset_manager import AssetManager

class EditorState(GameState):
    """In-game level editor for visual world building."""
    def __init__(self, manager, world):
        super().__init__(manager)
        self.world = world
        self.selected_tile = 1 # Default (e.g. Dirt)
        self.hover_pos = (0, 0)
        
        # Tile Palette Definition
        self.palette = [
            {"id": 1, "name": "Dirt", "color": (139, 69, 19)},
            {"id": 2, "name": "Wood", "color": (160, 82, 45)},
            {"id": 3, "name": "Cactus", "color": (34, 139, 34)},
            {"id": 4, "name": "Wall", "color": (105, 105, 105)}
        ]
        
        self.panel_width = 250
        self.font = pygame.font.SysFont("Arial", 18)
        self.font_bold = pygame.font.SysFont("Arial", 20, bold=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1: # Toggle back
                self.manager.pop()
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.world.save_map("assets/maps/world.json")
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Check if clicked on UI Panel
            if mx > SCREEN_WIDTH - self.panel_width:
                self._handle_ui_click(mx, my)
            else:
                # Place tile in world
                tx, ty = self.hover_pos
                self.world.set_tile(tx, ty, self.selected_tile)

    def _handle_ui_click(self, mx, my):
        # Calculate index based on Y position in panel
        y_offset = (my - 100) // 50
        if 0 <= y_offset < len(self.palette):
            self.selected_tile = self.palette[y_offset]["id"]
            
        # Check Save Button (bottom of panel)
        if my > SCREEN_HEIGHT - 60:
            self.world.save_map("assets/maps/world.json")

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        if mx < SCREEN_WIDTH - self.panel_width:
            # We need access to the camera from the underlying PlayingState
            # For simplicity, we'll assume the camera is at index -2 in stack
            playing_state = self.manager._stack[-2]
            tx, ty = iso_to_cartesian(mx, my, playing_state.camera)
            self.hover_pos = (int(tx), int(ty))

    def draw(self, screen):
        # 1. Under-draw the world (from PlayingState)
        playing_state = self.manager._stack[-2]
        playing_state.draw(screen)
        
        # 2. Draw Hover Highlight
        hx, hy = self.hover_pos
        draw_iso_tile(screen, hx, hy, camera=playing_state.camera)
        # Overlay highlight color
        iso_x, iso_y = cartesian_to_iso(hx, hy)
        iso_x, iso_y = playing_state.camera.apply(iso_x, iso_y)
        pts = [
            (iso_x, iso_y - TILE_HEIGHT // 2),
            (iso_x + TILE_WIDTH // 2, iso_y),
            (iso_x, iso_y + TILE_HEIGHT // 2),
            (iso_x - TILE_WIDTH // 2, iso_y)
        ]
        pygame.draw.polygon(screen, (255, 255, 100, 100), pts, 2)
        
        # 3. Draw UI Panel
        panel_rect = pygame.Rect(SCREEN_WIDTH - self.panel_width, 0, self.panel_width, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (30, 30, 30, 220), panel_rect)
        pygame.draw.line(screen, (100, 100, 100), (SCREEN_WIDTH - self.panel_width, 0), (SCREEN_WIDTH - self.panel_width, SCREEN_HEIGHT), 2)
        
        # Title
        title_surf = self.font_bold.render("LEVEL EDITOR", True, (255, 255, 255))
        screen.blit(title_surf, (SCREEN_WIDTH - self.panel_width + 20, 30))
        
        # Tile List
        for i, item in enumerate(self.palette):
            y_pos = 100 + i * 50
            # Selection Box
            if self.selected_tile == item["id"]:
                pygame.draw.rect(screen, (60, 60, 100), (SCREEN_WIDTH - self.panel_width + 10, y_pos, self.panel_width - 20, 40))
            
            # Preview Color
            pygame.draw.rect(screen, item["color"], (SCREEN_WIDTH - self.panel_width + 20, y_pos + 5, 30, 30))
            pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - self.panel_width + 20, y_pos + 5, 30, 30), 1)
            
            label = self.font.render(item["name"], True, (255, 255, 255))
            screen.blit(label, (SCREEN_WIDTH - self.panel_width + 60, y_pos + 10))
            
        # Save Button
        save_btn = pygame.Rect(SCREEN_WIDTH - self.panel_width + 20, SCREEN_HEIGHT - 60, self.panel_width - 40, 40)
        pygame.draw.rect(screen, (20, 100, 20), save_btn)
        save_label = self.font_bold.render("SAVE MAP (Ctrl+S)", True, (255, 255, 255))
        screen.blit(save_label, (save_btn.centerx - save_label.get_width()//2, save_btn.centery - save_label.get_height()//2))

        # Instructions
        instr = self.font.render(f"Grid: {hx}, {hy}", True, (200, 200, 200))
        screen.blit(instr, (20, SCREEN_HEIGHT - 30))
