import streamlit as st
from utils.analysis import render_asset_analysis_page

st.set_page_config(
    page_title="Asset Analysis",
    page_icon="📈",
    layout="wide",
)


render_asset_analysis_page()
