# Picker - Investment Research Assistant

## Project Overview

Picker is a Django-based investment research tool designed to help identify and analyze pre-market stock movers for day trading opportunities. The core workflow involves discovering stocks with significant pre-market movement, researching the catalyst (news), analyzing volume/liquidity metrics, and using AI (Claude) to evaluate trade potential.

**Key Strategy:** Buy news-driven movers at market open, sell on upward momentum.

---

## Tech Stack

- **Framework:** Django 5.0
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **AI Integration:** Anthropic Claude API (Haiku for fast analysis, Sonnet for complex research)
- **Market Data APIs:**
  - yfinance (free, real-time quotes and pre-market data)
  - Finnhub (news and company data)
  - Financial Modeling Prep (planned for discovery)
- **Frontend:** Tailwind CSS, vanilla JavaScript
- **Python:** 3.11+

---

## Project Structure

```
picker/
├── config/              # Django project settings
│   ├── settings.py      # Main settings (API keys via .env)
│   └── urls.py          # Root URL configuration
├── core/                # User authentication and base templates
│   ├── views.py         # Login/logout
│   └── templates/       # Base template with dark mode
├── strategies/          # Pre-Market Movers feature (main app)
│   ├── models.py        # PreMarketMover model with volume metrics
│   ├── views.py         # Dashboard, scanner, quick-add, AI analysis
│   ├── stock_data.py    # yfinance integration, StockData class
│   ├── finnhub_service.py  # Finnhub API client
│   ├── watchlists.py    # Predefined symbol lists
│   ├── management/commands/
│   │   └── scan_premarket_movers.py  # CLI scanner
│   ├── templatetags/
│   │   └── stock_filters.py  # Custom template filters
│   └── templates/strategies/
│       └── pre_market_movers.html  # Main dashboard
├── ai_service/          # Claude API integration (abstract pattern)
│   ├── client_interface.py  # Abstract base class
│   ├── live_client.py   # Production Claude client
│   ├── stub_client.py   # Development stub
│   ├── client_factory.py  # Factory pattern for client selection
│   └── models.py        # TokenUsageLog for cost tracking
├── docs/                # Comprehensive documentation
│   ├── PHASE_1_VOLUME_METRICS_REVIEW.md  # Current work (Volume metrics + discovery plan)
│   ├── FINNHUB_INTEGRATION.md
│   ├── AUTOMATED_SCANNER_SETUP.md
│   └── ...
├── .env                 # API keys (gitignored)
├── .env.example         # Template for environment variables
└── requirements.txt     # Python dependencies
```

---

## Key Models

### PreMarketMover (`strategies/models.py`)

Tracks stocks with significant pre-market movement.

**Core Fields:**
- `symbol` - Stock ticker
- `company_name` - Company name
- `news_headline`, `news_source`, `news_url` - Catalyst information
- `movement_percent` - % change from previous close
- `pre_market_price` - Current pre-market price

**Phase 1: Volume Metrics (Oct 2025)**
- `pre_market_volume` - Current trading volume
- `average_volume` - 3-month average (from yfinance)
- `relative_volume_ratio` (RVOL) - Pre-market vol / Avg vol (>3.0 = strong conviction)
- `spread_percent` - Bid-ask spread % (<1% = good liquidity, >2% = illiquid)

**AI Analysis:**
- `ai_analysis` - Claude-generated analysis
- `sentiment` - bullish/bearish/neutral

**Status Workflow:**
- `identified` → `researching` → `ready` → `executed` → `passed`

---

## Important Design Patterns

### 1. AI Client Abstract Pattern
**Why:** Support both production (Claude API) and development (stub) without changing business logic.

**Files:**
- `ai_service/client_interface.py` - Abstract base class
- `ai_service/live_client.py` - Real Claude API calls
- `ai_service/stub_client.py` - Fixed responses for testing
- `ai_service/client_factory.py` - `get_claude_client()` selects based on settings

**Usage:**
```python
client = get_claude_client()  # Returns live or stub based on USE_LIVE_CLAUDE setting
response = client.analyze_stock_opportunity(prompt)
```

### 2. Volume Metrics as Computed Properties
**Why:** Keep database clean, calculate on-the-fly from API data.

**Pattern:**
```python
class StockData:
    @property
    def relative_volume_ratio(self) -> Optional[float]:
        if self.average_volume and self.average_volume > 0:
            current_vol = self.pre_market_volume or self.regular_market_volume
            return current_vol / self.average_volume if current_vol > 0 else None
        return None
```

### 3. Graceful Data Handling
**Why:** Market data APIs are unreliable, especially off-hours.

