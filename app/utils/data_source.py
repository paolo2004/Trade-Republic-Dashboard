"""Which transaction export is loaded, and the UI for replacing it."""

import html
from pathlib import Path

import streamlit as st
from utils.import_data import load_data, validate_data

DEMO_FILE = Path(__file__).resolve().parents[2] / "assets" / "demo_transactions.csv"


def ensure_data_loaded():
    """Load the demo portfolio on first visit so every page has data to show."""
    if st.session_state.get("df") is not None:
        return

    try:
        st.session_state["df"] = load_data(DEMO_FILE)
    except Exception as error:
        st.error(f"Could not load demo data: {error}")
        st.stop()
    st.session_state["data_source"] = "demo"
    st.session_state["uploaded_file_name"] = None


@st.dialog("Import transactions")
def import_dialog():
    st.caption(
        "Upload your transaction export from Trade Republic. "
        "The file stays in this browser session and is never stored."
    )
    uploaded_file = st.file_uploader(
        "Transaction export", type=["csv"], label_visibility="collapsed"
    )

    if uploaded_file is not None:
        try:
            df = load_data(uploaded_file)
            validate_data(df)
        except Exception as error:
            st.error(f"Could not load the file: {error}")
            return
        st.session_state["df"] = df
        st.session_state["data_source"] = "upload"
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.rerun()

    if st.session_state.get("data_source") == "upload":
        if st.button("Switch back to demo portfolio", width="stretch"):
            st.session_state["df"] = None
            ensure_data_loaded()
            st.rerun()


def render_data_source_card():
    """Sidebar card naming the loaded file, with a button to replace it."""
    df = st.session_state["df"]
    if st.session_state.get("data_source") == "upload":
        name = st.session_state["uploaded_file_name"]
        detail = f"{len(df):,} rows · Trade Republic"
    else:
        name = "Demo portfolio"
        detail = f"{len(df):,} rows · sample data"

    safe_name = html.escape(name)
    with st.sidebar:
        with st.container(key="data_source_card"):
            st.markdown(
                f"""
                <div class="source-label">Data source</div>
                <div class="source-file">
                    <span class="source-icon" aria-hidden="true"></span>
                    <div>
                        <div class="source-name" title="{safe_name}">{safe_name}</div>
                        <div class="source-detail">{detail}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Replace file", key="replace_file", width="stretch"):
                import_dialog()
