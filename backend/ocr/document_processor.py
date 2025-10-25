"""
Document Processor - High-level document processing orchestrator
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import asyncio
from datetime import datetime
import json

from .ocr_factory import OCRFactory
from .analysis_engine import AnalysisEngine

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    High-level document processor
    Combines OCR and analysis for complete document processing
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize Document Processor

        Args:
            tesseract_path: Path to Tesseract-OCR binary
        """
        self.ocr_factory = OCRFactory(tesseract_path)
        self.analysis_engine = AnalysisEngine()

    async def process_and_analyze(
        self,
        file_path: Union[str, Path],
        language: Optional[str] = None,
        include_analysis: bool = True,
        include_key_phrases: bool = True,
    ) -> Dict[str, Any]:
        """
        Complete document processing pipeline:
        1. Extract text/data from document
        2. Analyze content
        3. Extract entities and generate insights

        Args:
            file_path: Path to document
            language: Override language detection
            include_analysis: Whether to perform detailed analysis
            include_key_phrases: Whether to extract key phrases

        Returns:
            Complete processing result with all stages
        """
        file_path = Path(file_path)

        logger.info(f"Starting complete processing: {file_path.name}")

        try:
            # Stage 1: OCR/Data extraction
            processing_start = datetime.utcnow()
            ocr_result = await self.ocr_factory.process_document(file_path, language)
            processing_time = (datetime.utcnow() - processing_start).total_seconds()

            result = {
                "file_info": {
                    "filename": ocr_result.get("filename"),
                    "document_type": ocr_result.get("document_type"),
                    "file_size_mb": ocr_result.get("file_size_mb"),
                    "processing_time_seconds": round(processing_time, 2),
                },
                "extraction": ocr_result,
            }

            # Stage 2: Content Analysis
            if include_analysis:
                analysis_start = datetime.utcnow()
                analysis_result = await self.analysis_engine.analyze_document(
                    ocr_result, language or ocr_result.get("detected_language", "en")
                )
                analysis_time = (datetime.utcnow() - analysis_start).total_seconds()

                result["analysis"] = analysis_result
                result["analysis"]["analysis_time_seconds"] = round(analysis_time, 2)

            # Stage 3: Key Phrases
            if include_key_phrases:
                extracted_text = ocr_result.get("extracted_text", "")
                if extracted_text:
                    key_phrases = AnalysisEngine.extract_key_phrases(extracted_text)
                    result["key_phrases"] = key_phrases

            # Add processing summary
            result["processing_summary"] = {
                "total_steps": 3 if include_analysis and include_key_phrases else 2,
                "successful_stages": self._count_successful_stages(result),
                "overall_status": "success",
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Document processing completed successfully: {file_path.name}"
            )
            return result

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                "file_info": {"filename": str(file_path.name)},
                "error": str(e),
                "processing_summary": {
                    "overall_status": "failed",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

    async def batch_process(
        self,
        file_paths: list[Union[str, Path]],
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process multiple documents in parallel

        Args:
            file_paths: List of document paths
            language: Override language detection

        Returns:
            Batch processing results
        """
        logger.info(f"Starting batch processing of {len(file_paths)} documents")

        # Process all files concurrently
        tasks = [
            self.process_and_analyze(fp, language)
            for fp in file_paths
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successful and failed
        successful = [r for r in results if isinstance(r, dict) and "error" not in r]
        failed = [r for r in results if isinstance(r, dict) and "error" in r]

        return {
            "batch_info": {
                "total_files": len(file_paths),
                "successful": len(successful),
                "failed": len(failed),
            },
            "results": results,
            "summary": {
                "successful_files": [r.get("file_info", {}).get("filename") for r in successful],
                "failed_files": [r.get("file_info", {}).get("filename") for r in failed],
            },
        }

    @staticmethod
    def _count_successful_stages(result: Dict[str, Any]) -> int:
        """Count number of successfully completed processing stages"""
        count = 0
        if result.get("extraction"):
            count += 1
        if result.get("analysis"):
            count += 1
        if result.get("key_phrases"):
            count += 1
        return count

    async def export_results(
        self,
        processing_result: Dict[str, Any],
        format: str = "json",
        output_path: Optional[Union[str, Path]] = None,
    ) -> Union[str, Path]:
        """
        Export processing results in various formats

        Args:
            processing_result: Result from process_and_analyze
            format: Export format ('json', 'txt', 'csv')
            output_path: Where to save results

        Returns:
            Path to exported file
        """
        filename = processing_result.get("file_info", {}).get("filename", "document")
        base_name = Path(filename).stem

        if output_path is None:
            output_path = Path(f"{base_name}_analysis.{format}")
        else:
            output_path = Path(output_path)

        try:
            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(processing_result, f, indent=2, ensure_ascii=False)

            elif format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(self._format_as_text(processing_result))

            elif format == "csv":
                self._format_as_csv(processing_result, output_path)

            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Results exported to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    @staticmethod
    def _format_as_text(result: Dict[str, Any]) -> str:
        """Format results as plain text"""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("DOCUMENT PROCESSING REPORT")
        lines.append("=" * 80)

        # File Info
        file_info = result.get("file_info", {})
        lines.append(f"\nFile: {file_info.get('filename')}")
        lines.append(f"Type: {file_info.get('document_type')}")
        lines.append(f"Size: {file_info.get('file_size_mb', 'N/A')} MB")
        lines.append(f"Processing Time: {file_info.get('processing_time_seconds', 'N/A')}s")

        # Extracted Text
        extraction = result.get("extraction", {})
        lines.append("\n" + "-" * 80)
        lines.append("EXTRACTED CONTENT")
        lines.append("-" * 80)
        lines.append(extraction.get("extracted_text", "No text extracted")[:2000])

        # Analysis
        analysis = result.get("analysis", {})
        if analysis:
            lines.append("\n" + "-" * 80)
            lines.append("CONTENT ANALYSIS")
            lines.append("-" * 80)
            lines.append(f"Content Type: {analysis.get('content_type')}")
            lines.append(f"Detected Language: {analysis.get('language')}")

            metrics = analysis.get("metrics", {})
            lines.append("\nMetrics:")
            lines.append(f"  - Total Words: {metrics.get('total_words')}")
            lines.append(f"  - Total Sentences: {metrics.get('total_sentences')}")
            lines.append(f"  - Readability Score: {metrics.get('readability_score', 'N/A')}")

            entities = analysis.get("entities", {})
            if entities:
                lines.append("\nEntities Found:")
                for entity_type, values in entities.items():
                    lines.append(f"  - {entity_type}: {len(values)} found")

        # Key Phrases
        key_phrases = result.get("key_phrases", [])
        if key_phrases:
            lines.append("\n" + "-" * 80)
            lines.append("KEY PHRASES")
            lines.append("-" * 80)
            for i, phrase in enumerate(key_phrases, 1):
                lines.append(f"{i}. {phrase}")

        return "\n".join(lines)

    @staticmethod
    def _format_as_csv(result: Dict[str, Any], output_path: Path) -> None:
        """Format results as CSV"""
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Headers
            writer.writerow(["Field", "Value"])

            # File Info
            file_info = result.get("file_info", {})
            for key, value in file_info.items():
                writer.writerow([key, value])

            # Analysis Summary
            analysis = result.get("analysis", {})
            if analysis:
                metrics = analysis.get("metrics", {})
                for key, value in metrics.items():
                    writer.writerow([f"metric_{key}", value])
