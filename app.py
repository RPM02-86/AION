import streamlit as st
import pandas as pd

from sample_data import generate_maintenance_data
from analyzer import ReliabilityAnalyzer
from agent import AIONAgent

# ---------------------------------------------------------
# CONFIG BÁSICA
# ---------------------------------------------------------
st.set_page_config(
    page_title="AION · Confiabilidade Industrial",
    page_icon="🤖",
    layout="wide",
)

st.title("AION · Agente de Confiabilidade Industrial")

st.markdown(
    """
Este app está rodando na nuvem com dados **simulados** de uma fábrica de sopro e envase de água mineral.

Use as abas abaixo para navegar:
- **Dashboard**: visão geral de KPIs
- **Pareto & FMEA**: análise de causas e riscos
- **Chat AION**: converse com o agente de confiabilidade
"""
)

# ---------------------------------------------------------
# CARREGA DADOS SIMULADOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = generate_maintenance_data()
    az = ReliabilityAnalyzer(df)
    return df, az

df, az = load_data()

# ---------------------------------------------------------
# ABA PRINCIPAL
# ---------------------------------------------------------
aba = st.sidebar.radio(
    "Navegação",
    ["Dashboard", "Pareto & FMEA", "Chat AION"],
)

# ---------------------------------------------------------
# DASHBOARD SIMPLES
# ---------------------------------------------------------
if aba == "Dashboard":
    st.header("📊 Dashboard de Confiabilidade (simplificado)")

    kpis = az.calcular_mtbf()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Custo total (R$)",
            f"{df['custo_reparo'].sum():,.0f}".replace(",", "."),
        )
    with col2:
        st.metric(
            "Horas de parada",
            f"{df['tempo_reparo_horas'].sum():.0f} h",
        )
    with col3:
        pct_corr = (df["tipo_manutencao"] == "Corretiva").mean() * 100
        st.metric(
            "% Manutenção Corretiva",
            f"{pct_corr:.1f} %",
        )

    st.subheader("MTBF / Disponibilidade por equipamento")
    st.dataframe(kpis, use_container_width=True)

# ---------------------------------------------------------
# PARETO & FMEA
# ---------------------------------------------------------
elif aba == "Pareto & FMEA":
    st.header("📈 Pareto & FMEA")

    pf, pe = az.analise_pareto()
    fmea = az.analise_fmea()

    st.subheader("Pareto de modos de falha")
    st.dataframe(pf, use_container_width=True, height=300)

    st.subheader("Pareto de equipamentos por custo")
    st.dataframe(pe, use_container_width=True, height=300)

    st.subheader("FMEA (Top 15 RPN)")
    st.dataframe(fmea.head(15), use_container_width=True, height=400)

# ---------------------------------------------------------
# CHAT AION
# ---------------------------------------------------------
elif aba == "Chat AION":
    st.header("🤖 Chat com o AION")

    # lê chave da OpenAI dos secrets (se existir)
    api_key = ""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        api_key = ""

    # inicializa agente
    if "aion_agent" not in st.session_state:
        st.session_state.aion_agent = AIONAgent(df, api_key=api_key)
        st.session_state.chat_hist = []

    agent: AIONAgent = st.session_state.aion_agent

    # histórico de chat
    for role, text in st.session_state.get("chat_hist", []):
        if role == "user":
            st.markdown(f"**Você:** {text}")
        else:
            st.markdown(f"**AION:** {text}")

    st.markdown("---")
    pergunta = st.text_input("Digite sua pergunta para o AION:")

    if st.button("Enviar") and pergunta.strip():
        resp, modo = agent.chat(pergunta)
        st.session_state.chat_hist.append(("user", pergunta))
        st.session_state.chat_hist.append(
            ("aion", f"{resp}\n\n_(modo: {modo})_")
        )
        st.experimental_rerun()
