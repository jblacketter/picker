from django.urls import path
from . import views

app_name = 'strategies'

urlpatterns = [
    path('pre-market-movers/', views.pre_market_movers, name='pre_market_movers'),
    path('pre-market-movers/add/', views.add_mover, name='add_mover'),
    path('pre-market-movers/scan/', views.scan_movers, name='scan_movers'),
    path('pre-market-movers/quick-add/', views.quick_add_mover, name='quick_add_mover'),
    path('pre-market-movers/<int:mover_id>/research/', views.research_mover, name='research_mover'),
]
