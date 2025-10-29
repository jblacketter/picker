# Finnhub Integration - Market Movers Enhancement

**Date:** October 29, 2025
**Status:** Phase 1 Complete - Automated News Fetching
**API Provider:** Finnhub.io

---

## Overview

This document outlines the integration of Finnhub API into the Picker Pre-Market Movers strategy to automate news discovery and enhance trading research workflow.

## Problem Statement

The original implementation required manual entry of news headlines, sources, and URLs for each tracked stock. This created friction in the workflow and slowed down the research process during critical pre-market hours.

## Solution Implemented

### Phase 1: Automated News Fetching (✅ Complete)

Integrated Finnhub API to automatically fetch and populate news data when tracking stocks and performing research.

---

## Changes Made

### 1. New Files Created

**`strategies/finnhub_service.py`** - Finnhub API Client Module
- `FinnhubClient` class for API interactions
- `get_company_news()` - Fetch recent company news (up to 7 days back)
- `get_quote()` - Real-time stock quotes
- `get_market_status()` - Market session detection (pre/regular/post)
- `get_top_news()` - General market news
- Convenience functions: `get_latest_news()`, `get_top_news_article()`
- Error handling and logging throughout

### 2. Configuration Updates

**`config/settings.py`**
```python
# Market Data API Configuration
FINNHUB_API_KEY = config('FINNHUB_API_KEY', default='')
```

**`.env`**
```bash
# Finnhub Market Data API
FINNHUB_API_KEY=your_finnhub_api_key_here
```

### 3. View Logic Enhancements

**`strategies/views.py`** - Updated Functions:

#### `quick_add_mover()` - Auto-fetch news when tracking from scan
```python
# New workflow:
1. User clicks "+ Track" on scan result
2. System fetches latest news from Finnhub
3. Populates headline, source, and URL automatically
4. Creates mover with real news data
5. Falls back to generic headline if news fetch fails
```

#### `analyze_mover()` - Auto-update news before AI analysis
```python
# New workflow:
1. User clicks "Research This"
2. Check if headline is generic (e.g., "Pre-market movement: +5%")
3. If generic, fetch latest news from Finnhub and update mover
4. Pass real news context to Claude AI
5. AI provides better analysis with actual news catalyst
```

---

## User Experience Improvements

### Before:
1. Scan for movers → See price changes
2. Click "+ Track"
3. **Manually Google the stock to find news**
4. **Copy/paste headline, source, URL into form**
5. Click "Research This"
6. Get AI analysis (without full news context)

### After:
1. Scan for movers → See price changes
2. Click "+ Track"
3. **News automatically fetched and populated** ✨
4. Click "Research This"
5. **News auto-updated if needed** ✨
6. Get AI analysis with real news catalyst ✨

**Time Saved:** ~2-3 minutes per stock tracked

---

## Testing Results

### API Connection Test
```
✓ Finnhub API authenticated successfully
✓ Fetched 10 news articles for AAPL
✓ Current price data retrieved ($268.97, -0.01%)
✓ Market status detected (US market, regular session)
```

### Integration Test
```
✓ Quick-add workflow: News auto-fetched for TSLA
  Headline: "Nvidia's AI self-driving cars get into Tesla's lane"
  Source: Yahoo

✓ Analyze workflow: Generic headline auto-updated for AAPL
  Before: "Pre-market movement: +2.5%"
  After: "What time does Meta report earnings Wednesday? Here's how to tune in"
```

### Error Handling
```
✓ Graceful fallback to generic headline if Finnhub fails
✓ Logging for all API calls and errors
✓ No user-facing errors during failure scenarios
```

---

## Technical Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Action: Click "+ Track" or "Research This"            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Django View (quick_add_mover / analyze_mover)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Finnhub Service: get_top_news_article(symbol)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Finnhub API: GET /company-news                             │
│  - Returns last 7 days of news                              │
│  - Sorted by datetime (most recent first)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Parse Response: Extract headline, summary, source, url     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Update PreMarketMover Model                                │
│  - news_headline, news_source, news_url populated           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  AI Analysis (if requested)                                 │
│  - Claude receives news context                             │
│  - Generates sentiment + trading implications               │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints Used

| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `/company-news` | Fetch company-specific news | 60 calls/min |
| `/quote` | Real-time stock quotes | 60 calls/min |
| `/stock/market-status` | Market session detection | 60 calls/min |