**Pattern:**
- Always return `None` for missing data, never crash
- UI displays "—" for None values
- Log warnings, don't raise exceptions

---

## API Key Management

**Environment Variables (.env):**
```bash
ANTHROPIC_API_KEY=sk-ant-...
FINNHUB_API_KEY=xxxxx
USE_LIVE_CLAUDE=True  # False for stub mode
```

**Settings Access:**
```python
# config/settings.py
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
USE_LIVE_CLAUDE = os.getenv('USE_LIVE_CLAUDE', 'False') == 'True'
```

---

## Common Tasks

### Run Development Server
```bash
python manage.py runserver
```

### Scan for Pre-Market Movers (CLI)
```bash
# Scan default watchlist
python manage.py scan_premarket_movers --watchlist default --threshold 5.0

# Dry run (test without creating records)
python manage.py scan_premarket_movers --dry-run

# Skip news fetching (faster testing)
python manage.py scan_premarket_movers --skip-news
```

### Create Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell
```bash
python manage.py shell
```

---

## Current Development Phase (Oct 2025)

### ✅ Completed: Phase 1 - Volume Metrics
- Added RVOL, spread, and volume tracking to distinguish tradeable opportunities from noise
- Integrated metrics into scanner, web UI, and tracked movers
- All Codex review issues resolved
- **Status:** Production-ready

### 🔄 In Progress: Discovery Implementation
**Problem:** User wants auto-populated movers list without manual symbol entry.

**Solution (Hybrid Approach):**
1. **Option A:** Test Financial Modeling Prep free API for gainers/losers endpoint
2. **Option B:** Build comprehensive universe (700-1000 symbols) with automated 6AM scan
3. **Hybrid:** Try FMP first, fallback to comprehensive scan if FMP fails

**Timeline:** 1-2 weeks for implementation and testing

### 📋 Planned: Future Phases
- **Phase 2:** Momentum Score calculation (price × volume × sentiment)
- **Phase 3:** Float, short interest, squeeze detection
- **Phase 4:** Market context (futures), VWAP, pre-market range
- **Phase 5:** Time-based filters, fresh catalyst alerts

---

## Code Style & Standards

### Python
- Type hints preferred: `def get_stock_data(symbols: List[str]) -> List[StockData]`
- Docstrings for all public methods
- Use `logger.warning()` for expected failures, `logger.error()` for unexpected
- Never crash on missing market data - return `None` and handle gracefully

### Django Templates
- Use Tailwind CSS utility classes
- Always include dark mode variants: `text-gray-900 dark:text-gray-100`
- Load custom template tags: `{% load stock_filters %}`
- Use `|format_volume` filter for volume display

### Database
- `null=True, blank=True` for optional market data fields (may be missing)
- `help_text` on all non-obvious fields
- Indexes on frequently queried fields (`identified_date`, `status`)

