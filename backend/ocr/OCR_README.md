# 🔍 RaptorFlow OCR Factory - World-Class Document Processing

Complete, production-ready OCR system with advanced document analysis and multi-language support.

## 🌟 Features

### Supported Document Formats
- **Images**: PNG, JPG, JPEG, WEBP, BMP, TIFF
- **PDFs**: Single and multi-page documents
- **Spreadsheets**: XLSX, XLS, CSV
- **Scanned Documents**: Automatic image optimization for OCR

### Advanced Capabilities
- ✅ **Multilingual Support**: 14+ languages with automatic detection
- ✅ **Entity Extraction**: Email, phone, URLs, currency, dates, percentages
- ✅ **Content Classification**: Invoice, receipt, contract, form, letter, report, presentation
- ✅ **Text Analysis**: Readability scoring, sentiment indicators, key phrase extraction
- ✅ **Confidence Scoring**: Quality metrics for all extraction operations
- ✅ **Batch Processing**: Process multiple documents in parallel
- ✅ **Image Optimization**: CLAHE contrast enhancement, noise reduction, preprocessing
- ✅ **Export Formats**: JSON, TXT, CSV results

### Supported Languages
English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese (Simplified & Traditional), Arabic, Hindi, Bengali, and more.

## 📦 Installation

### System Dependencies (Ubuntu/Debian)
```bash
apt-get install tesseract-ocr
apt-get install libsm6 libxext6 libxrender-dev  # For OpenCV
```

### Python Dependencies
All dependencies are in `requirements.cloud.txt`:
```bash
pip install -r requirements.cloud.txt
```

Key packages:
- `pytesseract`: OCR engine interface
- `pdf2image`: PDF conversion
- `Pillow`: Image processing
- `opencv-python`: Advanced image preprocessing
- `pandas`: Data handling
- `langdetect`: Language detection

## 🚀 Quick Start

### Basic Document Processing
```python
from backend.ocr.document_processor import DocumentProcessor
import asyncio

async def process_doc():
    processor = DocumentProcessor()
    result = await processor.process_and_analyze(
        "path/to/document.pdf",
        language=None,  # Auto-detect
        include_analysis=True,
        include_key_phrases=True
    )
    print(result)

asyncio.run(process_doc())
```

### Batch Processing
```python
async def batch_process():
    processor = DocumentProcessor()
    result = await processor.batch_process([
        "doc1.pdf",
        "doc2.png",
        "spreadsheet.xlsx"
    ])
    return result
```

## 📡 API Endpoints

### 1. Process Single Document
```
POST /api/ocr/process
Content-Type: multipart/form-data

Parameters:
- file: Document file
- language: (optional) Override language detection (e.g., 'en', 'es', 'ja')
- include_analysis: (optional) Enable/disable analysis (default: true)
- export_format: (optional) Export format ('json', 'txt', 'csv')

Response:
{
  "file_info": {
    "filename": "document.pdf",
    "document_type": "pdf",
    "file_size_mb": 2.5,
    "processing_time_seconds": 12.4
  },
  "extraction": {
    "total_pages": 5,
    "extracted_text": "...",
    "detected_language": "en",
    "language_confidence": 0.98
  },
  "analysis": {
    "content_type": "invoice",
    "entities": {
      "email": ["sales@company.com"],
      "currency": ["$1,500.00"],
      "date": ["2024-01-15"]
    },
    "metrics": {
      "total_words": 450,
      "readability_score": 65.2
    },
    "insights": [...]
  },
  "key_phrases": ["invoice number", "payment terms", "total amount"]
}
```

### 2. Batch Process Multiple Documents
```
POST /api/ocr/batch-process
Content-Type: multipart/form-data

Parameters:
- files: Array of document files
- language: (optional) Language override

Response:
{
  "batch_info": {
    "total_files": 3,
    "successful": 3,
    "failed": 0
  },
  "results": [
    { /* Process result 1 */ },
    { /* Process result 2 */ },
    { /* Process result 3 */ }
  ]
}
```

### 3. Extract Text Only (Fast)
```
POST /api/ocr/extract-text

Response:
{
  "filename": "document.png",
  "document_type": "image",
  "extracted_text": "...",
  "detected_language": "en"
}
```

### 4. Analyze Pre-extracted Text
```
POST /api/ocr/analyze

Parameters:
- text: Text content
- language: Language code (default: 'en')

Response:
{
  "analysis": {
    "content_type": "report",
    "entities": {...},
    "metrics": {...},
    "insights": [...]
  },
  "key_phrases": [...]
}
```

### 5. Get Supported Formats
```
GET /api/ocr/supported-formats

Response:
{
  "images": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"],
  "pdf": [".pdf"],
  "spreadsheets": [".xlsx", ".xls", ".csv"],
  "supported_languages": ["en", "es", "fr", "de", ...]
}
```

### 6. Health Check
```
GET /api/ocr/health

Response:
{
  "status": "healthy",
  "ocr_factory": "initialized",
  "analysis_engine": "initialized"
}
```

## 🏗️ Architecture

### Module Structure
```
backend/ocr/
├── __init__.py                 # Module exports
├── ocr_factory.py              # Main OCR processing (PDF, images, spreadsheets)
├── document_processor.py        # High-level orchestrator
├── analysis_engine.py           # Content analysis and insights
└── OCR_README.md               # This file
```

