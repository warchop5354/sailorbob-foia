"""
Analytics utilities for tracking events.
"""
import logging
from django.utils import timezone
from .models import ViewEvent, SearchEvent, DownloadEvent, UploadEvent

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def record_view_event(request, document):
    """Record a document view event."""
    try:
        ViewEvent.objects.create(
            document=document,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
        logger.debug(f"Recorded view event for document {document.id}")
    except Exception as e:
        logger.error(f"Failed to record view event: {e}")


def record_search_event(request, query, results_count=0, filters=None, processing_time=None):
    """Record a search event."""
    try:
        SearchEvent.objects.create(
            query=query,
            results_count=results_count,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            filters=filters or {},
            processing_time=processing_time
        )
        logger.debug(f"Recorded search event for query: {query}")
    except Exception as e:
        logger.error(f"Failed to record search event: {e}")


def record_download_event(request, document):
    """Record a document download event."""
    try:
        DownloadEvent.objects.create(
            document=document,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
        logger.debug(f"Recorded download event for document {document.id}")
    except Exception as e:
        logger.error(f"Failed to record download event: {e}")


def record_upload_event(user, document, processing_time=None, extraction_successful=False):
    """Record a document upload event."""
    try:
        UploadEvent.objects.create(
            document=document,
            user=user,
            file_size=document.file_size,
            mime_type=document.mime_type,
            processing_time=processing_time,
            extraction_successful=extraction_successful
        )
        logger.debug(f"Recorded upload event for document {document.id}")
    except Exception as e:
        logger.error(f"Failed to record upload event: {e}")


def get_analytics_summary(days=30):
    """Get analytics summary for the specified number of days."""
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        summary = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_views': ViewEvent.objects.filter(
                created_at__gte=start_date
            ).count(),
            'total_searches': SearchEvent.objects.filter(
                created_at__gte=start_date
            ).count(),
            'total_downloads': DownloadEvent.objects.filter(
                created_at__gte=start_date
            ).count(),
            'total_uploads': UploadEvent.objects.filter(
                created_at__gte=start_date
            ).count(),
            'unique_users': ViewEvent.objects.filter(
                created_at__gte=start_date,
                user__isnull=False
            ).values('user').distinct().count(),
            'avg_search_results': SearchEvent.objects.filter(
                created_at__gte=start_date
            ).aggregate(avg_results=Avg('results_count'))['avg_results'] or 0,
            'top_searches': list(
                SearchEvent.objects.filter(created_at__gte=start_date)
                .values('query')
                .annotate(count=Count('query'))
                .order_by('-count')[:10]
            ),
            'top_documents': list(
                ViewEvent.objects.filter(created_at__gte=start_date)
                .values('document__title', 'document__slug')
                .annotate(views=Count('id'))
                .order_by('-views')[:10]
            ),
            'top_downloads': list(
                DownloadEvent.objects.filter(created_at__gte=start_date)
                .values('document__title', 'document__slug')
                .annotate(downloads=Count('id'))
                .order_by('-downloads')[:10]
            )
        }
        
        return summary
    except Exception as e:
        logger.error(f"Failed to generate analytics summary: {e}")
        return {
            'error': str(e),
            'period_days': days
        }


def get_daily_stats(days=30):
    """Get daily statistics for charts."""
    from datetime import datetime, timedelta
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Get daily view counts
        daily_views = list(
            ViewEvent.objects.filter(created_at__date__gte=start_date)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Get daily search counts
        daily_searches = list(
            SearchEvent.objects.filter(created_at__date__gte=start_date)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Get daily download counts
        daily_downloads = list(
            DownloadEvent.objects.filter(created_at__date__gte=start_date)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        return {
            'daily_views': daily_views,
            'daily_searches': daily_searches,
            'daily_downloads': daily_downloads,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate daily stats: {e}")
        return {'error': str(e)}