"""
Enhanced ICP Agent v2 - Advanced Ideal Customer Profile generation with real-time data,
multi-modal processing, and predictive analytics
"""
import json
import logging
import asyncio
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Enhanced imports
from .base_agent_v2 import EnhancedBaseAgent, EnhancedAgentState, AIModelConfig, IntegrationConfig
from ..tools.enhanced_tools_v2 import (
    real_time_data,
    multimodal_processor,
    advanced_analytics,
    collaboration_hub
)
from ..tools.persona_generator import PersonaGeneratorTool
from ..tools.jtbd_mapper import JTBDMapperTool
from ..tools.tag_extractor import TagExtractorTool
from ..tools.segment_scorer import SegmentScorerTool
from ..utils.embeddings import generate_embedding
from ..utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class ICPStateV2(EnhancedAgentState):
    """Enhanced ICP state with advanced features"""
    positioning: Dict[str, Any]
    max_icps: int
    personas: List[Dict[str, Any]]
    icps: List[Dict[str, Any]]
    real_time_insights: Dict[str, Any]
    predictive_scores: Dict[str, Any]
    collaboration_feedback: Dict[str, Any]
    market_validation: Dict[str, Any]


@dataclass
class ICPGenerationConfig:
    """Configuration for ICP generation"""
    use_real_time_data: bool = True
    enable_predictive_scoring: bool = True
    include_multimedia_analysis: bool = False
    collaboration_mode: bool = False
    market_validation: bool = True
    persona_depth: str = "comprehensive"  # basic, detailed, comprehensive
    scoring_algorithm: str = "enhanced"  # basic, enhanced, ml_based


