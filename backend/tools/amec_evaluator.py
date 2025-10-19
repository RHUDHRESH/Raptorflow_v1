from langchain.tools import BaseTool
from utils.gemini_client import get_gemini_client
import json

class AMECEvaluatorTool(BaseTool):
    name = "amec_evaluator"
    description = """
    Evaluate marketing using AMEC framework:
    - Input: What did we invest? (time, money, effort)
    - Output: What did we produce? (content, campaigns)
    - Outcome: What happened? (engagement, leads)
    - Impact: What changed? (revenue, brand value, behavior)
    
    Examples:
    amec_evaluator(campaign_data={...}, performance_data={...})
    """
    
    def __init__(self):
        super().__init__()
        self.gemini = get_gemini_client()
    
    def _run(
        self,
        campaign_data: Dict,
        performance_data: Dict
    ) -> str:
        
        prompt = f"""Evaluate this campaign using the AMEC framework.

CAMPAIGN:
{json.dumps(campaign_data, indent=2)}

PERFORMANCE DATA:
{json.dumps(performance_data, indent=2)}

AMEC Framework Analysis:

## INPUT (What we invested)
Analyze:
- Budget spent
