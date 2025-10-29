"""
Live Claude Client - Production implementation using Anthropic API
"""

import anthropic
from django.conf import settings
from .client_interface import ClaudeClient, ClaudeResponse, TokenUsage
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class LiveClaudeClient(ClaudeClient):
    """
    Production implementation using Anthropic API.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-5-sonnet-20241022"
        self.fast_model = "claude-3-5-haiku-20241022"

    def generate_clarifications(self, question: str) -> ClaudeResponse:
        """Generate clarifying questions using Haiku (fast, cheap)"""
        try:
            prompt = self._build_clarification_prompt(question)
            logger.debug(f"Generating clarifications for question: {question[:100]}...")

            response = self.client.messages.create(
                model=self.fast_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            return ClaudeResponse(
                content=response.content[0].text,
                token_usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    model=self.fast_model
                ),
                request_id=response.id,
                success=True
            )

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error in generate_clarifications: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.fast_model),
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in generate_clarifications: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.fast_model),
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )

    def generate_response(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> ClaudeResponse:
        """Generate full response using Sonnet (higher quality)"""
        try:
            prompt = self._build_response_prompt(question, clarifications)
            logger.debug(f"Generating response for question: {question[:100]}...")

            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            return ClaudeResponse(
                content=response.content[0].text,
                token_usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    model=self.default_model
                ),
                request_id=response.id,
                success=True
            )

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error in generate_response: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.default_model),
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in generate_response: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.default_model),
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )

    def validate_question(self, question: str) -> ClaudeResponse:
        """Quick validation using Haiku"""
        try:
            prompt = f"""Is this question related to investing, finance, or retirement planning?

Question: "{question}"

Respond with ONLY a JSON object in this format:
{{"valid": true/false}}"""

            logger.debug(f"Validating question: {question[:100]}...")

            response = self.client.messages.create(
                model=self.fast_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            return ClaudeResponse(
                content=response.content[0].text,
                token_usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    model=self.fast_model
                ),
                request_id=response.id,
                success=True
            )

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error in validate_question: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.fast_model),
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in validate_question: {str(e)}")
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.fast_model),
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )

    def _build_clarification_prompt(self, question: str) -> str:
        """Build prompt for clarification generation"""
        return f"""You are an investment research assistant. A user has asked:

"{question}"

Generate 2-3 clarifying questions to better understand their context. Focus on:
- Risk tolerance
- Investment timeline
- Current portfolio allocation
- Specific concerns or goals

Return ONLY a JSON array of strings (the questions), no other text.

Example: ["What is your risk tolerance?", "What's your investment timeline?", "What percentage of your portfolio is in stocks?"]
"""

    def _build_response_prompt(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> str:
        """Build prompt for response generation"""
        context = "\n".join([
            f"Q: {item['question']}\nA: {item['answer']}"
            for item in clarifications
        ])

        return f"""You are an investment research assistant helping a user with their question.

Original Question: {question}

User Context:
{context}

Provide a thoughtful response in the following JSON format:
{{
  "summary": "2-3 sentence summary recommendation",
  "analysis": "Detailed markdown-formatted analysis with key considerations (use ## headers, bullet points, etc.)",
  "links": [
    {{"title": "Link title", "url": "https://...", "description": "Brief description"}},
    ...
  ]
}}

Guidelines:
- Be balanced and educational
- Never provide definitive "buy" or "sell" advice
- Include 3-5 high-quality, relevant links to reputable sources (Investopedia, Fidelity, Vanguard, SEC, etc.)
- Use markdown formatting in the analysis field for readability
- Consider the user's risk tolerance, timeline, and goals from the context
"""
