# Investment Research Assistant - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                 │
│  (React Components or Django Templates)                 │
│                                                          │
│  - Question Input                                       │
│  - Clarification Dialog                                 │
│  - Research Sessions List                               │
│  - Stock Watchlist                                      │
│  - Pre-Market Movers Dashboard                          │
│  - Fallen Angels Analyzer                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Django Application Layer                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Research   │  │    Stock     │  │   Strategy   │  │
│  │     App      │  │   Analysis   │  │     App      │  │
│  │              │  │     App      │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         AI Service / Orchestration Layer         │   │
│  │  - Question processing                           │   │
│  │  - Clarification generation                      │   │
│  │  - Response synthesis                            │   │
│  │  - Token usage tracking                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Access Layer                       │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Research    │  │    Stock     │  │   User       │  │
│  │  Sessions    │  │  Watchlist   │  │   Notes      │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│           PostgreSQL (prod) / SQLite (dev)               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              External Services Layer                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Anthropic   │  │   Market     │  │   News       │  │
│  │    Claude    │  │    Data      │  │    APIs      │  │
│  │     API      │  │  (MCP/APIs)  │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer
**Technology:** React (progressive enhancement from Django templates)

**Key Components:**
- `QuestionInput`: Main entry point for research questions
- `ClarificationDialog`: Interactive Q&A for context gathering
- `ResearchSession`: Display saved research with notes
- `StockCard`: Individual stock analysis view
- `WatchlistManager`: Manage saved stocks for deep research
- `PreMarketDashboard`: Track pre-market movers
- `FallenAngelsList`: Analyze formerly high-value stocks

### Backend Layer

#### Django Apps Structure

**1. `research` app**
- Question processing
- Research session management
- Save/retrieve research conversations
- Link curation and storage

**2. `stocks` app**
- Stock symbol management
- Watchlist functionality
- Stock data caching
- Analysis tools integration

**3. `strategies` app**
- Pre-market movers tracking
- Fallen angels analysis
- Custom strategy templates
- Strategy results tracking

**4. `ai_service` app**
- Anthropic Claude integration
- Token usage tracking and limits
- Response caching
- Prompt templates management

**5. `core` app**
- Shared utilities
- User settings
- Authentication (if needed)

### AI Integration Architecture

```
User Question
     │
     ▼
┌─────────────────────────────┐
│  Question Analyzer          │
│  - Categorize question type │
│  - Determine needed context │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Clarification Generator    │
│  - Generate clarifying Qs   │
│  - Validate user responses  │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Response Synthesizer       │
│  - Generate main response   │
│  - Curate relevant links    │
│  - Format for display       │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│  Token Usage Tracker        │
│  - Log token consumption    │
│  - Enforce limits           │
│  - Alert on thresholds      │
└─────────────────────────────┘
```

### Data Model (High Level)

**ResearchSession**
- question (original user question)
- clarifications (Q&A pairs)
- response (AI-generated advice)
- links (curated resources)
- notes (user annotations)
- status (active, archived)
- created_at, updated_at

**StockWatchlist**
- symbol
- company_name
- added_date
- research_notes
- analysis_data (JSON field for flexible storage)
- status (watching, researched, dismissed)

**PreMarketMover**
- symbol
- news_headline
- news_source
- movement_percent
- strategy_notes
- executed (boolean)
- date

**AIUsageLog**
- endpoint (question_analysis, clarification, response_generation)
- tokens_used
- cost_estimate
- session_id
- timestamp

## Technology Decisions

### Phase 1: Django Templates (MVP)
- Faster initial development
- Server-side rendering
- HTMX for interactivity if needed
- Get core functionality working

### Phase 2: React Migration (If Needed)
- Build API using Django REST Framework
- Create React frontend
- Better UX for complex interactions
- Progressive enhancement approach

### Data Storage
- **Development:** SQLite (simple, no setup)
- **Production:** PostgreSQL (robust, JSON support)

### External Data Sources
- **Market Data:** Consider MCP server for Yahoo Finance, Alpha Vantage, or similar
- **News:** NewsAPI, or scraping with proper attribution
- **Stock Info:** Financial Modeling Prep API, IEX Cloud

### Caching Strategy
- Cache AI responses for identical questions
- Cache stock data (with TTL)
- Django cache framework (Redis in production)

## Deployment Architecture (Future)

```
┌─────────────────┐
│   CloudFlare    │  (CDN, SSL)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Nginx       │  (Reverse proxy, static files)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Gunicorn      │  (WSGI server)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django App     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Postgres│ │ Redis  │
└────────┘ └────────┘
```

## Security Considerations

1. **API Key Management**
   - Environment variables for all API keys
   - Never commit secrets
   - Rotate keys periodically

2. **Token Cost Protection**
   - Rate limiting per user/session
   - Daily/monthly spending caps
   - Alert system for unusual usage

3. **Data Privacy**
   - User research is personal financial data
   - Local-first option for sensitive info
   - No sharing of research sessions

## Scalability Considerations

**Current Scope:** Single user (owner)

**Future Considerations:**
- Multi-user support
- User authentication
- Per-user token budgets
- Shared research sessions
- API rate limiting

## Development Workflow

1. **Local Development**
   - Python venv
   - SQLite database
   - Django development server
   - React dev server (if using React)

2. **Testing**
   - pytest for backend
   - Jest for frontend
   - Integration tests for AI flows

3. **CI/CD (Future)**
   - GitHub Actions
   - Automated testing
   - Deployment automation

## Codex Review Notes - Addressed

✅ **Defer `strategies` app to Phase 2** - Pre-market movers and fallen angels removed from MVP scope. Keeps initial complexity low.

✅ **AI client abstraction** - See `docs/claude-client-interface.md` for ClaudeClient interface pattern with live/stub implementations.

⏭️ **Background job queue (deferred to Phase 2+)** - For single-user MVP, synchronous AI calls are acceptable. Can add Celery/async if multiple users or performance becomes an issue.

⏭️ **Raw prompt/response storage (deferred to Phase 2+)** - TokenUsageLog captures model, token counts, and costs. Full audit logging (prompts, responses, request IDs) can be added later if needed.

📝 **Cache invalidation** - Not caching in MVP (responses are user-specific). When caching is added in Phase 2, will use simple TTL-based invalidation.
