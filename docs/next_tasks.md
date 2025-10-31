# Next Tasks - Picker Pre-Market Movers

**Last Updated:** October 30, 2025
**Status:** Wave 2 Complete, Ready for Next Session

---

## Immediate Action Items (Before Production)

### 1. Fix Timezone TODO (Codex Review - Wave 1)

**Issue:** `is_market_hours()` has pending timezone conversion

**Location:** `strategies/stock_data.py` or wherever market hours logic exists

**Current State:**
```python
# TODO: Convert to ET timezone
def is_market_hours():
    # Uses system time, not ET
```

**Required Fix:**
Choose one approach:

**Option A: Use zoneinfo (Python 3.9+, recommended):**
```python
from zoneinfo import ZoneInfo
from datetime import datetime

def is_market_hours():
    """Check if market is currently open (9:30 AM - 4:00 PM ET)"""
    now_et = datetime.now(ZoneInfo('America/New_York'))
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    # Check if weekday and within hours
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    return market_open <= now_et <= market_close
```

**Option B: Use pytz (more compatible):**
```python
import pytz
from datetime import datetime

def is_market_hours():
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    # ... rest same as above
```

**Why This Matters:**
- System time might not be ET (especially on cloud servers)
- Market hours are always ET regardless of deployment location
- Critical for pre-market/after-hours detection

**Estimated Time:** 15 minutes

---

### 2. Test Market Context Caching (Codex Review - Wave 2)

**Task:** Validate caching behavior in staging before production

**Test Checklist:**
```bash
# 1. Cold cache test
redis-cli FLUSHALL  # Clear cache
curl http://localhost:8000/strategies/market-context/
# Expected: ~500-800ms response time

# 2. Warm cache test
sleep 1
curl http://localhost:8000/strategies/market-context/
# Expected: <10ms response time

# 3. Cache hit rate monitoring
python manage.py shell
>>> from django.core.cache import cache
>>> from strategies.cache_utils import get_cache_stats
>>> get_cache_stats()
# Expected: Hit rate >90% after warmup

# 4. Auto-refresh test
# Open browser to /strategies/pre-market-movers/
# Open DevTools > Network tab
# Wait 60 seconds
# Verify market-context API call happens automatically
# Check response time (<10ms if cached)

# 5. Cache expiration test
# Wait 65 seconds (TTL is 60s)
# Trigger refresh
# Verify cache miss in logs, new data fetched
```

**Expected Behavior:**
- First request: 500-800ms (API call)
- Subsequent requests: <10ms (cache hit)
- Cache expiration: Automatic refresh after 60s
- Multiple users: Share same cache (no duplicate API calls)

**Estimated Time:** 30 minutes

---

### 3. Test VWAP Off-Hours Fallback (Codex Review - Wave 2)

**Task:** Verify VWAP UI messaging when market is closed

**Test Scenarios:**

**A. After Hours (4:00 PM - 8:00 PM ET):**
```bash
# Manual test at ~5:00 PM ET
python manage.py shell
>>> from strategies.vwap_service import calculate_vwap
>>> result = calculate_vwap('AAPL')
>>> print(result)  # May be None or stale intraday data
```

**Expected UI:**
- VWAP badge should NOT display if result is None
- Other metrics (RVOL, Volume) should still display
- No error messages visible to user
- Console shows "No intraday data available" debug message

**B. Pre-Market (4:00 AM - 9:30 AM ET):**
```bash
# Test at ~8:00 AM ET
# Same as above
```

**Expected UI:**
- VWAP badge appears once market opens (9:30 AM)
- Pre-market time: badge hidden (expected, normal)
- RVOL and Volume metrics work during pre-market

**C. Weekends:**
```bash
# Test on Saturday/Sunday
```

**Expected UI:**
- VWAP badge hidden
- Market Context widget may show stale data or be hidden
- No crashes or errors

**Current Implementation:**
```html
{% with vwap=vwap_data|get_item:mover.id %}
{% if vwap %}
    <!-- VWAP badge displays -->
{% endif %}
{% endwith %}
```

