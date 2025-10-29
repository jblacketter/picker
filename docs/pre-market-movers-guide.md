# Pre-Market Movers Tool - User Guide

## Overview

The Pre-Market Movers tool helps you identify and track stocks with significant activity during pre-market or after-hours trading, typically driven by news events.

**Strategy:** Identify news-driven stocks with momentum, research the opportunity, buy at market open, and sell on the upward swing.

## How to Access

**Navigation:** Click "Tools" in the top menu → Select "Pre-Market Movers"

**Direct URL:** http://localhost:8000/strategies/pre-market-movers/

## Features

### 1. Add Pre-Market Movers

Track stocks showing significant pre-market activity:

**Required Fields:**
- **Stock Symbol** - Ticker symbol (e.g., AAPL, TSLA)
- **News Headline** - What's driving the movement

**Optional Fields:**
- **Company Name** - Full company name
- **Movement %** - Pre-market percentage change
- **News Source** - Where you found the news (Reuters, Bloomberg, etc.)
- **News URL** - Link to the news article

**Two Options:**
1. **Add Mover** - Simply add to your tracking list
2. **Add + Get AI Analysis** - Add the mover and immediately get AI analysis of the opportunity

### 2. AI Analysis

When you click "Add + Get AI Analysis", the system:
- Analyzes the news and stock movement
- Provides 2-3 sentence assessment
- Determines sentiment (bullish, bearish, neutral)
- Highlights key factors to watch
- Automatically updates status to "Researching"

### 3. Status Tracking

Track each opportunity through your workflow:

- **Identified** - Just added, initial review pending
- **Researching** - Investigating the opportunity (AI analysis complete)
- **Ready to Trade** - Decision made, prepared to execute
- **Executed** - Trade completed
- **Passed** - Decided not to pursue

### 4. Filter by Status

Use the tabs at the top of the page to filter:
- **All** - See everything
- **Identified** - New opportunities
- **Researching** - Under investigation
- **Ready to Trade** - Prepared to execute
- **Executed** - Completed trades

### 5. Track Trade Performance

For executed trades, track your results via the admin panel:

1. Click "Edit Details" on a mover
2. Add Entry Price (what you bought at)
3. Add Exit Price (what you sold at)
4. System automatically calculates Profit/Loss
5. Set Executed At timestamp
6. Change status to "Executed"

## Workflow Example

### Morning Routine (Pre-Market)

1. **Scan for News** (6:00 AM - 9:30 AM ET)
   - Check financial news sites
   - Look for earnings releases, FDA approvals, major announcements
   - Identify stocks with >3% pre-market movement

2. **Add to Picker**
   - Enter symbol and news headline
   - Click "Add + Get AI Analysis"
   - Review AI assessment

3. **Research** (If opportunity looks promising)
   - Read the full news article
   - Check stock's recent performance
   - Review analyst opinions
   - Update status to "Ready to Trade" if confident

4. **Execute at Market Open** (9:30 AM ET)
   - Buy at market open
   - Set your exit target (e.g., +5%, +10%)
   - Monitor throughout the morning

5. **Track Results**
   - Record entry and exit prices in admin
   - System calculates P/L
   - Review what worked/didn't work

## Example Use Cases

### Case 1: Earnings Beat
```
Symbol: ABC
News: Company beats earnings by 20%, raises guidance
Movement: +8.5%
Strategy: Strong earnings beat often continues upward at open
AI Analysis: "Significant earnings beat suggests strong momentum.
Watch for profit-taking after initial surge."
```

### Case 2: FDA Approval
```
Symbol: XYZ
News: FDA approves breakthrough drug treatment
Movement: +15.2%
Strategy: FDA approvals can trigger sustained rallies
AI Analysis: "Major catalyst that validates years of development.
Monitor for partnership announcements."
```

### Case 3: Bad News (Short Opportunity)
```
Symbol: DEF
News: CEO resigns amid investigation
Movement: -12.3%
Strategy: Sometimes decline continues at open
AI Analysis: "Leadership uncertainty creates risk.
Watch for further disclosures."
```

## Tips for Success

### Identify Strong Candidates
- Look for >5% pre-market moves
- Prefer positive news (easier upward momentum)
- Company-specific news > market-wide news
- Check volume - high volume = more conviction

### Risk Management
- Never risk more than you can afford to lose
- Set stop-losses
- Take profits when targets hit
- Don't chase - if you miss entry, wait for next opportunity

### What to Avoid
- Stocks with unclear/confusing news
- Low-volume pre-market moves (could be false signals)
- Stocks already at 52-week highs (less room to run)
- News that's already been "priced in"

## Integration with Other Tools

### Link to Watchlist
Stocks you're tracking long-term can be added to your Watchlist from the admin panel.

### Link to Research
Use the general Research tool to deep-dive on companies you're considering for pre-market trades.

## Admin Features

Access more detailed management at: http://localhost:8000/admin/strategies/premarketmover/

**Admin capabilities:**
- Edit all fields
- Bulk actions
- Filter by date, status, sentiment
- Export data
- View profit/loss summary

## Data Tracked

For each pre-market mover:
- Basic Info: Symbol, company, news
- Movement: Pre-market %, price
- AI Analysis: Analysis text, sentiment
- Trading: Entry/exit prices, P/L
- Dates: Identified, trade date, executed
- Notes: Your strategy notes

## Best Practices

1. **Document Everything** - Add notes about why you entered/exited
2. **Review Regularly** - Analyze what works and what doesn't
3. **Be Selective** - Quality over quantity
4. **Act Fast** - Pre-market opportunities move quickly
5. **Learn from Losses** - Track failures to avoid repeating mistakes

## Future Enhancements (Phase 3)

Potential additions:
- Real-time price alerts
- Integration with brokerage for execution
- Automated news scanning
- Historical performance analytics
- Pattern recognition (what news types work best)

---

**Ready to start?** Visit http://localhost:8000/strategies/pre-market-movers/
