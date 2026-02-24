import pygame

class Animation:
    """Represents a single animation sequence from a sprite sheet."""
    def __init__(self, sprite_sheet, frame_width, frame_height, num_frames, frame_duration=0.1, loop=True):
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration # Duration of one frame in seconds
        self.loop = loop

    def get_frame_rect(self, elapsed_time):
        """Calculates and returns the Rect for the current frame based on time."""
        total_duration = self.num_frames * self.frame_duration
        
        if self.loop:
            current_time = elapsed_time % total_duration
        else:
            current_time = min(elapsed_time, total_duration - 0.001)
            
        frame_index = int(current_time / self.frame_duration)
        frame_index = min(frame_index, self.num_frames - 1)
        
        # Assume frames are laid out horizontally in the sprite sheet
        return pygame.Rect(frame_index * self.frame_width, 0, self.frame_width, self.frame_height)

class Animator:
    """Component for managing multiple animations and current state."""
    def __init__(self):
        self.animations = {} # Dict of {name: Animation}
        self.current_state = None
        self.timer = 0.0
        self.is_playing = False

    def add_animation(self, name, animation):
        """Registers an animation sequence."""
        self.animations[name] = animation
        if self.current_state is None:
            self.current_state = name

    def play(self, name, reset=False):
        """Switches to the specified animation state."""
        if name not in self.animations:
            print(f"[Animator] Warning: Animation '{name}' not found.")
            return

        if self.current_state != name or reset:
            self.current_state = name
            self.timer = 0.0
            self.is_playing = True

    def update(self, dt):
        """Updates the animation timer."""
        if self.is_playing:
            self.timer += dt

    def get_current_frame_data(self):
        """Returns the source surface and the current frame's source rect."""
        if self.current_state and self.current_state in self.animations:
            anim = self.animations[self.current_state]
            rect = anim.get_frame_rect(self.timer)
            return anim.sprite_sheet, rect
        return None, None
