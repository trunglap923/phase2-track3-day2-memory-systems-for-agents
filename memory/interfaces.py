from abc import ABC, abstractmethod
from typing import Any, List, Dict

class ShortTermMemory(ABC):
    @abstractmethod
    def get_messages(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_message(self, role: str, content: str) -> None:
        pass

class LongTermMemory(ABC):
    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_profile(self, key: str, value: Any) -> None:
        pass

class EpisodicMemory(ABC):
    @abstractmethod
    def get_episodes(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_episode(self, episode: Dict[str, Any]) -> None:
        pass

class SemanticMemory(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[str]:
        pass

    @abstractmethod
    def add_documents(self, documents: List[str]) -> None:
        pass
