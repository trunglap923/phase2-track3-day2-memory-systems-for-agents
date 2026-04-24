import json
import os
from typing import Dict, Any
from .interfaces import LongTermMemory

class JSONProfileMemory(LongTermMemory):
    def __init__(self, file_path: str = "data/profile.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def get_profile(self) -> Dict[str, Any]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_profile(self, key: str, value: Any) -> None:
        # Conflict resolution: new value overwrites old value implicitly by using dict updates
        profile = self.get_profile()
        profile[key] = value
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
