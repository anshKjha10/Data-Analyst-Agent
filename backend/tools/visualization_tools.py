import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_histogram(df, numerical_cols):
    for col in numerical_cols:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col], kde=True)
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.show()

def plot_barchart(df, categorical_cols):
    for col in categorical_cols:
        plt.figure(figsize=(8, 5))
        df[col].value_counts().head(10).plot(kind='bar')
        plt.title(f'Bar Chart of {col}')
        plt.xlabel(col)
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.show()

def plot_heatmap(corr_matrix):
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.show()

def plot_scatter(df, numerical_cols):
    if len(numerical_cols) < 2:
        return
    
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x=numerical_cols[0], y=numerical_cols[1])

    plt.title(f"{numerical_cols[0]} vs {numerical_cols[1]}")
    plt.show()

def plot_pie_chart(df, categorical_cols):

    if not categorical_cols:
        return

    col = categorical_cols[0]

    plt.figure(figsize=(7,7))

    df[col] \
      .value_counts() \
      .head(5) \
      .plot(
          kind="pie",
          autopct="%1.1f%%"
      )

    plt.ylabel("")

    plt.title(
        f"Pie Chart - {col}"
    )

    plt.show()