from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class BetEvaluatorTool(BaseTool):
    name = "bet_evaluator"
    description = """
    Create and evaluate strategic bets with kill-switches.
    
    A strategic bet format:
    - Hypothesis: "Instagram Reels will drive 40% of leads"
    - Success threshold: "40% of leads from Reels by end of Q1"
    - Kill-switch: "If < 10% by week 4, stop and pivot"
    - Resource allocation: "20% of budget, 30% of content time"
    
    Examples:
    bet_evaluator(strategy={...}, icps=[...])
    bet_evaluator(action='evaluate', bet={...}, current_data={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        action: str = 'create',
        strategy: Optional[Dict] = None,
        icps: Optional[List[Dict]] = None,
        bet: Optional[Dict] = None,
        current_data: Optional[Dict] = None,
        count: int = 5
    ) -> str:
        
        if action == 'create':
            if not strategy:
                raise ValueError("create requires: strategy")
            
            prompt = f"""Create {count} strategic bets for this marketing strategy.

STRATEGY:
{json.dumps(strategy, indent=2)}

{f"ICPs: {json.dumps(icps)}" if icps else ""}

A strategic bet is a high-conviction hypothesis about what will drive results.

For each bet, provide:

1. HYPOTHESIS
   - Clear statement: "We believe [action] will result in [outcome]"
   - Specific and measurable
   - Time-bound

2. SUCCESS THRESHOLD
   - Metric: What we measure
   - Target: Specific number/percentage
   - Timeline: When we measure
   - Example: "40% of leads from Instagram Reels by end of Q1"

3. KILL-SWITCH (When to abandon)
   - Early indicator: What to check before full timeline
   - Red flag threshold: When it's clearly not working
   - Example: "If < 10% of leads from Reels by week 4, stop"

4. RESOURCE ALLOCATION
   - Budget: Percentage or dollar amount
