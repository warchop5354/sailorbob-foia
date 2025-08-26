"""
Celery tasks for background processing.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def extract_document_text(document_id):
    """
    Celery task to extract text from a document.
    """
    from .models import Document
    from .utils import extract_text_from_document
    
    try:
        document = Document.objects.get(id=document_id)
        success = extract_text_from_document(document)
        
        if success:
            logger.info(f"Text extraction completed for document {document_id}")
            return f"Text extraction successful for document {document_id}"
        else:
            logger.warning(f"Text extraction failed for document {document_id}")
            return f"Text extraction failed for document {document_id}"
            
    except Document.DoesNotExist:
        error_msg = f"Document {document_id} not found"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error extracting text from document {document_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def reindex_all_documents_task():
    """
    Celery task to reindex all documents.
    """
    from .utils import reindex_all_documents
    
    try:
        success_count, error_count = reindex_all_documents()
        result = f"Reindexing complete: {success_count} success, {error_count} errors"
        logger.info(result)
        return result
    except Exception as e:
        error_msg = f"Error during bulk reindexing: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def cleanup_orphaned_files():
    """
    Celery task to clean up orphaned files.
    """
    import os
    from django.conf import settings
    from .models import Document
    
    try:
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            return "Media root does not exist"
        
        # Get all file paths from database
        db_files = set()
        for doc in Document.objects.all():
            if doc.file:
                db_files.add(os.path.join(media_root, doc.file.name))
        
        # Find all files in media directory
        orphaned_files = []
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_files:
                    orphaned_files.append(file_path)
        
        # Remove orphaned files (be careful with this in production!)
        removed_count = 0
        for file_path in orphaned_files:
            try:
                os.remove(file_path)
                removed_count += 1
                logger.info(f"Removed orphaned file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove {file_path}: {e}")
        
        result = f"Cleanup complete: {removed_count} orphaned files removed"
        logger.info(result)
        return result
        
    except Exception as e:
        error_msg = f"Error during file cleanup: {str(e)}"
        logger.error(error_msg)
        return error_msg