import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import os
import json

try:
    os.environ["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    pass

from sample_data import generate_maintenance_data, generate_equipment_specs
from analyzer import ReliabilityAnalyzer
from agent import AIONAgent

st.set_page_config(
    page_title="AION · Confiabilidade Industrial",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#060a10;}
[data-testid="stSidebar"]{background:#080d14;border-right:1px solid #0ff2;}
html,body,[class*="css"]{font-family:'Segoe UI',sans-serif;color:#cdd9e5;}
.aion-logo{font-size:2.2rem;font-weight:900;letter-spacing:6px;
background:linear-gradient(90deg,#00f0ff,#7b5ea7,#00f0ff);
background-size:200%;-webkit-background-clip:text;
-webkit-text-fill-color:transparent;}
.kpi-card{background:#0d1520;border:1px solid #0ff3;border-radius:14px;
padding:20px;text-align:center;}
.kpi-value{font-size:1.8rem;font-weight:700;}
.kpi-label{font-size:.8rem;color:#8b949e;margin-top:4px;}
.c-cyan{color:#00f0ff;}.c-green{color:#3fb950

