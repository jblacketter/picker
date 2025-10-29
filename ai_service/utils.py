"""
Utility functions for AI service
"""

from decimal import Decimal
from .client_interface import TokenUsage


# Claude pricing (as of October 2024)
# https://www.anthropic.com/pricing
PRICING = {
    'claude-3-5-sonnet-20241022': {
        'input': Decimal('0.003') / 1000,  # $3 per million tokens
        'output': Decimal('0.015') / 1000,  # $15 per million tokens
    },
    'claude-3-5-haiku-20241022': {
        'input': Decimal('0.001') / 1000,  # $1 per million tokens
        'output': Decimal('0.005') / 1000,  # $5 per million tokens
    },
    'stub': {
        'input': Decimal('0'),
        'output': Decimal('0'),
    }
}


def calculate_cost(token_usage: TokenUsage) -> Decimal:
    """
    Calculate estimated cost for token usage.

    Args:
        token_usage: TokenUsage object with prompt, completion tokens and model

    Returns:
        Decimal cost in USD
    """
    model = token_usage.model

    # Get pricing for this model, default to Sonnet if unknown
    pricing = PRICING.get(model, PRICING['claude-3-5-sonnet-20241022'])

    input_cost = Decimal(token_usage.prompt_tokens) * pricing['input']
    output_cost = Decimal(token_usage.completion_tokens) * pricing['output']

    return input_cost + output_cost


def format_cost(cost: Decimal) -> str:
    """
    Format cost for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted string like "$0.0234" or "$0.00" for small amounts
    """
    if cost == 0:
        return "$0.00"
    elif cost < Decimal('0.01'):
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"
