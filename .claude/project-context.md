# Investment Research Assistant - Project Context

## Project Purpose
A personal investment research assistant designed to help navigate the overwhelming amount of investment information available. The app focuses on **question-driven exploration** rather than trying to compete with existing financial platforms.

## Target User
- Primary user: Developer/owner learning about investing
- Uses Fidelity retirement account
- Overwhelmed by the massive amount of tools, links, and resources
- Wants focused, curated research experiences starting from simple questions

## Core Value Proposition
**What makes this unique:** Starts from simple questions, prompts for clarifications, then provides focused answers with curated links. Saves research progress so users can return later and continue where they left off.

This is NOT trying to replace Bloomberg, TradingView, or brokerage research tools. It's a **personal research organizer** that helps trim the noise.

## Key Features (MVP and Beyond)

### 1. Question-Based Exploration
- User asks investment question (e.g., "Should I move 401k into bonds?")
- App asks clarifying questions
- Provides AI-generated advice with relevant links
- Saves question/research session for later access
- Can return to research in progress

### 2. Stock Research Workflow
**Part A: General Exploration**
- Ask broad questions: "What AI stocks should I look at for growth?"
- Answer clarifying questions
- Get summary with links to stocks, news, research

**Part B: Deep Dive on Specific Stocks**
- Save stock symbols to watchlist/research view
- Evaluation tools (Bollinger Bands, fundamental analysis, etc.)
- Save important findings with personal notes
- Return to research later

### 3. Pre-Market Movers Strategy (Separate Tab/Page)
- Track stocks with news before market opens
- Strategy: Buy at open, sell on upward swing
- Monitor free market movers

### 4. Fallen Angels Analysis
- Analyze stocks that were high-value in the past
- Now trading under $5/share
- Identify potential recovery plays

## Technical Approach

### Technology Stack
- **Backend:** Django (Python)
- **Frontend:** React (or Django templates initially, then React if needed)
- **Database:** SQLite for dev, PostgreSQL for production
- **AI Integration:** Anthropic Claude API via MCP server where appropriate
- **Cross-Platform:** Mac (primary dev), Windows (must support)

### AI Strategy - Token Cost Management
**CRITICAL:** Token usage must be monitored and limited
- User has small amounts of Anthropic and Codex tokens purchased
- Primary development uses Anthropic Pro account
- Need cost controls before production
- Implement token usage tracking
- Consider caching responses where appropriate
- Limit AI calls to essential research steps

### Development Environment
- Python virtual environment (venv)
- requirements.txt for dependencies
- Cross-platform setup (Mac + Windows)
- Good README with setup instructions for both platforms

### Future Considerations
- MCP server integration for financial data
- Potential agent-based workflows
- Real-time market data integration
- Portfolio tracking integration with Fidelity

## Architecture Decisions

### Why Django?
- Project may become complex over time
- Django admin for data management
- Built-in ORM for research session storage
- Good authentication if needed later
- REST framework available if we build API

### Why React (potential)?
- Better UX for interactive research flows
- Component reusability
- State management for research sessions
- Can start with Django templates and migrate later

## Design Principles
1. **Question-first:** Always start with user's question
2. **Clarify before answering:** Get context before providing advice
3. **Curate, don't overwhelm:** Provide focused links, not everything
4. **Save everything:** Research sessions are valuable, must persist
5. **Cost-conscious:** Monitor and limit AI token usage
6. **Iterative:** Build MVP, then enhance

## Domain Context
- Investment research and decision-making
- Retirement account management (401k focus)
- Stock analysis and evaluation
- Trading strategies (pre-market movers, value plays)
- Technical analysis (Bollinger Bands, etc.)
- Fundamental analysis

## Non-Goals
- NOT a trading platform
- NOT trying to replace professional tools
- NOT providing financial advice (user researches, makes own decisions)
- NOT real-time trading execution
