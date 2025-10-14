import pandas as pd

def estrai_macro(df_macro, startup):
    startup = startup.strip().lower()
    df_macro['Startup'] = df_macro['Startup'].astype(str).str.strip().str.lower()
    
    subset = df_macro[df_macro['Startup'] == startup].sort_values(by='Prio')
    rischio_cumulato = 0
    selected_rows = []
    
    for _, row in subset.iterrows():
        rischio_cumulato += row['Rischio%']
        selected_rows.append(row)
        if rischio_cumulato >= 90:
            break
    
    selected_df = pd.DataFrame(selected_rows)
    
    # Ritorno lista tuple (FC, valore)
    fc_valori = []
    if 'FC1' in selected_df.columns and 'FC1_Value' in selected_df.columns:
        fc_valori += selected_df[['FC1', 'FC1_Value']].dropna().values.tolist()
    if 'FC2' in selected_df.columns and 'FC2_Value' in selected_df.columns:
        fc_valori += selected_df[['FC2', 'FC2_Value']].dropna().values.tolist()
    
    return selected_df, fc_valori


def estrai_fattori_per_descrizioni(df, startup, descrizioni):
    startup = startup.strip().lower()
    df['Startup'] = df['Startup'].astype(str).str.strip().str.lower()
    df['Descr.'] = df['Descr.'].astype(str).str.strip().str.lower()
    descrizioni = [d.strip().lower() for d in descrizioni]
    
    selected_rows = []
    for desc in descrizioni:
        subset = df[(df['Startup'] == startup) & (df['Descr.'] == desc)].sort_values(by='Prio')
        rischio_cumulato = 0
        for _, row in subset.iterrows():
            rischio_cumulato += row['Rischio%']
            selected_rows.append(row)
            if rischio_cumulato >= 90:
                break
                
    selected_df = pd.DataFrame(selected_rows)
    
    fc_valori = []
    if 'FC1' in selected_df.columns and 'FC1_Value' in selected_df.columns:
        fc_valori += selected_df[['FC1', 'FC1_Value']].dropna().values.tolist()
    if 'FC2' in selected_df.columns and 'FC2_Value' in selected_df.columns:
        fc_valori += selected_df[['FC2', 'FC2_Value']].dropna().values.tolist()
    
    return selected_df, fc_valori


def estrai_meso(df_meso, startup, fc_macro):
    descrizioni = list(set([fc[0] for fc in fc_macro]))
    return estrai_fattori_per_descrizioni(df_meso, startup, descrizioni)

def estrai_micro(df_micro, startup, fc_meso):
    descrizioni = list(set([fc[0] for fc in fc_meso]))
    return estrai_fattori_per_descrizioni(df_micro, startup, descrizioni)

def estrai_scores(df_scores, startup):
    startup = startup.strip().lower()
    df_scores['Startup'] = df_scores['Startup'].astype(str).str.strip().str.lower()
    row = df_scores[df_scores['Startup'] == startup]
    if not row.empty:
        return row.iloc[0].to_dict()
    return {}
