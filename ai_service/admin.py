from django.contrib import admin
from .models import TokenUsageLog
from django.db.models import Sum
from django.utils.html import format_html


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'endpoint',
        'model',
        'total_tokens',
        'cost_display',
        'session_link'
    )
    list_filter = ('endpoint', 'model', 'timestamp')
    search_fields = ('session__title',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('API Call', {
            'fields': ('endpoint', 'model', 'session')
        }),
        ('Token Usage', {
            'fields': ('prompt_tokens', 'completion_tokens', 'total_tokens', 'cost_estimate')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

    def cost_display(self, obj):
        return f"${obj.cost_estimate:.4f}"
    cost_display.short_description = 'Cost'

    def session_link(self, obj):
        if obj.session:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:research_researchsession_change', args=[obj.session.id])
            return format_html('<a href="{}">{}</a>', url, obj.session.title)
        return '-'
    session_link.short_description = 'Session'

    def changelist_view(self, request, extra_context=None):
        # Add summary statistics
        response = super().changelist_view(request, extra_context)

        try:
            qs = response.context_data['cl'].queryset
            summary = qs.aggregate(
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('cost_estimate')
            )

            response.context_data['summary'] = summary
        except (AttributeError, KeyError):
            pass

        return response
