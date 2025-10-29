# Scanner Usage - Quick Reference

## TRUE Market Discovery

Scan hundreds of stocks to discover what's actually moving, not just check your favorites.

---

## Usage Examples

### **Best for Discovery: Comprehensive Scan**
```bash
python manage.py scan_premarket_movers --universe comprehensive --threshold 3.0
```
**Scans:** 143 stocks (S&P 500 + NASDAQ 100 + Retail Favorites)
**Best for:** Daily morning discovery

---

### **Maximum Coverage: Scan Everything**
```bash
python manage.py scan_premarket_movers --universe all --threshold 5.0
```
**Scans:** 200+ stocks (all universes combined)
**Slower but most thorough**

---

### **Fast Sector Scans**

**Biotech (FDA/clinical news):**
```bash
python manage.py scan_premarket_movers --universe biotech --threshold 3.0
```

**Semiconductors (AI/chip news):**
```bash
python manage.py scan_premarket_movers --universe semiconductor --threshold 2.0
```

**EV & Auto:**
```bash
python manage.py scan_premarket_movers --universe ev --threshold 3.0
```

**Crypto-Exposed Stocks:**
```bash
python manage.py scan_premarket_movers --universe crypto --threshold 5.0
```

**Retail/Meme Stocks:**
```bash
python manage.py scan_premarket_movers --universe retail --threshold 5.0
```

---

## Available Universes

| Universe | Symbols | Description |
|----------|---------|-------------|
| **comprehensive** | 143 | S&P 500 + NASDAQ + Retail (BEST FOR DISCOVERY) |
| **all** | 200+ | Everything combined (slower) |
| **sp500** | 100 | S&P 500 most liquid |
| **nasdaq** | 50 | NASDAQ 100 subset |
| **retail** | 20 | Meme stocks & retail favorites |
| **biotech** | 18 | Biotech movers on FDA news |
| **semiconductor** | 18 | Chip/AI stocks |
| **ev** | 9 | EV & auto stocks |
| **crypto** | 7 | Crypto-exposed stocks |
| **chinese** | 10 | Chinese ADRs |
| **defense** | 9 | Defense & aerospace |

---

## Common Options

### Threshold (% Change)
```bash
--threshold 2.0   # More movers (±2%)
--threshold 5.0   # Fewer movers (±5%, default)
--threshold 10.0  # Only big movers (±10%)
```

### Limit Results
```bash
--limit 10   # Top 10 movers
--limit 50   # Top 50 movers
```

### Dry Run (Test Without Creating)
```bash
--dry-run   # See what would be created
```

### Skip News (Faster Testing)
```bash
--skip-news   # Don't fetch Finnhub news
```

---

## Recommended Daily Workflow

**Morning Routine (8:00 AM ET):**
```bash
# Comprehensive scan for discovery
python manage.py scan_premarket_movers --universe comprehensive --threshold 3.0

# Then check specific sectors if relevant
python manage.py scan_premarket_movers --universe biotech --threshold 3.0
```

**Afternoon (Check After-Hours):**
```bash
python manage.py scan_premarket_movers --universe comprehensive --threshold 5.0
```

---

## Automation Setup

**Daily at 8:00 AM ET (crontab):**
```bash
0 13 * * 1-5 cd /Users/jackblacketter/projects/picker && /Users/jackblacketter/projects/picker/.venv/bin/python manage.py scan_premarket_movers --universe comprehensive --threshold 3.0 >> logs/scanner.log 2>&1
```

---

## Still Want Custom Watchlists?

Use the `--watchlist` flag instead:
```bash
python manage.py scan_premarket_movers --watchlist default
python manage.py scan_premarket_movers --watchlist aggressive
```

Edit watchlists in: `strategies/watchlists.py`

---

## Pro Tips

1. **Lower threshold for discovery** - Use 2-3% to catch more movers
2. **Higher threshold for automation** - Use 5%+ to reduce noise
3. **Scan multiple times** - Duplicate detection prevents re-tracking
4. **Check logs** - `tail -f logs/scanner.log` for real-time monitoring
5. **Combine sectors** - Run biotech + semiconductor + ev scans together

---

**Bottom Line:** Use `--universe comprehensive` for true market-wide discovery. This is what you wanted - find the movers, don't just check your favorites!
