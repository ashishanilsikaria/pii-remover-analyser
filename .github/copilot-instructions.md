# Copilot Instructions for PII Remover Analyser

## Overview
Streamlit app that cleans PII and analyzes uploaded files (images, XLSX, PPTX, PDF) with Google Gemini, then renders results in the UI and saves a PPTX summary. Security/PII focus throughout.

## Architecture & Flow
- UI: `src/streamlit_app.py` handles uploads, spinners, table rendering, and calls `pipeline.get_set_go()` per file.
- Router: `src/pipeline.py:get_set_go(file)` branches by MIME type, logs, sanitizes content, and calls Gemini. Returns a JSON string parsed via `json.loads` to a dict.
- AI: `src/gemini_data_analyzer.py` uses `google-genai` (`gemini-2.5-flash`, `thinking_budget=0`, `response_mime_type="application/json"`). Prompts enforce a strict JSON schema.
- PII: `src/pii_remover.py` uses Presidio (spaCy `en_core_web_lg`) to redact images and anonymize text in DataFrames; engines are cached with `@st.cache_resource`.
- Utilities: `src/helpers.py` provides PPTX/PDF extraction stubs, HTML list formatting, and a shared logger `my_logger` writing to `app.log`.

## File-Type Handling (pipeline)
- Images (`image/png|jpeg`): `remove_pii_from_image` → `analyze_image_with_gemini(image)` → parse JSON.
- Excel (`.xlsx`): `pandas.read_excel` → `remove_pii_from_df` (string cells only) → `analyze_dataframe_with_gemini(df)` → parse JSON.
- PowerPoint (`.pptx`): `extract_content_from_pptx` (text/tables/images) → anonymize tables with `remove_pii_from_df` → analyze embedded images individually → `analyze_ppt_with_gemini(text, tables_df, image_results)`.
- PDF (`application/pdf`): `extract_content_from_pdf` currently returns text placeholder only; not yet analyzed with Gemini.

## JSON Contract (Gemini)
- Expected shape (see `src/extras/gemini_sample_analysis_return.json`):
  `{ "file_description": { "heading": str, "description": str }, "key_findings": [str, ...] }`.
- Responses are parsed with `json.loads` inside `pipeline.py`; ensure Gemini returns valid JSON (no markdown fences).

## UI & Output
- Results mapped to `ProcessedFile` (see `src/models.py`) and displayed as an HTML table; `helpers.list_to_html_ol` renders `key_findings` lists.
- PPT: `src/generate_ppt.py:create_presentation(data, output_filename)` currently produces static slides (does not yet render per-file rows passed from Streamlit).

## Conventions & Gotchas
- Logging: use `helpers.my_logger` for consistent file + console logs. Avoid print.
- Types: `models.ProcessedFile.key_findings` is typed `str` but code passes a list; keep the runtime behavior (list) consistent with UI expectations.
- Presidio models: spaCy model `en_core_web_lg` is installed via `pyproject.toml`. Engines are heavy; rely on `@st.cache_resource`.
- Gemini key: `gemini_data_analyzer.py` reads from `.env` via `dotenv.get_key(".env", "GEMINI_API_KEY")`; ensure a `.env` file exists.

## Developer Workflow
- Install deps (Python 3.12+, uses uv):
  - `uv sync`
- Run app:
  - `uv run streamlit run src/streamlit_app.py`
  - or `uv run python main.py`
- Try PPT generator alone:
  - `uv run src/generate_ppt.py`
- Logs: tail `app.log` for pipeline/Gemini results.

## Extending/Changing Behavior
- New file types: add a MIME branch in `pipeline.get_set_go` and reuse Presidio/Gemini helpers.
- Gemini prompts: update `prompt`, `prompt_for_image`, `prompt_for_output` in `gemini_data_analyzer.py`. Keep response_mime_type JSON and parse in pipeline.
- PDF analysis: implement text/image extraction in `helpers.extract_content_from_pdf` and wire into Gemini similarly to PPTX.

## External Integrations
- Google Gemini (`google-genai`) for analysis; uses `Part.from_bytes` for images and plain text for tabular/text content.
- Presidio Analyzer/Anonymizer/Image Redactor for PII with spaCy `en_core_web_lg` (see `src/presidio_nlp_engine_config.py`, custom recognizers in `patterns/`).