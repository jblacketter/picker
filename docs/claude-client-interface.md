# Claude Client Interface Design

## Overview

This document defines the `ClaudeClient` interface pattern for AI interactions. Having a clean abstraction allows us to:

1. **Develop without API keys** - Use stub implementation during setup
2. **Test without API costs** - Mock responses in tests
3. **Swap implementations** - Easy to switch between live, cached, or mock clients
4. **Handle errors gracefully** - Centralize error handling and retry logic

## Interface Definition

```python
# ai_service/client_interface.py

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
```

## Live Implementation

```python
# ai_service/live_client.py

import anthropic
from django.conf import settings
from .client_interface import ClaudeClient, ClaudeResponse, TokenUsage

class LiveClaudeClient(ClaudeClient):
    """Production implementation using Anthropic API"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-5-sonnet-20241022"
        self.fast_model = "claude-3-5-haiku-20241022"

    def generate_clarifications(self, question: str) -> ClaudeResponse:
        """Generate clarifying questions using Haiku (fast, cheap)"""
        try:
            prompt = self._build_clarification_prompt(question)

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
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.fast_model),
                success=False,
                error_message=str(e)
            )

    def generate_response(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> ClaudeResponse:
        """Generate full response using Sonnet (higher quality)"""
        try:
            prompt = self._build_response_prompt(question, clarifications)

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
            return ClaudeResponse(
                content="",
                token_usage=TokenUsage(0, 0, 0, self.default_model),
                success=False,
                error_message=str(e)
            )

    def validate_question(self, question: str) -> ClaudeResponse:
        """Quick validation using Haiku"""
        # Similar implementation...
        pass

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

Example: ["What is your risk tolerance?", "What's your investment timeline?"]
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

        return f"""You are an investment research assistant. Help the user with their question.

Original Question: {question}

User Context:
{context}

Provide a response in the following JSON format:
{{
  "summary": "2-3 sentence summary recommendation",
  "analysis": "Detailed analysis with key considerations",
  "links": [
    {{"title": "Link title", "url": "https://...", "description": "Brief description"}},
    ...
  ]
}}

Be balanced and educational. Never provide definitive "buy" or "sell" advice.
Include 3-5 high-quality, relevant links to reputable sources.
"""
```

## Stub Implementation

```python
# ai_service/stub_client.py

from .client_interface import ClaudeClient, ClaudeResponse, TokenUsage
from typing import List, Dict
import json

class StubClaudeClient(ClaudeClient):
    """Stub implementation for development and testing"""

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
            success=True
        )

    def generate_response(
        self,
        question: str,
        clarifications: List[Dict[str, str]]
    ) -> ClaudeResponse:
        """Return fixed response"""
        response = {
            "summary": "Based on your context, a balanced approach between stocks and bonds may be appropriate.",
            "analysis": "Consider your risk tolerance and timeline when making allocation decisions. Bonds typically provide stability but lower returns, while stocks offer growth potential with higher volatility.",
            "links": [
                {
                    "title": "Understanding Asset Allocation",
                    "url": "https://www.investopedia.com/terms/a/assetallocation.asp",
                    "description": "Comprehensive guide to portfolio allocation strategies"
                },
                {
                    "title": "Bonds vs. Stocks",
                    "url": "https://www.fidelity.com/learning-center/investment-products/bonds/bonds-vs-stocks",
                    "description": "Fidelity's comparison of bonds and stocks"
                }
            ]
        }

        return ClaudeResponse(
            content=json.dumps(response),
            token_usage=TokenUsage(
                prompt_tokens=500,
                completion_tokens=300,
                total_tokens=800,
                model="stub"
            ),
            success=True
        )

    def validate_question(self, question: str) -> ClaudeResponse:
        """Always validate as true"""
        return ClaudeResponse(
            content=json.dumps({"valid": True}),
            token_usage=TokenUsage(50, 10, 60, "stub"),
            success=True
        )
```

## Factory Pattern

