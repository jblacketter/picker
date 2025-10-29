# Next Steps - Market Movers Strategy
**Status:** Phase 1 Complete (Finnhub Integration)
**Date:** October 29, 2025

---

## ✅ What's Working Now

**Core Functionality:**
- ✅ Real-time stock scanning with yfinance
- ✅ Automated news fetching via Finnhub API
- ✅ AI analysis with Claude (fixed blocking issue)
- ✅ Status workflow tracking (identified → researching → ready → executed)
- ✅ Manual and quick-add tracking options
- ✅ Dark mode support with good contrast
- ✅ Larger, readable fonts

**What This Enables:**
You can now:
1. Scan a list of symbols for price movements
2. Click "+ Track" and news auto-populates from Finnhub
3. Click "Research This" and get AI analysis
4. Move stocks through your workflow
5. Toggle dark mode for late-night/early-morning use

---

## 🎯 Recommended Priority Order

Based on impact and effort, here's what to build next:

### **PRIORITY 1: Automated Morning Scanner** ⭐⭐⭐
**Why:** Saves 30 minutes every morning, most impactful feature
**Effort:** 2-3 hours
**Impact:** HIGH

**What it does:**
- Runs automatically at 8:00 AM ET via cron/scheduler
- Scans predefined watchlist (SPY components, tech stocks, etc.)
- Identifies stocks with >5% pre-market movement
- Auto-fetches news for all movers
- Sends email summary OR just populates dashboard
- You wake up, log in, see the movers ready to research

**Implementation:**
```bash
# Django management command
python manage.py scan_premarket_movers

# Add to crontab (8:00 AM ET)
0 13 * * 1-5 cd /path/to/picker && python manage.py scan_premarket_movers
```

**Files to Create:**
- `strategies/management/commands/scan_premarket_movers.py`
- `strategies/watchlists.py` (configurable symbol lists)
- Optional: Email template for summary

**Questions:**
- What symbols should be in default watchlist?
  - Suggestion: AAPL, TSLA, NVDA, AMD, META, MSFT, AMZN, GOOGL, NFLX, SHOP
  - Or: SPY top 50 holdings
- Email notification or just populate dashboard?
- Minimum movement threshold (default 5%)?

---

### **PRIORITY 2: Enhanced AI Analysis** ⭐⭐⭐
**Why:** Makes AI actually useful for trading decisions
**Effort:** 3-4 hours
**Impact:** HIGH

**Current AI Output:**
```json
{
  "analysis": "Brief 2-3 sentence overview",
  "sentiment": "bullish"
}
```

**Enhanced AI Output:**
```json
{
  "analysis": "Detailed catalyst explanation",
  "sentiment": "bullish",
  "confidence": "high",
  "entry_strategy": "Wait for 9:35 AM for volatility to settle. Enter at $150-152.",
  "exit_targets": ["$158 (5% gain)", "$162 (8% gain - stretch)"],
  "stop_loss": "$147 (2% max loss)",
  "risk_reward": "3:1",
  "key_catalysts": ["FDA approval", "Analyst upgrade"],
  "risks": ["High IV", "Profit-taking at open"]
}
```

**Database Changes Needed:**
Add fields to PreMarketMover model:
- `confidence_level` (high/medium/low)
- `entry_strategy` (text)
- `exit_targets` (JSON or text)
- `stop_loss_price` (decimal)
- `risk_reward_ratio` (text)
- `key_catalysts` (JSON array)
- `risks` (JSON array)

**UI Updates:**
- Display entry/exit targets prominently
- Show stop loss and R:R ratio
- Expandable section for risks/catalysts

**Questions:**
- Which fields are MOST valuable to you?
- Should we add position sizing suggestions?
- Display all in card or collapsible section?

---

### **PRIORITY 3: Market Status Detection** ⭐⭐
**Why:** Better awareness of market state
**Effort:** 1-2 hours
**Impact:** MEDIUM

**What it does:**
- Displays badge showing current session:
  - "PRE-MARKET" (6:00-9:30 AM ET) - Green
  - "REGULAR HOURS" (9:30 AM-4:00 PM ET) - Blue
  - "AFTER-HOURS" (4:00-8:00 PM ET) - Orange
  - "CLOSED" - Gray
- Uses Finnhub market status API
- Updates scanner behavior based on session
- Warning if scanning during closed hours

**Implementation:**
- Add `get_market_status()` call to view context
- Display badge in navigation or page header
- Optional: Different scanning strategies per session

**Questions:**
- Should we change scanning behavior based on session?
- Pre-market: focus on news-driven moves only?
- Regular hours: include volume + price action?

---

### **PRIORITY 4: Real-Time Webhooks** ⭐
**Why:** Never miss breaking news on tracked stocks
**Effort:** 4-5 hours
**Impact:** MEDIUM (nice-to-have)

**What it does:**
- Finnhub sends real-time news alerts
- Auto-trigger research for tracked stocks
- Optional: Email/SMS/push notifications
- Only alert for significant news (configurable)

