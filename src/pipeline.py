import pandas as pd
import json
import io
from PIL import Image

from helpers import (
    my_logger,
    extract_content_from_pptx,
    extract_content_from_pdf,
)
from pii_remover import remove_pii_from_image, remove_pii_from_df, remove_pii_from_text
from gemini_data_analyzer import (
    analyze_image_with_gemini,
    analyze_dataframe_with_gemini,
    analyze_embedded_image_with_gemini,
    analyze_ppt_with_gemini,
)


def get_set_go(input_file) -> dict:

    try:

        file_type = input_file.type

        my_logger.info(
            f"\n Processing file: {input_file.name}, Type: {file_type}, Size: {input_file.size} bytes"
        )

        if file_type in ["image/png", "image/jpg", "image/jpeg"]:

            try:

                pii_removed_image = remove_pii_from_image(input_file)

                analyzed_text_json = analyze_image_with_gemini(
                    pii_removed_image, file_type
                )

                return json.loads(analyzed_text_json)  # type: ignore
            except Exception as e:
                my_logger.error(f"Error processing image file {input_file.name}: {e}")
                return {"error": str(e)}

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            try:
                df = pd.read_excel(input_file)

                anonymized_df = remove_pii_from_df(df.copy())

                analyzed_text_json = analyze_dataframe_with_gemini(anonymized_df)

                my_logger.info(f"Excel DataFrame:\n{df.head()}")

                return json.loads(analyzed_text_json)  # type: ignore

            except Exception as e:
                my_logger.error(f"Error processing Excel file {input_file.name}: {e}")
                return {"error": str(e)}

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ):
            try:
                extracted_content_from_pptx = extract_content_from_pptx(input_file)

                text = extracted_content_from_pptx["text"]
                sanitized_text = []
                if text:
                    for texts in text:
                        sanitized_text.append(remove_pii_from_text(texts))

                tables = extracted_content_from_pptx["tables"]
                anonymized_df = []
                if tables:
                    for table in tables:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        anonymized_table = remove_pii_from_df(df.copy())
                        anonymized_df.append(anonymized_table)

                images = extracted_content_from_pptx["images"]
                image_analysis_by_ai = []
                if images:
                    for image in images:
                        data = image
                        image = Image.open(io.BytesIO(data))

                        pii_removed_image = remove_pii_from_image(image)
                        image_analysis_result = analyze_embedded_image_with_gemini(
                            pii_removed_image
                        )

                        image_analysis_by_ai.append(image_analysis_result)

                analyzed_text_json = analyze_ppt_with_gemini(
                    text, anonymized_df, image_analysis_by_ai
                )

                return json.loads(analyzed_text_json)  # type: ignore

            except Exception as e:
                my_logger.error(f"Error processing PPTX file {input_file.name}: {e}")
                return {"error": str(e)}

        elif file_type == "application/pdf":
            try:

                extracted_content_from_pdf = extract_content_from_pdf(input_file)

                text = extracted_content_from_pdf["text"]
                sanitized_text = []
                if text:
                    for texts in text:
                        sanitized_text.append(remove_pii_from_text(texts))

                images = extracted_content_from_pdf["images"]
                image_analysis_by_ai = []
                if images:
                    for image in images:
                        data, ext = image
                        image = Image.open(io.BytesIO(data))

                        pii_removed_image = remove_pii_from_image(image)
                        image_analysis_result = analyze_embedded_image_with_gemini(
                            pii_removed_image
                        )
                        image_analysis_by_ai.append(image_analysis_result)

                my_logger.info(f"PDF Text:\n{extracted_content_from_pdf}")
            except Exception as e:
                my_logger.error(f"Error processing PDF file {input_file.name}: {e}")
                return {"error": str(e)}

        return {"error": "Unsupported file type."}

    except Exception as e:
        my_logger.error(f"Error processing file {input_file.name}: {e}")
        return {"error": str(e)}
