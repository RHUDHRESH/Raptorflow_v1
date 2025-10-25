"""
OCR API Routes
Exposes document processing capabilities via REST API
"""

import logging
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import tempfile
import asyncio
from typing import Optional

from ..ocr.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

# Global document processor instance
_processor: Optional[DocumentProcessor] = None


def get_processor() -> DocumentProcessor:
    """Get or initialize document processor"""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor


@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Override language detection"),
    include_analysis: bool = Query(True, description="Include detailed analysis"),
    export_format: Optional[str] = Query(None, description="Export format: json, txt, csv"),
):
    """
    Process a document: extract text, analyze content, identify entities

    Supported formats:
    - Images: PNG, JPG, JPEG, WEBP, BMP, TIFF
    - PDF: Any PDF (single or multi-page)
    - Spreadsheets: XLSX, XLS, CSV

    Returns: Extracted text, analysis, entities, and insights
    """
    try:
        processor = get_processor()

        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Process document
            result = await processor.process_and_analyze(
                tmp_path,
                language=language,
                include_analysis=include_analysis,
                include_key_phrases=True,
            )

            # Export if requested
            if export_format:
                export_path = await processor.export_results(
                    result, format=export_format
                )
                return FileResponse(export_path, filename=f"analysis.{export_format}")

            return result

        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail="Error processing document")


@router.post("/batch-process")
async def batch_process(
    files: list[UploadFile] = File(...),
    language: Optional[str] = Query(None),
):
    """
    Process multiple documents in parallel

    Returns: Results for all documents with summary
    """
    try:
        processor = get_processor()

        # Save all files to temp
        temp_paths = []
        try:
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
                    content = await file.read()
                    tmp.write(content)
                    temp_paths.append(tmp.name)

            # Process all files
            result = await processor.batch_process(temp_paths, language=language)
            return result

        finally:
            # Clean up
            for path in temp_paths:
                Path(path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail="Error processing batch")


@router.post("/extract-text")
async def extract_text_only(
    file: UploadFile = File(...),
    language: Optional[str] = Query(None),
):
    """
    Quick text extraction without analysis
    Useful for performance-critical applications
    """
    try:
        processor = get_processor()

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # OCR only, no analysis
            ocr_result = await processor.ocr_factory.process_document(tmp_path, language)
            return {
                "filename": ocr_result.get("filename"),
                "document_type": ocr_result.get("document_type"),
                "extracted_text": ocr_result.get("extracted_text"),
                "detected_language": ocr_result.get("detected_language"),
                "processing_time_seconds": ocr_result.get("processing_time_seconds"),
            }

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise HTTPException(status_code=500, detail="Error extracting text")


@router.post("/analyze")
async def analyze_extracted(
    text: str,
    language: str = "en",
):
    """
    Analyze already-extracted text
    Useful for post-processing or analyzing text from other sources
    """
    try:
        processor = get_processor()

        # Create mock OCR result
        mock_result = {
            "extracted_text": text,
            "document_type": "text",
        }

        analysis = await processor.analysis_engine.analyze_document(mock_result, language)

        # Add key phrases
        key_phrases = processor.analysis_engine.extract_key_phrases(text)

        return {
            "analysis": analysis,
            "key_phrases": key_phrases,
        }

    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing text")


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "images": list(DocumentProcessor({}).ocr_factory.IMAGE_FORMATS),
        "pdf": list(DocumentProcessor({}).ocr_factory.PDF_FORMATS),
        "spreadsheets": list(DocumentProcessor({}).ocr_factory.SPREADSHEET_FORMATS),
        "supported_languages": list(DocumentProcessor({}).ocr_factory.LANGUAGE_MAP.keys()),
    }


@router.get("/health")
async def ocr_health():
    """Check OCR system health"""
    try:
        processor = get_processor()
        return {
            "status": "healthy",
            "ocr_factory": "initialized",
            "analysis_engine": "initialized",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
