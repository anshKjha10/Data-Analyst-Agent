import sys
import os
import json

# Ensure project root is on sys.path so backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.dataset_agent import DatasetAgent
from backend.agents.planner_agent import PlannerAgent

def run_test():
    print("=== Testing Metadata-Driven PlannerAgent ===")
    
    file_path = "D:\\Data Analyst Agent\\datasets\\SampleSuperstore.csv"
    if not os.path.exists(file_path):
        print(f"Error: Test file not found at {file_path}")
        return

    # 1. Initialize dataset state
    state = {"file_path": file_path}
    print("Extracting dataset info...")
    dataset_state = DatasetAgent().run(state)
    state.update(dataset_state)

    # 2. Instantiate PlannerAgent
    planner = PlannerAgent()

    # 3. Run planner
    print("\nRunning metadata-driven planner...")
    res = planner.run(state)
    
    print("\n--- Analysis Plan ---")
    print(json.dumps(res["analysis_plan"], indent=2))

if __name__ == "__main__":
    run_test()
