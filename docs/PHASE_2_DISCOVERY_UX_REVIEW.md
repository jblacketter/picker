# Phase 2: Discovery Mode + UX Improvements - Implementation Review

**Date:** October 29, 2025
**Status:** Complete / Awaiting Codex Review
**Lead Developer:** Claude Code
**Reviewer:** Codex
**Next Phase:** Phase 3 - Market Context & Advanced Metrics

## Executive Summary

- **Auto-discovery implemented:** Users can now scan 410 stocks with one click (no manual symbol entry required)
- **Smart filtering added:** 4 configurable filters (universe, threshold, RVOL, spread) before scanning
- **UX improvements:** Loading indicator, scan results persistence, individual/bulk delete
- **Files modified:** 5 files (views.py, pre_market_movers.html, urls.py, market_universe.py, scan_premarket_movers.py)
- **Testing status:** Manually tested - all features working correctly

## Implementation Details

### Architecture Changes

**Pattern: Session-Based Scan Results**
- Scan results stored in Django session (survives page refreshes)
- Results persist when user tracks a stock (no longer cleared on action)
- Session cleared only on new scan or manual clear

**Pattern: Filter-First Design**
- User configures filters before scanning (not after)
- Backend applies filters during scan (efficient)
- Filter values stored in session for UI persistence

**Pattern: Progressive Enhancement**
- Loading indicator with JavaScript (degrades gracefully)
- Confirmation dialogs for destructive actions
- Dark mode support on all new UI elements

### Files Modified

1. **strategies/market_universe.py** (lines 59, 111-113)
   - Removed 4 invalid/delisted symbols (ANSS, WISH, CANO, NKLA)
   - Cleaned up symbol lists based on yfinance 404 errors

2. **strategies/views.py** (lines 17-35, 150-234, 327-354)
   - `pre_market_movers()`: Changed session.pop() to session.get() for persistence
   - `scan_movers()`: Added filter parameters (universe, threshold, min_rvol, max_spread)
   - `scan_movers()`: Added filtering logic for RVOL and spread
   - `delete_mover()`: New view for individual delete
   - `delete_all_movers()`: New view for bulk delete

3. **strategies/urls.py** (lines 12-13)
   - Added routes for delete_mover and delete_all_movers

4. **strategies/templates/strategies/pre_market_movers.html** (lines 28-134, 327-362, 491-499)
   - Replaced manual symbol textarea with filter dropdowns
   - Added loading indicator with spinner animation
   - Added "Delete All" button at top of tracked movers section
   - Added individual delete button on each mover card

5. **strategies/management/commands/scan_premarket_movers.py** (lines 30-101)
   - Added --discovery flag for automated scanning
   - Updated defaults: threshold from 5.0 to 2.5 in discovery mode
   - Added mode-specific messaging

### Database Changes

**No schema changes** - All changes are UI/logic only

### New Features

#### 1. **Discovery Mode (One-Click Scanning)**

**Template:** strategies/templates/strategies/pre_market_movers.html:28-46
```html
<form method="post" action="{% url 'strategies:scan_movers' %}" id="scanForm">
    {% csrf_token %}
    <input type="hidden" name="discovery_mode" value="true">

    <!-- 4 filter dropdowns here -->

    <button type="submit" id="scanButton">
        Scan for Movers
    </button>
</form>
```

**View:** strategies/views.py:156-168
```python
def scan_movers(request):
    discovery_mode = request.POST.get('discovery_mode', '').lower() == 'true'

    # Get filter parameters
    universe_name = request.POST.get('universe', 'comprehensive')
    threshold = float(request.POST.get('threshold', '2.5'))
    min_rvol = float(request.POST.get('min_rvol', '0'))
    max_spread = float(request.POST.get('max_spread', '999'))

    if discovery_mode:
        from strategies.market_universe import get_market_universe
        symbols = get_market_universe(universe_name)
        logger.info(f"Discovery scan started: {len(symbols)} symbols from '{universe_name}', threshold {threshold}%")
```

**Why this approach:**
- Hidden input `discovery_mode=true` distinguishes from future manual mode
- Loads market universe dynamically based on filter selection
- Default to 'comprehensive' (410 stocks) for balance of speed vs coverage

