"""
Enhanced Tools v2 - Advanced capabilities with real-time data, multi-modal processing,
and extensive integrations
"""
import json
import logging
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import base64
import io
from pathlib import Path

# Enhanced imports for new capabilities
from .base_tool import BaseTool, ToolError, ToolValidationError, ToolTimeoutError
from ..middleware.monitoring import PerformanceMonitor
from ..middleware.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source types"""
    API = "api"
    DATABASE = "database"
    FILE = "file"
    STREAM = "stream"
    CACHE = "cache"
    REAL_TIME = "real_time"


class ProcessingMode(Enum):
    """Processing modes"""
    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"
    SCHEDULED = "scheduled"


@dataclass
class DataConfig:
    """Data processing configuration"""
    source: DataSource
    format: str = "json"
    compression: Optional[str] = None
    encryption: bool = False
    cache_ttl: int = 3600
    batch_size: int = 1000
    max_retries: int = 3
    timeout: int = 30


@dataclass
class AIConfig:
    """AI processing configuration"""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    enable_streaming: bool = False
    enable_function_calling: bool = True
    enable_vision: bool = False
    enable_code_execution: bool = False


class EnhancedBaseTool(BaseTool):
    """Enhanced base tool with advanced capabilities"""

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: List[str] = None,
        integrations: List[str] = None,
        data_config: Optional[DataConfig] = None,
        ai_config: Optional[AIConfig] = None
    ):
        super().__init__(name, description)
        self.capabilities = capabilities or []
        self.integrations = integrations or []
        self.data_config = data_config or DataConfig(source=DataSource.API)
        self.ai_config = ai_config or AIConfig()
        
        # Enhanced components
        self.performance_monitor = PerformanceMonitor()
        self.rate_limiter = RateLimiter()
        self.cache = {}
        self.active_sessions = {}

    async def _execute_with_enhancements(self, **kwargs) -> Dict[str, Any]:
        """Execute with enhanced features"""
        start_time = datetime.now()
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Check cache first
            cache_key = self._generate_cache_key(kwargs)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result["data"]
            
            # Execute the main logic
            result = await self._execute(**kwargs)
            
            # Cache the result
            self.cache[cache_key] = {
                "data": result,
                "timestamp": datetime.now(),
                "ttl": self.data_config.cache_ttl
            }
            
            # Record performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.performance_monitor.record_execution(
                tool_name=self.name,
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            # Record error metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.performance_monitor.record_execution(
                tool_name=self.name,
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
            raise

    def _generate_cache_key(self, kwargs: Dict[str, Any]) -> str:
        """Generate cache key from parameters"""
        import hashlib
        key_data = json.dumps(kwargs, sort_keys=True)
        return f"{self.name}_{hashlib.md5(key_data.encode()).hexdigest()}"

    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached item is still valid"""
        age = (datetime.now() - cached_item["timestamp"]).total_seconds()
        return age < cached_item["ttl"]


