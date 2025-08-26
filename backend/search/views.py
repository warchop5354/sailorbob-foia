"""
Search views and API endpoints.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.core.cache import cache
from .utils import search_documents, get_facets, reindex_all_documents
from documents.permissions import CanAccessAdminFeatures


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_view(request):
    """
    Search documents with query, filters, and facets.
    
    Query parameters:
    - q: Search query string
    - agency_office: Filter by agency/office
    - tags: Filter by tags (comma-separated)
    - mime_type: Filter by file type
    - release_date_from: Filter by release date (YYYY-MM-DD)
    - release_date_to: Filter by release date (YYYY-MM-DD)
    - record_date_from: Filter by record date (YYYY-MM-DD)
    - record_date_to: Filter by record date (YYYY-MM-DD)
    - sort: Sort field and direction (e.g., 'created_at:desc')
    - limit: Number of results per page (default: 20, max: 100)
    - offset: Offset for pagination (default: 0)
    - facets: Include facets in response (true/false)
    """
    
    # Get query parameters
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 20)), 100)
    offset = int(request.GET.get('offset', 0))
    include_facets = request.GET.get('facets', 'false').lower() == 'true'
    
    # Build filters
    filters = {}
    
    # Agency office filter
    agency_office = request.GET.get('agency_office')
    if agency_office:
        filters['agency_office'] = agency_office
    
    # Tags filter
    tags = request.GET.get('tags')
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if tag_list:
            filters['tags'] = tag_list
    
    # MIME type filter
    mime_type = request.GET.get('mime_type')
    if mime_type:
        filters['mime_type'] = mime_type
    
    # Date range filters
    release_date_from = request.GET.get('release_date_from')
    release_date_to = request.GET.get('release_date_to')
    if release_date_from:
        filters['release_date'] = f'>= {release_date_from}'
    if release_date_to:
        filters['release_date'] = f'<= {release_date_to}'
    
    record_date_from = request.GET.get('record_date_from')
    record_date_to = request.GET.get('record_date_to')
    if record_date_from:
        filters['record_date_start'] = f'>= {record_date_from}'
    if record_date_to:
        filters['record_date_end'] = f'<= {record_date_to}'
    
    # Sorting
    sort_param = request.GET.get('sort')
    sort = None
    if sort_param:
        # Parse sort parameter (e.g., 'created_at:desc')
        if ':' in sort_param:
            field, direction = sort_param.split(':', 1)
            if direction.lower() in ['asc', 'desc']:
                sort = [f"{field}:{direction}"]
    
    # Facets to include
    facets = None
    if include_facets:
        facets = ['agency_office', 'tags', 'mime_type', 'file_extension']
    
    # Perform search
    results = search_documents(
        query=query,
        filters=filters if filters else None,
        facets=facets,
        limit=limit,
        offset=offset,
        sort=sort
    )
    
    # Build response
    response_data = {
        'results': results['hits'],
        'total': results['total'],
        'query': query,
        'limit': limit,
        'offset': offset,
        'processing_time': results.get('processing_time', 0)
    }
    
    # Add facets if requested
    if include_facets:
        response_data['facets'] = results.get('facets', {})
    
    # Add error if any
    if 'error' in results:
        response_data['error'] = results['error']
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def facets_view(request):
    """
    Get available facets for filtering.
    """
    # Try to get from cache first
    cache_key = 'search_facets'
    facets = cache.get(cache_key)
    
    if facets is None:
        facets = get_facets()
        # Cache for 15 minutes
        cache.set(cache_key, facets, 900)
    
    return Response({'facets': facets})


@api_view(['POST'])
@permission_classes([CanAccessAdminFeatures])
def reindex_view(request):
    """
    Trigger a full reindex of all documents.
    This is an admin-only operation.
    """
    try:
        # Try to run reindexing as a background task
        from documents.tasks import reindex_all_documents_task
        task = reindex_all_documents_task.delay()
        return Response({
            'message': 'Reindexing started',
            'task_id': task.id
        })
    except ImportError:
        # Fallback to synchronous reindexing
        success = reindex_all_documents()
        if success:
            # Clear facets cache
            cache.delete('search_facets')
            return Response({'message': 'Reindexing completed successfully'})
        else:
            return Response(
                {'error': 'Reindexing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    """
    Get search suggestions based on query.
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response({'suggestions': []})
    
    # Simple implementation - in production you might want more sophisticated suggestions
    try:
        # Search for titles and agency offices that match the query
        results = search_documents(
            query=query,
            limit=10,
            facets=['agency_office', 'tags']
        )
        
        suggestions = []
        
        # Add matching titles
        for hit in results['hits']:
            title = hit.get('title', '')
            if query.lower() in title.lower() and title not in suggestions:
                suggestions.append(title)
        
        # Add matching agency offices
        facets = results.get('facets', {})
        agency_offices = facets.get('agency_office', {})
        for agency in agency_offices.keys():
            if query.lower() in agency.lower() and agency not in suggestions:
                suggestions.append(agency)
        
        # Add matching tags
        tags = facets.get('tags', {})
        for tag in tags.keys():
            if query.lower() in tag.lower() and tag not in suggestions:
                suggestions.append(tag)
        
        # Limit to 10 suggestions
        suggestions = suggestions[:10]
        
        return Response({'suggestions': suggestions})
        
    except Exception as e:
        return Response({'suggestions': [], 'error': str(e)})


@api_view(['GET'])
@permission_classes([CanAccessAdminFeatures])
def search_stats(request):
    """
    Get search statistics (admin only).
    """
    try:
        from analytics.models import SearchEvent
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Get stats for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        stats = {
            'total_searches': SearchEvent.objects.count(),
            'recent_searches': SearchEvent.objects.filter(created_at__gte=thirty_days_ago).count(),
            'top_queries': list(
                SearchEvent.objects.filter(created_at__gte=thirty_days_ago)
                .values('query')
                .annotate(count=Count('query'))
                .order_by('-count')[:10]
            ),
            'avg_results': SearchEvent.objects.filter(
                created_at__gte=thirty_days_ago
            ).aggregate(
                avg_results=models.Avg('results_count')
            )['avg_results'] or 0
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
