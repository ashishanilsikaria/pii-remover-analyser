import streamlit as st
from typing import List
from models import ProcessedFile, filetypes
from pipeline import get_set_go
import pandas as pd

from helpers import list_to_html_ol, my_logger


st.set_page_config(page_title="Ashish", layout="wide")
st.title("PII remover and analyser")


uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)

results: List[ProcessedFile] = []

if uploaded_files:
    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):

            try:
                data_from_pipeline = get_set_go(file)

                if data_from_pipeline:

                    results.append(
                        ProcessedFile(
                            file_name=file.name,
                            file_type=filetypes[file.type],
                            file_heading=data_from_pipeline["file_description"][
                                "heading"
                            ],
                            file_description=data_from_pipeline["file_description"][
                                "description"
                            ],
                            key_findings=data_from_pipeline["key_findings"],
                        )
                    )

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

if results:
    table_rows = []

    for r in results:
        table_rows.append(
            {
                "File Name": r.file_name,
                "File Type": r.file_type,
                "File Description": f"<b>{r.file_heading}</b>"
                + "<br>"
                + r.file_description,
                "Key Findings": r.key_findings,
            }
        )

    df = pd.DataFrame(table_rows)

    st.subheader("File Analysis Output")

    df["Key Findings"] = df["Key Findings"].apply(list_to_html_ol)

    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
