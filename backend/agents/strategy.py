from __future__ import annotations

import json
from typing import Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from ..tools.bet_evaluator import BetEvaluatorTool
from ..tools.north_star_calculator import NorthStarCalculatorTool
from ..tools.race_planner import RACEPlannerTool
from ..tools.seven_ps_builder import SevenPsBuilderTool
from ..utils.supabase_client import get_supabase_client


class StrategyState(TypedDict):
    business_id: str
    positioning: Dict
    icps: List[Dict]
    strategy: Dict
    status: str


class StrategyAgent:
    """Generate the end-to-end go-to-market strategy artefacts."""

    def __init__(self) -> None:
        self.seven_ps = SevenPsBuilderTool()
        self.north_star = NorthStarCalculatorTool()
        self.bet_evaluator = BetEvaluatorTool()
        self.race_planner = RACEPlannerTool()
        self.supabase = get_supabase_client()

        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(StrategyState)
        graph.add_node("build_mix", self._build_marketing_mix)
        graph.add_node("north_star", self._calculate_north_star)
        graph.add_node("strategic_bets", self._create_bets)
        graph.add_node("race_plan", self._plan_race)
        graph.add_node("persist", self._persist)

        graph.set_entry_point("build_mix")
        graph.add_edge("build_mix", "north_star")
        graph.add_edge("north_star", "strategic_bets")
        graph.add_edge("strategic_bets", "race_plan")
        graph.add_edge("race_plan", "persist")
        graph.add_edge("persist", END)
        return graph

    def _build_marketing_mix(self, state: StrategyState) -> StrategyState:
        business_id = state["business_id"]
        business = (
            self.supabase.table("businesses")
            .select("*")
            .eq("id", business_id)
            .single()
            .execute()
            .data
        )

        positioning_record = (
            self.supabase.table("positioning_analyses")
            .select("selected_option")
            .eq("business_id", business_id)
            .single()
            .execute()
            .data
        ) or {"selected_option": {}}

        icps = (
            self.supabase.table("icps")
            .select("*")
            .eq("business_id", business_id)
            .execute()
            .data
        )

        result = json.loads(
            self.seven_ps._run(  # pylint: disable=protected-access
                business_data=business or {},
                positioning=positioning_record.get("selected_option") or {},
                icps=icps or [],
            )
        )
        state["strategy"] = {
            "seven_ps": result["seven_ps"],
            "positioning_word": result.get("positioning"),
        }
        state["icps"] = icps or []
        return state

    def _calculate_north_star(self, state: StrategyState) -> StrategyState:
        business_id = state["business_id"]
        business = (
            self.supabase.table("businesses")
            .select("*")
            .eq("id", business_id)
            .single()
            .execute()
            .data
        )

        objectives = (
            self.supabase.table("subscriptions")
            .select("tier", "status")
            .eq("business_id", business_id)
            .single()
            .execute()
            .data
        ) or {}

        north_star = json.loads(
            self.north_star._run(  # pylint: disable=protected-access
                business_data=business or {},
                objectives=objectives,
            )
        )
        state["strategy"]["north_star"] = north_star
        return state

    def _create_bets(self, state: StrategyState) -> StrategyState:
        bets = json.loads(
            self.bet_evaluator._run(  # pylint: disable=protected-access
                action="create",
                strategy=state["strategy"].get("seven_ps", {}),
                icps=state.get("icps", []),
            )
        )
        state["strategy"]["strategic_bets"] = bets.get("bets")
        return state

    def _plan_race(self, state: StrategyState) -> StrategyState:
        race_plan = json.loads(
            self.race_planner._run(  # pylint: disable=protected-access
                business_id=state["business_id"],
                goal="north_star",
                positioning=state["strategy"].get("seven_ps", {}),
            )
        )
        state["strategy"]["race_plan"] = race_plan
        return state

    def _persist(self, state: StrategyState) -> StrategyState:
        self.supabase.table("strategies").insert(
            {
                "business_id": state["business_id"],
                "strategy": state["strategy"],
            }
        ).execute()
        state["status"] = "complete"
        return state


strategy_agent = StrategyAgent().app
