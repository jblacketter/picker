from django.contrib import admin
from .models import WatchlistItem


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company_name', 'status', 'added_date')
    list_filter = ('status', 'added_date')
    search_fields = ('symbol', 'company_name', 'notes')
    readonly_fields = ('added_date',)

    fieldsets = (
        ('Stock Info', {
            'fields': ('symbol', 'company_name', 'status')
        }),
        ('Research', {
            'fields': ('notes', 'source_session')
        }),
        ('Metadata', {
            'fields': ('added_date',),
            'classes': ('collapse',)
        }),
    )
