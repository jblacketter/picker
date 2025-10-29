# Data Model Documentation

## Entity Relationship Diagram

```
┌─────────────────────────┐
│   ResearchSession       │
│─────────────────────────│
│ id (PK)                 │
│ title                   │
│ original_question       │
│ status                  │
│ created_at              │
│ updated_at              │
└───────┬─────────────────┘
        │
        │ 1:N
        │
        ├──────────┐
        │          │
        ▼          ▼
┌──────────────┐ ┌──────────────────┐
│Clarification │ │ ResearchResponse │
│   Question   │ │                  │
│──────────────│ │──────────────────│
│ id (PK)      │ │ id (PK)          │
│ session_id   │ │ session_id (FK)  │
│ question     │ │ summary          │
│ order        │ │ detailed_resp    │
└───┬──────────┘ │ links (JSON)     │
    │            │ token_count      │
    │ 1:N        └──────────────────┘
    │
    ▼
┌──────────────┐
│UserResponse  │
│──────────────│
│ id (PK)      │
│ clarif_id    │
│ response     │
└──────────────┘

┌─────────────────────────┐
│   ResearchNote          │
│─────────────────────────│
│ id (PK)                 │
│ session_id (FK)         │
│ note_text               │
│ created_at              │
└─────────────────────────┘

┌─────────────────────────┐
│   WatchlistItem         │
│─────────────────────────│
│ id (PK)                 │
│ symbol                  │
│ company_name            │
│ added_date              │
│ notes                   │
│ source_session_id (FK)  │
│ status                  │
└─────────────────────────┘

┌─────────────────────────┐
│   TokenUsageLog         │
│─────────────────────────│
│ id (PK)                 │
│ endpoint                │
│ tokens_used             │
│ cost_estimate           │
│ session_id (FK)         │
│ timestamp               │
└─────────────────────────┘
```

## Model Definitions

### ResearchSession

Represents a complete research conversation from question to response.

```python
class ResearchSession(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    original_question = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title
```

**Fields:**
- `title`: Auto-generated from original question (first 200 chars or summarized)
- `original_question`: The user's initial investment question
- `status`: Tracks completion state
- `created_at`: When research session started
- `updated_at`: Last modification time

**Relationships:**
- One-to-Many: ClarificationQuestions
- One-to-One: ResearchResponse
- One-to-Many: ResearchNotes
- One-to-Many: WatchlistItems (optional reference)

### ClarificationQuestion

AI-generated questions to gather context before providing advice.

```python
class ClarificationQuestion(models.Model):
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='clarifications')
    question_text = models.TextField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['session', 'order'], name='unique_clarification_order_per_session'),
        ]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."
```

**Fields:**
- `session`: Parent research session
- `question_text`: The clarifying question
- `order`: Display order (1, 2, 3...)

**Relationships:**
- Many-to-One: ResearchSession
- One-to-One: UserResponse (single answer per clarifying question)

### UserResponse

User's answers to clarification questions.

```python
class UserResponse(models.Model):
    clarification = models.OneToOneField(ClarificationQuestion, on_delete=models.CASCADE, related_name='user_response')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to: {self.clarification.question_text[:30]}..."
```

**Fields:**
- `clarification`: The question being answered
- `response_text`: User's answer
- `created_at`: When answer was first submitted
- `updated_at`: Last modification time (allows editing answers)

**Relationships:**
- One-to-One: ClarificationQuestion

### ResearchResponse

AI-generated advice and curated links.

```python
class ResearchResponse(models.Model):
    session = models.OneToOneField(ResearchSession, on_delete=models.CASCADE, related_name='response')
    summary = models.TextField()
    detailed_response = models.TextField()
    links = models.JSONField(default=list)
    token_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for: {self.session.title}"
```

**Fields:**
- `session`: Parent research session
- `summary`: Brief 2-3 sentence recommendation
- `detailed_response`: Full advice with considerations (Markdown format)
- `links`: Array of {title, url, description} objects
- `token_count`: Number of tokens used to generate this response

**Links JSON Structure:**
```json
[
    {
        "title": "Understanding Bond Allocation in Retirement Accounts",
        "url": "https://example.com/article",
        "description": "Comprehensive guide to bond allocation strategies"
    },
    ...
]
```

**Relationships:**
- One-to-One: ResearchSession

### ResearchNote

User-added notes and annotations on research sessions.

```python
class ResearchNote(models.Model):
    session = models.ForeignKey(ResearchSession, on_delete=models.CASCADE, related_name='notes')
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.session.title}: {self.note_text[:50]}..."
```

**Fields:**
- `session`: Research session this note belongs to
- `note_text`: User's personal notes
- `created_at`: When note was added

**Relationships:**
- Many-to-One: ResearchSession

### WatchlistItem

Stocks the user is tracking and researching.

