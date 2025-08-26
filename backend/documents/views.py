"""
Views for document operations.
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import os

from .models import Document, Tag, DocumentText
from .serializers import (
    DocumentListSerializer, DocumentDetailSerializer, DocumentUploadSerializer, TagSerializer
)
from .permissions import CanUploadDocuments, CanManageDocuments


class TagListCreateView(generics.ListCreateAPIView):
    """
    List all tags or create a new tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class DocumentListView(generics.ListAPIView):
    """
    List all documents with filtering and pagination.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'agency_office': ['exact', 'icontains'],
        'tags': ['exact'],
        'mime_type': ['exact'],
        'release_date': ['gte', 'lte'],
        'record_date_start': ['gte', 'lte'],
        'record_date_end': ['gte', 'lte'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['title', 'description', 'agency_office', 'request_id']
    ordering_fields = ['created_at', 'updated_at', 'title', 'release_date', 'file_size']
    ordering = ['-created_at']


class DocumentUploadView(generics.CreateAPIView):
    """
    Upload a new document.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentUploadSerializer
    permission_classes = [CanUploadDocuments]
    parser_classes = [MultiPartParser, FormParser]


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a document.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            permission_classes = [CanManageDocuments]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_document(request, slug):
    """
    Download a document file.
    """
    document = get_object_or_404(Document, slug=slug)
    
    if not document.file:
        raise Http404("File not found")
    
    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("File not found on disk")
    
    # Record download event
    try:
        from analytics.utils import record_download_event
        record_download_event(request, document)
    except ImportError:
        pass
    
    # Serve file
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=document.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
        response['Content-Length'] = document.file_size
        return response


@api_view(['POST'])
@permission_classes([CanManageDocuments])
def extract_text(request, slug):
    """
    Manually trigger text extraction for a document.
    """
    document = get_object_or_404(Document, slug=slug)
    
    try:
        # Try async extraction first
        from .tasks import extract_document_text
        task = extract_document_text.delay(document.id)
        return Response({
            'message': 'Text extraction started',
            'task_id': task.id
        })
    except ImportError:
        # Fallback to synchronous extraction
        from .utils import extract_text_from_document
        success = extract_text_from_document(document)
        
        if success:
            return Response({'message': 'Text extraction completed successfully'})
        else:
            return Response(
                {'error': 'Text extraction failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def document_stats(request):
    """
    Get document statistics.
    """
    from django.db.models import Count, Sum, Avg
    
    stats = Document.objects.aggregate(
        total_documents=Count('id'),
        total_size=Sum('file_size'),
        avg_size=Avg('file_size'),
        total_agencies=Count('agency_office', distinct=True),
        total_tags=Count('tags', distinct=True)
    )
    
    # Recent uploads (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_uploads = Document.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Popular file types
    file_types = Document.objects.values('mime_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'stats': stats,
        'recent_uploads': recent_uploads,
        'popular_file_types': file_types
    })
