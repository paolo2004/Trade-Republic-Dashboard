from pathlib import Path
import streamlit as st
from utils.chart import register_chart_theme

STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"


@st.cache_data
def _read_css(names):
    return "\n".join((STYLES_DIR / name).read_text(encoding="utf-8") for name in names)


def setup_page(title, icon, *extra_css):
    """Configure the page, apply the stylesheets and register the chart theme.

    Must be the first Streamlit call in a page, because `st.set_page_config`
    has to run before anything else renders.
    """
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    css = _read_css(("tokens.css", "main.css", *extra_css))
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    register_chart_theme()
