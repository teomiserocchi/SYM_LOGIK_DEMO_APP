import streamlit as st
import pandas as pd
import json
import os
from utils.reader import load_data
from utils.extraction import estrai_macro, estrai_meso, estrai_micro, estrai_scores
from utils.prompt_builder import prompt_builder
from fpdf import FPDF
import io
from openai import OpenAI
import plotly.graph_objects as go

# --- Inizializza OpenAI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- File persistenza ---
REPORTS_FILE = "generated_reports.json"
PERMISSIONS_FILE = "permissions.json"
USERS_FILE = "credentials.json"

# --- Utility ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

USER_CREDENTIALS = load_users()

def load_reports():
    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except:
            return {}
    return {}

def save_reports(reports):
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

def load_permissions():
    if os.path.exists(PERMISSIONS_FILE):
        try:
            with open(PERMISSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- PDF ---
def create_pdf(report_text, startup_name, generated_by, logo_path="Sym Logik Logo.png"):
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "…": "...", "•": "-", "´": "'"
    }
    for k, v in replacements.items():
        report_text = report_text.replace(k, v)
    
    pdf = FPDF()
    pdf.add_page()
    if logo_path and os.path.exists(logo_path):
        pdf.image(logo_path, 10, 8, 25)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Startup Report: {startup_name}", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, report_text)
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "© SymLogik 2025 - Confidential", 0, 0, "C")

    pdf_bytes = pdf.output(dest="S").encode('latin-1')  # <-- importante
    pdf_buffer = io.BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    return pdf_buffer


# --- Funzione grafici ---
def plot_score_charts(score_dict):
    """
    Radar + barre orizzontali + tabella riepilogo per le 5 categorie principali.
    Chiavi normalizzate, radar ordinato per Score decrescente.
    """
    import math

    categories_excel = ["team", "product", "market", "businessmodel", "fundraising"]
    labels = ["Team", "Product", "Market", "Business Model", "Fundraising"]

    # Normalizza chiavi del dizionario
    clean = {}
    for k, v in (score_dict or {}).items():
        kk = k.lower().replace(" ", "").replace("-", "").replace("_", "")
        clean[kk] = v

    score_vals, risk_vals, strength_vals = [], [], []

    for cat in categories_excel:
        # Chiavi possibili: scoreteam, team_score, ecc.
        s = clean.get(f"score{cat}", 0)
        r = clean.get(f"risk{cat}", 0)
        stg = clean.get(f"strength{cat}", s - r)

        score_vals.append(s or 0)
        risk_vals.append(r or 0)
        strength_vals.append(stg or 0)

    combined = list(zip(labels, score_vals, risk_vals, strength_vals))
    combined.sort(key=lambda x: x[1], reverse=True)  # ordina per Score decrescente
    labels_sorted, score_sorted, risk_sorted, strength_sorted = zip(*combined)

    # Chiudi il radar
    score_radar = list(score_sorted) + [score_sorted[0]]
    risk_radar = list(risk_sorted) + [risk_sorted[0]]
    labels_radar = list(labels_sorted) + [labels_sorted[0]]

    # Radar chart
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(r=score_radar, theta=labels_radar, mode='lines+markers', name='Score', marker=dict(color='#FF6AB7')))
    radar_fig.add_trace(go.Scatterpolar(r=risk_radar, theta=labels_radar, mode='lines+markers', name='Risk', marker=dict(color='#FFB347')))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]),
                   angularaxis=dict(direction="clockwise", rotation=90)),
        title="Radar Chart - Score & Risk"
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # Bar chart
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=score_sorted, name='Score', orientation='h', marker=dict(color='#FF6AB7')))
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=risk_sorted, name='Risk', orientation='h', marker=dict(color='#FFB347')))
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=strength_sorted, name='Strength', orientation='h', marker=dict(color='#7D83F4')))
    bar_fig.update_layout(barmode='group', title='Horizontal Bar Chart - Categories')
    st.plotly_chart(bar_fig, use_container_width=True)

    # Tabella
    table_df = pd.DataFrame({
        "Category": labels_sorted,
        "Score": score_sorted,
        "Risk": risk_sorted,
        "Strength": strength_sorted
    })
    st.subheader("Meso Summary Table")
    st.dataframe(table_df.sort_values("Score", ascending=False))



