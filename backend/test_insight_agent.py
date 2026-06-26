import sys
import os
import json

# Ensure project root is on sys.path so backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.insight_agent import InsightAgent

def run_test():
    print("=== Testing InsightAgent ===")
    
    # Mock input state
    state = {
        "dataset_info": {
            "rows": 9994,
            "columns": 21,
            "column_names": ["Row ID", "Order ID", "Sales", "Quantity", "Discount", "Profit"],
            "numeric_columns": ["Sales", "Quantity", "Discount", "Profit"],
            "categorical_columns": ["Category", "Sub-Category"],
            "datetime_columns": ["Order Date", "Ship Date"],
            "missing_values": {}
        },
        "eda_results": {
            "summary_statistics": [
                {"index": "Sales", "mean": 229.858, "std": 623.245, "min": 0.444, "max": 22638.48},
                {"index": "Profit", "mean": 28.656, "std": 234.26, "min": -6599.978, "max": 8399.976}
            ],
            "outlier_detection": {
                "Sales": 1167,
                "Profit": 1881
            }
        },
        "visualizations": [
            {
                "title": "Histogram of Sales",
                "chart_type": "Histogram",
                "x_column": "Sales",
                "y_column": None,
                "image_url": "reports/histogram_Sales.png"
            },
            {
                "title": "Sales vs Profit Scatter",
                "chart_type": "Scatter Plot",
                "x_column": "Sales",
                "y_column": "Profit",
                "image_url": "reports/scatter_plot_Sales_vs_Profit.png"
            }
        ]
    }

    # Instantiate and run InsightAgent
    agent = InsightAgent()
    print("Running Insight agent...")
    output = agent.run(state)

    print("\n--- Insight Agent Output Keys ---")
    print(list(output.keys()))

    print("\n--- Insights Generated ---")
    print(json.dumps(output["insights"], indent=2))

if __name__ == "__main__":
    run_test()
