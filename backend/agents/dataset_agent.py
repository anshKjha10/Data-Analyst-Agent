import pandas as pd

def dataset_agent(state):
    """
    Reads dataset and extracts data
    """

    file_path = state["file_path"]
    df = pd.read_csv(file_path)

    numeric_cols = df.select_dtypes(
        include = ["int64", "float64"]
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include = ["object"]
    ).columns.tolist()

    datetime_cols = []

    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            datetime_cols.append(col)
        except:
            pass

    dataset_info = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "missing_values": df.isnull().sum().to_dict()
    }

    return{
        "dataset_info" : dataset_info
    }

    