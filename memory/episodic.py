import json
import os
from typing import List, Dict, Any
from .interfaces import EpisodicMemory

class JSONEpisodicMemory(EpisodicMemory):
    def __init__(self, file_path: str = "data/episodes.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_episodes(self) -> List[Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def add_episode(self, episode: Dict[str, Any]) -> None:
        episodes = self.get_episodes()
        episodes.append(episode)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(episodes, f, ensure_ascii=False, indent=2)
