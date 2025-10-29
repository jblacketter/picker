from django.db import models


class WatchlistItem(models.Model):
    """
    Stocks the user is tracking and researching.
    """
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('researched', 'Researched'),
        ('dismissed', 'Dismissed'),
    ]

    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=200, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    source_session = models.ForeignKey(
        'research.ResearchSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='watchlist_items'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watching')

    class Meta:
        ordering = ['-added_date']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.company_name}" if self.company_name else self.symbol