```python
class WatchlistItem(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('researched', 'Researched'),
        ('dismissed', 'Dismissed'),
    ]

    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=200, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    source_session = models.ForeignKey(ResearchSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='watchlist_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watching')

    class Meta:
        ordering = ['-added_date']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.company_name}"
```

**Fields:**
- `symbol`: Stock ticker symbol (e.g., "AAPL")
- `company_name`: Full company name (can be fetched later)
- `added_date`: When added to watchlist
- `notes`: User's research notes on this stock
- `source_session`: Optional link to research session that mentioned this stock
- `status`: Tracking status

**Relationships:**
- Many-to-One: ResearchSession (optional)

### TokenUsageLog

Tracks AI API usage for cost monitoring.

```python
class TokenUsageLog(models.Model):
    ENDPOINT_CHOICES = [
        ('analyze', 'Question Analysis'),
        ('clarify', 'Clarification Generation'),
        ('respond', 'Response Generation'),
    ]

    endpoint = models.CharField(max_length=20, choices=ENDPOINT_CHOICES)
    model = models.CharField(max_length=50)  # e.g., 'claude-3-5-sonnet-20241022'
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    total_tokens = models.IntegerField()
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=6)
    session = models.ForeignKey(ResearchSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='token_logs')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['model']),
        ]

    def __str__(self):
        return f"{self.endpoint} ({self.model}): {self.total_tokens} tokens"
```

**Fields:**
- `endpoint`: Which AI operation was called
- `model`: Claude model used (Sonnet, Haiku, etc.)
- `prompt_tokens`: Input tokens consumed
- `completion_tokens`: Output tokens generated
- `total_tokens`: Sum of prompt + completion tokens
- `cost_estimate`: Estimated cost in USD
- `session`: Related research session (if applicable)
- `timestamp`: When the API call was made

**Relationships:**
- Many-to-One: ResearchSession (optional)

## Codex Review Notes - Incorporated

✅ **Extended TokenUsageLog** - Added `model`, `prompt_tokens`, `completion_tokens` fields for accurate cost tracking and reconciliation with Anthropic invoices.

✅ **UserResponse timestamps** - Added `created_at`/`updated_at` for edit auditability if users revise their answers.

✅ **Unique constraint on clarification order** - Prevents data integrity issues with question ordering.

**Note:** Endpoint naming uses short labels (`analyze`, `clarify`, `respond`) consistently across all docs and code for simplicity.

## Common Queries

### Get all research sessions with responses
```python
ResearchSession.objects.filter(status='completed').select_related('response')
```

### Get session with all related data
```python
session = ResearchSession.objects.prefetch_related(
    'clarifications__user_response',
    'notes',
    'token_logs'
).select_related('response').get(id=session_id)
```

### Get total tokens used today
```python
from django.utils import timezone
from django.db.models import Sum

today = timezone.now().date()
total = TokenUsageLog.objects.filter(
    timestamp__date=today
).aggregate(Sum('tokens_used'))['tokens_used__sum']
```

### Get watchlist with source sessions
```python
WatchlistItem.objects.filter(
    status='watching'
).select_related('source_session')
```

## Database Indexes

Critical indexes for performance:

1. `ResearchSession.created_at` - Descending (for recent sessions list)
2. `ResearchSession.status` - For filtering by status
3. `WatchlistItem.symbol` - For quick lookups
4. `TokenUsageLog.timestamp` - For usage analytics

## Migration Strategy

### Initial Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Future Schema Changes
1. Create migration: `python manage.py makemigrations`
2. Review SQL: `python manage.py sqlmigrate app_name migration_number`
3. Apply: `python manage.py migrate`
4. Test rollback: `python manage.py migrate app_name previous_migration`

## Data Seeding (Development)

Create a management command for test data:

```python
# research/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from research.models import ResearchSession, ResearchResponse

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Create sample research sessions
        session = ResearchSession.objects.create(
            title="Should I invest in bonds?",
            original_question="I'm 35 and wondering if I should move some of my 401k into bonds...",
            status='completed'
        )
        # Add clarifications, responses, etc.
```

Run: `python manage.py seed_data`

## Backup and Export

### SQLite Backup
```bash
# Backup
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# Restore
cp backups/db_20240115.sqlite3 db.sqlite3
```

### Export to JSON
```bash
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

## Phase 2 Models (Future)

### PreMarketMover
```python
class PreMarketMover(models.Model):
    symbol = models.CharField(max_length=10)
    news_headline = models.TextField()
    news_source = models.CharField(max_length=200)
    movement_percent = models.DecimalField(max_digits=6, decimal_places=2)
    strategy_notes = models.TextField(blank=True)
    executed = models.BooleanField(default=False)
    date = models.DateField()
```

### FallenAngel
```python
class FallenAngel(models.Model):
    symbol = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    historical_high = models.DecimalField(max_digits=10, decimal_places=2)
    high_date = models.DateField()
    drop_percent = models.DecimalField(max_digits=6, decimal_places=2)
    analysis_notes = models.TextField(blank=True)
```
