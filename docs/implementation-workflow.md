# Implementation Workflow & Next Steps

## Current Status

✅ **Planning Phase Complete**

You now have:
- `.claude/` directory with project context and settings
- `.claudeignore` to keep AI context focused
- `/docs` with comprehensive planning documents
- Custom slash commands for Django development
- README with setup instructions

## What's Been Created

### Documentation Structure

```
picker/
├── .claude/
│   ├── settings.json              # Claude Code configuration
│   ├── project-context.md         # Project intent and design principles
│   └── commands/                  # Custom slash commands
│       ├── migrate.md             # /migrate - Run migrations
│       ├── runserver.md           # /runserver - Start dev server
│       ├── shell.md               # /shell - Django shell
│       ├── test.md                # /test - Run tests
│       ├── check.md               # /check - System checks
│       ├── create-app.md          # /create-app - New Django app
│       └── token-usage.md         # /token-usage - Check AI usage
├── docs/
│   ├── architecture.md            # System architecture & design
│   ├── mvp-plan.md               # Development roadmap
│   ├── tech-decisions.md         # Technical choices & rationale
│   ├── data-model.md             # Database schema & models
│   └── implementation-workflow.md # This file
├── .claudeignore                  # Files to exclude from AI context
├── .env.example                   # Environment variables template
└── README.md                      # Setup and usage guide
```

## Recommendations Before Implementation

### 1. Review Documentation

**Priority: HIGH**

Read through these docs to understand the full plan:

1. **Start here:** `README.md` - Overview and setup instructions
2. **Understand the vision:** `.claude/project-context.md` - Project goals and principles
3. **See the roadmap:** `docs/mvp-plan.md` - What we're building and when
4. **Understand technical choices:** `docs/tech-decisions.md` - Why Django, why these tools
5. **Review architecture:** `docs/architecture.md` - How it all fits together
6. **Study the data model:** `docs/data-model.md` - Database structure

### 2. Consider Django vs. Lighter Approach

**Decision Point: Choose Your Starting Framework**

The docs assume Django, but given your project scope, consider:

**Option A: Django (Recommended in docs)**
- ✅ Built for complex apps that will grow
- ✅ Admin panel out of the box
- ✅ ORM handles relationships well
- ❌ More setup overhead
- ❌ Heavier for initial MVP

**Option B: FastAPI + SQLModel (Alternative)**
- ✅ Lighter, faster to prototype
- ✅ Modern Python (async, type hints)
- ✅ Auto-generated API docs
- ❌ Need to add admin separately
- ❌ Less "batteries included"

**Option C: Flask + SQLAlchemy (Middle ground)**
- ✅ Lightweight but mature
- ✅ Flexible, unopinionated
- ❌ Need to choose more components

**My recommendation:** Stick with Django given:
- You want "pretty complex by the end"
- Built-in admin helps manage data
- Strong ecosystem for adding React later
- Better suited for session management and complex queries

### 3. Check with Codex (As You Mentioned)

Before implementing, you may want to:

1. Review the architecture with a fresh AI perspective
2. Validate the data model design
3. Get input on Django app structure
4. Discuss AI prompt strategies for investment research

**Suggestion:** Share these docs with Codex/another AI and ask:
- "Review this architecture - any red flags?"
- "Is this data model normalized correctly?"
- "Suggestions for the MVP scope?"

## Codex Review Notes - Incorporated

✅ **Focus on end-to-end research loop first** - MVP prioritizes complete question → clarifications → response → saved session flow before adding watchlist or dashboards. This keeps the implementation aligned.

✅ **AI service fallback (stub client)** - Created comprehensive ClaudeClient interface pattern in `docs/claude-client-interface.md`. Includes both LiveClaudeClient and StubClaudeClient implementations so development isn't blocked by API availability.

✅ **Error handling checklist** - Added acceptance criteria in `docs/mvp-plan.md` for handling Claude timeouts, malformed JSON, network errors, and graceful degradation.

📝 **Slash command consistency** - Will update `/token-usage` command documentation once the actual reporting script is implemented to ensure it stays in sync.

## Implementation Order (When Ready)

### Phase 0: Environment Setup (30 minutes)

```bash
# 1. Initialize Django project
django-admin startproject picker .

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install Django and dependencies
pip install django anthropic python-decouple
pip freeze > requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# 5. Initial Django configuration
python manage.py migrate
python manage.py createsuperuser

# 6. Test it works
python manage.py runserver
```

### Phase 1A: Create Django Apps (1 hour)

```bash
# Create the core apps
python manage.py startapp research
python manage.py startapp stocks
python manage.py startapp ai_service
python manage.py startapp core

# Add to INSTALLED_APPS in picker/settings.py
```

### Phase 1B: Define Models (2 hours)

Implement the models from `docs/data-model.md`:

1. `research/models.py` - ResearchSession, Clarification, etc.
2. `stocks/models.py` - WatchlistItem
3. `ai_service/models.py` - TokenUsageLog (with extended fields)

**Key changes from Codex review:**
- Add `created_at`/`updated_at` to UserResponse
- Add `model`, `prompt_tokens`, `completion_tokens` to TokenUsageLog
- Add unique constraint on ClarificationQuestion (session + order)

