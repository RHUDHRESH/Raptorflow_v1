"""Base tool class with common functionality"""
import logging
import json
from typing import Any, Optional, Dict, Callable
from abc import ABC, abstractmethod
from functools import wraps

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Custom exception for tool errors"""
    pass


class ToolValidationError(ToolError):
    """Exception for validation errors"""
    pass


class ToolTimeoutError(ToolError):
    """Exception for timeout errors"""
    pass


def validate_inputs(required_fields: list):
    """Decorator to validate tool inputs"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check required fields
            for field in required_fields:
                if field not in kwargs and not args:
                    raise ToolValidationError(f"Missing required field: {field}")

            # Call the actual function
            return await func(self, *args, **kwargs)

        return wrapper
    return decorator


class BaseTool(ABC):
    """Base class for all LLM tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool - implement in subclass"""
        pass

    async def run(self, **kwargs) -> str:
        """Run the tool with error handling"""
        try:
            logger.debug(f"Tool {self.name} executing with args: {list(kwargs.keys())}")

            # Validate inputs
            self._validate_inputs(**kwargs)

            # Execute
            result = await self._execute(**kwargs)

            logger.debug(f"Tool {self.name} succeeded")
            return json.dumps(result)

        except ToolValidationError as e:
            logger.error(f"Tool {self.name} validation error: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": "validation"
            })

        except ToolTimeoutError as e:
            logger.error(f"Tool {self.name} timeout: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": "timeout"
            })

        except Exception as e:
            logger.exception(f"Tool {self.name} failed: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "error_type": "unknown"
            })

    def _validate_inputs(self, **kwargs):
        """Override in subclass to validate inputs"""
        pass

    async def _call_api(self, url: str, method: str = "GET", **kwargs):
        """Helper to make API calls with error handling"""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise ToolTimeoutError(f"API timeout calling {url}")
        except Exception as e:
            raise ToolError(f"API error: {str(e)}")
