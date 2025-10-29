# Automated Morning Scanner - Setup Guide

The automated scanner runs every morning to identify pre-market movers, fetch news, and populate your dashboard automatically.

---

## ✅ What's Installed

**Files Created:**
- `strategies/management/commands/scan_premarket_movers.py` - Scanner command
- `strategies/watchlists.py` - Configurable symbol lists
- `docs/AUTOMATED_SCANNER_SETUP.md` - This guide

**What It Does:**
1. Scans your watchlist at 8:00 AM ET (pre-market hours)
2. Finds stocks with >5% movement
3. Auto-fetches news from Finnhub
4. Creates PreMarketMover records with status='identified'
5. Prevents duplicates (won't re-track same stock twice in one day)

---

## 🧪 Manual Testing (Do This First!)

Before setting up automation, test the scanner manually:

```bash
# Basic test (dry-run mode)
python manage.py scan_premarket_movers --dry-run

# Run for real with lower threshold
python manage.py scan_premarket_movers --threshold 2.0

# Test with different watchlists
python manage.py scan_premarket_movers --watchlist aggressive
python manage.py scan_premarket_movers --watchlist conservative

# Fast test (skip news fetching)
python manage.py scan_premarket_movers --skip-news

# See all options
python manage.py scan_premarket_movers --help
```

**Expected Output:**
```
============================================================
PRE-MARKET MOVERS SCANNER
============================================================
Watchlist: default
Symbols: 26 (AAPL, MSFT, GOOGL, AMZN, META, TSLA...)
Threshold: ±5.0%
Limit: 20 movers

Fetching market data...
Found 26 stocks, 3 meet threshold

📊 NVDA (NVIDIA Corporation)
   Price: $206.54  Change: +2.74%
   Fetching news from Finnhub...
   📰 Nvidia Just Became the First $5 Trillion Company...
   ✅ Tracked (ID: 7)

...

============================================================
SUMMARY
============================================================
Scanned: 26 symbols
Moving ±5.0%: 3 stocks
Created: 3 new movers
Skipped: 0 (already tracked today)

✅ Done! Check dashboard at /strategies/pre-market-movers/
```

---

## ⏰ Setting Up Automation

### Option 1: Cron (Linux/macOS)

**1. Open your crontab:**
```bash
crontab -e
```

**2. Add this line to run at 8:00 AM ET every weekday:**
```bash
# Pre-Market Movers Scanner (8:00 AM ET = 1:00 PM UTC)
# Adjust for your timezone!
0 13 * * 1-5 cd /Users/jackblacketter/projects/picker && /Users/jackblacketter/projects/picker/.venv/bin/python manage.py scan_premarket_movers --threshold 5.0 >> /Users/jackblacketter/projects/picker/logs/scanner.log 2>&1
```

**Important Timezone Notes:**
- Cron uses your server's timezone (usually UTC)
- If server is UTC and you want 8:00 AM ET:
  - EST (winter): 8 AM ET = 1:00 PM UTC → `0 13`
  - EDT (summer): 8 AM ET = 12:00 PM UTC → `0 12`
- Check your timezone: `date`
- Use https://crontab.guru to verify schedule

**3. Verify cron is scheduled:**
```bash
crontab -l
```

**4. Check logs:**
```bash
tail -f /Users/jackblacketter/projects/picker/logs/scanner.log
```

---

### Option 2: macOS LaunchAgent

For better macOS integration, create a LaunchAgent:

**1. Create plist file:**
```bash
nano ~/Library/LaunchAgents/com.picker.scanner.plist
```

**2. Paste this configuration:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.picker.scanner</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/jackblacketter/projects/picker/.venv/bin/python</string>
        <string>/Users/jackblacketter/projects/picker/manage.py</string>
        <string>scan_premarket_movers</string>
        <string>--threshold</string>
        <string>5.0</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/jackblacketter/projects/picker</string>

    <key>StandardOutPath</key>
    <string>/Users/jackblacketter/projects/picker/logs/scanner.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/jackblacketter/projects/picker/logs/scanner_error.log</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>1</integer>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>2</integer>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>3</integer>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>4</integer>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>5</integer>
    </dict>
</dict>
</plist>
```

**3. Load the LaunchAgent:**
```bash
launchctl load ~/Library/LaunchAgents/com.picker.scanner.plist
```

**4. Verify it's loaded:**
```bash
launchctl list | grep picker
```

**5. Test it now (don't wait for 8 AM):**
```bash
launchctl start com.picker.scanner
```

**6. Check logs:**
```bash
tail -f /Users/jackblacketter/projects/picker/logs/scanner.log
```

**To disable:**
```bash
launchctl unload ~/Library/LaunchAgents/com.picker.scanner.plist
```

---

### Option 3: Windows Task Scheduler

**1. Open Task Scheduler**

**2. Create Basic Task:**
- Name: "Picker Pre-Market Scanner"
- Description: "Scan for pre-market movers every weekday at 8 AM"

**3. Trigger:**
- Daily, start at 8:00 AM
- Recur every 1 day
- Advanced: Repeat task every 1 week on Monday, Tuesday, Wednesday, Thursday, Friday

**4. Action - Start a program:**
```
Program: C:\path\to\picker\.venv\Scripts\python.exe
Arguments: manage.py scan_premarket_movers --threshold 5.0
Start in: C:\path\to\picker
```

**5. Conditions:**
- ✅ Start only if computer is on AC power (uncheck if laptop)
- ✅ Wake computer to run this task (optional)

---

## 🛠️ Customization

### Change the Watchlist

Edit `strategies/watchlists.py`:

```python
DEFAULT_WATCHLIST = [
    'AAPL', 'TSLA', 'NVDA',  # Add your symbols here
    # ...
]
```

Or create a custom list:
```python
MY_WATCHLIST = ['AAPL', 'GOOGL', 'MSFT']
```

Then use it:
```bash
python manage.py scan_premarket_movers --watchlist my
```

### Change the Threshold

Lower threshold = more movers found:
```bash
--threshold 3.0   # Catches stocks moving ±3% or more
--threshold 2.0   # More aggressive
--threshold 7.0   # More conservative
```

### Combine Multiple Watchlists

In Python:
```python
from strategies.watchlists import combine_watchlists

symbols = combine_watchlists('default', 'aggressive')
```

---

## 📧 Optional: Email Notifications

To get email summary when scanner runs:

**1. Install django-mail:**
```bash
pip install django-anymail
```

**2. Configure email in `config/settings.py`:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Picker Scanner <your-email@gmail.com>'
```

**3. Modify command to send email:**
```python
# In scan_premarket_movers.py, add at the end:
from django.core.mail import send_mail

send_mail(
    subject=f'Pre-Market Scanner: {created_count} movers found',
    message=f'Created {created_count} new movers. Check dashboard.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@gmail.com'],
)
```

---

## 🐛 Troubleshooting

### Scanner Not Running
```bash
# Check if cron is running
ps aux | grep cron

# Check cron logs
tail -f /var/log/syslog | grep CRON  # Linux
tail -f /var/log/system.log | grep cron  # macOS

# Test manually
python manage.py scan_premarket_movers
```

### No Movers Found
- Market might be closed or low volatility
- Try lowering threshold: `--threshold 2.0`
- Check if watchlist symbols are valid
- Run during market hours for better data

### Duplicate Records
- Scanner automatically prevents duplicates per day
- If you see duplicates, check `identified_date` field
- Clear old records: Delete movers older than X days

### News Not Fetching
- Check Finnhub API key in `.env`
- Verify API limits not exceeded
- Use `--skip-news` to bypass temporarily

---

## 📊 Monitoring & Logs

### View Scanner History
```bash
# Recent scanner runs
tail -50 logs/scanner.log

# Live monitoring
tail -f logs/scanner.log

# Search for errors
grep -i error logs/scanner.log
```

### Dashboard Check
After scanner runs, check:
http://localhost:8000/strategies/pre-market-movers/?status=identified

### Database Query
```python
# Django shell
python manage.py shell

from strategies.models import PreMarketMover
from datetime import date

# Movers from today
today_movers = PreMarketMover.objects.filter(identified_date__date=date.today())
print(f"Found {today_movers.count()} movers today")
```

---

## 🎯 Recommended Schedule

**Pre-Market Trading Hours:** 4:00 AM - 9:30 AM ET

**Suggested Scanner Times:**
- **8:00 AM ET** - Primary scan (1 hour before market open)
- **7:00 AM ET** - Earlier scan for very early news
- **6:00 AM ET** - Catch overnight developments

**Multiple scans per day:**
```bash
# In crontab (times in UTC)
0 11 * * 1-5  # 6:00 AM ET scan
0 12 * * 1-5  # 7:00 AM ET scan
0 13 * * 1-5  # 8:00 AM ET scan (main)
```

Scanner automatically prevents duplicates, so multiple scans are safe!

---

## ✅ Success Checklist

- [ ] Tested scanner manually with `--dry-run`
- [ ] Tested scanner for real, saw record created
- [ ] Verified duplicate detection works
- [ ] Set up cron/LaunchAgent/Task Scheduler
- [ ] Verified automation runs (check logs tomorrow)
- [ ] Customized watchlist to your preferences
- [ ] Adjusted threshold to your risk tolerance
- [ ] Dashboard shows movers automatically

---

## 🚀 Next Steps

Once the scanner is running smoothly:

1. **Fine-tune watchlist** - Add/remove symbols based on what's relevant
2. **Adjust threshold** - Find sweet spot between too many/too few movers
3. **Add email notifications** - Get alerts even if not logged in
4. **Build Priority 2** - Enhanced AI analysis with entry/exit targets
5. **Track performance** - Which movers led to profitable trades?

---

**You're all set! Tomorrow morning, wake up to a populated dashboard ready for research.**

Questions? Check the logs or run `python manage.py scan_premarket_movers --help`
