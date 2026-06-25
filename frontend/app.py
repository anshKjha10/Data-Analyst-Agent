import streamlit as st
import pandas as pd
import sys
import os

# Ensure project root is on sys.path so `backend` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.tools.data_loader import load_data
from backend.tools.eda_tools import run_complete_eda

st.title("Data Analysis and Visualization Tool")

uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")

    st.dataframe(df.head())

    results = run_complete_eda(df)

    st.subheader("Overview")

    st.write(results["overview"])

    st.subheader("Missing Values")

    st.dataframe(results["missing_values"])

    st.subheader("Summary Statistics")

    st.dataframe(
        results["summary_statistics"]
    )