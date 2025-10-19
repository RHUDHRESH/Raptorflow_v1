
from __future__ import annotations

import json
from typing import Any, Iterable, List

from langchain.tools import BaseTool

from utils.supabase_client import get_supabase_client


class RTBLinkerTool(BaseTool):
    """
    Link marketing claims to reasons-to-believe evidence nodes.

    Each invocation creates a claim node plus supporting evidence entries and
    connects them via edges in the evidence graph. When Supabase is not
    configured the data is stored in the in-memory client provided by
    ``get_supabase_client``.
    """

    name = "rtb_linker"
    description = (
        "Link claims to evidence. "
        "Use: rtb_linker(business_id='uuid', claim='Fastest delivery', evidence=['Study ...'])"
    )

    def __init__(self) -> None:
        super().__init__()
        self.supabase = get_supabase_client()

    def _run(  # type: ignore[override]
        self,
        business_id: str,
        claim: str,
        evidence: Iterable[str],
        source: str = "research_agent",
    ) -> str:
        claim_record = (
            self.supabase.table("evidence_nodes")
            .insert(
                {
                    "business_id": business_id,
                    "node_type": "claim",
                    "content": claim,
                    "source": source,
                    "confidence_score": 0.0,
                }
            )
            .execute()
            .data[0]
        )

        evidence_rows: List[dict[str, Any]] = []
        for snippet in evidence:
            ev_record = (
                self.supabase.table("evidence_nodes")
                .insert(
                    {
                        "business_id": business_id,
                        "node_type": "rtb",
                        "content": snippet,
                        "source": source,
                        "confidence_score": 1.0,
                    }
                )
                .execute()
                .data[0]
            )

            self.supabase.table("evidence_edges").insert(
                {
                    "from_node": claim_record["id"],
                    "to_node": ev_record["id"],
                    "relationship_type": "supported_by",
                }
            ).execute()
            evidence_rows.append(ev_record)

        if evidence_rows:
            avg_confidence = sum(row.get("confidence_score", 0.0) for row in evidence_rows) / len(evidence_rows)
            self.supabase.table("evidence_nodes").update(
                {"confidence_score": avg_confidence}
            ).eq("id", claim_record["id"]).execute()
            claim_record["confidence_score"] = avg_confidence

        payload = {
            "claim_id": claim_record["id"],
            "evidence_count": len(evidence_rows),
            "confidence": claim_record.get("confidence_score", 0.0),
        }
        return json.dumps(payload)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        return self._run(*args, **kwargs)
