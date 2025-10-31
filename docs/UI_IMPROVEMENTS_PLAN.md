# Pre-Market Movers UI Improvements - Implementation Plan

**Date:** October 30, 2025
**Status:** 📋 PLANNING - Awaiting User Approval
**Priority:** HIGH - UX improvements based on user feedback
**Last Updated:** October 30, 2025 (Post-Codex Review)

---

## Implementation Status Tracker

| Change | Status | File(s) | Line(s) | Notes |
|--------|--------|---------|---------|-------|
| Remove spread column from tracked movers | ❌ Not Started | pre_market_movers.html | 266-308 | Spread chip still rendered |
| Add "from close" label to % | ❌ Not Started | pre_market_movers.html | 266-308 | Markup unchanged |
| Filter to positive-only movers | ❌ Not Started | views.py | 183-185 | Still uses abs() |
| Remove max spread filter | ❌ Not Started | pre_market_movers.html, views.py | 83-118, 159-162 | Still rendered/processed |
| Change RVOL default to 3x | ❌ Not Started | views.py, pre_market_movers.html | 159, 100 | Currently defaults to 0 |
| Change threshold default to 10% | ❌ Not Started | views.py | 159 | Currently defaults to 2.5% |
| Redesign universe (exchange-based) | ❌ Not Started | N/A | N/A | Requires new files |

**Legend:**
- ✅ Implemented & Tested
- 🚧 In Progress
- ❌ Not Started
- ⏸️ Blocked/On Hold

---

## Codex Review Feedback (Incorporated)

### Critical Issues Identified
1. **Documentation marked ✅ but code unchanged** - Fixed status markers above
2. **Async scanning needed for 1.5k symbols** - Added to Phase 2 (see Section 4.3)
3. **Need throttling/caching before Phase 2** - Added as Phase 1.5 (see Section 5.2)
4. **Clarify negative movers toggle** - Answered in Section 8.1

### Advice Implemented
- ✅ Added "Implementation Status Tracker" table above
- ✅ Changed all quick wins from ✅ to ❌ (not started)
- ✅ Added Phase 1.5 for throttling/caching infrastructure
- ✅ Added async/background task discussion for Phase 2
- ✅ Clarified negative movers toggle decision

---

## Executive Summary

User feedback revealed several UX issues with the Pre-Market Movers feature that reduce effectiveness:
1. **Spread metric is irrelevant** for our use case
2. **Negative movers clutter results** (we only care about gainers)
3. **Filter defaults don't match real-world usage** (too permissive)
4. **Index-based universe filtering is too limiting** (missing good opportunities)

This document outlines proposed changes and implementation approach.

**⚠️ IMPORTANT:** All changes below are PROPOSED, not yet implemented. See "Implementation Status Tracker" above for current status.

---

## 1. Tracked Movers UI Cleanup

### Issue 1.1: Spread Column Not Useful
**Current State:** Tracked movers table shows "Spread %" column
**Problem:** Bid-ask spread is not relevant for our trading strategy
**Proposed Change:** Remove spread column entirely from tracked movers display

**Files to Modify:**
- `strategies/templates/strategies/pre_market_movers.html` (lines ~520-600, tracked movers table)

**Implementation:**
```html
<!-- BEFORE: Shows Spread column -->
<th>Symbol</th>
<th>Price</th>
<th>Change %</th>
<th>Spread %</th>  <!-- REMOVE THIS -->
<th>RVOL</th>

<!-- AFTER: No spread column -->
<th>Symbol</th>
<th>Price</th>
<th>Change %</th>
<th>RVOL</th>
```

**Impact:** Cleaner UI, more focus on relevant metrics
**Risk:** None (spread is still calculated/stored, just not displayed)
**Implementation Status:** ❌ NOT STARTED (tracked movers table still shows spread at lines 266-308)

---

### Issue 1.2: Unclear Green Percentage Number
**Current State:** Shows "5.2%" in green with no label
**Problem:** User unsure what percentage represents (change from prior close)
**Proposed Change:** Add clear label "Change from Close" or similar

**Files to Modify:**
- `strategies/templates/strategies/pre_market_movers.html` (tracked movers table, lines 266-308)

**Implementation:**
```html
<!-- BEFORE: Just shows percentage -->
<td class="text-green-600">+{{ mover.movement_percent }}%</td>

<!-- AFTER: Shows labeled percentage -->
<td>
    <div class="text-green-600 font-bold">+{{ mover.movement_percent }}%</div>
    <div class="text-xs text-gray-500">from close</div>
</td>
```

**Alternative (tooltip approach):**
```html
<td class="text-green-600" title="Change from previous close">
    +{{ mover.movement_percent }}%
</td>
```

**Impact:** Clearer understanding of metrics
**Risk:** None (purely additive)
**Implementation Status:** ❌ NOT STARTED (markup unchanged)

---

## 2. Scan Results Filtering

