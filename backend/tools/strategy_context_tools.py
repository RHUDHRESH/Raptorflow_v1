"""Strategy Workspace Context Tools"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..base_tool import BaseTool, ToolValidationError

logger = logging.getLogger(__name__)


class AddContextTool(BaseTool):
    """Add context item to strategy workspace"""

    def __init__(self):
        super().__init__(
            name="add_context",
            description="Add a text, file, or URL context item to the strategy workspace"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "item_type", "content"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

        valid_types = ["text", "file_image", "file_pdf", "file_video", "file_audio", "url"]
        if kwargs.get("item_type") not in valid_types:
            raise ToolValidationError(f"Invalid item_type: {kwargs.get('item_type')}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute context addition"""
        workspace_id = kwargs.get("workspace_id")
        item_type = kwargs.get("item_type")
        content = kwargs.get("content")
        metadata = kwargs.get("metadata", {})

        # Create context item record
        context_item = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "item_type": item_type,
            "source": "user_input",
            "raw_content": content,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

        return {
            "success": True,
            "context_item": context_item,
            "message": f"Context item added: {item_type}"
        }


class ListContextItemsTool(BaseTool):
    """List context items in workspace"""

    def __init__(self):
        super().__init__(
            name="list_context",
            description="List all context items in a strategy workspace"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        if "workspace_id" not in kwargs:
            raise ToolValidationError("Missing required field: workspace_id")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute context listing"""
        workspace_id = kwargs.get("workspace_id")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "message": "Context items retrieved",
            # In real implementation, would query database
            "items": []
        }


class DeleteContextItemTool(BaseTool):
    """Delete context item from workspace"""

    def __init__(self):
        super().__init__(
            name="delete_context",
            description="Delete a context item from the strategy workspace"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "context_item_id"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute context deletion"""
        workspace_id = kwargs.get("workspace_id")
        context_item_id = kwargs.get("context_item_id")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "context_item_id": context_item_id,
            "message": "Context item deleted"
        }


class LockJobsTool(BaseTool):
    """Lock jobs to prevent further extraction"""

    def __init__(self):
        super().__init__(
            name="lock_jobs",
            description="Lock the extracted jobs to prevent further changes during analysis"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        if "workspace_id" not in kwargs:
            raise ToolValidationError("Missing required field: workspace_id")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute job locking"""
        workspace_id = kwargs.get("workspace_id")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "message": "Jobs locked for analysis phase"
        }


class MergeJobsTool(BaseTool):
    """Merge two similar jobs"""

    def __init__(self):
        super().__init__(
            name="merge_jobs",
            description="Merge two similar Jobs-to-be-Done into one"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "jtbd_id_1", "jtbd_id_2", "merged_jtbd"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute job merging"""
        workspace_id = kwargs.get("workspace_id")
        jtbd_id_1 = kwargs.get("jtbd_id_1")
        jtbd_id_2 = kwargs.get("jtbd_id_2")
        merged_jtbd = kwargs.get("merged_jtbd")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "merged_id": str(uuid.uuid4()),
            "merged_jtbd": merged_jtbd,
            "message": f"Merged {jtbd_id_1} and {jtbd_id_2}"
        }


