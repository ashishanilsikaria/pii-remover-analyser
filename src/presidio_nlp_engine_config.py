import logging
import os
from typing import Tuple

from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.nlp_engine import (
    NlpEngine,
    NlpEngineProvider,
)

logger = logging.getLogger("presidio-streamlit")


def create_nlp_engine_with_spacy() -> Tuple[NlpEngine, RecognizerRegistry]:
    # def create_nlp_engine_with_spacy() -> NlpEngine:
    """
    Instantiate an NlpEngine with a spaCy model
    :param model_path: path to model / model name.
    """
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
        "ner_model_configuration": {
            "model_to_presidio_entity_mapping": {
                "PER": "PERSON",
                "PERSON": "PERSON",
                "NORP": "NRP",
                "FAC": "FACILITY",
                "LOC": "LOCATION",
                "GPE": "LOCATION",
                "LOCATION": "LOCATION",
                "ORG": "ORGANIZATION",
                "ORGANIZATION": "ORGANIZATION",
                "DATE": "DATE",
                "TIME": "TIME",
                "PERSON": "person",
                "EMAIL_ADDRESS": "email",
                "PHONE_NUMBER": "phone_number",
                "CREDIT_CARD": "credit_card",
                "DATE_TIME": "date_time",
                "URL": "url",
                "IP_ADDRESS": "ip_address",
                "IBAN_CODE": "iban",
                "US_SSN": "ssn",
                "US_PASSPORT": "passport",
                "US_DRIVER_LICENSE": "driver_license",
                "LOCATION": "location",
            },
            # "low_confidence_score_multiplier": 0.4,
            # "low_score_entity_names": ["ORG", "ORGANIZATION"],
        },
    }

    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    registry = RecognizerRegistry()

    base_dir = os.path.dirname(__file__)
    registry.add_recognizers_from_yaml(os.path.join(base_dir, "patterns", "emp.yaml"))
    registry.add_recognizers_from_yaml(os.path.join(base_dir, "patterns", "token.yaml"))

    registry.load_predefined_recognizers(nlp_engine=nlp_engine)

    return nlp_engine, registry
