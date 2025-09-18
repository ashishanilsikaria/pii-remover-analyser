import pandas as pd
import json
import io
from PIL import Image

from helpers import (
    my_logger,
    extract_content_from_pptx,
    extract_content_from_pdf,
)
from pii_remover import remove_pii_from_image, remove_pii_from_df
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

            pii_removed_image = remove_pii_from_image(input_file)

            analyzed_text_json = analyze_image_with_gemini(pii_removed_image, file_type)

            return json.loads(analyzed_text_json)  # type: ignore

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            df = pd.read_excel(input_file)

            anonymized_df = remove_pii_from_df(df.copy())

            csv_buffer = io.StringIO()
            anonymized_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            analyzed_text_json = analyze_dataframe_with_gemini(anonymized_df)

            my_logger.info(f"Excel DataFrame:\n{df.head()}")

            return json.loads(analyzed_text_json)  # type: ignore

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ):

            extracted_content_from_pptx = extract_content_from_pptx(input_file)

            text = extracted_content_from_pptx["text"]
            if text:
                my_logger.info(f"\nPPTX Text Content:\n{text}")

            tables = extracted_content_from_pptx["tables"]
            if tables:
                df_tables = pd.DataFrame(tables[0][1:], columns=tables[0][0])
                my_logger.info(f"\nFirst table as DataFrame:\n{df_tables.head()}")

            # to do
            # Sanitize text

            anonymized_df = pd.DataFrame()
            for table in tables:
                anonymized_table = remove_pii_from_df(table.copy())
                anonymized_df = pd.concat(
                    [anonymized_df, anonymized_table], ignore_index=True
                )

            images = extracted_content_from_pptx["images"]
            image_analysis_by_ai = []
            for image in images:
                data, ext = image
                image = Image.open(io.BytesIO(data))

                # To do
                # Sanitize image

                image_analysis_result = analyze_embedded_image_with_gemini(image)
                image_analysis_by_ai.append(image_analysis_result)

            analyzed_text_json = analyze_ppt_with_gemini(
                text, anonymized_df, image_analysis_by_ai
            )

            return json.loads(analyzed_text_json)  # type: ignore

        elif file_type == "application/pdf":

            extracted_content_from_pdf = extract_content_from_pdf(input_file)

            # To do
            # Sanitize text
            # sanitize images
            # send images to Gemini for analysis

            my_logger.info(f"PDF Text:\n{extracted_content_from_pdf}")

        return {"error": "Unsupported file type."}

    except Exception as e:
        my_logger.error(f"Error processing file {input_file.name}: {e}")
        return {"error": str(e)}
