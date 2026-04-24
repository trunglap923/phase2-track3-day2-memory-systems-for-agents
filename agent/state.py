from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages

class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]
    user_profile: dict
    episodes: List[Dict[str, Any]]
    semantic_hits: List[str]
    memory_budget: int