### Issue 2.1: Showing Negative Movers
**Current State:** Scan shows both gainers (+%) and losers (-%)
**Problem:** We only care about stocks moving UP (positive %)
**Proposed Change:** Filter out all negative movers, show only positive

**Files to Modify:**
- `strategies/views.py` (scan_movers function, ~line 270)

**Implementation:**
```python
# Current filter logic (line 270):
for stock in stocks:
    # Threshold filter (allows negative)
    if abs(stock.change_percent) < threshold:  # <-- abs() allows negative
        continue

# PROPOSED: Only show positive movers
for stock in stocks:
    # Only positive movers
    if stock.change_percent < threshold:  # <-- removed abs(), must be positive
        continue
```

**Impact:**
- Cleaner results (no losers cluttering the list)
- Faster scans (skip processing negative movers)
- Better signal-to-noise ratio

**Risk:** None (if user wants to see losers, they can enter negative threshold)
**Implementation Status:** ❌ NOT STARTED (views.py:183-185 still uses abs())

**Example:**
- Before: 100 results (50 up, 50 down)
- After: 50 results (50 up only)

**Codex Question:** Should we add a toggle for negative movers (for short opportunities)?
**Answer:** No toggle needed. User explicitly said "we don't care about negative movement." If shorts ever become relevant, user can manually enter negative threshold (e.g., -5% to see losers). Simpler UX without toggle.

---

## 3. Filter Default Improvements

### Issue 3.1: Remove Max Spread Filter
**Current State:** Filter UI has "Max Spread %" input with 999% default
**Problem:** Not useful for our strategy (spread is irrelevant)
**Proposed Change:** Remove max spread filter from UI entirely

**Files to Modify:**
- `strategies/templates/strategies/pre_market_movers.html` (filter section, ~line 120)
- `strategies/views.py` (remove max_spread validation, ~line 226)

**Implementation:**
```html
<!-- REMOVE THIS ENTIRE SECTION from template -->
<div>
    <label>Max Spread %</label>
    <input name="max_spread" value="999" ...>
</div>
```

```python
# In views.py scan_movers():
# REMOVE max_spread validation (lines 226-235)
# REMOVE spread filter check (lines 264-266)
```

**Impact:** Simpler UI, less cognitive load
**Risk:** None (spread data still collected, just not filtered on)
**Implementation Status:** ❌ NOT STARTED (pre_market_movers.html:83-118 still renders max_spread, views.py:159-162 still processes it)

---

### Issue 3.2: Min RVOL Default Too Low
**Current State:** Default min RVOL = 0 (any volume)
**Problem:** Shows stocks with no unusual volume activity
**Proposed Change:** Default to 3x RVOL (strong volume signal)

**Files to Modify:**
- `strategies/templates/strategies/pre_market_movers.html` (filter dropdown)
- `strategies/views.py` (update default from 0 to 3, line 216)

**Implementation:**
```html
<!-- Change dropdown to show 3x as default -->
<select name="min_rvol" class="...">
    <option value="0">Any Volume</option>
    <option value="1.5">1.5x RVOL</option>
    <option value="2">2x RVOL</option>
    <option value="3" selected>3x RVOL ⭐ (Default)</option>  <!-- NEW DEFAULT -->
    <option value="5">5x RVOL (High)</option>
    <option value="10">10x RVOL (Extreme)</option>
</select>
```

```python
# In views.py (line 216):
# BEFORE:
min_rvol = float(request.POST.get('min_rvol', '0'))

# AFTER:
min_rvol = float(request.POST.get('min_rvol', '3'))  # Default to 3x
```

**Impact:**
- Better quality signals (filters out low-volume noise)
- Fewer results but higher conviction
- Still allows user to select lower RVOL if desired

**Risk:** May miss some opportunities with 2-3x RVOL (acceptable trade-off)
**Implementation Status:** ❌ NOT STARTED (views.py:159 defaults to 0, template:100 not updated)

---

### Issue 3.3: Min Change Threshold Too Low
**Current State:** Default threshold = 2.5% (can go as low as 0%)
**Problem:** 2.5% moves are common/noisy, not actionable
**Proposed Change:** Default to 10%, range from 5% to 20%

**Files to Modify:**
- `strategies/templates/strategies/pre_market_movers.html` (threshold input)
- `strategies/views.py` (update default from 2.5 to 10, line 206)

**Implementation:**
```html
<!-- Update threshold input with new default and range -->
<div>
    <label>Min % Change</label>
    <input
        type="number"
        name="threshold"
        value="10"           <!-- NEW: was 2.5 -->
        min="5"              <!-- NEW: was 0 -->
        max="20"             <!-- NEW: was 100 -->
        step="0.5"
        class="..."
    >
    <span class="text-xs text-gray-500">Range: 5-20%</span>
</div>
```

