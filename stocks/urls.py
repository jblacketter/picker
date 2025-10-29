from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('', views.watchlist, name='watchlist'),
    path('add/', views.add_to_watchlist, name='add_to_watchlist'),
]
