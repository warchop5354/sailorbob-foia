"""
Search utilities for Meilisearch integration.
"""
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
import meilisearch

logger = logging.getLogger(__name__)


class SearchClient:
    """Meilisearch client wrapper."""
    
    def __init__(self):
        self.client = meilisearch.Client(
            settings.MEILISEARCH_HOST,
            settings.MEILISEARCH_MASTER_KEY
        )
        self.index_name = settings.MEILISEARCH_INDEX
    
    def get_index(self):
        """Get or create the search index."""
        try:
            return self.client.index(self.index_name)
        except Exception as e:
            logger.error(f"Failed to get search index: {e}")
            return None
    
    def setup_index(self):
        """Set up the search index with proper configuration."""
        try:
            # Create index if it doesn't exist
            try:
                index = self.client.create_index(self.index_name, {'primaryKey': 'id'})
            except meilisearch.errors.MeilisearchApiError as e:
                if 'already exists' in str(e):
                    index = self.client.index(self.index_name)
                else:
                    raise
            
            # Configure searchable attributes
            index.update_searchable_attributes([
                'title',
                'description',
                'agency_office',
                'request_id',
                'extracted_text',
                'tags'
            ])
            
            # Configure filterable attributes
            index.update_filterable_attributes([
                'agency_office',
                'tags',
                'mime_type',
                'release_date',
                'record_date_start',
                'record_date_end',
                'created_at',
                'file_extension'
            ])
            
            # Configure sortable attributes
            index.update_sortable_attributes([
                'created_at',
                'updated_at',
                'title',
                'release_date',
                'file_size'
            ])
            
            # Configure ranking rules
            index.update_ranking_rules([
                'words',
                'typo',
                'proximity',
                'attribute',
                'sort',
                'exactness'
            ])
            
            # Configure display attributes (what to return)
            index.update_displayed_attributes([
                'id',
                'title',
                'description',
                'slug',
                'agency_office',
                'tags',
                'mime_type',
                'file_size',
                'release_date',
                'created_at',
                'file_extension'
            ])
            
            logger.info(f"Search index '{self.index_name}' configured successfully")
            return index
            
        except Exception as e:
            logger.error(f"Failed to setup search index: {e}")
            return None


def get_search_client() -> SearchClient:
    """Get configured search client."""
    return SearchClient()


def index_document(document) -> bool:
    """
    Index a single document in Meilisearch.
    """
    try:
        client = get_search_client()
        index = client.get_index()
        
        if not index:
            logger.error("Search index not available")
            return False
        
        # Prepare document data for indexing
        doc_data = {
            'id': document.id,
            'title': document.title,
            'description': document.description or '',
            'slug': document.slug,
            'agency_office': document.agency_office or '',
            'request_id': document.request_id or '',
            'tags': [tag.name for tag in document.tags.all()],
            'mime_type': document.mime_type,
            'file_size': document.file_size,
            'file_extension': document.file_extension,
            'release_date': document.release_date.isoformat() if document.release_date else None,
            'record_date_start': document.record_date_start.isoformat() if document.record_date_start else None,
            'record_date_end': document.record_date_end.isoformat() if document.record_date_end else None,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
        }
        
        # Add extracted text if available
        if hasattr(document, 'text_content') and document.text_content:
            doc_data['extracted_text'] = document.text_content.extracted_text
        
        # Index the document
        index.add_documents([doc_data])
        logger.info(f"Document {document.id} indexed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to index document {document.id}: {e}")
        return False


def delete_document_from_index(document_id: int) -> bool:
    """
    Remove a document from the search index.
    """
    try:
        client = get_search_client()
        index = client.get_index()
        
        if not index:
            logger.error("Search index not available")
            return False
        
        index.delete_document(str(document_id))
        logger.info(f"Document {document_id} removed from index")
        return True
        
    except Exception as e:
        logger.error(f"Failed to remove document {document_id} from index: {e}")
        return False


def search_documents(
    query: str = '',
    filters: Optional[Dict[str, Any]] = None,
    facets: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
    sort: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search documents with filters and facets.
    """
    try:
        client = get_search_client()
        index = client.get_index()
        
        if not index:
            return {
                'hits': [],
                'total': 0,
                'facets': {},
                'error': 'Search index not available'
            }
        
        # Build search parameters
        search_params = {
            'limit': limit,
            'offset': offset,
            'attributesToHighlight': ['title', 'description', 'extracted_text'],
            'highlightPreTag': '<mark>',
            'highlightPostTag': '</mark>',
        }
        
        # Add filters
        if filters:
            filter_strings = []
            for key, value in filters.items():
                if isinstance(value, list):
                    # Multiple values for the same field (OR condition)
                    filter_parts = [f"{key} = '{v}'" for v in value]
                    filter_strings.append(f"({' OR '.join(filter_parts)})")
                else:
                    filter_strings.append(f"{key} = '{value}'")
            
            if filter_strings:
                search_params['filter'] = ' AND '.join(filter_strings)
        
        # Add facets
        if facets:
            search_params['facets'] = facets
        
        # Add sorting
        if sort:
            search_params['sort'] = sort
        
        # Perform search
        results = index.search(query or '', search_params)
        
        return {
            'hits': results.get('hits', []),
            'total': results.get('estimatedTotalHits', 0),
            'facets': results.get('facetDistribution', {}),
            'processing_time': results.get('processingTimeMs', 0),
            'query': query
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            'hits': [],
            'total': 0,
            'facets': {},
            'error': str(e)
        }


def get_facets() -> Dict[str, Any]:
    """
    Get available facets for filtering.
    """
    try:
        client = get_search_client()
        index = client.get_index()
        
        if not index:
            return {}
        
        # Search with facets but no query to get all facet values
        results = index.search('', {
            'limit': 0,
            'facets': ['agency_office', 'tags', 'mime_type', 'file_extension']
        })
        
        return results.get('facetDistribution', {})
        
    except Exception as e:
        logger.error(f"Failed to get facets: {e}")
        return {}


def reindex_all_documents():
    """
    Reindex all documents from the database.
    """
    from documents.models import Document
    
    try:
        client = get_search_client()
        
        # Setup index
        index = client.setup_index()
        if not index:
            logger.error("Failed to setup search index")
            return False
        
        # Clear existing documents
        index.delete_all_documents()
        
        # Index all documents
        documents = Document.objects.prefetch_related('tags', 'text_content').all()
        success_count = 0
        
        for document in documents:
            if index_document(document):
                success_count += 1
        
        logger.info(f"Reindexing complete: {success_count} documents indexed")
        return True
        
    except Exception as e:
        logger.error(f"Reindexing failed: {e}")
        return False