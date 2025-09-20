import streamlit as st
import pandas as pd
from typing import List

from pipeline import get_set_go
from helpers import list_to_html_ol, my_logger
from models import ProcessedFile, filetypes
from generate_ppt import create_presentation

st.set_page_config(page_title="File Analyser", layout="wide")
st.title("PII remover and analyser")


uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)

generate_ppt = st.button(label="Generate PPT from analysis")
download_button = st.download_button

# Initialize session state stores
if "results" not in st.session_state:
    st.session_state["results"] = []
if "ppt_rows" not in st.session_state:
    st.session_state["ppt_rows"] = []
if "files_key" not in st.session_state:
    st.session_state["files_key"] = None


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
        st.session_state["ppt_rows"].append(
            [
                r.file_name,
                r.file_type,
                r.file_heading,
                r.file_description,
                r.key_findings,
            ]
        )

    df = pd.DataFrame(table_rows)
    df["Key Findings"] = df["Key Findings"].apply(list_to_html_ol)

    return df.to_html(escape=False)


results: List[ProcessedFile] = st.session_state["results"]

if uploaded_files:
    current_files_key = [
        (f.name, getattr(f, "size", None), f.type) for f in uploaded_files
    ]

    # Only process if the uploaded files changed
    if st.session_state["files_key"] != current_files_key:
        # Reset caches for new file set
        st.session_state["results"] = []
        st.session_state["ppt_rows"] = []
        results = st.session_state["results"]

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
            current_progress = (i + 1) / total_files
            progress_bar.progress(current_progress)
            status_text.text(f"Processing {file.name}... ({i+1}/{total_files})")

            with st.spinner(f"Processing {file.name}..."):
                try:
                    data_from_pipeline = get_set_go(file)

                    if data_from_pipeline:
                        if "error" in data_from_pipeline:
                            st.error(
                                f"Error processing {file.name}: {data_from_pipeline['error']}"
                            )
                            my_logger.error(
                                f"Pipeline error for {file.name}: {data_from_pipeline['error']}"
                            )
                        else:
                            processed = ProcessedFile(
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
                            results.append(processed)

                            st.session_state["ppt_rows"].append(
                                [
                                    processed.file_name,
                                    processed.file_type,
                                    processed.file_heading,
                                    processed.file_description,
                                    processed.key_findings,
                                ]
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

        # Final progress update and cache the file key
        progress_bar.progress(1.0)
        status_text.text(f"Completed processing all {total_files} files!")
        st.session_state["files_key"] = current_files_key

        # Show final success message if any files were processed successfully
        if results:
            st.success(
                f"Successfully processed {len(results)} out of {total_files} files."
            )
    else:
        # Files unchanged; use cached results
        if st.session_state["results"]:
            st.info("Using cached analysis. Click Generate PPT when ready.")
            df = pd.DataFrame(
                [
                    {
                        "File Name": r.file_name,
                        "File Type": r.file_type,
                        "File Description": f"<b>{r.file_heading}</b>"
                        + "<br>"
                        + r.file_description,
                        "Key Findings": r.key_findings,
                    }
                    for r in st.session_state["results"]
                ]
            )
            df["Key Findings"] = df["Key Findings"].apply(list_to_html_ol)
            st.subheader("File Analysis Output")
            st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

if generate_ppt:
    try:
        if not st.session_state["results"]:
            st.warning("Please upload files before generating PPT.")
            st.stop()

        create_presentation(
            st.session_state["ppt_rows"], output_filename="analysis_output.pptx"
        )
        download_button(
            label="Download PPT",
            data=open("analysis_output.pptx", "rb").read(),
            file_name="analysis_output.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            on_click="ignore",
        )

    except Exception as e:
        st.error(f"Error generating PPT: {e}")
        my_logger.error(f"Error generating PPT: {e}")
