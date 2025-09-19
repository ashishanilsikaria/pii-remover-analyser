System Design: PII Remover & Insight Analyzer

- Context: Streamlit app that ingests files, removes PII using Presidio, analyzes sanitized content with Google Gemini, and outputs a PPTX summary and on-screen table.

**System Requirements**
- Functional: Upload images, XLSX, PPTX, PDFs; extract content; remove PII; analyze sanitized data; display results; export PPTX summary.
- Non-functional: Strong PII/privacy posture; consistent JSON contract from AI; observable logs; deterministic UI rendering; scalable for large files; minimal latency for small files.

**Proposed Architecture & Workflow**
- Modular pipeline with clear separation: UI → Router → Extractors → PII Cleanser → AI Analyzer → Result Mapper → PPTX Generator.
- Strict JSON response contract between Analyzer and Router.

**Workflow Diagram**
- User Upload (Streamlit) ➔ [1. Router `pipeline.get_set_go`] ➔ [2. Pre-processing & Extraction] ➔ [3. Cleansing Engine (Presidio)] ➔ [4. Analysis Engine (Gemini)] ➔ [5. Results Mapping + PPTX Generator] ➔ UI Table + PPTX Download

**Module Descriptions**
1. Router & File Ingestion
- Entry: `src/streamlit_app.py` handles uploads; calls `pipeline.get_set_go(file)`.
- Routing: Detect MIME and dispatch:
  - `image/png|jpeg` → image redaction and analysis
  - `.xlsx` → DataFrame PII removal → analysis
  - `.pptx` → text/tables/images extraction → targeted cleansing → analysis
  - `application/pdf` → text/image extraction (extend) → analysis
- Contract: Returns dict parsed from strict JSON produced by Analyzer.

2. Pre-processing & Extraction
- Excel: `pandas.read_excel` with string-cell focus.
- PPTX: `helpers.extract_content_from_pptx` to collect slide text, tables, and embedded images.
- PDF: `helpers.extract_content_from_pdf` (extend to real text/image extraction; current stub returns placeholder text).
- Images: Loaded as bytes; fed to Presidio Image Redactor and Gemini as needed.

3. Cleansing Engine (Anonymization) 🛡️
- Technology: Microsoft Presidio (Analyzer, Anonymizer, ImageRedactor) with spaCy `en_core_web_lg`.
- Resource Management: Engines cached with `@st.cache_resource` to avoid cold starts.
- Text PIIs (DataFrames): `pii_remover.remove_pii_from_df` anonymizes string cells only; configurable recognizers via `patterns/`.
- Image PIIs: `pii_remover.remove_pii_from_image` masks detections directly on images.
- NLP Config: `presidio_nlp_engine_config.py` defines NLP pipeline and recognizers.
- Outcome: Sanitized artifacts move forward to AI; never send raw PII to Gemini.

4. Analysis Engine 🧠
- Technology: Google Gemini via `google-genai` (`gemini-2.5-flash`) in `gemini_data_analyzer.py`.
- Response Discipline: `response_mime_type="application/json"`, `thinking_budget=0`, no markdown fences.
- Prompts: `prompt`, `prompt_for_image`, `prompt_for_output` enforce a strict schema and concise, deterministic outputs.
- JSON Contract:
  - Shape: `{ "file_description": { "heading": str, "description": str }, "key_findings": [str, ...] }`
  - Parsing: `pipeline` uses `json.loads` and maps to `ProcessedFile`. Keep `key_findings` as list for UI expectations (despite type).
- Modes:
  - Images: `analyze_image_with_gemini(image_bytes)`.
  - DataFrames: `analyze_dataframe_with_gemini(df)`.
  - PPTX bundle: `analyze_ppt_with_gemini(text, tables_df, image_results)`.
  - PDF: wire similar to PPTX after extraction improvements.

5. Results Mapping & Report Generator
- Mapping: `models.ProcessedFile` used to store per-file outputs; lists rendered via `helpers.list_to_html_ol`.
- UI: Streamlit renders a styled results table and provides PPTX download.
- PPTX: `generate_ppt.create_presentation(data, output_filename)` generates a deck; extend to iterate per-file rows to mirror UI table.

**Proposed Technology Stack**
- Backend: Python 3.12+, Streamlit UI.
- File Processing: `pandas`, `python-pptx`, `openpyxl`, `pillow`.
- OCR (optional enhancement): `pytesseract` for scanned PDFs/images.
- PII Cleansing: Microsoft Presidio + spaCy `en_core_web_lg` with custom patterns.
- LLM Engine: Google Gemini via `google-genai` SDK.
- Packaging/Dev: `uv`, `pyproject.toml`.
- Logging: Shared `helpers.my_logger` to `app.log` and console.

**Security & Privacy**
- Data Flow: Only sanitized text/images reach Gemini; raw PII never leaves the process.
- Keys & Config: `dotenv.get_key(".env", "GEMINI_API_KEY")`; `.env` required and not committed.
- Logging Hygiene: No PII or large payloads in logs; log event metadata and sizes only.
- Caching: Securely cache Presidio resources; avoid caching sensitive content.

**Error Handling & Observability**
- Robust Parsing: Guard `json.loads` with try/except and fallbacks; log analyzer errors with minimal context.
- Timeouts/Retries: Set sensible Gemini timeouts and one retry with jitter.
- Telemetry: Count processed files by type, redaction stats, analyzer success/failure.

**Extensibility**
- New Types: Add MIME branch in `pipeline.get_set_go` and reuse extract/clean/analyze/emit pattern.
- Prompts: Evolve `gemini_data_analyzer.py` prompts; preserve JSON schema and deterministic outputs.
- PDF Enhancements: Implement real text and image extraction; optionally add OCR for scanned pages.
- PPTX Improvements: Render per-file rows with headings and bullet findings mirroring UI.

**Operational Notes**
- Run:
  - `uv sync` to install dependencies
  - `uv run streamlit run src/streamlit_app.py` for the app
  - `uv run python main.py` alternate entry
- Logs: Tail `app.log` for pipeline and analyzer insights.

**Acceptance Criteria**
- Upload of mixed file types yields:
  - PII removed in text cells and redacted in images.
  - Analyzer returns valid JSON contract every time.
  - UI table displays `heading`, `description`, and ordered `key_findings`.
  - PPTX export includes all processed files with consistent formatting.
- No raw PII sent to external services; no PII in logs.
- Failures degrade gracefully with user-facing notices and actionable logs.
