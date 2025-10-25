"""
Planner Agent - Research Strategy & DAG Generation

Phase 2 of research workflow:
- Decomposes complex queries into sub-questions
- Builds dependency graph for parallel execution
- Creates execution plan respecting dependencies
- Enables efficient multi-threaded research
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ..state import ResearchState

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Creates research plan as a DAG (Directed Acyclic Graph).
    Decomposes main query into researchable sub-questions with dependencies.
    Enables parallel execution of independent research paths.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """
        Initialize planner agent with LLM.

        Args:
            llm: Language model instance (uses default if not provided)
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.5)

    async def process(self, state: ResearchState) -> ResearchState:
        """
        Phase 2: Strategic Planning

        Args:
            state: Current research state

        Returns:
            Updated state with research plan and execution order
        """
        logger.info("Planning phase started")

        query = state["clarified_query"] or state["user_query"]
        intent = state["research_intent"]
        query_type = state["query_type"]

        state["current_phase"] = "planning"

        # 1. Decompose into sub-questions
        sub_questions = await self._decompose_query(query, intent, query_type)
        state["sub_questions"] = sub_questions
        logger.info(f"Decomposed query into {len(sub_questions)} sub-questions")

        # 2. Build dependency graph
        dag = await self._build_dag(sub_questions)
        state["research_plan"] = dag
        state["dependencies"] = dag["dependencies"]
        logger.debug(f"Built DAG with {len(dag['nodes'])} nodes")

        # 3. Calculate execution order using topological sort
        priority = self._topological_sort(dag)
        state["priority_order"] = priority
        logger.info(f"Execution order: {priority}")

        # 4. Generate strategy description
        state["research_strategy"] = self._describe_strategy(dag, query_type)

        state["current_phase"] = "searching"
        return state

    async def _decompose_query(
        self,
        query: str,
        intent: str,
        query_type: str
    ) -> List[str]:
        """
        Break down complex query into researchable sub-questions.

        Args:
            query: Main research query
            intent: Detected research intent
            query_type: Research type (breadth/depth/hybrid)

        Returns:
            List of 5-10 sub-questions
        """
        sub_question_count = self._calculate_num_subquestions(query_type)

        prompt = f"""
        Decompose this research query into {sub_question_count} specific,
        researchable sub-questions that together provide comprehensive coverage.

        Main Query: "{query}"
        Research Intent: {intent}
        Research Type: {query_type}

        Requirements for sub-questions:
        - Each must be independently researchable
        - Cover different aspects: WHAT, WHY, HOW, WHO, WHEN, WHERE, TRENDS
        - Include both fundamental and advanced perspectives
        - Consider practical implications and theoretical foundations
        - Include recent developments if applicable
        - Ensure completeness: answering all should answer the main query

        For {query_type} research:
        - breadth_first: Wide coverage of different aspects and perspectives
        - depth_first: Deep exploration of specific technical/conceptual aspects
        - hybrid: Balance of both breadth and depth

        Respond with ONLY a JSON array of strings (questions):
        ["question1", "question2", "question3", ...]
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Parse JSON array
            if content.startswith("["):
                sub_questions = json.loads(content)
            else:
                import re
                json_match = re.search(r"\[.*\]", content, re.DOTALL)
                if json_match:
                    sub_questions = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON array in response")

            # Ensure we have questions
            if not sub_questions:
                sub_questions = [query]  # Fallback to original query

            return sub_questions[:10]  # Limit to 10

        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")
            # Return default decomposition
            return [
                f"What is {query.lower()}?",
                f"Why is {query.lower()} important?",
                f"How does {query.lower()} work?",
                f"What are recent developments in {query.lower()}?"
            ]

    async def _build_dag(self, sub_questions: List[str]) -> Dict[str, Any]:
        """
        Create DAG showing dependencies between questions.

        Args:
            sub_questions: List of sub-questions

        Returns:
            DAG structure with nodes and dependencies
        """
        prompt = f"""
        Analyze these research sub-questions and identify dependencies.
        Some questions should be answered before others for context.

        Sub-questions:
        {json.dumps(sub_questions, indent=2)}

        For each question, determine if it depends on answers to other questions.
        Example: "How does X work?" might depend on "What is X?"

        Respond with ONLY valid JSON:
        {{
            "nodes": [
                {{"id": "q1", "index": 0, "level": 0}},
                {{"id": "q2", "index": 1, "level": 1}},
                {{"id": "q3", "index": 2, "level": 1}}
            ],
            "dependencies": {{
                "q2": ["q1"],
                "q3": ["q1"]
            }},
            "parallel_groups": [
                ["q1"],
                ["q2", "q3"],
                ["q4"]
            ],
            "notes": "Execution strategy description"
        }}

        Guidelines:
        - Use "q1", "q2", etc. as node IDs matching array indices
        - Only specify dependencies where truly necessary
        - Maximize opportunities for parallel execution
        - Keep total levels (depth) reasonable (usually 2-3)
        """

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("{"):
                dag = json.loads(content)
            else:
                import re
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    dag = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON in response")

            # Add questions to nodes
            for i, node in enumerate(dag.get("nodes", [])):
                if i < len(sub_questions):
                    node["question"] = sub_questions[i]

            return dag

        except Exception as e:
            logger.error(f"DAG building failed: {e}")
            # Return default sequential DAG
            nodes = [
                {"id": f"q{i}", "index": i, "level": 0, "question": q}
                for i, q in enumerate(sub_questions)
            ]
            return {
                "nodes": nodes,
                "dependencies": {},
                "parallel_groups": [[f"q{i}" for i in range(len(sub_questions))]],
                "notes": "Sequential execution (default)"
            }

    def _topological_sort(self, dag: Dict[str, Any]) -> List[str]:
        """
        Determine execution order respecting dependencies.
        Uses Kahn's algorithm for topological sorting.

        Args:
            dag: Dependency graph

        Returns:
            List of node IDs in execution order
        """
        # Build in-degree map
        dependencies = dag.get("dependencies", {})
        all_nodes = {node["id"] for node in dag.get("nodes", [])}

        in_degree = {node: 0 for node in all_nodes}
        adjacency = defaultdict(list)

        # Build graph
        for node, deps in dependencies.items():
            for dep in deps:
                adjacency[dep].append(node)
                in_degree[node] += 1

        # Kahn's algorithm
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles (shouldn't happen with proper input)
        if len(result) != len(all_nodes):
            logger.warning("Cycle detected in DAG, returning partial order")

        return result

    def _calculate_num_subquestions(self, query_type: str) -> int:
        """
        Calculate number of sub-questions based on query type.

        Args:
            query_type: Type of research query

        Returns:
            Number of sub-questions to generate
        """
        return {
            "breadth_first": 8,
            "depth_first": 6,
            "hybrid": 7
        }.get(query_type, 7)

    def _describe_strategy(self, dag: Dict[str, Any], query_type: str) -> str:
        """
        Generate human-readable strategy description.

        Args:
            dag: Dependency graph
            query_type: Type of research

        Returns:
            Strategy description
        """
        parallel_groups = dag.get("parallel_groups", [])
        num_groups = len(parallel_groups)

        description = f"""
Research Strategy:
- Query Type: {query_type}
- Execution Model: {num_groups} sequential phases with internal parallelization
- Total Sub-questions: {len(dag.get('nodes', []))}
- Estimated Phases: {num_groups}

Execution Plan:
"""
        for i, group in enumerate(parallel_groups, 1):
            description += f"\nPhase {i} (Parallel): {', '.join(group)}"

        return description.strip()
