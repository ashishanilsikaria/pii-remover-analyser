import io
import dotenv

from google import genai
from google.genai import types

from helpers import my_logger

dotenv.load_dotenv()

GEMINI_API_KEY = dotenv.get_key(".env", "GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


prompt = """You are a security consultant. Analyse and provide insights in a few lines. Don't add any additional text."""

prompt_for_output = """Generate a JSON object based on a security analysis.
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


# Analyze direct image input
def analyze_image_with_gemini(image, file_type):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    data = buf.getvalue()
    # my_file = client.files.upload(file=buf)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            prompt_for_output,
            genai.types.Part.from_bytes(data=data, mime_type="image/png"),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        ),
    )
    my_logger.info(f"Image analysis result:\n{response.text}")
    return response.text


# Analyze dataframe content
def analyze_dataframe_with_gemini(df):
    content = f"The following data was found in the excel file:{df.head().to_string()} "
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, content, prompt_for_output],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        ),
    )
    my_logger.info(f"DataFrame analysis result:\n{response}")
    return response.text


# Analyze embedded image in pptx
def analyze_embedded_image_with_gemini(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    data = buf.getvalue()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            genai.types.Part.from_bytes(data=data, mime_type="image/png"),
        ],
        config=genai.types.GenerateContentConfig(
            thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        ),
    )
    my_logger.info(f"Embedded image analysis result:\n{response}")
    return response.text


# Analyze pptx content
def analyze_ppt_with_gemini(text, tables, images):
    content = f"The following text:{text}, tables:{tables},and images:{images} were found in the pptx file."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, content, prompt_for_output],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        ),
    )
    my_logger.info(f"PPTX analysis result:\n{response}")
    return response.text


# # using bytes
# def analyze_image_with_gemini_direct(image_bytes):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=["What is this image?", image_bytes],
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0),
#             response_mime_type="application/json",
#         ),
#     )

#     return response.text


# using raw data
# def analyze_image_bytes_with_gemini(image_bytes):
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[f"{prompt_for_image_analysis} {image_bytes}"],
#         config=types.GenerateContentConfig(
#             thinking_config=types.ThinkingConfig(thinking_budget=0),
#             response_mime_type="application/json",
#         ),
#     )

#     return response.text