### Error Handling Strategy

1. **Network Failures**: Log warning, use generic headline, continue workflow
2. **Invalid Symbols**: Return empty news array, use fallback
3. **Rate Limiting**: Graceful degradation (future: add caching)
4. **Malformed Responses**: Safe parsing with defaults

---

## Future Enhancements (Roadmap)

### Phase 2: Automated Morning Scanner (Planned)

**Goal:** Eliminate manual symbol entry by auto-scanning a watchlist pre-market

**Implementation:**
- Django management command: `python manage.py scan_premarket_movers`
- Runs via cron at 8:00 AM ET (pre-market hours)
- Scans predefined watchlist (configurable in settings)
- Auto-identifies stocks with >5% movement
- Fetches news for all movers
- Sends email/notification summary
- Populates dashboard with results

**Files to Create:**
- `strategies/management/commands/scan_premarket_movers.py`
- `strategies/watchlist.py` (configurable stock lists)
- Email template for morning summary

**Estimated Effort:** 2-3 hours

---

### Phase 3: Market Status Detection (Planned)

**Goal:** Adapt behavior based on market session

**Implementation:**
- Display current market session in UI (pre/regular/post/closed)
- Different scanning strategies per session:
  - Pre-market: Focus on news-driven moves
  - Regular: Use volume + price action
  - After-hours: Earnings reactions
- Visual indicators for session type
- Warning if scanning during closed hours

**Files to Modify:**
- `strategies/views.py` - Add market status to context
- `strategies/templates/pre_market_movers.html` - Display session badge
- `strategies/finnhub_service.py` - Add `get_current_session()` helper

**Estimated Effort:** 1-2 hours

---

### Phase 4: Enhanced AI Analysis (Planned)

**Goal:** More actionable trading insights from Claude

**Current AI Output:**
```json
{
  "analysis": "Brief 2-3 sentence overview",
  "sentiment": "bullish/bearish/neutral"
}
```

**Proposed Enhanced Output:**
```json
{
  "analysis": "Detailed catalyst explanation",
  "sentiment": "bullish",
  "confidence": "high",
  "entry_strategy": "Wait for 9:35 AM for opening volatility to settle. Enter at $150-152 range.",
  "exit_targets": ["$158 (5% gain)", "$162 (8% gain - stretch)"],
  "stop_loss": "$147 (2% max loss)",
  "risk_reward_ratio": "3:1",
  "key_catalysts": ["FDA approval announcement", "Analyst upgrade from JPM"],
  "risks": ["High IV, potential profit-taking at open"]
}
```

**Implementation:**
- Update AI prompt in `analyze_mover()` function
- Add new fields to `PreMarketMover` model (migration required)
- Enhanced UI to display entry/exit targets
- Risk management calculator

**Estimated Effort:** 3-4 hours

---

### Phase 5: Finnhub Webhooks (Future)

**Goal:** Real-time alerts for breaking news

**Webhook Secret:** `your_finnhub_webhook_secret_here`

**Implementation:**
- Django view to receive webhook events
- Authenticate via `X-Finnhub-Secret` header
- Process news events in real-time
- Send push notifications for tracked stocks
- Auto-trigger research for significant news

**Files to Create:**
- `strategies/webhooks.py` - Webhook receiver
- URL route: `/webhooks/finnhub/`
- Notification service integration (email/SMS)

**Estimated Effort:** 4-5 hours

---

### Phase 6: Historical Performance Analytics (Future)

**Goal:** Learn which news types correlate with successful trades

**Features:**
- Track outcome of each trade (profit/loss)
- Categorize news by type (earnings, FDA, merger, analyst, etc.)
- Calculate win rate by news category
- Identify best-performing patterns
- ML-based suggestions for similar setups

**Files to Create:**
- `strategies/analytics.py` - Performance calculations
- New template: `pre_market_analytics.html`
- Charts/visualizations (Chart.js or similar)

**Estimated Effort:** 6-8 hours

---

## API Limits & Costs

### Finnhub Free Tier
- **Rate Limit:** 60 API calls/minute, 30 calls/second
- **Daily Quota:** Unlimited for news endpoints
- **Cost:** Free (current plan)

### Current Usage Estimate
- **Per stock tracked:** 1 API call (news fetch)
- **Per research action:** 1 API call (news update if needed)
- **Morning scanner:** ~50-100 API calls (if scanning 50 symbols)

