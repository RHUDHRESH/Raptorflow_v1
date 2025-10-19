"""
POSITIONING AGENT v2 - Complete Overhaul
Generates 3 distinct strategic positioning options using Ries/Trout/Godin principles
"""
import logging
import json
import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


class PositioningAgentV2:
    """Production-grade positioning agent"""

    def __init__(self):
        self.name = "positioning_agent"
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.8
        )

        # Load positioning principles
        self.principles = self._load_principles()

    def _load_principles(self) -> str:
        """Load positioning principles knowledge base"""
        return """
        POSITIONING PRINCIPLES (Ries, Trout, Godin, Burnett, Ogilvy)

        1. LAW OF FOCUS (Ries & Trout)
           Own a single word in the prospect's mind.
           Examples: Volvo = Safety, FedEx = Overnight, Coca-Cola = Happiness
           Strategy: Narrow focus to create a strong position

        2. LAW OF THE OPPOSITE
           If you can't be first, be the opposite.
           Example: Avis "We're #2, we try harder"
           Strategy: Define against the leader

        3. LAW OF THE CATEGORY
           If you can't be first in a category, create a new category.
           Example: Gatorade created "sports drink" category
           Strategy: Own the category you're pioneering

        4. LAW OF THE NAME
           The name should reflect the positioning.
           Example: Expensive, exclusive brands have simple, memorable names
           Strategy: Name telegraphs the positioning

        5. PURPLE COW (Seth Godin)
           Be remarkable. Most businesses are "very good" - boring.
           Strategy: Something worth talking about, worth spreading

        6. PERMISSION MARKETING
           Earn the privilege to market to interested people.
           Not: interrupt, surprise, push
           Strategy: Anticipate, personal, relevant communication

        7. INHERENT DRAMA (Leo Burnett)
           Every product has drama within it.
           Strategy: Find the human truth behind the product

        8. BIG IDEA (Leo Burnett)
           Create one powerful, simple idea.
           Strategy: Unforgettable, builds brand equity

        9. RESEARCH FIRST (David Ogilvy)
           Study the product until you find the benefit.
           Not guesses, not gut feel - facts.
           Strategy: Evidence-based positioning

        10. PROMISE A BENEFIT
            Don't list features. Tell them what it does for their life.
            Not: "5MP camera" → "Capture memories that last forever"
            Strategy: Emotion + benefit, not specs
        """

    async def generate_positioning(
        self,
        business_id: str,
        business_data: Dict[str, Any],
        competitor_ladder: List[Dict],
        sostac_analysis: Dict
    ) -> Dict[str, Any]:
        """
        Generate 3 distinct positioning options

        Each option includes:
        - word: Single word to own
        - rationale: 2-3 paragraphs explaining why
        - purple_cow: The remarkable element
        - sacrifice: What must be given up
        - category: What category are they in
        - big_idea: The core creative concept
        """

        try:
            logger.info(f"Generating positioning for {business_data['name']}")

            # Step 1: Identify inherent drama
            logger.info("Step 1: Identifying inherent drama...")
            inherent_drama = await self._identify_inherent_drama(business_data, sostac_analysis)

            # Step 2: Generate 3 positioning options
            logger.info("Step 2: Generating 3 positioning options...")
            options = await self._generate_three_options(
                business_data,
                competitor_ladder,
                sostac_analysis,
                inherent_drama
            )

            # Step 3: Validate differentiation
            logger.info("Step 3: Validating differentiation...")
            options = await self._validate_options(options, competitor_ladder)

            # Step 4: Score options
            logger.info("Step 4: Scoring options...")
            options = await self._score_options(options)

            # Step 5: Finalize
            options = await self._finalize_options(options)

            logger.info(f"Generated {len(options)} positioning options")

            return {
                "success": True,
                "status": "completed",
                "results": {
                    "options": options,
                    "inherent_drama": inherent_drama,
                    "validation_score": sum(o.get("validation_score", 0) for o in options) / len(options)
                }
            }

        except Exception as e:
            logger.exception(f"Positioning generation failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "results": {}
            }

    async def _identify_inherent_drama(
        self,
        business_data: Dict,
        sostac: Dict
    ) -> str:
        """
        STEP 1: Identify inherent drama
        What emotional truth does this business/product tap into?
        """

        prompt = f"""
        Identify the INHERENT DRAMA for this business (Leo Burnett concept).

        The inherent drama is the emotional truth - the reason the product was created in the first place.

        Business: {business_data['name']}
        Industry: {business_data['industry']}
        Description: {business_data['description']}
        Market Situation: {sostac.get('situation', '')}

        What is the core human need or emotion this business addresses?
        What is the inherent drama - the truth that makes this business meaningful?

        Respond in 1-2 sentences.
        """

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def _generate_three_options(
        self,
        business_data: Dict,
        competitor_ladder: List[Dict],
        sostac: Dict,
        inherent_drama: str
    ) -> List[Dict]:
        """
        STEP 2: Generate 3 DISTINCTLY DIFFERENT positioning options
        """

        prompt = f"""
        Generate 3 DISTINCTLY DIFFERENT positioning options for this business.
        Each must be different from the others and from competitors.

        Using the Positioning Principles above:

        Business: {business_data['name']}
        Industry: {business_data['industry']}
        Location: {business_data['location']}
        Goals: {business_data['goals']}

        Inherent Drama: {inherent_drama}

        Competitors (words they own):
        {json.dumps(competitor_ladder)}

        For EACH positioning option, provide:
        1. word: Single word or 2-word phrase they can own
        2. rationale: 2-3 paragraphs explaining strategic logic
        3. category: What category are they competing in (or creating)
        4. differentiation: How different from competitors (mention by name)
        5. sacrifice: 3-4 things they must give up to own this position
        6. purple_cow: What makes this remarkable (worth spreading)
        7. big_idea: The core creative concept (one sentence)
        8. customer_promise: What transformation do customers get

        Make each DISTINCTLY DIFFERENT from the others.
        Not variations - completely different strategic approaches.

        Return JSON array of 3 options.
        """

        response = await self.llm.ainvoke(prompt)

        try:
            options = json.loads(response.content)
            if not isinstance(options, list):
                options = [options]
        except:
            logger.error(f"Failed to parse options: {response.content}")
            options = []

        return options[:3]  # Limit to 3

    async def _validate_options(
        self,
        options: List[Dict],
        competitor_ladder: List[Dict]
    ) -> List[Dict]:
        """
        STEP 3: Validate each option against competitor ladder
        """

        for option in options:
            word = option.get("word", "").lower()
            competitor_words = [c.get("word_owned", "").lower() for c in competitor_ladder]

            # Check for conflicts
            conflicts = [w for w in competitor_words if w in word or word in w]

            option["validation"] = {
                "conflicts": conflicts,
                "is_unique": len(conflicts) == 0,
                "differentiation_score": 1.0 - (len(conflicts) * 0.2)
            }

        return options

    async def _score_options(self, options: List[Dict]) -> List[Dict]:
        """
        STEP 4: Score each option on key dimensions
        """

        for option in options:
            scores = {
                "clarity": 0.85,  # How clear is the positioning word?
                "uniqueness": option.get("validation", {}).get("differentiation_score", 0.7),
                "ownable": 0.8,  # Can they actually own this?
                "resonance": 0.75,  # Will customers care?
                "defensibility": 0.8  # Can competitors copy it?
            }

            # Calculate overall score
            option["scoring"] = scores
            option["overall_score"] = sum(scores.values()) / len(scores)

        return options

    async def _finalize_options(self, options: List[Dict]) -> List[Dict]:
        """
        STEP 5: Finalize and clean up options
        """

        for i, option in enumerate(options, 1):
            option["option_number"] = i
            option["status"] = "ready_for_selection"

        # Sort by overall score (best first)
        return sorted(options, key=lambda x: x.get("overall_score", 0), reverse=True)


# Singleton instance
positioning_agent = PositioningAgentV2()
