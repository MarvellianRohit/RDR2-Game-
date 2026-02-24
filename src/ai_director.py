import math
import random

class AIDirector:
    """Central tactical manager for enemy behavior."""
    def __init__(self):
        self.global_tactic = "PATROL"
        self.last_tactic = "PATROL"
        print("[AI Director] System Online. Initial Tactic: PATROL")

    def assess_state(self, player_pos, player_health, npc_active):
        """
        Evaluates game conditions and updates global enemy tactics.
        Called periodically (e.g., once per second).
        """
        if not npc_active:
            self.global_tactic = "PATROL"
            return self._check_change()

        # Simple logic based on player health and distance
        # For our current 1-NPC demo, we simulate the "enemy group" behavior
        if player_health < 30:
            self.global_tactic = "RUSH" # Press the advantage
        elif player_health < 60:
            self.global_tactic = "FLANK" # Play tactically
        else:
            self.global_tactic = "PATROL" # Standard caution

        # Distance factor: if player is too close and NPC health (placeholder) is low, RETREAT
        # Note: NPC doesn't have health yet, so we'll just use the tactic logic requested
        
        return self._check_change()

    def _check_change(self):
        if self.global_tactic != self.last_tactic:
            print(f"[AI Director] TACTIC SHIFT: {self.last_tactic} -> {self.global_tactic}")
            self.last_tactic = self.global_tactic
            return True
        return False

    def get_enemy_target(self, enemy_pos, player_pos):
        """Calculates a target coordinate based on current tactic."""
        if self.global_tactic == "RUSH":
            return player_pos # Go directly to player
        elif self.global_tactic == "FLANK":
            # Target a point slightly offset from the player
            angle = math.atan2(enemy_pos[1] - player_pos[1], enemy_pos[0] - player_pos[0])
            offset_x = math.cos(angle + math.pi/2) * 2.0
            offset_y = math.sin(angle + math.pi/2) * 2.0
            return (player_pos[0] + offset_x, player_pos[1] + offset_y)
        elif self.global_tactic == "RETREAT":
            # Move away from player
            dx = enemy_pos[0] - player_pos[0]
            dy = enemy_pos[1] - player_pos[1]
            return (enemy_pos[0] + dx, enemy_pos[1] + dy)
        else:
            # PATROL: move to random nearby point
            return (enemy_pos[0] + random.uniform(-2, 2), enemy_pos[1] + random.uniform(-2, 2))
