# from utilities.gemini_data_analyzer import analyze_image_with_gemini
import pandas as pd
from gemini_data_analyzer import (
    analyze_uploaded_image_with_gemini,
    analyze_image_bytes_with_gemini,
)
from helpers import (
    my_logger,
    extract_pptx,
    strip_json_formatting,
    extract_text_from_pdf,
)
import json


def get_set_go(input_file) -> dict:

    file_type = input_file.type

    my_logger.info(
        f"\n Processing file: {input_file.name}, Type: {file_type}, Size: {input_file.size} bytes"
    )

    if file_type in ["image/png", "image/jpg", "image/jpeg"]:

        analyzed_text_json = analyze_uploaded_image_with_gemini(input_file, file_type)
        stripped_data = strip_json_formatting(analyzed_text_json)
        json_data = json.loads(stripped_data)
        return json_data

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        df = pd.read_excel(input_file)
        my_logger.info(f"Excel DataFrame:\n{df.head()}")

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]:

        extracted_content_from_pptx = extract_pptx(input_file)
        my_logger.info(
            f"Extracted text from PPTX:\n{extracted_content_from_pptx['text']}, \nTables: {extracted_content_from_pptx['tables']}"
        )
        for img_bytes in extracted_content_from_pptx["images"]:
            image_analysis_by_ai = analyze_image_bytes_with_gemini(img_bytes)
            my_logger.info(f"Image analysis result:\n{image_analysis_by_ai}")
            break

        return extracted_content_from_pptx

    elif file_type == "application/pdf":

        pdf_text = extract_text_from_pdf(input_file)
        my_logger.info(f"PDF Text:\n{pdf_text}")

    else:

        final_data = "Unsupported file type."

    return input_file
