"""
EVIDENCE GRAPH TOOLS v2 - Knowledge graph for evidence linking
Maps evidence to claims, builds RTB (Reason To Believe) networks, validates completeness
"""
import logging
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class EvidenceGraphBuilderTool(BaseTool):
    """Build evidence graph structure"""

    def __init__(self):
        super().__init__(
            name="evidence_graph_builder",
            description="Build knowledge graph connecting evidence to claims"
        )

    async def _execute(
        self,
        claims: List[str],
        evidence_sources: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Build evidence graph from claims and evidence"""
        logger.info(f"Building evidence graph for {len(claims)} claims")

        try:
            nodes = []
            edges = []
            node_id = 0

            # Create claim nodes
            claim_nodes = {}
            for claim in claims:
                claim_nodes[claim] = node_id
                nodes.append({
                    "id": node_id,
                    "type": "claim",
                    "content": claim,
                    "timestamp": datetime.now().isoformat()
                })
                node_id += 1

            # Create evidence nodes and link to claims
            for source in evidence_sources:
                evidence_text = source.get("evidence", "")
                source_type = source.get("type", "unknown")
                credibility = source.get("credibility", 0.5)

                nodes.append({
                    "id": node_id,
                    "type": "evidence",
                    "content": evidence_text,
                    "source": source.get("source", ""),
                    "source_type": source_type,
                    "credibility": credibility,
                    "timestamp": source.get("timestamp", datetime.now().isoformat())
                })

                # Link to relevant claims
                for claim, claim_id in claim_nodes.items():
                    relevance = self._calculate_relevance(evidence_text, claim)
                    if relevance > 0.3:  # Threshold for relevance
                        edges.append({
                            "from": node_id,
                            "to": claim_id,
                            "type": "supports",
                            "strength": round(relevance, 2),
                            "confidence": round(credibility * relevance, 2)
                        })

                node_id += 1

            # Calculate graph metrics
            total_nodes = len(nodes)
            total_edges = len(edges)
            avg_confidence = round(sum(e["confidence"] for e in edges) / len(edges), 2) if edges else 0
            coverage = self._calculate_coverage(claim_nodes, edges)

            return {
                "success": True,
                "nodes": nodes,
                "edges": edges,
                "statistics": {
                    "total_nodes": total_nodes,
                    "claim_nodes": len(claim_nodes),
                    "evidence_nodes": len(nodes) - len(claim_nodes),
                    "total_edges": total_edges,
                    "avg_confidence": avg_confidence,
                    "coverage": coverage
                },
                "graph_density": round(total_edges / (total_nodes * (total_nodes - 1) / 2) if total_nodes > 1 else 0, 2)
            }

        except Exception as e:
            logger.error(f"Evidence graph building failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_relevance(self, evidence: str, claim: str) -> float:
        """Calculate relevance between evidence and claim (0.0-1.0)"""
        evidence_lower = evidence.lower()
        claim_lower = claim.lower()

        # Exact match
        if claim_lower in evidence_lower:
            return 1.0

        # Partial matches
        claim_words = claim_lower.split()
        matched_words = sum(1 for word in claim_words if word in evidence_lower)
        partial_relevance = matched_words / len(claim_words) if claim_words else 0

        return min(1.0, partial_relevance)

    def _calculate_coverage(self, claims: Dict, edges: List[Dict]) -> float:
        """Calculate what % of claims have supporting evidence"""
        if not claims:
            return 0.0

        claim_ids = set(claims.values())
        supported_claims = set(edge["to"] for edge in edges)

        coverage = len(supported_claims & claim_ids) / len(claim_ids)
        return round(coverage, 2)


class RTBLinkerTool(BaseTool):
    """Link Reasons To Believe (RTB) to positioning claims"""

    def __init__(self):
        super().__init__(
            name="rtb_linker",
            description="Create RTB (Reason To Believe) connections between evidence and claims"
        )

    async def _execute(
        self,
        positioning_claims: Dict,
        evidence_sources: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Create RTB connections"""
        logger.info("Creating RTB connections")

        try:
            rtbs = []

            for claim_type, claim_content in positioning_claims.items():
                relevant_evidence = []

                for evidence in evidence_sources:
                    relevance = self._score_relevance(claim_content, evidence)
                    if relevance > 0.4:
                        relevant_evidence.append({
                            "evidence": evidence.get("evidence"),
                            "source": evidence.get("source"),
                            "relevance_score": round(relevance, 2),
                            "credibility": evidence.get("credibility", 0.5)
                        })

                # Sort by relevance
                relevant_evidence.sort(key=lambda x: x["relevance_score"], reverse=True)

                strength = self._calculate_rtb_strength(relevant_evidence)

                rtbs.append({
                    "claim": claim_type,
                    "claim_content": claim_content,
                    "evidence_count": len(relevant_evidence),
                    "supporting_evidence": relevant_evidence[:3],  # Top 3
                    "rtb_strength": round(strength, 2),
                    "recommendation": self._get_rtb_recommendation(strength, len(relevant_evidence))
                })

            # Calculate overall credibility
            total_rtbs = len(rtbs)
            strong_rtbs = sum(1 for rtb in rtbs if rtb["rtb_strength"] >= 0.7)
            credibility_score = round(strong_rtbs / max(total_rtbs, 1), 2)

            return {
                "success": True,
                "rtbs": rtbs,
                "total_claims": len(positioning_claims),
                "total_rtbs": total_rtbs,
                "strong_rtbs": strong_rtbs,
                "overall_credibility": credibility_score,
                "recommendation": "RTBs are well-supported. Ready for communication." if credibility_score > 0.7 else "Strengthen RTBs with additional evidence."
            }

        except Exception as e:
            logger.error(f"RTB linking failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _score_relevance(self, claim: str, evidence: Dict) -> float:
        """Score how relevant evidence is to claim"""
        claim_lower = claim.lower()
        evidence_text = evidence.get("evidence", "").lower()

        if claim_lower in evidence_text:
            return 1.0

        # Check keyword overlap
        claim_words = set(claim_lower.split())
        evidence_words = set(evidence_text.split())
        overlap = len(claim_words & evidence_words) / len(claim_words | evidence_words) if claim_words | evidence_words else 0

        # Factor in credibility
        credibility = evidence.get("credibility", 0.5)
        return min(1.0, overlap * credibility)

    def _calculate_rtb_strength(self, evidence: List[Dict]) -> float:
        """Calculate RTB strength based on evidence quality"""
        if not evidence:
            return 0.0

        # Average relevance weighted by credibility
        weighted_sum = sum(e["relevance_score"] * e["credibility"] for e in evidence)
        count = len(evidence)

        strength = weighted_sum / count if count else 0
        return min(1.0, strength)

    def _get_rtb_recommendation(self, strength: float, evidence_count: int) -> str:
        """Get RTB recommendation"""
        if strength >= 0.8 and evidence_count >= 3:
            return "Strong RTB. Well-supported claim."
        elif strength >= 0.6 and evidence_count >= 2:
            return "Moderate RTB. Adequate support."
        elif evidence_count == 0:
            return "No evidence found. Add supporting proof."
        else:
            return "Weak RTB. Gather more evidence or refine claim."


class CompletenessValidatorTool(BaseTool):
    """Validate research completeness"""

    def __init__(self):
        super().__init__(
            name="completeness_validator",
            description="Validate research completeness across multiple dimensions"
        )

    async def _execute(
        self,
        evidence_graph: Dict,
        competitor_coverage: List[str],
        market_data: Dict,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate completeness"""
        logger.info("Validating research completeness")

        try:
            scores = {}

            # Evidence completeness (0-0.3 weight)
            evidence_score = self._score_evidence_completeness(evidence_graph)
            scores["evidence"] = {
                "score": round(evidence_score, 2),
                "weight": 0.3,
                "weighted": round(evidence_score * 0.3, 2),
                "details": f"{evidence_graph.get('statistics', {}).get('total_edges', 0)} evidence connections"
            }

            # Competitor coverage (0-0.3 weight)
            competitor_score = self._score_competitor_coverage(competitor_coverage)
            scores["competitors"] = {
                "score": round(competitor_score, 2),
                "weight": 0.3,
                "weighted": round(competitor_score * 0.3, 2),
                "details": f"{len(competitor_coverage)} competitors analyzed"
            }

            # Market data (0-0.2 weight)
            market_score = self._score_market_data(market_data)
            scores["market_data"] = {
                "score": round(market_score, 2),
                "weight": 0.2,
                "weighted": round(market_score * 0.2, 2),
                "details": f"Market size, trends, and dynamics covered"
            }

            # Strategic alignment (0-0.2 weight)
            strategic_score = self._score_strategic_alignment(market_data)
            scores["strategic"] = {
                "score": round(strategic_score, 2),
                "weight": 0.2,
                "weighted": round(strategic_score * 0.2, 2),
                "details": f"Objectives and challenges addressed"
            }

            # Calculate total completeness
            total_score = sum(s["weighted"] for s in scores.values())
            total_score = round(min(1.0, total_score), 2)

            # Generate areas for improvement
            gaps = [k for k, v in scores.items() if v["score"] < 0.6]

            return {
                "success": True,
                "completeness_score": total_score,
                "dimension_scores": scores,
                "gaps": gaps,
                "recommendation": self._get_completeness_recommendation(total_score, gaps)
            }

        except Exception as e:
            logger.error(f"Completeness validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _score_evidence_completeness(self, evidence_graph: Dict) -> float:
        """Score evidence completeness"""
        stats = evidence_graph.get("statistics", {})
        edges = stats.get("total_edges", 0)
        coverage = stats.get("coverage", 0)

        # Need at least 10 evidence connections for completeness
        edge_score = min(1.0, edges / 10)
        coverage_score = coverage

        return (edge_score * 0.6 + coverage_score * 0.4)

    def _score_competitor_coverage(self, competitors: List[str]) -> float:
        """Score competitor coverage"""
        count = len(competitors)

        if count >= 5:
            return 1.0
        elif count >= 3:
            return 0.8
        elif count >= 1:
            return 0.5
        else:
            return 0.0

    def _score_market_data(self, market_data: Dict) -> float:
        """Score market data completeness"""
        required_fields = ["market_size", "growth_rate", "trends", "dynamics"]
        present_fields = sum(1 for field in required_fields if field in market_data and market_data[field])

        return present_fields / len(required_fields)

    def _score_strategic_alignment(self, market_data: Dict) -> float:
        """Score strategic alignment"""
        alignment_fields = ["objectives", "challenges", "opportunities", "threats"]
        present_fields = sum(1 for field in alignment_fields if field in market_data and market_data[field])

        return present_fields / len(alignment_fields)

    def _get_completeness_recommendation(self, score: float, gaps: List[str]) -> str:
        """Get completeness recommendation"""
        if score >= 0.85:
            return "Research is comprehensive. Ready for strategy development."
        elif score >= 0.65:
            return f"Research is adequate but has gaps: {', '.join(gaps)}. Consider deepening these areas."
        else:
            return f"Research needs significant work. Focus on: {', '.join(gaps)}"


class EvidenceSearchTool(BaseTool):
    """Search for relevant evidence"""

    def __init__(self):
        super().__init__(
            name="evidence_searcher",
            description="Search and retrieve relevant evidence for claims"
        )

    async def _execute(
        self,
        query: str,
        evidence_sources: List[Dict],
        min_credibility: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """Search for relevant evidence"""
        logger.info(f"Searching evidence for query: {query}")

        try:
            results = []

            for source in evidence_sources:
                credibility = source.get("credibility", 0.5)

                if credibility < min_credibility:
                    continue

                evidence = source.get("evidence", "")
                relevance = self._calculate_match_score(query, evidence)

                if relevance > 0.3:
                    results.append({
                        "evidence": evidence,
                        "source": source.get("source"),
                        "source_type": source.get("type", "unknown"),
                        "credibility": credibility,
                        "relevance": round(relevance, 2),
                        "score": round(credibility * relevance, 2)
                    })

            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)

            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results[:10],  # Top 10
                "coverage": len([r for r in results if r["score"] > 0.7])
            }

        except Exception as e:
            logger.error(f"Evidence search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_match_score(self, query: str, text: str) -> float:
        """Calculate match score between query and text"""
        query_lower = query.lower()
        text_lower = text.lower()

        if query_lower in text_lower:
            return 1.0

        query_words = query_lower.split()
        text_words = set(text_lower.split())

        matched = sum(1 for word in query_words if word in text_words)
        return matched / len(query_words) if query_words else 0


# Singleton instances
evidence_graph_builder = EvidenceGraphBuilderTool()
rtb_linker = RTBLinkerTool()
completeness_validator = CompletenessValidatorTool()
evidence_searcher = EvidenceSearchTool()
