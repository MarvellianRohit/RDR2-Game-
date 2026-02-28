import ctypes
import os
import sys
import pygame
from src.input_manager import InputManager
from src.inventory_grid import InventoryGrid, Item
from src.time_system import WorldClock
from src.animator import Animation, Animator
from src.player import Player
from src.utils import cartesian_to_iso, iso_to_cartesian, draw_iso_tile, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_WIDTH, TILE_HEIGHT
from src.level_editor import EditorState
import math
import random
from src.logic import GameLogic
from src.event_system import EventManager
from src.state_manager import GameState, StateManager
from src.asset_manager import AssetManager
from src.localization import LocalizationManager
from src.inventory import WeaponWheel
from src.dialogue_system import DialogueNode, DialogueManager
from src.camera import Camera
from src.save_system import SaveManager
from src.audio_manager import AudioManager
from src.ai_director import AIDirector
from src.hud import HUDManager
from src.world_manager import WorldManager
from src.sequencer import CutsceneManager
from src.dev_console import DevConsole
from src.post_processing import PostProcessor
from src.telemetry import TelemetryTracker
from src.mod_api import ModLoader

# --- Engine Bridge (C-to-Python) ---
LIB_PATH = os.path.join(os.getcwd(), "libengine.dylib")

class Vector3(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float)]

class ProjectileInput(ctypes.Structure):
    _fields_ = [("start", Vector3), ("velocity", Vector3)]

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

class AABB(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("w", ctypes.c_float), ("h", ctypes.c_float)]

class Entity(ctypes.Structure):
    pass
Entity._fields_ = [
    ("id", ctypes.c_int),
    ("x", ctypes.c_float),
    ("y", ctypes.c_float),
    ("vx", ctypes.c_float),
    ("vy", ctypes.c_float),
    ("sprite_type", ctypes.c_int),
    ("hitbox_width", ctypes.c_float),
    ("hitbox_height", ctypes.c_float),
    ("hitbox_offset_x", ctypes.c_float),
    ("hitbox_offset_y", ctypes.c_float),
    ("active", ctypes.c_int),
    ("prev", ctypes.c_void_p),
    ("next", ctypes.c_void_p)
]

class QuadNode(ctypes.Structure):
    pass

# --- Asset Mapping ---
SPRITE_MAP = {
    0: "outlaw_idle", # Player
    1: "bullet",
    2: "enemy"
}

class Particle(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float), ("y", ctypes.c_float),
        ("vx", ctypes.c_float), ("vy", ctypes.c_float),
        ("life", ctypes.c_float), ("max_life", ctypes.c_float),
        ("color", ctypes.c_uint32), ("active", ctypes.c_int)
    ]

def load_engine():
    try:
        engine = ctypes.CDLL(LIB_PATH)
        engine.engine_init.argtypes = []
        engine.engine_shutdown.argtypes = []
        engine.add_entity.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_int]
        engine.add_entity.restype = ctypes.POINTER(Entity)
        engine.update_entities.argtypes = [ctypes.c_float]
        engine.get_entity_head.restype = ctypes.POINTER(Entity)
        engine.find_path.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(Point), ctypes.c_int]
        engine.find_path.restype = ctypes.c_int
        engine.check_collision_aabb.argtypes = [AABB, AABB]
        engine.check_collision_aabb.restype = ctypes.c_int
        engine.check_entity_collision.argtypes = [ctypes.c_float] * 12
        engine.check_entity_collision.restype = ctypes.c_int
        engine.create_node.argtypes = [AABB]
        engine.create_node.restype = ctypes.POINTER(QuadNode)
        engine.qt_insert.argtypes = [ctypes.POINTER(QuadNode), ctypes.c_int, ctypes.c_float, ctypes.c_float]
        engine.qt_query.argtypes = [ctypes.POINTER(QuadNode), AABB, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        engine.free_quadtree.argtypes = [ctypes.POINTER(QuadNode)]
        engine.particles_init.argtypes = []
        engine.emit.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_uint32]
        engine.update_particles.argtypes = [ctypes.c_float]
        engine.get_particle_pool.restype = ctypes.POINTER(Particle)
        engine.get_max_particles.restype = ctypes.c_int
        engine.dump_memory_leaks.argtypes = []
        engine.get_entity_count.restype = ctypes.c_int
        engine.get_quadtree_node_count.argtypes = [ctypes.POINTER(QuadNode)]
        engine.get_quadtree_node_count.restype = ctypes.c_int
        engine.get_total_memory_usage.restype = ctypes.c_size_t
        return engine
    except OSError as e:
        print(f"Error: Could not load the C engine library. Details: {e}")
        return None