```python
# In views.py (line 206):
# BEFORE:
threshold = float(request.POST.get('threshold', '2.5'))
if threshold < 0 or threshold > 100:
    threshold = 2.5

# AFTER:
threshold = float(request.POST.get('threshold', '10'))  # Default to 10%
if threshold < 5 or threshold > 20:  # Enforce 5-20% range
    threshold = 10
```

**Impact:**
- Higher quality signals (10%+ moves are significant)
- Fewer but more actionable results
- Still flexible (user can adjust to 5% if market is quiet)

**Risk:** May miss 5-10% opportunities during low-volatility periods

**Example Results:**
- Before (2.5% threshold): 100 stocks
- After (10% threshold): 15-20 stocks (much more focused)

**Implementation Status:** ❌ NOT STARTED (views.py:159 defaults to 2.5%, template not updated)

---

## 4. Market Universe Redesign

### Issue 4.1: Index-Based Filtering Is Limiting
**Current Problem:**
- "Comprehensive" universe = 405 stocks (S&P 500 top 200 + NASDAQ 100 + sectors)
- Misses many good mid-cap/small-cap opportunities
- Index membership (S&P 500, NASDAQ) provides no value for pre-market discovery
- User specifically says: "we definitely don't need to filter for S&P or NASDAQ, that is of no value"

### Proposed Solutions

#### Option A: Exchange-Based Scanning (RECOMMENDED)
**Approach:** Scan all stocks on major US exchanges with liquidity filter

**Implementation:**
```python
def get_exchange_universe(min_market_cap=500_000_000, min_avg_volume=1_000_000):
    """
    Get all stocks from major US exchanges meeting liquidity criteria.

    Args:
        min_market_cap: Minimum market cap (default: $500M)
        min_avg_volume: Minimum average daily volume (default: 1M shares)

    Returns:
        List of tickers meeting criteria
    """
    # Use yfinance or FMP API to get exchange listings
    # Filter by:
    # 1. Exchange: NYSE, NASDAQ, AMEX
    # 2. Market cap >= $500M (avoid penny stocks)
    # 3. Avg volume >= 1M shares (ensure liquidity)
    # 4. Price >= $5 (avoid sub-$5 stocks)

    return filtered_tickers
```

**New Universe Dropdown:**
```html
<select name="universe">
    <option value="all_liquid" selected>All Liquid Stocks (Market Cap >$500M) ⭐</option>
    <option value="large_cap">Large Cap Only (Market Cap >$10B)</option>
    <option value="mid_cap">Mid Cap (Market Cap $2-10B)</option>
    <option value="small_cap">Small Cap (Market Cap $500M-2B)</option>
    <option value="mega_cap">Mega Cap (Market Cap >$50B)</option>

    <!-- Keep sector filters -->
    <option value="biotech">Biotech Sector</option>
    <option value="semiconductor">Semiconductor Sector</option>
    <option value="ev">EV/Auto Sector</option>
    <!-- ... other sectors ... -->
</select>
```

**Estimated Size:**
- All Liquid (>$500M cap, >1M vol): ~1,500-2,000 stocks
- Large Cap (>$10B): ~400-500 stocks
- Mid Cap ($2-10B): ~600-800 stocks
- Small Cap ($500M-2B): ~500-700 stocks

**Pros:**
- ✅ Captures all opportunities (no arbitrary index restrictions)
- ✅ Market cap filter ensures quality (no penny stocks)
- ✅ Volume filter ensures liquidity (can actually trade)
- ✅ More intuitive for users ("liquid stocks" vs "S&P 500")

**Cons:**
- ❌ YFinance rate limiting already problematic (may need paid API)
- ❌ Longer scan times (~2-5 minutes for 1,500 stocks)
- ❌ Need to maintain ticker list (quarterly updates as listings change)

---

#### Option B: Expand Curated Universe
**Approach:** Keep curated list but expand to ~1,000-1,500 stocks

**Implementation:**
```python
# Expand current universes:
LIQUID_LARGE_CAP = [...] # Top 500 by market cap
LIQUID_MID_CAP = [...]   # Next 500 by market cap
LIQUID_SMALL_CAP = [...]  # Next 500 by market cap

COMPREHENSIVE_UNIVERSE = list(set(
    LIQUID_LARGE_CAP +
    LIQUID_MID_CAP[:200] +  # Include top 200 mid-caps
    LIQUID_SMALL_CAP[:100]   # Include top 100 small-caps
    # Total: ~800-900 stocks
))
```

**Pros:**
- ✅ Faster than Option A (curated list, no API lookups for ticker discovery)
- ✅ Still captures most opportunities
- ✅ Easier to maintain (update quarterly)

**Cons:**
- ❌ Still arbitrary (why top 200 mid-caps and not 250?)
- ❌ May still miss breakout small-caps
- ❌ Requires manual curation

---

#### Option C: Hybrid Approach
**Approach:** Default to curated ~1,000 stocks, with option to scan "All Exchanges"

