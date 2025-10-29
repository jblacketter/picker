from django.db import models


class TokenUsageLog(models.Model):
    """
    Tracks AI API usage for cost monitoring.
    """
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
    session = models.ForeignKey(
        'research.ResearchSession',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='token_logs'
    )
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
