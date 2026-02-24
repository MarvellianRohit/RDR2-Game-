import math

class WorldManager:
    """Manages world chunking and dynamic asset streaming."""
    def __init__(self, chunk_size=64):
        self.chunk_size = chunk_size
        self.current_chunk = (0, 0)
        self.active_chunks = set()
        self.tiles = {} # {(x, y): type_id}
        self.load_map("assets/maps/world.json")
        print(f"[World] World Manager initialized. Chunk Size: {chunk_size}x{chunk_size}")

    def set_tile(self, x, y, type_id):
        """Sets a tile type at a specific coordinate."""
        self.tiles[(int(x), int(y))] = type_id

    def get_tile(self, x, y):
        """Returns the tile type at a coordinate, or None if default."""
        return self.tiles.get((int(x), int(y)))

    def save_map(self, path):
        """Serializes tile data to JSON."""
        import json, os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Convert tuple keys to strings for JSON
        serializable_tiles = {f"{k[0]},{k[1]}": v for k, v in self.tiles.items()}
        with open(path, 'w') as f:
            json.dump(serializable_tiles, f, indent=4)
        print(f"[World] Map saved to {path}")

    def load_map(self, path):
        """Loads tile data from JSON."""
        import json, os
        if not os.path.exists(path): return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Convert string keys back to tuples
                self.tiles = {}
                for k, v in data.items():
                    x, y = map(int, k.split(','))
                    self.tiles[(x, y)] = v
            print(f"[World] Map loaded from {path} ({len(self.tiles)} tiles)")
        except Exception as e:
            print(f"[World] Error loading map: {e}")

    def update(self, player_pos):
        """
        Calculates current chunk and updates active set.
        Returns (True, loaded, unloaded) if chunks changed.
        """
        px, py = player_pos
        cx = int(px // self.chunk_size)
        cy = int(py // self.chunk_size)
        
        if (cx, cy) == self.current_chunk and self.active_chunks:
            return False, [], []
            
        old_chunks = self.active_chunks
        self.current_chunk = (cx, cy)
        
        # Calculate new 3x3 grid around player
        new_chunks = set()
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                new_chunks.add((cx + dx, cy + dy))
        
        self.active_chunks = new_chunks
        
        loaded = new_chunks - old_chunks
        unloaded = old_chunks - new_chunks
        
        if loaded:
            for c in loaded: print(f"[World] Loading Chunk: {c}")
        if unloaded:
            for c in unloaded: print(f"[World] Unloading Chunk: {c}")
            
        return True, list(loaded), list(unloaded)

    def get_active_boundary(self):
        """Returns (min_x, min_y, width, height) of the active 3x3 chunk area."""
        cx, cy = self.current_chunk
        min_x = (cx - 1) * self.chunk_size
        min_y = (cy - 1) * self.chunk_size
        size = self.chunk_size * 3
        return (float(min_x), float(min_y), float(size), float(size))

    def is_in_active_range(self, x, y):
        """Checks if a coordinate is within the loaded 3x3 area."""
        cx, cy = self.current_chunk
        min_x, min_y = (cx - 1) * self.chunk_size, (cy - 1) * self.chunk_size
        max_x, max_y = (cx + 2) * self.chunk_size, (cy + 2) * self.chunk_size
        return min_x <= x < max_x and min_y <= y < max_y