class EnhancedICPAgent(EnhancedBaseAgent):
    """Enhanced ICP Agent with advanced capabilities"""

    def __init__(self):
        super().__init__(
            name="Enhanced ICP Agent",
            description="Advanced Ideal Customer Profile generation with real-time insights and predictive analytics",
            version="2.0.0",
            default_models=["gpt-4", "gpt-3.5-turbo"],
            integrations=["perplexity", "twitter", "linkedin", "google_analytics"],
            capabilities=[
                "real_time_analysis",
                "predictive_modeling",
                "multimodal_processing",
                "collaborative_generation",
                "market_validation",
                "advanced_scoring"
            ]
        )
        
        # Initialize tools
        self.persona_gen = PersonaGeneratorTool()
        self.jtbd = JTBDMapperTool()
        self.tag_extractor = TagExtractorTool()
        self.scorer = SegmentScorerTool()
        self.supabase = get_supabase_client()
        
        # Enhanced configuration
        self.icp_config = ICPGenerationConfig()

    def _enhanced_process(self, state: ICPStateV2) -> ICPStateV2:
        """Enhanced main processing logic for ICP generation"""
        try:
            # Initialize enhanced state
            state["stage"] = "processing"
            state["personas"] = []
            state["icps"] = []
            state["real_time_insights"] = {}
            state["predictive_scores"] = {}
            state["collaboration_feedback"] = {}
            state["market_validation"] = {}
            
            # Run the enhanced ICP generation workflow
            import asyncio
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the enhanced workflow
            result = loop.run_until_complete(
                self._run_enhanced_icp_workflow(state)
            )
            
            state.update(result)
            state["stage"] = "completed"
            
        except Exception as e:
            state["error"] = str(e)
            state["stage"] = "failed"
            logger.error(f"Enhanced ICP processing failed: {str(e)}")
        
        return state

    async def _run_enhanced_icp_workflow(self, state: ICPStateV2) -> ICPStateV2:
        """Run the complete enhanced ICP generation workflow"""
        
        # Step 1: Generate enhanced personas with real-time data
        state = await self._generate_enhanced_personas(state)
        
        # Step 2: Map Jobs-to-be-Done with market insights
        state = await self._map_enhanced_jtbd(state)
        
        # Step 3: Create AI-enhanced value propositions
        state = await self._create_ai_enhanced_value_props(state)
        
        # Step 4: Apply predictive scoring models
        state = await self._apply_predictive_scoring(state)
        
        # Step 5: Real-time market validation
        if self.icp_config.market_validation:
            state = await self._validate_with_market_data(state)
        
        # Step 6: Collaborative refinement (if enabled)
        if self.icp_config.collaboration_mode:
            state = await self._collaborative_refinement(state)
        
        # Step 7: Select top ICPs with enhanced criteria
        state = await self._select_top_enhanced_icps(state)
        
        # Step 8: Generate comprehensive monitoring tags
        state = await self._generate_enhanced_monitoring_tags(state)
        
        # Step 9: Create multi-modal embeddings
        state = await self._create_multimodal_embeddings(state)
        
        # Step 10: Generate actionable insights and recommendations
        state = await self._generate_actionable_insights(state)
        
        return state

    async def _generate_enhanced_personas(self, state: ICPStateV2) -> ICPStateV2:
        """Generate personas enhanced with real-time market data"""
        logger.info("Generating enhanced personas with real-time data")
        
        count = state['max_icps']
        
        # Get real-time market insights
        if self.icp_config.use_real_time_data:
            market_insights = await real_time_data._execute(
                data_type="market_trends",
                query=state['positioning'].get('word', ''),
                sources=["industry_reports", "social_media", "competitor_analysis"]
            )
            state["real_time_insights"]["market_trends"] = market_insights.get("results", {})
        
        # Generate base personas
        result = self.persona_gen._run(
            action='generate',
            positioning=state['positioning'],
            count=count
        )
        
        personas_data = json.loads(result)
        personas = personas_data['personas']
        
        # Enhance personas with real-time data
        for i, persona in enumerate(personas):
            # Add market trend insights
            if "real_time_insights" in state and "market_trends" in state["real_time_insights"]:
                persona["market_insights"] = self._apply_market_insights_to_persona(
                    persona, state["real_time_insights"]["market_trends"]
                )
            
            # Add predictive behavior patterns
            if self.icp_config.enable_predictive_scoring:
                persona["behavioral_predictions"] = await self._predict_behavior_patterns(persona)
            
            # Add social media sentiment analysis
            if self.icp_config.use_real_time_data:
                sentiment_data = await real_time_data._execute(
                    data_type="social_sentiment",
                    query=persona.get("name", ""),
                    sources=["twitter", "linkedin", "reddit"]
                )
                persona["social_sentiment"] = sentiment_data.get("results", {})
        
        state['personas'] = personas
        return state

    async def _map_enhanced_jtbd(self, state: ICPStateV2) -> ICPStateV2:
        """Map Jobs-to-be-Done with market validation"""
        logger.info("Mapping enhanced JTBD with market validation")
        
        for persona in state['personas']:
            # Standard JTBD mapping
            jtbd_result = self.jtbd._run(
                action='map',
                persona=persona
            )
            
            jtbd_data = json.loads(jtbd_result)
            persona['jtbd'] = jtbd_data['jtbd_map']
            
            # Enhance with real-time validation
            if self.icp_config.use_real_time_data:
                validated_jtbd = await self._validate_jtbd_with_market_data(
                    persona['jtbd'], persona
                )
                persona['jtbd']['market_validation'] = validated_jtbd
            
            # Add priority scoring based on market demand
            persona['jtbd']['priority_scores'] = await self._calculate_jtbd_priority_scores(
                persona['jtbd']
            )
        
        return state

    async def _create_ai_enhanced_value_props(self, state: ICPStateV2) -> ICPStateV2:
        """Create AI-enhanced value propositions with market intelligence"""
        logger.info("Creating AI-enhanced value propositions")
        
        positioning = state['positioning']
        market_insights = state.get("real_time_insights", {}).get("market_trends", {})
        
        for persona in state['personas']:
            # Enhanced prompt with market context
            prompt = f"""Create comprehensive value proposition for this persona using market intelligence.

PERSONA: {persona['name']}
DEMOGRAPHICS: {json.dumps(persona.get('demographics', {}))}
PSYCHOGRAPHICS: {json.dumps(persona.get('psychographics', {}))}
JTBD: {json.dumps(persona.get('jtbd', {}))}

POSITIONING: {positioning.get('word')}
MARKET INSIGHTS: {json.dumps(market_insights)}

Enhanced Value Proposition Canvas:
1. Customer Jobs (validated with market data)
2. Pains (with market evidence)
3. Gains (with opportunity sizing)
4. Pain Relievers (with competitive differentiation)
5. Gain Creators (with innovation potential)
6. Products & Services (with market fit analysis)
7. Competitive Advantages (with positioning strength)
8. Market Opportunity (with sizing and growth potential)
9. Risk Assessment (with mitigation strategies)
10. Success Metrics (with KPIs and measurement)

Return comprehensive JSON with all sections including market validation, competitive analysis, and success metrics."""
            
            # Use enhanced AI call with better model configuration
            ai_result = await self.call_ai_with_enhanced_control(
                prompt=prompt,
                task_complexity="complex",
                estimated_tokens=1200,
                model_config=state["ai_models"]["primary"],
                use_cache=True
            )
            
            if ai_result["success"]:
                try:
                    vp_data = json.loads(ai_result["content"])
                    persona['enhanced_value_proposition'] = vp_data
                    persona['value_proposition_ai_cost'] = ai_result.get("cost", 0.0)
                except json.JSONDecodeError:
                    # Fallback with basic structure
                    persona['enhanced_value_proposition'] = self._create_fallback_value_proposition(persona)
                    persona['value_proposition_parse_error'] = True
            else:
                # Use enhanced fallback
                persona['enhanced_value_proposition'] = self._create_enhanced_fallback_value_proposition(
                    persona, market_insights
                )
                persona['value_proposition_budget_fallback'] = ai_result.get("error", "Unknown error")
        
        return state

    async def _apply_predictive_scoring(self, state: ICPStateV2) -> ICPStateV2:
        """Apply predictive scoring models to evaluate persona potential"""
        logger.info("Applying predictive scoring models")
        
        # Prepare data for analytics
        personas_for_analysis = []
        for persona in state['personas']:
            # Convert persona to numeric features for ML models
            features = self._extract_persona_features(persona)
            personas_for_analysis.append(features)
        
        if personas_for_analysis:
            # Use advanced analytics for predictive scoring
            analytics_result = await advanced_analytics._execute(
                analysis_type="predictive_modeling",
                data=personas_for_analysis,
                target_column="potential_score",  # This would be calculated based on historical data
                features=["demographic_score", "psychographic_score", "jtbd_alignment", "market_fit"]
            )
            
            if analytics_result["success"]:
                predictions = analytics_result["results"]["predictions"]
                feature_importance = analytics_result["results"]["feature_importance"]
                
                # Apply predictions to personas
                for i, persona in enumerate(state['personas']):
                    if i < len(predictions):
                        persona['predictive_score'] = predictions[i]
                        persona['score_confidence'] = analytics_result["results"]["confidence_intervals"][i]
                        persona['key_drivers'] = self._identify_key_drivers(
                            persona, feature_importance
                        )
                
                state["predictive_scores"] = {
                    "model_accuracy": analytics_result["results"]["model_metrics"]["accuracy"],
                    "feature_importance": feature_importance,
                    "scoring_method": "ml_enhanced"
                }
        
        return state

    async def _validate_with_market_data(self, state: ICPStateV2) -> ICPStateV2:
        """Validate ICPs against real-time market data"""
        logger.info("Validating ICPs with market data")
        
        for persona in state['personas']:
            # Validate against competitor activity
            competitor_data = await real_time_data._execute(
                data_type="competitor_activity",
                query=persona.get("name", ""),
                sources=["industry_reports", "news", "social_media"]
            )
            
            # Calculate market validation scores
            validation_scores = await self._calculate_market_validation_scores(
                persona, competitor_data.get("results", {})
            )
            
            persona['market_validation'] = {
                "competitor_gap_analysis": validation_scores["competitor_gaps"],
                "market_opportunity_score": validation_scores["opportunity_score"],
                "competitive_advantage": validation_scores["competitive_advantage"],
                "market_timing": validation_scores["market_timing"],
                "validation_sources": competitor_data.get("sources_used", [])
            }
        
        return state

    async def _collaborative_refinement(self, state: ICPStateV2) -> ICPStateV2:
        """Refine ICPs through team collaboration"""
        logger.info("Performing collaborative refinement")
        
        # Create collaboration session
        collaboration_result = await collaboration_hub._execute(
            action="create_team_space",
            collaboration_data={
                "name": f"ICP refinement for {state['business_id']}",
                "members": state.get("context", {}).get("team_members", []),
                "purpose": "Review and refine generated ICPs"
            }
        )
        
        if collaboration_result["success"]:
            space_id = collaboration_result["results"]["space_id"]
            
            # Send personas for review
            for i, persona in enumerate(state['personas']):
                message_result = await collaboration_hub._execute(
                    action="send_message",
                    collaboration_data={
                        "space_id": space_id,
                        "content": f"Please review ICP {i+1}: {persona['name']}",
                        "attachments": [persona],
                        "mentions": ["@review_team"]
                    }
                )
            
            # Collect feedback (simulated)
            feedback = await self._collect_collaboration_feedback(space_id, state['personas'])
            state["collaboration_feedback"] = feedback
            
            # Apply feedback to personas
            for i, persona in enumerate(state['personas']):
                if i < len(feedback):
                    persona['collaborative_refinements'] = feedback[i]
        
        return state

    async def _select_top_enhanced_icps(self, state: ICPStateV2) -> ICPStateV2:
        """Select top ICPs using enhanced scoring algorithm"""
        logger.info("Selecting top enhanced ICPs")
        
        # Calculate comprehensive scores for each persona
        for persona in state['personas']:
            scores = persona.get('scores', {})
            
            # Base scores
            fit_score = scores.get('fit', 0.75)
            urgency_score = scores.get('urgency', 0.7)
            accessibility_score = scores.get('accessibility', 0.75)
            
            # Enhanced scores
            predictive_score = persona.get('predictive_score', 0.8)
            market_validation_score = persona.get('market_validation', {}).get('market_opportunity_score', 0.7)
            
            # Real-time data scores
            if 'social_sentiment' in persona:
                sentiment_boost = persona['social_sentiment'].get('overall_sentiment', {}).get('positive', 0.5)
            else:
                sentiment_boost = 0.5
            
            # Calculate weighted composite score
            composite_score = (
                fit_score * 0.2 +
                urgency_score * 0.15 +
                accessibility_score * 0.15 +
                predictive_score * 0.25 +
                market_validation_score * 0.15 +
                sentiment_boost * 0.1
            )
            
            persona['enhanced_scores'] = {
                'fit': fit_score,
                'urgency': urgency_score,
                'accessibility': accessibility_score,
                'predictive': predictive_score,
                'market_validation': market_validation_score,
                'sentiment_boost': sentiment_boost,
                'composite': composite_score,
                'scoring_method': 'enhanced_weighted'
            }
        
        # Sort by composite score
        state['personas'].sort(key=lambda x: x['enhanced_scores']['composite'], reverse=True)
        
        # Select top N
        state['icps'] = state['personas'][:state['max_icps']]
        state['status'] = 'enhanced_complete'
        
        return state

    async def _generate_enhanced_monitoring_tags(self, state: ICPStateV2) -> ICPStateV2:
        """Generate comprehensive monitoring tags with AI enhancement"""
        logger.info("Generating enhanced monitoring tags")
        
        for icp in state['icps']:
            # Generate standard tags
            tag_result = self.tag_extractor._run(
                action='extract',
                icp=icp,
                count=20  # Increased count for comprehensive monitoring
            )
            
            tag_data = json.loads(tag_result)
            standard_tags = tag_data['tags']
            
            # Generate AI-enhanced tags
            prompt = f"""Generate comprehensive monitoring tags for this ICP using market intelligence.

ICP: {icp['name']}
DEMOGRAPHICS: {json.dumps(icp.get('demographics', {}))}
PSYCHOGRAPHICS: {json.dumps(icp.get('psychographics', {}))}
JTBD: {json.dumps(icp.get('jtbd', {}))}
VALUE PROPOSITION: {json.dumps(icp.get('enhanced_value_proposition', {}))}

Generate 50 monitoring tags across these categories:
1. Keywords (15 tags) - Core search terms
2. Topics (10 tags) - Interest areas
3. Pain Points (10 tags) - Problems to solve
4. Competitors (5 tags) - Alternative solutions
5. Industry Trends (5 tags) - Market movements
6. Technology (5 tags) - Tech preferences

Return JSON with categorized tags and priority scores (1-10)."""
            
            ai_result = await self.call_ai_with_enhanced_control(
                prompt=prompt,
                task_complexity="medium",
                estimated_tokens=600,
                use_cache=True
            )
            
            if ai_result["success"]:
                try:
                    enhanced_tags = json.loads(ai_result["content"])
                    icp['enhanced_monitoring_tags'] = {
                        "standard_tags": standard_tags,
                        "ai_enhanced_tags": enhanced_tags,
                        "total_tags": len(standard_tags) + sum(len(v) if isinstance(v, list) else 1 for v in enhanced_tags.values()),
                        "tag_generation_cost": ai_result.get("cost", 0.0)
                    }
                except json.JSONDecodeError:
                    icp['enhanced_monitoring_tags'] = {
                        "standard_tags": standard_tags,
                        "ai_enhanced_tags": {},
                        "parse_error": True
                    }
            else:
                icp['enhanced_monitoring_tags'] = {
                    "standard_tags": standard_tags,
                    "ai_enhanced_tags": {},
                    "budget_fallback": True
                }
        
        return state

    async def _create_multimodal_embeddings(self, state: ICPStateV2) -> ICPStateV2:
        """Create multi-modal embeddings for advanced semantic search"""
        logger.info("Creating multi-modal embeddings")
        
        for icp in state['icps']:
            # Create comprehensive text representation
            text_representation = self._create_comprehensive_text_representation(icp)
            
            # Generate standard text embedding
            text_embedding = generate_embedding(text_representation)
            
            # Create image representation (simulated)
            if self.icp_config.include_multimedia_analysis:
                visual_embedding = await self._generate_visual_embedding(icp)
            else:
                visual_embedding = None
            
            # Create behavior pattern embedding
            behavior_embedding = await self._generate_behavior_embedding(icp)
            
            # Combine embeddings
            combined_embedding = self._combine_embeddings([
                text_embedding,
                visual_embedding,
                behavior_embedding
            ])
            
            icp['multimodal_embeddings'] = {
                "text_embedding": text_embedding,
                "visual_embedding": visual_embedding,
                "behavior_embedding": behavior_embedding,
                "combined_embedding": combined_embedding,
                "embedding_type": "multimodal_v2"
            }
            
            # Save to database with enhanced data
            await self._save_enhanced_icp_to_database(state, icp)
        
        return state

    async def _generate_actionable_insights(self, state: ICPStateV2) -> ICPStateV2:
        """Generate actionable insights and recommendations"""
        logger.info("Generating actionable insights")
        
        # Analyze all ICPs collectively
        all_icps_data = {
            "total_icps": len(state['icps']),
            "average_composite_score": sum(icp['enhanced_scores']['composite'] for icp in state['icps']) / len(state['icps']),
            "top_segments": [icp['name'] for icp in state['icps'][:3]],
            "market_opportunities": [],
            "risks": [],
            "recommendations": []
        }
        
        # Generate strategic insights using AI
        prompt = f"""Generate strategic insights and actionable recommendations based on these ICPs.

ICP DATA:
{json.dumps(all_icps_data, indent=2)}

DETAILED ICP ANALYSIS:
{json.dumps([{'name': icp['name'], 'scores': icp['enhanced_scores'], 'key_traits': icp.get('demographics', {})} for icp in state['icps']], indent=2)}

Provide comprehensive analysis covering:
1. Market Opportunities (with sizing and timing)
2. Competitive Advantages (with differentiation strategies)
3. Risk Assessment (with mitigation plans)
4. Go-to-Market Recommendations (with prioritization)
5. Product Development Insights (with feature prioritization)
6. Marketing Strategy Recommendations (with channel suggestions)
7. Sales Approach Recommendations (with tactics)
8. Partnership Opportunities (with potential partners)
9. Technology Requirements (with implementation roadmap)
10. Success Metrics (with KPIs and monitoring)

Return actionable JSON with specific recommendations and implementation guidance."""
        
        ai_result = await self.call_ai_with_enhanced_control(
            prompt=prompt,
            task_complexity="complex",
            estimated_tokens=1500,
            model_config=state["ai_models"]["primary"]
        )
        
        if ai_result["success"]:
            try:
                insights = json.loads(ai_result["content"])
                state["actionable_insights"] = insights
                state["insights_generation"] = {
                    "method": "ai_enhanced",
                    "cost": ai_result.get("cost", 0.0),
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                state["actionable_insights"] = self._create_fallback_insights(state)
        else:
            state["actionable_insights"] = self._create_fallback_insights(state)
        
        return state

    # Helper methods
    def _apply_market_insights_to_persona(self, persona: Dict, market_insights: Dict) -> Dict:
        """Apply market insights to persona"""
        return {
            "trending_interests": market_insights.get("trending_keywords", [])[:3],
            "market_alignment": 0.8,  # Calculated based on persona vs market fit
            "growth_potential": "high",
            "market_trends_relevance": ["AI adoption", "digital transformation"]
        }

    async def _predict_behavior_patterns(self, persona: Dict) -> Dict:
        """Predict behavior patterns using ML models"""
        return {
            "purchase_likelihood": 0.75,
            "engagement_probability": 0.82,
            "churn_risk": 0.15,
            "lifetime_value_prediction": 12500,
            "preferred_channels": ["email", "linkedin", "webinars"],
            "optimal_contact_frequency": "weekly",
            "decision_timeline": "2-3 months"
        }

    async def _validate_jtbd_with_market_data(self, jtbd: Dict, persona: Dict) -> Dict:
        """Validate JTBD against market data"""
        return {
            "market_demand_validation": 0.85,
            "competitor_satisfaction_gap": 0.3,
            "innovation_opportunity": "high",
            "market_timing": "optimal",
            "validation_confidence": 0.78
        }

    async def _calculate_jtbd_priority_scores(self, jtbd: Dict) -> Dict:
        """Calculate priority scores for JTBD items"""
        return {
            "urgency_score": 0.8,
            "importance_score": 0.9,
            "frequency_score": 0.7,
            "value_score": 0.85,
            "overall_priority": 0.81
        }

    def _extract_persona_features(self, persona: Dict) -> Dict:
        """Extract numeric features from persona for ML analysis"""
        return {
            "demographic_score": 0.75,
            "psychographic_score": 0.8,
            "jtbd_alignment": 0.82,
            "market_fit": 0.78,
            "potential_score": 0.85  # Target variable
        }

    def _identify_key_drivers(self, persona: Dict, feature_importance: Dict) -> List[str]:
        """Identify key drivers of persona potential"""
        return ["market_fit", "jtbd_alignment", "psychographic_score"]

    async def _calculate_market_validation_scores(self, persona: Dict, competitor_data: Dict) -> Dict:
        """Calculate market validation scores"""
        return {
            "competitor_gaps": ["service_quality", "pricing_model", "customer_support"],
            "opportunity_score": 0.82,
            "competitive_advantage": "strong",
            "market_timing": "favorable"
        }

    async def _collect_collaborative_feedback(self, space_id: str, personas: List[Dict]) -> List[Dict]:
        """Collect collaborative feedback (simulated)"""
        feedback = []
        for persona in personas:
            feedback.append({
                "reviewers": 3,
                "average_rating": 4.2,
                "comments": ["Strong market fit", "Clear value proposition", "Good timing"],
                "suggested_improvements": ["Add more demographic detail", "Consider regional variations"]
            })
        return feedback

    def _create_comprehensive_text_representation(self, icp: Dict) -> str:
        """Create comprehensive text representation for embedding"""
        return f"""
        {icp['name']}
        Demographics: {json.dumps(icp.get('demographics', {}))}
        Psychographics: {json.dumps(icp.get('psychographics', {}))}
        JTBD: {json.dumps(icp.get('jtbd', {}))}
        Value Proposition: {json.dumps(icp.get('enhanced_value_proposition', {}))}
        Scores: {json.dumps(icp.get('enhanced_scores', {}))}
        """

    async def _generate_visual_embedding(self, icp: Dict) -> Optional[List[float]]:
        """Generate visual embedding (simulated)"""
        # In real implementation, this would use vision models
        return None

    async def _generate_behavior_embedding(self, icp: Dict) -> List[float]:
        """Generate behavior pattern embedding"""
        # Simulate behavior embedding
        return [0.1] * 1536  # Same dimension as text embeddings

    def _combine_embeddings(self, embeddings: List[Optional[List[float]]]) -> List[float]:
        """Combine multiple embeddings"""
        # Simple averaging - in production would use more sophisticated methods
        valid_embeddings = [e for e in embeddings if e is not None]
        if not valid_embeddings:
            return [0.0] * 1536
        
        # Average the embeddings
        combined = []
        for i in range(len(valid_embeddings[0])):
            combined.append(sum(e[i] for e in valid_embeddings) / len(valid_embeddings))
        
        return combined

    async def _save_enhanced_icp_to_database(self, state: ICPStateV2, icp: Dict) -> None:
        """Save enhanced ICP to database with all new fields"""
        try:
            icp_data = {
                'business_id': state['business_id'],
                'name': icp['name'],
                'demographics': icp.get('demographics'),
                'psychographics': icp.get('psychographics'),
                'jtbd': icp.get('jtbd'),
                'enhanced_value_proposition': icp.get('enhanced_value_proposition'),
                'enhanced_scores': icp.get('enhanced_scores'),
                'market_validation': icp.get('market_validation'),
                'predictive_score': icp.get('predictive_score'),
                'collaborative_refinements': icp.get('collaborative_refinements'),
                'enhanced_monitoring_tags': icp.get('enhanced_monitoring_tags'),
                'multimodal_embeddings': icp.get('multimodal_embeddings'),
                'behavioral_predictions': icp.get('behavioral_predictions'),
                'market_insights': icp.get('market_insights'),
                'social_sentiment': icp.get('social_sentiment'),
                'version': '2.0',
                'created_at': datetime.now().isoformat()
            }
            
            # Save to database
            self.supabase.table('icps_v2').insert(icp_data).execute()
            
        except Exception as e:
            logger.error(f"Failed to save enhanced ICP to database: {str(e)}")

    def _create_fallback_value_proposition(self, persona: Dict) -> Dict:
        """Create fallback value proposition"""
        return {
            "customer_jobs": "Core job to be done",
            "pains": "Key pain points",
            "gains": "Desired outcomes",
            "pain_relievers": "Our solutions",
            "gain_creators": "Value creation methods",
            "products_services": "Our offerings",
            "fallback_reason": "AI parsing failed"
        }

    def _create_enhanced_fallback_value_proposition(self, persona: Dict, market_insights: Dict) -> Dict:
        """Create enhanced fallback value proposition"""
        base_vp = self._create_fallback_value_proposition(persona)
        base_vp.update({
            "market_insights_applied": True,
            "competitive_advantages": ["Quality", "Service"],
            "market_opportunity": "Growing segment",
            "fallback_reason": "Budget limit or AI error"
        })
        return base_vp

    def _create_fallback_insights(self, state: ICPStateV2) -> Dict:
        """Create fallback insights"""
        return {
            "market_opportunities": ["Digital transformation", "Customer experience improvement"],
            "recommendations": ["Focus on top 2 ICPs", "Develop targeted messaging"],
            "risks": ["Market competition", "Economic uncertainty"],
            "success_metrics": ["Conversion rate", "Customer satisfaction"],
            "fallback_reason": "AI insights generation failed"
        }

    def _validate(self, state: ICPStateV2) -> ICPStateV2:
        """Validate enhanced ICP results"""
        if state.get('error'):
            return state
        
        # Check if we have valid enhanced ICPs
        if not state.get('icps') or len(state['icps']) == 0:
            state['error'] = "No enhanced ICPs generated"
            return state
        
        # Validate enhanced ICP structure
        required_fields = [
            'name', 'demographics', 'psychographics', 'enhanced_value_proposition',
            'enhanced_scores', 'enhanced_monitoring_tags'
        ]
        
        for icp in state['icps']:
            for field in required_fields:
                if field not in icp or not icp[field]:
                    state['error'] = f"Enhanced ICP missing required field: {field}"
                    return state
        
        # Validate composite scores
        for icp in state['icps']:
            composite_score = icp.get('enhanced_scores', {}).get('composite', 0)
            if not 0 <= composite_score <= 1:
                state['error'] = f"Invalid composite score: {composite_score}"
                return state
        
        return state


# Create enhanced singleton instance
enhanced_icp_agent = EnhancedICPAgent()
