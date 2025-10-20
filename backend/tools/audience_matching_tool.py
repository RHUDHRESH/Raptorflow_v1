"""
AUDIENCE MATCHING TOOL
Match content to customer personas and ICPs
"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class AudienceMatchingTool:
    """Match content to audience personas"""

    def __init__(self):
        self.name = "audience_matching"
        self.description = "Match content to target audience personas"

    async def _execute(
        self,
        content: str,
        content_type: str,
        icps: List[Dict[str, Any]],
        tone_assessment: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Match content to ICPs"""

        logger.info("Matching content to audience personas")

        try:
            matches = []

            for icp in icps:
                match_score = self._calculate_match_score(content, content_type, icp, tone_assessment)
                matches.append({
                    "icp_name": icp.get("name", "Unknown"),
                    "icp_role": icp.get("role", "Unknown"),
                    "match_score": round(match_score, 2),
                    "match_level": self._score_to_level(match_score),
                    "ideal_platforms": icp.get("behavior", {}).get("top_platforms", []),
                    "content_preferences": icp.get("behavior", {}).get("content_preferences", {}),
                    "resonance_factors": self._identify_resonance_factors(content, icp),
                    "messaging_suggestions": self._generate_messaging_suggestions(content, icp)
                })

            # Sort by match score
            matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)

            return {
                "success": True,
                "matches": matches,
                "best_match": matches[0] if matches else None,
                "total_icps_evaluated": len(icps),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Audience matching failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _calculate_match_score(
        self,
        content: str,
        content_type: str,
        icp: Dict[str, Any],
        tone_assessment: Dict = None
    ) -> float:
        """Calculate match score between content and ICP"""

        score = 0.5  # Base score

        # Content type preference match
        content_prefs = icp.get("behavior", {}).get("content_preferences", {})
        if content_type.lower() in [ct.lower() for ct in content_prefs.keys()]:
            score += 0.15

        # Word count match
        word_count = len(content.split())
        ideal_word_range = icp.get("behavior", {}).get("ideal_word_count", (50, 300))
        if ideal_word_range[0] <= word_count <= ideal_word_range[1]:
            score += 0.1

        # Tone match
        if tone_assessment:
            icp_tone_preference = icp.get("behavior", {}).get("preferred_tone", "neutral")
            tone = tone_assessment.get("primary_tone", "neutral")

            if tone.lower() == icp_tone_preference.lower():
                score += 0.1

            # Formality match
            icp_formality = icp.get("behavior", {}).get("formality_preference", "semi-formal")
            formality = tone_assessment.get("formality", "semi-formal")

            if formality.lower() == icp_formality.lower():
                score += 0.05

        # Sentiment match
        if tone_assessment:
            icp_sentiment = icp.get("behavior", {}).get("sentiment_preference", "positive")
            sentiment = tone_assessment.get("sentiment", {}).get("type", "neutral")

            if sentiment.lower() == icp_sentiment.lower():
                score += 0.05

        # Content features match
        icp_features = icp.get("behavior", {}).get("content_features", [])

        if "questions" in icp_features and "?" in content:
            score += 0.05

        if "calls_to_action" in icp_features and any(
            cta in content.lower() for cta in ["click", "join", "subscribe", "buy"]
        ):
            score += 0.05

        # Platform alignment
        ideal_platforms = icp.get("behavior", {}).get("top_platforms", [])
        # This would be matched during platform recommendation

        return min(1.0, score)

    def _score_to_level(self, score: float) -> str:
        """Convert score to descriptive level"""
        if score >= 0.85:
            return "Perfect Match"
        elif score >= 0.70:
            return "Strong Match"
        elif score >= 0.55:
            return "Good Match"
        elif score >= 0.40:
            return "Fair Match"
        else:
            return "Poor Match"

    def _identify_resonance_factors(self, content: str, icp: Dict[str, Any]) -> List[str]:
        """Identify why content resonates with ICP"""

        factors = []
        content_lower = content.lower()

        # Pain points
        pain_points = icp.get("pain_points", [])
        for pain in pain_points:
            if pain.lower() in content_lower:
                factors.append(f"Addresses pain point: {pain}")

        # Goals
        goals = icp.get("goals", [])
        for goal in goals:
            if goal.lower() in content_lower:
                factors.append(f"Supports goal: {goal}")

        # Values
        values = icp.get("values", [])
        for value in values:
            if value.lower() in content_lower:
                factors.append(f"Aligns with value: {value}")

        # Use case
        use_cases = icp.get("use_cases", [])
        for use_case in use_cases:
            if use_case.lower() in content_lower:
                factors.append(f"Relevant to use case: {use_case}")

        # Industry/role specific language
        role = icp.get("role", "").lower()
        industry_keywords = {
            "executive": ["roi", "growth", "strategy", "results"],
            "developer": ["code", "api", "technical", "integration"],
            "marketer": ["campaign", "audience", "engagement", "analytics"],
            "sales": ["deal", "pipeline", "prospect", "close"],
            "operations": ["process", "efficiency", "automation", "scaling"]
        }

        if role in industry_keywords:
            keywords = industry_keywords[role]
            matched_keywords = [kw for kw in keywords if kw in content_lower]
            if matched_keywords:
                factors.append(f"Uses {role}-relevant language: {', '.join(matched_keywords)}")

        return factors if factors else ["Generic content that could work for most audiences"]

    def _generate_messaging_suggestions(self, content: str, icp: Dict[str, Any]) -> List[str]:
        """Generate messaging suggestions for ICP"""

        suggestions = []

        # Pain point focused messaging
        pain_points = icp.get("pain_points", [])
        if pain_points:
            suggestions.append(f"Emphasize how this solves: {pain_points[0]}")

        # Goal-focused messaging
        goals = icp.get("goals", [])
        if goals:
            suggestions.append(f"Connect to their goal: {goals[0]}")

        # Role-specific messaging
        role = icp.get("role", "")
        if role.lower() in ["executive", "cfo", "ceo"]:
            suggestions.append("Lead with business impact and ROI metrics")
        elif role.lower() in ["developer", "technical lead"]:
            suggestions.append("Include technical details and integration possibilities")
        elif role.lower() in ["marketer"]:
            suggestions.append("Highlight metrics, engagement, and audience insights")

        # Seniority level messaging
        seniority = icp.get("seniority", "")
        if seniority.lower() == "senior":
            suggestions.append("Focus on strategic impact and organizational benefits")
        elif seniority.lower() == "junior":
            suggestions.append("Provide clear, actionable steps and learning opportunities")

        # Budget consideration
        budget = icp.get("budget_level", "")
        if budget.lower() in ["low", "limited"]:
            suggestions.append("Highlight cost-effectiveness and ROI")
        elif budget.lower() in ["high", "enterprise"]:
            suggestions.append("Emphasize premium features and comprehensive solutions")

        # Experience level
        experience = icp.get("experience_level", "")
        if experience.lower() == "beginner":
            suggestions.append("Use simple language and include helpful guides")
        elif experience.lower() == "expert":
            suggestions.append("Dive into advanced features and customization options")

        return suggestions

    def _get_ideal_platforms_by_icp(self, icp: Dict[str, Any]) -> List[str]:
        """Get ideal platforms for ICP"""
        return icp.get("behavior", {}).get("top_platforms", [])


class ICPPersonaBuilder:
    """Build and manage ICP personas"""

    def __init__(self):
        self.name = "icp_persona_builder"
        self.description = "Build and manage ideal customer personas"

    async def _execute(
        self,
        icp_data: Dict[str, Any],
        action: str = "create",
        **kwargs
    ) -> Dict[str, Any]:
        """Build or update ICP persona"""

        logger.info(f"ICP persona action: {action}")

        try:
            if action == "create":
                persona = self._create_persona(icp_data)
            elif action == "update":
                persona = self._update_persona(icp_data)
            elif action == "analyze":
                persona = self._analyze_persona(icp_data)
            elif action == "compare":
                persona = self._compare_personas(icp_data)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

            return {
                "success": True,
                "action": action,
                "persona": persona,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"ICP persona operation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _create_persona(self, icp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new ICP persona"""

        return {
            "id": f"icp_{datetime.now().timestamp()}",
            "name": icp_data.get("name", "Unnamed Persona"),
            "role": icp_data.get("role", "Unknown"),
            "seniority": icp_data.get("seniority", "mid-level"),
            "demographics": {
                "age_range": icp_data.get("age_range", "25-45"),
                "experience_level": icp_data.get("experience_level", "mid-career"),
                "company_size": icp_data.get("company_size", "mid-market")
            },
            "pain_points": icp_data.get("pain_points", []),
            "goals": icp_data.get("goals", []),
            "values": icp_data.get("values", []),
            "use_cases": icp_data.get("use_cases", []),
            "behavior": {
                "top_platforms": icp_data.get("platforms", []),
                "content_preferences": icp_data.get("content_preferences", {}),
                "ideal_word_count": icp_data.get("ideal_word_count", (100, 300)),
                "preferred_tone": icp_data.get("preferred_tone", "semi-formal"),
                "formality_preference": icp_data.get("formality_preference", "semi-formal"),
                "sentiment_preference": icp_data.get("sentiment_preference", "positive"),
                "content_features": icp_data.get("content_features", [])
            },
            "budget_level": icp_data.get("budget_level", "mid-range"),
            "decision_criteria": icp_data.get("decision_criteria", []),
            "created_at": datetime.now().isoformat()
        }

    def _update_persona(self, icp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing persona"""
        # In production, this would update in database
        return self._create_persona(icp_data)

    def _analyze_persona(self, icp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze persona characteristics"""

        return {
            "persona_profile": icp_data.get("name", "Unknown"),
            "motivation_drivers": self._identify_motivation_drivers(icp_data),
            "decision_making_style": self._identify_decision_style(icp_data),
            "preferred_communication": self._identify_communication_style(icp_data),
            "likely_objections": self._predict_objections(icp_data),
            "activation_triggers": self._identify_activation_triggers(icp_data),
            "customer_journey_stage": self._identify_customer_stage(icp_data)
        }

    def _compare_personas(self, personas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple personas"""

        personas = personas_data.get("personas", [])

        if len(personas) < 2:
            return {"error": "Need at least 2 personas to compare"}

        return {
            "comparison": {
                "total_personas": len(personas),
                "common_pain_points": self._find_common_items(personas, "pain_points"),
                "common_goals": self._find_common_items(personas, "goals"),
                "platform_overlap": self._find_common_platforms(personas),
                "differences": self._identify_differences(personas)
            }
        }

    def _identify_motivation_drivers(self, icp: Dict[str, Any]) -> List[str]:
        """Identify what motivates the persona"""
        drivers = []

        goals = icp.get("goals", [])
        for goal in goals:
            if "growth" in goal.lower():
                drivers.append("Business growth and expansion")
            elif "efficiency" in goal.lower():
                drivers.append("Operational efficiency")
            elif "revenue" in goal.lower():
                drivers.append("Revenue increase")
            elif "quality" in goal.lower():
                drivers.append("Quality improvement")

        return drivers if drivers else ["Achieving business objectives"]

    def _identify_decision_style(self, icp: Dict[str, Any]) -> str:
        """Identify decision-making style"""
        seniority = icp.get("seniority", "").lower()

        if seniority in ["executive", "c-level"]:
            return "Data-driven, ROI-focused, delegates implementation"
        elif seniority in ["senior", "manager"]:
            return "Balanced approach with team input"
        else:
            return "Detailed research, peer recommendations"

    def _identify_communication_style(self, icp: Dict[str, Any]) -> str:
        """Identify preferred communication style"""
        role = icp.get("role", "").lower()

        if role in ["executive", "ceo"]:
            return "Executive summaries, high-level metrics"
        elif role in ["technical", "developer"]:
            return "Technical documentation, code examples"
        else:
            return "Conversational, balanced detail"

    def _predict_objections(self, icp: Dict[str, Any]) -> List[str]:
        """Predict likely objections"""
        objections = []

        if icp.get("budget_level", "").lower() in ["low", "limited"]:
            objections.append("Cost concerns")

        if icp.get("experience_level", "").lower() == "beginner":
            objections.append("Implementation complexity")

        if icp.get("company_size", "").lower() == "enterprise":
            objections.append("Integration requirements")

        return objections if objections else ["No significant objections identified"]

    def _identify_activation_triggers(self, icp: Dict[str, Any]) -> List[str]:
        """Identify what triggers action from persona"""

        triggers = []
        pain_points = icp.get("pain_points", [])

        for pain in pain_points[:3]:
            triggers.append(f"Experiences {pain}")

        return triggers if triggers else ["Encountering relevant business challenge"]

    def _identify_customer_stage(self, icp: Dict[str, Any]) -> str:
        """Identify where in customer journey"""
        seniority = icp.get("seniority", "").lower()

        if seniority == "executive":
            return "Decision-maker / Influencer"
        elif seniority == "manager":
            return "Evaluator / Advocate"
        else:
            return "User / Implementer"

    def _find_common_items(self, personas: List[Dict], key: str) -> List[str]:
        """Find common items across personas"""
        if not personas:
            return []

        common = set(personas[0].get(key, []))
        for persona in personas[1:]:
            common = common.intersection(set(persona.get(key, [])))

        return list(common)

    def _find_common_platforms(self, personas: List[Dict]) -> List[str]:
        """Find common platforms across personas"""
        if not personas:
            return []

        all_platforms = [
            p.get("behavior", {}).get("top_platforms", []) for p in personas
        ]
        if not all_platforms:
            return []

        common = set(all_platforms[0])
        for platforms in all_platforms[1:]:
            common = common.intersection(set(platforms))

        return list(common)

    def _identify_differences(self, personas: List[Dict]) -> Dict[str, Any]:
        """Identify key differences between personas"""

        differences = {
            "by_role": list(set(p.get("role", "Unknown") for p in personas)),
            "by_seniority": list(set(p.get("seniority", "Unknown") for p in personas)),
            "unique_pain_points": {}
        }

        return differences


# Singleton instances
audience_matching = AudienceMatchingTool()
icp_persona_builder = ICPPersonaBuilder()
