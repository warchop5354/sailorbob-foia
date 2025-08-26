"""
Admin configuration for documents app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Document, Tag, DocumentText


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    """
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class DocumentTextInline(admin.StackedInline):
    """
    Inline for document text content.
    """
    model = DocumentText
    extra = 0
    readonly_fields = ['extraction_method', 'extraction_confidence', 'extracted_at', 'word_count']
    fields = ['extracted_text', 'extraction_method', 'extraction_confidence', 'extracted_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for Document model.
    """
    list_display = [
        'title', 'agency_office', 'file_type_display', 'file_size_display', 
        'uploaded_by', 'created_at', 'has_text'
    ]
    list_filter = [
        'mime_type', 'agency_office', 'release_date', 'created_at', 'uploaded_by'
    ]
    search_fields = [
        'title', 'description', 'request_id', 'agency_office', 'uploaded_by__username'
    ]
    filter_horizontal = ['tags']
    readonly_fields = [
        'slug', 'mime_type', 'file_size', 'sha256_hash', 'created_at', 'updated_at',
        'file_extension', 'is_pdf', 'is_text_extractable'
    ]
    inlines = [DocumentTextInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'tags')
        }),
        ('File Information', {
            'fields': ('file', 'mime_type', 'file_size', 'sha256_hash', 'file_extension', 'is_pdf', 'is_text_extractable')
        }),
        ('FOIA Information', {
            'fields': (
                'request_id', 'agency_office', 'release_date', 'exemptions_applied',
                'redaction_notes', 'source_link'
            )
        }),
        ('Date Range', {
            'fields': ('record_date_start', 'record_date_end'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_type_display(self, obj):
        """Display file type with icon."""
        if obj.is_pdf:
            return format_html('<span style="color: red;">📄 PDF</span>')
        elif 'word' in obj.mime_type:
            return format_html('<span style="color: blue;">📝 Word</span>')
        elif 'text' in obj.mime_type:
            return format_html('<span style="color: green;">📄 Text</span>')
        else:
            return obj.mime_type
    file_type_display.short_description = 'File Type'
    
    def file_size_display(self, obj):
        """Display file size in human readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'File Size'
    
    def has_text(self, obj):
        """Check if document has extracted text."""
        return hasattr(obj, 'text_content') and bool(obj.text_content.extracted_text)
    has_text.boolean = True
    has_text.short_description = 'Has Text'
    
    actions = ['extract_text_action', 'reindex_documents']
    
    def extract_text_action(self, request, queryset):
        """Admin action to extract text from selected documents."""
        from .utils import extract_text_from_document
        
        success_count = 0
        for document in queryset:
            if extract_text_from_document(document):
                success_count += 1
        
        self.message_user(
            request,
            f"Text extraction completed for {success_count} out of {queryset.count()} documents."
        )
    extract_text_action.short_description = "Extract text from selected documents"
    
    def reindex_documents(self, request, queryset):
        """Admin action to reindex selected documents."""
        try:
            from search.utils import index_document
            success_count = 0
            for document in queryset:
                try:
                    index_document(document)
                    success_count += 1
                except Exception:
                    pass
            
            self.message_user(
                request,
                f"Reindexed {success_count} out of {queryset.count()} documents."
            )
        except ImportError:
            self.message_user(request, "Search indexing not available.", level='warning')
    reindex_documents.short_description = "Reindex selected documents"


@admin.register(DocumentText)
class DocumentTextAdmin(admin.ModelAdmin):
    """
    Admin interface for DocumentText model.
    """
    list_display = ['document', 'extraction_method', 'word_count', 'extraction_confidence', 'extracted_at']
    list_filter = ['extraction_method', 'extracted_at']
    search_fields = ['document__title', 'extracted_text']
    readonly_fields = ['word_count', 'extracted_at']
    ordering = ['-extracted_at']