### API Integration
- Wrap all API calls in try/except
- Log API errors with context (symbol, endpoint)
- Implement rate limit handling (sleep, backoff)
- Cache when appropriate (e.g., average volume doesn't change intraday)

---

## Codex Code Review Process

### Role Definition

**Claude Code (AI Assistant):** LEAD DEVELOPER
- Final decision authority on all implementation choices
- Responsible for architecture, code quality, and feature design
- Reviews Codex suggestions and decides what to implement

**Codex (AI Reviewer):** CODE REVIEWER
- Provides suggestions and identifies potential issues
- Reviews completed work for bugs, improvements, and edge cases
- Suggestions are advisory - Claude Code has final say

**Jack (Product Owner):** DECISION MAKER
- Tests features manually
- Provides product requirements and UX feedback
- Approves final implementation before moving to next phase

### Automatic Review Document Creation

**IMPORTANT:** At the completion of each phase, Claude Code MUST automatically create a review document without being asked.

**Trigger Points:**
1. All phase requirements completed
2. Manual testing confirmed working
3. Ready to move to next phase

**Action:** Create `docs/PHASE_X_FEATURE_NAME_REVIEW.md` and inform user it's ready for Codex review.

### Document Structure Template

```markdown
# Phase X: [Feature Name] - Implementation Review

**Date:** YYYY-MM-DD
**Status:** Complete / Awaiting Codex Review
**Lead Developer:** Claude Code
**Reviewer:** Codex
**Next Phase:** [What's planned next]

## Executive Summary
- [3-5 bullet points of what was accomplished]
- [Key metrics: files changed, features added, tests passing]

## Implementation Details

### Architecture Changes
- [High-level design decisions]
- [Patterns used and why]

### Files Modified
1. `path/to/file.py` (lines X-Y) - [Purpose]
2. `path/to/other.py` (lines A-B) - [Purpose]

### Database Changes
- [Schema updates]
- [Migration commands]

### New Features
1. **[Feature Name]** - [Description]
   ```python
   # Code example with line numbers
   # strategies/views.py:150-175
   ```

2. **[Feature Name]** - [Description]
   ```python
   # Code example
   ```

## Testing Guide

### Manual Testing Steps
1. [Step-by-step instructions]
2. [Expected results]
3. [Edge cases to verify]

### Known Limitations
- [List any known issues or constraints]

## Questions for Codex

1. **Architecture:** [Specific question about design choice]
2. **Performance:** [Concerns about scalability]
3. **Edge Cases:** [Unusual scenarios that need validation]
4. **Alternatives:** [Other approaches considered]

## Next Phase Plan

**Phase X+1: [Next Feature]**
- [High-level overview]
- [Dependencies]
- [Estimated timeline]

---

## Codex Review #1 - [Date]

### Blocking Issues
[To be filled by Codex]

### High-Priority Suggestions
[To be filled by Codex]

### Questions / Clarifications
[To be filled by Codex]

---

## Claude Code's Analysis of Codex Review #1

### ✅ Accepted Suggestions
**Issue:** [Codex finding]
**Reasoning:** [Why I agree]
**Action:** [What I'll implement]

**Issue:** [Another finding]
**Reasoning:** [Why I agree]
**Action:** [What I'll implement]

### ❌ Rejected Suggestions
**Issue:** [Codex finding]
**Reasoning:** [Why I disagree - technical justification]
**Decision:** [What I'm keeping and why]

### 💭 Discussion Points
**Issue:** [Codex question]
**My Perspective:** [Explanation of current approach]
**Open to:** [Alternative if compelling reason provided]

---

## Codex Review Fixes - [Date]

### Changes Implemented
1. **[Fix description]**
   - File: `path/to/file.py:line-numbers`
   - Before: [Code snippet]
   - After: [Code snippet]
   - Why: [Reasoning]

2. **[Another fix]**
   - [Details]

### Validation
- [ ] Manual testing confirms fix works
- [ ] No regressions introduced
- [ ] Documentation updated if needed

---

## Codex Review #2 - [Date]
[Repeat structure for subsequent reviews]
```

### Best Practices

1. **Include line numbers** - Reference specific files and lines (e.g., `strategies/views.py:170-181`)
2. **Show code examples** - Include actual code snippets from implementation
3. **Document all changes** - List every modified file with purpose
4. **Add testing steps** - Provide clear instructions for validation
5. **Ask specific questions** - Don't just ask "looks good?", ask about specific concerns
6. **Analyze Codex feedback** - Explicitly state what you agree/disagree with and why
7. **Keep history** - Show progression of fixes across multiple reviews
8. **Be decisive** - As lead, make clear architectural decisions with reasoning

### Review Flow

1. **Phase Completion**
   - Claude Code completes all phase requirements
   - User tests manually and confirms working
   - Claude Code AUTOMATICALLY creates review document
   - Claude Code: "Phase X complete. Created `docs/PHASE_X_REVIEW.md` for Codex review."

2. **Codex Review**
   - User sends document to Codex
   - Codex fills in "Blocking Issues", "High-Priority", "Questions" sections
   - User pastes Codex feedback back into document

3. **Claude Code Analysis**
   - Claude Code reads Codex feedback
   - Claude Code adds "Claude Code's Analysis" section with:
     - ✅ What I'm implementing and why
     - ❌ What I'm rejecting and why
     - 💭 Discussion points worth exploring
   - Claude Code implements accepted suggestions
   - Claude Code documents all changes in "Codex Review Fixes" section

4. **Iteration**
   - User sends updated doc to Codex for second review
   - Repeat until Codex has no blocking issues
   - User does final manual testing
   - Move to next phase

5. **Conflict Resolution**
   - If Codex insists on something Claude Code disagrees with:
     - Claude Code provides detailed technical reasoning
     - Claude Code asks user (Jack) to make final call
     - Jack's decision is final

### Example Analysis Section

```markdown
## Claude Code's Analysis of Codex Review #1

### ✅ Accepted Suggestions

**Issue:** Documentation claims "10-day average" but implementation uses 3-month average
**Reasoning:** This is a factual error that creates confusion. Codex is correct.
**Action:** Update all documentation to accurately reflect "3-month average via yfinance `averageVolume` field"

**Issue:** Missing API key setup instructions for FMP
**Reasoning:** Users need clear setup steps. This improves documentation quality.
**Action:** Add Step 1 to testing section with FMP API key setup and apikey parameter note

### ❌ Rejected Suggestions

**Issue:** Should use asyncio for parallel API requests to improve scan speed
**Reasoning:** While asyncio would be faster, it adds significant complexity for marginal gain:
- Current scan completes in 2-5 minutes for 410 symbols (acceptable)
- yfinance library doesn't support async natively, would require full rewrite
- Synchronous code is easier to debug and maintain
- Performance optimization is not a phase goal
**Decision:** Keep synchronous implementation. Can revisit in Phase 6 if speed becomes a bottleneck.

**Issue:** Should create new comprehensive_universe.py file
**Reasoning:** This creates duplicate symbol management. Better to extend existing market_universe.py:
- Avoids maintaining two separate files
- All universes in one place for easier updates
- Consistent with existing architecture
**Decision:** Extend market_universe.py instead of creating new file

### 💭 Discussion Points

**Issue:** Should we add rate limiting protection for yfinance?
**My Perspective:** Currently not needed because:
- Scanning 410 symbols takes 2-5 minutes naturally (spread out requests)
- yfinance has internal retry logic
- We've seen no rate limit errors in testing
**Open to:** Adding explicit rate limiting if we see 429 errors in production logs
```

### Current Example

See `docs/PHASE_1_VOLUME_METRICS_REVIEW.md` (1000+ lines) for a complete example including:
- Initial implementation details
- First Codex review feedback
- All fixes documented with code samples
- Second review addressing new findings
- Discovery API research and implementation plan

---

## Testing Strategy

### Manual Testing
- Test scanner during pre-market hours (4:00-9:30 AM ET) for real data
- Verify volume metrics populate correctly
- Check dark mode readability
- Test with both real and missing data (market closed)

### Edge Cases to Consider
- Market closed (no pre-market data)
- Symbol doesn't exist (yfinance returns empty)
- API rate limits hit
- Missing bid/ask (spread_percent = None)
- Zero average volume (avoid division by zero)

---

## Deployment Notes

### Production Checklist
- [ ] Set `DEBUG = False` in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure static files (collectstatic)
- [ ] Set up SSL/HTTPS
- [ ] Use environment variables for all secrets
- [ ] Set up cron job for automated scanning (6AM weekdays)
- [ ] Monitor yfinance data quality (may need Finnhub fallback)
- [ ] Consider Polygon.io upgrade ($29/mo) for reliable discovery

### Server Requirements
- Python 3.11+
- 512MB RAM minimum (1GB recommended for scanning 1000 symbols)
- Timezone: Set to ET (America/New_York) for accurate pre-market timing

---

## Troubleshooting

### Scanner returns no movers
- **Check market hours:** Pre-market data only available 4:00-9:30 AM ET
- **Lower threshold:** Try `--threshold 2.0` instead of 5.0
- **Check yfinance:** May be rate limited or down

### Volume metrics showing "—" in UI
- **Normal off-hours:** yfinance doesn't provide bid/ask when market closed
- **Check API response:** Use Django shell to inspect StockData object
- **Consider Finnhub fallback:** If consistently missing during pre-market

### AI analysis returns {"valid": true} instead of analysis
- **Fixed in Oct 2025:** Updated to use `analyze_stock_opportunity()` method
- **Check client type:** Ensure using correct method (not `validate_question()`)

---

## Documentation

- **Primary Review Doc:** `docs/PHASE_1_VOLUME_METRICS_REVIEW.md` (comprehensive, updated Oct 30, 2025)
- **Finnhub Integration:** `docs/FINNHUB_INTEGRATION.md`
- **Scanner Setup:** `docs/AUTOMATED_SCANNER_SETUP.md`
- **All docs in:** `/docs` directory

---

## Contact & Context

**Project Owner:** Jack Blacketter
**Development Started:** October 2025
**AI Assistant:** Claude Code (Anthropic)
**Primary Use Case:** Personal day trading research tool

---

## Notes for Claude

- **Always read** `docs/PHASE_1_VOLUME_METRICS_REVIEW.md` for latest context
- **Volume metrics** are the current focus - RVOL and spread are critical for filtering noise
- **Discovery** is the next priority - user wants auto-populated movers list
- **Prefer editing** existing files over creating new ones
- **Dark mode** must always work - test all UI changes in both modes
- **Market data is unreliable** - always handle None gracefully
- **yfinance is free but unofficial** - may need paid alternatives (Polygon, Finnhub) for production
- **Cost tracking** is important - log all Claude API token usage
- **User is a trader** - understands market mechanics, wants actionable data fast

---

Last Updated: October 30, 2025
