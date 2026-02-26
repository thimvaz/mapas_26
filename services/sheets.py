import pandas as pd
import streamlit as st
from services.gcp import get_gspread_client

@st.cache_data(ttl=600) # Mantém os dados por 10 minutos
def carregar_planilha(sheet_id, aba=None):
    gc = get_gspread_client()
    sh = gc.open_by_key(sheet_id)
    ws = sh.sheet1 if aba is None else sh.worksheet(aba)
    return pd.DataFrame(ws.get_all_records())
