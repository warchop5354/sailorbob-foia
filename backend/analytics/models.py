"""
Analytics models for tracking user interactions.
"""
from django.db import models
from django.conf import settings


class ViewEvent(models.Model):
    """
    Track document view events.
    """
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='view_events'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'View Event'
        verbose_name_plural = 'View Events'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['document', 'created_at']),
        ]
    
    def __str__(self):
        user_str = str(self.user) if self.user else self.ip_address or 'Anonymous'
        return f"{user_str} viewed {self.document.title}"


class SearchEvent(models.Model):
    """
    Track search query events.
    """
    query = models.CharField(max_length=500)
    results_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Search Event'
        verbose_name_plural = 'Search Events'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['query']),
        ]
    
    def __str__(self):
        user_str = str(self.user) if self.user else self.ip_address or 'Anonymous'
        return f'{user_str} searched for "{self.query}"'


class DownloadEvent(models.Model):
    """
    Track document download events.
    """
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='download_events'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Download Event'
        verbose_name_plural = 'Download Events'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['document', 'created_at']),
        ]
    
    def __str__(self):
        user_str = str(self.user) if self.user else self.ip_address or 'Anonymous'
        return f"{user_str} downloaded {self.document.title}"


class UploadEvent(models.Model):
    """
    Track document upload events.
    """
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='upload_events'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    processing_time = models.FloatField(null=True, blank=True, help_text="Upload processing time in seconds")
    extraction_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Upload Event'
        verbose_name_plural = 'Upload Events'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} uploaded {self.document.title}"
