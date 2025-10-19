
from __future__ import annotations

import json
from typing import Any

from langchain.tools import BaseTool

from utils.subscription_tiers import SUBSCRIPTION_TIERS
from utils.supabase_client import get_supabase_client


class TierValidatorTool(BaseTool):
    """Validate whether a business' subscription tier grants access to a feature."""

    name = "tier_validator"
    description = (
        "Check subscription entitlements. "
        "Use: tier_validator(business_id='uuid', feature='trend-monitoring')"
    )

    def __init__(self) -> None:
        super().__init__()
        self.supabase = get_supabase_client()

    def _run(self, business_id: str, feature: str) -> str:  # type: ignore[override]
        response = (
            self.supabase.table("subscriptions")
            .select("*")
            .eq("business_id", business_id)
            .single()
            .execute()
        )

        tier = response.data["tier"] if response.data else "basic"
        tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["basic"])

        features = tier_info.get("features", set())
        has_access = feature in features or feature == "basic"

        upgrade_to: str | None = None
        if not has_access:
            for name, info in SUBSCRIPTION_TIERS.items():
                if feature in info.get("features", set()):
                    upgrade_to = name
                    break

        payload: dict[str, Any] = {
            "business_id": business_id,
            "feature": feature,
            "tier": tier,
            "has_access": has_access,
            "upgrade_to": upgrade_to,
            "max_icps": tier_info.get("max_icps"),
        }
        return json.dumps(payload)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        return self._run(*args, **kwargs)
