"""
URL patterns for analytics app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.analytics_summary, name='analytics-summary'),
    path('daily/', views.daily_stats, name='analytics-daily'),
    path('popular/', views.popular_content, name='analytics-popular'),
    path('users/', views.user_activity, name='analytics-users'),
]