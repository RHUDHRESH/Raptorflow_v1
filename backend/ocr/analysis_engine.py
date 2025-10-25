"""
Analysis Engine - Advanced document analysis and insights
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content classification types"""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    FORM = "form"
    LETTER = "letter"
    REPORT = "report"
    PRESENTATION = "presentation"
    TABLE_DATA = "table_data"
    UNSTRUCTURED = "unstructured"


class AnalysisEngine:
    """
    Advanced document analysis engine
    Extracts entities, classifies content, and generates insights
    """

    def __init__(self):
        """Initialize analysis engine"""
        self.patterns = self._compile_patterns()

    @staticmethod
    def _compile_patterns() -> Dict[str, Any]:
        """Compile regex patterns for entity extraction"""
        return {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+\d{1,3}\s?\d{1,14}"
            ),
            "url": re.compile(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b"),
            "ipv4": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            "currency": re.compile(r"[$€£¥₹][\s]?[\d.,]+(?:\s*(?:USD|EUR|GBP|JPY|INR))?"),
            "date": re.compile(
                r"\b(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:\d{4}|\d{2})\b"
            ),
            "percentage": re.compile(r"\d+(?:\.\d+)?%"),
            "numbers": re.compile(r"\b\d+(?:[.,]\d+)*\b"),
        }

    async def analyze_document(
        self, processed_data: Dict[str, Any], language: str = "en"
    ) -> Dict[str, Any]:
        """
        Comprehensive document analysis

        Args:
            processed_data: Output from OCRFactory.process_document()
            language: Detected/specified language code

        Returns:
            Analysis results with entities, classification, metrics
        """
        extracted_text = processed_data.get("extracted_text", "")

        if not extracted_text:
            return {"analysis": None, "error": "No text extracted"}

        logger.info("Analyzing document content")

        # Extract entities
        entities = self._extract_entities(extracted_text)

        # Classify content
        content_type = self._classify_content(extracted_text)

        # Generate metrics
        metrics = self._calculate_metrics(extracted_text)

        # Generate insights
        insights = self._generate_insights(extracted_text, entities, metrics)

        return {
            "content_type": content_type,
            "entities": entities,
            "metrics": metrics,
            "insights": insights,
            "language": language,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {}

        for entity_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Remove duplicates while preserving order
                unique_matches = list(dict.fromkeys(matches))
                entities[entity_type] = unique_matches[:20]  # Limit to 20 per type

        return entities

    @staticmethod
    def _classify_content(text: str) -> str:
        """Classify document type based on content"""
        text_lower = text.lower()

        # Pattern-based classification
        classifiers = {
            ContentType.INVOICE.value: r"invoice|bill|amount due|total amount|payment",
            ContentType.RECEIPT.value: r"receipt|paid|transaction|receipt#|thank you for your purchase",
            ContentType.CONTRACT.value: r"contract|agreement|terms and conditions|parties|whereas|hereby",
            ContentType.FORM.value: r"form|application|please fill|signature|date:",
            ContentType.LETTER.value: r"dear|sincerely|regards|enclosed|please find",
            ContentType.REPORT.value: r"report|summary|conclusion|findings|analysis|data|results",
            ContentType.PRESENTATION.value: r"slide|presentation|agenda|speaker|next",
        }

        scores = {}
        for doc_type, pattern in classifiers.items():
            matches = len(re.findall(pattern, text_lower))
            scores[doc_type] = matches

        # Return highest scoring type or default
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return ContentType.UNSTRUCTURED.value

    @staticmethod
    def _calculate_metrics(text: str) -> Dict[str, Any]:
        """Calculate text metrics"""
        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        lines = text.split("\n")

        return {
            "total_characters": len(text),
            "total_words": len(words),
            "total_sentences": len([s for s in sentences if s.strip()]),
            "total_lines": len(lines),
            "average_word_length": (
                sum(len(w) for w in words) / len(words) if words else 0
            ),
            "unique_words": len(set(w.lower() for w in words)),
            "readability_score": AnalysisEngine._calculate_readability(text),
        }

    @staticmethod
    def _calculate_readability(text: str) -> float:
        """Calculate Flesch-Kincaid readability score (0-100)"""
        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        syllables = sum(AnalysisEngine._count_syllables(word) for word in words)

        if not words or not sentences:
            return 0.0

        total_words = len(words)
        total_sentences = len([s for s in sentences if s.strip()])

        if total_sentences == 0:
            return 0.0

        # Flesch-Kincaid Reading Ease
        score = (
            206.835
            - 1.015 * (total_words / total_sentences)
            - 84.6 * (syllables / total_words)
        )

        return max(0.0, min(100.0, score))

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        syllable_count = 0
        vowels = "aeiou"
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith("e"):
            syllable_count -= 1

        # Adjust for le ending
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1

        return max(1, syllable_count)

    def _generate_insights(
        self, text: str, entities: Dict[str, List[str]], metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights from analysis"""
        insights = []

        # Text quality insight
        if metrics["readability_score"] > 60:
            insights.append(
                {
                    "type": "readability",
                    "level": "high",
                    "message": "Document is highly readable and well-structured",
                    "score": metrics["readability_score"],
                }
            )
        elif metrics["readability_score"] > 30:
            insights.append(
                {
                    "type": "readability",
                    "level": "medium",
                    "message": "Document has moderate readability",
                    "score": metrics["readability_score"],
                }
            )
        else:
            insights.append(
                {
                    "type": "readability",
                    "level": "low",
                    "message": "Document may be complex or poorly structured",
                    "score": metrics["readability_score"],
                }
            )

        # Entity-based insights
        if entities.get("email"):
            insights.append(
                {
                    "type": "entities",
                    "entity_type": "email",
                    "count": len(entities["email"]),
                    "message": f"Found {len(entities['email'])} email address(es)",
                }
            )

        if entities.get("phone"):
            insights.append(
                {
                    "type": "entities",
                    "entity_type": "phone",
                    "count": len(entities["phone"]),
                    "message": f"Found {len(entities['phone'])} phone number(s)",
                }
            )

        if entities.get("currency"):
            insights.append(
                {
                    "type": "entities",
                    "entity_type": "currency",
                    "count": len(entities["currency"]),
                    "message": f"Document contains {len(entities['currency'])} monetary value(s)",
                    "values": entities["currency"][:5],
                }
            )

        # Structure insights
        if metrics["total_lines"] > 100:
            insights.append(
                {
                    "type": "structure",
                    "level": "long",
                    "message": "Document is lengthy, consider breaking into sections",
                    "line_count": metrics["total_lines"],
                }
            )

        # Complexity insight
        avg_word_length = metrics["average_word_length"]
        if avg_word_length > 6:
            insights.append(
                {
                    "type": "complexity",
                    "level": "high",
                    "message": "Document contains complex terminology",
                    "avg_word_length": round(avg_word_length, 2),
                }
            )

        return insights

    @staticmethod
    def extract_key_phrases(text: str, top_n: int = 10) -> List[str]:
        """
        Extract key phrases from text
        Simple frequency-based approach
        """
        # Split into words and clean
        words = [
            w.lower()
            for w in re.findall(r"\b\w+\b", text)
            if len(w) > 4 and not AnalysisEngine._is_stopword(w.lower())
        ]

        # Count frequencies
        from collections import Counter

        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(top_n)]

    @staticmethod
    def _is_stopword(word: str) -> bool:
        """Check if word is a common stopword"""
        common_stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
        }
        return word in common_stopwords
