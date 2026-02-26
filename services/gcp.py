import streamlit as st
import gspread

@st.cache_resource
def get_gspread_client():
    creds = st.secrets["gcp_service_account"]
    return gspread.service_account_from_dict(creds)

