import streamlit as st
from PIL import Image
from utils.import_data import load_data
from pathlib import Path

st.set_page_config(page_title="Home", layout="wide")
image = Image.open("assets/logo.webp")
image = image.resize((120, 80))

def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# LOAD CUSTOM CSS
# =========================================================
CSS_FILE = Path(__file__).resolve().parent / "styles" / "main.css"
with open(CSS_FILE, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

st.markdown("""
<div class="dashboard-hero">
    <div class="hero-badge">PERSONAL PORTFOLIO ANALYTICS</div>
    <h1>Understand your portfolio.</h1>
    <p>
        Explore performance, allocation, transactions and passive
        income from your Trade Republic data.
    </p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### Import portfolio")
    st.caption(
        "Upload your Trade Republic CSV export, "
        "or continue exploring with the demo portfolio."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
    )


st.markdown("## Explore your portfolio")
col1, col2, col3 = st.columns(3)
with col1:
    feature_card(
        "📈",
        "Portfolio Overview",
        "Monitor portfolio value, invested capital and performance."
    )

with col2:
    feature_card(
        "🥧",
        "Asset Allocation",
        "See how your portfolio is distributed across assets and sectors."
    )

with col3:
    feature_card(
        "💸",
        "Dividends",
        "Track dividend income, taxes and your strongest income sources."
    )

col4, col5, col6 = st.columns(3)

with col4:
    feature_card(
        "🔁",
        "Transactions",
        "Search and analyse your complete transaction history."
    )

with col5:
    feature_card(
        "💳",
        "Expenses",
        "Understand fees, card expenses and spending activity."
    )

with col6:
    feature_card(
        "🔎",
        "Asset Analysis",
        "Inspect individual investments in greater detail."
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
        f"✓ Using {st.session_state['uploaded_file_name']}"
    )
else:
    st.info("🧪 Demo portfolio loaded · Upload a CSV to use your own data")

if df is not None and not df.empty:
    st.markdown("## Portfolio Snapshot")
    st.caption(
        "A quick overview based on the currently loaded transaction history."
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Transactions", len(df), help="Total number of transactions in the imported dataset.")
    with col2:
        invested = abs(df.loc[df["type"].isin(["BUY", "SELL"]), "amount"].sum())
        st.metric("Total invested", f"€{invested:,.2f}", help="Total amount invested in the portfolio.")
    with col3:
        assets = df.loc[df ["type"] == "BUY", "name"].nunique()
        st.metric("Assets purchased", assets, help="Number of unique assets purchased.")
    with col4:
        st.metric(
            "Date range",
            f"{df['date'].min():%b %Y} – {df['date'].max():%b %Y}",
            help="The date range of the loaded transaction data."
        )

    st.info(
        "Use the pages in the sidebar to explore your portfolio, transactions, "
        "dividends, expenses, and asset allocation."
    )

    with st.expander("Show raw transaction data"):
     st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("Please upload a Trade Republic export file.")
