from google import genai
from google.genai import types
import io

import dotenv

dotenv.load_dotenv()

GEMINI_API_KEY = dotenv.get_key(".env", "GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

prompt_for_original_image = """You are a security consultant.
Generate a JSON object based on a security analysis of the content of the uploaded file.
The JSON object must have the following structure:
1.  A top-level key named "file_description". Its value must be a JSON object containing:
    - A key "heading" with a string value.
    - A key "description" with a string value.
2.  A top-level key named "key_findings". Its value must be an array of three to four strings, where each string is a distinct security finding.

Here is the exact format to follow:
{
  "file_description": {
    "heading": "",
    "description": ""
  },
  "key_findings": [
  ]
}"""

prompt_for_image_analysis = """You are a security consultant. Analyse the image and provide insights. Don't add any additional text."""


def analyze_image_with_gemini(input_file, file_type):
    image_bytes = input_file.getvalue()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt_for_original_image,
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


def analyze_embedded_image_with_gemini(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    data = buf.getvalue()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt_for_image_analysis,
            genai.types.Part.from_bytes(
                data=data,
                mime_type="image/png"
            ),
        ],
        config=genai.types.GenerateContentConfig(
            thinking_config=genai.types.ThinkingConfig(thinking_budget=0)
        ),
    )
    return response


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


# using raw data
# def analyze_image_bytes_with_gemini(image_bytes):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[f"{prompt_for_image_analysis} {image_bytes}"],
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0)
#         ),
#     )

#     return response.text
