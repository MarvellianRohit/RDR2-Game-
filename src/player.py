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
        # Try to load real sprite sheets from AssetManager
        from src.asset_manager import AssetManager
        am = AssetManager()
        
        idle_surf = am.get_sprite("outlaw_idle")
        walk_surf = am.get_sprite("outlaw_walk")
        
        # Setup IDLE animations (1 frame)
        if idle_surf:
            w, h = idle_surf.get_width(), idle_surf.get_height()
            for d in ["N", "S", "E", "W"]:
                self.animator.add_animation(f"IDLE_{d}", Animation(idle_surf, w, h, 1, frame_duration=1.0))
        else:
            # Fallback
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(surf, (50, 150, 50), (16, 16), 14)
            for d in ["N", "S", "E", "W"]:
                self.animator.add_animation(f"IDLE_{d}", Animation(surf, 32, 32, 1))

        # Setup WALK animations (4 frames)
        if walk_surf:
            # Assuming horizontal strip: 4 frames
            # Adjust frame dimensions based on sheet width
            frame_w = walk_surf.get_width() // 4
            frame_h = walk_surf.get_height()
            for d in ["N", "S", "E", "W"]:
                self.animator.add_animation(f"WALK_{d}", Animation(walk_surf, frame_w, frame_h, 4, frame_duration=0.15))
        else:
            # Fallback using idle or placeholder
            surf = idle_surf if idle_surf else pygame.Surface((32, 32), pygame.SRCALPHA)
            w, h = surf.get_width(), surf.get_height()
            for d in ["N", "S", "E", "W"]:
                self.animator.add_animation(f"WALK_{d}", Animation(surf, w, h, 1))
        
        self.animator.play("IDLE_S")

    def update(self, dt, world_manager=None, engine=None):
        """Processes input and updates movement/animations with collision detection."""
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
            dx = (move_vec[0] / length) * self.speed * dt
            dy = (move_vec[1] / length) * self.speed * dt
            
            # --- Collision Detection ---
            # Hitbox: centered horizontally, small depth (bottom of sprite)
            # We use world units (1.0 = 1 tile size)
            hitbox_w = 0.4
            hitbox_h = 0.2
            
            # X Movement
            new_x = self.pos[0] + dx
            can_move_x = True
            if world_manager:
                # Boundary check
                min_x, min_y, max_x, max_y = world_manager.get_world_bounds()
                if new_x - hitbox_w/2 < min_x or new_x + hitbox_w/2 > max_x:
                    can_move_x = False
                
                # Solid tile check
                # Check target tile and corners of hitbox
                for check_y in [self.pos[1] - hitbox_h/2, self.pos[1] + hitbox_h/2]:
                    if world_manager.is_solid(new_x + (hitbox_w/2 if dx > 0 else -hitbox_w/2), check_y):
                        can_move_x = False; break
            
            if not can_move_x: print(f"[Collision] Blocked X at {new_x:.2f}")
            if can_move_x: self.pos[0] = new_x

            # Y Movement
            new_y = self.pos[1] + dy
            can_move_y = True
            if world_manager:
                # Boundary check
                min_x, min_y, max_x, max_y = world_manager.get_world_bounds()
                if new_y - hitbox_h/2 < min_y or new_y + hitbox_h/2 > max_y:
                    can_move_y = False
                
                # Solid tile check
                for check_x in [self.pos[0] - hitbox_w/2, self.pos[0] + hitbox_w/2]:
                    if world_manager.is_solid(check_x, new_y + (hitbox_h/2 if dy > 0 else -hitbox_h/2)):
                        can_move_y = False; break

            if not can_move_y: print(f"[Collision] Blocked Y at {new_y:.2f}")
            if can_move_y: self.pos[1] = new_y
            
            self.animator.play(f"WALK_{self.direction}")
        else:
            self.animator.play(f"IDLE_{self.direction}")
            
        if input_mgr.get_action(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1})) == "ACTION_SHOOT":
            # This is a bit hacky because update(dt) doesn't have the event
            # In a real scenario, events are handled by the state
            pass

        self.animator.update(dt)

    def shoot(self, engine, camera):
        """Spawns a bullet toward the mouse cursor."""
        from src.utils import cartesian_to_iso
        from src.input_manager import InputManager
        import math
        
        # 1. Get Mouse Screen Pos via InputManager
        input_mgr = InputManager()
        mx, my = input_mgr.get_mouse_pos()
        
        # 2. Get Player Screen Pos (Visual center)
        iso_x, iso_y = cartesian_to_iso(self.pos[0], self.pos[1])
        screen_x, screen_y = camera.apply(iso_x, iso_y)
        
        # Use animator's current frame data to find the center
        _, rect = self.animator.get_current_frame_data()
        if rect:
            # Sprite is anchored at (screen_x, screen_y) as its bottom-center
            # Visual center is height/2 above that base
            py = screen_y - (rect.height // 2)
            px = screen_x
        else:
            py = screen_y - 32
            px = screen_x
            
        # 3. Calculate Angle in Screen Space
        angle = math.atan2(my - py, mx - px)
        
        # 4. Spawn Bullet via C-Bridge
        # Bullet speed significantly faster than walking (speed=5.0)
        speed_multiplier = 25.0 
        
        bullet = engine.add_entity(ctypes.c_float(self.pos[0]), ctypes.c_float(self.pos[1]), 1)
        if bullet:
            bullet.contents.vx = math.cos(angle) * speed_multiplier
            bullet.contents.vy = math.sin(angle) * speed_multiplier
            camera.add_trauma(0.5)
            print(f"[Shoot] Projectile spawned toward ({mx}, {my}) at {speed_multiplier}u/s")

    def draw(self, screen, camera):
        """Renders the player sprite relative to the camera."""
        from src.utils import cartesian_to_iso
        
        iso_x, iso_y = cartesian_to_iso(self.pos[0], self.pos[1])
        screen_x, screen_y = camera.apply(iso_x, iso_y)
        
        sheet, rect = self.animator.get_current_frame_data()
        if sheet:
            # Anchor by feet: center horizontally, bottom at position
            draw_x = screen_x - (rect.width // 2)
            draw_y = screen_y - rect.height
            screen.blit(sheet, (draw_x, draw_y), area=rect)
        else:
            pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), 18)
