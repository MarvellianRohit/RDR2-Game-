import json
import os

class CutsceneManager:
    """Manages playback of scripted cinematic sequences."""
    def __init__(self, camera, entities=None):
        self.camera = camera
        self.entities = entities if entities else {} # Map actor_id -> object
        self.timeline = []
        self.elapsed_time = 0.0
        self.active_keyframes = []
        self.is_playing = False
        print("[Sequencer] Cutscene Manager initialized.")

    def load_timeline(self, file_path):
        """Loads a cutscene timeline from a JSON file."""
        if not os.path.exists(file_path):
            print(f"[Sequencer] Error: Timeline file not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                self.timeline = json.load(f)
                # Sort by timestamp
                self.timeline.sort(key=lambda x: x.get('timestamp', 0))
                print(f"[Sequencer] Loaded timeline '{file_path}' with {len(self.timeline)} keyframes.")
                return True
        except Exception as e:
            print(f"[Sequencer] Failed to load timeline: {e}")
            return False

    def start(self):
        self.elapsed_time = 0.0
        self.active_keyframes = list(self.timeline) # Copy
        self.is_playing = True
        print("[Sequencer] Cutscene started.")

    def update(self, dt):
        if not self.is_playing:
            return
            
        self.elapsed_time += dt
        
        # Check for keyframes to trigger
        while self.active_keyframes and self.active_keyframes[0]['timestamp'] <= self.elapsed_time:
            kf = self.active_keyframes.pop(0)
            self._execute_keyframe(kf)
            
        if not self.active_keyframes:
            # We might want a 'duration' for the last keyframe if it's a pan
            pass

    def _execute_keyframe(self, kf):
        action = kf.get('action')
        data = kf.get('data', {})
        actor_id = kf.get('actor_id')
        
        print(f"[Sequencer] @{self.elapsed_time:.2f}s: {action} (Actor: {actor_id})")
        
        if action == 'CAMERA_PAN':
            tx, ty = data.get('target_pos', (0, 0))
            duration = data.get('duration', 1.0)
            # Future: Smooth interpolation logic
            # For now, immediate snap or simple move
            self.camera.manual_offset = (tx, ty)
            
        elif action == 'ACTOR_WALK':
            actor = self.entities.get(actor_id)
            if actor and hasattr(actor, 'calculate_path'):
                tx, ty = data.get('target_tile', (0, 0))
                actor.calculate_path(tx, ty)
                
        elif action == 'ACTOR_SAY':
            # This could hook into the DialogueManager or a simplified HUD popup
            print(f"[Sequencer] {actor_id} says: {data.get('text')}")

    def is_finished(self):
        return not self.active_keyframes and self.is_playing

    def stop(self):
        self.is_playing = False
        print("[Sequencer] Cutscene stopped.")