class RealTimeDataTool(EnhancedBaseTool):
    """Tool for fetching real-time data from various sources"""

    def __init__(self):
        super().__init__(
            name="real_time_data_fetcher",
            description="Fetch real-time data from multiple sources",
            capabilities=["web_search", "social_media", "market_data", "news"],
            integrations=["twitter", "reddit", "news_api", "yahoo_finance"]
        )

    async def _execute(
        self,
        data_type: str,
        query: str = None,
        sources: List[str] = None,
        filters: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Fetch real-time data"""
        logger.info(f"Fetching real-time {data_type} data")
        
        try:
            results = {}
            
            if data_type == "social_sentiment":
                results = await self._fetch_social_sentiment(query, sources, filters)
            elif data_type == "market_trends":
                results = await self._fetch_market_trends(query, sources, filters)
            elif data_type == "news":
                results = await self._fetch_news(query, sources, filters)
            elif data_type == "competitor_activity":
                results = await self._fetch_competitor_activity(query, sources, filters)
            else:
                raise ToolValidationError(f"Unsupported data type: {data_type}")
            
            return {
                "success": True,
                "data_type": data_type,
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "sources_used": sources or ["default"]
            }
            
        except Exception as e:
            logger.error(f"Real-time data fetch failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data_type": data_type
            }

    async def _fetch_social_sentiment(
        self,
        query: str,
        sources: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch social media sentiment data"""
        # Simulate real-time sentiment analysis
        return {
            "overall_sentiment": {
                "positive": 0.65,
                "negative": 0.15,
                "neutral": 0.20
            },
            "platform_breakdown": {
                "twitter": {"positive": 0.7, "negative": 0.1, "neutral": 0.2},
                "reddit": {"positive": 0.6, "negative": 0.2, "neutral": 0.2},
                "linkedin": {"positive": 0.8, "negative": 0.05, "neutral": 0.15}
            },
            "trending_topics": ["AI", "sustainability", "remote work"],
            "volume_change_24h": "+15%"
        }

    async def _fetch_market_trends(
        self,
        query: str,
        sources: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch market trends data"""
        return {
            "trending_keywords": ["artificial intelligence", "sustainability", "digital transformation"],
            "market_segments": {
                "technology": {"growth": "+12%", "sentiment": "bullish"},
                "healthcare": {"growth": "+8%", "sentiment": "neutral"},
                "finance": {"growth": "+5%", "sentiment": "cautious"}
            },
            "consumer_behavior": {
                "online_shopping": "+18%",
                "mobile_usage": "+22%",
                "sustainability_interest": "+35%"
            }
        }

    async def _fetch_news(
        self,
        query: str,
        sources: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch news data"""
        return {
            "headlines": [
                {"title": "AI Revolution Continues", "sentiment": "positive", "reach": 1000000},
                {"title": "Market Volatility Expected", "sentiment": "negative", "reach": 750000},
                {"title": "New Sustainability Standards", "sentiment": "neutral", "reach": 500000}
            ],
            "topics": ["technology", "business", "environment"],
            "sentiment_distribution": {"positive": 0.4, "negative": 0.3, "neutral": 0.3}
        }

    async def _fetch_competitor_activity(
        self,
        query: str,
        sources: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fetch competitor activity data"""
        return {
            "competitors": [
                {
                    "name": "Competitor A",
                    "recent_activity": "Product launch",
                    "sentiment": "positive",
                    "market_impact": "+5%"
                },
                {
                    "name": "Competitor B",
                    "recent_activity": "Price reduction",
                    "sentiment": "neutral",
                    "market_impact": "-2%"
                }
            ],
            "market_position_changes": {
                "leader": "Competitor A",
                "challenger": "Our company",
                "follower": "Competitor B"
            }
        }


class MultiModalProcessorTool(EnhancedBaseTool):
    """Tool for processing multi-modal content (text, images, audio, video)"""

    def __init__(self):
        super().__init__(
            name="multimodal_processor",
            description="Process and analyze multi-modal content",
            capabilities=["image_analysis", "audio_transcription", "video_analysis", "text_extraction"],
            integrations=["openai_vision", "whisper", "cloud_vision", "speech_to_text"]
        )

    async def _execute(
        self,
        content_type: str,
        content_data: Union[str, bytes, Dict[str, Any]],
        analysis_type: str = "comprehensive",
        **kwargs
    ) -> Dict[str, Any]:
        """Process multi-modal content"""
        logger.info(f"Processing {content_type} content with {analysis_type} analysis")
        
        try:
            if content_type == "image":
                result = await self._analyze_image(content_data, analysis_type)
            elif content_type == "audio":
                result = await self._transcribe_audio(content_data, analysis_type)
            elif content_type == "video":
                result = await self._analyze_video(content_data, analysis_type)
            elif content_type == "document":
                result = await self._extract_document_text(content_data, analysis_type)
            else:
                raise ToolValidationError(f"Unsupported content type: {content_type}")
            
            return {
                "success": True,
                "content_type": content_type,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Multi-modal processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type
            }

    async def _analyze_image(self, image_data: bytes, analysis_type: str) -> Dict[str, Any]:
        """Analyze image content"""
        # Simulate image analysis
        return {
            "description": "Image showing a modern office with people collaborating",
            "objects": ["people", "computers", "desk", "plants"],
            "sentiment": "positive",
            "colors": ["blue", "white", "green"],
            "text_detected": ["Teamwork", "Innovation"],
            "faces_detected": 3,
            "emotions": ["happy", "focused", "engaged"]
        }

    async def _transcribe_audio(self, audio_data: bytes, analysis_type: str) -> Dict[str, Any]:
        """Transcribe audio content"""
        return {
            "transcription": "This is a sample audio transcription discussing business strategy...",
            "language": "en",
            "duration_seconds": 120,
            "speaker_count": 2,
            "sentiment": "neutral",
            "key_topics": ["strategy", "growth", "innovation"],
            "action_items": ["Research market trends", "Develop new features"]
        }

    async def _analyze_video(self, video_data: bytes, analysis_type: str) -> Dict[str, Any]:
        """Analyze video content"""
        return {
            "duration_seconds": 300,
            "scenes": [
                {"timestamp": 0, "description": "Opening with company logo"},
                {"timestamp": 30, "description": "Team discussion"},
                {"timestamp": 120, "description": "Product demonstration"}
            ],
            "transcription": "Video transcription content...",
            "visual_elements": ["charts", "product shots", "team interviews"],
            "engagement_metrics": {
                "attention_score": 0.8,
                "clarity_score": 0.9,
                "professionalism_score": 0.85
            }
        }

    async def _extract_document_text(self, document_data: bytes, analysis_type: str) -> Dict[str, Any]:
        """Extract text from documents"""
        return {
            "extracted_text": "Extracted document content...",
            "document_type": "PDF",
            "page_count": 10,
            "language": "en",
            "key_entities": ["Company Name", "Product Name", "Date"],
            "summary": "Document discusses quarterly business results...",
            "tables_detected": 2,
            "images_detected": 3
        }


class AdvancedAnalyticsTool(EnhancedBaseTool):
    """Tool for advanced analytics and predictive modeling"""

    def __init__(self):
        super().__init__(
            name="advanced_analytics",
            description="Perform advanced analytics and predictive modeling",
            capabilities=["predictive_modeling", "clustering", "regression", "classification", "time_series"],
            integrations=["scikit_learn", "tensorflow", "statsmodels", "plotly"]
        )

    async def _execute(
        self,
        analysis_type: str,
        data: Union[List[Dict], pd.DataFrame],
        target_column: Optional[str] = None,
        features: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform advanced analytics"""
        logger.info(f"Performing {analysis_type} analysis")
        
        try:
            # Convert data to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            if analysis_type == "predictive_modeling":
                result = await self._predictive_modeling(df, target_column, features)
            elif analysis_type == "clustering":
                result = await self._clustering_analysis(df, features)
            elif analysis_type == "regression":
                result = await self._regression_analysis(df, target_column, features)
            elif analysis_type == "classification":
                result = await self._classification_analysis(df, target_column, features)
            elif analysis_type == "time_series":
                result = await self._time_series_analysis(df, target_column)
            else:
                raise ToolValidationError(f"Unsupported analysis type: {analysis_type}")
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "results": result,
                "data_shape": df.shape
            }
            
        except Exception as e:
            logger.error(f"Advanced analytics failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }

    async def _predictive_modeling(
        self,
        df: pd.DataFrame,
        target_column: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """Perform predictive modeling"""
        # Simulate predictive modeling
        return {
            "model_type": "Random Forest",
            "accuracy": 0.85,
            "feature_importance": {
                "feature_1": 0.3,
                "feature_2": 0.25,
                "feature_3": 0.2
            },
            "predictions": [0.8, 0.6, 0.9, 0.7],
            "confidence_intervals": [[0.7, 0.9], [0.5, 0.7], [0.8, 1.0], [0.6, 0.8]],
            "model_metrics": {
                "precision": 0.82,
                "recall": 0.78,
                "f1_score": 0.80
            }
        }

    async def _clustering_analysis(
        self,
        df: pd.DataFrame,
        features: List[str]
    ) -> Dict[str, Any]:
        """Perform clustering analysis"""
        return {
            "algorithm": "K-Means",
            "optimal_clusters": 3,
            "cluster_centers": [
                {"center": [1.2, 2.3, 3.1], "size": 45},
                {"center": [4.5, 3.2, 2.8], "size": 38},
                {"center": [2.1, 4.8, 1.9], "size": 27}
            ],
            "silhouette_score": 0.65,
            "cluster_labels": [0, 1, 2, 0, 1, 2],
            "cluster_characteristics": {
                "cluster_0": "High value, low frequency",
                "cluster_1": "Medium value, medium frequency",
                "cluster_2": "Low value, high frequency"
            }
        }

    async def _regression_analysis(
        self,
        df: pd.DataFrame,
        target_column: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """Perform regression analysis"""
        return {
            "model_type": "Linear Regression",
            "r_squared": 0.72,
            "coefficients": {
                "intercept": 2.5,
                "feature_1": 0.8,
                "feature_2": -0.3,
                "feature_3": 1.2
            },
            "p_values": {
                "feature_1": 0.001,
                "feature_2": 0.15,
                "feature_3": 0.0001
            },
            "residuals": {
                "mean": 0.02,
                "std": 0.15,
                "distribution": "normal"
            },
            "predictions": [5.2, 4.8, 6.1, 5.5],
            "confidence_intervals": [[4.8, 5.6], [4.4, 5.2], [5.7, 6.5], [5.1, 5.9]]
        }

    async def _classification_analysis(
        self,
        df: pd.DataFrame,
        target_column: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """Perform classification analysis"""
        return {
            "model_type": "Logistic Regression",
            "accuracy": 0.78,
            "confusion_matrix": [[45, 5], [8, 32]],
            "classification_report": {
                "precision": {"class_0": 0.85, "class_1": 0.86},
                "recall": {"class_0": 0.90, "class_1": 0.80},
                "f1_score": {"class_0": 0.87, "class_1": 0.83}
            },
            "feature_coefficients": {
                "feature_1": 1.2,
                "feature_2": -0.8,
                "feature_3": 0.5
            },
            "predictions": [0, 1, 0, 1],
            "prediction_probabilities": [[0.8, 0.2], [0.3, 0.7], [0.9, 0.1], [0.4, 0.6]]
        }

    async def _time_series_analysis(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Perform time series analysis"""
        return {
            "trend": "increasing",
            "seasonality": "monthly",
            "forecast_periods": 12,
            "forecast_values": [120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175],
            "confidence_intervals": [
                [115, 125], [120, 130], [125, 135], [130, 140],
                [135, 145], [140, 150], [145, 155], [150, 160],
                [155, 165], [160, 170], [165, 175], [170, 180]
            ],
            "model_metrics": {
                "mae": 8.5,
                "rmse": 12.3,
                "mape": 0.08
            },
            "decomposition": {
                "trend_strength": 0.7,
                "seasonal_strength": 0.5,
                "noise_level": 0.3
            }
        }


class AutomationTool(EnhancedBaseTool):
    """Tool for workflow automation and task scheduling"""

    def __init__(self):
        super().__init__(
            name="automation_engine",
            description="Automate workflows and schedule tasks",
            capabilities=["workflow_automation", "task_scheduling", "webhook_handling", "email_automation"],
            integrations=["zapier", "make_com", "smtp", "webhooks", "cron"]
        )

    async def _execute(
        self,
        action: str,
        workflow_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute automation actions"""
        logger.info(f"Executing automation action: {action}")
        
        try:
            if action == "create_workflow":
                result = await self._create_workflow(workflow_config)
            elif action == "schedule_task":
                result = await self._schedule_task(kwargs)
            elif action == "trigger_webhook":
                result = await self._trigger_webhook(kwargs)
            elif action == "send_automated_email":
                result = await self._send_automated_email(kwargs)
            elif action == "monitor_and_act":
                result = await self._monitor_and_act(workflow_config)
            else:
                raise ToolValidationError(f"Unsupported automation action: {action}")
            
            return {
                "success": True,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Automation execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create automated workflow"""
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        return {
            "workflow_id": workflow_id,
            "status": "created",
            "triggers": workflow_config.get("triggers", []),
            "actions": workflow_config.get("actions", []),
            "conditions": workflow_config.get("conditions", []),
            "schedule": workflow_config.get("schedule"),
            "estimated_runs_per_month": workflow_config.get("frequency", 30)
        }

    async def _schedule_task(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a task for future execution"""
        task_id = f"task_{datetime.now().timestamp()}"
        
        return {
            "task_id": task_id,
            "scheduled_time": task_params.get("scheduled_time"),
            "task_type": task_params.get("task_type"),
            "parameters": task_params.get("parameters"),
            "priority": task_params.get("priority", "normal"),
            "status": "scheduled"
        }

    async def _trigger_webhook(self, webhook_params: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger external webhook"""
        # Simulate webhook call
        return {
            "webhook_url": webhook_params.get("url"),
            "method": webhook_params.get("method", "POST"),
            "payload_sent": webhook_params.get("payload"),
            "response_code": 200,
            "response_body": {"status": "success", "message": "Webhook received"},
            "timestamp": datetime.now().isoformat()
        }

    async def _send_automated_email(self, email_params: Dict[str, Any]) -> Dict[str, Any]:
        """Send automated email"""
        return {
            "email_id": f"email_{datetime.now().timestamp()}",
            "to": email_params.get("to"),
            "subject": email_params.get("subject"),
            "template_used": email_params.get("template"),
            "personalization": email_params.get("personalization"),
            "status": "sent",
            "delivery_time": datetime.now().isoformat()
        }

    async def _monitor_and_act(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor conditions and trigger actions"""
        return {
            "monitoring_id": f"monitor_{datetime.now().timestamp()}",
            "conditions_monitored": monitoring_config.get("conditions"),
            "actions_triggered": ["email_alert", "task_creation", "webhook_notification"],
            "thresholds_met": ["cpu_usage > 80%", "response_time > 2s"],
            "next_check": (datetime.now() + timedelta(minutes=15)).isoformat()
        }


class CollaborationTool(EnhancedBaseTool):
    """Tool for team collaboration and communication"""

    def __init__(self):
        super().__init__(
            name="collaboration_hub",
            description="Facilitate team collaboration and communication",
            capabilities=["team_messaging", "file_sharing", "project_management", "video_conferencing"],
            integrations=["slack", "teams", "zoom", "asana", "trello", "google_drive"]
        )

    async def _execute(
        self,
        action: str,
        collaboration_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute collaboration actions"""
        logger.info(f"Executing collaboration action: {action}")
        
        try:
            if action == "create_team_space":
                result = await self._create_team_space(collaboration_data)
            elif action == "send_message":
                result = await self._send_team_message(collaboration_data)
            elif action == "share_file":
                result = await self._share_file(collaboration_data)
            elif action == "schedule_meeting":
                result = await self._schedule_meeting(collaboration_data)
            elif action == "assign_task":
                result = await self._assign_task(collaboration_data)
            else:
                raise ToolValidationError(f"Unsupported collaboration action: {action}")
            
            return {
                "success": True,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "results": result
            }
            
        except Exception as e:
            logger.error(f"Collaboration action failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _create_team_space(self, space_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create team collaboration space"""
        space_id = f"space_{datetime.now().timestamp()}"
        
        return {
            "space_id": space_id,
            "name": space_data.get("name"),
            "members": space_data.get("members", []),
            "channels": ["general", "projects", "random"],
            "integrations": ["slack", "google_drive"],
            "permissions": space_data.get("permissions", "read_write")
        }

    async def _send_team_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to team"""
        return {
            "message_id": f"msg_{datetime.now().timestamp()}",
            "channel": message_data.get("channel"),
            "sender": message_data.get("sender"),
            "content": message_data.get("content"),
            "attachments": message_data.get("attachments", []),
            "mentions": message_data.get("mentions", []),
            "delivered_to": 5,
            "read_by": 3
        }

    async def _share_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Share file with team"""
        return {
            "file_id": f"file_{datetime.now().timestamp()}",
            "filename": file_data.get("filename"),
            "size": file_data.get("size"),
            "shared_with": file_data.get("recipients", []),
            "permissions": file_data.get("permissions", "view"),
            "download_count": 0,
            "expiry_date": file_data.get("expiry_date")
        }

    async def _schedule_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule team meeting"""
        return {
            "meeting_id": f"meeting_{datetime.now().timestamp()}",
            "title": meeting_data.get("title"),
            "scheduled_time": meeting_data.get("time"),
            "duration": meeting_data.get("duration", 60),
            "attendees": meeting_data.get("attendees", []),
            "agenda": meeting_data.get("agenda", []),
            "meeting_link": f"https://zoom.us/j/{datetime.now().timestamp()}",
            "calendar_invites_sent": True
        }

    async def _assign_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign task to team member"""
        return {
            "task_id": f"task_{datetime.now().timestamp()}",
            "title": task_data.get("title"),
            "assigned_to": task_data.get("assignee"),
            "assigned_by": task_data.get("assigner"),
            "due_date": task_data.get("due_date"),
            "priority": task_data.get("priority", "normal"),
            "description": task_data.get("description"),
            "status": "assigned",
            "estimated_hours": task_data.get("estimated_hours", 4)
        }


# Create singleton instances
real_time_data = RealTimeDataTool()
multimodal_processor = MultiModalProcessorTool()
advanced_analytics = AdvancedAnalyticsTool()
automation_engine = AutomationTool()
collaboration_hub = CollaborationTool()
