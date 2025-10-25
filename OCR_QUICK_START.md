# 🚀 RaptorFlow OCR - Quick Start Guide

Get started with the OCR system in minutes. This guide covers the most common use cases.

---

## ⚡ 5-Minute Setup

### 1. Ensure Dependencies Are Installed
```bash
cd backend
pip install -r requirements.cloud.txt
```

### 2. System Requirements
- **Linux/Mac**: `apt-get install tesseract-ocr`
- **Windows**: Download from [GitHub Tesseract Release](https://github.com/UB-Mannheim/tesseract/wiki)
- **Python**: 3.12+

---

## 🔗 API Usage Examples

### Example 1: Process a Single Document

```bash
# Upload and process a PDF
curl -X POST http://localhost:8000/api/ocr/process \
  -F "file=@invoice.pdf" \
  -F "include_analysis=true"
```

**Response includes**:
- Extracted text from all pages
- Detected language with confidence score
- Entity extraction (emails, phone numbers, currency amounts, dates)
- Document classification (invoice, receipt, contract, etc.)
- Key phrases and insights

### Example 2: Batch Process Multiple Files

```bash
# Process multiple documents in parallel
curl -X POST http://localhost:8000/api/ocr/batch-process \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.png" \
  -F "files=@doc3.xlsx"
```

**Returns**:
- Results for all 3 documents
- Batch summary (successful/failed counts)
- Processing time for each file

### Example 3: Fast Text Extraction Only

```bash
# Just extract text, skip analysis (faster)
curl -X POST http://localhost:8000/api/ocr/extract-text \
  -F "file=@scanned_page.png"
```

**Returns**:
- Extracted text
- Detected language
- File metadata

### Example 4: Analyze Pre-extracted Text

```bash
# Analyze text you already have
curl -X POST http://localhost:8000/api/ocr/analyze \
  -d "text=Your extracted text here..." \
  -H "Content-Type: application/json"
```

**Returns**:
- Entity extraction
- Content classification
- Key phrases
- Text metrics

### Example 5: Export Results

```bash
# Process and export as JSON
curl -X POST http://localhost:8000/api/ocr/process \
  -F "file=@document.pdf" \
  -F "export_format=json" \
  -o analysis.json

# Or export as CSV
curl -X POST http://localhost:8000/api/ocr/process \
  -F "file=@document.pdf" \
  -F "export_format=csv" \
  -o analysis.csv
```

---

## 🐍 Python Usage Examples

### Example 1: Basic Processing

```python
import asyncio
from backend.ocr.document_processor import DocumentProcessor

async def process_document():
    processor = DocumentProcessor()

    # Process a document
    result = await processor.process_and_analyze(
        "path/to/document.pdf",
        language=None,  # Auto-detect
        include_analysis=True,
        include_key_phrases=True
    )

    # Access results
    text = result["extraction"]["extracted_text"]
    language = result["extraction"]["detected_language"]
    entities = result["analysis"]["entities"]

    print(f"Extracted {len(text)} characters")
    print(f"Language: {language}")
    print(f"Found {len(entities.get('email', []))} email addresses")

    return result

# Run
result = asyncio.run(process_document())
```

### Example 2: Batch Processing

```python
async def batch_process_documents():
    processor = DocumentProcessor()

    files = [
        "invoice_1.pdf",
        "invoice_2.pdf",
        "receipt.png",
        "spreadsheet.xlsx"
    ]

    result = await processor.batch_process(files)

    # Summary
    successful = result["batch_info"]["successful"]
    failed = result["batch_info"]["failed"]
    print(f"Processed {successful} files, {failed} failed")

    # Access individual results
    for i, res in enumerate(result["results"]):
        if "error" not in res:
            print(f"File {i}: {res['extraction']['filename']}")
            print(f"  - Language: {res['extraction']['detected_language']}")
            print(f"  - Words: {res['analysis']['metrics']['total_words']}")

asyncio.run(batch_process_documents())
```

### Example 3: Invoice Processing Workflow

```python
async def process_invoice(invoice_path):
    processor = DocumentProcessor()

    # Process invoice
    result = await processor.process_and_analyze(invoice_path)

    # Extract key information
    entities = result["analysis"]["entities"]

    invoice_data = {
        "amount": entities.get("currency", [None])[0],
        "date": entities.get("date", [None])[0],
        "recipient_email": entities.get("email", [None])[0],
        "recipient_phone": entities.get("phone", [None])[0],
        "urls": entities.get("url", []),
    }

    # Export results
    await processor.export_results(result, format="json")

    return invoice_data

# Usage
invoice_info = asyncio.run(process_invoice("invoice.pdf"))
print(f"Invoice amount: {invoice_info['amount']}")
print(f"Invoice date: {invoice_info['date']}")
```

### Example 4: Language-Specific Processing

```python
async def process_multilingual_document():
    processor = DocumentProcessor()

    # Spanish document (auto-detected)
    result_es = await processor.process_and_analyze("documento_espanol.pdf")
    print(f"Spanish detected: {result_es['extraction']['detected_language']}")

    # Override language if auto-detection fails
    result_ja = await processor.process_and_analyze(
        "japanese_doc.pdf",
        language="ja"  # Force Japanese
    )

    return result_es, result_ja

results = asyncio.run(process_multilingual_document())
```

---

## 📊 Supported File Formats

### Images
- PNG, JPG, JPEG, WEBP, BMP, TIFF
- Recommended: 300 DPI for best accuracy

### PDFs
- Single-page and multi-page documents
- Scanned PDFs automatically optimized

### Spreadsheets
- XLSX, XLS (Excel format)
- CSV files

### Processing Tips
- **Large PDFs**: Use batch processing with smaller chunks
- **Scanned Documents**: System automatically optimizes contrast
- **Low Quality Images**: Consider resizing to 300+ DPI

---

## 🌍 Supported Languages

Auto-detected or specify with language code:

| Code | Language | Code | Language |
|------|----------|------|----------|
| en | English | ja | Japanese |
| es | Spanish | ko | Korean |
| fr | French | zh | Chinese |
| de | German | ar | Arabic |
| it | Italian | hi | Hindi |
| pt | Portuguese | bn | Bengali |
| ru | Russian | | |

**Usage**:
```python
result = await processor.process_and_analyze(
    "document.pdf",
    language="es"  # Spanish
)
```

---

## 🔍 Entity Types Extracted

The OCR system automatically extracts:

- **Email**: email@example.com
- **Phone**: +1 (555) 123-4567 (multiple formats)
- **URLs**: https://example.com
- **Currency**: $1,500.00, €500, £200, ¥10000, ₹5000
- **Dates**: 2024-01-15, 01/15/2024, 15-Jan-2024
- **Percentages**: 50%, 75.5%
- **Numbers**: Integer and decimal values
- **IPv4**: 192.168.1.1

---

## 📄 Content Classifications

Documents are automatically classified as:

- **Invoice/Bill**: Financial documents
- **Receipt**: Purchase receipts
- **Contract**: Legal agreements
- **Form**: Data collection forms
- **Letter**: Correspondence documents
- **Report**: Analytical or research documents
- **Presentation**: Slide decks
- **Table Data**: Structured tabular content
- **Unstructured Text**: General text documents

---

## 📈 Response Format

### Single Document Response
```json
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

---

## ⚙️ Configuration

### Environment Variables
```bash
# For Windows Tesseract
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# For Linux/Mac (default: /usr/bin/tesseract)
TESSERACT_PATH=/usr/bin/tesseract
```

### Performance Tuning
```python
# For large batches, process in chunks
from backend.ocr.document_processor import DocumentProcessor

processor = DocumentProcessor()
large_file_list = [...]  # 100+ files

# Process in batches of 10
import asyncio
chunk_size = 10
for i in range(0, len(large_file_list), chunk_size):
    chunk = large_file_list[i:i+chunk_size]
    result = await processor.batch_process(chunk)
    print(f"Processed chunk {i//chunk_size + 1}")
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Tesseract not found** | Install system package: `apt-get install tesseract-ocr` |
| **Language not detected** | Ensure document is clear, or use `language` parameter |
| **PDF extraction fails** | Check if PDF is scanned (image-based) vs text-based |
| **Memory error with large files** | Process files in batches, or split large documents |
| **Slow processing** | Use `/api/ocr/extract-text` if full analysis not needed |
| **Low accuracy** | Ensure 300+ DPI, check image contrast/quality |

---

## 📚 Full Documentation

For complete documentation, see:
- `backend/ocr/OCR_README.md` - Comprehensive guide
- `OCR_FEATURE_SUMMARY.md` - Feature overview
- `PROJECT_COMPLETION_REPORT.md` - Architecture & stats

---

## 🚀 Next Steps

1. **Test Endpoints**: Try the examples above with your documents
2. **Integrate with Frontend**: Add OCR upload UI to your application
3. **Process Production Documents**: Start with real documents
4. **Optimize for Use Case**: Tune language detection and export formats

---

**Ready to process any document in any language!** 🎉

Start with: `curl http://localhost:8000/api/ocr/health` to verify the system is running.
