"""
Writer Agent - Final Report Generation

Phase 7 of research workflow:
- Generates professional markdown reports
- Integrates synthesized findings
- Creates citations and bibliography
- Produces multiple output formats
"""

import logging
import json
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..state import ResearchState

logger = logging.getLogger(__name__)


class WriterAgent:
    """
    Generates final research reports in markdown format.
    Includes executive summary, detailed findings, citations, confidence scores.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize writer agent.

        Args:
            llm: Language model (uses most powerful model for quality)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.3)

    async def process(self, state: ResearchState) -> ResearchState:
        """
        Phase 7: Report Writing

        Args:
            state: Current research state

        Returns:
            Updated state with final report and citations
        """
        logger.info("Writing phase started")

        synthesized_chunks = state.get("synthesized_chunks", [])
        ranked_sources = state.get("ranked_sources", [])[:30]
        contradictions = state.get("contradictions", [])

        # Generate report
        report = await self._generate_report(
            query=state.get("clarified_query") or state.get("user_query", ""),
            syntheses=synthesized_chunks,
            sources=ranked_sources,
            contradictions=contradictions
        )

        state["final_report"] = report.get("markdown", "")
        state["report_sections"] = report.get("sections", {})
        state["citations"] = report.get("citations", [])
        state["confidence_scores"] = report.get("confidence", {})
        state["bibliography"] = report.get("bibliography", [])
        state["summary"] = report.get("summary", "")
        state["current_phase"] = "complete"
        state["research_complete"] = True

        logger.info("Report generation complete")
        return state

    async def _generate_report(
        self,
        query: str,
        syntheses: List[Dict],
        sources: List[Dict],
        contradictions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive research report.

        Args:
            query: Original research query
            syntheses: Synthesized findings for each sub-question
            sources: Ranked source list
            contradictions: Identified contradictions

        Returns:
            Complete report with markdown, citations, and metadata
        """
        syntheses_text = json.dumps(syntheses[:10], indent=2)
        sources_text = json.dumps([
            {
                "url": s.get("url"),
                "title": s.get("title"),
                "relevance": s.get("relevance_score")
            }
            for s in sources
        ], indent=2)

        prompt = f"""
        Write a world-class research report on the following query:

        Research Query: {query}

        Synthesized Findings:
        {syntheses_text}

        Top Sources:
        {sources_text}

        Contradictions Found:
        {json.dumps(contradictions, indent=2) if contradictions else "None"}

        Report Requirements:
        1. Executive Summary (2-3 paragraphs with key findings)
        2. Introduction and Context
        3. Detailed Findings (organized by topic)
        4. Key Takeaways (bulleted)
        5. Analysis and Implications
        6. Limitations and Uncertainties
        7. Recommendations for Further Research
        8. Conclusion

        Formatting:
        - Use markdown with proper headings (#, ##, ###)
        - Include inline citations [1], [2], etc.
        - Bold important concepts
        - Use bullet points for lists
        - Professional academic tone
        - Technical accuracy appropriate to query

        Return JSON:
        {{
            "markdown": "Full report in markdown",
            "sections": {{"section_name": "section_content"}},
            "summary": "1-2 sentence summary",
            "citations": [
                {{"id": 1, "url": "...", "title": "...", "accessed": "date"}}
            ],
            "bibliography": [
                {{"id": 1, "authors": "...", "title": "...", "url": "...", "accessed": "date"}}
            ],
            "confidence": {{
                "overall": 0.0-1.0,
                "by_section": {{"section": 0.0-1.0}}
            }}
        }}
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("{"):
                report = json.loads(content)
            else:
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    report = json.loads(json_match.group())
                else:
                    # Fallback: treat entire response as markdown
                    report = {
                        "markdown": content,
                        "sections": {"Full Report": content},
                        "summary": "Report generation succeeded",
                        "citations": [],
                        "bibliography": [],
                        "confidence": {"overall": 0.7}
                    }

            # Ensure required fields
            report.setdefault("markdown", "")
            report.setdefault("sections", {})
            report.setdefault("citations", [])
            report.setdefault("bibliography", [])
            report.setdefault("confidence", {"overall": 0.7})
            report.setdefault("summary", "Research completed successfully")

            logger.info("Report generated successfully")
            return report

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {
                "markdown": f"# Research Report\n\nQuery: {query}\n\nReport generation encountered an error.",
                "sections": {},
                "citations": [],
                "bibliography": [],
                "confidence": {"overall": 0.0},
                "summary": "Report generation failed"
            }

    def _format_citations(self, citations: List[Dict]) -> str:
        """
        Format citations for markdown output.

        Args:
            citations: List of citation dictionaries

        Returns:
            Formatted citation string
        """
        if not citations:
            return ""

        formatted = "\n## References\n\n"
        for i, cite in enumerate(citations, 1):
            url = cite.get("url", "")
            title = cite.get("title", "Unknown")
            formatted += f"[{i}] {title}\n{url}\n\n"

        return formatted
