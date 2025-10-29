# Picker - Investment Research Assistant

A personal AI-powered investment research tool that helps you navigate the overwhelming amount of investment information by starting with simple questions and building focused research sessions.

## What Makes This Different?

Unlike existing financial platforms, Picker is:
- **Question-driven:** Start with what you want to know, not what tools are available
- **Curated:** Get focused advice and links, not information overload
- **Personal:** Save your research, add notes, return when ready
- **AI-assisted:** Get clarifying questions and personalized responses

## Features (MVP)

✅ **Question-Based Research**
- Ask any investment question
- Receive clarifying questions to understand your context
- Get AI-generated advice with curated resource links
- Save complete research sessions

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
- Track costs
- Set usage limits

## Technology Stack

- **Backend:** Django 5.0+ (Python)
- **Frontend:** Django Templates + Tailwind CSS (MVP)
- **Database:** SQLite (development), PostgreSQL (production)
- **AI:** Anthropic Claude API
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

```powershell
# 1. Clone the repository (or navigate to project directory)
cd picker

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
copy .env.example .env
# Edit .env in notepad and add your ANTHROPIC_API_KEY

# 6. Run migrations
python manage.py migrate

# 7. Create superuser (for Django admin)
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver

# 9. Open browser
# Navigate to http://localhost:8000
```

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
├── docs/                   # Project documentation
│   ├── architecture.md     # System architecture
│   ├── mvp-plan.md        # Development roadmap
│   └── tech-decisions.md  # Technical decision log
├── picker/                # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── research/              # Research session app
│   ├── models.py
│   ├── views.py
│   └── templates/
├── stocks/                # Stock watchlist app
│   ├── models.py
│   ├── views.py
│   └── templates/
├── ai_service/           # AI integration layer
│   ├── claude_service.py
│   ├── prompt_templates.py
│   └── models.py
├── .claude/              # Claude Code configuration
│   ├── settings.json
│   ├── project-context.md
│   └── commands/         # Custom slash commands
├── .env                  # Environment variables (not in git)
├── .env.example         # Template for .env
├── requirements.txt     # Python dependencies
└── manage.py           # Django management script
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

```bash
# Delete SQLite database
rm db.sqlite3

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

### ✅ Phase 1 (MVP) - Current
- Core research flow
- Session management
- Basic watchlist
- Token tracking

### 🔄 Phase 2 - Planned
- Pre-market movers tracking
- Fallen angels analysis
- React frontend
- Advanced stock analysis tools

### 🔮 Phase 3 - Future
- MCP server integration
- Real-time market data
- Portfolio tracking
- Technical indicators
- Mobile app

## Documentation

- [Architecture Overview](docs/architecture.md) - System design and component structure
- [MVP Development Plan](docs/mvp-plan.md) - Phase-by-phase implementation roadmap
- [Technical Decisions](docs/tech-decisions.md) - Technology choices and rationale
- [Data Model](docs/data-model.md) - Database schema and relationships
- [Claude Client Interface](docs/claude-client-interface.md) - AI abstraction layer design
- [Implementation Workflow](docs/implementation-workflow.md) - Step-by-step development guide
- [Project Context](.claude/project-context.md) - Vision, goals, and principles

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

- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Built with [Django](https://www.djangoproject.com/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)