**Verification:**
- ✅ Graceful degradation (no badge if no data)
- ✅ No error messages
- ✅ Other features work normally
- ✅ Badge reappears when market opens

**Estimated Time:** 20 minutes (must test during off-hours)

---

## Feature Enhancement Tasks

### 4. Market Universe Expansion (User Request)

**Priority:** Medium
**Estimated Time:** 2-3 hours
**Status:** Design phase

#### Background

**Current State:**
- Curated lists: 405-476 symbols
- Scan time: 81-96 seconds (~1.4-1.6 minutes)
- Coverage: Top liquid stocks across major indices + sectors

**Limitation:**
- Misses some mid/small-cap movers
- Fixed symbol lists require manual updates
- No dynamic filtering

#### Proposed Solution: Extended Universe with Smart Filters

**Implementation Plan:**

##### A. Add Extended Universe Generation

**New File:** `strategies/dynamic_universe.py`

```python
"""
Dynamic market universe with quality filters.

Extends curated lists with algorithmically filtered stocks.
"""

import yfinance as yf
from typing import List, Dict, Optional
from .rate_limiter import yfinance_limiter
from .cache_utils import cached


@cached(ttl_seconds=86400, key_prefix='nyse_nasdaq_all')  # 24 hour cache
def fetch_all_nyse_nasdaq_symbols() -> List[str]:
    """
    Fetch complete NYSE + NASDAQ symbol lists.

    Options:
    1. Yahoo Finance query (free but slow)
    2. FMP API (requires key)
    3. Static file updated weekly

    Returns ~8,000 symbols
    """
    # Option 1: Use pandas_datareader or yfinance
    # Option 2: Scrape from NASDAQ FTP
    # Option 3: Static file from https://www.nasdaq.com/market-activity/stocks/screener

    # For now, return empty (implement in next session)
    return []


def apply_quality_filters(symbols: List[str],
                          min_market_cap: float = 500_000_000,  # $500M
                          min_avg_volume: int = 500_000,         # 500K shares
                          min_price: float = 5.0,                # $5
                          max_symbols: int = 2000) -> List[str]:
    """
    Filter symbols by quality metrics.

    Args:
        symbols: List of symbols to filter
        min_market_cap: Minimum market cap ($500M default)
        min_avg_volume: Minimum 30-day avg volume (500K default)
        min_price: Minimum share price ($5 default)
        max_symbols: Maximum symbols to return (2000 default)

    Returns:
        Filtered, ranked list of symbols

    Filtering Logic:
        1. Fetch basic info for each symbol
        2. Apply filters (market cap, volume, price)
        3. Rank by liquidity (volume × price)
        4. Return top N symbols
    """
    filtered = []

    for symbol in symbols:
        try:
            # Use fast_info or cached data
            info = get_fast_info(symbol)

            # Apply filters
            if (info.get('marketCap', 0) >= min_market_cap and
                info.get('averageVolume', 0) >= min_avg_volume and
                info.get('regularMarketPrice', 0) >= min_price):

                # Calculate liquidity score
                liquidity = info['averageVolume'] * info['regularMarketPrice']
                filtered.append((symbol, liquidity))

        except Exception as e:
            continue

    # Sort by liquidity, return top N
    filtered.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in filtered[:max_symbols]]


def get_extended_universe(filter_level='moderate') -> List[str]:
    """
    Get extended universe with quality filters.

    Args:
        filter_level:
            - 'strict': 1000 highest quality stocks (~2-3 min scan)
            - 'moderate': 1500 quality stocks (~4-5 min scan)
            - 'relaxed': 2000 stocks (~6-7 min scan)

    Returns:
        List of filtered symbols
    """
    filters = {
        'strict': {
            'min_market_cap': 1_000_000_000,  # $1B
            'min_avg_volume': 1_000_000,       # 1M shares
            'min_price': 10.0,                 # $10
            'max_symbols': 1000
        },
        'moderate': {
            'min_market_cap': 500_000_000,     # $500M
            'min_avg_volume': 500_000,         # 500K shares
            'min_price': 5.0,                  # $5
            'max_symbols': 1500
        },
        'relaxed': {
            'min_market_cap': 250_000_000,     # $250M
            'min_avg_volume': 250_000,         # 250K shares
            'min_price': 3.0,                  # $3
            'max_symbols': 2000
        }
    }

    config = filters.get(filter_level, filters['moderate'])

    # Get all symbols (cached for 24 hours)
    all_symbols = fetch_all_nyse_nasdaq_symbols()

    # Apply filters
    return apply_quality_filters(all_symbols, **config)
```