# --- Configuration & Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
TILE_WIDTH, TILE_HEIGHT = 128, 64
GRID_SIZE = 10
FPS = 60
UI_FONT_SCALE = 1.0 # Global scale for accessibility

COLOR_BG = (15, 15, 20)
COLOR_GRID = (40, 40, 50)
COLOR_TILE = (30, 30, 40)
COLOR_NPC = (200, 50, 50)
COLOR_SHERIFF = (50, 50, 200)
AMBIENT_LIGHT = (20, 20, 30, 110) # Brighter darkness for better grid visibility

# --- Lighting Helper ---
class LightSource:
    def __init__(self, x, y, radius, color=(255, 200, 100)):
        self.pos = (x, y)
        self.radius = radius
        self.mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        # Optimized gradient drawing with very soft falloff
        for r in range(radius, 0, -2):
            # Using a cubic power falloff for a much smoother edge transition
            alpha = int(255 * (1 - (r / radius)) ** 4)
            pygame.draw.circle(self.mask, (*color, alpha), (radius, radius), r)

    def draw(self, darkness_surface, camera=None):
        draw_x, draw_y = self.pos
        if camera: draw_x -= camera.offset_x; draw_y -= camera.offset_y
        darkness_surface.blit(self.mask, (draw_x - self.radius, draw_y - self.radius), special_flags=pygame.BLEND_RGBA_SUB)

# --- Isometric Projection Helpers (Moved to src/utils.py) ---

# --- Tile Color Mapping ---
TILE_COLORS = {
    1: (139, 69, 19),  # Dirt
    2: (160, 82, 45),  # Wood
    3: (34, 139, 34),  # Cactus
    4: (105, 105, 105) # Wall
}

# --- Game States ---