### Data Flow
```
Document Input
    ↓
[OCR Factory]
├── Document Type Detection
├── Format-specific Processing
│   ├── PDF → convert_from_path → OCR each page
│   ├── Image → preprocess → OCR
│   ├── Excel → pandas read → extract
│   └── CSV → pandas read → extract
├── Language Detection
└── Text Extraction
    ↓
[Analysis Engine]
├── Entity Extraction (email, phone, URL, etc.)
├── Content Classification
├── Text Metrics (readability, word count, etc.)
├── Key Phrase Extraction
└── Insight Generation
    ↓
Results + Metadata
```

## 🎯 Use Cases

### 1. Invoice Processing
```python
# Automatically extract invoice details
result = await processor.process_and_analyze("invoice.pdf")
entities = result["analysis"]["entities"]
amounts = entities["currency"]  # Extract all monetary values
dates = entities["date"]        # Extract dates
emails = entities["email"]      # Extract contact info
```

### 2. Document Classification
```python
# Classify document type automatically
doc_type = result["analysis"]["content_type"]
if doc_type == "invoice":
    # Handle invoice processing
elif doc_type == "contract":
    # Handle contract processing
```

### 3. Research Document Analysis
```python
# Analyze research papers and reports
key_phrases = result["key_phrases"]      # Main topics
readability = result["analysis"]["metrics"]["readability_score"]
metrics = result["analysis"]["metrics"]  # Word count, complexity, etc.
```

### 4. Multilingual Support
```python
# Process documents in any language
result = await processor.process_and_analyze(
    "document_in_spanish.pdf"
    # Language auto-detected as Spanish
)
lang = result["extraction"]["detected_language"]  # "es"
```

## 📊 Output Structure

### Extraction Result
```python
{
    "filename": str,
    "document_type": str,  # "pdf", "image", "excel", "csv"
    "extracted_text": str,
    "detected_language": str,
    "language_confidence": float,  # 0.0-1.0
    "processing_timestamp": str,
    "file_size_mb": float,

    # For PDFs:
    "total_pages": int,
    "pages": [...]  # Per-page data

    # For Images:
    "confidence": float,
    "image_dimensions": tuple,

    # For Spreadsheets:
    "total_sheets": int,
    "sheets": {
        "Sheet1": {
            "shape": tuple,
            "columns": list,
            "data": list[dict]
        }
    }
}
```

### Analysis Result
```python
{
    "content_type": str,  # invoice, receipt, contract, etc.
    "entities": {
        "email": list,
        "phone": list,
        "url": list,
        "currency": list,
        "date": list,
        "percentage": list,
        "numbers": list
    },
    "metrics": {
        "total_characters": int,
        "total_words": int,
        "total_sentences": int,
        "average_word_length": float,
        "unique_words": int,
        "readability_score": float  # 0-100
    },
    "insights": [
        {
            "type": str,  # "readability", "entities", "structure", etc.
            "level": str,  # "high", "medium", "low"
            "message": str,
            "count": int  # For entity insights
        }
    ]
}
```

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# For Windows Tesseract installation
TESSERACT_PATH=/usr/bin/tesseract  # Linux/Mac
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows
```

### Performance Tuning
```python
# For large batches, adjust concurrency
processor = DocumentProcessor()
# Process in chunks to avoid memory issues
for chunk in chunks(large_file_list, 10):
    result = await processor.batch_process(chunk)
```

## 📈 Metrics & Performance

### Typical Processing Times
- Single-page image: 2-5 seconds
- Multi-page PDF (10 pages): 10-20 seconds
- Excel file (1000 rows): 1-3 seconds
- Large CSV file: <1 second

### Accuracy Factors
- Image quality (DPI, resolution)
- Language complexity
- Document type
- Preprocessing effectiveness

## 🛡️ Error Handling

```python
try:
    result = await processor.process_and_analyze("doc.pdf")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Unsupported document type: {e}")
except Exception as e:
    print(f"Processing error: {e}")
```

## 🔐 Security Considerations

- **File Size Limits**: Implement max file size check
- **Timeout**: Set processing timeouts for long documents
- **Resource Limits**: Monitor CPU/memory usage for batch operations
- **Input Validation**: Verify file types before processing
- **Temporary Files**: Automatically cleaned up after processing

## 📚 Examples

### Example 1: Invoice Processing Workflow
```python
async def process_invoice(invoice_path):
    processor = DocumentProcessor()

    # Process invoice
    result = await processor.process_and_analyze(invoice_path)

    # Extract key information
    entities = result["analysis"]["entities"]

    invoice_data = {
        "amount": entities.get("currency", ["Unknown"])[0],
        "date": entities.get("date", ["Unknown"])[0],
        "recipient": entities.get("email", ["Unknown"])[0],
    }

    # Export as JSON
    await processor.export_results(result, format="json")

    return invoice_data
```

### Example 2: Batch PDF Processing
```python
async def process_pdf_batch(pdf_folder):
    processor = DocumentProcessor()
    from pathlib import Path

    # Get all PDFs
    pdfs = list(Path(pdf_folder).glob("*.pdf"))

    # Process in parallel
    result = await processor.batch_process(pdfs)

    print(f"Processed: {result['batch_info']['successful']} files")
    print(f"Failed: {result['batch_info']['failed']} files")

    # Export all results
    for res in result["results"]:
        if "error" not in res:
            await processor.export_results(res, format="csv")
```

## 🤝 Contributing

To add new document types or languages:

1. Update `DocumentType` enum in `ocr_factory.py`
2. Add processor method for new type
3. Update `LANGUAGE_MAP` for new languages
4. Add tests and examples

## 📞 Support

For issues or questions:
1. Check error messages and logs
2. Verify Tesseract installation (for OCR)
3. Check file format and size
4. Review language support
5. Check system resources (CPU, RAM, disk space)

## 📝 License

RaptorFlow © 2024. All rights reserved.