def plot_advanced_radar_single(score_dict):
    """
    Radar chart + barre orizzontali + tabella per le metriche Micro.
    Aggiunta Strength calcolata (Score - Risk).
    """

    metrics = [
        "idea_validation", "awareness", "willingness_to_pay", "urgency",
        "solution_validation", "technological_feasibility", "competitive_advantage",
        "scalability_flexibility_adaptability", "scalability", "capital_intensity",
        "sustainability", "dependence_on_others", "dimension", "opportunities",
        "attractiveness_growth_barriers", "regulatory_issues", "milestones_achieved",
        "users_customers", "strategic_partnerships", "awards", "defensibility",
        "differentiation", "direct_and_indirect_competition", "derisking",
        "time_to_market", "trajectory", "quality_and_experience", "commitment",
        "completeness", "capital_raised", "interest", "captable"
    ]

    # Normalizza chiavi
    clean = {}
    for k, v in (score_dict or {}).items():
        kk = k.lower().replace(" ", "").replace("-", "").replace("_", "")
        clean[kk] = v

    score_vals, risk_vals, strength_vals = [], [], []
    for m in metrics:
        key = m.lower().replace("_", "")
        s = clean.get(f"score{key}", 0)
        r = clean.get(f"risk{key}", 0)
        stg = s - r
        score_vals.append(s or 0)
        risk_vals.append(r or 0)
        strength_vals.append(stg or 0)

    # Ordina per score decrescente
    display_labels = [m.replace("_", " ").title() for m in metrics]
    combined = list(zip(display_labels, score_vals, risk_vals, strength_vals))
    combined.sort(key=lambda x: x[1], reverse=True)
    labels_sorted, score_sorted, risk_sorted, strength_sorted = zip(*combined)

    # Chiudi il radar
    score_vals_closed = list(score_sorted) + [score_sorted[0]]
    risk_vals_closed = list(risk_sorted) + [risk_sorted[0]]
    labels_closed = list(labels_sorted) + [labels_sorted[0]]

    # Radar chart
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(r=score_vals_closed, theta=labels_closed, mode='lines+markers', name='Score',marker=dict(color='#FF6AB7')))
    radar_fig.add_trace(go.Scatterpolar(r=risk_vals_closed, theta=labels_closed, mode='lines+markers', name='Risk', marker=dict(color='#FFB347')))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]),
                   angularaxis=dict(direction="clockwise", rotation=90)),
        title="Micro Elements Analysis"
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # Bar chart
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=score_sorted, name='Score', orientation='h',marker=dict(color='#FF6AB7')))
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=risk_sorted, name='Risk', orientation='h', marker=dict(color='#FFB347')))
    bar_fig.add_trace(go.Bar(y=labels_sorted, x=strength_sorted, name='Strength', orientation='h',marker=dict(color="#7D83F4")))
    bar_fig.update_layout(barmode='group', title='Horizontal Bar Chart - Micro Elements')
    st.plotly_chart(bar_fig, use_container_width=True)

    # Tabella
    table_df = pd.DataFrame({
        "Metric": labels_sorted,
        "Score": score_sorted,
        "Risk": risk_sorted,
        "Strength": strength_sorted
    })
    st.subheader("Micro Elements Table")
    st.dataframe(table_df.sort_values("Score", ascending=False))



# --- Login ---
def login():
    st.title("SymLogik Startup Detective - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
            user_org = USER_CREDENTIALS[username]["org"]
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["org"] = user_org
            st.success(f"✅ Login riuscito! Welcome {username} in {user_org}")
            st.rerun()
        else:
            st.error("❌ Username o password are wrong")

# --- App principale ---
def app():
    st.sidebar.image("Sym Logik Logo.png", width=120)
    st.sidebar.success(f"Welcome {st.session_state['username']} in {st.session_state['org']}")

    org_name = st.session_state["org"]
    macro, meso, micro, scores = load_data(org_name)

    all_startup_list = macro["Startup"].dropna().unique().tolist()
    all_startup_list = [s.strip() for s in all_startup_list]

    user = st.session_state["username"]
    permissions = load_permissions()
    allowed_startups = all_startup_list if user == "admin" else permissions.get(user, [])

    if not allowed_startups:
        st.warning("You don't have Startups")
        return

    startup = st.sidebar.selectbox("Select your Startup", options=allowed_startups)
    if not startup:
        return

    macro_df, macro_fc = estrai_macro(macro, startup)
    meso_df, meso_fc = estrai_meso(meso, startup, macro_fc)
    micro_df, micro_fc = estrai_micro(micro, startup, meso_fc)
    score_dict = estrai_scores(scores, startup)

    st.subheader(f"Startup: {startup}")
    st.write(f"Organization: {org_name}")

    score_general = round(score_dict.get("Score", 0))
    risk_general = round(score_dict.get("Risk", 0))
    col1, col2 = st.columns(2)
    col1.metric("Score", score_general)
    col2.metric("Risk", risk_general)

    # --- Mostra grafici ---
    plot_score_charts(score_dict)
    


    # --- Radar avanzato + tabella ---
    plot_advanced_radar_single(score_dict)
    # --- Generazione report ---
    if "reports_generated" not in st.session_state:
        st.session_state["reports_generated"] = load_reports()
    reports = st.session_state["reports_generated"]
    already_generated = reports.get(startup)

    if already_generated:
        st.subheader("Critical Factors Analysis")
        st.write(already_generated["report"])
        pdf_file = create_pdf(already_generated["report"], startup, already_generated["generated_by"])
        st.download_button("Download PDF", data=pdf_file, file_name=f"{startup}_report.pdf", mime="application/pdf")
    else:
        if st.button("Generate Report", key=f"gen_{startup}"):
            with st.spinner("Analyzing startup..."):
                try:
                    prompt = prompt_builder(macro_df, meso_df, micro_df, score_dict)
                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[
                            {"role": "system", "content": "Sei un analista di startup."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                    )
                    report_text = response.choices[0].message.content

                    reports[startup] = {"report": report_text, "generated_by": user}
                    save_reports(reports)
                    st.session_state["reports_generated"] = reports

                    st.subheader("Critical Factors Analysis")
                    st.write(report_text)
                    pdf_file = create_pdf(report_text, startup, user)
                    st.download_button("Download PDF", data=pdf_file, file_name=f"{startup}_report.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- Main ---
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        login()
    else:
        app()

if __name__ == "__main__":
    main()