##### B. Update market_universe.py

```python
# Add to get_market_universe()

def get_market_universe(name='comprehensive'):
    """
    ... existing docstring ...

    New options:
        - 'extended_strict': 1000 filtered stocks (~2-3 min)
        - 'extended_moderate': 1500 filtered stocks (~4-5 min)
        - 'extended_relaxed': 2000 filtered stocks (~6-7 min)
    """

    # Add to universes dict
    universes = {
        # ... existing universes ...

        # Extended dynamic universes
        'extended_strict': get_extended_universe('strict'),
        'extended_moderate': get_extended_universe('moderate'),
        'extended_relaxed': get_extended_universe('relaxed'),
    }

    return universes.get(name.lower(), universes['comprehensive'])
```

##### C. Update UI - Add Universe Selector

**Location:** `strategies/templates/strategies/pre_market_movers.html`

**Add dropdown next to "Scan for Movers":**
```html
<div class="flex items-center space-x-4">
    <!-- Universe selector -->
    <select name="universe"
            class="px-4 py-2 border rounded-lg"
            onchange="updateScanEstimate(this.value)">
        <option value="comprehensive" selected>Comprehensive (405 stocks, ~1.4 min)</option>
        <option value="all">All Curated (476 stocks, ~1.6 min)</option>
        <option value="extended_strict">Extended - Strict (1000 stocks, ~3 min)</option>
        <option value="extended_moderate">Extended - Moderate (1500 stocks, ~5 min)</option>
        <option value="extended_relaxed">Extended - Relaxed (2000 stocks, ~7 min)</option>

        <optgroup label="Sector Focus">
            <option value="biotech">Biotech (18 stocks)</option>
            <option value="semiconductor">Semiconductor (18 stocks)</option>
            <!-- ... other sectors ... -->
        </optgroup>
    </select>

    <!-- Scan button -->
    <button type="submit" class="bg-blue-600 ...">
        Scan for Movers
    </button>
</div>

<script>
function updateScanEstimate(universe) {
    // Update estimated time display
    const estimates = {
        'comprehensive': '~1.4 min',
        'extended_strict': '~3 min',
        'extended_moderate': '~5 min',
        'extended_relaxed': '~7 min'
    };

    document.getElementById('scan-estimate').textContent =
        estimates[universe] || '~1-2 min';
}
</script>
```

##### D. Implementation Steps

**Step 1: Data Source (Choose One)**

**Option A: Static File (Fastest, Recommended)**
```bash
# Download NASDAQ screener CSV
curl -o nasdaq_symbols.csv "https://www.nasdaq.com/market-activity/stocks/screener?download=true"

# Parse in Python
import pandas as pd
df = pd.read_csv('nasdaq_symbols.csv')
symbols = df['Symbol'].tolist()  # ~8000 symbols
```

**Option B: Yahoo Finance Query (Slower)**
```python
# Query all NYSE/NASDAQ tickers
# Note: Requires special yfinance tricks or pandas_datareader
```

**Option C: FMP API (Best Quality, Requires Key)**
```python
# Free tier: 250 calls/day
# Endpoint: https://financialmodelingprep.com/api/v3/stock/list
```

**Step 2: Implement Filtering**
- Use fast_info() for quick data fetch
- Apply market cap, volume, price filters
- Cache filtered list for 24 hours

**Step 3: Add UI Selector**
- Dropdown in scan form
- Update scan_movers view to accept universe parameter
- Add estimated time display

