"""
SLACK INTEGRATION
Send notifications and collaborate in Slack
"""
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class SlackNotificationTool(BaseTool):
    """Send notifications to Slack"""

    def __init__(self):
        super().__init__(
            name="slack_notifications",
            description="Send RaptorFlow notifications to Slack channels"
        )

    async def _execute(
        self,
        webhook_url: str,
        message_type: str,
        data: Dict,
        channel: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send notification to Slack"""
        logger.info(f"Sending {message_type} notification to Slack")

        try:
            # Format message
            formatted_message = self._format_slack_message(message_type, data)

            # Send to Slack
            response = await self._send_to_slack(webhook_url, formatted_message)

            return {
                "success": True,
                "message_type": message_type,
                "channel": channel or "#raptorflow",
                "timestamp": datetime.now().isoformat(),
                "slack_response": response,
                "formatted_message": formatted_message
            }

        except Exception as e:
            logger.error(f"Slack notification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _format_slack_message(self, message_type: str, data: Dict) -> Dict:
        """Format message for Slack"""
        business_name = data.get("business_name", "Business")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message_templates = {
            "research_complete": {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🔍 Research Analysis Complete"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Business:*\n{business_name}"},
                            {"type": "mrkdwn", "text": f"*Competitors Found:*\n{data.get('competitor_count', 5)}"},
                            {"type": "mrkdwn", "text": f"*Evidence Gathered:*\n{data.get('evidence_count', 20)}"},
                            {"type": "mrkdwn", "text": f"*Completeness:*\n{data.get('completeness', '85%')}"}
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "View Results"},
                                "url": f"https://raptorflow.app/dashboard/{data.get('business_id')}/research",
                                "style": "primary"
                            }
                        ]
                    }
                ]
            },
            "positioning_ready": {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "🎯 Positioning Options Ready"}
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{business_name}* has 3 new positioning options ready for review."
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Option 1:*\n{data.get('option_1', 'Premium')}"},
                            {"type": "mrkdwn", "text": f"*Option 2:*\n{data.get('option_2', 'Speed')}"},
                            {"type": "mrkdwn", "text": f"*Option 3:*\n{data.get('option_3', 'Innovation')}"}
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Review & Select"},
                                "url": f"https://raptorflow.app/dashboard/{data.get('business_id')}/positioning",
                                "style": "primary"
                            }
                        ]
                    }
                ]
            },
            "icps_generated": {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "👥 Customer Personas Generated"}
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{business_name}* personas are ready. {data.get('icp_count', 3)} detailed profiles created."
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*📊 Fit Score:*\n{data.get('fit_score', '0.85')}"},
                            {"type": "mrkdwn", "text": f"*🎯 Accessibility:*\n{data.get('accessibility', '0.72')}"}
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "View Personas"},
                                "url": f"https://raptorflow.app/dashboard/{data.get('business_id')}/icps",
                                "style": "primary"
                            }
                        ]
                    }
                ]
            },
            "alert": {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "⚠️ Alert"}
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": data.get("message", "Alert message")}
                    }
                ]
            }
        }

        return message_templates.get(message_type, {
            "text": f"{message_type}: {data.get('message', 'Update from RaptorFlow')}"
        })

    async def _send_to_slack(self, webhook_url: str, message: Dict) -> Dict:
        """Send message to Slack via webhook"""
        # In production, use requests or httpx to POST to webhook
        logger.info(f"Sending message to Slack webhook")

        # Mock response
        return {
            "ok": True,
            "ts": datetime.now().timestamp()
        }


class SlackCommandTool(BaseTool):
    """Handle Slack slash commands"""

    def __init__(self):
        super().__init__(
            name="slack_commands",
            description="Handle slash commands from Slack"
        )

    async def _execute(
        self,
        command: str,
        text: str,
        user_id: str,
        channel_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Slack command"""
        logger.info(f"Handling Slack command: {command}")

        try:
            response = self._process_command(command, text, user_id, channel_id)

            return {
                "success": True,
                "command": command,
                "response": response,
                "response_type": "in_channel"
            }

        except Exception as e:
            logger.error(f"Command processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _process_command(self, command: str, text: str, user_id: str, channel_id: str) -> Dict:
        """Process Slack command"""
        commands = {
            "/raptorflow": self._get_help_text(),
            "/research": self._start_research(text),
            "/positioning": self._get_positioning_status(text),
            "/icps": self._list_personas(text),
            "/dashboard": self._get_dashboard_link(text),
            "/report": self._generate_report(text)
        }

        return commands.get(command, self._get_help_text())

    def _get_help_text(self) -> Dict:
        """Get help text"""
        return {
            "text": "RaptorFlow Slack Commands",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Available Commands:*"}
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": """
`/research <business_id>` - Start research analysis
`/positioning <business_id>` - View positioning options
`/icps <business_id>` - View customer personas
`/dashboard <business_id>` - Get dashboard link
`/report <business_id>` - Generate report
                        """
                    }
                }
            ]
        }

    def _start_research(self, text: str) -> Dict:
        """Start research command"""
        return {
            "text": "🔍 Starting research analysis...",
            "attachments": [{"text": f"Business ID: {text}"}]
        }

    def _get_positioning_status(self, text: str) -> Dict:
        """Get positioning status"""
        return {
            "text": "🎯 Positioning Status",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": "*3 Options Available*"}},
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": "*Option 1:* Premium Quality (Score: 0.85)"},
                        {"type": "mrkdwn", "text": "*Option 2:* Speed & Efficiency (Score: 0.82)"},
                        {"type": "mrkdwn", "text": "*Option 3:* Innovation Leader (Score: 0.79)"}
                    ]
                }
            ]
        }

    def _list_personas(self, text: str) -> Dict:
        """List personas"""
        return {
            "text": "👥 Customer Personas",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": "*3 Personas Created*"}},
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": "*Executive Sarah* - 35-45, Enterprise"},
                        {"type": "mrkdwn", "text": "*Tech Tom* - 25-35, Fast-paced"},
                        {"type": "mrkdwn", "text": "*Growth Greg* - 40-55, Scale-focused"}
                    ]
                }
            ]
        }

    def _get_dashboard_link(self, text: str) -> Dict:
        """Get dashboard link"""
        return {
            "text": f"📊 Dashboard Link: https://raptorflow.app/dashboard/{text}"
        }

    def _generate_report(self, text: str) -> Dict:
        """Generate report"""
        return {
            "text": "📈 Generating report...",
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Report will be sent to your email shortly."}}
            ]
        }


class SlackDirectMessageTool(BaseTool):
    """Send direct messages to users"""

    def __init__(self):
        super().__init__(
            name="slack_direct_message",
            description="Send direct messages to Slack users"
        )

    async def _execute(
        self,
        user_id: str,
        message: str,
        attachments: List[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send direct message"""
        logger.info(f"Sending DM to {user_id}")

        try:
            response = await self._send_dm(user_id, message, attachments)

            return {
                "success": True,
                "user_id": user_id,
                "message_sent": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"DM failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _send_dm(self, user_id: str, message: str, attachments: List[Dict]) -> Dict:
        """Send DM via Slack API"""
        logger.info(f"Sending DM to {user_id}")

        return {
            "ok": True,
            "channel": f"D{user_id}",
            "ts": datetime.now().timestamp()
        }


# Singleton instances
slack_notifications = SlackNotificationTool()
slack_commands = SlackCommandTool()
slack_direct_message = SlackDirectMessageTool()
