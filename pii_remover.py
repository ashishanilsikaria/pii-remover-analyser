from presidio_image_redactor import ImageRedactorEngine
import streamlit as st
from PIL import Image
from helpers import my_logger


@st.cache_resource
def image_redactor_engine():
    return ImageRedactorEngine()


def remove_pii_from_image(input_file):
    try:

        image_redactor = image_redactor_engine()

        image = Image.open(input_file)
        pii_removed_image = image_redactor.redact(image=image, fill=(255, 0, 0))  # type: ignore
        
        col1, col2 = st.columns(2)
        col1.image(input_file, caption="Original Image", width="content")
        col2.image(
            pii_removed_image,  # type: ignore
            caption="PII Redacted Image",
            width="content",
        )

        return pii_removed_image
    

    except Exception as e:
        my_logger.error(f"Error processing file {input_file.name}: {e}")
        return {"error": str(e)}