#### 2. **Smart Filters (Pre-Scan Configuration)**

**Template:** strategies/templates/strategies/pre_market_movers.html:34-97
```html
<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    <!-- Universe Filter -->
    <select name="universe">
        <option value="comprehensive" selected>Comprehensive (410 stocks)</option>
        <option value="sp500">S&P 500 Top 200</option>
        <option value="nasdaq">NASDAQ 100</option>
        <option value="all">All Universe (488 stocks)</option>
    </select>

    <!-- Threshold Filter -->
    <select name="threshold">
        <option value="1.0">±1.0% (More results)</option>
        <option value="2.5" selected>±2.5% (Recommended)</option>
        <option value="5.0">±5.0% (Strong movers)</option>
        <option value="10.0">±10.0% (Extreme movers)</option>
    </select>

    <!-- RVOL Filter -->
    <select name="min_rvol">
        <option value="0" selected>Any volume</option>
        <option value="1.5">1.5x+ (Above average)</option>
        <option value="2.0">2.0x+ (High conviction)</option>
        <option value="3.0">3.0x+ (Strong conviction)</option>
    </select>

    <!-- Spread Filter -->
    <select name="max_spread">
        <option value="999" selected>Any spread</option>
        <option value="1.0">< 1.0% (Liquid)</option>
        <option value="2.0">< 2.0% (Tradeable)</option>
    </select>
</div>
```

**Backend filtering:** strategies/views.py:180-195
```python
# Apply filters
filtered_stocks = []
for stock in stocks:
    # Threshold filter
    if abs(stock.change_percent) < threshold:
        continue

    # RVOL filter
    if min_rvol > 0 and (stock.relative_volume_ratio is None or stock.relative_volume_ratio < min_rvol):
        continue

    # Spread filter
    if max_spread < 999 and (stock.spread_percent is None or stock.spread_percent > max_spread):
        continue

    filtered_stocks.append(stock)

logger.info(f"Discovery scan: {len(filtered_stocks)} movers found after filters")
```

**Why these specific filters:**
- **Universe:** Let users control scan breadth (speed vs coverage trade-off)
- **Threshold:** Standard mover detection (1% catches noise, 10% misses opportunities)
- **RVOL:** Volume conviction filter (high RVOL = institutional interest)
- **Spread:** Liquidity filter (wide spread = hard to execute trades profitably)

#### 3. **Loading Indicator**

**JavaScript:** strategies/templates/strategies/pre_market_movers.html:128-133
```javascript
document.getElementById('scanForm').addEventListener('submit', function() {
    document.getElementById('scanButton').disabled = true;
    document.getElementById('scanButtonText').textContent = 'Scanning...';
    document.getElementById('loadingIndicator').classList.remove('hidden');
});
```

**Indicator UI:** strategies/templates/strategies/pre_market_movers.html:113-119
```html
<div id="loadingIndicator" class="hidden mt-3 flex items-center text-blue-600 dark:text-blue-400">
    <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    <span class="font-medium">Scanning market... This may take 30-60 seconds</span>
</div>
```

**Why this approach:**
- Pure JavaScript (no dependencies)
- Disables button to prevent duplicate requests
- Spinner animates with Tailwind's animate-spin utility
- Sets user expectation with time estimate

#### 4. **Scan Results Persistence**

**Before (lost results):** strategies/views.py:27 (old)
```python
# Old code - cleared results immediately
scan_results = request.session.pop('scan_results', None)
```

**After (keeps results):** strategies/views.py:27-28
```python
# New code - keeps results in session
scan_results = request.session.get('scan_results', None)
scan_filters = request.session.get('scan_filters', {})
```

**Force session save:** strategies/views.py:219-227
```python
# Store results and filters in session (persistent across page loads)
request.session['scan_results'] = results
request.session['scan_filters'] = {
    'universe': universe_name,
    'threshold': threshold,
    'min_rvol': min_rvol,
    'max_spread': max_spread,
}
request.session.modified = True  # Force session save
```

**Why this matters:**
- User tracks a stock → page refreshes → scan results still visible
- Can track multiple stocks from same scan without re-scanning
- Session cleared only on new scan (expected behavior)