Then:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Phase 1C: AI Service Layer (3-4 hours)

Implement the ClaudeClient interface pattern (see `docs/claude-client-interface.md`):

1. Create `ai_service/client_interface.py` - Abstract base class
2. Create `ai_service/live_client.py` - Real Anthropic API client
3. Create `ai_service/stub_client.py` - Stub for development/testing
4. Create `ai_service/client_factory.py` - Factory to get appropriate client
5. Add `USE_STUB_AI` to settings

Test in Django shell:
```bash
python manage.py shell
>>> from ai_service.client_factory import get_claude_client
>>> client = get_claude_client()  # Returns stub or live based on config
>>> response = client.generate_clarifications("Should I invest in bonds?")
>>> print(response.content)
>>> print(response.token_usage)
```

**Benefits:**
- Can develop without API key (use stub)
- Tests don't consume API credits
- Easy to swap implementations
- Centralized error handling

### Phase 1D: Views and Templates (4-6 hours)

1. Create basic templates with Tailwind CSS
2. Implement views for:
   - Ask question form
   - Clarification form
   - Response display
   - Session list
3. Wire up URLs

### Phase 1E: Admin Interface (1 hour)

Register models in `admin.py` for each app:

```python
from django.contrib import admin
from .models import ResearchSession, ResearchResponse

@admin.register(ResearchSession)
class ResearchSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'original_question']
```

### Phase 1F: Testing & Refinement (2-3 hours)

1. Manual testing of complete workflow
2. Test on Windows (if Mac is primary dev)
3. Fix bugs and improve UX
4. Add error handling

### Total Estimated MVP Time: 15-20 hours

## Settings & Configuration

### Enhanced Settings for Claude Code

You may want to update `.claude/settings.json`:

```json
{
  "statusLine": {
    "enabled": true,
    "format": "Picker {{workingDirectory}} | Django"
  },
  "hooks": {
    "userPromptSubmit": null,
    "toolCall": null
  }
}
```

### Git Configuration (Recommended)

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
venv/
*.sqlite3

# Environment
.env

# IDE
.vscode/
.idea/
.DS_Store

# Django
staticfiles/
media/
```

Initialize git:
```bash
git init
git add .
git commit -m "Initial project setup with documentation"
```

## Available Slash Commands

Once you start implementing, use these commands:

- `/migrate` - Run database migrations
- `/runserver` - Start the development server
- `/shell` - Open Django shell for testing
- `/test` - Run test suite
- `/check` - Check for Django issues
- `/create-app` - Create a new Django app
- `/token-usage` - Check AI token usage

## Questions to Resolve Before Coding

1. **Do you want to start with Django as planned?**
   - Or would you prefer a lighter framework?

2. **Should we implement all MVP features?**
   - Or start with just the core research flow?

3. **React integration timing?**
   - Phase 1 (Django templates only)?
   - Add React in Phase 2?

4. **Deployment target?**
   - Local only for MVP?
   - Docker container?
   - Deploy to cloud?

5. **Testing approach?**
   - Manual testing for MVP?
   - Write tests as we go?
   - Add tests in Phase 2?

## Getting Codex/AI Review

**Suggested prompts for review:**

1. Architecture Review:
   ```
   "I'm building an investment research assistant. Review this architecture document and identify any potential issues or improvements: [attach architecture.md]"
   ```

2. Data Model Validation:
   ```
   "Review this Django data model for an investment research app. Check for normalization, missing relationships, or better approaches: [attach data-model.md]"
   ```

3. MVP Scope Check:
   ```
   "Is this MVP scope appropriate for a first version? What would you prioritize or defer? [attach mvp-plan.md]"
   ```

4. Django Best Practices:
   ```
   "Review this Django app structure and suggest best practices for organizing an investment research tool: [attach architecture.md app structure]"
   ```

## Next Actions (Your Choice)

**Option 1: Start Implementing**
- Begin with Phase 0: Environment Setup
- Follow the implementation order above
- Use Claude Code and slash commands

**Option 2: Review & Refine**
- Get Codex review on architecture
- Refine plans based on feedback
- Make any adjustments before coding

**Option 3: Prototype First**
- Build a simple proof-of-concept
- Just question → AI response → save
- Validate the concept before full build

**Option 4: Deep Dive Planning**
- Write detailed prompt templates
- Plan UI mockups
- Define exact API contracts
- More detailed task breakdown

## Conclusion

You're well-positioned to start building! The documentation provides:

✅ Clear project vision and goals
✅ Comprehensive architecture design
✅ Detailed data model and relationships
✅ Phase-by-phase implementation plan
✅ Technical decisions with rationale
✅ Setup instructions for Mac and Windows
✅ Custom Claude Code commands for Django dev

**Recommendation:**
1. Review the docs (30 min)
2. Run by Codex if desired (15 min)
3. Start with Phase 0 environment setup (30 min)
4. Build Phase 1A-1C (models + AI service) to validate approach (4-6 hours)
5. Then continue with full MVP

Let me know when you're ready to start coding, and I'll help implement each phase!
