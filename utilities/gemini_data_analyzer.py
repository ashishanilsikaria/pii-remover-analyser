from google import genai
from google.genai import types


import dotenv

dotenv.load_dotenv()

GEMINI_API_KEY = dotenv.get_key(".env", "GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """Generate a JSON object based on a security analysis of the content of the uploaded file.
The JSON object must have the following structure:
1.  A top-level key named "file_description". Its value must be a JSON object containing:
    - A key "heading" with a string value.
    - A key "description" with a string value.
2.  A top-level key named "key_findings". Its value must be an array of strings, where each string is a distinct security finding.

Here is the exact format to follow:
{
  "file_description": {
    "heading": "",
    "description": ""
  },
  "key_findings": [
  ]
}"""


def analyze_uploaded_image_with_gemini(input_file, file_type):
    image_bytes = input_file.getvalue()
    # uploaded_file = client.files.upload(file=input_file.getvalue)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=file_type,
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )

    return response.text


# # using bytes
# def analyze_image_with_gemini_direct(image_bytes):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=["What is this image?", image_bytes],
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0)
#         ),
#     )

#     return response.text


# # using raw data
# def analyze_data_with_gemini(raw_data):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[f"Analyze the following data and provide insights: {raw_data}"],
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0)
#         ),
#     )

#     return response.text