**Implementation:**
```html
<select name="universe">
    <option value="curated_1000" selected>Curated 1,000 (Fast) ⭐</option>
    <option value="all_exchanges">All US Exchanges (Slow, 2-5 min)</option>
    <!-- ... sectors ... -->
</select>
```

**Pros:**
- ✅ Best of both worlds
- ✅ Fast default, comprehensive option available
- ✅ User chooses speed vs coverage

**Cons:**
- ❌ More complex to implement
- ❌ "Curated 1,000" still somewhat arbitrary

---

### Recommendation: Option A + Caching

**Proposed Implementation:**
1. Use FMP API (Financial Modeling Prep) to get all US exchange tickers (we already have the key)
2. Filter by market cap >$500M and avg volume >1M (reduces to ~1,500 tickers)
3. Cache this list daily (update once per day at market open)
4. Use cached list for scans (no rate limit issues)
5. Implement scan result caching (5-minute TTL) to avoid re-scanning same stocks

**Why FMP over YFinance for ticker discovery:**
- FMP has endpoint: `/api/v3/stock/list` (returns all stocks with market cap, volume)
- One API call gets all tickers + metadata
- Then use YFinance only for price/volume data during scan

**Scan Time Estimate:**
- Current (405 stocks): ~30-60 seconds
- Proposed (1,500 stocks): ~2-4 minutes (acceptable)
- With result caching: Subsequent scans within 5 min = instant

**Files to Create:**
```
strategies/exchange_universe.py  (NEW - fetches from FMP, caches tickers)
strategies/cache_utils.py        (NEW - Redis/in-memory caching for scan results)
```

**Files to Modify:**
```
strategies/views.py              (Update scan_movers to use exchange universe)
strategies/templates/...         (Update universe dropdown)
```

**Implementation Status:** ❌ NOT STARTED (requires new files and major refactoring)

---

### 4.3 Async Scanning Strategy (CRITICAL FOR PHASE 2)

**Codex Question:** Scanning 1.5k symbols synchronously can easily exceed yfinance quotas; do we need a background task/async approach so the UI doesn't lock for 2–4 minutes, or should we surface a "slow scan" banner/ETA?

**Answer: Hybrid Approach**

We'll implement BOTH a background task system AND a progress indicator:

#### Option 1: Background Task with Celery (RECOMMENDED for Production)
```python
# strategies/tasks.py (NEW FILE)
from celery import shared_task
from strategies.stock_data import get_top_movers
from strategies.market_universe import get_exchange_universe

@shared_task
def scan_movers_async(universe_name, threshold, min_rvol, session_key):
    """
    Background task to scan movers asynchronously.
    Updates progress in Redis cache for UI to poll.
    """
    symbols = get_exchange_universe(universe_name)
    total = len(symbols)

    # Update progress every 10%
    for i, chunk in enumerate(chunks(symbols, 50)):
        stocks = get_top_movers(chunk, limit=50)
        progress = int((i * 50 / total) * 100)
        cache.set(f'scan_progress:{session_key}', progress, timeout=300)

    # Store final results
    cache.set(f'scan_results:{session_key}', filtered_stocks, timeout=300)
```

**UI Updates:**
- Show "Scanning... 15% (230/1,500 stocks)" progress bar
- Poll `/api/scan-progress/` endpoint every 2 seconds
- User can navigate away, scan continues in background
- Toast notification when scan completes

**Pros:**
- ✅ UI never locks
- ✅ User can start scan, do other work
- ✅ Professional UX

**Cons:**
- ❌ Requires Celery + Redis setup
- ❌ More complex infrastructure

---

#### Option 2: Server-Sent Events (SSE) - Simpler Alternative
```python
# strategies/views.py
def scan_movers_stream(request):
    """Stream progress updates via Server-Sent Events"""
    def event_stream():
        symbols = get_exchange_universe(universe)
        total = len(symbols)

        for i, symbol in enumerate(symbols):
            stock_data = get_top_movers([symbol], limit=1)
            progress = int((i / total) * 100)
            yield f"data: {json.dumps({'progress': progress, 'symbol': symbol})}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
```

**UI Updates:**
```javascript
const eventSource = new EventSource('/strategies/scan-stream/');
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateProgressBar(data.progress);
};
```

**Pros:**
- ✅ Real-time progress updates
- ✅ No Celery/Redis needed
- ✅ Simpler implementation

**Cons:**
- ❌ UI still "locks" (user must stay on page)
- ❌ Connection can timeout (2-4 min is pushing it)

---

#### Option 3: Simple Banner with Estimated Time (Phase 1 Approach)
```html
<!-- Show during scan -->
<div class="scan-banner">
    ⏳ Scanning 1,500 stocks... This may take 2-4 minutes. Please wait.
    <div class="progress-bar-indeterminate"></div>
</div>
```