#### 5. **Delete Functionality**

**Individual delete view:** strategies/views.py:327-341
```python
@login_required
def delete_mover(request, mover_id):
    """Delete a single pre-market mover"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    try:
        mover = PreMarketMover.objects.get(id=mover_id)
        symbol = mover.symbol
        mover.delete()
        logger.info(f"Deleted mover: {symbol} (ID: {mover_id})")
    except PreMarketMover.DoesNotExist:
        logger.error(f"Mover with id {mover_id} not found")

    return redirect('strategies:pre_market_movers')
```

**Bulk delete view:** strategies/views.py:344-354
```python
@login_required
def delete_all_movers(request):
    """Delete all pre-market movers"""
    if request.method != 'POST':
        return redirect('strategies:pre_market_movers')

    count = PreMarketMover.objects.count()
    PreMarketMover.objects.all().delete()
    logger.info(f"Deleted all {count} movers")

    return redirect('strategies:pre_market_movers')
```

**UI - Bulk delete button:** strategies/templates/strategies/pre_market_movers.html:332-340
```html
{% if movers.count > 0 %}
<form method="post" action="{% url 'strategies:delete_all_movers' %}"
      onsubmit="return confirm('Are you sure you want to delete all {{ movers.count }} tracked movers? This cannot be undone.');">
    {% csrf_token %}
    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 px-4 rounded-lg">
        🗑️ Delete All ({{ movers.count }})
    </button>
</form>
{% endif %}
```

**UI - Individual delete button:** strategies/templates/strategies/pre_market_movers.html:491-499
```html
<form method="post" action="{% url 'strategies:delete_mover' mover.id %}"
      class="inline" onsubmit="return confirm('Delete {{ mover.symbol }}?');">
    {% csrf_token %}
    <button type="submit" class="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium">
        🗑️ Delete
    </button>
</form>
```

**Why this approach:**
- Both actions POST to prevent accidental deletes from browser prefetch
- Confirmation dialogs prevent accidental clicks
- Bulk delete only shows when movers exist (progressive disclosure)
- Logs deletions for audit trail

## Testing Guide

### Manual Testing Steps

