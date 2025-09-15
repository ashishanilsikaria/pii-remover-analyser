# Copilot Instructions for PII Remover Analyser

## Project Overview
This is a security-focused document analysis tool built with Streamlit that processes uploaded files (images, PDFs, Excel, PowerPoint) using Google's Gemini AI to identify potential security vulnerabilities and PII risks.

## Architecture
- **Entry Point**: `streamlit_app.py` - Streamlit web interface for file uploads
- **Core Pipeline**: `pipeline.py:get_set_go()` - Main file processing router based on MIME types
- **AI Analysis**: `gemini_data_analyzer.py` - Google Gemini API integration for security analysis
- **Data Models**: `custom_types.py` - Type definitions for `ProcessedFile` and `filetypes` mapping
- **Utilities**: `helpers.py` - File extraction, logging, and HTML formatting utilities

## Key Integration Points

### File Processing Flow
1. Upload via Streamlit → `get_set_go()` → File type detection
2. Extract content (text/images/tables) using format-specific helpers
3. Send to Gemini with security analysis prompts → Structured JSON response
4. Display results in HTML table format

### Gemini AI Integration
- Uses `google-genai` client with API key from `.env` file
- **Critical**: All prompts use structured JSON output format defined in `prompt_for_output`
- Response format: `{"file_description": {"heading": "", "description": ""}, "key_findings": []}`
- Uses `gemini-2.5-flash` model with `thinking_budget=0`

### Supported File Types
Map in `custom_types.py:filetypes`:
- Images: PNG/JPEG → Direct Gemini vision analysis
- PowerPoint: PPTX → Extract text/tables/images → Combine analysis
- Excel: XLSX → DataFrame processing (partial implementation)
- PDF: Text extraction via PyPDF2 (partial implementation)

## Development Patterns

### Error Handling
- Comprehensive try-catch in `pipeline.py` with error logging
- Returns `{"error": "..."}` format for consistency
- Uses custom logger from `helpers.py:setup_logger()`

### Code Organization
- **Type safety**: Uses dataclasses and type hints throughout
- **Logging**: Centralized logger instance `my_logger` writes to `app.log`
- **Environment**: Uses `python-dotenv` for API key management
- **Testing Strategy**: No existing framework - recommended approach:
  - Unit tests: Test individual functions in `helpers.py` and `gemini_data_analyzer.py`
  - Integration tests: Mock Gemini API responses using `gemini_sample_analysis_return.json`
  - Streamlit tests: Use `test_streamlit.py` pattern for UI component testing
  - File processing tests: Test each MIME type handler in `pipeline.py` with sample files

### Streamlit Conventions
- Wide layout: `st.set_page_config(layout="wide")`
- Multi-file upload with type restrictions
- HTML rendering: Uses `unsafe_allow_html=True` for formatted tables
- Spinner feedback during processing

### JSON Processing
- **Critical Pattern**: Always use `helpers.py:strip_json_formatting()` to clean Gemini responses
- Gemini may return JSON wrapped in markdown code blocks

## External Dependencies
- `presidio-analyzer/presidio-anonymizer`: PII detection framework with NLP engine support
  - Currently unused but configured in `presidio_nlp_engine_config.py`
  - Uses spaCy NLP models with entity mapping (PERSON, ORGANIZATION, LOCATION, etc.)
  - Configured for multi-language support with confidence scoring
- `google-genai`: Primary AI analysis engine  
- `streamlit`: Web framework
- `python-pptx`: PowerPoint processing
- `PyPDF2`: PDF text extraction
- `pandas`: Data manipulation
- `PIL`: Image processing

### Presidio Integration (Available but Unused)
The project includes `presidio_nlp_engine_config.py` with a complete setup for:
- spaCy-based NLP engine with custom entity mappings
- RecognizerRegistry for predefined PII patterns
- Low confidence score handling for organizations
- Ready for integration with Gemini analysis pipeline

## Development Commands
- Run app: `streamlit run streamlit_app.py`
- Dependency management: Uses `uv` (note `uv.lock` file)
- Environment: Requires Python >=3.12

## Testing Strategy
Since no test framework currently exists, follow these patterns when adding tests:

### Recommended Test Structure
```
tests/
├── unit/
│   ├── test_helpers.py          # Test file extraction, JSON cleaning
│   ├── test_gemini_analyzer.py  # Mock Gemini API calls
│   └── test_pipeline.py         # Test file type routing
├── integration/
│   ├── test_full_pipeline.py    # End-to-end file processing
│   └── test_streamlit_ui.py     # UI component testing
└── fixtures/
    ├── sample_files/            # Test images, PDFs, PPTX
    └── mock_responses/          # Gemini API response mocks
```

### Key Test Patterns
- **Mock Gemini responses**: Use `gemini_sample_analysis_return.json` as template
- **File processing**: Test each MIME type in `custom_types.py:filetypes`
- **JSON cleaning**: Verify `strip_json_formatting()` handles markdown wrapping
- **Error handling**: Test exception flows in `pipeline.py:get_set_go()`

## Important Notes
- **Security Focus**: All prompts emphasize security analysis and PII identification
- **Incomplete Features**: PDF and Excel processing return data but don't send to Gemini yet
- **Empty Files**: `main.py`, `pii_remover.py` are placeholder/empty
- **Sample Data**: `gemini_sample_analysis_return.json` shows expected AI response format