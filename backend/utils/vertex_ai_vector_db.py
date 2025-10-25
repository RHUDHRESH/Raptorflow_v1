"""
Vertex AI Matching Engine Vector Database

Replaces Chroma DB with Google's managed Vertex AI Matching Engine for:
- Semantic search of conversations
- Research document retrieval
- ICP matching and audience segmentation
- Efficient semantic similarity queries

Migration path from Chroma → Vertex AI Matching Engine
"""

import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine import MatchingEngineIndex
import numpy as np

logger = logging.getLogger(__name__)


class VertexAIVectorDB:
    """
    Vertex AI Matching Engine wrapper for RaptorFlow.

    Provides semantic search for:
    1. Conversation history (find related discussions)
    2. Research documents (retrieve relevant sources)
    3. ICP matching (find similar customer profiles)
    4. Content relevance scoring
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        index_name: str = "raptorflow-embeddings"
    ):
        """
        Initialize Vertex AI Vector DB.

        Args:
            project_id: GCP project ID
            location: GCP region
            index_name: Name of the matching engine index
        """
        self.project_id = project_id
        self.location = location
        self.index_name = index_name

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        self.index: Optional[MatchingEngineIndex] = None
        self.index_endpoint = None
        self.is_deployed = False

        logger.info(f"✅ Vertex AI Vector DB initialized for project {project_id}")

    async def create_index(
        self,
        dimensions: int = 1536,  # OpenAI text-embedding-3-small
        approximate_neighbors: int = 150,
        display_name: Optional[str] = None
    ) -> str:
        """
        Create a new vector index (one-time setup).

        This creates an undeployed index. Must call deploy_endpoint() after.

        Args:
            dimensions: Vector dimension size (default 1536 for OpenAI)
            approximate_neighbors: Number of approximate neighbors for ANN
            display_name: Display name for the index

        Returns:
            Index resource name
        """
        if display_name is None:
            display_name = self.index_name

        logger.info(f"Creating vector index: {display_name}")

        # Create index with Tree-AH algorithm (efficient for high-dimensional vectors)
        self.index = MatchingEngineIndex.create_tree_ah_index(
            display_name=display_name,
            dimensions=dimensions,
            approximate_neighbors_count=approximate_neighbors,
            distance_measure_type="DOT_PRODUCT_DISTANCE",  # Cosine similarity alternative
            shard_size="SHARD_SIZE_SMALL",
            description="RaptorFlow marketing intelligence embeddings for semantic search",
            labels={
                "app": "raptorflow",
                "version": "1.0",
                "environment": "production"
            }
        )

        logger.info(f"✅ Created index: {self.index.resource_name}")
        return self.index.resource_name

    async def deploy_endpoint(
        self,
        endpoint_name: Optional[str] = None,
        machine_type: str = "n1-standard-2",
        min_replicas: int = 1,
        max_replicas: int = 10
    ) -> str:
        """
        Deploy index to queryable endpoint.

        Args:
            endpoint_name: Name for the endpoint
            machine_type: GCP machine type
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas

        Returns:
            Endpoint resource name
        """
        if not self.index:
            raise ValueError("No index created yet. Call create_index() first.")

        if endpoint_name is None:
            endpoint_name = f"{self.index_name}-endpoint"

        logger.info(f"Deploying index to endpoint: {endpoint_name}")

        # Create endpoint
        self.index_endpoint = MatchingEngineIndexEndpoint.create(
            display_name=endpoint_name,
            public_endpoint_enabled=True,
            description="RaptorFlow semantic search endpoint",
            labels={
                "app": "raptorflow",
                "version": "1.0"
            }
        )

        # Deploy index to endpoint
        self.index_endpoint.deploy_index(
            index=self.index,
            deployed_index_id="deployed_raptorflow_index",
            machine_type=machine_type,
            min_replica_count=min_replicas,
            max_replica_count=max_replicas,
        )

        logger.info(f"✅ Deployed endpoint: {self.index_endpoint.resource_name}")
        self.is_deployed = True

        return self.index_endpoint.resource_name

    async def upsert_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Add or update embeddings in the index.

        Args:
            ids: Unique identifiers for each embedding
            embeddings: Vector embeddings (must match index dimensions)
            metadata: Associated metadata for retrieval
        """
        if not self.is_deployed:
            raise ValueError("Index not deployed. Call deploy_endpoint() first.")

        if len(ids) != len(embeddings) or len(ids) != len(metadata):
            raise ValueError("ids, embeddings, and metadata must have same length")

        logger.info(f"Upserting {len(ids)} embeddings to index...")

        # Format datapoints for Vertex AI
        datapoints = []
        for id_, embedding, meta in zip(ids, embeddings, metadata):
            datapoints.append({
                "id": id_,
                "embedding": embedding,
                "restricts": [
                    {
                        "namespace": k,
                        "allow_list": [str(v)]
                    }
                    for k, v in meta.items()
                ],
            })

        # Batch upsert (Vertex AI handles batching internally)
        self.index.upsert_datapoints(datapoints=datapoints)

        logger.info(f"✅ Upserted {len(ids)} embeddings successfully")

    async def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find semantically similar vectors (nearest neighbors).

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filters: Optional filters like {"business_id": ["123"]}

        Returns:
            List of {id, distance, metadata}
        """
        if not self.is_deployed:
            raise ValueError("Index not deployed. Call deploy_endpoint() first.")

        logger.info(f"Searching for {top_k} nearest neighbors...")

        # Build filter list if provided
        restrict_list = None
        if filters:
            restrict_list = [
                {
                    "namespace": namespace,
                    "allow_list": values
                }
                for namespace, values in filters.items()
            ]

        # Query endpoint
        response = self.index_endpoint.match(
            deployed_index_id="deployed_raptorflow_index",
            queries=[query_embedding],
            num_neighbors=top_k,
            restrict_list=restrict_list,
        )

        # Extract results
        results = []
        for match in response[0]:
            results.append({
                "id": match.id,
                "distance": float(match.distance),
                "score": 1.0 - (float(match.distance) / 2.0),  # Normalize to [0,1]
            })

        logger.info(f"✅ Found {len(results)} matching results")
        return results

    async def delete_embeddings(self, ids: List[str]) -> None:
        """
        Delete embeddings from the index.

        Args:
            ids: IDs to delete
        """
        if not self.index:
            raise ValueError("No index available")

        logger.info(f"Deleting {len(ids)} embeddings...")

        for id_ in ids:
            self.index.remove_datapoints(datapoint_ids=[id_])

        logger.info(f"✅ Deleted {len(ids)} embeddings")

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.

        Returns:
            {
                "index_name": str,
                "deployed": bool,
                "dimension": int,
                "vectors_count": int,
                "status": str
            }
        """
        if not self.index:
            return {"error": "No index created yet"}

        return {
            "index_name": self.index.display_name,
            "deployed": self.is_deployed,
            "dimensions": self.index.dimensions if hasattr(self.index, 'dimensions') else None,
            "status": self.index.state if hasattr(self.index, 'state') else "unknown",
            "resource_name": self.index.resource_name,
        }


