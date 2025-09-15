# from utilities.gemini_data_analyzer import analyze_image_with_gemini
import pandas as pd
from gemini_data_analyzer import analyze_uploaded_image_with_gemini
from helpers import my_logger


def get_set_go(input_file):

    file_type = input_file.type

    my_logger.info(
        f"\n Processing file: {input_file.name}, Type: {file_type}, Size: {input_file.size} bytes"
    )

    if file_type in ["image/png", "image/jpg", "image/jpeg"]:

        # analyzed_text_json = analyze_uploaded_image_with_gemini(input_file, file_type)
        return "analyzed_text_json"

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        df = pd.read_excel(input_file)
        my_logger.info(f"Excel DataFrame:\n{df.head()}")

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]:
        s = 2

    elif file_type == "application/pdf":

        s = 2

    else:

        final_data = "Unsupported file type."

    return input_file
