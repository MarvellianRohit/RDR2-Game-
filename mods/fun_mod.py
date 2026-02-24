# --- Crimson Trails Sample Mod ---
# Use the @register_on_player_shoot decorator to hook into the shoot event.
# The function receives (x, y) coordinates of the player.

@register_on_player_shoot
def spawn_sparks(x, y):
    api.log(f"Shooting sparks at {x:.2f}, {y:.2f}!")
    # Spawn a few colorful particles
    api.spawn_particle(x, y, color=0xFFAA00FF) # Orange spark
    api.spawn_particle(x + 0.1, y + 0.1, color=0xFFFF00FF) # Yellow spark
    api.play_sound("gunshot") # Redundant but good for testing
