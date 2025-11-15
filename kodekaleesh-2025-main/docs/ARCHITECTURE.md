# Technical Architecture

## System Overview

```
┌─────────────────────┐
│   Web Browser       │
│   (React SPA)       │
└──────────┬──────────┘
           │
        HTTP/REST
           │
     ┌─────▼─────┐
     │   Flask   │
     │    API    │
     └─────┬─────┘
           │
      ┌────┴────────┬────────────┐
      │             │            │
  ┌───▼────┐  ┌────▼────┐  ┌───▼───┐
  │Document│  │Summariz-│  │Search │
  │Manager │  │   er    │  │Engine │
  └───┬────┘  └────┬────┘  └───┬───┘
      │            │           │
      └────────┬───┴───────┬───┘
               │           │
          ┌────▼────┐  ┌──▼──┐
          │documents │  │JSON │
          │ storage  │  │file │
          └──────────┘  └─────┘
```

## Components

### Frontend (React)

**Purpose**: User interface for document management

**Key Components**:
- `App.jsx`: Main application router and state management
- `DocumentUpload`: File upload with drag-and-drop
- `DocumentList`: Table view of all documents
- `SearchPanel`: Full-text search interface
- `SummaryPanel`: Document preview and metadata

**State Management**:
- Local component state (useState)
- API calls via Fetch API
- CORS-enabled requests

### Backend (Flask)

**Purpose**: REST API for document processing and search

**Key Modules**:
1. `app.py`: Flask application and route handlers
2. `document_processor.py`: Core document handling
3. `summarizer.py`: Text summarization
4. `search_engine.py`: Search functionality

### Data Layer

**Current**: JSON file-based storage
- Simple and lightweight
- No database setup required
- Suitable for MVP

**Document Structure**:
```json
{
  "doc-id-123": {
    "id": "doc-id-123",
    "filename": "case_report.txt",
    "content": "...",
    "created_at": "2025-11-14T...",
    "pages": 5,
    "text_length": 4500,
    "file_path": "uploads/case_report.txt"
  }
}
```

## API Design

### Request/Response Format

All endpoints follow REST conventions:

**Request**:
```
POST /api/upload
Content-Type: multipart/form-data

file: <binary data>
```

**Response**:
```json
{
  "success": true,
  "document_id": "abc123",
  "filename": "case.txt",
  "pages": 3,
  "text_length": 2500
}
```

### Error Handling

```json
{
  "error": "File type not allowed. Use PDF, TXT, or DOCX"
}
```

Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `413`: File Too Large
- `500`: Server Error

## Search Algorithm

### Simple Keyword-Based Search

1. **Indexing**: On-the-fly when query received
2. **Scoring**:
   - Exact phrase match: +100 points
   - Word occurrence: +5 points each
   - Filename match: +20 points
3. **Ranking**: Sort by total score descending
4. **Result Limit**: Top 10 results

### Context Extraction

- Extract 50 characters before and after match
- Useful for quick relevance assessment
- Helps users verify match is relevant

## Text Summarization

### Algorithm: Extractive Summarization

1. **Sentence Splitting**: Split by `.!?` punctuation
2. **Word Scoring**: Count important words (non-stopwords)
3. **Sentence Scoring**: Sum important word counts per sentence
4. **Selection**: Pick top 3 highest-scoring sentences
5. **Ordering**: Return in original order

### Limitations & Future Work

- Doesn't understand context deeply
- May miss important compound concepts
- Better with LLM integration (GPT-4, Claude)

## Entity Extraction

### Currently Supported

1. **Case Names**: Pattern `\w+ v\. \w+`
2. **Dates**: Pattern `YYYY-MM-DD` or `MM/DD/YYYY`
3. **Sections**: Pattern `Section \d+\.\d+`

### Regex-Based Approach

- Fast and lightweight
- Works well for structured legal documents
- Extensible with more patterns

### Better Alternative: NER

- Use spaCy or BERT for named entity recognition
- Better context understanding
- Higher accuracy for complex names

## Storage Considerations

### Current (MVP)

**Pros**:
- Zero setup
- No external dependencies
- Easy to debug

**Cons**:
- Not scalable beyond 1000s of documents
- No query optimization
- Single-threaded access
- No full-text index

### Production Database

**PostgreSQL + Elasticsearch**:

```sql
-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  filename VARCHAR(255),
  content TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Full-text index
CREATE INDEX idx_content_tsvector 
  ON documents USING gin(to_tsvector('english', content));
```

## Performance Characteristics

### Upload
- Time: O(file_size)
- Limits: 50MB max (configurable)

### Search
- Time: O(n_documents × document_size)
- Better with Elasticsearch: O(log n)

### Summarization
- Time: O(document_size)
- Extractive: Fast
- Abstractive: Slower (with LLMs)

## Security Considerations

### Current MVP

⚠️ **NOT production-ready**:
- No authentication
- No authorization
- No encryption at rest
- No audit logging

### Production Checklist

- [ ] User authentication (JWT/OAuth)
- [ ] Role-based access control
- [ ] Document encryption
- [ ] Audit logging
- [ ] API rate limiting
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] CORS configuration
- [ ] HTTPS enforcement
- [ ] Data retention policies

## Deployment Architecture

### Recommended Stack

```
┌──────────────────────────┐
│   CloudFlare/CDN         │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│   Load Balancer          │
└────────────┬─────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──┐         ┌───▼──┐
│Gunicorn      │Gunicorn
│(Backend)     │(Backend)
└───┬──┘         └───┬──┘
    │                 │
    └────────┬────────┘
             │
        ┌────▼──────────┐
        │ PostgreSQL    │
        │ + Elasticsearch
        └───────────────┘
```

### Container (Docker)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Monitoring & Logging

### Key Metrics

- Document upload rate
- Search query count
- Average response time
- Error rate
- Storage utilization

### Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Document {doc_id} processed in {time}ms")
```

---

This architecture is designed for MVP simplicity while being extensible for production.
