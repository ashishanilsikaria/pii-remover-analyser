from presidio_image_redactor import ImageRedactorEngine
import streamlit as st
from PIL import Image
from helpers import my_logger
from presidio_nlp_engine_config import create_nlp_engine_with_spacy
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import pandas as pd


@st.cache_resource
def image_redactor_engine():
    return ImageRedactorEngine()


@st.cache_resource
def nlp_engine():
    return create_nlp_engine_with_spacy()


@st.cache_resource
def analyzer_engine():
    return AnalyzerEngine(nlp_engine=nlp_engine())


@st.cache_resource
def anonymizer_engine():
    return AnonymizerEngine()


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


def remove_pii_from_df(df):


    col1, col2 = st.columns(2)
    col1.dataframe(df)


    for column in df.select_dtypes(include=["object"]).columns:
        for index, value in df[column].items():
            if isinstance(value, str):
                results = analyzer_engine().analyze(
                    text=value,
                    # entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
                    language="en",
                )
                if results:
                    anonymized_value = anonymizer_engine().anonymize(
                        text=value, analyzer_results=results
                    )
                    # anonymized_value = anonymized_value['text']
                    df.at[index, column] = anonymized_value
    
    col2.dataframe(df)

    return df


# df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
# df["text"] = [st_text[res.start : res.end] for res in st_analyze_results]

# df_subset = df[["entity_type", "text", "start", "end", "score"]].rename(
#     {
#         "entity_type": "Entity type",
#         "text": "Text",
#         "start": "Start",
#         "end": "End",
#         "score": "Confidence",
#     },
#     axis=1,
# )
# df_subset["Text"] = [st_text[res.start : res.end] for res in st_analyze_results]
# if st_return_decision_process:
#     analysis_explanation_df = pd.DataFrame.from_records(
#         [r.analysis_explanation.to_dict() for r in st_analyze_results]
#     )
#     df_subset = pd.concat([df_subset, analysis_explanation_df], axis=1)
# st.dataframe(df_subset.reset_index(drop=True), use_container_width=True)