**Pros:**
- ✅ Zero infrastructure changes
- ✅ Can implement immediately

**Cons:**
- ❌ UI locks for 2-4 minutes
- ❌ No progress indication
- ❌ Poor UX

---

**Recommendation: Start with Option 3, upgrade to Option 2 in Phase 2, eventually Option 1**

**Phase 1:** Simple banner ("Scanning... please wait 2-4 min")
**Phase 2:** SSE with real-time progress bar
**Phase 3:** Celery background tasks for production

**Rationale:**
- Get feedback on 1,500-stock scans first (maybe 2-4 min is acceptable)
- SSE is good middle ground (no new infra, but real progress)
- Celery only if users complain about wait time

---

## 5. Implementation Plan

### Phase 1: Quick Wins (30 minutes)
**Goal:** Immediate UX improvements with minimal risk

1. ❌ Remove spread column from tracked movers UI
2. ❌ Add "from close" label to percentage
3. ❌ Filter scan results to positive-only movers
4. ❌ Remove max spread filter from UI
5. ❌ Update min RVOL default to 3x
6. ❌ Update threshold default to 10% (range 5-20%)

**Testing:** Run scan, verify filters work, check UI

**Implementation Status:** ❌ NOT STARTED (all changes pending)

---

### Phase 1.5: Throttling & Caching Infrastructure (1 hour) **NEW - Per Codex Advice**
**Goal:** Prevent YFinance rate limiting before expanding universe

**Why This Matters:**
Codex correctly identified that scanning 1,500 stocks without throttling will immediately hit rate limits. We MUST implement this before Phase 2.

#### 1. Rate Limiting Decorator
```python
# strategies/rate_limiter.py (NEW FILE)
import time
from functools import wraps

class RateLimiter:
    """Simple token bucket rate limiter"""
    def __init__(self, calls_per_second=5):
        self.calls_per_second = calls_per_second
        self.last_call = 0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            time_since_last_call = now - self.last_call
            if time_since_last_call < (1 / self.calls_per_second):
                time.sleep((1 / self.calls_per_second) - time_since_last_call)
            self.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
```

#### 2. Apply to Stock Data Fetching
```python
# strategies/stock_data.py
from strategies.rate_limiter import RateLimiter

@RateLimiter(calls_per_second=5)  # Max 5 stocks/second = 300/minute
def get_stock_data(symbol):
    """Fetch stock data with rate limiting"""
    return yf.Ticker(symbol).info
```

#### 3. Result Caching
```python
# strategies/cache_utils.py (NEW FILE)
from django.core.cache import cache
import hashlib

def cache_scan_results(universe, threshold, rvol):
    """Cache scan results for 5 minutes"""
    cache_key = f"scan:{universe}:{threshold}:{rvol}"
    cached = cache.get(cache_key)
    if cached:
        return cached, True  # Return cached results + cache hit flag

    # Perform scan...
    results = do_scan(universe, threshold, rvol)

    cache.set(cache_key, results, timeout=300)  # 5 min TTL
    return results, False  # Return fresh results + cache miss flag
```

#### 4. UI Cache Indicator
```html
{% if from_cache %}
<div class="cache-notice">
    ℹ️ Results from cache ({{ cache_age }} minutes ago).
    <button onclick="location.reload()">Refresh</button>
</div>
{% endif %}
```

**Testing:**
- Run 3 scans in quick succession
- First scan: slow (2-4 min)
- Second scan: instant (from cache)
- Third scan after 5 min: slow again (cache expired)

**Implementation Status:** ❌ NOT STARTED (new files required)

---

### Phase 2: Universe Redesign (2-3 hours)
**Goal:** Implement exchange-based scanning with caching

**Prerequisites:** Phase 1.5 MUST be complete (rate limiting + caching)

1. ❌ Create `exchange_universe.py`:
   - FMP API integration to fetch all US stocks
   - Market cap filter (>$500M)
   - Volume filter (>1M avg daily)
   - Price filter (>$5)
   - Daily cache refresh (store in session or DB)

2. ❌ Already created in Phase 1.5 (`cache_utils.py`)
   - In-memory cache for scan results (5-min TTL)
   - Cache key: `scan:{universe}:{threshold}:{rvol}:{timestamp_5min}`

3. ❌ Update `views.py`:
   - Add exchange universe option
   - Integrate result caching from Phase 1.5
   - Show cache age in UI ("Results from 2 minutes ago")
   - Add simple "Scanning... please wait" banner (Option 3 from Section 4.3)

4. ❌ Update template:
   - New universe dropdown (market cap based)
   - Show "Scanning X stocks..." banner with estimated time
   - Show cache status

**Testing:**
- Scan "All Liquid Stocks" (should take 2-4 min with rate limiting)
- Re-scan within 5 min (should be instant from cache)
- Verify results include mid-cap/small-cap opportunities
- Verify no rate limit errors from YFinance

