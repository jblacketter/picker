# Pre-Market Mover Scanner - Feature Documentation

## Overview

The **Discover Pre-Market Movers** scanner helps you find stocks with recent news and activity BEFORE you manually add them. It's the first step in your workflow.

## How It Works

### Two Discovery Methods

#### 1. Scan Specific Symbols
**Use when:** You have a watchlist of symbols you want to monitor

**How to use:**
1. Enter symbols in the text area (comma-separated)
   - Example: `AAPL, TSLA, NVDA, AMD, META, GOOGL`
2. Click "Scan These Symbols"
3. AI analyzes recent news (24-48 hours) for each
4. Returns only stocks WITH significant news
5. Shows: Symbol, news headline, activity level, source

**Activity Levels:**
- **HIGH** - Major catalyst (earnings beat, FDA approval, major product launch)
- **MEDIUM** - Notable news (partnership, analyst upgrade, product update)
- **LOW** - Minor news (routine announcements)

#### 2. AI-Powered Discovery
**Use when:** You want suggestions for what's moving in the market

**How to use:**
1. Select a sector (or "All Sectors")
   - Technology
   - Healthcare/Biotech
   - Finance
   - Energy
   - Retail/Consumer
2. Click "Get AI Suggestions"
3. AI suggests 5-8 stocks with significant recent news
4. Focuses on major catalysts (earnings, FDA, M&A, etc.)

## Scanner Results

Results appear below the scanner in a clean list:

```
[SYMBOL] Company Name          [ACTIVITY BADGE]
News: Brief headline describing what happened
Source: Where the news came from
                                    [+ Track This]
```

**Quick Actions:**
- Click **"+ Track This"** to immediately add to your tracking list
- Stock is added with news pre-filled
- Status automatically set to "Identified"

## Complete Workflow

### Morning Routine (Example)

**6:00 AM - Pre-Market Opens**

1. **Run AI Discovery**
   - Select "All Sectors"
   - Click "Get AI Suggestions"
   - Review 5-8 stocks with overnight news

2. **Scan Your Watchlist**
   - Enter your favorite symbols
   - Click "Scan These Symbols"
   - See which ones have news today

3. **Review Results**
   - Focus on HIGH activity stocks
   - Read the news summaries
   - Click "+ Track This" for interesting ones

4. **Research Tracked Stocks**
   - Added stocks appear in list below
   - Click "Add + Get AI Analysis" for deeper dive
   - OR manually add notes

5. **Mark Ready to Trade**
   - Update status to "Ready to Trade" in admin
   - Set your entry strategy

**9:30 AM - Market Opens**
- Execute on your prepared list

## Example Scans

### Scan Specific Symbols
```
Input: AAPL, NVDA, TSLA, META, MSFT

Results:
✓ NVDA - NVIDIA beats earnings, raises guidance (+12%)
✓ TSLA - Tesla announces new Gigafactory location
× AAPL - No significant news
× META - No significant news
× MSFT - No significant news

Only stocks with news are shown!
```

### AI Suggestions (Healthcare)
```
Results:
- MRNA - Moderna gets FDA approval for new vaccine
- PFE - Pfizer announces clinical trial success
- JNJ - Johnson & Johnson settles major lawsuit
- ABBV - AbbVie completes acquisition of biotech firm
- LLY - Eli Lilly obesity drug shows promising results
```

## Integration with Tracking

Once you click "+ Track This":
- Mover is added to database
- Appears in your tracking list below
- Status: "Identified"
- Can get AI analysis
- Can add notes
- Can track through execution

## Tips for Best Results

### Symbol Scanning
- Use 5-15 symbols at a time
- Mix sectors for diversification
- Include both large caps and smaller names
- Run multiple times during pre-market (news updates)

### AI Suggestions
- Try different sectors
- Run it a few times (AI may suggest different stocks)
- Focus on sectors you understand
- Cross-reference with your research

### Activity Levels
- **HIGH** = Strong potential, big catalyst
- **MEDIUM** = Worth investigating
- **LOW** = Minor, probably skip unless you know the stock well

## Technical Details

**How scanning works:**
1. You submit symbols or request suggestions
2. System sends request to AI (Claude)
3. AI analyzes recent financial news
4. Returns structured results (JSON)
5. Results displayed in clean UI
6. One-click to add to tracking

**Token Usage:**
- Each scan uses AI tokens
- Monitor in admin: Token Usage Logs
- Typical cost: $0.00-$0.02 per scan (with real API)
- Using stub client: $0.00

**Current Mode:**
- Using **stub client** (no real news)
- Returns mock/example data
- Perfect for testing the workflow
- Switch to real API for live news scanning

## Future Enhancements

Potential additions:
- Real-time market data integration
- Automated scanning (every 30 min during pre-market)
- Email/SMS alerts for HIGH activity stocks
- Integration with news APIs (NewsAPI, Benzinga, etc.)
- Historical scan results
- Pattern recognition (what types of news work best)

## Troubleshooting

**No results returned:**
- Stocks may not have recent news (normal!)
- Try different symbols
- Try AI suggestions instead

**Results seem outdated:**
- Remember: Stub client returns mock data
- Switch to real API for current news
- Add ANTHROPIC_API_KEY to .env

**Want real-time data:**
- Phase 2: Integrate market data API
- Phase 2: Web scraping of news sites
- Phase 2: MCP server for financial data

## Summary

The scanner transforms your workflow from:
❌ **Old:** Manually find stocks with news → Research each → Add to tracker

✅ **New:** Scanner finds stocks → Quick review → One-click add → Research only promising ones

**Result:** Spend less time searching, more time analyzing the best opportunities!
