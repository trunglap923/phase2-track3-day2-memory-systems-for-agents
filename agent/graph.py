from langgraph.graph import StateGraph, END
from .state import MemoryState
from .nodes import retrieve_memory, call_llm, update_memory

def create_agent_graph():
    workflow = StateGraph(MemoryState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_memory)
    workflow.add_node("generate", call_llm)
    workflow.add_node("update", update_memory)
    
    # Define edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "update")
    workflow.add_edge("update", END)
    
    # Compile graph
    app = workflow.compile()
    return app