**You Already Have:**
- Webhook secret: configured in environment
- Webhook authentication ready

**Implementation:**
- Django view to receive webhook events
- Authenticate via `X-Finnhub-Secret` header
- Process news events in real-time
- Trigger notifications (email/SMS via Twilio)

**Questions:**
- Which notifications? Email, browser push, SMS?
- Only alert for tracked stocks or any big movers?
- During market hours only or 24/7?

---

### **PRIORITY 5: Historical Performance Analytics** ⭐
**Why:** Learn which news types correlate with successful trades
**Effort:** 6-8 hours
**Impact:** MEDIUM-LOW (long-term value)

**What it does:**
- Track P/L for each trade
- Categorize news by type (earnings, FDA, merger, analyst, etc.)
- Calculate win rate by news category
- Identify best-performing patterns
- Charts showing performance over time

**Metrics to Track:**
- Win rate by news type
- Average P/L per trade
- Best time of day to enter
- Average hold time
- Stocks that repeat as movers

**Implementation:**
- New models for trade analytics
- Charts using Chart.js or similar
- New analytics page/dashboard
- ML suggestions for similar setups (future)

**Questions:**
- How far back to keep historical data?
- What metrics matter most?
- Archive old movers or keep forever?

---

## 🔧 Technical Debt / Improvements

### Low Priority (But Good)

**1. Caching for Finnhub Calls**
- Cache news for 15 minutes to reduce API calls
- Avoid re-fetching same news repeatedly
- **Effort:** 1 hour

**2. Add Unit Tests**
- Test `finnhub_service.py` functions
- Test AI client methods
- **Effort:** 2-3 hours

**3. Add Refresh News Button**
- Manual re-fetch of news if outdated
- Visible timestamp showing "News from 2 hours ago"
- **Effort:** 30 minutes

**4. Persist Finnhub Metadata**
- Store news timestamp, category on PreMarketMover
- Surface in UI for better context
- **Effort:** 1 hour (requires migration)

**5. Filter/Search Movers**
- Search by symbol, news text
- Filter by date range, sentiment
- **Effort:** 1-2 hours

---

## 📊 Recommended Roadmap

### Week 1 (This Week):
- ✅ Fix Codex issues (DONE)
- ✅ Improve dark mode (DONE)
- 🚧 Build automated morning scanner (PRIORITY 1)

### Week 2:
- Enhanced AI analysis (PRIORITY 2)
- Market status detection (PRIORITY 3)
- Add unit tests

### Week 3:
- Real-time webhooks (PRIORITY 4)
- Add caching and refresh button
- Performance optimizations

### Future (Month 2+):
- Historical analytics (PRIORITY 5)
- ML pattern recognition
- Brokerage integration for execution

---

## 💡 Quick Wins (Can Do Right Now)

These take <30 minutes each:

1. **Add "Last Updated" timestamp** to news
   - Shows when news was fetched
   - Helps judge freshness

2. **Add "Pre-Market" badge** to scanner results
   - Visual indicator in table
   - Already have the data

3. **Quick links in nav** for status filters
   - "Identified (3)" directly in nav
   - Faster access to ready trades

4. **Keyboard shortcuts**
   - `R` = Research this
   - `T` = Track
   - `/` = Focus search

5. **Export to CSV**
   - Download movers for external analysis
   - Simple Django view

---

## 🎯 My Recommendation: Start Here

**If you want immediate impact:**
→ Build the **Automated Morning Scanner** (Priority 1)

**Why:**
- Saves most time (30 min/day)
- Uses existing infrastructure
- No database changes needed
- Can iterate based on what you see

**Steps:**
1. Create management command
2. Define default watchlist (10-20 symbols)
3. Test manually: `python manage.py scan_premarket_movers`
4. Add to cron once it works
5. Iterate on symbol list and thresholds

**If you want better trading decisions:**
→ Build **Enhanced AI Analysis** (Priority 2)

**Why:**
- Makes AI output actionable
- Entry/exit targets help with discipline
- Stop loss prevents big losses
- Small DB migration required

---

## ❓ Questions for You

Before we start building, let's align on:

1. **Morning Scanner:**
   - What symbols should be in the default watchlist?
   - Email notification or just dashboard?
   - Minimum % movement threshold?

2. **AI Analysis:**
   - Which fields are most valuable? (entry/exit/stop/R:R/catalysts/risks)
   - Position sizing suggestions?

3. **Overall Priority:**
   - Which priority resonates most with your workflow?
   - Anything missing from this plan?

---

## 📈 Success Metrics

How we'll know it's working:

- **Morning Scanner:** Wake up, see 5-10 movers ready to review
- **AI Analysis:** Make faster trade decisions with clear entry/exit
- **Time Saved:** <10 minutes from wake-up to first trade idea
- **Win Rate:** Track and improve over time
- **Workflow:** Smooth progression through all statuses

---

**Bottom Line:** The foundation is solid. Now let's build the automation and intelligence layers to make this a truly hands-off morning routine.

**Ready to start?** Pick your priority and let's build it today!
