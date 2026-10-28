import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langgraph.graph import StateGraph, START, END
from backend.graphs.state import DataAnalystState

from backend.agents.dataset_agent import DatasetAgent
from backend.agents.eda_agent import EDAAgent
from backend.agents.insight_agent import InsightAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.reflection_agent import ReflectionAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.agents.visualization_agent import VisualizationAgent

dataset_agent = DatasetAgent()
eda_agent = EDAAgent()
planner_agent = PlannerAgent()
visualization_agent = VisualizationAgent()
insight_agent = InsightAgent()
reviewer_agent = ReviewerAgent()
reflection_agent = ReflectionAgent()
report_agent = ReportAgent()

# Step callback — set by app.py before each pipeline run for real-time progress
_step_callback = None

def set_step_callback(fn):
    global _step_callback
    _step_callback = fn

def _advance(step_idx: int):
    if _step_callback:
        try:
            _step_callback(step_idx)
        except Exception:
            pass

def dataset_node(state):
    _advance(0)
    return dataset_agent.run(state)

def eda_node(state):
    _advance(2)
    return eda_agent.run(state)

def planner_node(state):
    _advance(1)
    return planner_agent.run(state)

def visualization_node(state):
    _advance(3)
    return visualization_agent.run(state)

def insight_node(state):
    _advance(4)
    return insight_agent.run(state)

def reviewer_node(state):
    _advance(5)
    return reviewer_agent.run(state)

def reflection_node(state):
    _advance(6)
    result = reflection_agent.run(state)
    # Increment retry_count so we know how many loops have happened
    result["retry_count"] = state.get("retry_count", 0) + 1
    return result

def report_node(state):
    _advance(7)
    return report_agent.run(state)

graph = StateGraph(DataAnalystState)

graph.add_node("dataset", dataset_node)
graph.add_node("planner", planner_node)
graph.add_node("eda", eda_node)
graph.add_node("visualization", visualization_node)
graph.add_node("insight", insight_node)
graph.add_node("review", reviewer_node)
graph.add_node("reflection", reflection_node)
graph.add_node("report", report_node)

graph.add_edge(START, "dataset")
graph.add_edge("dataset", "planner")
graph.add_edge("planner", "eda")
graph.add_edge("eda", "visualization")
graph.add_edge("visualization", "insight")
graph.add_edge("insight", "review")

def review_router(state):
    # Cap at 1 retry max — after that, always proceed to report
    if state.get("retry_count", 0) >= 1:
        return "report"
    if state.get("review_passed", False):
        return "report"
    return "reflection"

graph.add_conditional_edges(
    "review",
    review_router,
    {
        "report": "report",
        "reflection": "reflection",
    }
)

graph.add_edge("reflection", "planner")
graph.add_edge("report", END)

complete = graph.compile()