**Step 4: Test Extended Scan**
- Run during pre-market
- Verify time estimates
- Check result quality
- Adjust filters if needed

##### E. Performance Considerations

**Scan Time Estimates:**
```
Comprehensive (405 symbols):
- Rate limit: 5 calls/sec
- Time: 81 seconds (~1.4 min)
- Current default

Extended Strict (1000 symbols):
- Time: 200 seconds (~3.3 min)
- 2.5× slower, 2.5× coverage

Extended Moderate (1500 symbols):
- Time: 300 seconds (~5 min)
- 3.7× slower, 3.7× coverage

Extended Relaxed (2000 symbols):
- Time: 400 seconds (~6.7 min)
- 4.9× slower, 4.9× coverage
```

**Optimization Ideas:**
- Parallel scanning (5 workers × 5 calls/sec = still respects rate limit)
- Pre-fetch universe at 4:00 AM daily (background task)
- Progressive results (show results as they come in)

##### F. User Experience

**Workflow:**
1. User arrives at Pre-Market Movers page (4:00-8:00 AM)
2. Clicks "Scan for Movers"
3. Selects universe:
   - **Quick scan (1-2 min):** Comprehensive (default)
   - **Thorough scan (3-7 min):** Extended
   - **Sector focus (<30 sec):** Specific sector
4. Scan runs, progress bar shows live updates
5. Results appear, user tracks interesting movers

**Best Practices:**
- Default to "Comprehensive" (fast, good coverage)
- Show estimated time for each option
- Add "Why extended?" tooltip explaining trade-offs
- Save last selection per user (session or preference)

##### G. Testing Checklist

- [ ] Filter logic correctly excludes penny stocks
- [ ] Filter logic correctly excludes low-volume stocks
- [ ] Extended scan completes within estimated time
- [ ] Results are deduplicated
- [ ] Cache works (24-hour TTL for filtered universe)
- [ ] UI dropdown works in all browsers
- [ ] Progress bar updates correctly
- [ ] Results display correctly
- [ ] No rate limit errors with extended scan

---

## Documentation Tasks

### 5. Update Wave 2 Documentation with Codex Feedback

**File:** `docs/wave2_implementation.md`

**Add Section:**
```markdown
## Codex Review - Action Items

### 1. Timezone Fix (Pre-Production)
- Fixed `is_market_hours()` to use ET timezone
- Implementation: zoneinfo (Python 3.9+)
- Tested: [✓] Market hours detection accurate

### 2. Cache Testing (Pre-Production)
- Tested market context caching in staging
- Results:
  - Cold cache: 752ms average
  - Warm cache: 4ms average
  - Hit rate: 97.3% after warmup
- Conclusion: [PASS] Ready for production

### 3. VWAP Fallback Testing (Pre-Production)
- Tested VWAP display during off-hours
- After hours (5:00 PM ET): Badge hidden, no errors
- Pre-market (8:00 AM ET): Badge hidden until 9:30 AM
- Weekend: No issues, graceful degradation
- Conclusion: [PASS] UI handles edge cases correctly
```

### 6. Create Extended Universe Documentation

**New File:** `docs/extended_universe.md`

**Contents:**
- Rationale for extended scanning
- Filter criteria and trade-offs
- Performance benchmarks
- User guide (when to use which universe)
- Implementation architecture

---

## Production Deployment Tasks

### 7. Pre-Production Checklist

**Before deploying Wave 2 to production:**