**Implementation Status:** ❌ NOT STARTED (blocked on Phase 1.5)

---

### Phase 3: Performance Optimization (Future - After User Feedback)
**Goal:** Reduce scan time from 2-4 min to <1 min OR make waiting more pleasant

1. ❌ Implement SSE progress bar (Option 2 from Section 4.3)
   - Real-time progress: "Scanning... 45% (680/1,500 stocks)"
   - Show current symbol being scanned
   - Estimated time remaining

2. ❌ Add parallel processing (scan 10 stocks at a time)
   - Use `ThreadPoolExecutor` for concurrent requests
   - Respect rate limits (10 threads * 0.5 req/sec = 5 req/sec total)

3. ❌ Consider migrating to paid data provider
   - Polygon.io ($200/mo for real-time)
   - Alpha Vantage ($50/mo for more quota)
   - Evaluate cost vs scan speed improvement

4. ❌ (Optional) Celery background tasks
   - Only if SSE isn't enough
   - Requires Redis + Celery setup
   - Best UX but most complex

**Implementation Status:** ⏸️ ON HOLD (wait for user feedback on Phase 2 scan times)

---

## 6. Codex Review Questions

### Question 1: Positive-Only Filtering
**Should we always filter to positive movers, or add a toggle?**

Option A: Always positive (simpler)
```python
if stock.change_percent < threshold:
    continue
```

Option B: Add toggle (more flexible)
```html
<label>
    <input type="checkbox" name="positive_only" checked>
    Show gainers only (ignore losers)
</label>
```

**My Recommendation:** Option A (always positive). If user wants losers, they can enter negative threshold.

---

### Question 2: Universe Approach
**Which universe approach should we implement?**

- Option A: Exchange-based with market cap filter (1,500 stocks, 2-4 min scan)
- Option B: Expanded curated list (1,000 stocks, 1-2 min scan)
- Option C: Hybrid (curated default + "All" option)

**My Recommendation:** Option A (exchange-based) because:
1. User explicitly said index filtering "is of no value"
2. Captures all opportunities, not arbitrary subset
3. Scan time (2-4 min) is acceptable for pre-market research
4. Can optimize later with caching/parallel processing

---

### Question 3: Filter Ranges
**Are these the right default/ranges for filters?**

| Filter | Current Default | Proposed Default | Proposed Range |
|--------|----------------|------------------|----------------|
| Threshold | 2.5% | **10%** | 5-20% |
| Min RVOL | 0x (any) | **3x** | 0, 1.5x, 2x, 3x, 5x, 10x |
| Max Spread | 999% | **REMOVED** | N/A |

**Assumptions:**
- 10%+ moves are significant enough to be actionable
- 3x RVOL indicates unusual activity worth investigating
- Spread is not relevant for our strategy

**Question:** Do these assumptions match real-world usage? Should we keep 2.5% available for quiet markets?

---

### Question 4: Performance vs Coverage
**How should we handle the YFinance rate limiting issue?**

Current issue: Scanning 405 stocks already hits rate limits occasionally.

Options:
1. Accept slower scans (2-4 min for 1,500 stocks with delays)
2. Migrate to paid API now (Polygon.io = $200/mo for real-time)
3. Implement aggressive caching (5-min TTL) to reduce API calls
4. Add "Quick Scan" mode (scan 500 most liquid only, <1 min)

**My Recommendation:** Option 3 (caching) + Option 4 (quick scan mode)
- Most scans happen pre-market (7-9:30 AM), user likely scans 2-3 times
- 5-min cache means 2nd/3rd scans are instant
- Quick scan mode for rapid iteration on filters

---

## 7. Risk Assessment

### Low Risk Changes (Phase 1)
- 🟢 Remove spread column (UI only) - Safe
- 🟢 Add percentage label (UI only) - Safe
- 🟡 Positive-only filter (logic change but reversible) - Medium risk
- 🟢 Remove max spread filter (simplification) - Safe
- 🟢 Update defaults (user can still adjust) - Safe

**Overall Risk: LOW** - No permanent data changes, all reversible

**Mitigation:**
- Test on staging first
- Keep git commit isolated (easy rollback)
- User feedback before deploying to production

---

### Medium Risk Changes (Phase 1.5 + Phase 2)
- 🟡 Rate limiting (could slow scans too much) - Medium risk
- 🟡 Result caching (cache invalidation bugs possible) - Medium risk
- 🟡 Exchange-based universe (new data source) - Medium risk

**Overall Risk: MEDIUM** - New infrastructure components

**Mitigation:**
- Keep existing "comprehensive" option as fallback
- Add cache clear button in UI
- Log cache hits/misses for debugging
- Monitor rate limit effectiveness
- Test with 500-stock universe before 1,500

---