class SplitJobTool(BaseTool):
    """Split one job into two"""

    def __init__(self):
        super().__init__(
            name="split_job",
            description="Split a Jobs-to-be-Done into two distinct jobs"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "jtbd_id", "jtbd_1", "jtbd_2"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute job splitting"""
        workspace_id = kwargs.get("workspace_id")
        jtbd_id = kwargs.get("jtbd_id")
        jtbd_1 = kwargs.get("jtbd_1")
        jtbd_2 = kwargs.get("jtbd_2")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "original_id": jtbd_id,
            "split_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "jtbds": [jtbd_1, jtbd_2],
            "message": f"Split job {jtbd_id} into 2 jobs"
        }


class UpdateICPTool(BaseTool):
    """Update ICP details (avatar, traits, etc.)"""

    def __init__(self):
        super().__init__(
            name="update_icp",
            description="Update ICP name, avatar, traits, pain points, or behaviors"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "icp_id"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute ICP update"""
        workspace_id = kwargs.get("workspace_id")
        icp_id = kwargs.get("icp_id")
        updates = {k: v for k, v in kwargs.items() if k not in ["workspace_id", "icp_id"]}

        return {
            "success": True,
            "workspace_id": workspace_id,
            "icp_id": icp_id,
            "updated_fields": list(updates.keys()),
            "message": "ICP updated successfully"
        }


class GenerateAvatarTool(BaseTool):
    """Generate or update ICP avatar"""

    def __init__(self):
        super().__init__(
            name="generate_avatar",
            description="Generate or update an avatar for an ICP with color and style options"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "icp_id", "avatar_type"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute avatar generation"""
        workspace_id = kwargs.get("workspace_id")
        icp_id = kwargs.get("icp_id")
        avatar_type = kwargs.get("avatar_type")
        color = kwargs.get("avatar_color", "#A68763")

        avatar_url = f"/avatars/{icp_id}/{avatar_type}?color={color}"

        return {
            "success": True,
            "workspace_id": workspace_id,
            "icp_id": icp_id,
            "avatar_url": avatar_url,
            "avatar_type": avatar_type,
            "avatar_color": color,
            "message": "Avatar generated"
        }


class UpdateChannelTool(BaseTool):
    """Update channel AISAS positioning"""

    def __init__(self):
        super().__init__(
            name="update_channel",
            description="Update AISAS stage and other channel settings"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "channel_id"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute channel update"""
        workspace_id = kwargs.get("workspace_id")
        channel_id = kwargs.get("channel_id")
        aisas_stage = kwargs.get("aisas_stage")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "channel_id": channel_id,
            "aisas_stage": aisas_stage,
            "message": "Channel updated successfully"
        }


class AddChannelTool(BaseTool):
    """Add a channel to the matrix"""

    def __init__(self):
        super().__init__(
            name="add_channel",
            description="Add a new channel to an ICP/JTBD cell in the matrix"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "icp_id", "jtbd_id", "channel_name"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute channel addition"""
        workspace_id = kwargs.get("workspace_id")
        icp_id = kwargs.get("icp_id")
        jtbd_id = kwargs.get("jtbd_id")
        channel_name = kwargs.get("channel_name")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "channel_id": str(uuid.uuid4()),
            "icp_id": icp_id,
            "jtbd_id": jtbd_id,
            "channel_name": channel_name,
            "message": "Channel added to matrix"
        }


class RemoveChannelTool(BaseTool):
    """Remove a channel from the matrix"""

    def __init__(self):
        super().__init__(
            name="remove_channel",
            description="Remove a channel from an ICP/JTBD cell in the matrix"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        required = ["workspace_id", "channel_id"]
        for field in required:
            if field not in kwargs:
                raise ToolValidationError(f"Missing required field: {field}")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute channel removal"""
        workspace_id = kwargs.get("workspace_id")
        channel_id = kwargs.get("channel_id")

        return {
            "success": True,
            "workspace_id": workspace_id,
            "channel_id": channel_id,
            "message": "Channel removed from matrix"
        }


class GetExplanationsTool(BaseTool):
    """Retrieve explanations with optional filtering"""

    def __init__(self):
        super().__init__(
            name="get_explanations",
            description="Retrieve explanations for strategic decisions with filtering options"
        )

    def _validate_inputs(self, **kwargs):
        """Validate required inputs"""
        if "workspace_id" not in kwargs:
            raise ToolValidationError("Missing required field: workspace_id")

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute explanation retrieval"""
        workspace_id = kwargs.get("workspace_id")
        entity_type = kwargs.get("entity_type")  # Optional filter
        filter_type = kwargs.get("filter_type")  # wisdom_rules, platform_specs, etc.

        return {
            "success": True,
            "workspace_id": workspace_id,
            "filters": {
                "entity_type": entity_type,
                "filter_type": filter_type,
            },
            "explanations": [],  # Would be populated from database
            "message": "Explanations retrieved"
        }


# Tool factory
def create_strategy_context_tools() -> Dict[str, BaseTool]:
    """Create all strategy context tools"""
    return {
        "add_context": AddContextTool(),
        "list_context": ListContextItemsTool(),
        "delete_context": DeleteContextItemTool(),
        "lock_jobs": LockJobsTool(),
        "merge_jobs": MergeJobsTool(),
        "split_job": SplitJobTool(),
        "update_icp": UpdateICPTool(),
        "generate_avatar": GenerateAvatarTool(),
        "update_channel": UpdateChannelTool(),
        "add_channel": AddChannelTool(),
        "remove_channel": RemoveChannelTool(),
        "get_explanations": GetExplanationsTool(),
    }
