# Constants (should ideally be imported from a config, but keeping here for simplicity)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_WIDTH = 64
TILE_HEIGHT = 32

def cartesian_to_iso(x, y):
    """Converts world cartesian coordinates to isometric screen coordinates."""
    iso_x = (x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2)
    return iso_x + SCREEN_WIDTH // 2, iso_y + SCREEN_HEIGHT // 4

def draw_iso_tile(screen, x, y, camera=None, color=None, sprite=None):
    """Renders a single isometric tile with optimization."""
    iso_x, iso_y = cartesian_to_iso(x, y)
    if camera: iso_x, iso_y = camera.apply(iso_x, iso_y)
    
    # Optimization: skip drawing if far off screen
    if iso_x < -TILE_WIDTH or iso_x > SCREEN_WIDTH + TILE_WIDTH or \
       iso_y < -TILE_HEIGHT or iso_y > SCREEN_HEIGHT + TILE_HEIGHT:
        return

    if sprite:
        screen.blit(sprite, (iso_x - TILE_WIDTH // 2, iso_y - TILE_HEIGHT // 2))
    else:
        pts = [
            (iso_x, iso_y - TILE_HEIGHT // 2),
            (iso_x + TILE_WIDTH // 2, iso_y),
            (iso_x, iso_y + TILE_HEIGHT // 2),
            (iso_x - TILE_WIDTH // 2, iso_y)
        ]
        
        import pygame
        if not color:
            color = (80, 80, 80) if (x + y) % 2 == 0 else (70, 70, 70)
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, (60, 60, 60), pts, 1)

def iso_to_cartesian(mx, my, camera):
    """Converts screen mouse coordinates to world cartesian coordinates."""
    # First, undo the camera projection
    # Camera apply does: (iso_x - self.x + self.w//2, iso_y - self.y + self.h//2)
    # We need to reverse:
    iso_x = mx + camera.x - camera.w // 2
    iso_y = my + camera.y - camera.h // 2
    
    # Now undo the isometric projection
    # iso_x - sw/2 = (x - y) * 32
    # iso_y - sh/4 = (x + y) * 16
    
    rel_x = (iso_x - SCREEN_WIDTH // 2) / 32.0
    rel_y = (iso_y - SCREEN_HEIGHT // 4) / 16.0
    
    # rel_x = x - y
    # rel_y = x + y
    # 2x = rel_x + rel_y => x = (rel_x + rel_y) / 2
    # 2y = rel_y - rel_x => y = (rel_y - rel_x) / 2
    
    x = (rel_x + rel_y) / 2.0
    y = (rel_y - rel_x) / 2.0
    return x, y