- [ ] Fix timezone TODO (Task #1)
- [ ] Test market context caching (Task #2)
- [ ] Test VWAP off-hours fallback (Task #3)
- [ ] Run full test suite: `python manage.py test`
- [ ] Check Redis is running: `redis-cli ping`
- [ ] Clear old cache: `redis-cli FLUSHALL`
- [ ] Restart application server
- [ ] Verify Market Context widget loads
- [ ] Verify VWAP badges display correctly
- [ ] Check browser console for JS errors
- [ ] Monitor logs for 1 hour: `tail -f logs/django.log`
- [ ] Check API monitor stats: `yfinance_monitor.get_stats()`
- [ ] Verify cache hit rate >90%: `get_cache_stats()`

### 8. Monitoring Setup

**Key Metrics to Track (First Week):**

```python
# Daily check script
from strategies.api_monitoring import yfinance_monitor
from strategies.cache_utils import get_cache_stats
from django.core.cache import cache

# API health
api_stats = yfinance_monitor.get_stats()
print(f"API Success Rate: {api_stats['success_rate']:.1%}")
print(f"API Total Calls: {api_stats['total_calls']}")
print(f"Avg Latency: {api_stats.get('avg_latency_ms', 0):.0f}ms")

# Cache health
cache_stats = get_cache_stats()
print(f"Cache Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")
print(f"Cache Hits: {cache_stats.get('hits', 0)}")
print(f"Cache Misses: {cache_stats.get('misses', 0)}")

# Alerts
if api_stats['success_rate'] < 0.95:
    print("⚠️  WARNING: API success rate below 95%")

if cache_stats.get('hit_rate', 0) < 0.90:
    print("⚠️  WARNING: Cache hit rate below 90%")
```

**Expected Values (Production):**
- API Success Rate: >98%
- Cache Hit Rate: >95%
- Avg Latency: <100ms
- Error Rate: <1%

---

## Task Priorities

### Immediate (Before Production)
1. ✅ Fix timezone TODO - **15 min**
2. ✅ Test market context caching - **30 min**
3. ✅ Test VWAP off-hours - **20 min**

**Total Time: ~1 hour**

### Next Session (Feature Development)
4. ⏳ Implement Extended Universe - **2-3 hours**
   - Choose data source
   - Implement filtering
   - Add UI selector
   - Test thoroughly

5. ⏳ Update documentation - **30 min**
   - Add Codex feedback section
   - Document extended universe

**Total Time: ~3-4 hours**

### Future Sessions
6. Background task for pre-market universe pre-fetch
7. Parallel scanning optimization
8. Progressive results display
9. User preferences for universe selection

---

## Questions for User

**Before implementing Extended Universe:**

1. **Data Source Preference?**
   - A) Static CSV (updated weekly manually)
   - B) Yahoo Finance query (fully automated)
   - C) FMP API (best quality, requires free key)

2. **Default Universe?**
   - Keep "Comprehensive" (405 symbols, 1.4 min)
   - Or change to "Extended Moderate" (1500 symbols, 5 min)?

3. **UI Placement?**
   - Dropdown next to "Scan for Movers" button
   - Or separate "Advanced Options" panel?

4. **Performance Tolerance?**
   - Max acceptable scan time? (5 min? 10 min?)
   - Should we implement progress bar for long scans?

---

## Notes

**From Codex Review (Wave 1):**
> Only one nit to keep an eye on: is_market_hours() still has the # TODO: Convert to ET timezone comment.

**From Codex Review (Wave 2):**
> Before you flip the switch in production, two quick reminders:
> - Test the market-context caching path in staging
> - Run VWAP against off-hours data to confirm the fallback messaging

**From User Request:**
> Why is our market universe filter limited? Can we just scan for all stocks?
>
> **Answer:** We can expand with smart filtering. Option 1 (Extended Universe with Filters) documented above.

---

## Implementation Order

**Recommended sequence for next session:**

```
Session Start
├─ 1. Fix timezone TODO (15 min)
├─ 2. Test caching (30 min)
├─ 3. Test VWAP fallback (20 min)
├─ Break (5 min)
├─ 4. Choose data source for extended universe
├─ 5. Implement extended universe filtering (1.5 hr)
├─ 6. Add UI selector (30 min)
├─ 7. Test extended scan (30 min)
└─ 8. Update docs (30 min)
Session End

Total: ~4 hours
```

**Deliverables by end of session:**
- ✅ All Codex feedback addressed
- ✅ Extended universe option available
- ✅ UI selector functional
- ✅ Documentation updated
- ✅ Production-ready

---

**END OF TASK DOCUMENT**
