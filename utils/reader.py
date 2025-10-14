# utils/reader.py
import pandas as pd
import os

def load_data(org_name):
    base_path = os.path.join("data", org_name)
    macro = pd.read_excel(os.path.join(base_path, "macro.xlsx"))
    meso = pd.read_excel(os.path.join(base_path, "meso.xlsx"))
    micro = pd.read_excel(os.path.join(base_path, "micro.xlsx"))
    scores = pd.read_excel(os.path.join(base_path, "Scores.xlsx"))
    return macro, meso, micro, scores
