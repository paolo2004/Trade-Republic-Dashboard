import streamlit as st
from PIL import Image
from utils.import_data import load_data
from pathlib import Path

st.set_page_config(page_title="Portfolio Dashboard", page_icon=":bar_chart:", layout="wide")
image = Image.open("assets/logo.webp")
image = image.resize((120, 80))

DEMO_FILE = Path(__file__).resolve().parent.parent / "assets" / "demo_transactions.csv"

# =========================================================
# INITIALIZE SESSION STATE
# =========================================================
if "df" not in st.session_state:
    st.session_state["df"] = None

if "data_source" not in st.session_state:
    st.session_state["data_source"] = None

if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None

col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image)

html_title = """
    <style>
    h1 {
        font-weight: bold;
        padding:1px;
        color: #4CAF50;
        border-radius: 6px;
    }
    </style>
    <center><h1>Trade Republic Dashboard</h1></center>
"""

with col2:
    st.markdown(html_title, unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    ":file_folder: Upload your own file",
    type=["csv", "txt", "xls", "xlsx"],
)

if uploaded_file is not None:
    # Only reload when a NEW file was uploaded
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.get("uploaded_file_id") != file_id:
        try:
            df = load_data(uploaded_file)
            st.session_state["df"] = df
            st.session_state["data_source"] = "upload"
            st.session_state["uploaded_file_name"] = uploaded_file.name
            st.session_state["uploaded_file_id"] = file_id
        except Exception as error:
            st.error(f"Could not load the file: {error}")
            st.stop()

# =========================================================
# LOAD DEMO DATA ONLY IF NOTHING IS STORED
# =========================================================
elif st.session_state["df"] is None:
    try:
        df = load_data(DEMO_FILE)
        st.session_state["df"] = df
        st.session_state["data_source"] = "demo"
        st.session_state["uploaded_file_name"] = None
        st.session_state["uploaded_file_id"] = None
    except Exception as error:
        st.error(f"Could not load demo data: {error}")
        st.stop()

df = st.session_state["df"]

if st.session_state["data_source"] == "upload":
    st.success(
        f"Your personal file is loaded: "
        f"**{st.session_state['uploaded_file_name']}**"
    )
else:
    st.info(
        "Showing demo data. Upload your Trade Republic export "
        "to use your own portfolio."
    )

if df is not None and not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Transactions", len(df))
    with col2:
        invested = abs(df.loc[df["type"].isin(["BUY", "SELL"]), "amount"].sum())
        st.metric("Total invested", f"€{invested:,.2f}")
    with col3:
        assets = df.loc[df ["type"] == "BUY", "name"].nunique()
        st.metric("Assets purchased", assets)
    with col4:
        st.metric(
            "Date range",
            f"{df['date'].min():%b %Y} – {df['date'].max():%b %Y}",
        )

    st.info(
        "Use the pages in the sidebar to explore your portfolio, transactions, "
        "dividends, expenses, and asset allocation."
    )

    with st.expander("Show raw transaction data"):
     st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("Please upload a Trade Republic export file.")
