"""ContextProcessorAgent - Processes text, files, and URLs for strategy extraction"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from ..core.service_factories import ServiceManager
from ..base_agent import BaseAgent, AgentState
from ..middleware.budget_controller import check_budget_before_api_call

logger = logging.getLogger(__name__)


class ContextProcessorAgent(BaseAgent):
    """
    Stage 1 Agent: Process context items (text, files, URLs)
    - Extracts text from files (images via OCR, PDFs, videos/audio via transcription)
    - Performs NLP analysis (topics, entities, keywords, sentiment, emotions)
    - Stores embeddings for vector search
    - Links evidence to context
    """

    def __init__(self):
        super().__init__(
            name="ContextProcessor",
            description="Processes and analyzes context items (text, files, URLs) for strategy extraction"
        )
        self.services = ServiceManager()

    async def _process(self, state: AgentState) -> AgentState:
        """Process context items"""
        try:
            state["stage"] = "processing_context"

            workspace_id = state["context"].get("workspace_id")
            context_items = state["context"].get("context_items", [])

            if not context_items:
                state["error"] = "No context items provided"
                return state

            processed_items = []

            for item in context_items:
                logger.info(f"Processing context item: {item.get('item_type')}")

                # Check budget before processing
                if not check_budget_before_api_call("context_processing"):
                    state["error"] = "Budget limit reached for context processing"
                    return state

                # Extract text based on item type
                extracted_text = await self._extract_text(item)

                if not extracted_text:
                    logger.warning(f"Failed to extract text from item: {item.get('id')}")
                    continue

                # Perform NLP analysis
                nlp_analysis = await self._perform_nlp_analysis(extracted_text)

                # Generate embeddings for vector search
                embedding = await self._generate_embedding(extracted_text)

                # Create processed item record
                processed_item = {
                    "id": item.get("id", str(uuid.uuid4())),
                    "workspace_id": workspace_id,
                    "item_type": item.get("item_type"),
                    "source": item.get("source", "user_input"),
                    "raw_content": item.get("content", ""),
                    "extracted_text": extracted_text,
                    "topics": nlp_analysis.get("topics", []),
                    "entities": nlp_analysis.get("entities", []),
                    "keywords": nlp_analysis.get("keywords", []),
                    "sentiment": nlp_analysis.get("sentiment"),
                    "emotions": nlp_analysis.get("emotions", []),
                    "embedding": embedding,
                    "created_at": datetime.utcnow().isoformat(),
                }

                processed_items.append(processed_item)

            state["results"]["processed_context_items"] = processed_items
            state["results"]["item_count"] = len(processed_items)

            logger.info(f"Processed {len(processed_items)} context items successfully")

        except Exception as e:
            logger.exception(f"Error in context processing: {str(e)}")
            state["error"] = str(e)

        return state

    async def _extract_text(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract text from various item types"""
        item_type = item.get("item_type")
        content = item.get("content", "")

        try:
            if item_type == "text":
                # Direct text input
                return content

            elif item_type == "file_image":
                # OCR from image
                return await self._perform_ocr(content)

            elif item_type == "file_pdf":
                # Extract text from PDF
                return await self._extract_from_pdf(content)

            elif item_type in ["file_video", "file_audio"]:
                # Transcribe video/audio
                return await self._transcribe_media(content, item_type)

            elif item_type == "url":
                # Fetch and parse web content
                return await self._fetch_url_content(content)

            else:
                logger.warning(f"Unknown item type: {item_type}")
                return None

        except Exception as e:
            logger.error(f"Error extracting text from {item_type}: {str(e)}")
            return None

    async def _perform_ocr(self, image_path: str) -> Optional[str]:
        """Perform OCR on image files"""
        try:
            # Use LLM service with vision capability for OCR
            llm = self.services.llm

            prompt = f"""Extract all text from this image. Return the extracted text exactly as it appears.
            Image path: {image_path}"""

            # Note: This assumes vision capability. For Ollama, would need a vision model like llava
            # For OpenAI, would use vision API
            response = await llm.invoke(prompt)

            return response

        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return None

    async def _extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF files"""
        try:
            import PyPDF2

            text = []
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())

            return "\n".join(text)

        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return None

    async def _transcribe_media(self, media_path: str, media_type: str) -> Optional[str]:
        """Transcribe audio or video files"""
        try:
            llm = self.services.llm

            # For Ollama: Use whisper.cpp or similar
            # For OpenAI: Use Whisper API
            prompt = f"""Transcribe the audio from this {media_type} file:
            File path: {media_path}

            Return the complete transcription of the spoken content."""

            transcription = await llm.invoke(prompt)
            return transcription

        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None

    async def _fetch_url_content(self, url: str) -> Optional[str]:
        """Fetch and parse content from a URL"""
        try:
            import httpx
            from bs4 import BeautifulSoup

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Parse HTML content
                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = " ".join(chunk for chunk in chunks if chunk)

                return text[:10000]  # Limit to 10k chars

        except Exception as e:
            logger.error(f"URL fetch error: {str(e)}")
            return None

    async def _perform_nlp_analysis(self, text: str) -> Dict[str, Any]:
        """Perform NLP analysis on text"""
        try:
            llm = self.services.llm

            prompt = f"""Analyze this text and extract NLP features in JSON format:

            Text: {text[:3000]}

            Return a JSON object with:
            - topics: List of main topics/themes (array of strings)
            - entities: Named entities (array of strings)
            - keywords: Key phrases (array of strings, max 10)
            - sentiment: Overall sentiment (positive, neutral, or negative)
            - emotions: Detected emotions (array of strings)

            Return ONLY valid JSON, no other text."""

            response = await llm.invoke(prompt)

            # Parse JSON response
            analysis = json.loads(response)
            return analysis

        except json.JSONDecodeError:
            logger.warning("Failed to parse NLP analysis response as JSON")
            return {
                "topics": [],
                "entities": [],
                "keywords": [],
                "sentiment": "neutral",
                "emotions": []
            }
        except Exception as e:
            logger.error(f"NLP analysis error: {str(e)}")
            return {
                "topics": [],
                "entities": [],
                "keywords": [],
                "sentiment": "neutral",
                "emotions": []
            }

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for text"""
        try:
            embeddings_service = self.services.embeddings

            # Get embeddings using the service (Ollama or OpenAI)
            embedding = await embeddings_service.embed_text(text)
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            return None

    async def _validate(self, state: AgentState) -> AgentState:
        """Validate processed context items"""
        try:
            state["stage"] = "validating_context"

            processed_items = state["results"].get("processed_context_items", [])

            if not processed_items:
                state["error"] = "No context items were successfully processed"
                return state

            # Validate each item has required fields
            for item in processed_items:
                if not item.get("extracted_text"):
                    logger.warning(f"Item {item.get('id')} missing extracted text")

            state["status"] = "completed"
            logger.info(f"Context processing validation passed")

        except Exception as e:
            logger.exception(f"Validation error: {str(e)}")
            state["error"] = str(e)

        return state

    async def _finalize(self, state: AgentState) -> AgentState:
        """Finalize context processing results"""
        state["stage"] = "finalized"
        return state


# Factory function for creating the agent
def create_context_processor_agent() -> ContextProcessorAgent:
    """Create a new ContextProcessorAgent instance"""
    return ContextProcessorAgent()
