import pandas as pd
import numpy as np
from scipy.stats import skew

def get_dataset_overview(df):
    return {
        "shape" : df.shape,
        "columns" : df.columns.tolist(),
        "dtypes" : df.dtypes.astype(str).to_dict(),
        "memory_mb" : round(
            df.memory_usage(deep=True).sum() / (1024 ** 2), 2
        )
    }

def get_missing_values(df):
    missing = pd.DataFrame({
        "Missing Count" : df.isnull().sum(),
        "Missing Percentage" : round(df.isnull().mean() * 100, 2)
    })

    return missing[missing["Missing Count"] > 0]

def get_duplicate_count(df):
    return int(df.duplicated().sum())

def get_column_types(df):
    numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    return numerical_cols, categorical_cols

def get_summary_statistics(df):
    return df.describe().T

def get_skewness(df, numerical_cols):
    results = {}
    for col in numerical_cols:
        results[col] = round(skew(df[col].dropna()), 2)
    
    return results

def detect_outliers(df, numerical_cols):
    results = {}
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]

        results[col] = len(outliers)

    return results

def get_correlation_matrix(df, numerical_cols):
    return df[numerical_cols].corr()

def run_complete_eda(df):
    numerical_cols, categorical_cols = (get_column_types(df))

    return {
        "overview" : get_dataset_overview(df),
        "missing_values" : get_missing_values(df),
        "duplicate_count" : get_duplicate_count(df),
        "numerical_columns" : numerical_cols,
        "categorical_columns" : categorical_cols,
        "summary_statistics" : get_summary_statistics(df),
        "skewness" : get_skewness(df, numerical_cols),
        "outliers" : detect_outliers(df, numerical_cols),
        "correlation_matrix" : get_correlation_matrix(df, numerical_cols)
    }