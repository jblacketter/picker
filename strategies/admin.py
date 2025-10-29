from django.contrib import admin
from .models import PreMarketMover


@admin.register(PreMarketMover)
class PreMarketMoverAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company_name', 'movement_percent', 'status', 'trade_date', 'profit_loss')
    list_filter = ('status', 'trade_date', 'sentiment')
    search_fields = ('symbol', 'company_name', 'news_headline')
    readonly_fields = ('identified_date', 'profit_loss')
    date_hierarchy = 'trade_date'

    fieldsets = (
        ('Stock Info', {
            'fields': ('symbol', 'company_name', 'status')
        }),
        ('News & Movement', {
            'fields': ('news_headline', 'news_source', 'news_url', 'movement_percent', 'pre_market_price')
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis', 'sentiment'),
            'classes': ('collapse',)
        }),
        ('Trading', {
            'fields': ('entry_price', 'exit_price', 'profit_loss', 'trade_date', 'executed_at')
        }),
        ('Notes', {
            'fields': ('strategy_notes',)
        }),
        ('Metadata', {
            'fields': ('identified_date',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-calculate profit/loss if both prices exist
        if obj.entry_price and obj.exit_price:
            obj.calculate_profit_loss()
        super().save_model(request, obj, form, change)
