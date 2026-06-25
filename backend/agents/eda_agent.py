import pandas as pd
from backend.tools.eda_tools import (
    get_dataset_overview,
    get_missing_values,
    get_duplicate_count,
    get_column_types,
    get_summary_statistics,
    get_skewness,
    detect_outliers,
    get_correlation_matrix
)

class EDAAgent:
    def __init__(self):
        self.action_map = {
            "summary_statistics" : get_summary_statistics,
            "correlation_analysis" : get_correlation_matrix,
            "missing_value_analysis" : get_missing_values,
            "outlier_detection" : detect_outliers,
            "get_column_types" : get_column_types,
            "get_skewness" : get_skewness,
            "get_dataset_overview" : get_dataset_overview,
            "get_duplicate_count" : get_duplicate_count,
        }

    def run(self, state):
        file_path = state["file_path"]
        df = pd.read_csv(file_path)
        plan = state["analysis_plan"]

        numerical_cols, categorical_cols = get_column_types(df)

        results = {}

        for task in plan.get("tasks", []):
            if task.get("agent") != "eda_agent":
                continue

            action_name = task.get("action")
            tools = self.action_map.get(action_name)
            if tools is None:
                continue

            try:
                task_args = task.get("args", {})
                target_cols = task_args.get("target_columns", [])
                
                if target_cols:
                    target_cols = [col for col in target_cols if col in df.columns]

                if action_name in ["correlation_analysis", "outlier_detection", "get_skewness"]:
                    cols_to_use = target_cols if target_cols else numerical_cols
                    result = tools(df, cols_to_use)
                else:
                    result = tools(df)

                if isinstance(result, pd.DataFrame):
                    result = result.reset_index().to_dict(orient="records")
                elif isinstance(result, pd.Series):
                    result = result.to_dict()

                results[action_name] = result

            except Exception as e:
                results[action_name] = {"error" : str(e)}

        return {
            "eda_results" : results
        }
            


    