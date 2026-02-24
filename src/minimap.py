import pygame

class Minimap:
    """Provides a top-down 2D tactical view of the isometric world."""
    def __init__(self, size=200):
        self.size = size
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self.scale = 10  # 1 tile = 10 pixels
        self.center = size // 2
        print(f"[Minimap] Minimap initialized ({size}x{size}).")

    def render(self, screen, player_pos, entities_head=None, static_npcs=None):
        """
        Projects world coordinates to top-down 2D.
        player_pos: (x, y) cartesian
        entities_head: C-engine entity list head (ctypes)
        static_npcs: list of (x, y, color) tuples
        """
        self.surface.fill((0, 0, 0, 150))
        
        # Draw Border
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, self.size, self.size), 2)
        
        px, py = player_pos
        
        # Draw static NPCs (e.g. Sheriff)
        if static_npcs:
            for nx, ny, color in static_npcs:
                mx = self.center + (nx - px) * self.scale
                my = self.center + (ny - py) * self.scale
                if 0 < mx < self.size and 0 < my < self.size:
                    pygame.draw.circle(self.surface, color, (int(mx), int(my)), 4)
        
        # Draw Player (always center)
        pygame.draw.circle(self.surface, (255, 255, 255), (self.center, self.center), 3)

        # Draw C Entities (Bullets, etc.)
        if entities_head:
            curr = entities_head
            while curr:
                if curr.contents.active:
                    ex, ey = curr.contents.x, curr.contents.y
                    mx = self.center + (ex - px) * self.scale
                    my = self.center + (ey - py) * self.scale
                    if 0 < mx < self.size and 0 < my < self.size:
                        pygame.draw.circle(self.surface, (255, 255, 100), (int(mx), int(my)), 2)
                curr = curr.contents.next

        # Blit to top-right of screen
        screen_w = screen.get_width()
        screen.blit(self.surface, (screen_w - self.size - 20, 20))
