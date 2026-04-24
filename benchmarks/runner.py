import json
import os
import shutil
import sys
from dotenv import load_dotenv

load_dotenv()

# Clean previous memory backends for a fresh run BEFORE importing any ChromaDB stuff
dirs_to_clean = ["data"]
for d in dirs_to_clean:
    if os.path.exists(d):
        try:
            shutil.rmtree(d)
        except Exception as e:
            print(f"Could not clean {d}: {e}")

# Ensure the root directory is in sys.path so we can import 'agent' and 'memory'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from agent import MultiMemoryAgent



def main():
    with open("benchmarks/scenarios.json", "r", encoding="utf-8") as f:
        scenarios = json.load(f)
        
    # Khởi tạo 2 Agent: một cái có memory, một cái không
    agent_with_mem = MultiMemoryAgent(memory="yes")
    agent_no_mem = MultiMemoryAgent(memory="no")
    
    results = []
    
    for sc in scenarios:
        print(f"Running Scenario {sc['id']}: {sc['name']}...")
        
        # Với No-memory, ta CHỈ truyền tin nhắn hiện tại (Stateless per turn)
        no_mem_ans = ""
        for turn in sc["turns"]:
            # Không dùng msgs_no_mem làm buffer, chỉ truyền tin nhắn đơn lẻ
            res = agent_no_mem.app.invoke({"messages": [HumanMessage(content=turn["content"])]})
            no_mem_ans = res["messages"][-1].content

        # Với With-memory, Agent sẽ duy trì bộ nhớ xuyên suốt các kịch bản
        with_mem_ans = ""
        msgs_with_mem = []
        for turn in sc["turns"]:
            msgs_with_mem.append(HumanMessage(content=turn["content"]))
            res = agent_with_mem.app.invoke({"messages": msgs_with_mem})
            with_mem_ans = res["messages"][-1].content
            msgs_with_mem.append(res["messages"][-1])
        
        passed = sc["expected_keyword"].lower() in with_mem_ans.lower()
        
        # Format outputs to be one line for the markdown table
        no_mem_ans_formatted = no_mem_ans.replace("\n", " ").replace("|", " ")
        with_mem_ans_formatted = with_mem_ans.replace("\n", " ").replace("|", " ")
        
        results.append({
            "id": sc["id"],
            "name": sc["name"],
            "no_memory": no_mem_ans_formatted,
            "with_memory": with_mem_ans_formatted,
            "passed": "Pass" if passed else "Fail"
        })
        
    # Write BENCHMARK.md
    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Results\n\n")
        f.write("This benchmark compares a standard LLM conversation (No-memory) with our LangGraph Multi-Memory Agent (With-memory).\n\n")
        f.write("| # | Scenario | No-memory result | With-memory result | Pass? |\n")
        f.write("|---|----------|------------------|---------------------|-------|\n")
        for r in results:
            f.write(f"| {r['id']} | {r['name']} | {r['no_memory']} | {r['with_memory']} | {r['passed']} |\n")
            
    print("Benchmark complete. Results saved to BENCHMARK.md")

if __name__ == "__main__":
    main()
