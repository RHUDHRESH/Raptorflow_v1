"""
Research State Schema

Defines the central state object used throughout the LangGraph workflow.
This state is persisted via checkpointing and shared across all agents.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime
from langgraph.graph import add_messages


class ResearchState(TypedDict):
    """
    Central state shared across all research agents.

    LangGraph uses this TypedDict to:
    - Maintain state between nodes
    - Perform checkpointing for fault tolerance
    - Enable human-in-the-loop interventions
    - Track execution metadata
    """

    # === IDENTIFICATION & SESSION ===
    thread_id: str
    """Unique research session ID for tracking and persistence"""

    user_id: Optional[str]
    """User who initiated the research"""

    created_at: str
    """ISO timestamp of research start"""

    # === INPUT & CONFIGURATION ===
    user_query: str
    """Original user research question"""

    query_type: str
    """Research style: 'breadth_first' | 'depth_first' | 'hybrid'"""

    max_depth: int
    """Maximum research depth (nested sub-questions)"""

    max_sources: int
    """Maximum sources to fetch and process"""

    focus_areas: Optional[List[str]]
    """Optional specific areas to focus on"""

    # === INTAKE PHASE ===
    clarified_query: Optional[str]
    """Refined/clarified version of user query"""

    research_intent: Optional[str]
    """Detected intent: 'technical' | 'business' | 'academic' | 'fact_check' | 'comparison'"""

    research_domain: Optional[str]
    """Detected domain (e.g., 'machine_learning', 'healthcare', 'finance')"""

    context_requirements: Optional[Dict]
    """Additional context needed for comprehensive research"""

    # === PLANNING PHASE ===
    research_plan: Optional[Dict]
    """DAG of research sub-questions with dependencies"""

    sub_questions: List[str]
    """Decomposed research questions"""

    dependencies: Dict[str, List[str]]
    """Question dependencies: {'q2': ['q1']} means q2 depends on q1"""

    priority_order: List[str]
    """Execution order respecting dependencies"""

    research_strategy: Optional[str]
    """Chosen strategy description"""

    # === SEARCH PHASE ===
    search_results: List[Dict]
    """All search results from all engines"""

    perplexity_results: List[Dict]
    """Perplexity Sonar API results with citations"""

    exa_results: List[Dict]
    """Exa.ai neural search results"""

    google_results: List[Dict]
    """Google Custom Search results"""

    search_metadata: Dict
    """Search performance metrics and statistics"""

    search_queries_executed: List[Dict]
    """Record of all executed search queries"""

    # === FETCH PHASE ===
    fetched_content: List[Dict]
    """Full content extracted from URLs"""

    extraction_errors: List[Dict]
    """Failed fetch attempts with error reasons"""

    content_metadata: Dict
    """Content statistics (word count, language, etc.)"""

    skipped_urls: List[Dict]
    """URLs skipped due to filters or errors"""

    # === RANKING PHASE ===
    ranked_sources: List[Dict]
    """Sources sorted by relevance score"""

    relevance_scores: Dict[str, float]
    """URL -> relevance score mapping (0.0-1.0)"""

    diversity_score: float
    """Metric for content diversity across sources (0.0-1.0)"""

    quality_metrics: Dict[str, Dict]
    """Quality metrics per source"""

    # === SYNTHESIS PHASE ===
    synthesized_chunks: List[Dict]
    """Structured synthesis for each sub-question"""

    cross_references: List[Dict]
    """Facts supported by multiple sources"""

    contradictions: List[Dict]
    """Conflicting information found"""

    synthesis_notes: List[Dict]
    """Notes on synthesis process per question"""

    knowledge_gaps: List[str]
    """Identified gaps in research coverage"""

    # === WRITING PHASE ===
    final_report: Optional[str]
    """Markdown-formatted research report"""

    report_sections: Optional[Dict[str, str]]
    """Report broken into sections (intro, findings, etc.)"""

    citations: List[Dict]
    """All citations with full metadata"""

    confidence_scores: Dict[str, float]
    """Confidence metrics: 'overall', 'by_section', 'per_claim'"""

    bibliography: List[Dict]
    """Formatted bibliography entries"""

    # === METADATA & CONTROL FLOW ===
    messages: Annotated[list, add_messages]
    """Agent conversation history for multi-turn interaction"""

    current_phase: str
    """Current workflow phase"""

    phase_history: List[Dict]
    """History of all phases executed"""

    errors: List[Dict]
    """Error tracking with timestamps"""

    warnings: List[Dict]
    """Non-critical warnings from agents"""

    execution_time: Dict[str, float]
    """Time spent per phase in seconds"""

    total_tokens_used: int
    """Total LLM tokens consumed"""

    api_calls_made: Dict[str, int]
    """Count of API calls per service"""

    # === HUMAN-IN-THE-LOOP ===
    requires_clarification: bool
    """Flag indicating user input needed"""

    clarification_question: Optional[str]
    """Specific question to ask user"""

    user_feedback: Optional[str]
    """User's response/feedback"""

    # === CACHING & OPTIMIZATION ===
    cache_hits: int
    """Number of cached results used"""

    embedding_cache: Dict[str, List[float]]
    """Cached embeddings for similarity scoring"""

    # === FINAL OUTPUT ===
    research_complete: bool
    """Flag indicating research completion"""

    output_format: str
    """Requested output format: 'markdown' | 'json' | 'html'"""

    summary: Optional[str]
    """Short summary of findings"""
