# Technical Decisions & Rationale

## Decision Log

### 1. Why Django over Flask/FastAPI?

**Decision:** Use Django for the backend framework

**Rationale:**
- Project will likely grow complex over time
- Django admin provides free data management UI
- Built-in ORM handles relationships well
- Authentication ready if needed later
- Django REST Framework available for API if we add React
- More "batteries included" for a full-featured app

**Trade-offs:**
- Heavier than Flask/FastAPI
- More opinionated structure
- Slight learning curve if unfamiliar

**Alternative Considered:** FastAPI
- Pro: Modern, fast, great for APIs
- Con: Need to add admin panel, ORM, etc.
- Con: Better for API-first, we're starting with monolith

### 2. Django Templates vs React (MVP)

**Decision:** Start with Django Templates for MVP, migrate to React in Phase 2

**Rationale:**
- Faster initial development
- One codebase (Python) to maintain
- Server-side rendering is simpler
- Can use HTMX for dynamic interactions if needed
- Easier to prototype and iterate

**Migration Path:**
- Phase 1: Django templates
- Phase 1.5: Add Django REST Framework
- Phase 2: Build React frontend consuming API
- Templates and API can coexist during migration

**Alternative Considered:** React from start
- Pro: Better UX for complex interactions
- Pro: Modern development experience
- Con: Two codebases to set up (Django + React)
- Con: Slower MVP delivery
- Con: More complex deployment initially

### 3. SQLite vs PostgreSQL (Development)

**Decision:** SQLite for development, PostgreSQL for production

**Rationale:**
- SQLite: Zero configuration, perfect for local dev
- PostgreSQL: Better JSON support, production-ready
- Django makes switching databases trivial
- Single user app initially, SQLite is sufficient

**Migration Path:**
- Develop on SQLite
- Before deployment, switch to PostgreSQL
- Test migrations work smoothly

### 4. Anthropic Claude API Choice

**Decision:** Use Claude 3.5 Sonnet for main interactions, Haiku for simple tasks

**Rationale:**
- Sonnet: Best balance of quality and cost
- Strong reasoning for investment advice
- Good at generating structured outputs
- Haiku: Fast and cheap for question classification, simple tasks

**Cost Management:**
- Track token usage per endpoint
- Use Haiku where possible (categorization, validation)
- Use Sonnet for research responses
- Cache aggressively
- Implement hard limits before MVP launch

**Alternative Considered:** GPT-4
- Pro: Slightly cheaper in some scenarios
- Con: User already has Anthropic subscription
- Con: Claude's context window and reasoning preferred

### 5. MCP Server Integration

**Decision:** Defer MCP integration to Phase 2+

**Rationale:**
- MVP can work with manual link curation
- MCP adds complexity to setup
- Focus on core research flow first
- Can add financial data MCP server later

**Future Integration Points:**
- Market data server (Yahoo Finance, Alpha Vantage)
- News aggregation server
- Portfolio tracking server

### 6. Styling Approach

**Decision:** Tailwind CSS via CDN for MVP

**Rationale:**
- No build step required
- Fast to prototype
- Responsive by default
- Easy to make things look decent quickly

**Future:**
- Phase 2: Consider build process for optimization
- If React is added, integrate Tailwind properly

**Alternative Considered:** Bootstrap
- Pro: Component library ready to go
- Con: More opinionated, harder to customize
- Con: Heavier CSS

### 7. Token Usage Tracking Strategy

**Decision:** Log all AI calls synchronously in database

**Rationale:**
- Critical for cost control
- Simple implementation (model + signal)
- Real-time visibility
- Can build dashboards from logs

**Implementation:**
```python
@receiver(post_save, sender=ResearchSession)
def log_token_usage(sender, instance, **kwargs):
    TokenUsageLog.objects.create(
        endpoint='research_response',
        tokens_used=instance.response.token_count,
        cost_estimate=calculate_cost(...),
        session=instance
    )
```

### 8. Caching Strategy

**Decision:** Start without caching, add Django cache in Phase 1F

**Rationale:**
- Premature optimization risk
- Stock data changes frequently
- Research questions are usually unique
- Add caching once we see patterns

**Future Caching Targets:**
- Identical questions (hash-based)
- Stock basic info (symbol -> company name)
- News articles (TTL: 1 hour)

### 9. External Data Sources

**Decision:** Start with manual/AI-curated links, add APIs in Phase 2

