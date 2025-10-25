"""
OCR Factory - Main orchestrator for document processing
Handles multiple file formats and languages
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import asyncio
from datetime import datetime

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import pandas as pd
import cv2
import numpy as np
from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Supported document types"""
    PDF = "pdf"
    IMAGE_PNG = "png"
    IMAGE_JPG = "jpg"
    IMAGE_JPEG = "jpeg"
    IMAGE_WEBP = "webp"
    IMAGE_BMP = "bmp"
    IMAGE_TIFF = "tiff"
    EXCEL_XLS = "xls"
    EXCEL_XLSX = "xlsx"
    CSV = "csv"
    UNKNOWN = "unknown"


class OCRFactory:
    """
    World-class OCR processing factory
    Handles documents in any format with multilingual support
    """

    # Supported formats by category
    IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}
    PDF_FORMATS = {".pdf"}
    SPREADSHEET_FORMATS = {".xlsx", ".xls", ".csv"}
    SUPPORTED_FORMATS = IMAGE_FORMATS | PDF_FORMATS | SPREADSHEET_FORMATS

    # Language codes for Tesseract
    LANGUAGE_MAP = {
        "en": "eng",
        "es": "spa",
        "fr": "fra",
        "de": "deu",
        "it": "ita",
        "pt": "por",
        "ru": "rus",
        "ja": "jpn",
        "ko": "kor",
        "zh": "chi_sim",  # Simplified Chinese
        "zh_tra": "chi_tra",  # Traditional Chinese
        "ar": "ara",
        "hi": "hin",
        "bn": "ben",
    }

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR Factory

        Args:
            tesseract_path: Path to Tesseract-OCR binary (optional on Linux/Mac)
        """
        if tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path

        logger.info("OCR Factory initialized")

    @staticmethod
    def get_document_type(file_path: Union[str, Path]) -> DocumentType:
        """Detect document type from file extension"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        # Map extensions to DocumentType
        type_map = {
            ".pdf": DocumentType.PDF,
            ".png": DocumentType.IMAGE_PNG,
            ".jpg": DocumentType.IMAGE_JPG,
            ".jpeg": DocumentType.IMAGE_JPEG,
            ".webp": DocumentType.IMAGE_WEBP,
            ".bmp": DocumentType.IMAGE_BMP,
            ".tiff": DocumentType.IMAGE_TIFF,
            ".xlsx": DocumentType.EXCEL_XLSX,
            ".xls": DocumentType.EXCEL_XLS,
            ".csv": DocumentType.CSV,
        }

        return type_map.get(extension, DocumentType.UNKNOWN)

    async def process_document(
        self, file_path: Union[str, Path], language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main document processing pipeline

        Args:
            file_path: Path to document
            language: Override language detection (e.g., 'en', 'es', 'ja')

        Returns:
            Dict with extracted text, metadata, and analysis
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        doc_type = self.get_document_type(file_path)

        logger.info(f"Processing document: {file_path.name} (Type: {doc_type.value})")

        # Route to appropriate processor
        if doc_type == DocumentType.PDF:
            return await self._process_pdf(file_path, language)
        elif doc_type in {
            DocumentType.IMAGE_PNG,
            DocumentType.IMAGE_JPG,
            DocumentType.IMAGE_JPEG,
            DocumentType.IMAGE_WEBP,
            DocumentType.IMAGE_BMP,
            DocumentType.IMAGE_TIFF,
        }:
            return await self._process_image(file_path, language)
        elif doc_type in {DocumentType.EXCEL_XLSX, DocumentType.EXCEL_XLS}:
            return await self._process_excel(file_path)
        elif doc_type == DocumentType.CSV:
            return await self._process_csv(file_path)
        else:
            raise ValueError(f"Unsupported document type: {doc_type.value}")

    async def _process_pdf(
        self, file_path: Path, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process PDF documents"""
        logger.info(f"Processing PDF: {file_path.name}")

        try:
            # Convert PDF to images
            images = convert_from_path(str(file_path), dpi=300)
            logger.info(f"Converted PDF to {len(images)} pages")

            all_text = []
            all_data = []

            for idx, image in enumerate(images, 1):
                # Process each page
                page_data = await self._process_image_data(image, language)
                all_text.append(f"--- Page {idx} ---\n{page_data['text']}")
                all_data.append(page_data)

            extracted_text = "\n\n".join(all_text)
            detected_language = self._detect_language(extracted_text)

            return {
                "filename": file_path.name,
                "document_type": "pdf",
                "total_pages": len(images),
                "extracted_text": extracted_text,
                "pages": all_data,
                "detected_language": detected_language,
                "language_confidence": self._calculate_confidence(extracted_text),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    async def _process_image(
        self, file_path: Path, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process image documents"""
        logger.info(f"Processing image: {file_path.name}")

        try:
            # Load image
            image = Image.open(file_path)

            # Optimize image for OCR
            image = self._preprocess_image(image)

            # Extract text
            page_data = await self._process_image_data(image, language)

            detected_language = self._detect_language(page_data["text"])

            return {
                "filename": file_path.name,
                "document_type": "image",
                "extracted_text": page_data["text"],
                "confidence": page_data.get("confidence", 0),
                "detected_language": detected_language,
                "language_confidence": self._calculate_confidence(page_data["text"]),
                "image_dimensions": image.size,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise

    async def _process_image_data(
        self, image: Image.Image, language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract text from PIL Image"""
        # Determine Tesseract language
        if not language:
            language = await asyncio.to_thread(self._detect_image_language, image)

        tesseract_lang = self.LANGUAGE_MAP.get(language, "eng")

        # Extract text with Tesseract
        extracted_text = await asyncio.to_thread(
            pytesseract.image_to_string,
            image,
            lang=tesseract_lang,
            config="--psm 3",  # PSM 3: Fully automatic page segmentation with OSD
        )

        # Get detailed data (confidence scores, etc.)
        data = await asyncio.to_thread(
            pytesseract.image_to_data, image, lang=tesseract_lang, output_type=pytesseract.Output.DICT
        )

        confidence_scores = [int(conf) for conf in data.get("confidence", []) if int(conf) > 0]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        )

        return {
            "text": extracted_text.strip(),
            "confidence": avg_confidence,
            "words_detected": len([w for w in data.get("text", []) if w.strip()]),
        }

    async def _process_excel(self, file_path: Path) -> Dict[str, Any]:
        """Process Excel spreadsheets"""
        logger.info(f"Processing Excel: {file_path.name}")

        try:
            xls = pd.ExcelFile(file_path)
            sheets_data = {}

            for sheet_name in xls.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets_data[sheet_name] = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "data": df.to_dict(orient="records"),
                }

            return {
                "filename": file_path.name,
                "document_type": "excel",
                "total_sheets": len(xls.sheet_names),
                "sheets": sheets_data,
                "extracted_text": self._extract_text_from_dataframes(sheets_data),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Error processing Excel: {e}")
            raise

    async def _process_csv(self, file_path: Path) -> Dict[str, Any]:
        """Process CSV files"""
        logger.info(f"Processing CSV: {file_path.name}")

        try:
            df = pd.read_csv(file_path)

            return {
                "filename": file_path.name,
                "document_type": "csv",
                "shape": df.shape,
                "columns": list(df.columns),
                "data": df.to_dict(orient="records"),
                "extracted_text": df.to_string(),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            raise

    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        - Convert to RGB if needed
        - Enhance contrast
        - Denoise
        """
        # Convert RGBA to RGB
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        cv_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Denoise
        cv_image = cv2.fastNlMeansDenoisingColored(cv_image, None, h=10, hForColorComponents=10)

        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

    @staticmethod
    def _detect_language(text: str) -> str:
        """Detect language from text"""
        if not text or len(text.strip()) < 10:
            return "unknown"

        try:
            # Get top language
            detected = detect(text)
            return detected
        except LangDetectException:
            return "unknown"

    @staticmethod
    def _detect_image_language(image: Image.Image) -> str:
        """Detect language from image using OCR sample"""
        try:
            # Extract small sample to determine language
            sample_text = pytesseract.image_to_string(image)[:500]
            if sample_text:
                return OCRFactory._detect_language(sample_text)
            return "en"
        except Exception:
            return "en"

    @staticmethod
    def _calculate_confidence(text: str) -> float:
        """Calculate confidence score for detected language"""
        if not text or len(text.strip()) < 10:
            return 0.0

        try:
            scores = detect_langs(text)
            if scores:
                return scores[0].prob
            return 0.0
        except LangDetectException:
            return 0.0

    @staticmethod
    def _extract_text_from_dataframes(sheets_data: Dict[str, Any]) -> str:
        """Extract concatenated text from all sheets"""
        all_text = []
        for sheet_name, sheet_info in sheets_data.items():
            all_text.append(f"=== Sheet: {sheet_name} ===")
            all_text.append(f"Columns: {', '.join(sheet_info['columns'])}")

            for record in sheet_info["data"][:50]:  # Limit to first 50 rows
                all_text.append(str(record))

        return "\n".join(all_text)
