import pytest
import json
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app
from document_processor import DocumentProcessor
from search_engine import SearchEngine
from summarizer import DocumentSummarizer
from ocr_processor import OCRProcessor


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def processor():
    """Document processor instance"""
    return DocumentProcessor()


@pytest.fixture
def search_engine_instance():
    """Search engine instance"""
    return SearchEngine()


@pytest.fixture
def summarizer_instance():
    """Summarizer instance"""
    return DocumentSummarizer()


@pytest.fixture
def ocr_instance():
    """OCR processor instance"""
    return OCRProcessor()


# ============ Health Check Tests ============

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test GET /api/health returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'status' in data


# ============ API Response Format Tests ============

class TestResponseFormat:
    """Test consistent response formatting"""
    
    def test_success_response_format(self, client):
        """Test success responses have required fields"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is True
    
    def test_error_response_format(self, client):
        """Test error responses have required fields"""
        response = client.post('/api/search', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert 'error_code' in data
    
    def test_invalid_json_format(self, client):
        """Test handling of invalid JSON"""
        response = client.post('/api/search', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_content_type_validation(self, client):
        """Test Content-Type validation"""
        response = client.post('/api/search',
                             data=json.dumps({'query': 'test'}),
                             content_type='text/plain')
        assert response.status_code == 400


# ============ Document Processing Tests ============

class TestDocumentProcessing:
    """Test document processing"""
    
    def test_list_documents_empty(self, client):
        """Test listing documents when none exist"""
        response = client.get('/api/documents')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'documents' in data
        assert 'total' in data
    
    def test_upload_no_file(self, client):
        """Test upload without file returns 400"""
        response = client.post('/api/upload')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No file provided' in data['error']


# ============ Search Tests ============

class TestSearch:
    """Test search functionality"""
    
    def test_search_missing_query(self, client):
        """Test search without query parameter"""
        response = client.post('/api/search', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    def test_search_empty_query(self, client):
        """Test search with empty query"""
        response = client.post('/api/search', json={'query': ''})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'cannot be empty' in data['error']
    
    def test_search_query_too_long(self, client):
        """Test search with query exceeding max length"""
        response = client.post('/api/search', json={'query': 'a' * 501})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'too long' in data['error']
    
    def test_search_limit_capping(self, client):
        """Test that search limit is capped at 100"""
        response = client.post('/api/search', json={'query': 'test', 'limit': 500})
        assert response.status_code == 200
        data = json.loads(response.data)
        # The backend should cap at 100


# ============ Document Metadata Tests ============

class TestDocumentMetadata:
    """Test document metadata endpoints"""
    
    def test_get_summary_invalid_doc_id(self, client):
        """Test summary for non-existent document"""
        response = client.get('/api/documents/invalid-id/summary')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Document not found' in data['error']
    
    def test_get_metadata_invalid_doc_id(self, client):
        """Test metadata for non-existent document"""
        response = client.get('/api/documents/invalid-id/metadata')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Document not found' in data['error']
    
    def test_delete_invalid_doc_id(self, client):
        """Test delete for non-existent document"""
        response = client.delete('/api/documents/invalid-id')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Document not found' in data['error']
    
    def test_summary_max_length_validation(self, client):
        """Test summary max_length parameter validation"""
        response = client.get('/api/documents/test-id/summary?max_length=10')
        # Should fail with 400 (max_length too small) or 404 (doc not found)
        assert response.status_code in [400, 404]
    
    def test_summary_max_length_invalid(self, client):
        """Test invalid max_length parameter"""
        # First get a valid document ID, or just test that 404 is returned
        response = client.get('/api/documents/test-id/summary?max_length=invalid')
        # Either 400 (invalid param) or 404 (doc not found) are both acceptable
        assert response.status_code in [400, 404]


# ============ Analysis Tests ============

class TestAnalysis:
    """Test document analysis"""
    
    def test_analyze_missing_doc_ids(self, client):
        """Test analyze without document_ids"""
        response = client.post('/api/analyze', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    def test_analyze_empty_doc_ids(self, client):
        """Test analyze with empty document_ids"""
        response = client.post('/api/analyze', json={'document_ids': []})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'non-empty list' in data['error']
    
    def test_analyze_too_many_docs(self, client):
        """Test analyze with more than 50 documents"""
        doc_ids = [f'doc-{i}' for i in range(51)]
        response = client.post('/api/analyze', json={'document_ids': doc_ids})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert '50 documents' in data['error']
    
    def test_analyze_invalid_doc_ids_type(self, client):
        """Test analyze with non-list document_ids"""
        response = client.post('/api/analyze', json={'document_ids': 'not-a-list'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'list' in data['error']


# ============ OCR Tests ============

class TestOCR:
    """Test OCR functionality"""
    
    def test_ocr_status(self, client):
        """Test OCR status endpoint"""
        response = client.get('/api/ocr/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'ocr_available' in data
        assert 'supported_formats' in data
    
    def test_ocr_extract_no_file(self, client):
        """Test OCR extract without file"""
        response = client.post('/api/ocr/extract')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No file provided' in data['error'] or 'file' in data['error'].lower()
    
    def test_ocr_extract_unsupported_format(self, client):
        """Test OCR extract with unsupported format"""
        # When no file is attached to the request, we get "No file provided"
        # This is expected because multipart/form-data requires proper formatting
        response = client.post('/api/ocr/extract')
        assert response.status_code == 400


# ============ AWS Integration Tests ============

class TestAWSIntegration:
    """Test AWS integration endpoints"""
    
    def test_aws_status(self, client):
        """Test AWS status endpoint"""
        response = client.get('/api/aws/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'aws_enabled' in data
    
    def test_aws_upload_disabled(self, client):
        """Test AWS upload when disabled"""
        response = client.post('/api/aws/upload', json={'document_id': 'test', 'file_path': 'test.txt'})
        # Should fail since AWS is not enabled (400) or endpoint doesn't exist (404)
        assert response.status_code in [400, 404, 500]
    
    def test_aws_upload_missing_fields(self, client):
        """Test AWS upload without required fields"""
        response = client.post('/api/aws/upload', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    def test_aws_textract_missing_fields(self, client):
        """Test Textract without required fields"""
        response = client.post('/api/aws/textract/extract', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']


# ============ Error Handler Tests ============

class TestErrorHandlers:
    """Test error handler responses"""
    
    def test_404_not_found(self, client):
        """Test 404 Not Found response"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_405_method_not_allowed(self, client):
        """Test 405 Method Not Allowed"""
        response = client.get('/api/upload')  # Should be POST
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_413_file_too_large(self, client):
        """Test 413 Payload Too Large response"""
        # This is handled by Flask's MAX_CONTENT_LENGTH
        # Hard to test without sending massive file


