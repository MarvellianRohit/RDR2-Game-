# --- Feature Test Mod ---

api.log("Feature test mod loaded.")
api.display_hud_message("Mod System Initialized: Secure Mode Active", duration=5.0)

@register_on_player_shoot
def announce_shot(x, y):
    api.display_hud_message(f"Shot detected at {x:.1f}, {y:.1f}", duration=1.0)