#### Test 1: Discovery Scan with Default Filters
1. Visit http://localhost:8000/strategies/pre-market-movers/
2. Click "Scan for Movers" button (don't change filters)
3. **Expected:**
   - Button text changes to "Scanning..."
   - Loading spinner appears
   - After 30-60 seconds, table populates with movers
   - Movers have ±2.5% or higher change
4. **Verify:** Check console logs for "Discovery scan started: 410 symbols"

#### Test 2: Filter Combinations
1. Set filters: S&P 500 + ±5.0% + 2.0x RVOL + <1.0% spread
2. Click "Scan for Movers"
3. **Expected:** Fewer results, all meeting filter criteria
4. **Verify:** Each result has RVOL ≥ 2.0x and spread < 1.0%

#### Test 3: Scan Results Persistence
1. Complete a scan (Test 1 or 2)
2. Click "+ Track" on any stock
3. **Expected:** Page refreshes, scan results still visible
4. Track another stock
5. **Expected:** Scan results still visible
6. **Verify:** Can track multiple stocks without re-scanning

#### Test 4: Loading Indicator
1. Clear browser cache/session
2. Click "Scan for Movers"
3. **Expected:** Loading indicator shows immediately
4. **Verify:** Indicator disappears after results load
5. **Verify:** Button is disabled during scan

#### Test 5: Individual Delete
1. Track 2-3 stocks
2. Click "🗑️ Delete" on one stock
3. **Expected:** Confirmation dialog appears
4. Click OK
5. **Expected:** Stock removed, page refreshes
6. **Verify:** Other stocks still present

#### Test 6: Bulk Delete
1. Track 5+ stocks
2. Click "Delete All (5)" button at top
3. **Expected:** Confirmation dialog: "Are you sure you want to delete all 5 tracked movers?"
4. Click OK
5. **Expected:** All movers deleted, empty state shows
6. **Verify:** Database empty (check admin)

#### Test 7: Dark Mode
1. Toggle dark mode (moon icon)
2. **Verify:** All new UI elements have proper contrast:
   - Filter dropdowns readable
   - Loading indicator visible
   - Delete buttons styled correctly

#### Test 8: Edge Cases
1. **No movers found:**
   - Set filters: ±10.0% + 3.0x RVOL + <1.0% spread
   - **Expected:** Empty state message
2. **Market closed (off-hours):**
   - Run scan at 5PM ET
   - **Expected:** Fewer movers, some missing RVOL/spread data (shows "—")
3. **Invalid symbols:**
   - Market universe cleaned up (ANSS, WISH, CANO, NKLA removed)
   - **Expected:** No 404 errors in logs

### Known Limitations

1. **Scan speed:** 410 symbols takes 30-60 seconds (yfinance rate limits)
   - **Mitigation:** Loading indicator sets expectation
   - **Future:** Consider paid API (Polygon.io) for sub-10s scans

2. **Off-hours data:** Volume metrics may be null when market closed
   - **Mitigation:** UI shows "—" for null values
   - **Future:** Cache last known values or show "Market Closed" banner

3. **Session expiry:** Scan results lost if session expires (default: 2 weeks)
   - **Mitigation:** Users re-scan easily with saved filters
   - **Future:** Consider localStorage backup

4. **Mobile UX:** 4 filter dropdowns stack vertically on mobile
   - **Current:** Functional but takes vertical space
   - **Future:** Collapsible filter section or horizontal scroll

## Questions for Codex

### 1. Architecture: Session vs Database for Scan Results

**Current approach:** Store scan results in Django session (in-memory/cache)

**Pros:**
- Fast read/write (no DB queries)
- Automatic expiry
- No cleanup needed

**Cons:**
- Lost on session expiry
- Not shareable between devices
- Limited size (default 4KB)

**Alternative:** Store as `ScanSession` model with foreign key to user

**Question:** Is session storage appropriate for scan results, or should we persist to DB?

### 2. Performance: Parallel API Requests

**Current approach:** Sequential yfinance requests (one at a time)

**Performance:**
- 410 symbols = 30-60 seconds
- Acceptable for now

**Alternative:** asyncio or threading for parallel requests

**Question:** Given yfinance doesn't support async natively, is threading worth the complexity? Or acceptable as-is?

### 3. Edge Cases: Filter Validation

**Current validation:** None - trusts form values

**Potential issues:**
- User could POST invalid threshold (e.g., "-5" or "abc")
- User could POST invalid universe name

**Current behavior:** float() raises ValueError, crashes request

**Question:** Should we add try/except with validation, or is form-level validation sufficient?

### 4. Alternatives: Frontend Framework

**Current approach:** Vanilla JavaScript + Django templates

**Pros:**
- Simple, no build step
- Server-rendered (SEO-friendly)
- Works without JS

**Cons:**
- Full page reload on every action
- Loading indicator requires page refresh to disappear
- No real-time updates

**Alternative:** React/Vue with Django REST API

**Question:** Is vanilla JS sufficient for this app's complexity, or should we consider a frontend framework?

## Next Phase Plan

### Phase 3: Market Context & Advanced Metrics

**Overview:**
Add contextual market data to improve trade timing and sizing decisions.

**Features:**
1. **Futures Context**
   - Display SPY, QQQ, IWM pre-market prices
   - Show futures sentiment (green/red)
   - Alert if market sentiment conflicts with mover direction

2. **VWAP Integration**
   - Calculate Volume-Weighted Average Price
   - Show pre-market VWAP vs current price
   - Flag opportunities above/below VWAP

3. **Pre-Market Range**
   - Track pre-market high/low
   - Calculate range % (volatility indicator)
   - Show current position in range (top/middle/bottom)

4. **Historical Performance**
   - Track executed trades (entry/exit/P&L)
   - Calculate win rate by setup type
   - Show cumulative P&L graph

**Dependencies:**
- Phase 2 complete (discovery working)
- May need paid API for VWAP data (Polygon.io or Alpaca)

**Estimated Timeline:** 2-3 weeks

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

[To be added after Codex provides feedback]

---

## Codex Review Fixes - [Date]

[To be added after implementing Codex suggestions]

---

Last Updated: October 29, 2025
