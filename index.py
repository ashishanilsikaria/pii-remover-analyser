import streamlit as st


st.set_page_config(page_title="Ashish", layout="wide")
st.title("PII remover and analyser")


uploaded = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)

