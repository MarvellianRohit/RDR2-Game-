import math

class WorldClock:
    """Manages in-game time and ambient lighting transitions."""
    def __init__(self, start_time=12.0, time_scale=0.1):
        self.time_of_day = start_time # 0.0 to 24.0
        self.time_scale = time_scale # How many game hours per real second (approx)
        
        # Key color targets: (R, G, B) normalized 0.0-1.0
        self.points = {
            0.0:  (0.05, 0.05, 0.2),  # Midnight (Deep Blue)
            6.0:  (1.0, 0.6, 0.4),   # Sunrise (Warm Orange)
            12.0: (1.0, 1.0, 1.0),   # Noon (Pure White)
            18.0: (1.0, 0.4, 0.3),   # Sunset (Reddish Orange)
            24.0: (0.05, 0.05, 0.2)  # Midnight (Deep Blue)
        }

    def update(self, dt):
        """Passes time based on delta time."""
        self.time_of_day += dt * self.time_scale
        if self.time_of_day >= 24.0:
            self.time_of_day -= 24.0

    def get_ambient_color(self):
        """Linearly interpolates between known time-color points."""
        sorted_keys = sorted(self.points.keys())
        
        # Find the two points we are between
        p1_key = sorted_keys[0]
        p2_key = sorted_keys[-1]
        
        for i in range(len(sorted_keys) - 1):
            if sorted_keys[i] <= self.time_of_day < sorted_keys[i+1]:
                p1_key = sorted_keys[i]
                p2_key = sorted_keys[i+1]
                break
        
        # Calculated factor
        t = (self.time_of_day - p1_key) / (p2_key - p1_key)
        
        c1 = self.points[p1_key]
        c2 = self.points[p2_key]
        
        # Lerp
        r = c1[0] + (c2[0] - c1[0]) * t
        g = c1[1] + (c2[1] - c1[1]) * t
        b = c1[2] + (c2[2] - c1[2]) * t
        
        return (r, g, b)

    def get_formatted_time(self):
        """Returns time as HH:MM string."""
        hours = int(self.time_of_day)
        minutes = int((self.time_of_day - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
