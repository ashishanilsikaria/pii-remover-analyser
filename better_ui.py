import streamlit as st
import pandas as pd
from typing import List

from pipeline import get_set_go
from helpers import list_to_html_ol, my_logger
from models import ProcessedFile, filetypes

st.set_page_config(page_title="Ashish", layout="wide")
st.title("PII remover and analyser")


uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)


def create_results_table(results: List[ProcessedFile]) -> str:
    """Create HTML table from results for dynamic display"""
    if not results:
        return ""

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
    df["Key Findings"] = df["Key_findings"].apply(list_to_html_ol)

    return df.to_html(escape=False)


results: List[ProcessedFile] = []

if uploaded_files:
    # Create placeholders for dynamic updates
    progress_container = st.container()
    results_container = st.empty()

    # Show overall progress
    with progress_container:
        st.subheader("Processing Files")
        progress_bar = st.progress(0)
        status_text = st.empty()

    total_files = len(uploaded_files)

    for i, file in enumerate(uploaded_files):
        # Update progress
        current_progress = i / total_files
        progress_bar.progress(current_progress)
        status_text.text(f"Processing {file.name}... ({i+1}/{total_files})")

        with st.spinner(f"Processing {file.name}..."):
            try:
                data_from_pipeline = get_set_go(file)

                if data_from_pipeline:
                    # Check if there's an error in the pipeline response
                    if "error" in data_from_pipeline:
                        st.error(
                            f"Error processing {file.name}: {data_from_pipeline['error']}"
                        )
                        my_logger.error(
                            f"Pipeline error for {file.name}: {data_from_pipeline['error']}"
                        )
                    else:
                        # Successfully processed file
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

                        # Update the results display immediately
                        with results_container.container():
                            st.subheader("File Analysis Output")
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
                            df["Key Findings"] = df["Key Findings"].apply(
                                list_to_html_ol
                            )
                            st.markdown(
                                df.to_html(escape=False), unsafe_allow_html=True
                            )

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
                my_logger.error(f"Error processing {file.name}: {e}")

    # Final progress update
    progress_bar.progress(1.0)
    status_text.text(f"Completed processing all {total_files} files!")

    # Show final success message if any files were processed successfully
    if results:
        st.success(f"Successfully processed {len(results)} out of {total_files} files.")
