"""
Deep Research Agent Module

World-class research system using LangGraph with:
- Multi-engine search (Perplexity, Exa, Google)
- Intelligent planning and decomposition
- Parallel execution with DAG-based dependencies
- Content fetching and synthesis
- Professional report generation
"""

from .state import ResearchState
from .agents import (
    IntakeAgent,
    PlannerAgent,
    SearcherAgent,
    FetcherAgent,
    RankerAgent,
    SynthesizerAgent,
    WriterAgent
)
from .workflow import DeepResearchGraph

__all__ = [
    "ResearchState",
    "IntakeAgent",
    "PlannerAgent",
    "SearcherAgent",
    "FetcherAgent",
    "RankerAgent",
    "SynthesizerAgent",
    "WriterAgent",
    "DeepResearchGraph"
]