**MVP Approach:**
- AI generates links to public resources
- User validates and saves relevant ones
- No real-time data fetching

**Phase 2 Data Sources:**
- **Market Data:** Yahoo Finance API (free tier) or MCP
- **Stock Info:** Financial Modeling Prep API
- **News:** NewsAPI.org
- **Historical Data:** Alpha Vantage

**Rationale:**
- MVP focuses on research organization
- Real-time data adds complexity and cost
- AI can generate useful links without direct API access

### 10. Authentication

**Decision:** No authentication for MVP (single user)

**Rationale:**
- App is for personal use (owner only)
- Local development/deployment
- Simplifies MVP significantly

**Phase 2 Consideration:**
- Add Django authentication if deployed
- Per-user research sessions
- Per-user token budgets

### 11. Testing Strategy

**Decision:** Manual testing for MVP, automated tests in Phase 2

**MVP Testing:**
- Manual testing of all workflows
- Test on Mac and Windows
- Validate AI responses manually

**Phase 2 Testing:**
- pytest for backend logic
- Django TestCase for views
- Mock AI calls in tests
- Integration tests for full flows

**Rationale:**
- MVP needs to work, not be perfectly tested
- Automated tests take time to write
- Once core features stabilize, add tests

### 12. Deployment Strategy

**Decision:** Local-first deployment (Django dev server initially)

**MVP Deployment:**
- Run locally on Mac
- Django development server
- SQLite database
- Access via localhost

**Future Deployment:**
- Option 1: Docker container
- Option 2: Deploy to VPS (DigitalOcean, etc.)
- Option 3: PaaS (Railway, Render, etc.)

**Rationale:**
- Single user doesn't need production deploy
- Local is simpler and free
- Can deploy later if needed

### 13. Version Control & Dependencies

**Decision:** Git + requirements.txt + detailed README

**Structure:**
```
requirements.txt          # Production dependencies
requirements-dev.txt      # Development dependencies (pytest, etc.)
.gitignore               # Standard Python/Django ignores
.env.example             # Template for environment variables
```

**Rationale:**
- requirements.txt is Python standard
- Easy to set up on any machine
- Clear separation of prod vs dev dependencies

### 14. Error Handling & Logging

**Decision:** Django logging + user-friendly error pages

**Approach:**
- Log all errors to file (dev) or service (prod)
- Show user-friendly error messages
- Graceful degradation if AI fails
- Never expose API keys or internal errors

**Implementation:**
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/picker.log',
        },
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'INFO'},
        'ai_service': {'handlers': ['file'], 'level': 'DEBUG'},
    },
}
```

### 15. API Key Management

**Decision:** Environment variables via .env file

**Implementation:**
- python-decouple or django-environ
- .env file for local development (not in git)
- .env.example checked into git as template

**Example:**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=django-secret-key
DEBUG=True
```

**Rationale:**
- Standard approach
- Works cross-platform (Mac/Windows)
- Easy to manage different environments
- Secure (keys not in code)

## Questions Still To Answer

1. **Link Curation:** Should AI generate links, or should we fetch from specific sources?
   - **Current thinking:** AI generates, Phase 2 validates with real APIs

2. **Research Session Search:** What fields should be searchable?
   - **Current thinking:** Title, question text, tags (if we add them)

3. **Stock Symbol Validation:** Should we validate that symbols exist?
   - **Current thinking:** Phase 2 feature, manual entry for MVP

4. **Response Format:** Markdown? HTML? Structured JSON?
   - **Current thinking:** Store as Markdown, render as HTML

## Decision Review Schedule

- After MVP completion: Review all decisions
- After 1 month of use: Assess what's working
- Before Phase 2: Re-evaluate React, MCP, and deployment decisions

## Codex Review Notes - Addressed

✅ **Extended TokenUsageLog** - Model now captures `model`, `prompt_tokens`, `completion_tokens`, and `total_tokens`. See updated schema in `docs/data-model.md`.

✅ **ClaudeClient interface** - Clean abstraction defined in `docs/claude-client-interface.md`. Makes testing easier and enables future extensions (caching, retries).

⏭️ **Smoke tests (deferred to Phase 1F/2)** - Will add lightweight tests around Claude client and token logging during polish phase. Manual testing sufficient for MVP core development.

📝 **MarketDataService interface (Phase 2)** - When adding MCP/real data providers, will create clean abstraction similar to ClaudeClient pattern. MVP uses AI-generated links only.
