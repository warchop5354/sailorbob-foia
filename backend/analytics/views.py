"""
Analytics views and dashboard endpoints.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from documents.permissions import CanAccessAdminFeatures
from .utils import get_analytics_summary, get_daily_stats


@api_view(['GET'])
@permission_classes([CanAccessAdminFeatures])
def analytics_summary(request):
    """
    Get analytics summary for admin dashboard.
    
    Query parameters:
    - days: Number of days to include (default: 30)
    """
    days = int(request.GET.get('days', 30))
    
    if days < 1 or days > 365:
        return Response(
            {'error': 'Days must be between 1 and 365'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    summary = get_analytics_summary(days=days)
    return Response(summary)


@api_view(['GET'])
@permission_classes([CanAccessAdminFeatures])
def daily_stats(request):
    """
    Get daily statistics for charts.
    
    Query parameters:
    - days: Number of days to include (default: 30)
    """
    days = int(request.GET.get('days', 30))
    
    if days < 1 or days > 365:
        return Response(
            {'error': 'Days must be between 1 and 365'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stats = get_daily_stats(days=days)
    return Response(stats)


@api_view(['GET'])
@permission_classes([CanAccessAdminFeatures])
def popular_content(request):
    """
    Get popular content statistics.
    """
    from django.db.models import Count
    from datetime import datetime, timedelta
    from .models import ViewEvent, DownloadEvent, SearchEvent
    
    # Get time period
    days = int(request.GET.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Most viewed documents
        most_viewed = list(
            ViewEvent.objects.filter(created_at__gte=start_date)
            .values(
                'document__id',
                'document__title',
                'document__slug',
                'document__agency_office'
            )
            .annotate(views=Count('id'))
            .order_by('-views')[:20]
        )
        
        # Most downloaded documents
        most_downloaded = list(
            DownloadEvent.objects.filter(created_at__gte=start_date)
            .values(
                'document__id',
                'document__title',
                'document__slug',
                'document__agency_office'
            )
            .annotate(downloads=Count('id'))
            .order_by('-downloads')[:20]
        )
        
        # Top search terms
        top_searches = list(
            SearchEvent.objects.filter(created_at__gte=start_date)
            .values('query')
            .annotate(count=Count('query'))
            .order_by('-count')[:20]
        )
        
        # Popular agencies
        popular_agencies = list(
            ViewEvent.objects.filter(
                created_at__gte=start_date,
                document__agency_office__isnull=False
            )
            .exclude(document__agency_office='')
            .values('document__agency_office')
            .annotate(views=Count('id'))
            .order_by('-views')[:10]
        )
        
        return Response({
            'most_viewed': most_viewed,
            'most_downloaded': most_downloaded,
            'top_searches': top_searches,
            'popular_agencies': popular_agencies,
            'period_days': days
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([CanAccessAdminFeatures])
def user_activity(request):
    """
    Get user activity statistics.
    """
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    from .models import ViewEvent, DownloadEvent, UploadEvent
    from accounts.models import User
    
    days = int(request.GET.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Active users (users who performed any action)
        active_users = User.objects.filter(
            Q(viewevent__created_at__gte=start_date) |
            Q(downloadevent__created_at__gte=start_date) |
            Q(uploadevent__created_at__gte=start_date)
        ).distinct().count()
        
        # User roles breakdown
        user_roles = User.objects.values('role').annotate(count=Count('id'))
        
        # Most active users
        most_active = list(
            User.objects.filter(
                viewevent__created_at__gte=start_date
            ).annotate(
                activity_count=Count('viewevent')
            ).order_by('-activity_count')[:10].values(
                'id', 'username', 'role', 'activity_count'
            )
        )
        
        # Upload activity by user
        upload_activity = list(
            UploadEvent.objects.filter(created_at__gte=start_date)
            .values('user__username', 'user__role')
            .annotate(uploads=Count('id'))
            .order_by('-uploads')[:10]
        )
        
        return Response({
            'active_users': active_users,
            'user_roles': list(user_roles),
            'most_active': most_active,
            'upload_activity': upload_activity,
            'period_days': days
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