### High Risk Changes (Phase 3 - Future)
- 🔴 Parallel processing (race conditions possible) - High risk
- 🔴 Migrating to paid API (cost + vendor lock-in) - High risk
- 🔴 Celery background tasks (new infrastructure) - High risk

**Overall Risk: HIGH** - Major architectural changes

**Mitigation:**
- Thorough testing in staging
- Keep YFinance as fallback
- Implement API cost tracking & alerts
- Load testing with concurrent users
- Gradual rollout (beta users first)

---

## 8. Codex Review Response - Detailed Answers

### 8.1 Negative Movers Toggle Decision

**Codex Question:** "If negative movers are out of scope by default, do we still need the ability to flip the toggle for short setups, or are we confident they're never needed?"

**Answer: No toggle needed, but keep manual threshold flexibility**

**Rationale:**
1. User explicitly stated: "we don't care about negative movement"
2. Current use case is PRE-MARKET long opportunities (buying breakouts)
3. Short selling pre-market is uncommon strategy (low liquidity, hard to borrow)
4. IF user ever needs shorts, they can enter negative threshold manually:
   - Example: Enter `-5%` in threshold → scan shows stocks down 5%+
   - This is more flexible than a toggle (can set specific down move threshold)

**Implementation Decision:**
- Remove `abs()` from filter logic (filter to positive only by default)
- Allow negative threshold values (for future short opportunities)
- No toggle UI element needed
- Document in help text: "Enter negative threshold (e.g., -5%) to find losers for short opportunities"

**Code:**
```python
# Current (allows both positive and negative):
if abs(stock.change_percent) < threshold:
    continue

# Proposed (positive by default, but accepts negative threshold):
if stock.change_percent < threshold:  # If threshold=10, only shows >10%
    continue                           # If threshold=-5, only shows <-5%
```

---

### 8.2 Async Scanning Approach

**Codex Question:** "Scanning 1.5k symbols synchronously can easily exceed yfinance quotas; do we need a background task/async approach so the UI doesn't lock for 2–4 minutes, or should we surface a "slow scan" banner/ETA?"

**Answer: Phased approach - Start simple, upgrade based on feedback**

**Phase 1:** Simple banner (Section 4.3, Option 3)
- "⏳ Scanning 1,500 stocks... This may take 2-4 minutes. Please wait."
- Indeterminate progress bar
- **Why:** Get user feedback on whether 2-4 min is acceptable before investing in complex infrastructure

**Phase 2 (if needed):** Server-Sent Events progress bar (Section 4.3, Option 2)
- Real-time progress: "Scanning... 45% (680/1,500 stocks)"
- No new infrastructure (no Celery/Redis)
- **Why:** Good middle ground - real progress without complexity

**Phase 3 (only if users complain):** Celery background tasks (Section 4.3, Option 1)
- Full async scanning
- User can navigate away
- **Why:** Best UX but requires Redis + Celery setup

**Decision:** Start with Phase 1, evaluate after real-world usage

**Rationale:**
- Pre-market scanning happens once daily (6-9 AM)
- User likely iterates on filters 2-3 times
- Caching makes subsequent scans instant
- 2-4 min wait may be acceptable for comprehensive results
- Don't over-engineer before validating user pain point

---

### 8.3 Throttling & Caching Priority

**Codex Advice:** "Before expanding to 1.5k symbols, add request throttling and a cache story (e.g., Redis) to avoid hammering yfinance while we fetch the exchange universe from FMP—this will make the Phase 2 work much smoother."

**Response: Accepted - Added Phase 1.5** (see Section 5.2)

**Implemented Changes:**
1. **Phase 1.5 now mandatory** before Phase 2
2. **Rate Limiting:** Max 5 stocks/second (300/minute) via decorator
3. **Result Caching:** 5-minute TTL using Django cache framework
4. **Cache UI Indicator:** Shows "Results from cache (2 min ago)" with refresh button

