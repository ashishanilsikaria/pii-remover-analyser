import streamlit as st
from typing import List
from pipeline import get_set_go

st.set_page_config(page_title="Ashish", layout="wide")
st.title("PII remover and analyser")


uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)


if uploaded_files:
    for file in uploaded_files:
        st.write(f"Uploaded file: {file.name}")
        st.write(f"File type: {file.type}")
        st.write(f"File size: {file.size} bytes")
        st.write("---")
        
        final_data = get_set_go(file)
        st.write(final_data)