```python
# ai_service/client_factory.py

from django.conf import settings
from .client_interface import ClaudeClient
from .live_client import LiveClaudeClient
from .stub_client import StubClaudeClient

def get_claude_client() -> ClaudeClient:
    """
    Factory function to get the appropriate Claude client.

    Returns LiveClaudeClient in production, StubClaudeClient in testing or
    when ANTHROPIC_API_KEY is not set.
    """
    # Use stub if explicitly set or if no API key
    use_stub = getattr(settings, 'USE_STUB_AI', False)

    if use_stub or not hasattr(settings, 'ANTHROPIC_API_KEY'):
        return StubClaudeClient()

    return LiveClaudeClient()
```

## Usage in Views

```python
# research/views.py

from ai_service.client_factory import get_claude_client
from ai_service.models import TokenUsageLog
import json

def generate_clarifications(request):
    """View to generate clarifying questions"""
    question = request.POST.get('question')

    # Get client (live or stub based on config)
    client = get_claude_client()

    # Call AI
    response = client.generate_clarifications(question)

    if not response.success:
        # Handle error
        return JsonResponse({'error': response.error_message}, status=500)

    # Log token usage
    TokenUsageLog.objects.create(
        endpoint='clarify',
        model=response.token_usage.model,
        prompt_tokens=response.token_usage.prompt_tokens,
        completion_tokens=response.token_usage.completion_tokens,
        total_tokens=response.token_usage.total_tokens,
        cost_estimate=calculate_cost(response.token_usage)
    )

    # Parse and return clarifications
    clarifications = json.loads(response.content)
    return JsonResponse({'clarifications': clarifications})
```

## Configuration

```python
# settings.py

# AI Client Configuration
USE_STUB_AI = os.getenv('USE_STUB_AI', 'False').lower() == 'true'
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
```

```bash
# .env

# Set to true to use stub implementation (no API calls)
USE_STUB_AI=False

# Anthropic API key (not needed if USE_STUB_AI=True)
ANTHROPIC_API_KEY=sk-ant-...
```

## Testing

```python
# tests/test_ai_service.py

from ai_service.stub_client import StubClaudeClient

def test_clarification_generation():
    """Test clarification generation without API calls"""
    client = StubClaudeClient()
    response = client.generate_clarifications("Should I invest in bonds?")

    assert response.success
    assert response.token_usage.total_tokens > 0

    clarifications = json.loads(response.content)
    assert len(clarifications) >= 2
    assert len(clarifications) <= 3
```

## Error Handling

The interface centralizes error handling:

1. **Network errors** - Caught and returned as `success=False`
2. **API errors** - Logged with error message
3. **Timeouts** - Can add timeout parameter to interface
4. **Malformed JSON** - Parse errors caught in view layer

## Benefits of This Approach

✅ **Development without API keys** - Use stub during setup
✅ **Testing without costs** - No API calls in tests
✅ **Consistent error handling** - All errors handled the same way
✅ **Easy to extend** - Add caching client, retry client, etc.
✅ **Token tracking built-in** - Every response includes usage
✅ **Swap implementations easily** - Single config change

## Future Enhancements

### Caching Client (Phase 2)
```python
class CachingClaudeClient(ClaudeClient):
    """Wraps another client with caching"""
    def __init__(self, wrapped_client: ClaudeClient):
        self.client = wrapped_client

    def generate_response(self, question, clarifications):
        # Check cache first
        cache_key = hash_inputs(question, clarifications)
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Call wrapped client
        response = self.client.generate_response(question, clarifications)

        # Cache successful responses
        if response.success:
            cache.set(cache_key, response, timeout=3600)

        return response
```

### Retry Client (Phase 2)
```python
class RetryClaudeClient(ClaudeClient):
    """Wraps another client with retry logic"""
    def __init__(self, wrapped_client: ClaudeClient, max_retries=3):
        self.client = wrapped_client
        self.max_retries = max_retries
```

## Migration Path

**Phase 1 (MVP):**
- Implement `ClaudeClient` interface
- Create `LiveClaudeClient` and `StubClaudeClient`
- Use factory pattern in views
- Manual error handling

**Phase 2:**
- Add `CachingClaudeClient` wrapper
- Add retry logic for transient failures
- Async support if needed

**Phase 3:**
- Background job processing for slow calls
- Request/response audit logging
- Advanced caching strategies