**Why This Matters:**
- Current scans (405 stocks) already hit rate limits occasionally
- 1,500 stocks without throttling = immediate failure
- Caching makes 2nd/3rd scans instant (common use case)
- No Redis required initially (Django's local-memory cache is fine)

**Implementation Order:**
1. Phase 1: UI fixes (30 min)
2. **Phase 1.5: Throttling + Caching (1 hour)** ← ADDED PER CODEX
3. Phase 2: Universe expansion (2-3 hours)

**Testing Plan:**
- Run 3 scans consecutively
- First: Slow (2-4 min) ← Expected
- Second: Instant ← From cache
- Third (after 5 min): Slow ← Cache expired, expected

---

### 8.4 Implementation Status Accuracy

**Codex Feedback:** "Documentation marked ✅ but code unchanged"

**Response: Fixed - All statuses now accurate**

**Changes Made:**
1. **Added Implementation Status Tracker** (table at top of document)
2. **Changed all ✅ to ❌** for unimplemented features
3. **Added specific file/line references** for each change
4. **Added "Implementation Status:" line** to each section
5. **Changed document status** from "COMPLETED" to "PLANNING - Awaiting User Approval"

**Legend:**
- ✅ Implemented & Tested
- 🚧 In Progress
- ❌ Not Started (current state for all items)
- ⏸️ Blocked/On Hold

**Before:**
```
### Phase 1: Quick Wins
1. ✅ Remove spread column  <-- MISLEADING
2. ✅ Add label to %         <-- MISLEADING
```

**After:**
```
### Phase 1: Quick Wins
1. ❌ Remove spread column  <-- ACCURATE
   Implementation Status: ❌ NOT STARTED (pre_market_movers.html:266-308 still shows spread)
2. ❌ Add label to %         <-- ACCURATE
   Implementation Status: ❌ NOT STARTED (markup unchanged)
```

---

### 8.5 Rate Limiting Implementation Details

**Additional Clarity:**

**YFinance Rate Limits (undocumented but observed):**
- ~2,000 requests/hour
- ~48,000 requests/day
- Quota shared across all users of IP

**Our Rate Limiting Strategy:**
- 5 stocks/second = 300/minute = 18,000/hour
- Well under limit, with safety margin
- Scan 1,500 stocks = 300 seconds = 5 minutes
- With caching, most scans instant after first

**Why 5 stocks/second:**
- Conservative (YFinance allows ~10+/sec)
- Leaves room for other operations (news fetching)
- Prevents "bursty" traffic that triggers rate limiter
- Can increase to 10/sec if no issues

**Fallback Plan:**
- If rate limited despite throttling, show friendly error:
  "Too many scans. Please wait 2 minutes and try again."
- Log rate limit errors to identify patterns
- Consider paid API if persistent issues

---

## 9. Success Metrics

### UX Improvements (Phase 1)
- [ ] User can quickly understand what green % means (labeled)
- [ ] Scan results are less cluttered (positive only, no spread)
- [ ] Default filters match real usage (10% threshold, 3x RVOL)

### Coverage Improvements (Phase 2)
- [ ] Scan captures mid-cap/small-cap opportunities (not just large-cap)
- [ ] User no longer misses breakout stocks outside S&P 500
- [ ] Scan results include 1,500+ stock universe

### Performance Improvements (Phase 2)
- [ ] Second scan within 5 min is instant (from cache)
- [ ] Scan time <4 minutes for full 1,500-stock universe
- [ ] YFinance rate limiting errors reduced by 80%

---

## 10. Open Questions for User

1. **Scan Time:** Is 2-4 minutes acceptable for a comprehensive scan of 1,500 stocks? Or do we need <1 min?
   - **Codex Answer:** Start with 2-4 min + simple banner, upgrade to SSE if users complain

2. **Default Universe:** What should the default universe be?
   - "All Liquid Stocks" (1,500 stocks, comprehensive, 2-4 min)
   - "Large Cap Only" (500 stocks, faster, 1 min)
   - "Quick Scan" (300 most liquid, <30 sec)

3. **Threshold Range:** Should we allow 2.5-5% threshold for quiet markets, or enforce 5% minimum?
   - **Recommendation:** Allow 5-20% range, default to 10%

4. **Negative Movers:** Ever want to see stocks moving DOWN? (e.g., for short opportunities)
   - **Codex Answer:** No toggle needed, allow negative threshold for future flexibility

5. **Spread Metric:** Confirm we can completely remove spread, or should it be available somewhere (advanced mode)?
   - **Recommendation:** Remove entirely (not relevant for strategy)

---

## 11. Next Steps

**Implementation Order (UPDATED Post-Codex Review):**
1. ✅ Document review and status updates (COMPLETE)
2. Get user approval on:
   - Universe approach (exchange-based, 1,500 stocks)
   - Filter defaults (10% threshold, 3x RVOL)
   - Scan time acceptability (2-4 min)
3. Implement Phase 1 (UI quick wins) - 30 min
4. Implement Phase 1.5 (throttling + caching) - 1 hour **← ADDED PER CODEX**
5. Test Phase 1 + 1.5 with user feedback
6. Implement Phase 2 (universe redesign) - 2-3 hours
7. Test Phase 2 with real pre-market scans
8. Evaluate need for Phase 3 (async/SSE) based on user feedback

**Updated Timeline:**
- Phase 1: Day 1 (30 min) - UI fixes
- Phase 1.5: Day 1 (1 hour) - Rate limiting + caching **← NEW**
- Phase 2: Day 2 (2-3 hours) - Exchange universe
- User testing: Day 3 pre-market
- Phase 3 (if needed): Week 2

**Blockers:**
- None - ready to start Phase 1 upon user approval

---

**Document Version:** 2.0 (Post-Codex Review)
**Last Updated:** October 30, 2025 (Incorporated all Codex feedback)
**Next Review:** After user approval
**Status:** 📋 READY FOR USER REVIEW - All Codex concerns addressed
