# utils/reader.py
import pandas as pd
import os

def load_data(org_name):
    base_path = os.path.join("data", org_name)
    files = ["macro.xlsx", "meso.xlsx", "micro.xlsx", "Scores.xlsx"]
    data = {}
    for f in files:
        path = os.path.join(base_path, f)
        if os.path.exists(path):
            data[f.split(".")[0]] = pd.read_excel(path)
        else:
            st.error(f"File not found: {path}")
            data[f.split(".")[0]] = pd.DataFrame()
    return data["macro"], data["meso"], data["micro"], data["Scores"]

