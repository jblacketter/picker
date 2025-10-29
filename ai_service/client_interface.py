"""
Claude Client Interface - Abstract base class for AI interactions

This interface allows us to:
- Develop without API keys (use stub implementation)
- Test without API costs (mock responses)
- Swap implementations easily
- Handle errors gracefully
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Token usage information from API call"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


@dataclass
class ClaudeResponse:
    """Standardized response from Claude API"""
    content: str
    token_usage: TokenUsage
    request_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class ClaudeClient(ABC):
    """Abstract base class for Claude API clients"""

    @abstractmethod
    def generate_clarifications(self, question: str) -> ClaudeResponse:
        """
        Generate 2-3 clarifying questions for a user's investment question.

        Args:
            question: User's original investment question

        Returns:
            ClaudeResponse with JSON array of clarification questions
        """
        pass

    @abstractmethod
    def generate_response(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> ClaudeResponse:
        """
        Generate investment research response based on question and context.

        Args:
            question: User's original question
            clarifications: List of {question, answer} dicts

        Returns:
            ClaudeResponse with research advice and curated links
        """
        pass

    @abstractmethod
    def validate_question(self, question: str) -> ClaudeResponse:
        """
        Quick validation that question is investment-related.

        Args:
            question: User's question

        Returns:
            ClaudeResponse with validation result (boolean)
        """
        pass

    @abstractmethod
    def analyze_stock_opportunity(self, prompt: str) -> ClaudeResponse:
        """
        Analyze a stock trading opportunity based on news and price movement.

        Args:
            prompt: Full analysis prompt with stock details, news, and movement

        Returns:
            ClaudeResponse with analysis and sentiment in JSON format
        """
        pass
