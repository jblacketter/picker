# Picker - Investment Research Assistant

A personal AI-powered investment research tool that helps you navigate the overwhelming amount of investment information by starting with simple questions and building focused research sessions.

## What Makes This Different?

Unlike existing financial platforms, Picker is:
- **Question-driven:** Start with what you want to know, not what tools are available
- **Curated:** Get focused advice and links, not information overload
- **Personal:** Save your research, add notes, return when ready
- **AI-assisted:** Get clarifying questions and personalized responses

## Features

✅ **Question-Based Research**
- Ask any investment question
- Receive clarifying questions to understand your context
- Get AI-generated advice with curated resource links
- Save complete research sessions

✅ **Pre-Market Movers Scanner**
- Real-time stock price and volume data (via yfinance)
- Scan symbols to find biggest movers
- One-click tracking from scan results
- AI-powered news research for drill-down analysis
- Status workflow: identified → researching → ready → executed

✅ **Research Session Management**
- View all saved sessions
- Add personal notes and annotations
- Search and filter past research

✅ **Stock Watchlist**
- Save stocks you're researching
- Add notes and track your analysis
- Link stocks to research sessions

✅ **Token Usage Tracking**
- Monitor AI API usage
- Track costs per endpoint
- Cost estimation with current Claude pricing

## Technology Stack

- **Backend:** Django 5.0+ (Python)
- **Frontend:** Django Templates + Tailwind CSS (MVP)
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **AI:** Anthropic Claude API (Haiku for clarifications, Sonnet for responses)
- **Market Data:** yfinance (Yahoo Finance API wrapper)
- **Deployment:** Local-first (development server)

## Quick Start

### Prerequisites

- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- Anthropic API key ([Get one](https://console.anthropic.com/))

### macOS Setup

```bash
# 1. Clone the repository (or navigate to project directory)
cd picker

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 6. Run migrations
python manage.py migrate

# 7. Create superuser (for Django admin)
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver

# 9. Open browser
# Navigate to http://localhost:8000
```

### Windows Setup

**Using PowerShell (Recommended):**

```powershell
# 1. Clone the repository
git clone https://github.com/jblacketter/picker.git
cd picker

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
copy .env.example .env
notepad .env
# Add your ANTHROPIC_API_KEY and save

# 6. Run database migrations
python manage.py migrate

# 7. Create superuser (for Django admin access)
python manage.py createsuperuser
# Username: admin
# Email: (your email)
# Password: (choose a password)

# 8. Start development server
python manage.py runserver

# 9. Open browser to http://localhost:8000
```

**Using Command Prompt (Alternative):**

```cmd
# 1. Clone and navigate
git clone https://github.com/jblacketter/picker.git
cd picker

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
copy .env.example .env
notepad .env

# 6-9. Same as PowerShell steps above
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Windows Notes:**
- If `python` doesn't work, try `py` or `python3`
- Make sure Python is added to your PATH during installation
- Administrator privileges may be required for some operations
- Use forward slashes (`/`) or escaped backslashes (`\\`) in file paths within Python code

### Linux/Ubuntu Setup

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git

# 3. Clone repository
git clone https://github.com/jblacketter/picker.git
cd picker

# 4. Create virtual environment
python3.11 -m venv .venv

# 5. Activate virtual environment
source .venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Set up environment variables
cp .env.example .env
nano .env
# Add your ANTHROPIC_API_KEY and save (Ctrl+X, Y, Enter)

# 8. Run migrations
python manage.py migrate

# 9. Create superuser
python manage.py createsuperuser

# 10. Run development server
python manage.py runserver

# 11. Open browser to http://localhost:8000
```

**Linux Notes:**
- For production deployment, see [Linux Production Deployment Guide](docs/linux-production-deployment.md)
- Use `python3` or `python3.11` depending on your system
- Virtual environment activation: `source .venv/bin/activate`
- To deactivate: `deactivate`

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Django settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Optional - Database (uses SQLite by default)
# DATABASE_URL=postgresql://user:password@localhost:5432/picker
```

## Project Structure

```
picker/
├── docs/                      # Project documentation
│   ├── architecture.md        # System architecture
│   ├── mvp-plan.md           # Development roadmap
│   ├── tech-decisions.md     # Technical decision log
│   ├── pre-market-movers-guide.md  # Pre-market movers user guide
│   └── scanner-feature.md    # Scanner feature documentation
├── config/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── research/                 # Research session app
│   ├── models.py
│   ├── views.py
│   └── templates/
├── stocks/                   # Stock watchlist app
│   ├── models.py
│   ├── views.py
│   └── templates/
├── strategies/               # Trading strategies app
│   ├── models.py            # PreMarketMover model
│   ├── views.py             # Scanner and research views
│   ├── stock_data.py        # yfinance integration
│   └── templates/
├── ai_service/              # AI integration layer
│   ├── client_interface.py  # Abstract base class
│   ├── live_client.py       # Production Claude API client
│   ├── stub_client.py       # Development mock client
│   ├── client_factory.py    # Factory pattern for client selection
│   ├── utils.py             # Token cost calculation
│   └── models.py            # TokenUsageLog
├── .claude/                 # Claude Code configuration
│   ├── settings.json
│   ├── project-context.md
│   └── commands/            # Custom slash commands
├── templates/               # Shared templates
│   └── base.html           # Base template with navigation
├── .env                     # Environment variables (not in git)
├── .env.example            # Template for .env
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## Development Workflow

### Running the App

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run development server
python manage.py runserver

# Access the app
# http://localhost:8000
```

### Database Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration SQL (optional)
python manage.py sqlmigrate research 0001
```

### Django Admin

Access the admin panel at `http://localhost:8000/admin`

```bash
# Create superuser if you haven't already
python manage.py createsuperuser
```

### Django Shell

```bash
# Interactive Python shell with Django context
python manage.py shell

# Example: Test AI service
>>> from ai_service.claude_service import analyze_question
>>> result = analyze_question("Should I invest in bonds?")
>>> print(result)
```

### Running Tests (Phase 2)

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test research

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Common Tasks

### Add a New Django App

```bash
python manage.py startapp app_name
```

Then add to `INSTALLED_APPS` in `settings.py`

### Clear Database (Start Fresh)

**macOS/Linux:**
```bash
# Delete SQLite database
rm db.sqlite3

# Run migrations again
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Windows:**
```powershell
# Delete SQLite database
del db.sqlite3

# Run migrations again
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Update Dependencies

```bash
# After adding new packages
pip freeze > requirements.txt

# Update existing packages
pip install --upgrade -r requirements.txt
```

## Usage Guide

### 1. Ask a Question

Navigate to the home page and enter your investment question:
- "Should I move some of my 401k into bonds?"
- "What AI stocks should I consider for growth?"
- "Is now a good time to increase international exposure?"

### 2. Answer Clarifications

The AI will ask 2-3 clarifying questions to understand your context:
- Risk tolerance
- Investment timeline
- Current allocation
- Specific concerns

### 3. Review Research

Get a personalized response including:
- Summary recommendation
- Key considerations
- Curated links for further reading

### 4. Save and Annotate

- Research session is automatically saved
- Add your own notes and thoughts
- Return anytime to continue research

### 5. Build Your Watchlist

- Save interesting stock symbols
- Add analysis notes
- Link to related research sessions

### 6. Use Pre-Market Movers Scanner

**Access:** Navigate to **Tools → Pre-Market Movers**

**Workflow:**
1. **Scan for movers:**
   - Enter stock symbols (e.g., `AAPL, TSLA, NVDA, AMD, META`)
   - Click "Scan for Movers"
   - View real-time price, % change, and volume data

2. **Track interesting stocks:**
   - Click "+ Track" on stocks with significant movement
   - Stocks are added to your tracking list

3. **Research the catalyst:**
   - Click "Research This" on tracked stocks
   - AI analyzes recent news and provides trading insights
   - Get sentiment (bullish/bearish/neutral) and key factors

4. **Manage workflow:**
   - Track status: Identified → Researching → Ready to Trade → Executed
   - Add notes, entry/exit prices, and P/L tracking

**See:** [Pre-Market Movers Guide](docs/pre-market-movers-guide.md) for detailed instructions

## Troubleshooting

### Virtual Environment Issues

**Problem:** `command not found: python`
**Solution:** Use `python3` instead of `python` on macOS/Linux

**Problem:** Virtual environment not activating
**Solution:** Make sure you're in the project directory and the path is correct

### Database Issues

**Problem:** `no such table` errors
**Solution:** Run migrations: `python manage.py migrate`

**Problem:** Database is locked
**Solution:** Close other connections, or delete `db.sqlite3` and re-migrate

### API Issues

**Problem:** `Invalid API key`
**Solution:** Check your `.env` file has the correct `ANTHROPIC_API_KEY`

**Problem:** Rate limit exceeded
**Solution:** Check token usage in admin panel, wait before retrying

### Windows-Specific Issues

**Problem:** `'python' is not recognized`
**Solution:** Make sure Python is in your PATH, or use full path to python.exe

**Problem:** Virtual environment activation fails
**Solution:** Try `venv\Scripts\activate.bat` instead

## Development Roadmap

### ✅ Phase 1 (MVP) - Completed
- Core research flow with AI clarifications
- Research session management
- Stock watchlist
- Token usage tracking
- Pre-market movers scanner with real-time data
- AI-powered news research drill-down

### 🔄 Phase 2 - In Progress
- Enhanced market data visualization
- Fallen angels analysis
- Pattern recognition for news types
- Automated scanning features

### 🔮 Phase 3 - Future
- React frontend migration
- MCP server integration for financial data
- Real-time WebSocket market data
- Portfolio tracking
- Technical indicators and charting
- Mobile app
- Email/SMS alerts for significant movers

## Documentation

### Core Documentation
- [Architecture Overview](docs/architecture.md) - System design and component structure
- [MVP Development Plan](docs/mvp-plan.md) - Phase-by-phase implementation roadmap
- [Technical Decisions](docs/tech-decisions.md) - Technology choices and rationale
- [Data Model](docs/data-model.md) - Database schema and relationships
- [Implementation Workflow](docs/implementation-workflow.md) - Step-by-step development guide
- [Project Context](.claude/project-context.md) - Vision, goals, and principles

### Feature Documentation
- [Pre-Market Movers Guide](docs/pre-market-movers-guide.md) - Complete user guide for pre-market scanner
- [Scanner Feature](docs/scanner-feature.md) - Technical details of the scanner implementation
- [Claude Client Interface](docs/claude-client-interface.md) - AI abstraction layer design

### Deployment & Security
- 🔒 [Security Checklist](docs/security-checklist.md) - **READ BEFORE PRODUCTION** - Critical security requirements
- 🐧 [Linux Production Deployment (Nginx)](docs/linux-production-deployment.md) - Complete production setup guide for Ubuntu/Linux with Nginx
- 🌐 [Apache Production Deployment](docs/apache-production-deployment.md) - Production setup guide for Apache web server
- 📋 `.env.production.example` - Production environment configuration template

## Contributing

This is a personal project, but if you're interested in the approach:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for personal use. See LICENSE file for details.

## Support

For issues or questions:
- Check the [docs/](docs/) directory
- Review [tech-decisions.md](docs/tech-decisions.md)
- Open an issue on GitHub

## Disclaimer

⚠️ **Important:** This app provides educational research assistance only. It is NOT financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

## Acknowledgments

- AI powered by [Anthropic Claude](https://www.anthropic.com/)
- Built with [Django](https://www.djangoproject.com/)
- Market data via [yfinance](https://github.com/ranaroussi/yfinance)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
