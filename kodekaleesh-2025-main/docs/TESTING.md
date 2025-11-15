# Testing Guide

## Unit Tests

### Backend Tests

Create `backend/test_app.py`:

```python
import unittest
import json
import os
from app import app
from document_processor import DocumentProcessor

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_upload_document(self):
        """Test document upload"""
        with open('test_document.txt', 'w') as f:
            f.write('Test legal document content')
        
        with open('test_document.txt', 'rb') as f:
            response = self.client.post('/api/upload', data={'file': f})
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        os.remove('test_document.txt')

    def test_list_documents(self):
        """Test listing documents"""
        response = self.client.get('/api/documents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_search(self):
        """Test search functionality"""
        response = self.client.post('/api/search', 
            json={'query': 'test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
```

### Frontend Tests

Create `frontend/src/App.test.jsx`:

```javascript
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders header', () => {
    render(<App />);
    const header = screen.getByText(/Legal Document Intelligence/i);
    expect(header).toBeInTheDocument();
  });

  test('renders navigation tabs', () => {
    render(<App />);
    expect(screen.getByText(/Upload/i)).toBeInTheDocument();
    expect(screen.getByText(/Documents/i)).toBeInTheDocument();
    expect(screen.getByText(/Search/i)).toBeInTheDocument();
  });
});
```

## Integration Tests

### End-to-End Flow

```bash
# 1. Start backend
cd backend
python app.py &

# 2. Start frontend
cd frontend
npm start &

# 3. Run E2E tests (Cypress example)
npx cypress run
```

## Manual Testing Checklist

### Document Upload
- [ ] Upload valid PDF (5KB - 50MB)
- [ ] Upload valid TXT
- [ ] Upload valid DOCX
- [ ] Reject invalid file type
- [ ] Reject file > 50MB
- [ ] Handle network error during upload

### Document Management
- [ ] View document list
- [ ] View document details
- [ ] Delete document
- [ ] Verify deleted document gone
- [ ] Handle empty list gracefully

### Search
- [ ] Search with single word
- [ ] Search with multiple words
- [ ] Search with special characters
- [ ] Empty search results
- [ ] Case-insensitive search
- [ ] View context snippets

### Summarization
- [ ] Generate summary for document
- [ ] Summary length appropriate
- [ ] Sentences in original order
- [ ] Handle large documents

### Performance
- [ ] Upload 1000 documents
- [ ] Search performance degradation
- [ ] UI responsiveness
- [ ] Memory usage

## Load Testing

### Apache Bench

```bash
# Test upload endpoint
ab -n 100 -c 10 http://localhost:5000/api/health

# Test search with POST
ab -n 100 -c 10 -p data.json \
  http://localhost:5000/api/search
```

### Locust

```python
from locust import HttpUser, task

class LegalDocUser(HttpUser):
    @task
    def search(self):
        self.client.post("/api/search", 
            json={"query": "plaintiff"})
    
    @task
    def list_docs(self):
        self.client.get("/api/documents")
```

## Debugging

### Browser DevTools

**Console Tab**: Check for JavaScript errors
**Network Tab**: Monitor API calls
**Application Tab**: Check localStorage

### Backend Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Processing document: {doc_id}")
```

### API Testing Tools

**Postman**:
```
POST http://localhost:5000/api/search
Content-Type: application/json

{
  "query": "breach of contract"
}
```

**curl**:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "breach"}'
```

---

Run tests regularly to ensure quality!
