"""
Serializers for document operations.
"""
from rest_framework import serializers
from .models import Document, Tag, DocumentText


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class DocumentTextSerializer(serializers.ModelSerializer):
    """Serializer for document text content."""
    
    class Meta:
        model = DocumentText
        fields = ['extracted_text', 'extraction_method', 'extraction_confidence', 'word_count', 'preview']
        read_only_fields = ['extraction_method', 'extraction_confidence', 'word_count', 'preview']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document lists."""
    tags = TagSerializer(many=True, read_only=True)
    uploaded_by = serializers.StringRelatedField(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'description', 'mime_type', 'file_size',
            'agency_office', 'release_date', 'tags', 'uploaded_by', 'created_at',
            'file_url', 'file_extension'
        ]
        read_only_fields = ['id', 'slug', 'mime_type', 'file_size', 'uploaded_by', 'created_at', 'file_extension']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for document details."""
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    uploaded_by = serializers.StringRelatedField(read_only=True)
    text_content = DocumentTextSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'description', 'file', 'mime_type', 'file_size',
            'sha256_hash', 'request_id', 'agency_office', 'release_date',
            'exemptions_applied', 'redaction_notes', 'source_link',
            'record_date_start', 'record_date_end', 'tags', 'tag_ids',
            'uploaded_by', 'created_at', 'updated_at', 'text_content',
            'file_url', 'file_extension', 'is_pdf', 'is_text_extractable'
        ]
        read_only_fields = [
            'id', 'slug', 'mime_type', 'file_size', 'sha256_hash', 'uploaded_by',
            'created_at', 'updated_at', 'file_extension', 'is_pdf', 'is_text_extractable'
        ]
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def validate_file(self, value):
        """Validate uploaded file."""
        from django.conf import settings
        import magic
        
        # Check file size
        if value.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise serializers.ValidationError(f"File size cannot exceed {max_mb}MB")
        
        # Check MIME type
        mime = magic.from_buffer(value.read(1024), mime=True)
        value.seek(0)  # Reset file pointer
        
        if mime not in settings.ALLOWED_UPLOAD_TYPES:
            raise serializers.ValidationError(f"File type '{mime}' is not allowed")
        
        return value
    
    def create(self, validated_data):
        """Create document with file validation and MIME type detection."""
        import magic
        
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Set MIME type
        if 'file' in validated_data and validated_data['file']:
            file_obj = validated_data['file']
            file_obj.seek(0)
            mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
            file_obj.seek(0)
            validated_data['mime_type'] = mime_type
        
        # Set uploaded_by to current user
        validated_data['uploaded_by'] = self.context['request'].user
        
        document = Document.objects.create(**validated_data)
        
        # Set tags
        if tag_ids:
            document.tags.set(tag_ids)
        
        return document
    
    def update(self, instance, validated_data):
        """Update document with tag handling."""
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        return instance


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer specifically for document uploads."""
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'file', 'request_id', 'agency_office',
            'release_date', 'exemptions_applied', 'redaction_notes', 'source_link',
            'record_date_start', 'record_date_end', 'tag_ids'
        ]
    
    def validate_file(self, value):
        """Validate uploaded file."""
        from django.conf import settings
        import magic
        
        # Check file size
        if value.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise serializers.ValidationError(f"File size cannot exceed {max_mb}MB")
        
        # Check MIME type
        mime = magic.from_buffer(value.read(1024), mime=True)
        value.seek(0)  # Reset file pointer
        
        if mime not in settings.ALLOWED_UPLOAD_TYPES:
            raise serializers.ValidationError(f"File type '{mime}' is not allowed")
        
        return value
    
    def create(self, validated_data):
        """Create document with file processing."""
        import magic
        
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Set MIME type
        if 'file' in validated_data and validated_data['file']:
            file_obj = validated_data['file']
            file_obj.seek(0)
            mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
            file_obj.seek(0)
            validated_data['mime_type'] = mime_type
        
        # Set uploaded_by to current user
        validated_data['uploaded_by'] = self.context['request'].user
        
        document = Document.objects.create(**validated_data)
        
        # Set tags
        if tag_ids:
            document.tags.set(tag_ids)
        
        # Trigger text extraction asynchronously if Celery is available
        try:
            from .tasks import extract_document_text
            extract_document_text.delay(document.id)
        except ImportError:
            # Fallback to synchronous extraction
            from .utils import extract_text_from_document
            extract_text_from_document(document)
        
        return document