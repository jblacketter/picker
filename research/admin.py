from django.contrib import admin
from .models import (
    ResearchSession,
    ClarificationQuestion,
    UserResponse,
    ResearchResponse,
    ResearchNote
)


class ClarificationInline(admin.TabularInline):
    model = ClarificationQuestion
    extra = 0
    fields = ('order', 'question_text')


class UserResponseInline(admin.TabularInline):
    model = UserResponse
    extra = 0
    fields = ('response_text', 'created_at')
    readonly_fields = ('created_at',)


class ResearchNoteInline(admin.TabularInline):
    model = ResearchNote
    extra = 1
    fields = ('note_text', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ResearchSession)
class ResearchSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'original_question')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClarificationInline, ResearchNoteInline]

    fieldsets = (
        ('Question', {
            'fields': ('title', 'original_question', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResearchResponse)
class ResearchResponseAdmin(admin.ModelAdmin):
    list_display = ('session', 'token_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session__title', 'summary')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Session', {
            'fields': ('session',)
        }),
        ('Response', {
            'fields': ('summary', 'detailed_response', 'links')
        }),
        ('Metadata', {
            'fields': ('token_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
