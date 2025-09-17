# from utilities.gemini_data_analyzer import analyze_image_with_gemini
import pandas as pd
from gemini_data_analyzer import (
    analyze_image_with_gemini,
    analyze_embedded_image_with_gemini,
    analyze_ppt_with_gemini,
)
from helpers import (
    my_logger,
    extract_pptx,
    strip_json_formatting,
    extract_text_from_pdf,
    # convert_images,
)
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine
import json
from PIL import Image
import io
import streamlit as st
from presidio_nlp_engine_config import create_nlp_engine_with_spacy


@st.cache_resource
def nlp_engine():
    return create_nlp_engine_with_spacy()


@st.cache_resource
def analyzer_engine():
    return AnalyzerEngine(nlp_engine=nlp_engine())


@st.cache_resource
def anonymizer_engine():
    return AnonymizerEngine()


@st.cache_resource
def image_redactor_engine():
    return ImageRedactorEngine()


def get_set_go(input_file) -> dict:

    try:

        file_type = input_file.type

        my_logger.info(
            f"\n Processing file: {input_file.name}, Type: {file_type}, Size: {input_file.size} bytes"
        )

        if file_type in ["image/png", "image/jpg", "image/jpeg"]:
            image_redactor = image_redactor_engine()

            image = Image.open(input_file)
            pii_removed_image = image_redactor.redact(image=image)  # type: ignore
            col1, col2 = st.columns(2)
            col1.image(input_file, caption="Original Image", width="content")
            col2.image(
                pii_removed_image,  # type: ignore
                caption="PII Redacted Image",
                width="content",
            )

            analyzed_text_json = analyze_image_with_gemini(pii_removed_image, file_type)
            stripped_data = strip_json_formatting(analyzed_text_json)
            json_data = json.loads(stripped_data)
            # json_data = {}
            return json_data

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            df = pd.read_excel(input_file)
            my_logger.info(f"Excel DataFrame:\n{df.head()}")

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ):

            extracted_content_from_pptx = extract_pptx(input_file)

            text = extracted_content_from_pptx["text"]
            if text:
                my_logger.info(f"\nPPTX Text Content:\n{text}")

            tables = extracted_content_from_pptx["tables"]
            if tables:
                df_tables = pd.DataFrame(tables[0][1:], columns=tables[0][0])
                my_logger.info(f"\nFirst table as DataFrame:\n{df_tables.head()}")

            # for img_bytes in extracted_content_from_pptx["images"]:
            # image_analysis_by_ai = analyze_image_bytes_with_gemini(img_bytes)
            # my_logger.info(f"Image analysis result:\n{image_analysis_by_ai}")
            images = extracted_content_from_pptx["images"]
            image_analysis_by_ai = []
            for image in images:
                data, ext = image
                image = Image.open(io.BytesIO(data))
                image_analysis_result = analyze_embedded_image_with_gemini(image)
                image_analysis_by_ai.append(image_analysis_result)

            analyzed_text_json = analyze_ppt_with_gemini(
                text, tables, image_analysis_by_ai
            )

            stripped_data = strip_json_formatting(analyzed_text_json)
            json_data = json.loads(stripped_data)
            return json_data

        elif file_type == "application/pdf":

            pdf_text = extract_text_from_pdf(input_file)
            my_logger.info(f"PDF Text:\n{pdf_text}")

        return {"error": "Unsupported file type."}

    except Exception as e:
        my_logger.error(f"Error processing file {input_file.name}: {e}")
        return {"error": str(e)}
