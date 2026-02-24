# --- Security Test Mod ---
# This mod should fail to load because 'import' is blocked.

try:
    import os
    api.log("FAILURE: 'os' module was successfully imported!")
except Exception as e:
    api.log(f"SUCCESS: Mod blocked from importing 'os'. Error: {e}")
