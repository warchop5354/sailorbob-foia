"""
URL patterns for documents app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Tags
    path('tags/', views.TagListCreateView.as_view(), name='tag-list'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    
    # Documents
    path('', views.DocumentListView.as_view(), name='document-list'),
    path('upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('stats/', views.document_stats, name='document-stats'),
    path('<slug:slug>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('<slug:slug>/download/', views.download_document, name='document-download'),
    path('<slug:slug>/extract-text/', views.extract_text, name='document-extract-text'),
]