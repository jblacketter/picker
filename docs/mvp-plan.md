# MVP Development Plan

## Project Name: "Picker" - Investment Research Assistant

## MVP Goal
Build a working question-driven investment research tool that allows the user to:
1. Ask an investment question
2. Receive clarifying questions
3. Get AI-generated advice with curated links
4. Save research sessions for later review

## MVP Scope (Phase 1)

### ✅ IN SCOPE

**Core Research Flow**
- [ ] Ask investment question via web form
- [ ] Receive 2-3 clarifying questions from AI
- [ ] Submit answers to clarifying questions
- [ ] Receive AI-generated advice with:
  - Summary of recommendation
  - Key considerations
  - 3-5 curated links to external resources
- [ ] Save entire research session

**Research Session Management**
- [ ] View list of saved research sessions
- [ ] Click to view full session details
- [ ] Add personal notes to saved sessions
- [ ] Basic search/filter of saved sessions

**Stock Watchlist (Basic)**
- [ ] Save stock symbol from research session
- [ ] View list of saved stocks
- [ ] Add notes to saved stocks
- [ ] Remove stocks from watchlist

**Token Usage Tracking**
- [ ] Log all AI API calls
- [ ] Display current session token usage
- [ ] Simple usage dashboard (tokens used today/this week)

### ❌ OUT OF SCOPE (Phase 2+)

- Pre-market movers tracking
- Fallen angels analysis
- Real-time stock data integration
- Technical analysis tools (Bollinger Bands, etc.)
- Portfolio integration with Fidelity
- Multi-user support
- Advanced search and filtering
- Charts and visualizations
- Email notifications
- Mobile app

## Technical Implementation (MVP)

### Technology Stack
- **Backend:** Django 5.0+
- **Frontend:** Django Templates + basic CSS (no React for MVP)
- **Database:** SQLite (dev), easy PostgreSQL migration later
- **AI:** Anthropic Claude API
- **Styling:** Tailwind CSS via CDN (minimal setup)

### Django Apps

**1. `research` app**
```
Models:
- ResearchSession
- ClarificationQuestion
- UserResponse
- ResearchNote

Views:
- ask_question (form)
- answer_clarifications (form)
- view_session (detail)
- list_sessions (list)

Templates:
- ask_question.html
- clarification_form.html
- session_detail.html
- session_list.html
```

**2. `stocks` app**
```
Models:
- WatchlistItem

Views:
- watchlist_view
- add_to_watchlist
- add_note

Templates:
- watchlist.html
```

**3. `ai_service` app**
```
Services (not models):
- claude_service.py
  - analyze_question()
  - generate_clarifications()
  - generate_response()
  - curate_links()

Models:
- TokenUsageLog

Utils:
- token_tracker.py
- prompt_templates.py
```

## Development Phases

### Phase 1A: Foundation (Week 1)
**Goal:** Basic Django setup and structure

- [ ] Initialize Django project
- [ ] Create app structure
- [ ] Set up SQLite database
- [ ] Create basic models
- [ ] Run migrations
- [ ] Set up Django admin

**Deliverable:** Empty Django project with models, accessible admin panel

### Phase 1B: AI Integration (Week 1-2)
**Goal:** Claude API working with token tracking

- [ ] Set up Anthropic API client
- [ ] Create prompt templates
- [ ] Implement question analysis
- [ ] Implement clarification generation
- [ ] Implement response generation
- [ ] Token usage logging
- [ ] Test AI flows in Django shell

**Deliverable:** Working AI service that can process questions

### Phase 1C: Core Research Flow (Week 2-3)
**Goal:** User can complete one research session

- [ ] Create question form view
- [ ] Create clarification form view
- [ ] Create response display view
- [ ] Wire up AI service to views
- [ ] Save complete research sessions
- [ ] Basic error handling

**Deliverable:** Working end-to-end research flow

### Phase 1D: Session Management (Week 3)
**Goal:** User can manage saved sessions

- [ ] List all research sessions
- [ ] View individual session details
- [ ] Add notes to sessions
- [ ] Basic styling with Tailwind

**Deliverable:** Working session management

### Phase 1E: Stock Watchlist (Week 4)
**Goal:** Basic stock tracking

- [ ] Watchlist model and views
- [ ] Add stock from session or manually
- [ ] View watchlist
- [ ] Add notes to stocks
- [ ] Link to external stock info (Yahoo Finance, etc.)

**Deliverable:** Basic watchlist functionality

### Phase 1F: Token Tracking UI (Week 4)
**Goal:** Visibility into AI usage

- [ ] Token usage dashboard
- [ ] Display usage stats
- [ ] Set basic limits/alerts

**Deliverable:** Token usage visibility

### Phase 1G: Polish & Deploy (Week 5)
**Goal:** Production-ready MVP

- [ ] Improve UI/UX
- [ ] Add error handling
- [ ] Write documentation
- [ ] Create setup scripts
- [ ] Test on Windows
- [ ] Deploy locally or to server

