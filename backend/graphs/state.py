from typing import TypedDict, Dict, List, Optional

class DataAnalystState(TypedDict):
    file_path: str
    user_query: str
    dataset_info: Dict
    analysis_plan: Dict
    eda_results: Dict
    visualizations: List[Dict]
    insights: List[str]
    report: str 
    review_score: Optional[float]
    feedback: Optional[str]
    review: Optional[Dict]
    review_passed: Optional[bool]