import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from .state import MemoryState
from .prompts import SYSTEM_PROMPT_TEMPLATE, PROFILE_EXTRACTION_PROMPT, EPISODIC_EXTRACTION_PROMPT
from memory import SimpleShortTermMemory, JSONProfileMemory, JSONEpisodicMemory, ChromaSemanticMemory
from dotenv import load_dotenv

load_dotenv()

# Initialize memory backends
short_term_mem = SimpleShortTermMemory()
long_term_mem = JSONProfileMemory()
episodic_mem = JSONEpisodicMemory()
semantic_mem = ChromaSemanticMemory()

# Seed some FAQ knowledge
semantic_mem.add_documents([
    "Để kết nối các container, tên service của Docker có thể được dùng làm hostname khi các container nằm trong cùng một mạng docker network.",
    "Cổng (port) mặc định để kết nối với cơ sở dữ liệu PostgreSQL là 5432.",
    "LangGraph là một thư viện chuyên dụng để xây dựng các ứng dụng stateful, multi-actor sử dụng LLM."
])

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extraction_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind(response_format={"type": "json_object"})

def retrieve_memory(state: MemoryState) -> MemoryState:
    # Get latest user message to search semantic memory
    latest_query = ""
    if state["messages"] and state["messages"][-1].type == "human":
        latest_query = state["messages"][-1].content

    # Retrieve from backends
    profile = long_term_mem.get_profile()
    episodes = episodic_mem.get_episodes()
    
    semantic_hits = []
    if latest_query:
        # Simple keyword fallback or vector search
        hits = semantic_mem.search(latest_query)
        if isinstance(hits, list):
            semantic_hits = hits
        else:
            semantic_hits = [hits]
            
    return {
        "user_profile": profile,
        "episodes": episodes[-5:], # Keep context size manageable
        "semantic_hits": semantic_hits
    }

def call_llm(state: MemoryState) -> MemoryState:
    # Construct system prompt
    profile_str = json.dumps(state.get("user_profile", {}), ensure_ascii=False, indent=2)
    episodes_str = json.dumps(state.get("episodes", []), ensure_ascii=False, indent=2)
    semantic_str = "\n".join(state.get("semantic_hits", []))
    
    sys_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        user_profile=profile_str,
        episodes=episodes_str,
        semantic_hits=semantic_str
    )
    
    # We use LangGraph's message state. To keep prompt size bounded, 
    # we could just use short_term_mem or trim state["messages"].
    messages = [SystemMessage(content=sys_prompt)] + state["messages"][-10:]
    
    # Call LLM
    response = llm.invoke(messages)
    
    # Save to short term memory interface (for tracking if needed, though LangGraph state handles it too)
    if state["messages"] and state["messages"][-1].type == "human":
        short_term_mem.add_message("human", state["messages"][-1].content)
    short_term_mem.add_message("ai", response.content)
    
    return {"messages": [response]}

def update_memory(state: MemoryState) -> MemoryState:
    # Need last human and ai message
    recent_history = ""
    msgs = state["messages"][-2:]
    for m in msgs:
        recent_history += f"{m.type}: {m.content}\n"
        
    current_profile = json.dumps(long_term_mem.get_profile(), ensure_ascii=False)
    
    # Extract profile updates
    prof_prompt = PROFILE_EXTRACTION_PROMPT.format(
        current_profile=current_profile,
        recent_history=recent_history
    )
    prof_response = extraction_llm.invoke([HumanMessage(content=prof_prompt)])
    try:
        new_facts = json.loads(prof_response.content)
        if new_facts and isinstance(new_facts, dict):
            for k, v in new_facts.items():
                long_term_mem.update_profile(k, v)
    except json.JSONDecodeError:
        pass

    # Extract episodic updates
    ep_prompt = EPISODIC_EXTRACTION_PROMPT.format(
        recent_history=recent_history
    )
    ep_response = extraction_llm.invoke([HumanMessage(content=ep_prompt)])
    try:
        new_episode = json.loads(ep_response.content)
        if new_episode and new_episode.get("event_type") and new_episode.get("summary"):
            episodic_mem.add_episode(new_episode)
    except json.JSONDecodeError:
        pass

    return state
