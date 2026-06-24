import pandas as pd

def load_data(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")