"""
Stub Claude Client - For development and testing without API calls
"""

from .client_interface import ClaudeClient, ClaudeResponse, TokenUsage
from typing import List, Dict
import json


class StubClaudeClient(ClaudeClient):
    """
    Stub implementation for development and testing.
    Returns realistic but fixed responses without making API calls.
    """

    def generate_clarifications(self, question: str) -> ClaudeResponse:
        """Return fixed clarification questions"""
        clarifications = [
            "What is your current age and target retirement age?",
            "How would you describe your risk tolerance (conservative, moderate, aggressive)?",
            "What percentage of your portfolio is currently in stocks vs. bonds?"
        ]

        return ClaudeResponse(
            content=json.dumps(clarifications),
            token_usage=TokenUsage(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                model="stub"
            ),
            request_id="stub-request-clarify",
            success=True
        )

    def generate_response(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> ClaudeResponse:
        """Return fixed response with mock advice"""
        response = {
            "summary": "Based on your context, a balanced approach between stocks and bonds may be appropriate for your retirement timeline and risk tolerance.",
            "analysis": """
## Key Considerations

- **Risk Tolerance**: Consider how market volatility affects your comfort level
- **Time Horizon**: Your timeline until retirement affects how much risk you can take
- **Diversification**: A mix of assets can help manage risk while pursuing growth
- **Regular Review**: Revisit your allocation periodically as your situation changes

## Balanced Approach

For most investors, a diversified portfolio including both stocks (for growth) and bonds (for stability) makes sense. The exact allocation depends on your specific circumstances.
""",
            "links": [
                {
                    "title": "Understanding Asset Allocation - Investopedia",
                    "url": "https://www.investopedia.com/terms/a/assetallocation.asp",
                    "description": "Comprehensive guide to portfolio allocation strategies"
                },
                {
                    "title": "Bonds vs. Stocks - Fidelity",
                    "url": "https://www.fidelity.com/learning-center/investment-products/bonds/bonds-vs-stocks",
                    "description": "Fidelity's comparison of bonds and stocks"
                },
                {
                    "title": "Asset Allocation Calculator - Vanguard",
                    "url": "https://investor.vanguard.com/calculator-tools/asset-allocation",
                    "description": "Tool to help determine appropriate allocation"
                },
                {
                    "title": "Retirement Investing - SEC",
                    "url": "https://www.investor.gov/introduction-investing/investing-basics/save-invest/savings-and-investing-retirement",
                    "description": "SEC guidance on retirement investing"
                }
            ]
        }

        return ClaudeResponse(
            content=json.dumps(response),
            token_usage=TokenUsage(
                prompt_tokens=500,
                completion_tokens=350,
                total_tokens=850,
                model="stub"
            ),
            request_id="stub-request-respond",
            success=True
        )

    def validate_question(self, question: str) -> ClaudeResponse:
        """Always validate as true for development"""
        # Simple heuristic: check if question contains investment-related keywords
        investment_keywords = [
            'invest', 'stock', 'bond', 'portfolio', '401k', 'retirement',
            'market', 'fund', 'asset', 'diversif', 'risk', 'return'
        ]

        question_lower = question.lower()
        is_valid = any(keyword in question_lower for keyword in investment_keywords)

        return ClaudeResponse(
            content=json.dumps({"valid": is_valid}),
            token_usage=TokenUsage(
                prompt_tokens=50,
                completion_tokens=10,
                total_tokens=60,
                model="stub"
            ),
            request_id="stub-request-validate",
            success=True
        )