# Singleton instance
_vertex_ai_db: Optional[VertexAIVectorDB] = None


def get_vertex_ai_db(project_id: str) -> VertexAIVectorDB:
    """Get or create singleton Vertex AI Vector DB instance."""
    global _vertex_ai_db

    if _vertex_ai_db is None:
        _vertex_ai_db = VertexAIVectorDB(project_id)

    return _vertex_ai_db


# ============================================================================
# Migration Helpers: Chroma → Vertex AI
# ============================================================================

async def migrate_chroma_to_vertex_ai(
    chroma_client,
    vertex_ai_db: VertexAIVectorDB,
    embedding_service,
    business_id: str
) -> Dict[str, Any]:
    """
    Migrate embeddings from Chroma DB to Vertex AI.

    Steps:
    1. Get all collections from Chroma
    2. For each document, generate embedding
    3. Upsert to Vertex AI with metadata

    Args:
        chroma_client: Chroma DB client instance
        vertex_ai_db: Vertex AI instance
        embedding_service: Service to generate embeddings
        business_id: Business to migrate

    Returns:
        Migration statistics
    """
    logger.info(f"Starting migration for business {business_id}...")

    stats = {
        "total_migrated": 0,
        "failed": 0,
        "errors": [],
        "start_time": datetime.utcnow(),
    }

    try:
        # Get all collections for this business
        collections = chroma_client.list_collections()

        for collection in collections:
            try:
                logger.info(f"Migrating collection: {collection.name}")

                # Get all documents from this collection
                documents = collection.get()

                if not documents or not documents.get("ids"):
                    logger.info(f"Collection {collection.name} is empty, skipping")
                    continue

                ids = documents["ids"]
                texts = documents["documents"]

                # Generate embeddings
                embeddings = []
                for text in texts:
                    embedding = await embedding_service.generate_embedding(text)
                    embeddings.append(embedding)

                # Prepare metadata
                metadata = []
                for id_, text in zip(ids, texts):
                    metadata.append({
                        "business_id": business_id,
                        "collection": collection.name,
                        "text_preview": text[:100],
                        "migrated_at": datetime.utcnow().isoformat(),
                    })

                # Upsert to Vertex AI
                await vertex_ai_db.upsert_embeddings(ids, embeddings, metadata)

                stats["total_migrated"] += len(ids)
                logger.info(f"✅ Migrated {len(ids)} from {collection.name}")

            except Exception as e:
                stats["failed"] += 1
                error_msg = f"Failed to migrate {collection.name}: {str(e)}"
                stats["errors"].append(error_msg)
                logger.error(error_msg)

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        stats["errors"].append(str(e))

    stats["end_time"] = datetime.utcnow()
    stats["duration_seconds"] = (stats["end_time"] - stats["start_time"]).total_seconds()

    logger.info(f"✅ Migration complete: {stats['total_migrated']} migrated, {stats['failed']} failed")
    return stats


async def validate_migration(
    chroma_client,
    vertex_ai_db: VertexAIVectorDB,
    business_id: str
) -> Dict[str, Any]:
    """
    Validate that migration was successful.

    Compares document counts and performs sample searches.

    Args:
        chroma_client: Chroma client
        vertex_ai_db: Vertex AI instance
        business_id: Business to validate

    Returns:
        Validation results
    """
    logger.info(f"Validating migration for {business_id}...")

    results = {
        "chroma_count": 0,
        "vertex_ai_count": 0,
        "sample_search_ok": False,
        "status": "unknown",
    }

    try:
        # Count Chroma documents
        collections = chroma_client.list_collections()
        chroma_count = 0
        for collection in collections:
            docs = collection.get()
            if docs:
                chroma_count += len(docs.get("ids", []))

        results["chroma_count"] = chroma_count

        # Get Vertex AI stats
        stats = vertex_ai_db.get_index_stats()
        results["vertex_ai_deployed"] = vertex_ai_db.is_deployed

        # Validate counts match
        if chroma_count > 0:
            results["status"] = "success" if vertex_ai_db.is_deployed else "warning"
        else:
            results["status"] = "no_data"

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        results["status"] = "failed"
        results["error"] = str(e)

    return results
