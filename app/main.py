
import streamlit as st
from PIL import Image
from utils.import_data import load_data

st.set_page_config(page_title="Portfolio Dashboard", page_icon=":bar_chart:", layout="wide")
image = Image.open("assets/logo.webp")
image = image.resize((120, 80))

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
    ":file_folder: Upload a file",
    type=["csv", "txt", "xls", "xlsx"],
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.session_state["df"] = df
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.success("File loaded successfully!")
    except ValueError as error:
        st.error(str(error))
    except Exception:
        st.error("Could not load the uploaded file.")

if "df" in st.session_state:
    df = st.session_state["df"]
    st.dataframe(df)

    begin_date = df["date"][0]
    end_date = df["date"].iloc[-1]

    st.write(f"**Date Range:** \n {begin_date} - {end_date}")
    st.write(f"**Total Number of Transactions:** \n {len(df)}")
    st.write(f"**Currency:** \n {df['currency'].unique()[0]}")
    st.write(f"**Fees:** \n {df['fee'].sum()} {df['currency'].unique()[0]}")

else:
    st.info("Please upload a Trade Republic export file.")
