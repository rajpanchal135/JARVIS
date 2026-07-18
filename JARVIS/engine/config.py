import os
import json

def _load_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"theme": "#00e5ff", "voice": "en-in", "wakeWord": "jarvis"}

ASSISTANT_NAME = _load_config().get("wakeWord", "jarvis").lower()