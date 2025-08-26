"""
URL patterns for search app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='search'),
    path('facets/', views.facets_view, name='search-facets'),
    path('suggestions/', views.search_suggestions, name='search-suggestions'),
    path('reindex/', views.reindex_view, name='search-reindex'),
    path('stats/', views.search_stats, name='search-stats'),
]