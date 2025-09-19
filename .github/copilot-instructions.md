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

# Copilot Instructions for PII Remover Analyser

Overview
This repository is a Streamlit-based PII cleaning + analysis pipeline that (1) removes or redact PII from uploaded files, (2) sends sanitized content to Google Gemini for structured analysis, and (3) renders results in the UI and produces a PPTX summary.

Architecture & key files
- **UI / entry:** `src/streamlit_app.py` — handles uploads, progress spinners and calls `pipeline.get_set_go(file)` for each uploaded file.
- **Router / orchestrator:** `src/pipeline.py` — single entry `get_set_go(file)` that branches on MIME type and returns a parsed JSON dict (it calls `json.loads` on Gemini output).
- **AI integration:** `src/gemini_data_analyzer.py` — wraps `google-genai` client; uses `Part.from_bytes` for images and sets `response_mime_type='application/json'`. Prompts live here (`prompt`, `prompt_for_image`, `prompt_for_output`).
- **PII tooling:** `src/pii_remover.py` — Presidio + spaCy (`en_core_web_lg`) for text anonymization and image redaction; engines are cached with `@st.cache_resource`.
- **Helpers & IO:** `src/helpers.py` — PPTX/PDF extraction stubs, HTML helpers, and shared logger `my_logger` that writes to `app.log`.
- **Models:** `src/models.py` — `ProcessedFile` is the runtime model used by the UI (note a typing mismatch: `key_findings` typed as `str` but code passes a list).

Important patterns and conventions
- Centralized orchestration: always look for new file-type handling in `pipeline.get_set_go`; adding types means adding a MIME branch and calling existing sanitizer + gemini helpers.
- JSON-first AI contract: Gemini is expected to return strict JSON (see `src/extras/gemini_sample_analysis_return.json`). Pipeline directly calls `json.loads` — do not return Markdown fences or extra text.
- Presidio usage: heavy NLP/image engines are cached via Streamlit `@st.cache_resource` in `pii_remover.py`; reuse existing engine initializers in `src/presidio_nlp_engine_config.py` and `patterns/` for custom recognizers.
- Logger: use `helpers.my_logger` instead of prints so logs appear in `app.log` and console consistently.

Developer workflows (project-specific)
- Install dependencies (project expects Python 3.12+ and uses `uv`):
  - `uv sync`
- Run Streamlit UI locally:
  - `uv run streamlit run src/streamlit_app.py`
  - or run the small runner: `uv run python main.py`
- Quick: run the PPT generator directly:
  - `uv run src/generate_ppt.py`
- Environment: add a `.env` with `GEMINI_API_KEY` — `src/gemini_data_analyzer.py` reads it via `dotenv.get_key('.env','GEMINI_API_KEY')`.
- spaCy model: the wheel `en_core_web_lg-3.8.0-py3-none-any.whl` is included in the repository root; installer scripts or `pip install ./en_core_web_lg-3.8.0-py3-none-any.whl` may be needed.

Integration notes & gotchas
- JSON contract example (file: `src/extras/gemini_sample_analysis_return.json`):

  {"file_description": {"heading": "...", "description": "..."}, "key_findings": ["finding1","finding2"]}

- Typing mismatch: `src/models.py` declares `ProcessedFile.key_findings` as `str` but runtime/UI expects a list; prefer returning lists unless you update the UI.
- `helpers.extract_content_from_pdf` is a placeholder — PDFs currently have limited analysis. See `src/helpers.py` to extend.
- `src/generate_ppt.py:create_presentation` creates static slides today; it doesn't yet render per-file rows passed from Streamlit — extend this to produce per-file summary slides.

Where to change AI prompts or model versions
- Edit prompts and output schema enforcement in `src/gemini_data_analyzer.py` (`prompt`, `prompt_for_image`, `prompt_for_output`). Keep `response_mime_type='application/json'` and validate with `json.loads` in `pipeline.py`.

Quick examples (where to look)
- Add new MIME handler: `pipeline.get_set_go` (search for `get_set_go` in `src/pipeline.py`).
- Update Presidio recognizers: `patterns/*.yaml` and `src/presidio_nlp_engine_config.py`.
- Expected AI output example: `src/extras/gemini_sample_analysis_return.json`.

If something is unclear
- Flag ambiguous areas: PDF extraction, PPTX per-row rendering, and the `ProcessedFile.key_findings` type. Ask the maintainer whether to normalize `key_findings` as `List[str]` (recommended).

Feedback request
Please review and tell me if you want the instructions expanded to include: test commands, CI, or an example PR checklist for adding new file types.
