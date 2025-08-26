"""
Text extraction utilities for documents.
"""
import os
import logging
from typing import Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> Tuple[str, str, Optional[float]]:
    """
    Extract text from PDF using pdfminer.six and fallback to Tesseract OCR.
    Returns (text, method, confidence)
    """
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        
        # If text is too short, might be a scanned PDF - try OCR
        if len(text.strip()) < 50 and settings.OCR_ENABLED:
            return extract_text_with_ocr(file_path)
        
        return text, 'pdfminer', None
    except Exception as e:
        logger.warning(f"PDF text extraction failed: {e}")
        
        # Fallback to OCR if enabled
        if settings.OCR_ENABLED:
            return extract_text_with_ocr(file_path)
        
        return "", 'pdfminer', None


def extract_text_from_docx(file_path: str) -> Tuple[str, str, Optional[float]]:
    """
    Extract text from DOCX files using python-docx.
    Returns (text, method, confidence)
    """
    try:
        from docx import Document
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text, 'docx', None
    except Exception as e:
        logger.warning(f"DOCX text extraction failed: {e}")
        return "", 'docx', None


def extract_text_from_doc(file_path: str) -> Tuple[str, str, Optional[float]]:
    """
    Extract text from DOC files (legacy Word format).
    This is a basic implementation - in production you might want to use
    more sophisticated tools like antiword or libreoffice --headless.
    Returns (text, method, confidence)
    """
    try:
        # Try using antiword if available
        import subprocess
        result = subprocess.run(
            ['antiword', file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout, 'antiword', None
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    logger.warning(f"DOC text extraction not available for {file_path}")
    return "", 'doc', None


def extract_text_from_txt(file_path: str) -> Tuple[str, str, Optional[float]]:
    """
    Extract text from plain text files.
    Returns (text, method, confidence)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        return text, 'plain', None
    except Exception as e:
        logger.warning(f"Text file reading failed: {e}")
        return "", 'plain', None


def extract_text_with_ocr(file_path: str) -> Tuple[str, str, Optional[float]]:
    """
    Extract text using Tesseract OCR.
    Returns (text, method, confidence)
    """
    try:
        import pytesseract
        from PIL import Image
        import pdf2image
        
        # For PDF files, convert to images first
        if file_path.lower().endswith('.pdf'):
            pages = pdf2image.convert_from_path(file_path)
            text_parts = []
            confidences = []
            
            for page in pages:
                data = pytesseract.image_to_data(page, output_type=pytesseract.Output.DICT)
                page_text = ' '.join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 0])
                text_parts.append(page_text)
                
                # Calculate average confidence for this page
                valid_confidences = [int(data['conf'][i]) for i in range(len(data['conf'])) if int(data['conf'][i]) > 0]
                if valid_confidences:
                    confidences.extend(valid_confidences)
            
            text = '\n'.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
        else:
            # For image files
            image = Image.open(file_path)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = ' '.join([data['text'][i] for i in range(len(data['text'])) if int(data['conf'][i]) > 0])
            
            valid_confidences = [int(data['conf'][i]) for i in range(len(data['conf'])) if int(data['conf'][i]) > 0]
            avg_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0
        
        return text, 'tesseract', avg_confidence / 100.0  # Convert to 0-1 scale
        
    except Exception as e:
        logger.warning(f"OCR text extraction failed: {e}")
        return "", 'tesseract', None


def extract_text_from_document(document) -> bool:
    """
    Extract text from a document and save to DocumentText model.
    Returns True if successful, False otherwise.
    """
    from .models import DocumentText
    
    if not document.file:
        logger.warning(f"No file attached to document {document.id}")
        return False
    
    if not document.is_text_extractable:
        logger.info(f"Document {document.id} is not text extractable")
        return False
    
    file_path = document.file.path
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    # Determine extraction method based on MIME type
    text = ""
    method = "other"
    confidence = None
    
    try:
        if document.mime_type == 'application/pdf':
            text, method, confidence = extract_text_from_pdf(file_path)
        elif document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text, method, confidence = extract_text_from_docx(file_path)
        elif document.mime_type == 'application/msword':
            text, method, confidence = extract_text_from_doc(file_path)
        elif document.mime_type in ['text/plain', 'text/rtf']:
            text, method, confidence = extract_text_from_txt(file_path)
        else:
            logger.warning(f"Unsupported MIME type for text extraction: {document.mime_type}")
            return False
        
        # Save extracted text
        doc_text, created = DocumentText.objects.get_or_create(
            document=document,
            defaults={
                'extracted_text': text,
                'extraction_method': method,
                'extraction_confidence': confidence,
            }
        )
        
        if not created:
            # Update existing text
            doc_text.extracted_text = text
            doc_text.extraction_method = method
            doc_text.extraction_confidence = confidence
            doc_text.save()
        
        logger.info(f"Text extraction successful for document {document.id} using {method}")
        
        # Index in search after successful extraction
        try:
            from search.utils import index_document
            index_document(document)
        except Exception as e:
            logger.warning(f"Failed to index document {document.id}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Text extraction failed for document {document.id}: {e}")
        return False


def reindex_all_documents():
    """
    Re-extract text from all documents and reindex them.
    This is useful for maintenance or when upgrading extraction methods.
    """
    from .models import Document
    
    documents = Document.objects.filter(file__isnull=False)
    success_count = 0
    error_count = 0
    
    for document in documents:
        try:
            if extract_text_from_document(document):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            logger.error(f"Failed to reindex document {document.id}: {e}")
            error_count += 1
    
    logger.info(f"Reindexing complete: {success_count} success, {error_count} errors")
    return success_count, error_count