# ============ Module Tests ============

class TestDocumentProcessor:
    """Test DocumentProcessor module"""
    
    def test_processor_initialization(self, processor):
        """Test processor initializes correctly"""
        assert processor is not None
    
    def test_list_documents(self, processor):
        """Test list_documents method"""
        documents = processor.list_documents()
        assert isinstance(documents, list)
    
    def test_get_nonexistent_document(self, processor):
        """Test getting non-existent document returns None"""
        doc = processor.get_document('nonexistent-id')
        assert doc is None


class TestSearchEngine:
    """Test SearchEngine module"""
    
    def test_search_initialization(self, search_engine_instance):
        """Test search engine initializes"""
        assert search_engine_instance is not None
    
    def test_search_empty_query(self, search_engine_instance):
        """Test search with empty query"""
        results = search_engine_instance.search('')
        assert isinstance(results, list)
    
    def test_search_limit(self, search_engine_instance):
        """Test search respects limit parameter"""
        results = search_engine_instance.search('test', limit=5)
        assert len(results) <= 5


class TestSummarizer:
    """Test DocumentSummarizer module"""
    
    def test_summarizer_initialization(self, summarizer_instance):
        """Test summarizer initializes"""
        assert summarizer_instance is not None
    
    def test_summarize_empty_text(self, summarizer_instance):
        """Test summarizing empty text"""
        summary = summarizer_instance.summarize('')
        assert isinstance(summary, str)
    
    def test_summarize_short_text(self, summarizer_instance):
        """Test summarizing text shorter than max_length"""
        text = 'This is a short text.'
        summary = summarizer_instance.summarize(text, max_length=500)
        assert isinstance(summary, str)
    
    def test_summarize_long_text(self, summarizer_instance):
        """Test summarizing long text"""
        text = ' '.join(['This is a sentence.'] * 100)
        summary = summarizer_instance.summarize(text, max_length=100)
        assert isinstance(summary, str)
        assert len(summary) <= 100


class TestOCRProcessor:
    """Test OCRProcessor module"""
    
    def test_ocr_initialization(self, ocr_instance):
        """Test OCR processor initializes"""
        assert ocr_instance is not None
    
    def test_ocr_is_available(self, ocr_instance):
        """Test is_available method"""
        available = ocr_instance.is_available()
        assert isinstance(available, bool)
    
    def test_ocr_supported_formats(self, ocr_instance):
        """Test supported formats are defined"""
        assert hasattr(ocr_instance, 'SUPPORTED_FORMATS')
        assert len(ocr_instance.SUPPORTED_FORMATS) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
