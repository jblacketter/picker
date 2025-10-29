from django.db import models
from django.utils import timezone


class PreMarketMover(models.Model):
    """
    Tracks stocks with significant pre-market or after-hours activity.
    Strategy: Buy at market open, sell on upward momentum.
    """
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('researching', 'Researching'),
        ('ready', 'Ready to Trade'),
        ('executed', 'Executed'),
        ('passed', 'Passed'),
    ]

    symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=200, blank=True)
    
    # News and Movement Info
    news_headline = models.TextField()
    news_source = models.CharField(max_length=200, blank=True)
    news_url = models.URLField(blank=True)
    movement_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pre_market_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # AI Analysis
    ai_analysis = models.TextField(blank=True, help_text="AI-generated analysis of the opportunity")
    sentiment = models.CharField(max_length=20, blank=True, help_text="bullish, bearish, neutral")
    
    # Strategy Notes
    strategy_notes = models.TextField(blank=True)
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    identified_date = models.DateTimeField(auto_now_add=True)
    trade_date = models.DateField(default=timezone.now)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-identified_date']
        indexes = [
            models.Index(fields=['-identified_date']),
            models.Index(fields=['status']),
            models.Index(fields=['trade_date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.trade_date} ({self.get_status_display()})"

    def calculate_profit_loss(self):
        """Calculate profit/loss if both entry and exit prices exist"""
        if self.entry_price and self.exit_price:
            self.profit_loss = self.exit_price - self.entry_price
            self.save()
        return self.profit_loss