**Deliverable:** Fully working MVP

## Codex Review Notes - Incorporated

✅ **ClaudeClient interface** - Created comprehensive interface design in `docs/claude-client-interface.md` with live and stub implementations. Enables development without API keys and testing without costs.

✅ **Extended token tracking** - Updated `TokenUsageLog` model to capture `model`, `prompt_tokens`, `completion_tokens`, and `total_tokens` for cost transparency.

✅ **Error handling requirements** - Added acceptance criteria below for Core Research Flow completion.

### Core Research Flow - Acceptance Criteria

Phase 1C is only complete when these scenarios are handled:

**Error Handling:**
- [ ] Claude API timeout (> 30 seconds)
- [ ] Malformed JSON response from Claude
- [ ] Network errors (no internet, API down)
- [ ] Invalid API key
- [ ] Rate limit exceeded

**User Experience:**
- [ ] User can restart abandoned session
- [ ] Error messages are user-friendly (not raw exceptions)
- [ ] Partial progress is saved (question entered, even if clarifications fail)
- [ ] User can retry failed AI calls

**Graceful Degradation:**
- [ ] Stub client works when API key not configured
- [ ] UI shows clear state (loading, error, success)

## Data Model (MVP)

### ResearchSession
```python
- id (PK)
- title (CharField) - Generated from original question
- original_question (TextField)
- created_at (DateTimeField)
- updated_at (DateTimeField)
- status (CharField) - CHOICES: 'in_progress', 'completed'
```

### ClarificationQuestion
```python
- id (PK)
- session (FK -> ResearchSession)
- question_text (TextField)
- order (IntegerField)
```

### UserResponse
```python
- id (PK)
- clarification (FK -> ClarificationQuestion)
- response_text (TextField)
```

### ResearchResponse
```python
- id (PK)
- session (OneToOne -> ResearchSession)
- summary (TextField)
- detailed_response (TextField)
- links (JSONField) - Array of {title, url, description}
- token_count (IntegerField)
```

### ResearchNote
```python
- id (PK)
- session (FK -> ResearchSession)
- note_text (TextField)
- created_at (DateTimeField)
```

### WatchlistItem
```python
- id (PK)
- symbol (CharField)
- company_name (CharField)
- added_date (DateTimeField)
- notes (TextField)
- source_session (FK -> ResearchSession, nullable)
```

### TokenUsageLog
```python
- id (PK)
- endpoint (CharField) - 'analyze', 'clarify', 'respond'
- tokens_used (IntegerField)
- cost_estimate (DecimalField)
- session (FK -> ResearchSession, nullable)
- timestamp (DateTimeField)
```

## Key Prompts (Initial Templates)

### Question Analysis Prompt
```
You are an investment research assistant. A user has asked the following question:

{user_question}

Analyze this question and generate 2-3 clarifying questions that will help you provide better, more personalized advice. Focus on:
- User's risk tolerance
- Investment timeframe
- Current portfolio allocation
- Specific concerns or goals

Return the clarifying questions in JSON format.
```

### Response Generation Prompt
```
You are an investment research assistant helping a user with their question:

Original Question: {original_question}

User Context:
{clarification_answers}

Provide a thoughtful response that includes:
1. A summary recommendation (2-3 sentences)
2. Key considerations (3-5 bullet points)
3. 5 high-quality external links for further research (format: title, URL, brief description)

Be balanced, educational, and encourage the user to do their own research. Never provide definitive "buy" or "sell" advice.
```

## Success Metrics (MVP)

- [ ] User can complete a research session in < 5 minutes
- [ ] AI responses are relevant and helpful
- [ ] Token costs are tracked accurately
- [ ] App works on Mac and Windows
- [ ] No crashes or major bugs
- [ ] User (you) finds it more helpful than Google alone

## Post-MVP Roadmap (Phase 2)

1. **Pre-Market Movers Module**
   - Track news and price movements
   - Strategy execution tracking

2. **Fallen Angels Analysis**
   - Historical price tracking
   - Filtering and analysis tools

3. **Advanced Stock Research**
   - Technical indicators (Bollinger Bands, RSI, etc.)
   - Fundamental data integration
   - Company financials

4. **React Frontend**
   - Better UX for complex interactions
   - Real-time updates
   - Richer visualizations

5. **MCP Integration**
   - Real-time market data
   - News aggregation
   - Portfolio tracking

## Risk Mitigation

**Risk:** Token costs spiral out of control
**Mitigation:**
- Implement hard limits before MVP launch
- Cache responses aggressively
- Use smaller models where appropriate

**Risk:** AI responses are not helpful
**Mitigation:**
- Test prompts extensively
- Iterate on prompt templates
- Add feedback mechanism

**Risk:** Too complex for MVP
**Mitigation:**
- Strictly limit scope to core research flow
- Defer all advanced features to Phase 2
- Focus on one use case working well
