from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('', views.home, name='home'),
    path('ask/', views.ask_question, name='ask_question'),
    path('session/<int:session_id>/clarify/', views.clarifications, name='clarifications'),
    path('session/<int:session_id>/submit/', views.submit_clarifications, name='submit_clarifications'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/note/', views.add_note, name='add_note'),
    path('sessions/', views.session_list, name='session_list'),
]
