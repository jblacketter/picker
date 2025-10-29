"""
Claude Client Factory - Factory function to get the appropriate client
"""

from django.conf import settings
from .client_interface import ClaudeClient
from .live_client import LiveClaudeClient
from .stub_client import StubClaudeClient
import logging

logger = logging.getLogger(__name__)


def get_claude_client() -> ClaudeClient:
    """
    Factory function to get the appropriate Claude client.

    Returns LiveClaudeClient in production when API key is configured,
    StubClaudeClient for development/testing.

    Behavior:
    - If USE_STUB_AI=True: Always return StubClaudeClient
    - If USE_STUB_AI=False and ANTHROPIC_API_KEY set: Return LiveClaudeClient
    - If USE_STUB_AI=False but no API key: Return StubClaudeClient (fallback)
    """
    # Check if stub is explicitly enabled
    use_stub = getattr(settings, 'USE_STUB_AI', False)

    if use_stub:
        logger.info("Using stub AI client (USE_STUB_AI=True)")
        return StubClaudeClient()

    # Check if API key is configured
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

    if not api_key:
        logger.warning(
            "ANTHROPIC_API_KEY not configured, falling back to stub client. "
            "Set ANTHROPIC_API_KEY in .env to use live API."
        )
        return StubClaudeClient()

    # Use live client
    logger.info("Using live Anthropic API client")
    return LiveClaudeClient()
