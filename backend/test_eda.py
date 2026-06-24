from tools.data_loader import load_data

from tools.eda_tools import (
    run_complete_eda
)

from tools.visualization_tools import *

df = load_data(
    "D:\\Data Analyst Agent\\datasets\\SampleSuperstore.csv"
)

results = run_complete_eda(df)

print(results["overview"])

print(results["duplicate_count"])

print(results["skewness"])

num_cols = results[
    "numerical_columns"
]

cat_cols = results[
    "categorical_columns"
]

plot_histogram(
    df,
    num_cols
)

plot_barchart(
    df,
    cat_cols
)

plot_heatmap(
    results["correlation_matrix"]
)

plot_scatter(
    df,
    num_cols
)

plot_pie_chart(
    df,
    cat_cols
)