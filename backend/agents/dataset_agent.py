import pandas as pd

DATE_KEYWORDS = {"date", "time", "year", "month", "day", "timestamp", "dt", "created", "updated"}

class DatasetAgent:
    def __init__(self):
        pass

    def run(self, state: dict) -> dict:
        """
        Reads dataset and extracts data metadata.
        """
        file_path = state["file_path"]
        df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)

        # Limit preview to 500 rows for EDA speed on free tier
        df = df.head(500) if len(df) > 500 else df

        numeric_cols = df.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Only try datetime detection on columns whose names hint at dates — avoids slow full-column parse
        datetime_cols = []
        for col in df.columns:
            if any(kw in col.lower() for kw in DATE_KEYWORDS):
                try:
                    pd.to_datetime(df[col].dropna().head(5), errors="raise")
                    datetime_cols.append(col)
                except Exception:
                    pass

        dataset_info = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "missing_values": df.isnull().sum().to_dict(),
            "sample_values": {col: df[col].dropna().head(3).tolist() for col in df.columns},
        }

        return {
            "dataset_info": dataset_info
        }

def dataset_agent(state: dict) -> dict:
    return DatasetAgent().run(state)