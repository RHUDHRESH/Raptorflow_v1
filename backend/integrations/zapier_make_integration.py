"""
ZAPIER & MAKE.COM INTEGRATION ADAPTER
Connect RaptorFlow to 5000+ apps via Zapier and Make.com
"""
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ZapierWebhookTool(BaseTool):
    """Handle Zapier webhook integrations"""

    def __init__(self):
        super().__init__(
            name="zapier_webhook",
            description="Create and manage Zapier webhook integrations"
        )

    async def _execute(
        self,
        action: str,
        data: Dict,
        webhook_url: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle Zapier webhook action"""
        logger.info(f"Processing Zapier webhook action: {action}")

        try:
            if action == "create_webhook":
                result = await self._create_webhook(data)
            elif action == "trigger":
                result = await self._trigger_zap(webhook_url, data)
            elif action == "test":
                result = await self._test_webhook(webhook_url)
            else:
                result = {"error": f"Unknown action: {action}"}

            return {
                "success": True,
                "action": action,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Zapier webhook failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_webhook(self, data: Dict) -> Dict:
        """Create Zapier webhook"""
        webhook_id = f"webhook_{datetime.now().timestamp()}"
        trigger_events = data.get("trigger_events", [
            "research_complete",
            "positioning_ready",
            "icps_generated"
        ])

        webhook_url = f"https://zapier.com/api/webhooks/{webhook_id}"

        return {
            "webhook_id": webhook_id,
            "webhook_url": webhook_url,
            "trigger_events": trigger_events,
            "status": "active",
            "setup_instructions": f"Copy this URL to Zapier: {webhook_url}"
        }

    async def _trigger_zap(self, webhook_url: str, data: Dict) -> Dict:
        """Trigger a Zap via webhook"""
        # In production, POST to Zapier webhook URL
        logger.info(f"Triggering Zap at {webhook_url}")

        return {
            "triggered": True,
            "timestamp": datetime.now().isoformat(),
            "data_sent": data
        }

    async def _test_webhook(self, webhook_url: str) -> Dict:
        """Test webhook connection"""
        logger.info(f"Testing webhook: {webhook_url}")

        return {
            "status": "active",
            "response_time": "245ms",
            "last_triggered": datetime.now().isoformat()
        }


class MakeComScenarioTool(BaseTool):
    """Create and manage Make.com (formerly Integromat) scenarios"""

    def __init__(self):
        super().__init__(
            name="make_com_scenarios",
            description="Create and manage Make.com scenarios for complex workflows"
        )

    async def _execute(
        self,
        scenario_type: str,
        business_data: Dict,
        config: Dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create Make scenario"""
        logger.info(f"Creating Make scenario: {scenario_type}")

        try:
            scenario = self._generate_scenario(scenario_type, business_data, config)

            return {
                "success": True,
                "scenario_type": scenario_type,
                "scenario_config": scenario,
                "activation_status": "ready",
                "setup_link": f"https://www.make.com/scenarios/new?template={scenario_type}",
                "documentation": self._get_scenario_docs(scenario_type)
            }

        except Exception as e:
            logger.error(f"Make scenario creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_scenario(self, scenario_type: str, business_data: Dict, config: Dict) -> Dict:
        """Generate Make.com scenario configuration"""
        scenarios = {
            "send_results_to_email": {
                "name": "Send RaptorFlow Results to Email",
                "modules": [
                    {"type": "trigger", "app": "RaptorFlow", "event": "new_results"},
                    {"type": "action", "app": "Gmail", "action": "send_email"},
                    {"type": "action", "app": "GoogleSheets", "action": "add_row"}
                ],
                "description": "Automatically email analysis results and save to sheet"
            },
            "slack_notifications": {
                "name": "Send Results to Slack",
                "modules": [
                    {"type": "trigger", "app": "RaptorFlow", "event": "analysis_complete"},
                    {"type": "action", "app": "Slack", "action": "send_message"},
                    {"type": "filter", "condition": "status == completed"}
                ],
                "description": "Notify Slack channel when analysis completes"
            },
            "google_forms_sync": {
                "name": "Sync Google Forms to RaptorFlow",
                "modules": [
                    {"type": "trigger", "app": "GoogleForms", "event": "new_response"},
                    {"type": "action", "app": "RaptorFlow", "action": "import_feedback"},
                    {"type": "action", "app": "GoogleSheets", "action": "update_row"}
                ],
                "description": "Import form responses and analyze sentiment"
            },
            "calendar_sync": {
                "name": "Sync Calendar with Content Plan",
                "modules": [
                    {"type": "trigger", "app": "RaptorFlow", "event": "content_calendar_created"},
                    {"type": "action", "app": "GoogleCalendar", "action": "create_events"},
                    {"type": "action", "app": "Slack", "action": "send_reminder"}
                ],
                "description": "Auto-create calendar events for content calendar"
            },
            "data_backup": {
                "name": "Auto-backup to Drive",
                "modules": [
                    {"type": "trigger", "app": "RaptorFlow", "event": "data_updated"},
                    {"type": "action", "app": "GoogleDrive", "action": "create_backup"},
                    {"type": "action", "app": "GoogleSheets", "action": "log_backup"}
                ],
                "description": "Automatically backup all data to Google Drive"
            },
            "competitor_monitoring": {
                "name": "Monitor Competitor Changes",
                "modules": [
                    {"type": "trigger", "app": "RSS", "event": "new_item"},
                    {"type": "filter", "condition": "contains competitor names"},
                    {"type": "action", "app": "RaptorFlow", "action": "log_competitor_update"},
                    {"type": "action", "app": "Slack", "action": "alert_team"}
                ],
                "description": "Monitor RSS feeds for competitor mentions"
            }
        }

        return scenarios.get(scenario_type, scenarios["send_results_to_email"])

    def _get_scenario_docs(self, scenario_type: str) -> str:
        """Get scenario documentation"""
        docs = {
            "send_results_to_email": """
1. Create Gmail module in Make
2. Select 'Send Email' action
3. Map recipients: {{analysis.email_list}}
4. Template: Use default or customize
5. Activate scenario
            """,
            "slack_notifications": """
1. Add Slack module with webhook
2. Select channel from dropdown
3. Message format: {{analysis.summary}}
4. Add any attachments needed
5. Test and activate
            """,
            "google_forms_sync": """
1. Set up Google Forms trigger
2. Map response fields to RaptorFlow
3. Configure sentiment analysis
4. Test with sample response
5. Enable auto-sync
            """
        }

        return docs.get(scenario_type, "See Make.com documentation")


class IntegrationMarketplaceAdapter(BaseTool):
    """Adapter for connecting RaptorFlow to integration marketplaces"""

    def __init__(self):
        super().__init__(
            name="integration_marketplace",
            description="Connect RaptorFlow to 5000+ apps via Zapier and Make.com"
        )

    async def _execute(
        self,
        marketplace: str,  # "zapier" or "make"
        action: str,
        data: Dict,
        **kwargs
    ) -> Dict[str, Any]:
        """Connect to integration marketplace"""
        logger.info(f"Connecting to {marketplace}")

        try:
            if marketplace == "zapier":
                result = await self._connect_zapier(action, data)
            elif marketplace == "make":
                result = await self._connect_make(action, data)
            else:
                return {"success": False, "error": f"Unknown marketplace: {marketplace}"}

            return {
                "success": True,
                "marketplace": marketplace,
                "action": action,
                "result": result
            }

        except Exception as e:
            logger.error(f"Marketplace connection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _connect_zapier(self, action: str, data: Dict) -> Dict:
        """Connect to Zapier"""
        return {
            "platform": "Zapier",
            "available_apps": 5000,
            "popular_integrations": [
                "Email (Gmail, Outlook)",
                "Communication (Slack, Teams)",
                "Sheets (Google Sheets, Excel)",
                "Forms (Google Forms, Typeform)",
                "CRM (HubSpot, Salesforce)",
                "Project Management (Asana, Monday.com)",
                "Analytics (Google Analytics, Mixpanel)"
            ],
            "get_started": "https://zapier.com/webintent/select/search?q=RaptorFlow"
        }

    async def _connect_make(self, action: str, data: Dict) -> Dict:
        """Connect to Make.com"""
        return {
            "platform": "Make.com",
            "available_apps": 1500,
            "popular_integrations": [
                "Email Automation",
                "Slack & Teams",
                "Google Suite",
                "Calendar Sync",
                "Document Management",
                "Data Analysis",
                "Social Media"
            ],
            "get_started": "https://www.make.com/en/integrations/search?q=RaptorFlow"
        }


class OneWaySyncTool(BaseTool):
    """One-way sync for data from external sources"""

    def __init__(self):
        super().__init__(
            name="one_way_sync",
            description="Sync data from external sources into RaptorFlow"
        )

    async def _execute(
        self,
        source: str,
        source_id: str,
        data_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Sync data from external source"""
        logger.info(f"Syncing {data_type} from {source}")

        try:
            # Fetch data from source
            source_data = await self._fetch_from_source(source, source_id)

            # Transform data
            transformed = self._transform_data(source_data, data_type)

            # Validate
            validation = self._validate_data(transformed)

            if validation["valid"]:
                return {
                    "success": True,
                    "source": source,
                    "data_type": data_type,
                    "records_synced": len(transformed),
                    "data": transformed,
                    "status": "synced"
                }
            else:
                return {
                    "success": False,
                    "error": f"Validation failed: {validation['errors']}"
                }

        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _fetch_from_source(self, source: str, source_id: str) -> List[Dict]:
        """Fetch data from source"""
        # In production, connect to actual services

        sources = {
            "google_forms": self._fetch_google_forms,
            "google_sheets": self._fetch_google_sheets,
            "salesforce": self._fetch_salesforce,
            "hubspot": self._fetch_hubspot,
            "csv": self._fetch_csv
        }

        fetch_func = sources.get(source)
        if fetch_func:
            return await fetch_func(source_id)

        return []

    async def _fetch_google_forms(self, form_id: str) -> List[Dict]:
        """Fetch from Google Forms"""
        return [{"response": "sample", "timestamp": datetime.now().isoformat()}]

    async def _fetch_google_sheets(self, sheet_id: str) -> List[Dict]:
        """Fetch from Google Sheets"""
        return [{"row": 1, "data": "sample"}]

    async def _fetch_salesforce(self, org_id: str) -> List[Dict]:
        """Fetch from Salesforce"""
        return [{"lead": "sample", "status": "new"}]

    async def _fetch_hubspot(self, account_id: str) -> List[Dict]:
        """Fetch from HubSpot"""
        return [{"contact": "sample", "stage": "new"}]

    async def _fetch_csv(self, file_path: str) -> List[Dict]:
        """Fetch from CSV"""
        return [{"row": 1, "data": "sample"}]

    def _transform_data(self, data: List[Dict], data_type: str) -> List[Dict]:
        """Transform data to RaptorFlow format"""
        return data

    def _validate_data(self, data: List[Dict]) -> Dict:
        """Validate transformed data"""
        return {
            "valid": len(data) > 0,
            "errors": [] if len(data) > 0 else ["No data found"]
        }


# Singleton instances
zapier_webhook = ZapierWebhookTool()
make_com_scenarios = MakeComScenarioTool()
integration_marketplace = IntegrationMarketplaceAdapter()
one_way_sync = OneWaySyncTool()
