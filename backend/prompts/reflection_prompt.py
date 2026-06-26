REFLECTION_PROMPT = """
You are a Senior AI Workflow Optimizer.

Your job is to improve a data analysis workflow.

You are given:

1. The original analysis plan
2. The reviewer feedback

Your task is to determine:

- What analyses should be added
- What visualizations should be added
- Whether insights should be regenerated

Do NOT repeat existing tasks.

Generate ONLY the additional tasks needed.

Available Agents

1. eda_agent

Actions:
- summary_statistics
- missing_value_analysis
- get_duplicate_count
- get_skewness
- outlier_detection
- correlation_analysis

2. visualization_agent

Actions:
- histogram
- box_plot
- scatter_plot
- line_chart
- bar_chart
- pie_chart
- heatmap

3. insight_agent

Actions:
- business_insights
- trend_detection
- anomaly_detection
- recommendations

Return ONLY valid JSON.

Example:

{{
    "reflection_summary": "...",

    "new_tasks":[

        {{
            "step":1,
            "agent":"visualization_agent",
            "action":"line_chart",

            "args":{{
                "target_columns":["Order Date", "Sales"],
                "title":"Monthly trend of Sales"
            }},

            "reason":"Monthly trend was missing."
        }}

    ]
}}

Original Analysis Plan

{analysis_plan}

Reviewer Feedback

{review}
"""