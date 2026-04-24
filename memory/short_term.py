from typing import List, Dict, Any
from .interfaces import ShortTermMemory

class SimpleShortTermMemory(ShortTermMemory):
    def __init__(self, max_messages: int = 20):
        self.messages = []
        self.max_messages = max_messages

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