class PlayingState(GameState):
    def __init__(self, manager, engine, audio):
        super().__init__(manager)
        self.engine, self.audio = engine, audio
        self.logic, self.events = GameLogic(), EventManager()
        self.darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        campfire_pos = cartesian_to_iso(5, 5)
        self.campfire = LightSource(campfire_pos[0], campfire_pos[1], 400, (255, 150, 50))
        # Player-attached light source: significantly larger radius and warm color
        self.player_light = LightSource(0, 0, 1600, (255, 220, 150))
        self.grid = (ctypes.c_int * (GRID_SIZE * GRID_SIZE))(*([0] * (GRID_SIZE * GRID_SIZE)))
        
        self.health = 100
        self.player = Player([2.0, 2.0], speed=6.0)
        
        # --- C-Engine Player Entity Setup ---
        if self.engine:
            # Outlaw sprite: 64x128. Hitbox: 32x16 at feet (bottom-center).
            # Offset is relative to the sprite center. 
            # Sprite center is (32, 64). Feet are at (32, 128).
            # So offset_y = 64 (down from center).
            self.player_entity = self.engine.add_entity(2.0, 2.0, 0) # type 0 for player
            if self.player_entity:
                self.player_entity.contents.hitbox_width = 32.0
                self.player_entity.contents.hitbox_height = 16.0
                self.player_entity.contents.hitbox_offset_x = 0.0
                self.player_entity.contents.hitbox_offset_y = -8.0 # Precisely at feet
        
        # NPC Setup (Disabled to resolve duplicate sprite issue)
        self.npc_pos, self.npc_active, self.npc_path, self.move_timer = [5.0, 5.0], False, [], 0
        self.npc_anim = Animator()
        
        # Load NPC sprite for animation
        am = AssetManager()
        npc_surface = am.get_sprite("outlaw_idle")
        if npc_surface:
            # Create a 1-frame idle animation using the loaded surface
            self.npc_anim.add_animation("idle", Animation(npc_surface, npc_surface.get_width(), npc_surface.get_height(), 1))
        
        # Culling Telemetry
        self.drawn_count = 0
        self.culled_count = 0
        self.telemetry_frame_count = 0
        self.weapons = WeaponWheel()
        self.weapons.add_weapon("Cattleman Revolver", 30, 6, 0.4)
        self.weapons.add_weapon("Lancaster Repeater", 45, 14, 0.6)
        self.weapons.add_weapon("Double-Barreled Shotgun", 80, 2, 0.8)
        
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TILE_WIDTH, TILE_HEIGHT)
        self.save_manager = SaveManager()
        self.director = AIDirector()
        self.hud = HUDManager(UI_FONT_SCALE)
        self.world = WorldManager(64)
        self.sequencer = CutsceneManager(self.camera, {"sheriff": self}) # SELF as proxy for pathfinding
        self.console = DevConsole(self, UI_FONT_SCALE)
        self.inventory = InventoryGrid()
        self.inventory.add_item(Item("Health Cure", stack_size=3, max_stack=5))
        self.inventory.add_item(Item("Canned Peaches", stack_size=1, max_stack=10))
        self.inventory.add_item(Item("Revolver Ammo", stack_size=12, max_stack=60))
        self.show_inventory = False
        self.clock = WorldClock()
        self.director_timer = 0
        self.last_qt_node_count = 0
        
        # --- Animation Setup ---
        self.player_anim = Animator()
        # self.npc_anim = Animator() # This line is now redundant due to the user's change
        
        # Load sprites (or create placeholders)
        am = AssetManager()
        player_sheet = am.get_sprite("player_sheet")
        if not player_sheet:
            # Create a procedural placeholder sprite sheet (4 frames: 32x32 each)
            player_sheet = pygame.Surface((128, 32), pygame.SRCALPHA)
            for i in range(4):
                color = (50, 100, 255) if i % 2 == 0 else (70, 120, 255)
                pygame.draw.rect(player_sheet, color, (i*32, 0, 32, 32))
                pygame.draw.rect(player_sheet, (255, 255, 255), (i*32, 0, 32, 32), 1)
            player_sheet = player_sheet.convert_alpha()
        
        self.player_anim.add_animation("idle", Animation(player_sheet, 32, 32, 1, frame_duration=1.0))
        self.player_anim.add_animation("walk", Animation(player_sheet, 32, 32, 4, frame_duration=0.15))
        
        # NPC animations are already initialized from outlaw_idle above (lines 190-197)
        # Avoid overwriting with 32x32 placeholders
        # self.npc_anim.add_animation("idle", Animation(player_sheet, 32, 32, 1, frame_duration=1.0))
        # self.npc_anim.add_animation("walk", Animation(player_sheet, 32, 32, 4, frame_duration=0.15))
        
        self.last_qt_root = None # Placeholder if needed
        
        # Initialize Mod Loader
        self.mod_loader = ModLoader(self)
        self.mod_loader.load_mods()
        
        if self.engine: 
            self.engine.engine_init()
            self.engine.particles_init()
        wind_sound = AssetManager().get_sound("ambient_wind")
        if wind_sound: self.audio.play_sound(wind_sound, category="ambient", loop=-1)

    def handle_event(self, event):
        input_mgr = InputManager()
        action = input_mgr.get_action(event)
        
        if action:
            if action == 'ACTION_SHOOT': self.events.post('ACTION_SHOOT')
            elif action == 'ACTION_PAUSE': self.manager.push(PausedState(self.manager, UI_FONT_SCALE))
            elif action == 'ACTION_INTERACT': self.start_sheriff_dialogue()
            elif action == 'ACTION_SAVE': self.perform_save()
            elif action == 'ACTION_LOAD': self.perform_load()
            elif action == 'ACTION_CUTSCENE':
                self.sequencer.load_timeline("assets/cutscenes/intro.json")
                self.sequencer.start()
                self.manager.push(CutsceneState(self.manager, self))
            elif action == 'ACTION_CONSOLE':
                self.manager.push(ConsoleState(self.manager, self))
            elif action == 'ACTION_EDITOR':
                self.manager.push(EditorState(self.manager, self.world))
            elif action == 'ACTION_INVENTORY': self.show_inventory = not self.show_inventory
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = input_mgr.get_action(event)
            if action == 'PLAYER_SHOOT':
                self.player.shoot(self.engine, self.camera)
            elif event.button == 4: self.weapons.next_weapon()
            elif event.button == 5: self.weapons.previous_weapon()
            else:
                mx, my = pygame.mouse.get_pos()
                tx, ty = iso_to_cartesian(mx, my, self.camera)
                if 0 <= tx < GRID_SIZE and 0 <= ty < GRID_SIZE: self.calculate_npc_path(tx, ty)

    def perform_save(self):
        loc = LocalizationManager()
        state = {"pos": self.player.pos, "health": self.health, "weapon": self.weapons.current_weapon.name}
        if self.save_manager.save_game(state): print(loc.get("UI_SAVE_SUCCESS"))

    def perform_load(self):
        loc = LocalizationManager()
        data = self.save_manager.load_game()
        if data:
            self.player.pos, self.health = data["pos"], data["health"]
            while self.weapons.current_weapon.name != data["weapon"]: self.weapons.next_weapon()
            print(loc.get("UI_LOAD_SUCCESS"))

    def start_sheriff_dialogue(self):
        loc = LocalizationManager()
        # Note: Sheriff is static for now, player approaches him
        sheriff_pos = [2.0, 2.0]
        dist = math.sqrt((self.player.pos[0]-sheriff_pos[0])**2 + (self.player.pos[1]-sheriff_pos[1])**2)
        if dist > 1.5: return # Too far
        
        root = DialogueNode(loc.get("UI_SHERIFF_GREET"))
        root.add_choice(loc.get("UI_CHOICE_PASS"), DialogueNode(loc.get("UI_SHERIFF_PASS")))
        root.add_choice(loc.get("UI_CHOICE_TROUBLE"), DialogueNode(loc.get("UI_SHERIFF_TROUBLE")))
        
        # Add a dynamic AI-driven option
        ai_node = DialogueNode("...", is_dynamic=True)
        root.add_choice(loc.get("UI_CHOICE_AI_BOUNTIES"), ai_node)
        
        self.manager.push(DialogueState(self.manager, DialogueManager(root, persona=loc.get("UI_SHERIFF_NAME"), reputation=100), UI_FONT_SCALE))

    def calculate_npc_path(self, tx, ty):
        if not self.engine: return
        max_len = GRID_SIZE * GRID_SIZE
        path_out = (Point * max_len)()
        count = self.engine.find_path(self.grid, GRID_SIZE, GRID_SIZE, int(self.npc_pos[0]), int(self.npc_pos[1]), tx, ty, path_out, max_len)
        if count > 0: self.npc_path = [(path_out[i].x, path_out[i].y) for i in range(count)]

    def trigger_explosion(self, x, y):
        if not self.engine: return
        for _ in range(50):
            vx, vy = (random.random() - 0.5) * 5.0, (random.random() - 0.5) * 5.0
            self.engine.emit(x, y, vx, vy, 1.0 + random.random(), 0x8B4513FF)

    def update(self, dt):
        self.logic.update(dt)
        self.clock.update(dt)
        if self.engine:
            self.engine.update_entities(ctypes.c_float(dt))
        self.player.update(dt, self.world, self.engine)
        if self.engine and self.player_entity:
            self.player_entity.contents.x = self.player.pos[0]
            self.player_entity.contents.y = self.player.pos[1]
            
        # Update player light position to anchored feet (ISO coordinates)
        px_iso, py_iso = cartesian_to_iso(self.player.pos[0], self.player.pos[1])
        self.player_light.pos = (px_iso, py_iso)
            
        self.npc_anim.update(dt)
        self.director_timer += 1
        
        # Update World/Chunks relative to player
        chunks_changed, loaded, unloaded = self.world.update(self.player.pos)
        
        if self.director_timer >= 60:
            sheriff_pos = [2.0, 2.0]
            self.director.assess_state(sheriff_pos, self.health, self.npc_active)
            self.director_timer = 0
            
        while self.events._queue:
            ev = self.events._queue.popleft()
            if ev.type == 'ACTION_SHOOT' and self.engine:
                # Spawn bullet with sprite_type 1
                self.engine.add_entity(0.0, 0.0, 1)
                shot_sound = AssetManager().get_sound("gunshot")
                if shot_sound: self.audio.play_sound(shot_sound, priority=0, category="sfx")
                
                # Trigger Mod Hooks
                self.mod_loader.trigger_shoot(self.npc_pos[0], self.npc_pos[1])
        
        if self.npc_active and self.npc_path:
            self.move_timer += dt
            self.npc_anim.play("walk")
            if self.move_timer > 0.3:
                p = self.npc_path.pop(0); self.npc_pos = [float(p[0]), float(p[1])]; self.move_timer = 0
        else:
            self.npc_anim.play("idle")
        
        self.camera.update(*cartesian_to_iso(self.player.pos[0], self.player.pos[1]))
        
        if self.engine:
            self.engine.update_entities(0.05, 0.05)
            self.engine.update_particles(dt)
            if self.npc_active:
                # Re-bound Quadtree to active 3x3 chunk area
                bx, by, bw, bh = self.world.get_active_boundary()
                root_boundary = AABB(bx, by, bw, bh)
                qt_root = self.engine.create_node(root_boundary)
                current = self.engine.get_entity_head()
                while current:
                    if current.contents.active: self.engine.qt_insert(qt_root, current.contents.id, current.contents.x, current.contents.y)
                    current = current.contents.next
                npc_box = AABB(self.npc_pos[0], self.npc_pos[1], 0.5, 0.5)
                max_hits = 10
                hits, hit_count = (ctypes.c_int * max_hits)(), ctypes.c_int(0)
                self.engine.qt_query(qt_root, npc_box, hits, ctypes.byref(hit_count), max_hits)
                for i in range(hit_count.value):
                    ent_id = hits[i]; curr = self.engine.get_entity_head()
                    while curr:
                        if curr.contents.id == ent_id and curr.contents.active:
                            if self.engine.check_collision_aabb(npc_box, AABB(curr.contents.x, curr.contents.y, 0.2, 0.2)):
                                print(f"HIT! Bullet {ent_id}."); self.npc_active = False; curr.contents.active = 0
                                self.trigger_explosion(curr.contents.x, curr.contents.y); break
                        curr = curr.contents.next
                    if not self.npc_active: break
                self.last_qt_node_count = self.engine.get_quadtree_node_count(qt_root)
                self.engine.free_quadtree(qt_root)

    def draw(self, screen):
        screen.fill(COLOR_BG)
        
        # 1. Draw Tiles (Bottom Layer)
        cx, cy = self.world.current_chunk
        size = self.world.chunk_size
        for chx, chy in self.world.active_chunks:
            for y in range(chy * size, (chy + 1) * size):
                if abs(y - self.player.pos[1]) > 15: continue 
                for x in range(chx * size, (chx + 1) * size):
                    if abs(x - self.player.pos[0]) > 15: continue
                    tile_type = self.world.get_tile(x, y)
                    color = TILE_COLORS.get(tile_type) if tile_type else None
                    sprite = AssetManager().get_sprite("desert_ground") if not tile_type else None
                    draw_iso_tile(screen, x, y, camera=self.camera, color=color, sprite=sprite)
        
        # 2. Reset Telemetry and Initialize Entity List
        self.drawn_count = 0
        self.culled_count = 0
        entities = []
        
        # Player
        px, py = self.player.pos
        p_iso_x, p_iso_y = cartesian_to_iso(px, py)
        if self.camera.is_visible(p_iso_x, p_iso_y, 64, 64):
            def draw_player(s, c):
                # Explicitly calculate draw coordinates to anchor by feet
                from src.utils import cartesian_to_iso
                iso_x, iso_y = cartesian_to_iso(self.player.pos[0], self.player.pos[1])
                screen_x, screen_y = c.apply(iso_x, iso_y)
                
                sheet, rect = self.player.animator.get_current_frame_data()
                if sheet:
                    # Feet Anchoring: X = screen_x - (w/2), Y = screen_y - h
                    draw_x = screen_x - (rect.width // 2)
                    draw_y = screen_y - rect.height
                    s.blit(sheet, (draw_x, draw_y), area=rect)
                else:
                    pygame.draw.circle(s, (0, 255, 0), (int(screen_x), int(screen_y)), 18)

            entities.append({
                'y': py,
                'type': 'player',
                'draw': draw_player
            })
            self.drawn_count += 1
        else:
            self.culled_count += 1
            
        # NPC
        if self.npc_active:
            nx, ny = self.npc_pos
            n_iso_x, n_iso_y = cartesian_to_iso(nx, ny)
            if self.camera.is_visible(n_iso_x, n_iso_y, 64, 64):
                def draw_npc(s, c):
                    iso_x, iso_y = cartesian_to_iso(self.npc_pos[0], self.npc_pos[1])
                    screen_x, screen_y = c.apply(iso_x, iso_y)
                    sheet, rect = self.npc_anim.get_current_frame_data()
                    if sheet:
                        # Anchor by feet: center horizontally, bottom at position
                        draw_x = screen_x - (rect.width // 2)
                        draw_y = screen_y - rect.height
                        s.blit(sheet, (draw_x, draw_y), area=rect)
                    else:
                        pygame.draw.circle(s, (255, 100, 100), (int(screen_x), int(screen_y)), 15)
                
                entities.append({
                    'y': self.npc_pos[1],
                    'type': 'npc',
                    'draw': draw_npc
                })
                self.drawn_count += 1
            else:
                self.culled_count += 1
            
        # Static Sheriff removed as requested (it was a duplicate)
        # sheriff_pos = [2.0, 2.0]
        # s_iso_x, s_iso_y = cartesian_to_iso(sheriff_pos[0], sheriff_pos[1])
        # if self.camera.is_visible(s_iso_x, s_iso_y, 64, 64):
        #     def draw_sheriff(s, c):
        #         iso_x, iso_y = cartesian_to_iso(sheriff_pos[0], sheriff_pos[1])
        #         screen_x, screen_y = c.apply(iso_x, iso_y)
        #         # Try to get sheriff sprite or fallback
        #         sprite = AssetManager().get_sprite("outlaw_idle")
        #         if sprite:
        #             # Anchor by feet: center horizontally, bottom at position
        #             draw_x = screen_x - (sprite.get_width() // 2)
        #             draw_y = screen_y - sprite.get_height()
        #             s.blit(sprite, (draw_x, draw_y))
        #         else:
        #             pygame.draw.circle(s, COLOR_SHERIFF, (int(screen_x), int(screen_y)), 18)
        #             
        #     entities.append({
        #         'y': sheriff_pos[1],
        #         'type': 'sheriff',
        #         'draw': draw_sheriff
        #     })
        #     self.drawn_count += 1
        # else:
        #     self.culled_count += 1
        
        # C-Engine Entities (Bullets etc.)
        if self.engine:
            current = self.engine.get_entity_head()
            while current:
                if current.contents.active:
                    ent = current.contents
                    # Skip drawing the player dot (the Python Player class handles its own rendering)
                    if self.player_entity and ent.id == self.player_entity.contents.id:
                        current = current.contents.next
                        continue
                        
                    # Culling check for C-entities
                    e_iso_x, e_iso_y = cartesian_to_iso(ent.x, ent.y)
                    if self.camera.is_visible(e_iso_x, e_iso_y, 32, 32):
                        def draw_bullet(s, c, e=ent):
                            cbx, cby = c.apply(*cartesian_to_iso(e.x, e.y))
                            # Use sprite mapping if available
                            sprite_name = SPRITE_MAP.get(e.sprite_type)
                            sprite = AssetManager().get_sprite(sprite_name)
                            if sprite:
                                s.blit(sprite, (cbx - sprite.get_width()//2, cby - sprite.get_height()//2))
                            else:
                                pygame.draw.circle(s, (255, 255, 100), (int(cbx), int(cby)), 4)
                            
                        entities.append({
                            'y': ent.y,
                            'type': 'bullet',
                            'draw': draw_bullet
                        })
                        self.drawn_count += 1
                    else:
                        self.culled_count += 1
                current = current.contents.next
                
        # --- EXECUTE Y-SORT ---
        entities.sort(key=lambda e: e['y'])
        
        # 3. Draw Sorted Entities
        for ent in entities:
            ent['draw'](screen, self.camera)
            
        # 4. Draw Particles (Top Visual Layer, usually don't need sorting)
        if self.engine:
            pool, max_p = self.engine.get_particle_pool(), self.engine.get_max_particles()
            for i in range(max_p):
                p = pool[i]
                if p.active:
                    # Particle culling
                    p_iso_x, p_iso_y = cartesian_to_iso(p.x, p.y)
                    if self.camera.is_visible(p_iso_x, p_iso_y, 4, 4):
                        cpx, cpy = self.camera.apply(p_iso_x, p_iso_y)
                        pygame.draw.circle(screen, (150, 150, 100, int(255 * (p.life / p.max_life))), (int(cpx), int(cpy)), 2)
                        self.drawn_count += 1
                    else:
                        self.culled_count += 1
                        
        # --- TELEMETRY OUTPUT ---
        self.telemetry_frame_count += 1
        if self.telemetry_frame_count >= 60:
            print(f"[Culling] Culled: {self.culled_count}, Drawn: {self.drawn_count}")
            self.telemetry_frame_count = 0

        # 5. Apply Ambient Lighting Overlay
        self.darkness.fill(AMBIENT_LIGHT)
        self.campfire.draw(self.darkness, camera=self.camera)
        self.player_light.draw(self.darkness, camera=self.camera)
        screen.blit(self.darkness, (0, 0))
        
        # --- HUD Render (Last Layer) ---
        sheriff_pos = [2.0, 2.0]
        static_npcs = [(sheriff_pos[0], sheriff_pos[1], COLOR_SHERIFF)]
        self.hud.render(screen, self.health, self.weapons.current_weapon, 
                        self.player.pos, self.engine.get_entity_head(), static_npcs,
                        inventory=self.inventory, show_inventory=self.show_inventory,
                        time_str=self.clock.get_formatted_time())

class CutsceneState(GameState):
    def __init__(self, manager, playing_state):
        self.manager = manager
        self.playing = playing_state
        self.sequencer = playing_state.sequencer

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.sequencer.stop()
            self.playing.camera.manual_offset = None
            self.manager.pop()

    def update(self, dt):
        self.sequencer.update(dt)
        if self.sequencer.is_finished():
            # Automatically exit back to play state
            self.playing.camera.manual_offset = None
            self.manager.pop()
            
    def draw(self, screen):
        self.playing.draw(screen)
        # Black bars for cinematic look
        screen_w, screen_h = screen.get_size()
        bar_h = 100
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_w, bar_h))
        pygame.draw.rect(screen, (0, 0, 0), (0, screen_h - bar_h, screen_w, bar_h))

class ConsoleState(GameState):
    def __init__(self, manager, playing_state):
        self.manager = manager
        self.playing = playing_state
        self.console = playing_state.console
        self.console._update_fonts(UI_FONT_SCALE) # Ensure console matches current scale

    def handle_event(self, event):
        input_mgr = InputManager()
        if input_mgr.get_action(event) == 'ACTION_CONSOLE':
            self.manager.pop()
            return
        self.console.handle_input(event)

    def update(self, dt):
        pass # World is paused

    def draw(self, screen):
        self.playing.draw(screen)
        self.console.draw(screen)

class DialogueState(GameState):
    def __init__(self, manager, dm, font_scale=1.0):
        super().__init__(manager)
        self.dm = dm
        self.font = pygame.font.SysFont("Arial", int(32 * font_scale))
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: self.dm.make_choice(0)
            elif event.key == pygame.K_2: self.dm.make_choice(1)
            elif event.key == pygame.K_3: self.dm.make_choice(2)
            elif event.key in [pygame.K_ESCAPE, pygame.K_e]:
                if self.dm.is_end(): self.manager.pop()
    def draw(self, screen):
        scale = self.font.get_height() / 32.0 # Approximation of scale factor
        height = int(300 * scale)
        pos_y = SCREEN_HEIGHT - height - 50
        overlay = pygame.Surface((SCREEN_WIDTH, height), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, pos_y))
        screen.blit(self.font.render(self.dm.get_text(), True, (255, 255, 255)), (50, pos_y + 40 * scale))
        for i, opt in enumerate(self.dm.get_options()): 
            screen.blit(self.font.render(opt, True, (200, 200, 100)), (70, pos_y + (120 * scale) + i * (50 * scale)))

class PausedState(GameState):
    def __init__(self, manager, font_scale=1.0):
        super().__init__(manager)
        self.font = pygame.font.SysFont("Arial", int(72 * font_scale), bold=True)
    def handle_event(self, event):
        input_mgr = InputManager()
        action = input_mgr.get_action(event)
        if action == 'ACTION_PAUSE': self.manager.pop()
    def draw(self, screen):
        loc = LocalizationManager()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        txt = self.font.render(loc.get("UI_PAUSED"), True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

def main():
    pygame.init()
    # Initialize Input Manager
    InputManager()
    # Ensure OpenGL 3.3 Core Profile for ModernGL on macOS
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    # Use OPENGL flag for hardware shaders
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Crimson Trails Engine")
    
    # Off-screen surface for standard Pygame rendering (RGBA for ModernGL compatibility)
    main_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()
    
    clock = pygame.time.Clock()
    # Optimized Asset Loading with Target Scaling
    AssetManager().load_directory("assets", default_scales={
        "desert_ground": (TILE_WIDTH, TILE_HEIGHT),
        "outlaw_idle": 0.2,   # Scale down large character assets
        "outlaw_walk": 0.2,
        "bandit": 0.2,
        "cactus": (48, 64),
        "bullet": (8, 8)
    })
    audio = AudioManager()
    engine = load_engine()
    
    # Initialize Post-Processor
    post_processor = PostProcessor(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Initialize Telemetry
    telemetry = TelemetryTracker()
    
    state_manager = StateManager()
    state_manager.push(PlayingState(state_manager, engine, audio))
    running = True
    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                state_manager.handle_event(event)
            dt = clock.tick(FPS) / 1000.0
            state_manager.update(dt); audio.update()
            
            # Record Telemetry
            if engine:
                # Need current state's quadtree root if available
                # For simplicity, we'll try to get it if we're in PlayingState
                qt_nodes = 0
                state = state_manager.peek()
                if hasattr(state, 'last_qt_node_count'):
                    qt_nodes = state.last_qt_node_count
                
                telemetry.record_frame(
                    dt, 
                    engine.get_entity_count(),
                    engine.get_total_memory_usage() + AssetManager().get_total_memory_usage(),
                    qt_nodes
                )
            
            # Render game to the off-screen surface
            main_surface.fill(COLOR_BG)
            if isinstance(state_manager.peek(), (PausedState, DialogueState, ConsoleState)) and len(state_manager._stack) > 1:
                # Under-draw for overlays (now includes ConsoleState)
                state_manager._stack[-2].draw(main_surface)
            state_manager.draw(main_surface)
            
            # Apply Post-Processing and render to OpenGL screen
            # Apply post-processing and flip
            state = state_manager.peek()
            tint = (1.0, 1.0, 1.0)
            if hasattr(state, 'clock'):
                tint = state.clock.get_ambient_color()
            elif len(state_manager._stack) > 1 and hasattr(state_manager._stack[-2], 'clock'):
                tint = state_manager._stack[-2].clock.get_ambient_color()
                
            post_processor.render(main_surface, rgb_tint=tint)
            pygame.display.flip()
    finally:
        if engine: 
            engine.clear_entities()
            engine.engine_shutdown()
        if telemetry:
            telemetry.export_session_data()
        pygame.quit()

if __name__ == "__main__": main()
