from django.db import models
from django.utils import timezone


class ResearchSession(models.Model):
    """
    Represents a complete research conversation from question to response.
    """
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


class ClarificationQuestion(models.Model):
    """
    AI-generated questions to gather context before providing advice.
    """
    session = models.ForeignKey(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name='clarifications'
    )
    question_text = models.TextField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'order'],
                name='unique_clarification_order_per_session'
            ),
        ]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class UserResponse(models.Model):
    """
    User's answers to clarification questions.
    """
    clarification = models.OneToOneField(
        ClarificationQuestion,
        on_delete=models.CASCADE,
        related_name='user_response'
    )
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response to: {self.clarification.question_text[:30]}..."


class ResearchResponse(models.Model):
    """
    AI-generated advice and curated links.
    """
    session = models.OneToOneField(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name='response'
    )
    summary = models.TextField()
    detailed_response = models.TextField()
    links = models.JSONField(default=list)
    token_count = models.IntegerField(default=0)  # For backward compatibility
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for: {self.session.title}"


class ResearchNote(models.Model):
    """
    User-added notes and annotations on research sessions.
    """
    session = models.ForeignKey(
        ResearchSession,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.session.title}: {self.note_text[:50]}..."
