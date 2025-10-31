from django.urls import path
from . import views

app_name = 'strategies'

urlpatterns = [
    path('pre-market-movers/', views.pre_market_movers, name='pre_market_movers'),
    path('pre-market-movers/add-form/', views.add_mover_form_page, name='add_mover_form_page'),
    path('pre-market-movers/add/', views.add_mover, name='add_mover'),
    path('pre-market-movers/scan/', views.scan_movers, name='scan_movers'),
    path('pre-market-movers/quick-add/', views.quick_add_mover, name='quick_add_mover'),
    path('pre-market-movers/<int:mover_id>/research/', views.research_mover, name='research_mover'),
    path('pre-market-movers/<int:mover_id>/delete/', views.delete_mover, name='delete_mover'),
    path('pre-market-movers/delete-all/', views.delete_all_movers, name='delete_all_movers'),
    path('pre-market-movers/toggle-api/', views.toggle_api, name='toggle_api'),
    path('api-usage/', views.api_usage, name='api_usage'),
    # Wave 2 Feature 2.1: Market Context API
    path('market-context/', views.market_context_api, name='market_context_api'),
]
