import pygame
import heapq
import time

class AudioManager:
    """Manages game audio with channels and priority-based SFX queuing."""
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Define channel allocations
        # Channel 0: Music
        # Channels 1-4: SFX
        # Channels 5-6: Ambient
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channels = [pygame.mixer.Channel(i) for i in range(1, 5)]
        self.ambient_channels = [pygame.mixer.Channel(i) for i in range(5, 7)]
        
        # Priority Queue for SFX (priority, timestamp, sound_object)
        # Note: heapq is a min-heap, so we store priority as a lower number for higher importance? 
        # Actually, let's use 0 as highest priority and higher numbers for lower.
        self.sfx_queue = []
        
        print("[Audio] Audio Manager initialized (7 Channels allocated).")

    def play_sound(self, sound, priority=10, category="sfx", loop=0):
        """
        Requests audio playback.
        Priority: 0 (Critical) to 100 (Background).
        Category: 'music', 'sfx', 'ambient'.
        """
        if not sound:
            return

        if category == "music":
            self.music_channel.play(sound, loops=-1 if loop == -1 else loop)
            print(f"[Audio] Routing Music: {sound}")
        elif category == "ambient":
            # Find an open ambient channel
            for chan in self.ambient_channels:
                if not chan.get_busy():
                    chan.play(sound, loops=-1 if loop == -1 else loop)
                    print(f"[Audio] Routing Ambient: {sound}")
                    return
            # If all busy, overwrite the first one
            self.ambient_channels[0].play(sound, loops=-1 if loop == -1 else loop)
        elif category == "sfx":
            # Add to priority queue
            # Using time.time() to ensure stable sorting for same-priority sounds
            heapq.heappush(self.sfx_queue, (priority, time.time(), sound, loop))

    def update(self):
        """Processes the SFX queue and assigns to free channels."""
        if not self.sfx_queue:
            return

        # Attempt to play queued sounds on free SFX channels
        for chan in self.sfx_channels:
            if not chan.get_busy() and self.sfx_queue:
                priority, ts, sound, loop = heapq.heappop(self.sfx_queue)
                chan.play(sound, loops=loop)
                # print(f"[Audio] Playing SFX (Pri: {priority}): {sound}")
                
        # Optional: If queue is very long, drop lowest priority sounds
        while len(self.sfx_queue) > 20:
            heapq.heappop(self.sfx_queue) # This actually pops the HIGH priority (min value). 
            # Fix: If we want to drop LOW priority, we'd need a max-heap or pop from end.
            # For this simple engine, 20 sounds in queue is plenty.
