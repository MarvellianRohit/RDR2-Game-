class Camera:
    """A smooth 2D camera that tracks a target using linear interpolation."""
    def __init__(self, screen_width, screen_height, grid_size, tile_width, tile_height):
        self.offset_x = 0
        self.offset_y = 0
        self.target_x = 0
        self.target_y = 0
        self.lerp_speed = 0.1
        self.manual_offset = None # (x, y) override for cutscenes
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate grid boundaries in screen space
        # Cartesian (0,0) is at (screen_width/2, screen_height/4)
        # Cartesian (grid_size, grid_size) is at (screen_width/2, screen_height/4 + grid_size * tile_height)
        # Cartesian (grid_size, 0) is at (screen_width/2 + grid_size * tile_width/2, screen_height/4 + grid_size * tile_height/2)
        # Cartesian (0, grid_size) is at (screen_width/2 - grid_size * tile_width/2, screen_height/4 + grid_size * tile_height/2)
        
        self.min_x = (screen_width // 2) - (grid_size * tile_width // 2)
        self.max_x = (screen_width // 2) + (grid_size * tile_width // 2)
        self.min_y = (screen_height // 4)
        self.max_y = (screen_height // 4) + (grid_size * tile_height)

    def update(self, target_screen_x, target_screen_y):
        """Glides the camera toward the target screen position."""
        # The goal is to center the target on the screen
        # Desired offset is (target_pos - screen_center)
        desired_offset_x = target_screen_x - self.screen_width // 2
        desired_offset_y = target_screen_y - self.screen_height // 2
        
        # Apply Lerp for smoothness
        if self.manual_offset:
            self.offset_x += (self.manual_offset[0] - self.offset_x) * self.lerp_speed
            self.offset_y += (self.manual_offset[1] - self.offset_y) * self.lerp_speed
        else:
            self.offset_x += (desired_offset_x - self.offset_x) * self.lerp_speed
            self.offset_y += (desired_offset_y - self.offset_y) * self.lerp_speed
        
        # Clamping logic to keep the camera within the world bounds
        # Note: This is a simplified clamping and might need adjustment for isometric scale
        # For now, let's just glide toward the target and subtract offsets during rendering.

    def apply(self, x, y):
        """Returns coordinates adjusted by the camera offset."""
        return x - self.offset_x, y - self.offset_y

    def get_viewport_rect(self):
        """Returns a pygame.Rect representing the current visible screen in world space."""
        import pygame
        # viewport is at (offset_x, offset_y) with size (screen_width, screen_height)
        return pygame.Rect(self.offset_x, self.offset_y, self.screen_width, self.screen_height)

    def is_visible(self, iso_x, iso_y, width=64, height=64):
        """
        Checks if an isometric coordinate (iso_x, iso_y) is within the camera's viewport.
        width/height: Bounding box of the sprite to prevent popping at edges.
        """
        import pygame
        # We check against the viewport rect in screen space
        # A simple check: apply the camera offset to iso coords and check screen bounds
        screen_x, screen_y = self.apply(iso_x, iso_y)
        
        # Buffer to prevent "popping" at the edges
        buffer = 100 
        return (screen_x + width + buffer > 0 and screen_x - buffer < self.screen_width and
                screen_y + height + buffer > 0 and screen_y - buffer < self.screen_height)
