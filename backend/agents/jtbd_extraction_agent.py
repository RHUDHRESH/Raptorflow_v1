"""JTBDExtractionAgent - Extracts Jobs-to-be-Done from processed context"""
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from sklearn.cluster import DBSCAN
import numpy as np
from ..core.service_factories import ServiceManager
from ..base_agent import BaseAgent, AgentState
from ..middleware.budget_controller import check_budget_before_api_call

logger = logging.getLogger(__name__)


class JTBDExtractionAgent(BaseAgent):
    """
    Stage 2 Agent: Extract Jobs-to-be-Done from processed context
    - Clusters similar context items by topic/intent
    - Generates JTBD statements with Why, Circumstances, Forces, Anxieties
    - Links evidence (citations) back to source context
    - Returns jobs ready for user review
    """

    def __init__(self):
        super().__init__(
            name="JTBDExtractor",
            description="Extracts Jobs-to-be-Done from context items with evidence citations"
        )
        self.services = ServiceManager()

    async def _process(self, state: AgentState) -> AgentState:
        """Extract JTBD from processed context"""
        try:
            state["stage"] = "extracting_jtbds"

            workspace_id = state["context"].get("workspace_id")
            context_items = state["context"].get("processed_context_items", [])

            if not context_items:
                state["error"] = "No processed context items provided"
                return state

            # Step 1: Cluster context items by topic/intent
            clusters = await self._cluster_context_items(context_items)

            logger.info(f"Clustered context into {len(clusters)} groups")

            # Step 2: Generate JTBD for each cluster
            extracted_jtbds = []

            for cluster_idx, cluster_items in enumerate(clusters):
                logger.info(f"Generating JTBD for cluster {cluster_idx + 1}")

                # Check budget
                if not check_budget_before_api_call("jtbd_extraction"):
                    state["error"] = "Budget limit reached for JTBD extraction"
                    return state

                # Generate JTBD statement
                jtbd = await self._generate_jtbd_statement(cluster_items)

                if jtbd:
                    # Link evidence citations
                    jtbd["evidence_citations"] = [item["id"] for item in cluster_items]
                    jtbd["id"] = str(uuid.uuid4())
                    jtbd["workspace_id"] = workspace_id
                    jtbd["created_at"] = datetime.utcnow().isoformat()

                    extracted_jtbds.append(jtbd)

            state["results"]["extracted_jtbds"] = extracted_jtbds
            state["results"]["jtbd_count"] = len(extracted_jtbds)

            logger.info(f"Successfully extracted {len(extracted_jtbds)} JTBDs")

        except Exception as e:
            logger.exception(f"Error in JTBD extraction: {str(e)}")
            state["error"] = str(e)

        return state

    async def _cluster_context_items(self, items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Cluster context items by topic/intent using embeddings"""
        try:
            # Extract embeddings
            embeddings = []
            valid_items = []

            for item in items:
                embedding = item.get("embedding")
                if embedding:
                    embeddings.append(embedding)
                    valid_items.append(item)

            if not embeddings:
                # If no embeddings, group by topic
                return self._cluster_by_topics(items)

            # Convert to numpy array
            embeddings_array = np.array(embeddings)

            # Use DBSCAN for clustering (density-based)
            clustering = DBSCAN(eps=0.5, min_samples=1).fit(embeddings_array)
            labels = clustering.labels_

            # Group items by cluster label
            clusters: Dict[int, List[Dict[str, Any]]] = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(valid_items[idx])

            return list(clusters.values())

        except Exception as e:
            logger.warning(f"Clustering error, falling back to topic-based grouping: {str(e)}")
            return self._cluster_by_topics(items)

    def _cluster_by_topics(self, items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Cluster items by topic when embeddings unavailable"""
        topic_clusters: Dict[str, List[Dict[str, Any]]] = {}

        for item in items:
            topics = item.get("topics", [])

            if not topics:
                # Create singleton cluster
                cluster_key = f"other_{len(topic_clusters)}"
                topic_clusters[cluster_key] = [item]
            else:
                # Use first topic as cluster key
                cluster_key = topics[0]
                if cluster_key not in topic_clusters:
                    topic_clusters[cluster_key] = []
                topic_clusters[cluster_key].append(item)

        return list(topic_clusters.values())

    async def _generate_jtbd_statement(self, cluster_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate a JTBD statement from a cluster of items"""
        try:
            llm = self.services.llm

            # Combine context from cluster items
            combined_context = "\n---\n".join([
                item.get("extracted_text", "")[:500]
                for item in cluster_items
            ])

            prompt = f"""Analyze these context items and extract a Jobs-to-be-Done statement.

Context:
{combined_context}

Generate a JTBD with these four components in JSON format:
{{
  "why": "The underlying job/goal (what are they trying to accomplish?)",
  "circumstances": "When/where does this job occur? What triggers it?",
  "forces": "What drives/pushes them toward this job? (emotional & functional drivers)",
  "anxieties": "What worries/fears do they have? What pulls them away from this job?"
}}

Return ONLY valid JSON. Be specific and grounded in the provided context. Each field should be 1-2 sentences."""

            response = await llm.invoke(prompt)
            jtbd = json.loads(response)

            # Add metadata
            jtbd["confidence_score"] = 0.8
            jtbd["status"] = "extracted"

            return jtbd

        except json.JSONDecodeError:
            logger.warning("Failed to parse JTBD response as JSON")
            return None
        except Exception as e:
            logger.error(f"JTBD generation error: {str(e)}")
            return None

    async def _validate(self, state: AgentState) -> AgentState:
        """Validate extracted JTBD statements"""
        try:
            state["stage"] = "validating_jtbds"

            extracted_jtbds = state["results"].get("extracted_jtbds", [])

            if not extracted_jtbds:
                logger.warning("No JTBDs extracted")
                # This is not necessarily an error - sometimes context doesn't yield clear jobs
                state["status"] = "completed"
                return state

            # Validate each JTBD has required fields
            required_fields = ["why", "circumstances", "forces", "anxieties"]
            valid_count = 0

            for jtbd in extracted_jtbds:
                if all(field in jtbd for field in required_fields):
                    valid_count += 1
                else:
                    logger.warning(f"JTBD {jtbd.get('id')} missing required fields")

            logger.info(f"Validated {valid_count}/{len(extracted_jtbds)} JTBDs")

            state["status"] = "completed"

        except Exception as e:
            logger.exception(f"Validation error: {str(e)}")
            state["error"] = str(e)

        return state

    async def _finalize(self, state: AgentState) -> AgentState:
        """Finalize JTBD extraction results"""
        state["stage"] = "finalized"

        jtbd_count = state["results"].get("jtbd_count", 0)
        logger.info(f"JTBD Extraction finalized with {jtbd_count} jobs")

        return state


# Factory function
def create_jtbd_extraction_agent() -> JTBDExtractionAgent:
    """Create a new JTBDExtractionAgent instance"""
    return JTBDExtractionAgent()
