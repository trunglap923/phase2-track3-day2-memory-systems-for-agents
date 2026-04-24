import json
import time
from typing import Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .state import MemoryState
from .prompts import SYSTEM_PROMPT_TEMPLATE, PROFILE_EXTRACTION_PROMPT, EPISODIC_EXTRACTION_PROMPT
from memory import (
    SimpleShortTermMemory, 
    JSONProfileMemory, 
    JSONEpisodicMemory, 
    ChromaSemanticMemory
)

class MultiMemoryAgent:
    def __init__(self, memory: str = "yes", model: str = "gpt-4o-mini"):
        self.use_memory = memory.lower() == "yes"
        
        # Khởi tạo các bộ nhớ
        self.short_term_mem = SimpleShortTermMemory()
        self.long_term_mem = JSONProfileMemory()
        self.episodic_mem = JSONEpisodicMemory()
        self.semantic_mem = ChromaSemanticMemory()

        # Khởi tạo LLM
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.extraction_llm = ChatOpenAI(model=model, temperature=0).bind(
            response_format={"type": "json_object"}
        )

        # Build Graph
        self.app = self._build_graph()

    def retrieve_node(self, state: MemoryState) -> MemoryState:
        """Node truy xuất dữ liệu từ các bộ nhớ."""
        if not self.use_memory:
            return {
                "user_profile": {},
                "episodes": [],
                "semantic_hits": []
            }

        latest_query = ""
        if state["messages"] and state["messages"][-1].type == "human":
            latest_query = state["messages"][-1].content

        profile = self.long_term_mem.get_profile()
        episodes = self.episodic_mem.get_episodes()
        
        semantic_hits = []
        if latest_query:
            hits = self.semantic_mem.search(latest_query)
            semantic_hits = hits if isinstance(hits, list) else [hits]
            
        return {
            "user_profile": profile,
            "episodes": episodes[-5:],
            "semantic_hits": semantic_hits
        }

    def generate_node(self, state: MemoryState) -> MemoryState:
        """Node tạo phản hồi từ LLM."""
        profile_str = json.dumps(state.get("user_profile", {}), ensure_ascii=False, indent=2)
        episodes_str = json.dumps(state.get("episodes", []), ensure_ascii=False, indent=2)
        semantic_str = "\n".join(state.get("semantic_hits", []))
        
        # Nếu tắt memory, prompt sẽ trống các phần bổ trợ
        sys_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            user_profile=profile_str if self.use_memory else "{}",
            episodes=episodes_str if self.use_memory else "[]",
            semantic_hits=semantic_str if self.use_memory else ""
        )
        
        messages = [SystemMessage(content=sys_prompt)] + state["messages"][-10:]
        response = self.llm.invoke(messages)
        
        return {"messages": [response]}

    def update_node(self, state: MemoryState) -> MemoryState:
        """Node trích xuất và cập nhật bộ nhớ sau hội thoại."""
        if not self.use_memory:
            return state

        # Lấy cặp tin nhắn gần nhất (Human và AI)
        last_human = ""
        last_ai = ""
        msgs = state["messages"][-2:]
        if len(msgs) >= 2:
            last_human = msgs[0].content
            last_ai = msgs[1].content
        else:
            return state

        recent_history = f"user: {last_human}\nai: {last_ai}"
        current_profile = json.dumps(self.long_term_mem.get_profile(), ensure_ascii=False)
        
        # 1. Update Profile
        prof_prompt = PROFILE_EXTRACTION_PROMPT.format(
            current_profile=current_profile,
            recent_history=recent_history
        )
        prof_response = self.extraction_llm.invoke([HumanMessage(content=prof_prompt)])
        try:
            new_facts = json.loads(prof_response.content)
            if new_facts:
                for k, v in new_facts.items():
                    self.long_term_mem.update_profile(k, v)
        except: pass

        # 2. Update Episodic với cấu trúc mới
        ep_prompt = EPISODIC_EXTRACTION_PROMPT.format(
            recent_history=recent_history
        )
        ep_response = self.extraction_llm.invoke([HumanMessage(content=ep_prompt)])
        try:
            extraction = json.loads(ep_response.content)
            if extraction and extraction.get("outcome"):
                new_episode = {
                    "timestamp": time.time(),
                    "query": last_human,
                    "response": last_ai,
                    "outcome": extraction.get("outcome")
                }
                self.episodic_mem.add_episode(new_episode)
        except: pass

        return state

    def _build_graph(self):
        workflow = StateGraph(MemoryState)
        
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("update", self.update_node)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "update")
        workflow.add_edge("update", END)
        
        return workflow.compile()

    def run(self, message: str, thread_id: str = "default"):
        """Hàm tiện ích để chạy agent với một tin nhắn đầu vào."""
        # Lưu ý: Ở đây ta có thể dùng thread_id nếu dùng Checkpointer của LangGraph
        inputs = {"messages": [HumanMessage(content=message)]}
        result = self.app.invoke(inputs)
        return result["messages"][-1].content