**Daily Estimated Usage:** 100-200 calls (well within limits)

### Upgrade Considerations
If we exceed free tier limits:
- **Premium Plan:** $49/month for 300 calls/min
- **Professional Plan:** $99/month for 600 calls/min

---

## Code Quality & Maintainability

### Logging
All Finnhub interactions are logged:
```python
logger.info(f"Fetched {len(articles)} news articles for {symbol}")
logger.warning(f"Could not fetch news for {symbol}: {e}")
logger.error(f"Finnhub API request failed: {e}")
```

### Error Handling
- All API calls wrapped in try/except blocks
- Graceful fallbacks for all failure modes
- No user-facing errors during API failures

### Testing
- Manual integration tests completed
- End-to-end workflow validation
- API connection verification

**Future:** Add automated unit tests for `finnhub_service.py`

---

## Security Considerations

### API Key Management
- ✅ API key stored in `.env` file (not committed to git)
- ✅ Settings use `config()` for environment variable loading
- ✅ Default empty string if key not configured

### Webhook Security (Future)
- Authenticate via `X-Finnhub-Secret` header
- Validate request signatures
- Rate limiting on webhook endpoint
- HTTPS required in production

---

## Deployment Notes

### Environment Variables Required
```bash
# Add to production .env
FINNHUB_API_KEY=your_finnhub_api_key_here
```

### Dependencies
No new Python packages required - uses standard `requests` library

### Database Migrations
No schema changes in Phase 1

**Future:** Phase 4 will require migration for new AI analysis fields

---

## Success Metrics

### Goals
- [ ] Reduce time spent on manual news entry by 80%
- [ ] Increase number of stocks researched per session by 2x
- [ ] Improve AI analysis quality with real news context
- [ ] Enable morning automation to save 30 min/day

### Current Progress
- ✅ Automated news fetching working
- ✅ Integration with existing workflow complete
- ✅ Error handling robust
- ✅ Zero breaking changes to existing features

---

## Appendix: Finnhub API Reference

### Company News Endpoint
```
GET https://finnhub.io/api/v1/company-news
Parameters:
  - symbol: Stock ticker (required)
  - from: Start date YYYY-MM-DD (required)
  - to: End date YYYY-MM-DD (required)
  - token: API key (required)

Response:
[
  {
    "category": "company news",
    "datetime": 1693526400,
    "headline": "Apple Announces New iPhone",
    "id": 123456,
    "image": "https://...",
    "related": "AAPL",
    "source": "Reuters",
    "summary": "Apple Inc unveiled...",
    "url": "https://..."
  }
]
```

### Quote Endpoint
```
GET https://finnhub.io/api/v1/quote
Parameters:
  - symbol: Stock ticker (required)
  - token: API key (required)

Response:
{
  "c": 178.18,    // Current price
  "d": 0.27,      // Change
  "dp": 0.15,     // Percent change
  "h": 178.42,    // High
  "l": 176.93,    // Low
  "o": 177.50,    // Open
  "pc": 177.91,   // Previous close
  "t": 1693526400 // Timestamp
}
```

---

## Questions for Review

1. **Watchlist Management:** How should we define the default watchlist for automated scanning?
   - Hardcode a list? (SPY components, tech stocks, etc.)
   - User-configurable in settings?
   - Database model for custom watchlists?

2. **Notification Preferences:** For automated morning scanner:
   - Email summary?
   - Browser push notifications?
   - SMS alerts (requires Twilio)?
   - Just populate dashboard?

3. **AI Analysis Enhancement:** Which fields are most valuable?
   - Entry/exit price targets?
   - Stop loss recommendations?
   - Position sizing suggestions?
   - Risk/reward ratios?

4. **News Filtering:** Should we filter news by:
   - Relevance score?
   - Source credibility?
   - News age (only show <24 hours)?
   - Category (exclude general market news)?

5. **Historical Data:** How far back should we retain old movers?
   - Keep all for analytics?
   - Archive after 30 days?
   - Delete after 90 days?

---

## Conclusion

Phase 1 of Finnhub integration is complete and tested. The automated news fetching significantly improves the user experience by eliminating manual data entry and providing better context for AI analysis.

The roadmap for Phases 2-6 will progressively enhance the market movers strategy with automation, real-time alerts, and data-driven insights.

**Ready for production deployment.**
