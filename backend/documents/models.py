"""
Document models for FOIA portal.
"""
import os
import hashlib
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField


class Tag(models.Model):
    """
    Tags for categorizing documents.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def document_upload_path(instance, filename):
    """
    Generate upload path for documents.
    """
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = f"{now.month:02d}"
    slug = instance.slug or slugify(instance.title)
    return f"{year}/{month}/{slug}/{filename}"


class Document(models.Model):
    """
    FOIA document model with metadata and file handling.
    """
    # Basic Information
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # File Information
    file = models.FileField(upload_to=document_upload_path)
    mime_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField()
    sha256_hash = models.CharField(max_length=64, unique=True)
    
    # FOIA Specific Fields
    request_id = models.CharField(max_length=100, blank=True, help_text="FOIA request identifier")
    agency_office = models.CharField(max_length=255, blank=True, help_text="Releasing agency/office")
    release_date = models.DateField(null=True, blank=True, help_text="Date document was released")
    exemptions_applied = ArrayField(
        models.CharField(max_length=10), 
        blank=True, 
        default=list,
        help_text="FOIA exemptions applied (e.g., ['5', '6', '7c'])"
    )
    redaction_notes = models.TextField(blank=True, help_text="Notes about redactions")
    source_link = models.URLField(blank=True, help_text="Link to original source")
    
    # Date Range (for records that span time periods)
    record_date_start = models.DateField(null=True, blank=True, help_text="Start date of record period")
    record_date_end = models.DateField(null=True, blank=True, help_text="End date of record period")
    
    # Relationships
    tags = models.ManyToManyField(Tag, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['agency_office']),
            models.Index(fields=['release_date']),
            models.Index(fields=['sha256_hash']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Calculate file hash and size if file is present
        if self.file and not self.sha256_hash:
            self.file.seek(0)
            hash_sha256 = hashlib.sha256()
            for chunk in iter(lambda: self.file.read(4096), b""):
                hash_sha256.update(chunk)
            self.sha256_hash = hash_sha256.hexdigest()
            self.file.seek(0, 2)  # Seek to end
            self.file_size = self.file.tell()
            self.file.seek(0)  # Reset to beginning
        
        super().save(*args, **kwargs)
    
    @property
    def file_extension(self):
        """Get file extension from filename."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''
    
    @property
    def is_pdf(self):
        """Check if document is a PDF."""
        return self.mime_type == 'application/pdf'
    
    @property
    def is_text_extractable(self):
        """Check if text can be extracted from this file type."""
        extractable_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/rtf',
            'application/vnd.oasis.opendocument.text',
        ]
        return self.mime_type in extractable_types
    
    def get_absolute_url(self):
        """Get the absolute URL for this document."""
        return f"/documents/{self.slug}/"


class DocumentText(models.Model):
    """
    Extracted text content from documents.
    """
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='text_content')
    extracted_text = models.TextField()
    extraction_method = models.CharField(
        max_length=50,
        choices=[
            ('pdfminer', 'PDF Miner'),
            ('docx', 'Python-docx'),
            ('tesseract', 'Tesseract OCR'),
            ('manual', 'Manual Entry'),
            ('other', 'Other'),
        ],
        default='other'
    )
    extraction_confidence = models.FloatField(null=True, blank=True, help_text="OCR confidence score if applicable")
    extracted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Text'
        verbose_name_plural = 'Document Texts'
    
    def __str__(self):
        return f"Text for {self.document.title}"
    
    @property
    def word_count(self):
        """Get approximate word count."""
        return len(self.extracted_text.split()) if self.extracted_text else 0
    
    @property
    def preview(self):
        """Get text preview (first 200 characters)."""
        if self.extracted_text:
            return self.extracted_text[:200] + '...' if len(self.extracted_text) > 200 else self.extracted_text
        return ''
