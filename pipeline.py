# from utilities.gemini_data_analyzer import analyze_image_with_gemini
from gemini_data_analyzer import analyze_uploaded_image_with_gemini



def get_set_go(input_file):

    data = input_file.read()

    file_type = input_file.type

    if file_type in ["image/png", "image/jpg", "image/jpeg"]:

        analyzed_text_json = analyze_uploaded_image_with_gemini(input_file, file_type)
        return analyzed_text_json

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:

        s = 2

    elif file_type in [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]:
        s = 2

    elif file_type == "application/pdf":

        s = 2

    else:

        final_data = "Unsupported file type."

    return data
