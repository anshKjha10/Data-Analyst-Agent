import pandas as pd
import numpy as np
from scipy.stats import skew

def get_dataset_overview(df):
    try:
        return {
            "shape" : df.shape,
            "columns" : df.columns.tolist(),
            "dtypes" : df.dtypes.astype(str).to_dict(),
            "memory_mb" : round(
                df.memory_usage(deep=True).sum() / (1024 ** 2), 2
            )
        }
    except Exception as e:
        return {
            "shape": (0, 0),
            "columns": [],
            "dtypes": {},
            "memory_mb": 0.0,
            "error": f"Failed to get dataset overview: {str(e)}"
        }

def get_missing_values(df):
    try:
        missing = pd.DataFrame({
            "Missing Count" : df.isnull().sum(),
            "Missing Percentage" : round(df.isnull().mean() * 100, 2)
        })
        return missing[missing["Missing Count"] > 0]
    except Exception:
        return pd.DataFrame(columns=["Missing Count", "Missing Percentage"])

def get_duplicate_count(df):
    try:
        return int(df.duplicated().sum())
    except Exception:
        return 0

def get_column_types(df):
    try:
        numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()
        return numerical_cols, categorical_cols
    except Exception:
        return [], []

def get_summary_statistics(df):
    try:
        return df.describe().T
    except Exception:
        return pd.DataFrame()

def get_skewness(df, numerical_cols):
    results = {}
    for col in numerical_cols:
        try:
            if col in df.columns:
                results[col] = round(skew(df[col].dropna()), 2)
        except Exception:
            results[col] = None
    return results

def detect_outliers(df, numerical_cols):
    results = {}
    for col in numerical_cols:
        try:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR

                outliers = df[(df[col] < lower) | (df[col] > upper)]
                results[col] = len(outliers)
        except Exception:
            results[col] = 0
    return results

def get_correlation_matrix(df, numerical_cols):
    try:
        valid_cols = [col for col in numerical_cols if col in df.columns]
        if not valid_cols:
            return pd.DataFrame()
        return df[valid_cols].corr()
    except Exception:
        return pd.DataFrame()

