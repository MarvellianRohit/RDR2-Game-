from src.animator import Animator, Animation
from src.input_manager import InputManager
import pygame

class Player:
    """Manages player state, movement, and animations."""
    def __init__(self, start_pos, speed=5.0):
        self.pos = list(start_pos) # [x, y] in world coordinates
        self.speed = speed
        self.direction = "S"
        self.animator = Animator()
        self._init_animations()

    def _init_animations(self):
        # Try to load real sprite sheet from AssetManager
        from src.asset_manager import AssetManager
        am = AssetManager()
        surface = am.get_sprite("outlaw_idle")
        
        if not surface:
            # Fallback to placeholder if asset not loaded
            surface = pygame.Surface((128, 32), pygame.SRCALPHA)
            for i in range(4):
                pygame.draw.rect(surface, (50, 150, 50), (i*32, 0, 32, 32))
                pygame.draw.rect(surface, (255, 255, 255), (i*32, 0, 32, 32), 1)

        # In this placeholder logic, we use the same sheet for all states
        # but vary the frame count to simulate different types of anims
        for d in ["N", "S", "E", "W"]:
            self.animator.add_animation(f"IDLE_{d}", Animation(surface, 32, 32, 1, frame_duration=1.0))
            self.animator.add_animation(f"WALK_{d}", Animation(surface, 32, 32, 4 if surface.get_width() >= 128 else 1, frame_duration=0.15))
        
        self.animator.play("IDLE_S")

    def update(self, dt):
        """Processes input and updates movement/animations."""
        input_mgr = InputManager()
        move_vec = [0.0, 0.0]
        
        if input_mgr.is_action_pressed("ACTION_MOVE_UP"):    move_vec[1] -= 1.0; self.direction = "N"
        if input_mgr.is_action_pressed("ACTION_MOVE_DOWN"):  move_vec[1] += 1.0; self.direction = "S"
        if input_mgr.is_action_pressed("ACTION_MOVE_LEFT"):  move_vec[0] -= 1.0; self.direction = "W"
        if input_mgr.is_action_pressed("ACTION_MOVE_RIGHT"): move_vec[0] += 1.0; self.direction = "E"
        
        moving = move_vec[0] != 0 or move_vec[1] != 0
        if moving:
            # Normalize movement vector for consistent diagonal speed
            length = (move_vec[0]**2 + move_vec[1]**2)**0.5
            move_vec[0] = (move_vec[0] / length) * self.speed * dt
            move_vec[1] = (move_vec[1] / length) * self.speed * dt
            
            self.pos[0] += move_vec[0]
            self.pos[1] += move_vec[1]
            self.animator.play(f"WALK_{self.direction}")
        else:
            self.animator.play(f"IDLE_{self.direction}")
            
        self.animator.update(dt)

    def draw(self, screen, camera):
        """Renders the player sprite relative to the camera."""
        from src.utils import cartesian_to_iso
        
        iso_x, iso_y = cartesian_to_iso(self.pos[0], self.pos[1])
        screen_x, screen_y = camera.apply(iso_x, iso_y)
        
        sheet, rect = self.animator.get_current_frame_data()
        if sheet:
            screen.blit(sheet, (screen_x - rect.width//2, screen_y - rect.height), area=rect)
        else:
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), 18)
