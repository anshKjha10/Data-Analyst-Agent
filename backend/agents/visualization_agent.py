import os
import pandas as pd
from backend.tools.visualization_tools import plot_chart

class VisualizationAgent:
    def __init__(self):

        self.action_to_chart = {
            "histogram": "Histogram",
            "bar_chart": "Bar Chart",
            "line_chart": "Line Chart",
            "scatter_plot": "Scatter Plot",
            "heatmap": "Heatmap",
            "box_plot": "Box Plot",
            "violin_plot": "Violin Plot",
            "count_plot": "Count Plot",
            "pie_chart": "Pie Chart"
        }

    def run(self, state):
        file_path = state["file_path"]
        df = pd.read_csv(file_path)
        plan = state["analysis_plan"]
        
        visualizations = state.get("visualizations", [])
        if visualizations is None:
            visualizations = []

        for task in plan.get("tasks", []):
            if task.get("agent") != "visualization_agent":
                continue

            action_name = task.get("action")
            chart_type = self.action_to_chart.get(action_name)
            if chart_type is None:
                continue

            try:
                task_args = task.get("args", {})
                target_columns = task_args.get("target_columns", [])

                x_col = target_columns[0] if len(target_columns) > 0 else None
                y_col = target_columns[1] if len(target_columns) > 1 else None
                result = plot_chart(df, chart_type, x_col=x_col, y_col=y_col)

                if "saved_path" in result:
                    visualizations.append({
                        "title": task_args.get("title", f"{chart_type}" + (f": {x_col}" if x_col else "") + (f" vs {y_col}" if y_col else "")),
                        "chart_type": chart_type,
                        "x_column": x_col,
                        "y_column": y_col,
                        "image_url": result["saved_path"]
                    })
                elif "error" in result:
                    print(f"Warning: Plot failed for task {action_name}: {result['error']}")

            except Exception as e:
                print(f"Exception during visualization task {action_name}: {str(e)}")

        return {
            "visualizations": visualizations
        }
